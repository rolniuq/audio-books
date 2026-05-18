import os
import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
from datetime import datetime

from app.config import settings
from app.models.book import Book, Chapter
from app.services.pdf_service import PDFService
from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.tts_service = TTSService()
    
    def create_book_from_upload(self, db: Session, file: UploadFile, title: str, author: str, language: str, voice: str) -> Book:
        os.makedirs(settings.BOOKS_DIR, exist_ok=True)
        
        book_dir = os.path.join(settings.BOOKS_DIR, f"book_{datetime.now().timestamp()}")
        os.makedirs(book_dir, exist_ok=True)
        
        pdf_path = os.path.join(book_dir, file.filename)
        
        with open(pdf_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        book = Book(
            title=title,
            author=author,
            language=language,
            voice=voice,
            pdf_path=pdf_path,
            status="pending",
            progress=0.0
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        
        return book
    
    async def convert_book_to_audio(self, db: Session, book_id: int):
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.error(f"Book {book_id} not found")
            return
        
        try:
            book.status = "extracting"
            book.updated_at = datetime.utcnow()
            db.commit()
            
            chapters_data = self._extract_chapters(db, book)
            
            book.status = "converting"
            book.updated_at = datetime.utcnow()
            db.commit()
            
            await self._convert_chapters(db, book, chapters_data)
            
            book.status = "completed"
            book.progress = 1.0
            book.updated_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            logger.error(f"Error converting book {book_id}: {str(e)}")
            book.status = "failed"
            book.error_message = str(e)
            book.updated_at = datetime.utcnow()
            db.commit()
    
    def _extract_chapters(self, db: Session, book: Book):
        full_text, chapter_info = self.pdf_service.extract_text_from_pdf(book.pdf_path)
        logger.info(f"PDF extraction complete: {len(full_text)} chars, {len(chapter_info)} chapters")
        logger.debug(f"Sample extracted text (first 200 chars): {repr(full_text[:200])}")
        chapters = []
        for i, info in enumerate(chapter_info):
            if "start_page" in info:
                text = self.pdf_service.extract_chapter_text(
                    book.pdf_path,
                    info["start_page"],
                    info.get("end_page")
                )
            elif "start_pos" in info and "end_pos" in info:
                text = full_text[info["start_pos"]:info["end_pos"]]
            else:
                logger.warning(f"Chapter {i+1}: missing position info")
                continue
            
            if not text or not text.strip():
                logger.warning(f"Chapter {i+1} ('{info.get('title')}'): empty content after extraction")
            
            chapter = Chapter(
                book_id=book.id,
                chapter_number=i + 1,
                title=info.get("title", f"Chapter {i + 1}"),
                content=text,
                status="pending"
            )
            db.add(chapter)
            chapters.append(chapter)
        
        db.commit()
        db.refresh(book)
        
        return chapters
    
    async def _convert_chapters(self, db: Session, book: Book, chapters: list):
        from app.config import settings
        book_dir = os.path.join(settings.BOOKS_DIR, f"book_{book.id}")
        os.makedirs(book_dir, exist_ok=True)
        
        total_chapters = len(chapters)
        completed_chapters = 0
        failed_chapters = []
        
        for i, chapter in enumerate(chapters):
            chapter.status = "converting"
            db.commit()
            
            if not chapter.content or not chapter.content.strip():
                chapter.status = "skipped"
                chapter.last_error = "Empty content"
                db.commit()
                logger.warning(f"Chapter {chapter.chapter_number} skipped: empty content")
                continue
            
            try:
                audio_path = os.path.join(book_dir, f"chapter_{chapter.chapter_number}.mp3")
                
                def on_retry(attempt: int, error: str):
                    chapter.retry_count = attempt
                    chapter.last_error = error
                    db.commit()
                    logger.warning(f"Chapter {chapter.chapter_number} retry {attempt}: {error}")
                
                text_length = len(chapter.content)
                timeout_seconds = min(600, 60 + text_length // 50)
                
                await asyncio.wait_for(
                    self.tts_service._convert_text_to_audio_async(
                        text=chapter.content,
                        output_path=audio_path,
                        voice=book.voice,
                        on_retry=on_retry
                    ),
                    timeout=timeout_seconds
                )
                
                chapter.audio_path = audio_path
                chapter.status = "completed"
                chapter.last_error = None
                
                duration = self.tts_service.get_audio_duration(audio_path)
                chapter.duration_seconds = duration
                
                db.commit()
                completed_chapters += 1
                
                progress = (i + 1) / total_chapters
                book.progress = progress
                book.updated_at = datetime.utcnow()
                db.commit()
                
            except asyncio.TimeoutError:
                logger.error(f"Chapter {chapter.chapter_number} timed out after {timeout_seconds}s ({text_length} chars)")
                chapter.status = "failed"
                chapter.last_error = f"Timeout after {timeout_seconds}s"
                db.commit()
                failed_chapters.append(chapter.chapter_number)
            except Exception as e:
                logger.error(f"Error converting chapter {chapter.chapter_number}: {str(e)}")
                chapter.status = "failed"
                chapter.last_error = str(e)
                db.commit()
                failed_chapters.append(chapter.chapter_number)
        
        if failed_chapters:
            logger.warning(f"Failed chapters for book {book.id}: {failed_chapters}")
    
    def delete_book(self, db: Session, book_id: int) -> bool:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return False
        
        if book.pdf_path and os.path.exists(book.pdf_path):
            book_dir = os.path.dirname(book.pdf_path)
            if os.path.exists(book_dir):
                import shutil
                shutil.rmtree(book_dir)
        
        db.delete(book)
        db.commit()
        
        return True
    
    def retry_conversion(self, db: Session, book_id: int, new_voice: Optional[str] = None, new_language: Optional[str] = None):
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None
        
        if new_voice:
            book.voice = new_voice
        if new_language:
            book.language = new_language
        
        book.status = "pending"
        book.progress = 0.0
        book.error_message = None
        book.updated_at = datetime.utcnow()
        
        chapters = db.query(Chapter).filter(Chapter.book_id == book_id).all()
        for chapter in chapters:
            chapter.status = "pending"
            if os.path.exists(chapter.audio_path):
                os.remove(chapter.audio_path)
            chapter.audio_path = None
            chapter.duration_seconds = None
        
        db.commit()
        
        return book