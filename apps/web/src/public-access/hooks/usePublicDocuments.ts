import { useQuery } from "@tanstack/react-query";
import { fetchPublicDocuments } from "../api";
import type { PublicDocument } from "../types";

export function publicDocumentsQueryKey(publicToken: string) {
  return ["public-portal", publicToken, "documents"] as const;
}

export function usePublicDocuments(
  publicToken: string | undefined,
  enabled: boolean,
) {
  const query = useQuery<PublicDocument[]>({
    queryKey: publicDocumentsQueryKey(publicToken ?? ""),
    queryFn: () => fetchPublicDocuments(publicToken!),
    enabled: Boolean(publicToken) && enabled,
    retry: false,
    staleTime: 30_000,
  });

  return {
    documents: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
}
