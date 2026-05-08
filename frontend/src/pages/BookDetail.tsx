import { useParams, useNavigate } from 'react-router-dom';
import { useBook } from '../hooks/useBooks';
import { Header } from '../components/Layout/Header';
import { Sidebar } from '../components/Layout/Sidebar';
import { ChapterList } from '../components/ChapterList/ChapterList';
import './BookDetail.css';

export function BookDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: book, isLoading, error } = useBook(id || '');

  if (isLoading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="book-detail-loading">Loading...</div>
        </main>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="book-detail-error">Book not found</div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Header />
        
        <div className="book-detail">
          <button className="back-btn" onClick={() => navigate('/')}>
            ← Back to Library
          </button>

          <div className="book-header">
            <div className="book-cover-large">
              {book.coverUrl ? (
                <img src={book.coverUrl} alt={book.title} />
              ) : (
                <div className="cover-placeholder">📖</div>
              )}
            </div>
            <div className="book-info-large">
              <h1 className="book-title-large">{book.title}</h1>
              <p className="book-author-large">{book.author}</p>
              <div className={`book-status-large ${book.status}`}>
                {book.status === 'converting' && (
                  <div className="conversion-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-bar-fill" 
                        style={{ width: `${book.progress || 0}%` }}
                      />
                    </div>
                    <span>{book.progress || 0}% converting...</span>
                  </div>
                )}
                {book.status === 'completed' && <span>✅ Ready to play</span>}
                {book.status === 'failed' && <span>❌ Conversion failed</span>}
                {book.status === 'new' && <span>📖 New</span>}
              </div>
            </div>
          </div>

          <ChapterList 
            chapters={book.chapters} 
            bookId={book.id}
            bookTitle={book.title}
          />
        </div>
      </main>
    </div>
  );
}