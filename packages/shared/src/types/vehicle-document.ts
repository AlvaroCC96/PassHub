import type { DocumentStatus } from "./document-status";
import type { DocumentType } from "./document-type";
import type { DocumentVisibility } from "./document-visibility";
import type { OverallDocumentStatus } from "./overall-document-status";

/** Mirrors `VehicleDocumentResponse`. */
export interface VehicleDocument {
  id: string;
  document_type: DocumentType;
  display_name: string;
  status: DocumentStatus;
  visibility: DocumentVisibility;
  is_required: boolean;
  issue_date: string | null;
  expiration_date: string | null;
  current_version_id: string | null;
}

/** Mirrors `DocumentStatusSummaryResponse`. */
export interface DocumentStatusSummary {
  total_documents: number;
  required_documents: number;
  uploaded_documents: number;
  missing_required_documents: number;
  expired_documents: number;
  expiring_soon_documents: number;
  completion_percentage: number;
  overall_status: OverallDocumentStatus;
}
