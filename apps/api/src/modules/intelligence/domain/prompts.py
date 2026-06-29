from typing import Any

from src.modules.intelligence.domain.rules import required_extraction_fields
from src.modules.intelligence.domain.value_objects import ExtractableDocumentType

#: Bumped whenever the prompt or schema shape changes — stored on every
#: `DocumentExtraction` row so past extractions stay attributable to the
#: prompt version that produced them, even after this string moves on.
PROMPT_VERSION = "drivepass-document-extraction-v1"

_INSTRUCTIONS = """You are extracting structured data from a Chilean vehicle document (image or text).
Document type: {document_type}.
Fields to extract: {field_list}.

Rules:
- Extract ONLY information that is visibly present in the document. Never invent or infer a value.
- If a field is not present or not legible, return null for its value (and a low confidence).
- Normalize the plate ("plate" field, wherever present) to uppercase with no spaces or dashes \
(e.g. "ABCD-12" or "abcd 12" -> "ABCD12").
- Format every date field as ISO 8601 (YYYY-MM-DD). If only a partial date is visible, return null \
rather than guessing the missing part.
- Give a confidence between 0 and 1 for each individual field, and one overall confidence_score for \
the whole extraction.
- List any inconsistency you notice (e.g. a date that doesn't make sense, text that looks tampered \
with, a field that's ambiguous) in "warnings" as short human-readable strings. Empty array if none.
- Set "requires_review" to true if confidence_score is low, if any field is missing that you'd expect \
this document type to show, or if there are any warnings.
"""

_VIN_NOTE = """
Note on "vin" vs "chassis_number": this document may print a field explicitly labeled "VIN", a \
field labeled "N° de Chasis" / "Chasis", both, or only one of them — they are not always the same \
value or the same field. Put whatever is explicitly labeled "VIN" into the "vin" field, and \
whatever is explicitly labeled "Chasis"/"N° de Chasis" into "chassis_number" (Padrón only — ignore \
this second field if it isn't in the field list above). Do not copy one into the other, and do not \
invent a "vin" value just because "chassis_number" is present.
"""

_HOMOLOGACION_EXPIRATION_NOTE = """
Note on "expiration_date": a Certificado de Homologación typically labels its expiration as \
"VÁLIDO HASTA" or "VIGENCIA HASTA" rather than "Fecha de Vencimiento" — treat that label as \
"expiration_date" too.
"""


def build_prompt(document_type: ExtractableDocumentType) -> str:
    fields = required_extraction_fields(document_type)
    prompt = _INSTRUCTIONS.format(document_type=document_type.value, field_list=", ".join(fields))
    if "vin" in fields or "chassis_number" in fields:
        prompt += _VIN_NOTE
    if document_type == ExtractableDocumentType.CERTIFICADO_HOMOLOGACION:
        prompt += _HOMOLOGACION_EXPIRATION_NOTE
    return prompt


def build_json_schema(document_type: ExtractableDocumentType) -> dict[str, Any]:
    """Strict JSON Schema for the Responses API's Structured Outputs —
    every object sets `additionalProperties: false` and lists every key in
    `required` (strict mode rejects schemas that don't), and every
    optionally-absent value uses a `["string", "null"]` type union instead
    of omitting the key, since strict mode has no notion of an optional
    property."""
    fields = required_extraction_fields(document_type)
    field_properties = {
        field: {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": ["number", "null"]},
            },
            "required": ["value", "confidence"],
            "additionalProperties": False,
        }
        for field in fields
    }
    return {
        "type": "object",
        "properties": {
            "document_type": {"type": "string", "enum": [document_type.value]},
            "confidence_score": {"type": "number"},
            "fields": {
                "type": "object",
                "properties": field_properties,
                "required": list(fields),
                "additionalProperties": False,
            },
            "warnings": {"type": "array", "items": {"type": "string"}},
            "requires_review": {"type": "boolean"},
        },
        "required": ["document_type", "confidence_score", "fields", "warnings", "requires_review"],
        "additionalProperties": False,
    }
