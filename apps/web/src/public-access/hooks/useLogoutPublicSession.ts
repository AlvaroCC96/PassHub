import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchLogoutPublicSession } from "../api";
import { publicDocumentsQueryKey } from "./usePublicDocuments";

export function useLogoutPublicSession(publicToken: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => fetchLogoutPublicSession(publicToken),
    onSuccess: () => {
      queryClient.removeQueries({
        queryKey: publicDocumentsQueryKey(publicToken),
      });
    },
  });
}
