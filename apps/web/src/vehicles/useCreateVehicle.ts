import type { Vehicle, VehicleInput } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { VEHICLES_QUERY_KEY } from "@/vehicles/useVehicles";

export function useCreateVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: VehicleInput) =>
      apiFetch<Vehicle>("/drivepass/vehicles/", { method: "POST", body: JSON.stringify(input) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: VEHICLES_QUERY_KEY }),
  });
}
