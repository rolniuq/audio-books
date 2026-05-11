import type { Book } from '../../types';
import { ProgressBar } from '../ProgressBar/ProgressBar';
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

  const getChapterInfo = () => {
    if (book.status === 'converting' && book.chapters) {
      const totalChapters = book.chapters.length;
      const completedChapters = book.chapters.filter(c => c.status === 'completed').length;
      return `Chapter ${completedChapters + 1} of ${totalChapters}`;
    }
    return undefined;
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
            {getStatusIcon()} {Math.round((book.progress || 0) * 100)}%
          </span>
        </div>
      </div>
      <div className="book-info">
        <h3 className="book-title">{book.title}</h3>
        <p className="book-author">{book.author}</p>
      </div>
      {book.status === 'converting' && (
        <div className="book-progress">
          <ProgressBar
            progress={book.progress || 0}
            status={book.status}
            chapterInfo={getChapterInfo()}
            size="sm"
          />
        </div>
      )}
    </div>
  );
}