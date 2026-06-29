import type { VehicleDocument } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { buildUploadFormData, type UploadDocumentVersionInput } from "@/documents/types";
import { documentStatusQueryKey } from "@/documents/useDocumentStatusSummary";
import { documentsQueryKey } from "@/documents/useDocuments";

export function useUploadDocumentVersion(vehicleId: string, documentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: UploadDocumentVersionInput) =>
      apiFetch<VehicleDocument>(
        `/drivepass/vehicles/${vehicleId}/documents/${documentId}/versions`,
        { method: "POST", body: buildUploadFormData(input) },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsQueryKey(vehicleId) });
      queryClient.invalidateQueries({ queryKey: documentStatusQueryKey(vehicleId) });
    },
  });
}
