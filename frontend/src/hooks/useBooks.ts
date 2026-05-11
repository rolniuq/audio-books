import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Book, BookDetail, Voice, UploadResponse, ProgressResponse } from '../types';

export const useBooks = () => {
  return useQuery<Book[]>({
    queryKey: ['books'],
    queryFn: api.getBooks,
    refetchInterval: 5000,
  });
};

export const useBook = (id: string) => {
  return useQuery<BookDetail>({
    queryKey: ['book', id],
    queryFn: () => api.getBook(id),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'converting') return 2000;
      return false;
    },
  });
};

export const useVoices = () => {
  return useQuery<Voice[]>({
    queryKey: ['voices'],
    queryFn: api.getVoices,
    staleTime: 1000 * 60 * 30,
  });
};

export const useUploadBook = () => {
  const queryClient = useQueryClient();

  return useMutation<UploadResponse, Error, { file: File; voiceId: string }>({
    mutationFn: ({ file, voiceId }) => api.uploadBook(file, voiceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useDeleteBook = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: api.deleteBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useStartConversion = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: api.startConversion,
    onSuccess: (_, bookId) => {
      queryClient.invalidateQueries({ queryKey: ['book', bookId] });
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useProgress = (bookId: string | null) => {
  return useQuery<ProgressResponse>({
    queryKey: ['progress', bookId],
    queryFn: () => api.getProgress(bookId!),
    enabled: !!bookId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return 2000;
      if (data.status === 'completed' || data.status === 'failed') return false;
      return 2000;
    },
  });
};