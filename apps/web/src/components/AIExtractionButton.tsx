import { Button } from "@passhub/ui";
import { LoadingModal } from "@/components/LoadingModal";
import { useExtractDocument } from "@/intelligence/useExtractDocument";
import { useReprocessDocument } from "@/intelligence/useReprocessDocument";

interface AIExtractionButtonProps {
  documentId: string;
  hasExtraction: boolean;
  onStarted?: () => void;
}

/** The one entry point into AI extraction from the document detail page —
 * hidden entirely by the caller when `ai.document_extraction.enabled` is
 * off (see `useFeatureFlag` in `DocumentDetailPage`). Shows a blocking
 * loading modal while the request is in flight — the OpenAI call can take
 * several seconds, long enough that just disabling the button isn't
 * enough feedback. */
export function AIExtractionButton({ documentId, hasExtraction, onStarted }: AIExtractionButtonProps) {
  const extract = useExtractDocument(documentId);
  const reprocess = useReprocessDocument(documentId);
  const mutation = hasExtraction ? reprocess : extract;

  const handleClick = () => {
    mutation.mutate(undefined, { onSuccess: onStarted });
  };

  return (
    <>
      <Button type="button" onClick={handleClick} disabled={mutation.isPending}>
        {hasExtraction ? "Reanalizar con IA" : "Analizar con IA"}
      </Button>
      <LoadingModal isOpen={mutation.isPending} message="Analizando información con IA…" />
    </>
  );
}
