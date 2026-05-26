import { useRef, useEffect } from 'react';
import { useMediaPipe } from '../hooks/useMediaPipe';
import './CameraFeed.css';

function CameraFeed({ onLandmarks, onFpsUpdate }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const { isLoading, fps, setOnLandmarks } = useMediaPipe(videoRef, canvasRef);

  useEffect(() => {
    if (onLandmarks) {
      setOnLandmarks(onLandmarks);
    }
  }, [onLandmarks, setOnLandmarks]);

  useEffect(() => {
    if (onFpsUpdate) {
      onFpsUpdate(fps);
    }
  }, [fps, onFpsUpdate]);

  return (
    <div className="camera-container" id="camera-feed">
      <video
        ref={videoRef}
        className="camera-video"
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        className="camera-canvas"
        width={1280}
        height={720}
      />
      {!isLoading && (
        <div className="live-badge" id="live-indicator">
          <span className="live-dot" />
          LIVE
        </div>
      )}
      {isLoading && (
        <div className="camera-loading">
          <div className="loading-spinner" />
          <span className="loading-text">Initializing camera &amp; pose model…</span>
        </div>
      )}
    </div>
  );
}

export default CameraFeed;
