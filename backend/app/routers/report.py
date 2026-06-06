from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from datetime import datetime
from app.services.report_service import report_service
from app.services.llm_service import llm_service
from app.models.conversation import EmotionType, EmotionAnalysis
from app.routers.auth import get_current_user
from app.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Reports"])


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    language: str = "en",
    current_user=Depends(get_current_user)
):
    contents = await file.read()

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")

    file_ext = file.filename.split(".")[-1].lower() if file.filename else "txt"

    try:
        processed = report_service.process_report(contents, file_ext)

        neutral_emotion = EmotionAnalysis(
            primary_emotion=EmotionType.CALM,
            confidence=0.8,
            all_scores={"calm": 0.8, "neutral": 0.2},
            distress_level="low",
            requires_escalation=False
        )

        summary = await llm_service.explain_report(
            processed["extracted_text"], neutral_emotion, language
        )

        db = get_database()
        doc = {
            "user_id": current_user["id"],
            "file_name": file.filename,
            "file_type": file_ext,
            "extracted_text": processed["extracted_text"],
            "summary": summary,
            "key_findings": processed["key_findings"],
            "concern_level": processed["concern_level"],
            "upload_time": datetime.utcnow()
        }
        result = await db.reports.insert_one(doc)
        report_id = str(result.inserted_id)

        return {
            "report_id": report_id,
            "file_name": file.filename,
            "summary": summary,
            "key_findings": processed["key_findings"],
            "concern_level": processed["concern_level"],
            "message": (
                "Your report has been processed. I am here to help you understand it. "
                "Remember, a healthcare professional can provide complete guidance."
            )
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Report upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process report")


@router.get("/{report_id}")
async def get_report(report_id: str, current_user=Depends(get_current_user)):
    db = get_database()
    from bson import ObjectId
    doc = await db.reports.find_one({
        "_id": ObjectId(report_id),
        "user_id": current_user["id"]
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc