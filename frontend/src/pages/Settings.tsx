import { useState, useEffect } from 'react';
import { Header } from '../components/Layout/Header';
import { Sidebar } from '../components/Layout/Sidebar';
import { usePlayerStore } from '../store/playerStore';
import './Settings.css';

const SPEED_OPTIONS = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];

const VOICE_OPTIONS = [
  { value: 'vi-VN-HoaiNeural', label: 'HoaiNeural (Female) - Vietnamese' },
  { value: 'vi-VN-NamMinhNeural', label: 'NamMinhNeural (Male) - Vietnamese' },
  { value: 'en-US-JennyNeural', label: 'JennyNeural (Female) - English' },
  { value: 'en-US-GuyNeural', label: 'GuyNeural (Male) - English' },
  { value: 'ja-JP-NanamiNeural', label: 'NanamiNeural (Female) - Japanese' },
  { value: 'zh-CN-XiaoxiaoNeural', label: 'XiaoxiaoNeural (Female) - Chinese' },
];

export function Settings() {
  const {
    theme,
    setTheme,
    defaultVoice,
    setDefaultVoice,
    defaultPlaybackRate,
    setDefaultPlaybackRate,
    clearAllData,
    playbackPosition
  } = usePlayerStore();

  const [showClearConfirm, setShowClearConfirm] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const handleThemeChange = (newTheme: 'dark' | 'light') => {
    setTheme(newTheme);
  };

  const handleClearData = () => {
    if (showClearConfirm) {
      clearAllData();
      setShowClearConfirm(false);
      alert('All data cleared successfully!');
    } else {
      setShowClearConfirm(true);
      setTimeout(() => setShowClearConfirm(false), 3000);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Header title="Settings" />
        
        <div className="settings-section">
          <h2>Appearance</h2>
          <div className="setting-item">
            <label>Theme</label>
            <div className="theme-buttons">
              <button
                className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                onClick={() => handleThemeChange('dark')}
              >
                🌙 Dark
              </button>
              <button
                className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                onClick={() => handleThemeChange('light')}
              >
                ☀️ Light
              </button>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2>Voice Settings</h2>
          <div className="setting-item">
            <label>Default Voice for New Uploads</label>
            <select
              value={defaultVoice}
              onChange={(e) => setDefaultVoice(e.target.value)}
            >
              {VOICE_OPTIONS.map((voice) => (
                <option key={voice.value} value={voice.value}>
                  {voice.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h2>Playback Settings</h2>
          <div className="setting-item">
            <label>Default Playback Speed</label>
            <div className="speed-buttons">
              {SPEED_OPTIONS.map((speed) => (
                <button
                  key={speed}
                  className={`speed-btn ${defaultPlaybackRate === speed ? 'active' : ''}`}
                  onClick={() => setDefaultPlaybackRate(speed)}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="settings-section danger-zone">
          <h2>Data Management</h2>
          <div className="setting-item">
            <label>Clear All Data</label>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>
              This will clear playback positions ({Object.keys(playbackPosition).length} saved), 
              settings, and preferences.
            </p>
            <button
              className="clear-btn"
              onClick={handleClearData}
            >
              {showClearConfirm ? 'Click again to confirm' : 'Clear All Data'}
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>About</h2>
          <div className="about-info">
            <p>AudioBook - PDF to Audio Converter</p>
            <p className="version">Version 1.0.0</p>
            <p className="version">Powered by edge-tts</p>
          </div>
        </div>
      </main>
    </div>
  );
}