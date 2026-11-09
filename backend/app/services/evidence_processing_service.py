import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import pypdf

from app.models.submission_evidence import SubmissionEvidence
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEvidenceItem:
    """Normalized content extracted from an evidence file for AI evaluation."""

    evidence_id: str
    original_filename: str
    media_type: str
    text_content: Optional[str] = None
    image_bytes: Optional[bytes] = None
    limitation_note: Optional[str] = None


class EvidenceProcessingService:
    """Extracts machine-readable text and multimodal payloads from stored evidence files."""

    def extract_evidence_content(self, evidence: SubmissionEvidence) -> ExtractedEvidenceItem:
        """Process a single evidence artifact based on its MIME type and file format."""
        try:
            file_path = storage_service.get_file_path(evidence.storage_key)
        except Exception as e:
            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type=evidence.media_type,
                limitation_note=f"File could not be accessed from storage: {str(e)}",
            )

        media_type = evidence.media_type.lower()
        filename_lower = evidence.original_filename.lower()

        # 1. Plain Text files (.txt)
        if media_type == "text/plain" or filename_lower.endswith(".txt"):
            return self._process_text_file(evidence, file_path)

        # 2. PDF Documents (.pdf)
        if media_type == "application/pdf" or filename_lower.endswith(".pdf"):
            return self._process_pdf_file(evidence, file_path)

        # 3. Image Artifacts (PNG, JPEG, JPG)
        if media_type in ("image/png", "image/jpeg") or filename_lower.endswith((".png", ".jpg", ".jpeg")):
            return self._process_image_file(evidence, file_path)

        # 4. Fallback / Unrecognized
        return ExtractedEvidenceItem(
            evidence_id=str(evidence.id),
            original_filename=evidence.original_filename,
            media_type=evidence.media_type,
            limitation_note=f"Format '{evidence.media_type}' is stored but not supported for automated AI content parsing.",
        )

    def _process_text_file(self, evidence: SubmissionEvidence, file_path: Path) -> ExtractedEvidenceItem:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            # Limit character size to avoid prompt overflow
            max_chars = 30000
            if len(content) > max_chars:
                content = content[:max_chars] + f"\n... [Truncated at {max_chars} characters for review]"
            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type="text/plain",
                text_content=content,
            )
        except Exception as e:
            logger.warning("Failed to read text evidence %s: %s", evidence.original_filename, e)
            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type="text/plain",
                limitation_note=f"Could not read text file content: {str(e)}",
            )

    def _process_pdf_file(self, evidence: SubmissionEvidence, file_path: Path) -> ExtractedEvidenceItem:
        try:
            reader = pypdf.PdfReader(str(file_path))
            extracted_pages: List[str] = []
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(f"--- Page {page_idx + 1} ---\n{page_text}")

            full_text = "\n\n".join(extracted_pages).strip()
            if not full_text:
                return ExtractedEvidenceItem(
                    evidence_id=str(evidence.id),
                    original_filename=evidence.original_filename,
                    media_type="application/pdf",
                    limitation_note="PDF contains no extractable text (it may be a scanned document or image-only PDF without OCR).",
                )

            max_chars = 40000
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + f"\n... [PDF text truncated at {max_chars} characters for review]"

            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type="application/pdf",
                text_content=full_text,
            )
        except Exception as e:
            logger.warning("Failed to extract text from PDF %s: %s", evidence.original_filename, e)
            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type="application/pdf",
                limitation_note=f"PDF parsing error: {str(e)}",
            )

    def _process_image_file(self, evidence: SubmissionEvidence, file_path: Path) -> ExtractedEvidenceItem:
        try:
            data = file_path.read_bytes()
            # Normalize media type for Gemini Part
            m_type = "image/png" if evidence.original_filename.lower().endswith(".png") else "image/jpeg"
            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type=m_type,
                image_bytes=data,
            )
        except Exception as e:
            logger.warning("Failed to read image bytes %s: %s", evidence.original_filename, e)
            return ExtractedEvidenceItem(
                evidence_id=str(evidence.id),
                original_filename=evidence.original_filename,
                media_type=evidence.media_type,
                limitation_note=f"Image binary could not be read: {str(e)}",
            )

    def process_all_evidence(self, evidence_list: List[SubmissionEvidence]) -> List[ExtractedEvidenceItem]:
        """Process and extract content for all attached submission evidence."""
        return [self.extract_evidence_content(e) for e in evidence_list]


evidence_processing_service = EvidenceProcessingService()

