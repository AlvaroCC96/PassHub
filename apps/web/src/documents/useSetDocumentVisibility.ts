import { DocumentVisibility } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { documentsQueryKey } from "./useDocuments";

export function useSetDocumentVisibility(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, visibility }: { documentId: string; visibility: DocumentVisibility }) =>
      apiFetch(`/drivepass/vehicles/${vehicleId}/documents/${documentId}/visibility`, {
        method: "PATCH",
        body: JSON.stringify({ visibility }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsQueryKey(vehicleId) });
    },
  });
}
