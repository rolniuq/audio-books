import { useAudioPlayer } from '../../hooks/useAudioPlayer';
import { usePlayerStore } from '../../store/playerStore';
import './AudioPlayer.css';

export function AudioPlayer() {
  const { seek, skipForward, skipBackward } = useAudioPlayer();
  const {
    currentChapter,
    currentBook,
    isPlaying,
    currentTime,
    duration,
    volume,
    playbackRate,
    setVolume,
    setPlaybackRate,
    togglePlay,
  } = usePlayerStore();

  if (!currentChapter || !currentBook) return null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    seek(parseFloat(e.target.value));
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVolume(parseFloat(e.target.value));
  };

  const playbackRates = [0.5, 0.75, 1, 1.25, 1.5, 2];

  return (
    <div className="audio-player">
      <div className="player-controls">
        <button className="control-btn" onClick={() => skipBackward(10)} aria-label="Skip back 10s">
          ◀◀
        </button>
        <button className="control-btn play-btn" onClick={togglePlay} aria-label={isPlaying ? 'Pause' : 'Play'}>
          {isPlaying ? '⏸' : '▶️'}
        </button>
        <button className="control-btn" onClick={() => skipForward(10)} aria-label="Skip forward 10s">
          ▶▶
        </button>
      </div>

      <div className="player-info">
        <div className="player-track">
          <span className="track-title">{currentChapter.title}</span>
          <span className="track-time">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>
        <input
          type="range"
          className="seek-slider"
          min={0}
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
        />
      </div>

      <div className="player-extras">
        <div className="speed-control">
          <select
            value={playbackRate}
            onChange={(e) => setPlaybackRate(parseFloat(e.target.value))}
          >
            {playbackRates.map((rate) => (
              <option key={rate} value={rate}>
                {rate}x
              </option>
            ))}
          </select>
        </div>
        <div className="volume-control">
          <span>🔊</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.1}
            value={volume}
            onChange={handleVolumeChange}
          />
        </div>
      </div>
    </div>
  );
}