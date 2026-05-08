import type {
  Book,
  BookDetail,
  Voice,
  UploadResponse,
  ProgressResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  getBooks: () => fetchApi<Book[]>('/api/books'),

  getBook: (id: string) => fetchApi<BookDetail>(`/api/books/${id}`),

  deleteBook: (id: string) =>
    fetchApi<void>(`/api/books/${id}`, { method: 'DELETE' }),

  uploadBook: async (file: File, voiceId: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('voice_id', voiceId);

    const response = await fetch(`${API_BASE}/api/books/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new ApiError(response.status, error.detail || 'Upload failed');
    }

    return response.json();
  },

  startConversion: (bookId: string) =>
    fetchApi<void>(`/api/books/${bookId}/convert`, { method: 'POST' }),

  getProgress: (bookId: string) =>
    fetchApi<ProgressResponse>(`/api/books/${bookId}/progress`),

  getVoices: () => fetchApi<Voice[]>('/api/voices'),

  streamChapter: (chapterId: string) =>
    `${API_BASE}/api/chapters/${chapterId}/stream`,

  downloadChapter: (chapterId: string) =>
    `${API_BASE}/api/chapters/${chapterId}/download`,
};

export const STORAGE_KEYS = {
  PLAYBACK_POSITION: 'audiobook_playback_position',
  THEME: 'audiobook_theme',
};

export function savePlaybackPosition(bookId: string, chapterId: string, position: number) {
  const key = `${STORAGE_KEYS.PLAYBACK_POSITION}_${bookId}`;
  const data = JSON.parse(localStorage.getItem(key) || '{}');
  data[chapterId] = position;
  localStorage.setItem(key, JSON.stringify(data));
}

export function getPlaybackPosition(bookId: string, chapterId: string): number {
  const key = `${STORAGE_KEYS.PLAYBACK_POSITION}_${bookId}`;
  const data = JSON.parse(localStorage.getItem(key) || '{}');
  return data[chapterId] || 0;
}

export function saveTheme(theme: 'light' | 'dark') {
  localStorage.setItem(STORAGE_KEYS.THEME, theme);
  document.documentElement.setAttribute('data-theme', theme);
}

export function getTheme(): 'light' | 'dark' {
  const saved = localStorage.getItem(STORAGE_KEYS.THEME) as 'light' | 'dark' | null;
  return saved || 'dark';
}