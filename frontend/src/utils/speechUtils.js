/**
 * Text-to-speech utility using the Web Speech API.
 */
export function speak(text, lang = 'en-IN') {
  if (!window.speechSynthesis) {
    console.warn('Speech synthesis not supported');
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 0.9;
  utterance.pitch = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

export function getVoices() {
  return window.speechSynthesis?.getVoices() || [];
}
