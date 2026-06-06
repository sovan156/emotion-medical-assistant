from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.emotion_service import emotion_service

router = APIRouter(prefix="/emotion", tags=["Emotion"])


class EmotionRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/analyze")
async def analyze(req: EmotionRequest):
    if len(req.text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text too short")
    result = await emotion_service.analyze_text_emotion(req.text)
    return result