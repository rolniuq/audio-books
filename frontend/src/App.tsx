import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Library } from './pages/Library';
import { BookDetail } from './pages/BookDetail';
import { Settings } from './pages/Settings';
import { AudioPlayer } from './components/AudioPlayer/AudioPlayer';
import './index.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Library />} />
          <Route path="/book/:id" element={<BookDetail />} />
          <Route path="/recent" element={<Library />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
        <AudioPlayer />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;