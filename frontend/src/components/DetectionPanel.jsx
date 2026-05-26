import './DetectionPanel.css';

function DetectionPanel({ sign, confidence, category }) {
  const confidencePercent = confidence.toFixed(1);
  const hasSign = sign && sign.length > 0;

  return (
    <div className="detection-card" id="detection-panel">
      <div className="card-label">Detection</div>
      <div className={`sign-name ${!hasSign ? 'empty' : ''}`} id="detected-sign">
        {hasSign ? sign : '—'}
      </div>
      <div className="confidence-bar-track">
        <div
          className="confidence-bar-fill"
          style={{ width: `${hasSign ? confidencePercent : 0}%` }}
          id="confidence-bar"
        />
      </div>
      <div className="confidence-info">
        <span className="confidence-text" id="confidence-value">
          Confidence: {hasSign ? `${confidencePercent}%` : '—'}
        </span>
        {category && (
          <span className="category-badge" id="category-badge">
            <span className={`category-dot ${category.toLowerCase()}`} />
            {category}
          </span>
        )}
      </div>
    </div>
  );
}

export default DetectionPanel;
