import type { DocumentExtraction } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export function extractionsQueryKey(documentId: string) {
  return ["intelligence", "documents", documentId, "extractions"] as const;
}

export function useDocumentExtractions(documentId: string) {
  const query = useQuery({
    queryKey: extractionsQueryKey(documentId),
    queryFn: () =>
      apiFetch<DocumentExtraction[]>(`/intelligence/documents/${documentId}/extractions`),
    enabled: Boolean(documentId),
  });

  return { extractions: query.data ?? [], isLoading: query.isLoading };
}
