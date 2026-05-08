import type { Book } from '../../types';
import './BookCard.css';

interface BookCardProps {
  book: Book;
  onClick: () => void;
}

export function BookCard({ book, onClick }: BookCardProps) {
  const getStatusIcon = () => {
    switch (book.status) {
      case 'new': return '📖';
      case 'converting': return '🔄';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '📖';
    }
  };

  const getStatusText = () => {
    switch (book.status) {
      case 'new': return 'New';
      case 'converting': return `${book.progress || 0}%`;
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      default: return 'Unknown';
    }
  };

  return (
    <div className="book-card glass-card" onClick={onClick}>
      <div className="book-cover">
        {book.coverUrl ? (
          <img src={book.coverUrl} alt={book.title} />
        ) : (
          <div className="book-cover-placeholder">📖</div>
        )}
        <div className="book-status">
          <span className={`status-badge ${book.status}`}>
            {getStatusIcon()} {getStatusText()}
          </span>
        </div>
      </div>
      <div className="book-info">
        <h3 className="book-title">{book.title}</h3>
        <p className="book-author">{book.author}</p>
      </div>
      {book.status === 'converting' && (
        <div className="book-progress">
          <div className="progress-bar">
            <div 
              className="progress-bar-fill" 
              style={{ width: `${book.progress || 0}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}