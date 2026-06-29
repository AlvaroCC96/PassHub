import type { DocumentType, DocumentVisibility } from "@passhub/shared";

export interface UploadDocumentInput {
  documentType: DocumentType;
  file: File;
  issueDate?: string;
  expirationDate?: string;
  visibility?: DocumentVisibility;
}

export interface UploadDocumentVersionInput {
  file: File;
  issueDate?: string;
  expirationDate?: string;
  visibility?: DocumentVisibility;
}

export function buildUploadFormData(
  input: UploadDocumentInput | UploadDocumentVersionInput,
): FormData {
  const formData = new FormData();
  if ("documentType" in input) {
    formData.append("document_type", input.documentType);
  }
  formData.append("file", input.file);
  if (input.issueDate) formData.append("issue_date", input.issueDate);
  if (input.expirationDate) formData.append("expiration_date", input.expirationDate);
  if (input.visibility) formData.append("visibility", input.visibility);
  return formData;
}
