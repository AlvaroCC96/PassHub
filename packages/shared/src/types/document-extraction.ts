import type { ExtractionStatus } from "./extraction-status";

export interface ExtractedFieldValue {
  value: string | null;
  confidence: number | null;
}

/** Shape of `DocumentExtraction.extracted_data` — the AI's full parsed
 * response, kept as one JSON blob on the backend. */
export interface ExtractedData {
  document_type: string;
  confidence_score: number;
  fields: Record<string, ExtractedFieldValue>;
  warnings: string[];
  requires_review: boolean;
}

/** Mirrors `DocumentExtractionResponse`. */
export interface DocumentExtraction {
  id: string;
  document_id: string;
  document_version_id: string;
  vehicle_id: string;
  status: ExtractionStatus;
  provider: string;
  model: string;
  prompt_version: string;
  extracted_data: ExtractedData | null;
  confidence_score: number | null;
  warnings: string[];
  requires_review: boolean;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  estimated_cost_usd: number | null;
  processing_time_ms: number | null;
  error_message: string | null;
  confirmed_at: string | null;
  rejected_at: string | null;
}

/** Mirrors `DocumentExtractedFieldResponse`. */
export interface DocumentExtractedField {
  id: string;
  field_name: string;
  field_value: string | null;
  normalized_value: string | null;
  confidence_score: number | null;
  source: string;
}

/** Mirrors `DocumentExtractionDetailResponse`. */
export interface DocumentExtractionDetail extends DocumentExtraction {
  fields: DocumentExtractedField[];
}
