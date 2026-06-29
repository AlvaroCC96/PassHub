import type { DocumentExtractionDetail } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export function extractionQueryKey(extractionId: string) {
  return ["intelligence", "extractions", extractionId] as const;
}

export function useExtraction(extractionId: string | undefined) {
  const query = useQuery({
    queryKey: extractionQueryKey(extractionId ?? ""),
    queryFn: () =>
      apiFetch<DocumentExtractionDetail>(`/intelligence/extractions/${extractionId}`),
    enabled: Boolean(extractionId),
  });

  return { extraction: query.data, isLoading: query.isLoading };
}
