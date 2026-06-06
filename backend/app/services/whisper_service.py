import tempfile
import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class WhisperService:
    """Converts audio (speech) to text using OpenAI Whisper."""

    LANGUAGE_MAP = {
        "en": "english",
        "hi": "hindi",
        "bn": "bengali"
    }

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            import whisper
            self.model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
            logger.info(f"Whisper '{settings.WHISPER_MODEL_SIZE}' loaded")
        except Exception as e:
            logger.error(f"Whisper load failed: {e}")
            self.model = None

    async def transcribe_audio(self, audio_bytes: bytes, language: str = "en", file_ext: str = "wav") -> dict:
        if not self.model:
            raise RuntimeError("Whisper model not available. Check installation.")

        suffix = f".{file_ext}"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            whisper_lang = self.LANGUAGE_MAP.get(language, "english")
            result = self.model.transcribe(tmp_path, language=whisper_lang, fp16=False, verbose=False)

            text = result.get("text", "").strip()
            segments = result.get("segments", [])
            confidence = 0.7

            if segments:
                avg_lp = sum(s.get("avg_logprob", -0.5) for s in segments) / len(segments)
                confidence = max(0.0, min(1.0, avg_lp + 1.0))

            return {
                "text": text,
                "language": result.get("language", language),
                "confidence": round(confidence, 3)
            }
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


whisper_service = WhisperService()