import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBooks } from '../hooks/useBooks';
import { BookCard } from '../components/BookCard/BookCard';
import { Header } from '../components/Layout/Header';
import { Sidebar } from '../components/Layout/Sidebar';
import { UploadModal } from '../components/Upload/UploadModal';
import './Library.css';

export function Library() {
  const navigate = useNavigate();
  const { data: books, isLoading, error } = useBooks();
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  useEffect(() => {
    const handleOpenUpload = () => setIsUploadOpen(true);
    window.addEventListener('open-upload', handleOpenUpload);
    return () => window.removeEventListener('open-upload', handleOpenUpload);
  }, []);

  if (isLoading) {
    return (
      <div className="library-loading">
        <span className="animate-spin">🔄</span>
        <p>Loading books...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="library-error">
        <p>Failed to load books: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Header title="Library" />
        
        <div className="book-grid">
          {books && books.length > 0 ? (
            books.map((book) => (
              <BookCard
                key={book.id}
                book={book}
                onClick={() => navigate(`/book/${book.id}`)}
              />
            ))
          ) : (
            <div className="empty-state">
              <span className="empty-icon">📚</span>
              <h3>No books yet</h3>
              <p>Upload your first PDF to get started</p>
              <button className="btn btn-primary" onClick={() => setIsUploadOpen(true)}>
                Upload PDF
              </button>
            </div>
          )}
        </div>
      </main>

      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />
    </div>
  );
}