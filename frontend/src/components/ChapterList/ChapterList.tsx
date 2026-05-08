import type { Chapter } from '../../types';
import { playChapter } from '../../store/playerStore';
import './ChapterList.css';

interface ChapterListProps {
  chapters: Chapter[];
  bookId: string;
  bookTitle: string;
}

export function ChapterList({ chapters, bookId, bookTitle }: ChapterListProps) {
  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusIcon = (status: Chapter['status']) => {
    switch (status) {
      case 'completed': return '▶️';
      case 'converting': return '🔄';
      case 'queued': return '⏳';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  const handlePlay = (chapter: Chapter) => {
    if (chapter.status === 'completed') {
      playChapter(chapter, { id: bookId, title: bookTitle, author: '', status: 'completed', createdAt: '', updatedAt: '' });
    }
  };

  return (
    <div className="chapter-list">
      <h3 className="chapter-list-title">Chapters</h3>
      <div className="chapters">
        {chapters.map((chapter) => (
          <div 
            key={chapter.id} 
            className={`chapter-item ${chapter.status}`}
            onClick={() => handlePlay(chapter)}
          >
            <div className="chapter-number">{chapter.number}</div>
            <div className="chapter-info">
              <span className="chapter-title">{chapter.title}</span>
              <span className="chapter-duration">
                {getStatusIcon(chapter.status)} {formatDuration(chapter.duration)}
              </span>
            </div>
            {chapter.status === 'converting' && (
              <div className="chapter-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${chapter.progress || 0}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}