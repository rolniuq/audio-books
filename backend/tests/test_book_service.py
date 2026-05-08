import pytest
import os
import io
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from fastapi import UploadFile

from app.models.book import Book, Chapter
from app.services.book_service import BookService


class TestBookService:
    @pytest.fixture
    def book_service(self):
        return BookService()
    
    def test_create_book_from_upload(self, book_service, test_db):
        pdf_content = b"%PDF-1.4 test content"
        file = MagicMock(spec=UploadFile)
        file.filename = "test.pdf"
        file.file = io.BytesIO(pdf_content)
        
        with patch('app.services.book_service.settings') as mock_settings:
            mock_settings.BOOKS_DIR = "/tmp/test_books"
            book = book_service.create_book_from_upload(
                test_db, file, "Test Book", "Test Author", "vi-VN", "vi-VN-HoaiNeural"
            )
        
        assert book is not None
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.status == "pending"
        assert book.progress == 0.0
        
        test_db.query(Book).filter(Book.id == book.id).delete()
        test_db.commit()
    
    def test_delete_book(self, book_service, test_db):
        book = Book(
            title="Delete Test",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiNeural",
            pdf_path="/tmp/test.pdf",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        book_id = book.id
        
        result = book_service.delete_book(test_db, book_id)
        
        assert result is True
        assert test_db.query(Book).filter(Book.id == book_id).first() is None
    
    def test_delete_nonexistent_book(self, book_service, test_db):
        result = book_service.delete_book(test_db, 99999)
        assert result is False
    
    def test_retry_conversion(self, book_service, test_db):
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            book = Book(
                title="Retry Test",
                author="Author",
                language="vi-VN",
                voice="vi-VN-HoaiNeural",
                status="failed",
                progress=0.5,
                error_message="Previous error"
            )
            test_db.add(book)
            test_db.commit()
            
            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                title="Chapter 1",
                status="failed",
                content="Test content",
                audio_path=os.path.join(temp_dir, "existing.mp3")
            )
            test_db.add(chapter)
            test_db.commit()
            
            with patch('app.services.book_service.settings') as mock_settings:
                mock_settings.BOOKS_DIR = temp_dir
                
                result = book_service.retry_conversion(test_db, book.id, new_voice="en-US-JennyNeural")
            
            assert result is not None
            assert result.status == "pending"
            assert result.progress == 0.0
            assert result.error_message is None
            assert result.voice == "en-US-JennyNeural"
            
            test_db.query(Book).filter(Book.id == book.id).delete()
            test_db.commit()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_retry_conversion_book_not_found(self, book_service, test_db):
        result = book_service.retry_conversion(test_db, 99999)
        assert result is None


class TestBookModel:
    def test_book_creation(self, test_db):
        book = Book(
            title="Test Book",
            author="Test Author",
            language="vi-VN",
            voice="vi-VN-HoaiNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        
        assert book.id is not None
        assert book.status == "pending"
        assert book.progress == 0.0
        
        test_db.query(Book).filter(Book.id == book.id).delete()
        test_db.commit()
    
    def test_book_with_chapters(self, test_db):
        book = Book(
            title="Test Book with Chapters",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        
        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            title="Chapter 1",
            content="Content here",
            status="pending"
        )
        test_db.add(chapter)
        test_db.commit()
        
        assert len(book.chapters) == 1
        assert book.chapters[0].title == "Chapter 1"
        
        test_db.query(Chapter).filter(Chapter.book_id == book.id).delete()
        test_db.query(Book).filter(Book.id == book.id).delete()
        test_db.commit()
    
    def test_chapter_retry_tracking(self, test_db):
        book = Book(
            title="Retry Test Book",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        
        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            title="Chapter 1",
            content="Content",
            status="failed",
            retry_count=2,
            last_error="Network timeout"
        )
        test_db.add(chapter)
        test_db.commit()
        
        assert chapter.retry_count == 2
        assert chapter.last_error == "Network timeout"
        
        test_db.query(Chapter).filter(Chapter.book_id == book.id).delete()
        test_db.query(Book).filter(Book.id == book.id).delete()
        test_db.commit()