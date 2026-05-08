from fastapi import APIRouter
from app.api import books, audio

api_router = APIRouter()

api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(audio.router, prefix="/chapters", tags=["audio"])
api_router.include_router(books.voices_router, prefix="/voices", tags=["voices"])