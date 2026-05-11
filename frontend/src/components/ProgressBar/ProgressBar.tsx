import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  status: 'new' | 'converting' | 'completed' | 'failed';
  chapterInfo?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function ProgressBar({ progress, status, chapterInfo, size = 'md' }: ProgressBarProps) {
  const getStatusText = () => {
    switch (status) {
      case 'new': return 'Waiting';
      case 'converting': return 'Converting';
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      default: return '';
    }
  };

  const getColorClass = () => {
    switch (status) {
      case 'completed': return 'progress-success';
      case 'failed': return 'progress-error';
      default: return 'progress-active';
    }
  };

  return (
    <div className={`progress-container size-${size}`}>
      <div className="progress-header">
        <span className={`progress-status ${getColorClass()}`}>
          {status === 'converting' && '⚡ '}
          {status === 'completed' && '✓ '}
          {status === 'failed' && '✗ '}
          {getStatusText()}
        </span>
        <span className="progress-percentage">{Math.round(progress * 100)}%</span>
      </div>
      <div className="progress-track">
        <div 
          className={`progress-fill ${getColorClass()}`}
          style={{ width: `${Math.round(progress * 100)}%` }}
        />
      </div>
      {chapterInfo && (
        <div className="progress-chapter-info">{chapterInfo}</div>
      )}
    </div>
  );
}