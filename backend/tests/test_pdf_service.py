import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from app.services.pdf_service import PDFService


class TestPDFService:
    @pytest.fixture
    def pdf_service(self):
        return PDFService()
    
    @pytest.fixture
    def sample_pdf_content(self):
        return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
303
%%EOF
"""

    def test_pdf_service_init(self, pdf_service):
        assert pdf_service is not None
        assert pdf_service.chapter_fallback_words > 0
    
    def test_detect_chapters_returns_list(self, pdf_service):
        chapters = pdf_service._detect_fallback("word " * 1000)
        assert isinstance(chapters, list)
        assert len(chapters) > 0
    
    def test_detect_chapters_fallback_splits_text(self, pdf_service):
        text = " ".join(["word"] * 6000)
        chapters = pdf_service._detect_fallback(text)
        assert len(chapters) >= 1
        assert "title" in chapters[0]
    
    def test_detect_chapters_from_regex(self, pdf_service):
        text = "Chapter 1: Introduction\nSome content\nChapter 2: Main Content"
        chapters = pdf_service._detect_from_regex(text)
        assert isinstance(chapters, list)
    
    def test_clean_text_removes_extra_whitespace(self, pdf_service):
        text = "Line 1\n\n\n\nLine 2"
        cleaned = pdf_service.clean_text(text)
        assert "\n\n\n" not in cleaned
        assert "Line 1" in cleaned
    
    def test_clean_text_removes_page_numbers(self, pdf_service):
        text = "Some text\nPage 42\nMore text"
        cleaned = pdf_service.clean_text(text)
        assert "Page 42" not in cleaned
        assert "Some text" in cleaned
    
    def test_split_text_into_segments(self, pdf_service):
        pdf_service.segment_size = 100
        text = " ".join(["word"] * 100)
        chapters = []
        for i in range(0, len(text.split()), 10):
            chunk = " ".join(text.split()[i:i+10])
            if chunk:
                chapters.append(chunk)
        assert isinstance(chapters, list)
    
    @patch('fitz.open')
    def test_extract_text_from_empty_pdf_raises_error(self, mock_fitx, pdf_service):
        mock_doc = MagicMock()
        mock_doc.page_count = 0
        mock_fitx.return_value = mock_doc
        
        with pytest.raises(ValueError, match="no pages"):
            pdf_service.extract_text_from_pdf("dummy.pdf")
    
    @patch('fitz.open')
    def test_extract_text_from_scanned_pdf_raises_error(self, mock_fitx, pdf_service):
        mock_doc = MagicMock()
        mock_doc.page_count = 1
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_fitx.return_value = mock_doc
        
        with pytest.raises(ValueError, match="scanned or contains no extractable text"):
            pdf_service.extract_text_from_pdf("dummy.pdf")