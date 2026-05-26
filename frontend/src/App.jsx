import { useState, useCallback, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import CameraFeed from './components/CameraFeed';
import DetectionPanel from './components/DetectionPanel';
import SentenceBuilder from './components/SentenceBuilder';
import ModelSelector from './components/ModelSelector';
import { useWebSocket } from './hooks/useWebSocket';
import { usePrediction } from './hooks/usePrediction';
import { flattenLandmarks } from './utils/landmarkUtils';

function App() {
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [fps, setFps] = useState(0);

  const fetchModels = useCallback(() => {
    fetch('http://localhost:8000/api/models')
      .then((res) => res.json())
      .then((data) => {
        if (data.models && data.models.length > 0) {
          const formattedModels = data.models.map(m => ({
            ...m,
            name: `${m.name} (${m.id}.pkl)`
          }));
          setAvailableModels(formattedModels);
          // Only set selected model if current is empty or not in the new list
          setSelectedModel(current => {
            if (!current || !data.models.find(m => m.id === current)) {
              return formattedModels[0].id;
            }
            return current;
          });
        }
      })
      .catch((err) => console.error('Failed to fetch models:', err));
  }, []);

  // Fetch available models on mount
  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const { isConnected, lastMessage, sendMessage } = useWebSocket('ws://localhost:8000/ws/predict');
  const {
    currentSign,
    confidence,
    category,
    sentence,
    processPrediction,
    clearSentence,
    speakSentence,
  } = usePrediction();

  // Process incoming WebSocket predictions
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'prediction') {
      processPrediction(lastMessage);
    }
  }, [lastMessage, processPrediction]);

  // Handle landmarks from CameraFeed → send to backend via WebSocket
  const handleLandmarks = useCallback(
    (landmarks) => {
      const flattened = flattenLandmarks(landmarks);
      if (flattened) {
        sendMessage({
          type: 'predict',
          model: selectedModel,
          landmarks: flattened,
        });
      }
    },
    [selectedModel, sendMessage]
  );

  // Handle FPS updates from CameraFeed
  const handleFpsUpdate = useCallback((newFps) => {
    setFps(newFps);
  }, []);

  return (
    <div className="app">
      <Header isConnected={isConnected} fps={fps} />
      <main className="main-content">
        <div className="camera-section">
          <CameraFeed
            onLandmarks={handleLandmarks}
            onFpsUpdate={handleFpsUpdate}
          />
        </div>
        <div className="controls-section">
          <DetectionPanel
            sign={currentSign}
            confidence={confidence}
            category={category}
          />
          <SentenceBuilder
            sentence={sentence}
            onSpeak={speakSentence}
            onClear={clearSentence}
          />
          <ModelSelector
            models={availableModels}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
            onModelUploaded={fetchModels}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
