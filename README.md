# 🎧 AudioBook App

A free application that converts PDF files into audiobooks with Vietnamese voice reading. Features a fully separated Backend/Frontend architecture designed to support future expansion to mobile and desktop apps.

![AudioBook App](https://img.shields.io/badge/Status-Complete-success) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![React](https://img.shields.io/badge/React-18+-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688)

---

## ✨ Features

- 📄 **PDF Upload** - Drag & drop PDF files with voice selection
- 🔊 **Text-to-Speech** - High-quality Vietnamese voices via edge-tts (free, no API key)
- 📚 **Chapter Detection** - Automatic chapter splitting (TOC, heading-based, or fixed chunks)
- 🎵 **Audio Player** - Spotify-like persistent player with play/pause, seek, speed control
- 📊 **Real-time Progress** - Live conversion progress updates
- 💾 **Local Storage** - Playback position memory per book
- 📱 **Responsive Design** - Works on desktop and mobile browsers
- 🌙 **Dark Mode** - Beautiful glassmorphism UI with dark/light toggle

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│  🎧 AudioBook                         ⚙️  🌙/☀️    │
├──────────┬───────────────────────────────────────────┤
│          │                                           │
│ 📚 Library│   ┌───────┐ ┌───────┐ ┌───────┐         │
│          │   │  📖   │ │  📖   │ │  📖   │         │
│ 🕐 Recent │   │ Book1 │ │ Book2 │ │ Book3 │         │
│          │   │  75%  │ │ Done  │ │  New  │         │
│ ➕ Upload │   └───────┘ └───────┘ └───────┘         │
│          │                                           │
│          │   Chapters                                │
│          │   ├── Ch 1: Introduction      ▶️  05:30  │
│          │   ├── Ch 2: Getting Started   ▶️  12:45  │
│          │   ├── Ch 3: Deep Dive         🔄  ...    │
│          │   └── Ch 4: Conclusion        ⏳  Queue  │
│          │                                           │
├──────────┴───────────────────────────────────────────┤
│  ◀◀  ▶️  ▶▶  │  ━━━━━━━━●━━━━━━━━━  │  🔊 ████░░  │
│  Chapter 2    │  05:23 / 12:45       │  Speed: 1x  │
└──────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.11+ / FastAPI | Async API development |
| **PDF → Text** | PyMuPDF (fitz) | Fast PDF text extraction |
| **Text → Speech** | edge-tts | Free Vietnamese TTS (vi-VN-HoaiNeural) |
| **Database** | SQLite + SQLAlchemy | Simple, zero-setup storage |
| **Task Processing** | asyncio | Background tasks (no Redis needed) |
| **Frontend** | React + Vite + TypeScript | Fast, modern UI |
| **State Management** | Zustand | Lightweight global state |
| **Audio Player** | HTML5 Audio + custom UI | Browser-native playback |
| **Styling** | CSS3 + Glassmorphism | Dark mode, gradients, animations |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

### Docker Deployment (One-Command Setup)

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/books/upload` | Upload a PDF file, select voice/language |
| `GET` | `/api/books` | List all books with status |
| `GET` | `/api/books/{id}` | Get book detail including chapters |
| `DELETE` | `/api/books/{id}` | Delete book and all associated files |
| `POST` | `/api/books/{id}/convert` | Start or retry TTS conversion |
| `GET` | `/api/books/{id}/progress` | Get conversion progress (for polling) |
| `GET` | `/api/chapters/{id}/stream` | Stream chapter audio (supports range requests) |
| `GET` | `/api/chapters/{id}/download` | Download chapter as MP3 |
| `GET` | `/api/voices` | List available TTS voices |

---

## 🎯 Supported Voices

Default voice: `vi-VN-HoaiNeural` (Vietnamese female)

### Vietnamese Voices
- `vi-VN-HoaiNeural` (Female) - Default
- `vi-VN-NamMinhNeural` (Male)

### Other Languages (40+ supported)
- English: `en-US-JennyNeural`, `en-GB-SoniaNeural`
- Japanese: `ja-JP-NanamiNeural`
- Chinese: `zh-CN-XiaoxiaoNeural`
- And many more...

---

## 📂 Project Structure

```
audio-book/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Settings & configuration
│   │   ├── database.py       # SQLAlchemy setup
│   │   ├── models/           # Book, Chapter models
│   │   ├── schemas/          # Pydantic request/response
│   │   ├── api/              # REST API endpoints
│   │   ├── services/         # PDF, TTS, Book services
│   │   └── storage/          # Generated files (PDFs, MP3s)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/           # Library, BookDetail, Settings
│   │   ├── hooks/           # Custom hooks
│   │   ├── store/           # Zustand store
│   │   ├── api/             # API client
│   │   └── types/           # TypeScript interfaces
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml         # One-command deployment
├── docs/                     # Documentation
│   └── plan/               # Implementation plan
└── .c4/                     # C4 Multi-Agent AI Plugin
    ├── leader/              # Leader agent files
    ├── dev-1/               # Backend dev agent
    ├── dev-2/               # Frontend dev agent
    ├── dev-3/               # DevOps/Test agent
    └── _log/                # Event logs
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Build Verification

```bash
cd frontend
npm run build
```

### Manual Testing Checklist

- [ ] Upload a Vietnamese PDF → verify text extraction
- [ ] Upload an English PDF → verify it works
- [ ] Run conversion → verify audio quality and chapter splitting
- [ ] Play audio → verify streaming, seeking, chapter navigation
- [ ] Test on mobile browser → verify responsive layout
- [ ] Test error cases: corrupt PDF, empty PDF, very large PDF

---

## ⚠️ Important Notes

### TTS Engine: `edge-tts`
- ✅ **Completely free**, no API key needed
- ✅ **Vietnamese voices**: `vi-VN-HoaiNeural` (female), `vi-VN-NamMinhNeural` (male)
- ✅ **40+ languages** supported
- ✅ **Neural voice quality** - very natural sounding
- ✅ **No GPU required**, very fast
- ⚠️ **Requires internet** (sends text to Microsoft server)
- ⚠️ Excessive usage may trigger rate limiting

### Task Queue
This app uses **asyncio background tasks** instead of Celery + Redis for simplicity. Perfect for personal use. If you need persistent queues across restarts, you can upgrade to Celery later.

---

## 🎮 Development Phases (Completed)

- [x] **Phase 1: Core Backend** - FastAPI, SQLAlchemy, PDF/TTS services, API endpoints
- [x] **Phase 2: Frontend** - React setup, design system, pages, audio player
- [x] **Phase 3: Polish & Deployment** - Docker, testing, optimizations
- [ ] **Phase 4: Future Enhancements** - Mobile app, offline TTS, bookmarks

---

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 🙏 Acknowledgments

- [edge-tts](https://github.com/rany2/edge-tts) - Free Microsoft Edge TTS wrapper
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - Fast PDF processing
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library

---

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

**Built with ❤️ by the C4 Multi-Agent AI Team** (Leader + Dev-1 + Dev-2 + Dev-3)
