from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from app.services.whisper_service import whisper_service
from app.services.emotion_service import emotion_service
from app.routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/transcribe")
async def transcribe(
    audio_file: UploadFile = File(...),
    language: str = "en",
    current_user=Depends(get_current_user)
):
    contents = await audio_file.read()

    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max 25MB.")

    file_ext = audio_file.filename.split(".")[-1] if audio_file.filename else "wav"

    try:
        transcription = await whisper_service.transcribe_audio(contents, language, file_ext)
        emotion = None
        if transcription.get("text"):
            emotion = await emotion_service.analyze_text_emotion(transcription["text"])

        return {
            "transcription": transcription,
            "emotion_analysis": emotion.model_dump() if emotion else None,
            "status": "success"
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail="Transcription failed")