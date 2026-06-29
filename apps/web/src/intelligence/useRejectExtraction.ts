import type { DocumentExtraction } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { extractionQueryKey } from "@/intelligence/useExtraction";

export function useRejectExtraction(extractionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiFetch<DocumentExtraction>(`/intelligence/extractions/${extractionId}/reject`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionQueryKey(extractionId) });
    },
  });
}
