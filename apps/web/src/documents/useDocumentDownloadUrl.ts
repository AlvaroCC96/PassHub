import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

interface DownloadUrlResponse {
  url: string;
  expires_in: number;
}

/** A mutation, not a query — the backend mints a brand-new signed URL (and
 * logs an audit event) on every call, so this should only run when the user
 * actually clicks "View", never as a background/cached fetch. */
export function useDocumentDownloadUrl(vehicleId: string) {
  return useMutation({
    mutationFn: (documentId: string) =>
      apiFetch<DownloadUrlResponse>(
        `/drivepass/vehicles/${vehicleId}/documents/${documentId}/download-url`,
      ),
  });
}
