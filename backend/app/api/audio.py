import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Chapter

router = APIRouter()

@router.get("/{chapter_id}/stream")
def stream_audio(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.audio_path or not os.path.exists(chapter.audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    file_size = os.path.getsize(chapter.audio_path)
    
    def generate_range():
        with open(chapter.audio_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
    
    return StreamingResponse(
        generate_range(),
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Disposition": f"inline; filename=chapter_{chapter_id}.mp3"
        }
    )

@router.get("/{chapter_id}/download")
def download_audio(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.audio_path or not os.path.exists(chapter.audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    file_size = os.path.getsize(chapter.audio_path)
    
    def generate():
        with open(chapter.audio_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="audio/mpeg",
        headers={
            "Content-Length": str(file_size),
            "Content-Disposition": f"attachment; filename=chapter_{chapter.chapter_number}.mp3"
        }
    )