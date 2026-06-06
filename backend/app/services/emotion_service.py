import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import logging
from typing import Tuple
from app.models.conversation import EmotionAnalysis, EmotionType
from app.config import settings

logger = logging.getLogger(__name__)


class EmotionService:
    """Detects emotions from text using HuggingFace transformers."""

    EMOTION_MAPPING = {
        "anger": "stress",
        "disgust": "stress",
        "fear": "anxiety",
        "joy": "calm",
        "neutral": "neutral",
        "sadness": "sadness",
        "surprise": "confusion",
    }

    ESCALATION_KEYWORDS = [
        "give up", "hopeless", "can't take it", "too much",
        "end it", "no point", "overwhelmed completely",
        "scared to death", "panicking", "breaking down",
        "dying", "want to die"
    ]

    def __init__(self):
        self.classifier = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "text-classification",
                model=settings.HF_MODEL_NAME,
                top_k=None,
                device=-1
            )
            logger.info(f"Emotion model loaded: {settings.HF_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Could not load emotion model: {e}")
            self.classifier = None

    def _check_escalation_keywords(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.ESCALATION_KEYWORDS)

    def _get_distress_level(self, emotion: str, confidence: float, escalation: bool) -> Tuple[str, bool]:
        if escalation:
            return "severe", True
        if emotion in ["anxiety", "fear", "stress"]:
            if confidence > 0.85:
                return "severe", True
            elif confidence > 0.70:
                return "high", False
            elif confidence > 0.50:
                return "moderate", False
        elif emotion == "sadness":
            if confidence > 0.85:
                return "severe", True
            elif confidence > 0.65:
                return "high", False
        return "low", False

    async def analyze_text_emotion(self, text: str) -> EmotionAnalysis:
        """Main method: analyze text and return emotion."""
        if not text or len(text.strip()) < 3:
            return EmotionAnalysis(
                primary_emotion=EmotionType.NEUTRAL,
                confidence=1.0,
                all_scores={"neutral": 1.0},
                distress_level="low",
                requires_escalation=False
            )

        escalation = self._check_escalation_keywords(text)

        if self.classifier:
            return await self._model_analysis(text, escalation)
        else:
            return self._rule_based_analysis(text, escalation)

    async def _model_analysis(self, text: str, escalation: bool) -> EmotionAnalysis:
        try:
            results = self.classifier(text[:512])

            raw_scores = {}
            result_list = results[0] if isinstance(results[0], list) else results
            for item in result_list:
                raw_scores[item["label"].lower()] = round(item["score"], 4)

            # Map to our emotion categories
            mapped = {"anxiety": 0.0, "stress": 0.0, "confusion": 0.0,
                      "calm": 0.0, "sadness": 0.0, "fear": 0.0, "neutral": 0.0}

            for label, score in raw_scores.items():
                target = self.EMOTION_MAPPING.get(label, "neutral")
                if label == "fear":
                    mapped["anxiety"] += score * 0.7
                    mapped["fear"] = score * 0.3
                elif target in mapped:
                    mapped[target] += score

            primary = max(mapped, key=mapped.get)
            confidence = mapped[primary]
            distress_level, requires_escalation = self._get_distress_level(primary, confidence, escalation)

            return EmotionAnalysis(
                primary_emotion=EmotionType(primary),
                confidence=round(confidence, 4),
                all_scores=mapped,
                distress_level=distress_level,
                requires_escalation=requires_escalation
            )
        except Exception as e:
            logger.error(f"Model analysis error: {e}")
            return self._rule_based_analysis(text, escalation)

    def _rule_based_analysis(self, text: str, escalation: bool) -> EmotionAnalysis:
        """Fallback: simple keyword-based detection."""
        text_lower = text.lower()

        keyword_map = {
            "anxiety": ["worried", "anxious", "nervous", "scared", "afraid", "panic"],
            "stress": ["stressed", "overwhelmed", "pressure", "tense", "frustrated"],
            "confusion": ["confused", "don't understand", "unclear", "complicated", "lost"],
            "calm": ["okay", "fine", "understand", "good", "alright", "clear"],
            "sadness": ["sad", "upset", "crying", "depressed", "unhappy"],
            "fear": ["terrified", "petrified", "dread", "horrified"],
            "neutral": ["what", "how", "tell me", "explain"]
        }

        scores = {}
        for emotion, keywords in keyword_map.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            scores[emotion] = round(count / len(keywords), 4)

        total = sum(scores.values()) or 1
        scores = {k: round(v / total, 4) for k, v in scores.items()}

        if all(v == 0 for v in scores.values()):
            scores["neutral"] = 1.0

        primary = max(scores, key=scores.get)
        confidence = scores[primary]
        distress_level, requires_escalation = self._get_distress_level(primary, confidence, escalation)

        return EmotionAnalysis(
            primary_emotion=EmotionType(primary) if primary in [e.value for e in EmotionType] else EmotionType.NEUTRAL,
            confidence=confidence,
            all_scores=scores,
            distress_level=distress_level,
            requires_escalation=requires_escalation
        )


emotion_service = EmotionService()