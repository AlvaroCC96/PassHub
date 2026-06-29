import type { Vehicle } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export function useVehicle(vehicleId: string | undefined) {
  const query = useQuery({
    queryKey: ["drivepass", "vehicles", vehicleId],
    queryFn: () => apiFetch<Vehicle>(`/drivepass/vehicles/${vehicleId}`),
    enabled: Boolean(vehicleId),
  });

  return { vehicle: query.data, isLoading: query.isLoading, error: query.error };
}
