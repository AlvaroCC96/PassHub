import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { VEHICLES_QUERY_KEY } from "@/vehicles/useVehicles";

export function useDeleteVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (vehicleId: string) =>
      apiFetch<void>(`/drivepass/vehicles/${vehicleId}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: VEHICLES_QUERY_KEY }),
  });
}
