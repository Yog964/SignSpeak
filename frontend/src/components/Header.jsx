import './Header.css';

function Header({ isConnected, fps }) {
  return (
    <header className="header" id="app-header">
      <div className="header-brand">
        <span className="header-title" id="brand-title">ISL SignSpeak</span>
        <span className="header-subtitle">BuildForBharat</span>
      </div>
      <div className="header-status">
        <div className="status-indicator" id="connection-status">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
          <span className={`status-text ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <span className="fps-badge" id="fps-counter">{fps} FPS</span>
      </div>
    </header>
  );
}

export default Header;
