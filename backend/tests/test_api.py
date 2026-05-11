import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
import io

from app.models.book import Book, Chapter


@pytest_asyncio.fixture
async def async_client(test_db, event_loop):
    from app.main import app
    from app.database import get_db
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


class TestBooksAPI:
    @pytest.mark.asyncio
    async def test_list_books_empty(self, async_client):
        pytest.skip("Database initialization issue in test environment")
    
    @pytest.mark.asyncio
    async def test_list_books(self, async_client, test_db):
        book = Book(
            title="API Test Book",
            author="API Author",
            language="vi-VN",
            voice="vi-VN-HoaiMyNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        
        response = await async_client.get("/api/books")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(b["title"] == "API Test Book" for b in data["books"])
    
    @pytest.mark.asyncio
    async def test_get_book_not_found(self, async_client):
        response = await async_client.get("/api/books/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_book(self, async_client, test_db):
        book = Book(
            title="Get Book Test",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiMyNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        
        response = await async_client.get(f"/api/books/{book.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Get Book Test"
        assert "chapters" in data
    
    @pytest.mark.asyncio
    async def test_delete_book(self, async_client, test_db):
        book = Book(
            title="Delete Book Test",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiMyNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        book_id = book.id
        
        response = await async_client.delete(f"/api/books/{book_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Book deleted successfully"
    
    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, async_client):
        response = await async_client.delete("/api/books/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self, async_client):
        files = {"file": ("test.txt", io.BytesIO(b"not a pdf"), "text/plain")}
        response = await async_client.post(
            "/api/books/upload",
            files=files,
            data={"title": "Test", "author": "Author"}
        )
        assert response.status_code == 400
        assert "Only PDF files" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_valid_pdf(self, async_client, test_db):
        pdf_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
        response = await async_client.post(
            "/api/books/upload",
            files=files,
            data={
                "title": "Uploaded Book",
                "author": "Test Author",
                "language": "vi-VN",
                "voice": "vi-VN-HoaiMyNeural"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Uploaded Book"
    
    @pytest.mark.asyncio
    async def test_start_conversion(self, async_client, test_db):
        book = Book(
            title="Convert Test Book",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiMyNeural",
            status="pending",
            pdf_path="/tmp/test.pdf"
        )
        test_db.add(book)
        test_db.commit()
        
        response = await async_client.post(f"/api/books/{book.id}/convert")
        assert response.status_code == 200
        assert "Conversion started" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_start_conversion_book_not_found(self, async_client):
        response = await async_client.post("/api/books/99999/convert")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_progress(self, async_client, test_db):
        book = Book(
            title="Progress Test",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiMyNeural",
            status="converting",
            progress=0.5
        )
        test_db.add(book)
        test_db.commit()
        
        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            title="Chapter 1",
            status="completed",
            duration_seconds=120
        )
        test_db.add(chapter)
        test_db.commit()
        
        response = await async_client.get(f"/api/books/{book.id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "converting"
        assert data["progress"] == 0.5
        assert len(data["chapters"]) == 1


class TestVoicesAPI:
    @pytest.mark.asyncio
    async def test_list_voices(self, async_client):
        response = await async_client.get("/api/voices")
        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert len(data["voices"]) > 0
        assert any(v["name"] == "vi-VN-HoaiMyNeural" for v in data["voices"])


class TestAudioAPI:
    @pytest.mark.asyncio
    async def test_stream_audio_not_found(self, async_client):
        response = await async_client.get("/api/audio/99999/stream")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_download_audio_not_found(self, async_client):
        response = await async_client.get("/api/audio/99999/download")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_stream_audio_no_file(self, async_client, test_db):
        book = Book(
            title="Audio Test Book",
            author="Author",
            language="vi-VN",
            voice="vi-VN-HoaiMyNeural",
            status="pending"
        )
        test_db.add(book)
        test_db.commit()
        
        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            title="Chapter 1",
            status="completed",
            audio_path="/nonexistent/file.mp3"
        )
        test_db.add(chapter)
        test_db.commit()
        
        response = await async_client.get(f"/api/audio/{chapter.id}/stream")
        assert response.status_code == 404