import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchRegenerateLink } from "../api";
import { publicAccessQueryKey } from "./usePublicAccess";

export function useRegenerateLink(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => fetchRegenerateLink(vehicleId),
    onSuccess: (data) => {
      queryClient.setQueryData(publicAccessQueryKey(vehicleId), data);
    },
  });
}
