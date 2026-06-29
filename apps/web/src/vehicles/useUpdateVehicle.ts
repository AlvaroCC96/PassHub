import type { Vehicle, VehicleInput } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { VEHICLES_QUERY_KEY } from "@/vehicles/useVehicles";

export function useUpdateVehicle(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: VehicleInput) =>
      apiFetch<Vehicle>(`/drivepass/vehicles/${vehicleId}`, {
        method: "PUT",
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VEHICLES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["drivepass", "vehicles", vehicleId] });
    },
  });
}
