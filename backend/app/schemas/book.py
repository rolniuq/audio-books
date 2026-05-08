from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChapterResponse(BaseModel):
    id: int
    chapter_number: int
    title: str
    content: Optional[str] = None
    audio_path: Optional[str] = None
    status: str
    duration_seconds: Optional[int] = None
    retry_count: int = 0
    last_error: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    title: str
    author: str = "Unknown"
    language: str = "vi-VN"
    voice: str = "vi-VN-HoaiNeural"

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    voice: Optional[str] = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    language: str
    voice: str
    pdf_path: Optional[str] = None
    status: str
    progress: float
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    chapters: List[ChapterResponse] = []
    
    class Config:
        from_attributes = True

class BookListResponse(BaseModel):
    books: List[BookResponse]
    total: int

class BookProgressResponse(BaseModel):
    id: int
    status: str
    progress: float
    error_message: Optional[str] = None
    chapters: List[ChapterResponse]

class VoiceInfo(BaseModel):
    name: str
    language: str
    gender: str

class VoiceListResponse(BaseModel):
    voices: List[VoiceInfo]

class ConvertRequest(BaseModel):
    voice: Optional[str] = None
    language: Optional[str] = None