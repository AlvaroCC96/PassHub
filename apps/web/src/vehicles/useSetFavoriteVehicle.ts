import type { Vehicle } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { VEHICLES_QUERY_KEY } from "@/vehicles/useVehicles";

/** Not in the originally named hook list, but `VehicleCard`/`FavoriteBadge`
 * need a way to call `PATCH /drivepass/vehicles/{id}/favorite` — added
 * alongside the requested CRUD hooks rather than inlining the fetch call. */
export function useSetFavoriteVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (vehicleId: string) =>
      apiFetch<Vehicle>(`/drivepass/vehicles/${vehicleId}/favorite`, { method: "PATCH" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: VEHICLES_QUERY_KEY }),
  });
}
