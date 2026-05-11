# Audio Book Project - Context for AI Assistant

## Project Overview
PDF to audio converter with web interface. Users upload PDF files, system converts to audio chapters using TTS.

## Tech Stack
- **Frontend**: React + TypeScript + Vite
- **Backend**: Python FastAPI
- **Database**: SQLite
- **Audio**: TTS using Windows SAPI voices via COM interface in Docker

## Running Services
- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (internal, via nginx)
- Docker containers: `audiobook-frontend`, `audiobook-backend`

## Key Endpoints
- `GET /api/books` - List all books
- `GET /api/books/{id}` - Book details with chapters
- `POST /api/books/upload` - Upload PDF
- `GET /api/audio/{chapter_id}/stream` - Stream chapter audio

## Project Structure
```
backend/
├── app/
│   ├── api/          # API routes (books.py, audio.py)
│   ├── models/       # SQLAlchemy models (Book, Chapter)
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic (book_service.py, pdf_service.py, tts_service.py)
│   └── config.py     # Configuration
frontend/
├── src/
│   ├── api/          # API client
│   ├── components/   # React components
│   ├── hooks/        # Custom hooks (useBooks, useAudioPlayer)
│   ├── pages/        # Page components (Library, BookDetail)
│   ├── store/        # Zustand store (playerStore)
│   └── types/        # TypeScript types
```

## Current Known Issues
- Audio content may not match PDF text (needs investigation)
- Chapter extraction can produce empty content for some chapters

## Recent Changes (2026-05-11)
- Fixed progress bar display (was showing 0.75% instead of 75%)
- Added "Play All" button on book detail page
- Implemented chapter queue for sequential playback
- Cleaned up duplicate chapters in database

## Docker Commands
```bash
# View containers
docker ps

# View logs
docker logs audiobook-backend
docker logs audiobook-frontend

# Access container
docker exec -it audiobook-backend /bin/bash

# Rebuild
docker compose up -d --build
```

## Database
- SQLite at `backend/data/audiobook.db`
- Access: `docker exec audiobook-backend python3 -c "from app.database import SessionLocal; ..."`

## Key Files to Remember
- `frontend/src/store/playerStore.ts` - Audio playback state management
- `backend/app/services/tts_service.py` - TTS conversion logic
- `backend/app/services/pdf_service.py` - PDF text extraction