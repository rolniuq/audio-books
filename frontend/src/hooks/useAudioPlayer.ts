import { useEffect, useRef, useCallback } from 'react';
import { usePlayerStore } from '../store/playerStore';
import { api, savePlaybackPosition, getPlaybackPosition } from '../api/client';

export function useAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const {
    currentChapter,
    currentBook,
    isPlaying,
    duration,
    volume,
    playbackRate,
    setIsPlaying,
    setCurrentTime,
    setDuration,
  } = usePlayerStore();

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.preload = 'metadata';
    }

    const audio = audioRef.current;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
      if (currentBook && currentChapter) {
        savePlaybackPosition(currentBook.id, currentChapter.id, audio.currentTime);
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      const savedPosition = currentBook && currentChapter 
        ? getPlaybackPosition(currentBook.id, currentChapter.id)
        : 0;
      if (savedPosition > 0 && savedPosition < audio.duration - 1) {
        audio.currentTime = savedPosition;
      }
    };

    const handleEnded = () => {
      setIsPlaying(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [currentBook, currentChapter, setCurrentTime, setDuration, setIsPlaying]);

  useEffect(() => {
    if (currentChapter && currentBook) {
      const audio = audioRef.current;
      if (audio) {
        audio.src = api.streamChapter(currentChapter.id);
        audio.load();
      }
    }
  }, [currentChapter, currentBook]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackRate;
    }
  }, [playbackRate]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !currentChapter) return;

    if (isPlaying) {
      audio.play().catch(() => setIsPlaying(false));
    } else {
      audio.pause();
    }
  }, [isPlaying, currentChapter, setIsPlaying]);

  const seek = useCallback((time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  }, [setCurrentTime]);

  const skipForward = useCallback((seconds: number = 10) => {
    if (audioRef.current) {
      const newTime = Math.min(audioRef.current.currentTime + seconds, duration);
      seek(newTime);
    }
  }, [duration, seek]);

  const skipBackward = useCallback((seconds: number = 10) => {
    if (audioRef.current) {
      const newTime = Math.max(audioRef.current.currentTime - seconds, 0);
      seek(newTime);
    }
  }, [seek]);

  return {
    audioRef,
    seek,
    skipForward,
    skipBackward,
  };
}