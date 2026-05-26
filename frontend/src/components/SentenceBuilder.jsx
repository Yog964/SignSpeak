import './SentenceBuilder.css';

function SentenceBuilder({ sentence, onSpeak, onClear }) {
  const words = sentence || [];
  const text = words.join(' ');

  return (
    <div className="sentence-card" id="sentence-builder">
      <div className="sentence-header">
        <div className="card-label" style={{ marginBottom: 0 }}>Sentence Builder</div>
        <span className="word-count-badge" id="word-count">{words.length} words</span>
      </div>
      <div className="sentence-display" id="sentence-text">
        {text.length > 0 ? (
          text
        ) : (
          <span className="sentence-placeholder">Waiting for signs…</span>
        )}
      </div>
      <div className="sentence-buttons">
        <button
          className="btn-speak"
          onClick={onSpeak}
          disabled={words.length === 0}
          id="speak-button"
        >
          🔊 Speak
        </button>
        <button
          className="btn-clear"
          onClick={onClear}
          disabled={words.length === 0}
          id="clear-button"
        >
          Clear
        </button>
      </div>
    </div>
  );
}

export default SentenceBuilder;
