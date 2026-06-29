import type { VehicleDocument } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export function documentsQueryKey(vehicleId: string) {
  return ["drivepass", "vehicles", vehicleId, "documents"] as const;
}

export function useDocuments(vehicleId: string) {
  const query = useQuery({
    queryKey: documentsQueryKey(vehicleId),
    queryFn: () => apiFetch<VehicleDocument[]>(`/drivepass/vehicles/${vehicleId}/documents/`),
    enabled: Boolean(vehicleId),
  });

  return { documents: query.data ?? [], isLoading: query.isLoading, error: query.error };
}
