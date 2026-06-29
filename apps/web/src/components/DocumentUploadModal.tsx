import { DocumentVisibility, type DocumentType } from "@passhub/shared";
import { Button } from "@passhub/ui";
import { useState } from "react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { ApiRequestError } from "@/lib/api-client";
import { useUploadDocument } from "@/documents/useUploadDocument";
import { useUploadDocumentVersion } from "@/documents/useUploadDocumentVersion";

interface DocumentUploadModalProps {
  vehicleId: string;
  displayName: string;
  isOpen: boolean;
  onClose: () => void;
  /** Provide exactly one of these: a `documentType` starts a brand-new
   * document's first version; a `documentId` replaces an existing one. */
  documentType?: DocumentType;
  documentId?: string;
}

export function DocumentUploadModal({
  vehicleId,
  displayName,
  isOpen,
  onClose,
  documentType,
  documentId,
}: DocumentUploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [expirationDate, setExpirationDate] = useState("");
  const [visibility, setVisibility] = useState<DocumentVisibility>(DocumentVisibility.Private);

  const uploadInitial = useUploadDocument(vehicleId);
  const uploadVersion = useUploadDocumentVersion(vehicleId, documentId ?? "");
  const mutation = documentId ? uploadVersion : uploadInitial;

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!file) return;
    const shared = { file, expirationDate: expirationDate || undefined, visibility };

    if (documentId) {
      uploadVersion.mutate(shared, { onSuccess: () => closeAndReset() });
    } else if (documentType) {
      uploadInitial.mutate({ ...shared, documentType }, { onSuccess: () => closeAndReset() });
    }
  };

  const closeAndReset = () => {
    setFile(null);
    setExpirationDate("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-lg dark:bg-slate-900">
        <h2 className="text-lg font-semibold">
          {documentId ? "Replace" : "Upload"} {displayName}
        </h2>

        {mutation.error && (
          <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
            {mutation.error instanceof ApiRequestError ? mutation.error.message : "Upload failed"}
          </p>
        )}

        <div className="mt-4 space-y-4">
          <UploadDropzone file={file} onFileSelected={setFile} />

          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">Expiration date (optional)</span>
            <input
              type="date"
              value={expirationDate}
              onChange={(event) => setExpirationDate(event.target.value)}
              className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">Visibility</span>
            <select
              value={visibility}
              onChange={(event) => setVisibility(event.target.value as DocumentVisibility)}
              className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            >
              <option value={DocumentVisibility.Private}>Private</option>
              <option value={DocumentVisibility.OwnerOnly}>Owner only</option>
            </select>
          </label>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={closeAndReset}
            className="rounded-md px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Cancel
          </button>
          <Button type="button" onClick={handleSubmit} disabled={!file || mutation.isPending}>
            {mutation.isPending ? "Uploading…" : "Upload"}
          </Button>
        </div>
      </div>
    </div>
  );
}
