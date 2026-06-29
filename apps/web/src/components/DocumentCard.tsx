import type { VehicleDocument } from "@passhub/shared";
import { useState } from "react";
import { Link } from "react-router-dom";
import { DocumentStatusBadge } from "@/components/DocumentStatusBadge";
import { DocumentUploadModal } from "@/components/DocumentUploadModal";
import { useDeleteDocument } from "@/documents/useDeleteDocument";
import { useDocumentDownloadUrl } from "@/documents/useDocumentDownloadUrl";

interface DocumentCardProps {
  vehicleId: string;
  document: VehicleDocument;
}

export function DocumentCard({ vehicleId, document }: DocumentCardProps) {
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const downloadUrl = useDocumentDownloadUrl(vehicleId);
  const deleteDocument = useDeleteDocument(vehicleId);

  const hasVersion = document.current_version_id !== null;

  const handleView = () => {
    downloadUrl.mutate(document.id, {
      onSuccess: (result) => window.open(result.url, "_blank", "noopener,noreferrer"),
    });
  };

  const handleDelete = () => {
    if (!window.confirm(`Remove ${document.display_name}? You can upload it again later.`)) return;
    deleteDocument.mutate(document.id);
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-start justify-between">
        <div>
          <Link to={`/app/drive/vehicles/${vehicleId}/documents/${document.id}`} className="hover:underline">
            <h3 className="text-base font-semibold">{document.display_name}</h3>
          </Link>
          {document.is_required && (
            <p className="text-xs text-slate-500 dark:text-slate-400">Required</p>
          )}
        </div>
        <DocumentStatusBadge status={document.status} />
      </div>

      {document.expiration_date && (
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
          Expires {new Date(document.expiration_date).toLocaleDateString()}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setIsUploadOpen(true)}
          className="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-900 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
        >
          {hasVersion ? "Replace" : "Upload"}
        </button>
        {hasVersion && (
          <>
            <button
              type="button"
              onClick={handleView}
              disabled={downloadUrl.isPending}
              className="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-900 transition-colors hover:bg-slate-200 disabled:opacity-50 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
            >
              View
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleteDocument.isPending}
              className="rounded-md bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20"
            >
              Delete
            </button>
          </>
        )}
      </div>

      <DocumentUploadModal
        vehicleId={vehicleId}
        displayName={document.display_name}
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        documentType={hasVersion ? undefined : document.document_type}
        documentId={hasVersion ? document.id : undefined}
      />
    </div>
  );
}
