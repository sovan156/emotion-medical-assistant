from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Report(BaseModel):
    id: Optional[str] = None
    user_id: str
    file_name: str
    file_type: str
    extracted_text: str
    summary: Optional[str] = None
    key_findings: List[str] = []
    concern_level: str = "low"
    upload_time: datetime = Field(default_factory=datetime.utcnow)