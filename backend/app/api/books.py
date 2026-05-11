import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.book import Book, Chapter
from app.schemas.book import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookListResponse,
    BookProgressResponse,
    VoiceListResponse,
    VoiceInfo,
    ConvertRequest
)
from app.services.book_service import BookService
from app.services.tts_service import TTSService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
voices_router = APIRouter()

book_service = BookService()
tts_service = TTSService()

@router.post("/upload", response_model=BookResponse)
async def upload_book(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    author: str = "Unknown",
    language: str = "vi-VN",
    voice: str = "vi-VN-HoaiMyNeural",
    voice_id: Optional[str] = None,
    auto_convert: bool = True,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Upload request: filename={file.filename}, title={title}, voice={voice}, voice_id={voice_id}")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Use voice_id if provided
        if voice_id:
            voice = voice_id
        
        # Use filename as title if not provided
        if not title:
            title = file.filename.replace('.pdf', '').replace('.PDF', '')
        
        book = book_service.create_book_from_upload(db, file, title, author, language, voice)
        logger.info(f"Book created successfully: id={book.id}, title={book.title}")
        
        if auto_convert and background_tasks:
            logger.info(f"Auto-converting book {book.id}")
            book.status = "pending"
            db.commit()
            background_tasks.add_task(book_service.convert_book_to_audio, db, book.id)
        
        return book
    except HTTPException as he:
        raise
    except Exception as e:
        logger.error(f"Error in upload_book: {str(e)}", exc_info=True)
        raise

@router.get("", response_model=BookListResponse)
def list_books(db: Session = Depends(get_db)):
    from app.schemas.book import BookListItem
    books = db.query(Book).order_by(Book.created_at.desc()).all()
    book_items = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "language": book.language,
            "voice": book.voice,
            "pdf_path": book.pdf_path,
            "status": book.status,
            "progress": book.progress,
            "error_message": book.error_message,
            "created_at": book.created_at,
            "updated_at": book.updated_at,
            "chapters": []
        }
        for book in books
    ]
    return {"books": book_items, "total": len(books)}

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapters = db.query(Chapter).filter(Chapter.book_id == book_id).order_by(Chapter.chapter_number).all()
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "language": book.language,
        "voice": book.voice,
        "pdf_path": book.pdf_path,
        "status": book.status,
        "progress": book.progress,
        "error_message": book.error_message,
        "created_at": book.created_at,
        "updated_at": book.updated_at,
        "chapters": [
            {
                "id": ch.id,
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "content": None,
                "audio_path": ch.audio_path,
                "status": ch.status,
                "duration_seconds": ch.duration_seconds,
                "retry_count": ch.retry_count,
                "last_error": ch.last_error,
                "created_at": ch.created_at
            }
            for ch in chapters
        ]
    }

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = book_service.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book deleted successfully"}

@router.post("/{book_id}/convert")
def start_conversion(
    book_id: int,
    background_tasks: BackgroundTasks,
    request: ConvertRequest = ConvertRequest(),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if request.voice:
        book.voice = request.voice
    if request.language:
        book.language = request.language
    
    book.status = "pending"
    book.progress = 0.0
    book.updated_at = None
    db.commit()
    
    background_tasks.add_task(book_service.convert_book_to_audio, db, book_id)
    
    return {"message": "Conversion started", "book_id": book_id}

@router.get("/{book_id}/progress", response_model=BookProgressResponse)
def get_progress(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapters = db.query(Chapter).filter(Chapter.book_id == book_id).order_by(Chapter.chapter_number).all()
    
    return {
        "id": book.id,
        "status": book.status,
        "progress": book.progress,
        "error_message": book.error_message,
        "chapters": chapters
    }

@voices_router.get("", response_model=VoiceListResponse)
def list_voices():
    voices = [
        VoiceInfo(name=v["name"], language=v["language"], gender=v["gender"])
        for v in tts_service.get_voices()
    ]
    return {"voices": voices}