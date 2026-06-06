/**
 * Text-to-Speech service using Web Speech API
 * with support for multiple languages
 */

const LANGUAGE_CODES = {
  en: 'en-US',
  hi: 'hi-IN',
  bn: 'bn-BD',
  es: 'es-ES',
  fr: 'fr-FR',
};

class TTSService {
  constructor() {
    this.synth = window.speechSynthesis;
    this.currentUtterance = null;
    this.isSupported = 'speechSynthesis' in window;
  }

  speak(text, language = 'en', options = {}) {
    if (!this.isSupported) {
      console.warn('Text-to-speech not supported in this browser');
      return false;
    }

    // Stop any current speech
    this.stop();

    // Clean markdown from text
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/#{1,6}\s/g, '')
      .replace(/---/g, '')
      .replace(/💙|⚕️|•/g, '');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = LANGUAGE_CODES[language] || 'en-US';
    utterance.rate = options.rate || 0.85; // Slightly slower for medical context
    utterance.pitch = options.pitch || 1.0;
    utterance.volume = options.volume || 0.9;

    // Select appropriate voice
    const voices = this.synth.getVoices();
    const langCode = LANGUAGE_CODES[language] || 'en-US';
    const matchingVoice = voices.find(
      (v) => v.lang === langCode && v.localService
    ) || voices.find((v) => v.lang.startsWith(language));

    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onstart = options.onStart;
    utterance.onend = options.onEnd;
    utterance.onerror = options.onError;

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
    return true;
  }

  stop() {
    if (this.synth && this.synth.speaking) {
      this.synth.cancel();
    }
  }

  pause() {
    if (this.synth && this.synth.speaking) {
      this.synth.pause();
    }
  }

  resume() {
    if (this.synth && this.synth.paused) {
      this.synth.resume();
    }
  }

  get isSpeaking() {
    return this.synth?.speaking || false;
  }
}

export const ttsService = new TTSService();
