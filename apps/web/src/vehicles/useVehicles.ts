import type { Vehicle } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { useAuth } from "@/auth/useAuth";

export const VEHICLES_QUERY_KEY = ["drivepass", "vehicles"] as const;

async function fetchVehicles(): Promise<Vehicle[]> {
  return apiFetch<Vehicle[]>("/drivepass/vehicles/");
}

export function useVehicles() {
  const { status } = useAuth();
  const query = useQuery({
    queryKey: VEHICLES_QUERY_KEY,
    queryFn: fetchVehicles,
    enabled: status === "authenticated",
  });

  return { vehicles: query.data ?? [], isLoading: query.isLoading, error: query.error };
}
