import { useState, useCallback, useEffect } from 'react';
import { useVoices, useUploadBook, useStartConversion } from '../../hooks/useBooks';
import './UploadModal.css';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const { data: voices, isLoading: loadingVoices } = useVoices();
  const uploadMutation = useUploadBook();
  const conversionMutation = useStartConversion();
  
  const [file, setFile] = useState<File | null>(null);
  const [selectedVoice, setSelectedVoice] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const defaultVietnameseVoices = [
    { id: 'vi-VN-HoaiNeural', name: 'HoaiNeural (Female)', language: 'vi-VN' },
    { id: 'vi-VN-NamMinhNeural', name: 'NamMinhNeural (Male)', language: 'vi-VN' },
  ];

  useEffect(() => {
    if (voices && voices.length > 0 && !selectedVoice) {
      const vietnameseVoice = voices.find(v => v.language.startsWith('vi'));
      if (vietnameseVoice) {
        setSelectedVoice(vietnameseVoice.id);
      }
    }
  }, [voices, selectedVoice]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please drop a PDF file');
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile?.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file || !selectedVoice) return;
    
    try {
      setUploadProgress(0);
      const result = await uploadMutation.mutateAsync({ file, voiceId: selectedVoice });
      setUploadProgress(100);
      
      await conversionMutation.mutateAsync(result.bookId);
      
      setTimeout(() => {
        onClose();
        setFile(null);
        setUploadProgress(null);
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  if (!isOpen) return null;

  const allVoices = voices && voices.length > 0 
    ? voices 
    : defaultVietnameseVoices;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upload PDF</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div
          className={`drop-zone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="file-preview">
              <span className="file-icon">📄</span>
              <span className="file-name">{file.name}</span>
              <button className="remove-file" onClick={() => setFile(null)}>×</button>
            </div>
          ) : (
            <>
              <span className="drop-icon">📁</span>
              <p>Drag & drop your PDF here</p>
              <span className="drop-or">or</span>
              <label className="file-input-label">
                <input type="file" accept=".pdf" onChange={handleFileSelect} />
                Browse files
              </label>
            </>
          )}
        </div>

        {error && <div className="upload-error">{error}</div>}

        <div className="voice-select">
          <label>Voice</label>
          <select
            value={selectedVoice}
            onChange={(e) => setSelectedVoice(e.target.value)}
            disabled={loadingVoices}
          >
            {loadingVoices ? (
              <option>Loading voices...</option>
            ) : (
              allVoices.map((voice) => (
                <option key={voice.id} value={voice.id}>
                  {voice.name}
                </option>
              ))
            )}
          </select>
        </div>

        {uploadProgress !== null && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
            </div>
            <span>{uploadProgress}%</span>
          </div>
        )}

        <button
          className="btn btn-primary upload-btn"
          onClick={handleUpload}
          disabled={!file || !selectedVoice || uploadMutation.isPending}
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload & Convert'}
        </button>
      </div>
    </div>
  );
}