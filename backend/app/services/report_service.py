import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)

CONCERNING_WORDS = [
    "malignant", "carcinoma", "cancer", "tumor", "mass",
    "abnormal", "elevated", "critical", "severe", "infection"
]

REASSURING_WORDS = [
    "normal", "within range", "benign", "negative", "clear",
    "healthy", "no evidence", "unremarkable", "stable"
]


class ReportService:

    def extract_from_pdf(self, file_bytes: bytes) -> str:
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return self._clean(text)
        except Exception as e:
            raise ValueError(f"Could not read PDF: {e}")

    def extract_from_txt(self, file_bytes: bytes) -> str:
        return self._clean(file_bytes.decode("utf-8", errors="ignore"))

    def _clean(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()

    def assess_concern_level(self, text: str) -> Tuple[str, List[str]]:
        text_lower = text.lower()
        concerning_count = sum(1 for w in CONCERNING_WORDS if w in text_lower)
        reassuring_count = sum(1 for w in REASSURING_WORDS if w in text_lower)
        findings = []

        for word in CONCERNING_WORDS:
            if word in text_lower:
                idx = text_lower.find(word)
                context = text[max(0, idx - 40):idx + 80].strip()
                findings.append(f"...{context}...")

        if concerning_count == 0:
            level = "low"
        elif concerning_count <= 2 and reassuring_count >= concerning_count:
            level = "low"
        elif concerning_count <= 3:
            level = "moderate"
        else:
            level = "high"

        return level, findings[:4]

    def process_report(self, file_bytes: bytes, file_ext: str) -> dict:
        if file_ext in ["pdf", "application/pdf"]:
            text = self.extract_from_pdf(file_bytes)
        elif file_ext in ["txt", "text/plain"]:
            text = self.extract_from_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        level, findings = self.assess_concern_level(text)

        return {
            "extracted_text": text,
            "concern_level": level,
            "key_findings": findings
        }


report_service = ReportService()