import type { DocumentExtraction } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { extractionsQueryKey } from "@/intelligence/useDocumentExtractions";

export function useExtractDocument(documentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiFetch<DocumentExtraction>(`/intelligence/documents/${documentId}/extract`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionsQueryKey(documentId) });
    },
  });
}
