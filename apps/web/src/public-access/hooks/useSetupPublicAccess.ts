import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchSetupPublicAccess } from "../api";
import { publicAccessQueryKey } from "./usePublicAccess";

export function useSetupPublicAccess(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (pin: string) => fetchSetupPublicAccess(vehicleId, pin),
    onSuccess: (data) => {
      queryClient.setQueryData(publicAccessQueryKey(vehicleId), data);
    },
  });
}
