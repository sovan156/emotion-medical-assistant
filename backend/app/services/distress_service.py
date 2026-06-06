from app.models.conversation import EmotionAnalysis, EmotionType
from app.utils.prompt_templates import ESCALATION_MESSAGES

HELPLINES = {
    "en": [
        {"name": "iCall (TISS)", "number": "9152987821"},
        {"name": "Vandrevala Foundation", "number": "1860-2662-345"},
        {"name": "NIMHANS Helpline", "number": "080-46110007"},
        {"name": "Your doctor or healthcare provider", "number": "See your prescription"},
    ]
}


class DistressService:

    def should_escalate(self, emotion: EmotionAnalysis) -> bool:
        if emotion.requires_escalation:
            return True
        if emotion.distress_level == "severe":
            return True
        high_risk = [EmotionType.ANXIETY, EmotionType.FEAR, EmotionType.STRESS, EmotionType.SADNESS]
        if emotion.primary_emotion in high_risk and emotion.confidence >= 0.85:
            return True
        return False

    def get_escalation_response(self, emotion: EmotionAnalysis, language: str = "en") -> dict:
        message = ESCALATION_MESSAGES.get(language, ESCALATION_MESSAGES["en"])
        helplines = HELPLINES.get(language, HELPLINES["en"])
        return {
            "message": message,
            "helplines": helplines,
            "recommendation": "Please reach out to a healthcare professional or trusted person."
        }


distress_service = DistressService()