import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";

export interface DocumentVersionDto {
  id: string;
  version_number: number;
  original_filename: string;
  content_type: string;
  file_size_bytes: number;
  uploaded_by_user_id: string;
  uploaded_at: string;
  is_current: boolean;
}

export function useDocumentVersions(vehicleId: string, documentId: string | undefined) {
  const query = useQuery({
    queryKey: ["drivepass", "vehicles", vehicleId, "documents", documentId, "versions"],
    queryFn: () =>
      apiFetch<DocumentVersionDto[]>(
        `/drivepass/vehicles/${vehicleId}/documents/${documentId}/versions`,
      ),
    enabled: Boolean(vehicleId) && Boolean(documentId),
  });

  return { versions: query.data ?? [], isLoading: query.isLoading };
}
