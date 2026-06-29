import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { documentStatusQueryKey } from "@/documents/useDocumentStatusSummary";
import { documentsQueryKey } from "@/documents/useDocuments";

export function useDeleteDocument(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) =>
      apiFetch<void>(`/drivepass/vehicles/${vehicleId}/documents/${documentId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsQueryKey(vehicleId) });
      queryClient.invalidateQueries({ queryKey: documentStatusQueryKey(vehicleId) });
    },
  });
}
