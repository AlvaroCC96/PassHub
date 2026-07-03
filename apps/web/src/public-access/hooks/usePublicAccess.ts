import { useQuery } from "@tanstack/react-query";
import { ApiRequestError } from "@/lib/api-client";
import { fetchPublicAccess } from "../api";
import type { PublicAccessConfig } from "../types";

export function publicAccessQueryKey(vehicleId: string) {
  return ["public-access", vehicleId] as const;
}

export function usePublicAccess(vehicleId: string | undefined) {
  const query = useQuery<PublicAccessConfig>({
    queryKey: publicAccessQueryKey(vehicleId ?? ""),
    queryFn: () => fetchPublicAccess(vehicleId!),
    enabled: Boolean(vehicleId),
    retry: false,
  });

  return {
    config: query.data,
    isLoading: query.isLoading,
    isNotFound: query.error instanceof ApiRequestError && query.error.status === 404,
    error: query.error,
  };
}
