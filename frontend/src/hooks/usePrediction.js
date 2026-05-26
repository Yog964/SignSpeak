import { useState, useRef, useCallback } from 'react';

export function usePrediction() {
  const [currentSign, setCurrentSign] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [category, setCategory] = useState('');
  const [sentence, setSentence] = useState([]);

  const predictionHistory = useRef([]);
  const lastStableSign = useRef('');
  const stableStartTime = useRef(null);
  const HISTORY_SIZE = 15;
  const STABILITY_THRESHOLD = 5;
  const AUTO_ADD_DELAY = 2000;

  const processPrediction = useCallback((prediction) => {
    if (!prediction || prediction.type === 'error') return;

    const { sign, confidence: conf, category: cat } = prediction;

    setConfidence(conf || 0);
    setCategory(cat || '');

    if (!sign) {
      setCurrentSign('');
      lastStableSign.current = '';
      stableStartTime.current = null;
      return;
    }

    predictionHistory.current.push(sign);
    if (predictionHistory.current.length > HISTORY_SIZE) {
      predictionHistory.current.shift();
    }

    const freq = {};
    predictionHistory.current.forEach(s => {
      freq[s] = (freq[s] || 0) + 1;
    });
    const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
    const [topSign, topCount] = sorted[0] || ['', 0];

    if (topCount >= STABILITY_THRESHOLD) {
      setCurrentSign(topSign);

      if (topSign === lastStableSign.current) {
        if (stableStartTime.current && Date.now() - stableStartTime.current >= AUTO_ADD_DELAY) {
          setSentence(prev => {
            if (prev.length === 0 || prev[prev.length - 1] !== topSign) {
              return [...prev, topSign];
            }
            return prev;
          });
          stableStartTime.current = Date.now();
          predictionHistory.current = [];
        }
      } else {
        lastStableSign.current = topSign;
        stableStartTime.current = Date.now();
      }
    } else {
      setCurrentSign(topSign);
    }
  }, []);

  const clearSentence = useCallback(() => {
    setSentence([]);
    predictionHistory.current = [];
    lastStableSign.current = '';
    stableStartTime.current = null;
    setCurrentSign('');
    setConfidence(0);
    setCategory('');
  }, []);

  const speakSentence = useCallback(() => {
    if (sentence.length === 0) return;
    const text = sentence.join(' ');
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-IN';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }, [sentence]);

  return {
    currentSign,
    confidence,
    category,
    sentence,
    processPrediction,
    clearSentence,
    speakSentence,
  };
}
