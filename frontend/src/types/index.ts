export type BookStatus = 'new' | 'converting' | 'completed' | 'failed';

export interface Book {
  id: string;
  title: string;
  author: string;
  coverUrl?: string;
  status: BookStatus;
  progress?: number;
  createdAt: string;
  updatedAt: string;
}

export type ChapterStatus = 'queued' | 'converting' | 'completed' | 'failed';

export interface Chapter {
  id: string;
  bookId: string;
  number: number;
  title: string;
  status: ChapterStatus;
  duration?: number;
  audioUrl?: string;
  progress?: number;
}

export interface BookDetail extends Book {
  chapters: Chapter[];
}

export interface Voice {
  id: string;
  name: string;
  language: string;
  gender?: string;
}

export interface UploadResponse {
  bookId: string;
  message: string;
}

export interface ProgressResponse {
  bookId: string;
  status: BookStatus;
  progress: number;
  chapters: {
    id: string;
    status: ChapterStatus;
    progress: number;
  }[];
}

export interface PlayerState {
  currentChapter: Chapter | null;
  currentBook: Book | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  playbackRate: number;
  playbackPosition: Record<string, number>;
  defaultPlaybackRate: number;
  defaultVoice: string;
  theme: 'dark' | 'light';
  setCurrentChapter: (chapter: Chapter | null) => void;
  setCurrentBook: (book: Book | null) => void;
  setIsPlaying: (playing: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (volume: number) => void;
  setPlaybackRate: (rate: number) => void;
  play: () => void;
  pause: () => void;
  togglePlay: () => void;
  getPlaybackPosition: (chapterId: string) => number;
  savePlaybackPosition: (chapterId: string, position: number) => void;
  clearPlaybackPosition: (chapterId: string) => void;
  setDefaultPlaybackRate: (rate: number) => void;
  setDefaultVoice: (voice: string) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  clearAllData: () => void;
}