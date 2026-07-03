import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchSetPublicEnabled } from "../api";
import { publicAccessQueryKey } from "./usePublicAccess";

export function useSetEnabled(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (enabled: boolean) => fetchSetPublicEnabled(vehicleId, enabled),
    onSuccess: (data) => {
      queryClient.setQueryData(publicAccessQueryKey(vehicleId), data);
    },
  });
}
