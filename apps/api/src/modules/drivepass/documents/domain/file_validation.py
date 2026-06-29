"""File upload validation. Deliberately dependency-free (no `python-magic`/
`libmagic`) — the allowed set is five well-known formats, each identifiable
by a short, stable byte signature, so a hand-rolled sniffer is both simpler
and one less native dependency in the Docker image.
"""

import hashlib
import re

from src.core.exceptions import ValidationError

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

#: Maps the *real*, sniffed content type to the file extensions it's allowed
#: to be uploaded under. The client's declared `Content-Type` header is
#: never trusted — only this mapping, checked against the file's own bytes.
ALLOWED_CONTENT_TYPES: dict[str, frozenset[str]] = {
    "application/pdf": frozenset({".pdf"}),
    "image/jpeg": frozenset({".jpg", ".jpeg"}),
    "image/png": frozenset({".png"}),
    "image/webp": frozenset({".webp"}),
}

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def sniff_content_type(header: bytes) -> str | None:
    """Identifies a file by its magic bytes — the only thing in this module
    that decides what a file *actually* is."""
    if header.startswith(b"%PDF-"):
        return "application/pdf"
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    return None


def safe_filename(filename: str) -> str:
    """Strips any path component and replaces anything that isn't an
    alphanumeric, dot, dash, or underscore — defends against path traversal
    and shell/URL-unsafe characters ending up in a storage key."""
    base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    cleaned = _UNSAFE_FILENAME_CHARS.sub("_", base).strip("._")
    return cleaned or "file"


def compute_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_upload(*, filename: str, size_bytes: int, content_bytes: bytes) -> str:
    """Validates size, extension, and real file content. Returns the
    sniffed (trustworthy) content type — callers must store *this*, never
    whatever the client's `Content-Type` header claimed."""
    if size_bytes <= 0:
        raise ValidationError("Uploaded file is empty", error_code="empty_file")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"File exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit",
            error_code="file_too_large",
        )

    extension = _extract_extension(filename)
    sniffed_type = sniff_content_type(content_bytes[:32])
    if sniffed_type is None:
        raise ValidationError(
            "Unsupported or unrecognizable file type", error_code="unsupported_file_type"
        )

    allowed_extensions = ALLOWED_CONTENT_TYPES[sniffed_type]
    if extension not in allowed_extensions:
        raise ValidationError(
            f"File content ({sniffed_type}) does not match its extension ({extension})",
            error_code="file_content_mismatch",
        )

    return sniffed_type


def _extract_extension(filename: str) -> str:
    safe = safe_filename(filename)
    if "." not in safe:
        raise ValidationError("File is missing an extension", error_code="missing_file_extension")
    return f".{safe.rsplit('.', 1)[-1].lower()}"
