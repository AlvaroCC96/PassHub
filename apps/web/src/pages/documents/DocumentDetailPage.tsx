import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AIExtractionButton } from "@/components/AIExtractionButton";
import { AIExtractionResultPanel } from "@/components/AIExtractionResultPanel";
import { BackLink } from "@/components/BackLink";
import { DocumentStatusBadge } from "@/components/DocumentStatusBadge";
import { DocumentUploadModal } from "@/components/DocumentUploadModal";
import { DocumentVersionList } from "@/components/DocumentVersionList";
import { Loading } from "@/components/Loading";
import { useConfirmDialog } from "@/components/useConfirmDialog";
import { useDeleteDocument } from "@/documents/useDeleteDocument";
import { useDocument } from "@/documents/useDocument";
import { useDocumentDownloadUrl } from "@/documents/useDocumentDownloadUrl";
import { useDocumentExtractions } from "@/intelligence/useDocumentExtractions";
import { useFeatureFlag } from "@/platform/useFeatureFlags";

const AI_EXTRACTION_FEATURE_FLAG = "ai.document_extraction.enabled";

export function DocumentDetailPage() {
  const { vehicleId, documentId } = useParams<{ vehicleId: string; documentId: string }>();
  const navigate = useNavigate();
  const { document, isLoading } = useDocument(vehicleId, documentId);
  const downloadUrl = useDocumentDownloadUrl(vehicleId ?? "");
  const deleteDocument = useDeleteDocument(vehicleId ?? "");
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const aiExtractionEnabled = useFeatureFlag(AI_EXTRACTION_FEATURE_FLAG);
  const { extractions } = useDocumentExtractions(documentId ?? "");
  const { confirm, dialog } = useConfirmDialog();

  if (isLoading) return <Loading />;
  if (!document || !vehicleId || !documentId) return null;

  const latestExtraction = extractions[0];

  const hasVersion = document.current_version_id !== null;

  const handleDelete = async () => {
    const ok = await confirm({
      title: "Eliminar documento",
      message: `¿Eliminar ${document.display_name}?`,
      confirmLabel: "Eliminar",
      variant: "danger",
    });
    if (!ok) return;
    deleteDocument.mutate(documentId, {
      onSuccess: () => navigate(`/app/drive/vehicles/${vehicleId}/documents`),
    });
  };

  return (
    <div className="mx-auto max-w-2xl">
      <BackLink to={`/app/drive/vehicles/${vehicleId}/documents`} label="Back to documents" />

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{document.display_name}</h1>
        <DocumentStatusBadge status={document.status} />
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Required</dt>
          <dd className="font-medium">{document.is_required ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Expiration date</dt>
          <dd className="font-medium">
            {document.expiration_date
              ? new Date(document.expiration_date).toLocaleDateString()
              : "—"}
          </dd>
        </div>
      </dl>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => setIsUploadOpen(true)}
          className="inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700"
        >
          {hasVersion ? "Replace" : "Upload"}
        </button>
        {hasVersion && (
          <>
            <button
              type="button"
              onClick={() =>
                downloadUrl.mutate(documentId, {
                  onSuccess: (result) => window.open(result.url, "_blank", "noopener,noreferrer"),
                })
              }
              disabled={downloadUrl.isPending}
              className="inline-flex items-center justify-center rounded-md bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition-colors hover:bg-slate-200 disabled:opacity-50 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
            >
              View
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleteDocument.isPending}
              className="inline-flex items-center justify-center rounded-md bg-red-50 px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20"
            >
              Delete
            </button>
          </>
        )}
      </div>

      {aiExtractionEnabled && hasVersion && (
        <section className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Análisis con IA</h2>
            <AIExtractionButton documentId={documentId} hasExtraction={extractions.length > 0} />
          </div>
          {latestExtraction && (
            <div className="mt-3">
              <AIExtractionResultPanel extraction={latestExtraction} />
            </div>
          )}
        </section>
      )}

      <section className="mt-8">
        <h2 className="text-base font-semibold">Version history</h2>
        <div className="mt-3">
          <DocumentVersionList vehicleId={vehicleId} documentId={documentId} />
        </div>
      </section>

      <DocumentUploadModal
        vehicleId={vehicleId}
        displayName={document.display_name}
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        documentType={hasVersion ? undefined : document.document_type}
        documentId={hasVersion ? documentId : undefined}
      />
      {dialog}
    </div>
  );
}
