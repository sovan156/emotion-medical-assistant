import logging
import random
from typing import List, Optional
from app.models.conversation import (
    Message, MessageRole, EmotionAnalysis, EmotionType
)
from app.services.ollama_service import ollama_service
from app.utils.prompt_builder import (
    build_prompt,
    build_report_explanation_prompt,
    DISCLAIMER
)

logger = logging.getLogger(__name__)


# ============================================================
# FALLBACK RESPONSES
# Used when Ollama is not available
# ============================================================

FALLBACK_RESPONSES = {
    EmotionType.ANXIETY: [
        (
            "I understand you are feeling worried right now, "
            "and that is completely natural. 💙\n\n"
            "Medical findings can feel overwhelming, but please "
            "remember that a report is the beginning of a "
            "conversation with your doctor, not a final answer.\n\n"
            "Take a slow breath. Let us look at this together, "
            "one small step at a time. What specific part is "
            "worrying you most?\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        ),
        (
            "It makes complete sense to feel anxious about "
            "medical results. You are not alone in this feeling. "
            "💙\n\n"
            "Here is what I want you to remember: most medical "
            "findings, when addressed early, have good outcomes. "
            "The fact that you are getting evaluated means you "
            "are taking care of yourself.\n\n"
            "What would you like me to help you understand?\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ],
    EmotionType.CONFUSION: [
        (
            "Medical language can be genuinely confusing — "
            "even doctors find other doctors' notes hard to "
            "read sometimes! 😊\n\n"
            "Let me help translate. Think of a medical report "
            "like a mechanic's report on your car — it uses "
            "technical words, but it really just means: "
            "here is what we checked, here is what we found, "
            "and here is what we suggest.\n\n"
            "Which specific words or sentences are confusing "
            "you? Share them and I will explain in plain "
            "language.\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ],
    EmotionType.CALM: [
        (
            "Great — let us go through this clearly. 📋\n\n"
            "Medical reports compare your measurements against "
            "established healthy ranges. Key things to look "
            "for:\n\n"
            "• Values marked H or L mean High or Low compared "
            "to normal range\n"
            "• The Impression section summarizes what it all "
            "means together\n"
            "• Recommendations tell you what action to take "
            "next\n\n"
            "Share your specific findings and I will give you "
            "a detailed explanation.\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ],
    EmotionType.STRESS: [
        (
            "Let us make this manageable. You only need to "
            "focus on three things right now: 📋\n\n"
            "1. What did the report find?\n"
            "2. Does it need urgent or routine attention?\n"
            "3. What is your next step?\n\n"
            "You do not need to understand everything today. "
            "Just enough to have a good conversation with "
            "your doctor.\n\n"
            "What is the main finding in your report?\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ],
    EmotionType.FEAR: [
        (
            "You are safe right now. 💙\n\n"
            "Fear when facing medical information is one of "
            "the most human experiences there is. It is okay "
            "to feel this way.\n\n"
            "Before we look at any details, I want you to "
            "know: one medical finding does not define your "
            "health story. Doctors see these findings "
            "regularly and know how to help.\n\n"
            "Whenever you are ready, I am here with you. "
            "What would you like to understand first?\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ],
    EmotionType.SADNESS: [
        (
            "I am truly sorry you are going through this. "
            "💙\n\n"
            "What you are feeling is completely valid. "
            "Medical situations can feel very heavy, and "
            "you are allowed to feel however you feel.\n\n"
            "When you are ready, I am here to help you "
            "understand the information. Sometimes "
            "understanding what something actually means "
            "can reduce some of the fear around it.\n\n"
            "You do not have to face this alone.\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ],
    EmotionType.NEUTRAL: [
        (
            "I am here to help you understand your health "
            "information clearly. 📋\n\n"
            "Feel free to ask me about any part of your "
            "report or any health question you have. "
            "I will do my best to explain it in a clear "
            "and helpful way.\n\n"
            "What would you like to know?\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance."
        )
    ]
}

SUGGESTED_QUESTIONS = {
    EmotionType.ANXIETY: [
        "Is this something I should be very worried about?",
        "What are the next steps I should take?",
        "Can you explain this more gently?"
    ],
    EmotionType.CONFUSION: [
        "What does this medical term mean in simple words?",
        "Can you give me an everyday example?",
        "What is the most important thing to understand?"
    ],
    EmotionType.CALM: [
        "What do these specific values indicate?",
        "What questions should I ask my doctor?",
        "What does this finding typically mean?"
    ],
    EmotionType.STRESS: [
        "What do I absolutely need to do next?",
        "What is the most important point?",
        "How urgent is this?"
    ],
    EmotionType.FEAR: [
        "Is this an emergency situation?",
        "What is the most reassuring thing you can tell me?",
        "Who should I contact first?"
    ],
    EmotionType.SADNESS: [
        "Is there hope in this situation?",
        "What support is available?",
        "What should I do next?"
    ],
    EmotionType.NEUTRAL: [
        "Can you explain this more simply?",
        "What should I do next?",
        "What does this finding mean?"
    ]
}


class LLMService:
    """
    Emotion-aware adaptive response generation using Ollama + Gemma 2B.
    Falls back to built-in responses if Ollama is unavailable.
    """

    def __init__(self):
        self.ollama = ollama_service
        logger.info(
            "LLM Service initialized with Ollama backend "
            f"(model: {self.ollama.model})"
        )

    def _get_fallback(self, emotion: EmotionType) -> str:
        """Get fallback response when Ollama is unavailable."""
        responses = FALLBACK_RESPONSES.get(
            emotion,
            FALLBACK_RESPONSES[EmotionType.NEUTRAL]
        )
        return random.choice(responses)

    def _clean_response(self, text: str) -> str:
        """Clean up Gemma response text."""
        # Remove common Gemma artifacts
        text = text.strip()
        unwanted = [
            "<end_of_turn>",
            "<start_of_turn>",
            "<bos>",
            "<eos>",
            "model\n",
            "user\n"
        ]
        for item in unwanted:
            text = text.replace(item, "")

        # Ensure disclaimer is present
        if "consult your healthcare provider" not in text.lower():
            text += (
                "\n\n⚕️ Please consult your healthcare "
                "provider for complete guidance."
            )

        return text.strip()

    async def generate_adaptive_response(
        self,
        user_message: str,
        history: List[Message],
        emotion: EmotionAnalysis,
        session_phase: str = "assessment",
        language: str = "en",
        report_context: Optional[str] = None
    ) -> str:
        """
        Main response generator.

        Flow:
        1. Build emotion-aware prompt
        2. Send to Ollama (Gemma 2B)
        3. Return adaptive response
        4. Fall back to built-in if Ollama fails
        """
        emotion_type = emotion.primary_emotion

        logger.info(
            f"Generating response for emotion: {emotion_type.value}, "
            f"phase: {session_phase}"
        )

        # Build the emotion-aware prompt
        prompt = build_prompt(
            emotion=emotion_type,
            user_message=user_message,
            report_text=report_context or ""
        )

        # Try Ollama first
        try:
            if self.ollama.is_available():
                logger.info("Ollama available — sending to Gemma 2B")
                raw_response = self.ollama.generate(prompt)
                cleaned = self._clean_response(raw_response)
                logger.info("Gemma 2B responded successfully")
                return cleaned
            else:
                logger.warning(
                    "Ollama not available — using fallback response"
                )
                return self._get_fallback(emotion_type)

        except ConnectionError as e:
            logger.error(f"Ollama connection error: {e}")
            return self._get_fallback(emotion_type)

        except Exception as e:
            logger.error(f"Unexpected error with Ollama: {e}")
            return self._get_fallback(emotion_type)

    async def explain_report(
        self,
        report_text: str,
        emotion: EmotionAnalysis,
        language: str = "en"
    ) -> str:
        """
        Generate an emotionally adaptive explanation of a medical report.
        Called when user uploads a report.
        """
        emotion_type = emotion.primary_emotion

        logger.info(
            f"Explaining report for emotion: {emotion_type.value}"
        )

        # Build report-specific prompt
        prompt = build_report_explanation_prompt(
            emotion=emotion_type,
            report_text=report_text
        )

        # Try Ollama
        try:
            if self.ollama.is_available():
                raw_response = self.ollama.generate(prompt)
                cleaned = self._clean_response(raw_response)
                return cleaned
            else:
                logger.warning(
                    "Ollama not available for report explanation"
                )
                return self._get_report_fallback(
                    emotion_type, report_text
                )

        except Exception as e:
            logger.error(f"Report explanation error: {e}")
            return self._get_report_fallback(
                emotion_type, report_text
            )

    def _get_report_fallback(
        self,
        emotion: EmotionType,
        report_text: str
    ) -> str:
        """Fallback report explanation without Ollama."""
        preview = report_text[:200].strip()

        intros = {
            EmotionType.ANXIETY: (
                "I can see you have uploaded your report, and I "
                "want to help you understand it gently. 💙\n\n"
                "Please remember that medical reports contain "
                "many findings, and not everything listed means "
                "something is wrong. Let us look at it together "
                "calmly."
            ),
            EmotionType.CONFUSION: (
                "Let me help you make sense of this report in "
                "plain, simple language. 📋\n\n"
                "Medical reports look complex but follow a simple "
                "structure. I will explain each part clearly."
            ),
            EmotionType.CALM: (
                "Here is a structured overview of your report. "
                "📊\n\n"
                "I will explain the key findings and what they "
                "typically indicate."
            ),
            EmotionType.STRESS: (
                "Let me give you just the key points from your "
                "report — no overwhelming detail. 📋"
            ),
        }

        intro = intros.get(
            emotion,
            "I have received your report and I am here to help "
            "you understand it. 💙"
        )

        return (
            f"{intro}\n\n"
            f"**Your report begins with:**\n"
            f'"{preview}..."\n\n'
            "Please share which specific part you would like me "
            "to explain in detail. I will break it down in "
            "simple terms.\n\n"
            "⚕️ Please consult your healthcare provider for "
            "complete guidance on your results."
        )

    async def get_suggested_questions(
        self,
        emotion: EmotionType,
        context: str,
        language: str = "en"
    ) -> List[str]:
        """Return emotion-appropriate suggested questions."""
        return SUGGESTED_QUESTIONS.get(
            emotion,
            SUGGESTED_QUESTIONS[EmotionType.NEUTRAL]
        )


# Singleton instance
llm_service = LLMService()
