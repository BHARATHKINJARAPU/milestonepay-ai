import hashlib
import logging
import os
from pathlib import Path
from typing import Optional, Set, Tuple
import uuid
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# Allowed file extensions and corresponding MIME types
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
}

MAX_FILE_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # 10 MB default
MAX_EVIDENCE_FILES = settings.MAX_EVIDENCE_FILES  # 5 default


class StorageService:
    """Manages file persistence, cryptographic verification, and safe file retrieval."""

    def __init__(self, base_dir: Optional[str] = None):
        # Resolve upload directory safely
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            self.base_dir = (Path(__file__).resolve().parent.parent.parent / settings.UPLOAD_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("StorageService initialized with base directory: %s", self.base_dir)

    def _sanitize_extension(self, filename: str) -> str:
        """Extract and validate file extension."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{ext}'. Allowed extensions are: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )
        return ext

    def _validate_mime_type(self, content_type: Optional[str]) -> str:
        """Validate content type against whitelist."""
        if not content_type:
            return "application/octet-stream"
        normalized = content_type.lower().split(";")[0].strip()
        if normalized not in ALLOWED_MIME_TYPES and normalized != "application/octet-stream":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported media type '{normalized}'. Supported types: PDF, PNG, JPG/JPEG, TXT.",
            )
        return normalized

    async def save_uploaded_file(self, upload_file: UploadFile) -> Tuple[str, int, str, str]:
        """Save an UploadFile securely with sha256 calculation and random storage key.

        Returns: (storage_key, file_size_bytes, sha256_hash, media_type)
        """
        filename = upload_file.filename or "upload"
        ext = self._sanitize_extension(filename)
        media_type = self._validate_mime_type(upload_file.content_type)

        # Generate unique random storage key
        random_id = uuid.uuid4().hex
        storage_key = f"{random_id}{ext}"
        destination_path = (self.base_dir / storage_key).resolve()

        # Path traversal defense
        if not str(destination_path).startswith(str(self.base_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file storage path.",
            )

        sha256 = hashlib.sha256()
        file_size = 0
        chunk_size = 1024 * 64  # 64 KB chunks

        try:
            with open(destination_path, "wb") as buffer:
                while True:
                    chunk = await upload_file.read(chunk_size)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > MAX_FILE_SIZE_BYTES:
                        # Clean up partial file on oversize
                        buffer.close()
                        if destination_path.exists():
                            destination_path.unlink()
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
                        )
                    sha256.update(chunk)
                    buffer.write(chunk)
        except HTTPException:
            raise
        except Exception as e:
            if destination_path.exists():
                destination_path.unlink()
            logger.error("Failed to write uploaded file %s: %s", filename, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store uploaded evidence file.",
            )

        if file_size == 0:
            if destination_path.exists():
                destination_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty files cannot be uploaded as evidence.",
            )

        return storage_key, file_size, sha256.hexdigest(), media_type

    def get_file_path(self, storage_key: str) -> Path:
        """Resolve physical file path for a storage key with path traversal prevention."""
        clean_key = os.path.basename(storage_key)
        file_path = (self.base_dir / clean_key).resolve()

        if not str(file_path).startswith(str(self.base_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path identifier.",
            )

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence file not found on storage.",
            )

        return file_path

    def delete_file(self, storage_key: str) -> bool:
        """Safely delete file from disk storage."""
        try:
            file_path = self.get_file_path(storage_key)
            if file_path.exists():
                file_path.unlink()
                logger.info("Deleted evidence file: %s", storage_key)
                return True
        except HTTPException:
            pass
        except Exception as e:
            logger.warning("Failed to delete evidence file %s: %s", storage_key, e)
        return False


storage_service = StorageService()
