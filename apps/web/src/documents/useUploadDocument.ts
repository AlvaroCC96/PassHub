import type { VehicleDocument } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { buildUploadFormData, type UploadDocumentInput } from "@/documents/types";
import { documentStatusQueryKey } from "@/documents/useDocumentStatusSummary";
import { documentsQueryKey } from "@/documents/useDocuments";

export function useUploadDocument(vehicleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: UploadDocumentInput) =>
      apiFetch<VehicleDocument>(`/drivepass/vehicles/${vehicleId}/documents/`, {
        method: "POST",
        body: buildUploadFormData(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsQueryKey(vehicleId) });
      queryClient.invalidateQueries({ queryKey: documentStatusQueryKey(vehicleId) });
    },
  });
}
