import type { DocumentStatusSummary } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export function documentStatusQueryKey(vehicleId: string) {
  return ["drivepass", "vehicles", vehicleId, "documents", "status"] as const;
}

export function useDocumentStatusSummary(vehicleId: string) {
  const query = useQuery({
    queryKey: documentStatusQueryKey(vehicleId),
    queryFn: () =>
      apiFetch<DocumentStatusSummary>(`/drivepass/vehicles/${vehicleId}/documents/status`),
    enabled: Boolean(vehicleId),
  });

  return { summary: query.data, isLoading: query.isLoading };
}
