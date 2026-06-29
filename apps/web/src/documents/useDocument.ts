import type { VehicleDocument } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export function useDocument(vehicleId: string | undefined, documentId: string | undefined) {
  const query = useQuery({
    queryKey: ["drivepass", "vehicles", vehicleId, "documents", documentId],
    queryFn: () =>
      apiFetch<VehicleDocument>(`/drivepass/vehicles/${vehicleId}/documents/${documentId}`),
    enabled: Boolean(vehicleId) && Boolean(documentId),
  });

  return { document: query.data, isLoading: query.isLoading };
}
