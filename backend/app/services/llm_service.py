import logging
from typing import List, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.models.conversation import Message, MessageRole, EmotionAnalysis, EmotionType
from app.utils.prompt_templates import build_system_prompt, DISCLAIMER

logger = logging.getLogger(__name__)


class LLMService:
    """Generates emotionally adaptive responses using GPT."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _format_messages(self, history: List[Message], system_prompt: str) -> list:
        formatted = [{"role": "system", "content": system_prompt}]
        for msg in history[-10:]:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                formatted.append({"role": msg.role.value, "content": msg.content})
        return formatted

    def _get_temperature(self, emotion: EmotionType) -> float:
        temps = {
            EmotionType.ANXIETY: 0.4,
            EmotionType.FEAR: 0.4,
            EmotionType.STRESS: 0.5,
            EmotionType.CONFUSION: 0.4,
            EmotionType.CALM: 0.7,
            EmotionType.SADNESS: 0.5,
            EmotionType.NEUTRAL: 0.6,
        }
        return temps.get(emotion, 0.6)

    async def generate_adaptive_response(
        self,
        user_message: str,
        history: List[Message],
        emotion: EmotionAnalysis,
        session_phase: str = "assessment",
        language: str = "en",
        report_context: Optional[str] = None
    ) -> str:
        system_prompt = build_system_prompt(emotion.primary_emotion, language, session_phase)

        if report_context:
            system_prompt += f"\n\nREPORT CONTEXT:\n{report_context[:1500]}"

        messages = self._format_messages(history, system_prompt)
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=700,
                temperature=self._get_temperature(emotion.primary_emotion)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return self._fallback_response(emotion.primary_emotion, language)

    def _fallback_response(self, emotion: EmotionType, language: str) -> str:
        disclaimer = DISCLAIMER.get(language, DISCLAIMER["en"])
        if emotion in [EmotionType.ANXIETY, EmotionType.FEAR]:
            msg = ("I understand you may be feeling anxious. Please take a breath. "
                   "Many medical findings require further evaluation, and it is completely "
                   "natural to have questions. I encourage you to speak with your healthcare "
                   "provider who can guide you personally.")
        elif emotion == EmotionType.CONFUSION:
            msg = ("It is completely okay not to understand medical information right away. "
                   "Please ask me to explain anything in simpler terms. Your doctor can also "
                   "walk you through everything step by step.")
        else:
            msg = ("I am here to help you understand your health information. "
                   "Please remember to consult your healthcare provider for personalized guidance.")
        return f"{msg}\n\n{disclaimer}"

    async def explain_report(self, report_text: str, emotion: EmotionAnalysis, language: str = "en") -> str:
        prompt = f"""You are helping a patient understand their medical report.
Patient emotional state: {emotion.primary_emotion.value}

Medical report content:
{report_text[:2000]}

Provide:
1. A brief, gentle summary appropriate for someone who is {emotion.primary_emotion.value}
2. Simple explanation of any key findings
3. Clear guidance to consult a healthcare professional
4. Emotional support

NEVER provide a diagnosis. NEVER use alarming language.
Respond in {'English' if language == 'en' else 'Hindi' if language == 'hi' else 'Bengali'}.
"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Report explain error: {e}")
            disclaimer = DISCLAIMER.get(language, DISCLAIMER["en"])
            return (f"Your report has been received. For a complete and accurate understanding, "
                    f"please discuss this with your healthcare provider. {disclaimer}")

    async def get_suggested_questions(self, emotion: EmotionType, context: str, language: str = "en") -> List[str]:
        try:
            prompt = f"""Suggest 3 short follow-up questions a patient feeling {emotion.value} 
might ask about their medical information. Context: {context[:150]}
Language: {'English' if language == 'en' else 'Hindi' if language == 'hi' else 'Bengali'}
Return only the 3 questions as a numbered list."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.6
            )
            lines = [l.strip() for l in response.choices[0].message.content.split('\n') if l.strip()]
            questions = [l.lstrip('0123456789.-) ').strip() for l in lines if l.lstrip('0123456789.-) ')]
            return questions[:3]
        except Exception:
            return [
                "Can you explain this more simply?",
                "What should I do next?",
                "Should I be concerned about this?"
            ]


llm_service = LLMService()