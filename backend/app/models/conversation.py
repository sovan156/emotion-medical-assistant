from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import uuid


class EmotionType(str, Enum):
    ANXIETY = "anxiety"
    STRESS = "stress"
    CONFUSION = "confusion"
    CALM = "calm"
    FEAR = "fear"
    SADNESS = "sadness"
    NEUTRAL = "neutral"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EmotionAnalysis(BaseModel):
    primary_emotion: EmotionType
    confidence: float
    all_scores: Dict[str, float]
    distress_level: str
    requires_escalation: bool = False


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    emotion_analysis: Optional[EmotionAnalysis] = None
    is_voice: bool = False
    language: str = "en"


class Conversation(BaseModel):
    id: Optional[str] = None
    user_id: str
    report_id: Optional[str] = None
    messages: List[Message] = []
    current_emotion: Optional[EmotionAnalysis] = None
    session_phase: str = "initial"
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    language: str = "en"
    is_voice: bool = False
    report_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: Message
    emotion_analysis: Optional[EmotionAnalysis] = None
    session_phase: str
    escalation_recommended: bool = False
    escalation_message: Optional[str] = None
    suggested_next_questions: List[str] = []