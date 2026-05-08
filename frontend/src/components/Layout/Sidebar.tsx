import { NavLink } from 'react-router-dom';
import './Sidebar.css';

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-icon">🎧</span>
        <span className="logo-text">AudioBook</span>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📚</span>
          <span className="nav-label">Library</span>
        </NavLink>
        
        <NavLink to="/recent" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🕐</span>
          <span className="nav-label">Recent</span>
        </NavLink>
        
        <button className="nav-item upload-btn" onClick={() => window.dispatchEvent(new CustomEvent('open-upload'))}>
          <span className="nav-icon">➕</span>
          <span className="nav-label">Upload</span>
        </button>
      </nav>
      
      <div className="sidebar-footer">
        <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">⚙️</span>
          <span className="nav-label">Settings</span>
        </NavLink>
      </div>
    </aside>
  );
}