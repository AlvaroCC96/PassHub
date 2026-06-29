from io import BytesIO

from pypdf import PdfReader

#: Below this many non-whitespace characters, a PDF is treated as having no
#: usable text layer (i.e. it's a scan) — arbitrary but generous: a real
#: vehicle document's first page alone is comfortably hundreds of
#: characters once it has any text layer at all.
MIN_USEFUL_TEXT_CHARS = 30


def extract_pdf_text(content_bytes: bytes) -> str | None:
    """Best-effort text-layer extraction — no OCR, no image rendering. Returns
    `None` if the PDF can't be parsed or has no meaningful text layer (a
    scanned document, for instance), signaling the caller to fall back
    rather than send an empty prompt to the AI provider."""
    try:
        reader = PdfReader(BytesIO(content_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        # Any malformed-PDF error means "no usable text", not a crash.
        return None

    if len(text.strip()) < MIN_USEFUL_TEXT_CHARS:
        return None
    return text
