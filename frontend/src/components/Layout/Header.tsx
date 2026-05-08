import { useState, useEffect } from 'react';
import { saveTheme, getTheme } from '../../api/client';
import './Header.css';

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  const [theme, setTheme] = useState<'light' | 'dark'>(getTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    saveTheme(newTheme);
  };

  return (
    <header className="header">
      <h1 className="header-title">{title || 'Library'}</h1>
      <div className="header-actions">
        <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </div>
    </header>
  );
}