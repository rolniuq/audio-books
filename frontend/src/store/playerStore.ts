import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Chapter, Book, PlayerState } from '../types';

interface PersistedState {
  playbackPosition: Record<string, number>;
  defaultPlaybackRate: number;
  defaultVoice: string;
  theme: 'dark' | 'light';
}

export const usePlayerStore = create<PlayerState & PersistedState>()(
  persist(
    (set, get) => ({
      currentChapter: null,
      currentBook: null,
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      volume: 1,
      playbackRate: 1,
      playbackPosition: {},
      defaultPlaybackRate: 1,
      defaultVoice: 'vi-VN-HoaiNeural',
      theme: 'dark',

      setCurrentChapter: (chapter) => set({ currentChapter: chapter }),
      setCurrentBook: (book) => set({ currentBook: book }),
      setIsPlaying: (isPlaying) => set({ isPlaying }),
      setCurrentTime: (currentTime) => set({ currentTime }),
      setDuration: (duration) => set({ duration }),
      setVolume: (volume) => set({ volume }),
      setPlaybackRate: (playbackRate) => set({ playbackRate }),
      play: () => set({ isPlaying: true }),
      pause: () => set({ isPlaying: false }),
      togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),

      getPlaybackPosition: (chapterId: string) => {
        const positions = get().playbackPosition;
        return positions[chapterId] || 0;
      },

      savePlaybackPosition: (chapterId: string, position: number) => {
        const positions = { ...get().playbackPosition, [chapterId]: position };
        set({ playbackPosition: positions });
      },

      clearPlaybackPosition: (chapterId: string) => {
        const positions = { ...get().playbackPosition };
        delete positions[chapterId];
        set({ playbackPosition: positions });
      },

      setDefaultPlaybackRate: (rate: number) => set({ defaultPlaybackRate: rate }),
      setDefaultVoice: (voice: string) => set({ defaultVoice: voice }),
      setTheme: (theme: 'dark' | 'light') => set({ theme }),
      clearAllData: () => set({
        playbackPosition: {},
        defaultPlaybackRate: 1,
        defaultVoice: 'vi-VN-HoaiNeural',
        theme: 'dark'
      }),
    }),
    {
      name: 'audiobook-settings',
      partialize: (state) => ({
        playbackPosition: state.playbackPosition,
        defaultPlaybackRate: state.defaultPlaybackRate,
        defaultVoice: state.defaultVoice,
        theme: state.theme,
      }),
    }
  )
);

export const playChapter = (chapter: Chapter, book: Book) => {
  const store = usePlayerStore.getState();
  const savedPosition = store.getPlaybackPosition(chapter.id);
  
  store.setCurrentChapter(chapter);
  store.setCurrentBook(book);
  store.setCurrentTime(savedPosition);
  store.setPlaybackRate(store.defaultPlaybackRate);
  store.play();
};

export const stopPlayback = () => {
  const store = usePlayerStore.getState();
  const chapter = store.currentChapter;
  const time = store.currentTime;
  
  if (chapter && time > 0) {
    store.savePlaybackPosition(chapter.id, time);
  }
  
  store.setCurrentChapter(null);
  store.setCurrentBook(null);
  store.setIsPlaying(false);
  store.setCurrentTime(0);
  store.setDuration(0);
};

export const onChapterComplete = () => {
  const store = usePlayerStore.getState();
  const chapter = store.currentChapter;
  
  if (chapter) {
    store.clearPlaybackPosition(chapter.id);
  }
  
  store.pause();
};