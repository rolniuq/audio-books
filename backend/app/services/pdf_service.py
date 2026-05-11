import re
import fitz
from typing import List, Dict, Tuple, Optional
from app.config import settings

class PDFService:
    def __init__(self):
        self.chapter_fallback_words = settings.CHAPTER_FALLBACK_WORDS
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, List[Dict]]:
        doc = fitz.open(pdf_path)
        
        if doc.page_count == 0:
            raise ValueError("PDF has no pages")
        
        full_text = ""
        for page in doc:
            text = page.get_text()
            if text.strip():
                full_text += text + "\n"
        
        if not full_text.strip():
            raise ValueError("PDF appears to be scanned or contains no extractable text. Try using OCR first.")
        
        chapters = self.detect_chapters(full_text, doc)
        return full_text, chapters
    
    def detect_chapters(self, text: str, doc: fitz.Document) -> List[Dict]:
        chapters = []
        
        toc = doc.get_toc()
        if len(toc) > 1:
            chapters = self._detect_from_toc(toc, doc)
            if chapters:
                return chapters
        
        chapters = self._detect_from_font_size(doc)
        if chapters:
            return chapters
        
        chapters = self._detect_from_regex(text)
        if chapters:
            return chapters
        
        return self._detect_fallback(text)
    
    def _detect_from_toc(self, toc: List, doc: fitz.Document) -> List[Dict]:
        chapters = []
        for i, item in enumerate(toc):
            level, title, page_num = item[0], item[1], item[2]
            if level == 1:
                chapters.append({
                    "title": title.strip(),
                    "start_page": page_num - 1
                })
        
        for i in range(len(chapters) - 1):
            chapters[i]["end_page"] = chapters[i + 1]["start_page"] - 1
        
        if chapters:
            chapters[-1]["end_page"] = doc.page_count - 1
        
        return chapters
    
    def _detect_from_font_size(self, doc: fitz.Document) -> List[Dict]:
        chapters = []
        prev_size = 0
        
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span["size"] > prev_size and prev_size > 0:
                                text = span["text"].strip()
                                if len(text) > 3 and len(text) < 100:
                                    chapters.append({
                                        "title": text,
                                        "start_page": page_num
                                    })
                            prev_size = span["size"]
        
        return chapters[:10] if len(chapters) > 10 else []
    
    def _detect_from_regex(self, text: str) -> List[Dict]:
        patterns = [
            r'(?:Chapter|Chương)\s*(\d+|[IVXLC]+)[:\.\s]+(.+)',
            r'Part\s*(\d+|[IVXLC]+)[:\.\s]+(.+)',
            r'Phần\s*(\d+|[IVXLC]+)[:\.\s]+(.+)'
        ]
        
        chapters = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            if matches:
                for match in matches:
                    title = match.group(0).strip()
                    chapters.append({"title": title, "start_pos": match.start()})
                break
        
        if len(chapters) > 1:
            for i in range(len(chapters) - 1):
                chapters[i]["end_pos"] = chapters[i + 1]["start_pos"]
            chapters[-1]["end_pos"] = len(text)
        
        return chapters
    
    def _detect_fallback(self, text: str) -> List[Dict]:
        words = text.split()
        chunk_size = self.chapter_fallback_words
        chapters = []
        
        pos = 0
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            title = f"Chapter {len(chapters) + 1}"
            chunk_text = " ".join(chunk)
            
            chapters.append({
                "title": title,
                "start_pos": pos,
                "end_pos": pos + len(chunk_text)
            })
            pos += len(chunk_text) + 1
        
        return chapters
    
    def extract_chapter_text(self, pdf_path: str, start_page: int, end_page: Optional[int] = None) -> str:
        doc = fitz.open(pdf_path)
        end_page = end_page or doc.page_count
        
        text = ""
        for page_num in range(start_page, min(end_page, doc.page_count)):
            page = doc[page_num]
            text += page.get_text() + "\n"
        
        return self.clean_text(text)
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'Page\s*\d+', '', text, flags=re.IGNORECASE)
        
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        return '\n'.join(cleaned_lines)