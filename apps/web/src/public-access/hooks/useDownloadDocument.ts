import { useMutation } from "@tanstack/react-query";
import { fetchDocumentDownloadUrl } from "../api";

export function useDownloadDocument(publicToken: string) {
  return useMutation({
    mutationFn: (documentId: string) =>
      fetchDocumentDownloadUrl(publicToken, documentId),
    onSuccess: ({ url }) => {
      window.open(url, "_blank", "noopener,noreferrer");
    },
  });
}
