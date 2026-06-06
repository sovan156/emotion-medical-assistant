from fastapi import APIRouter, Depends
from datetime import datetime
import uuid
from app.models.conversation import ChatRequest, ChatResponse, Message, MessageRole, Conversation, EmotionType
from app.services.emotion_service import emotion_service
from app.services.llm_service import llm_service
from app.services.distress_service import distress_service
from app.database import get_database
from app.routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, current_user=Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]

    # Load or create conversation
    conversation = None
    conv_id = None

    if request.conversation_id:
        try:
            from bson import ObjectId
            doc = await db.conversations.find_one({
                "_id": ObjectId(request.conversation_id),
                "user_id": user_id
            })
            if doc:
                doc["id"] = str(doc["_id"])
                conversation = Conversation(**{k: v for k, v in doc.items() if k != "_id"})
                conv_id = request.conversation_id
        except Exception as e:
            logger.warning(f"Could not load conversation: {e}")

    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            report_id=request.report_id,
            language=request.language
        )

    # Detect emotion
    emotion = await emotion_service.analyze_text_emotion(request.message)
    conversation.current_emotion = emotion

    # Determine phase
    msg_count = len(conversation.messages)
    if msg_count == 0:
        phase = "initial"
    elif msg_count < 6:
        phase = "assessment"
    elif request.report_id or conversation.report_id:
        phase = "explanation"
    else:
        phase = "support"
    conversation.session_phase = phase

    # Check escalation
    escalate = distress_service.should_escalate(emotion)
    escalation_data = None
    if escalate:
        escalation_data = distress_service.get_escalation_response(emotion, request.language)

    # Get report context
    report_context = None
    rid = request.report_id or conversation.report_id
    if rid:
        try:
            from bson import ObjectId
            report_doc = await db.reports.find_one({"_id": ObjectId(rid)})
            if report_doc:
                report_context = report_doc.get("extracted_text", "")[:1500]
        except Exception:
            pass

    # Generate response
    ai_text = await llm_service.generate_adaptive_response(
        user_message=request.message,
        history=conversation.messages,
        emotion=emotion,
        session_phase=phase,
        language=request.language,
        report_context=report_context
    )

    if escalation_data:
        ai_text += f"\n\n---\n{escalation_data['message']}"

    # Get suggested questions
    suggestions = await llm_service.get_suggested_questions(
        emotion.primary_emotion, request.message, request.language
    )

    # Create message objects
    user_msg = Message(
        role=MessageRole.USER,
        content=request.message,
        emotion_analysis=emotion,
        is_voice=request.is_voice,
        language=request.language
    )
    assistant_msg = Message(
        role=MessageRole.ASSISTANT,
        content=ai_text,
        language=request.language
    )

    conversation.messages.extend([user_msg, assistant_msg])
    conversation.updated_at = datetime.utcnow()

    # Save to DB
    conv_dict = {
        "user_id": conversation.user_id,
        "report_id": conversation.report_id,
        "messages": [m.model_dump() for m in conversation.messages],
        "current_emotion": emotion.model_dump(),
        "session_phase": phase,
        "language": request.language,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }

    if conv_id:
        from bson import ObjectId
        await db.conversations.update_one({"_id": ObjectId(conv_id)}, {"$set": conv_dict})
    else:
        result = await db.conversations.insert_one(conv_dict)
        conv_id = str(result.inserted_id)

    return ChatResponse(
        conversation_id=conv_id,
        message=assistant_msg,
        emotion_analysis=emotion,
        session_phase=phase,
        escalation_recommended=escalate,
        escalation_message=escalation_data["message"] if escalation_data else None,
        suggested_next_questions=suggestions
    )


@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str, current_user=Depends(get_current_user)):
    db = get_database()
    from bson import ObjectId
    doc = await db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": current_user["id"]
    })
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/conversations")
async def list_conversations(current_user=Depends(get_current_user)):
    db = get_database()
    cursor = db.conversations.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1).limit(20)

    result = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        doc.pop("messages", None)
        result.append(doc)
    return {"conversations": result}