import { useMutation } from "@tanstack/react-query";
import { fetchChangePin } from "../api";

export function useChangePin(vehicleId: string) {
  return useMutation({
    mutationFn: ({ old_pin, new_pin }: { old_pin: string; new_pin: string }) =>
      fetchChangePin(vehicleId, old_pin, new_pin),
  });
}
