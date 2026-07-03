import { useQuery } from "@tanstack/react-query";
import { ApiRequestError } from "@/lib/api-client";
import { fetchPublicVehicle } from "../api";
import type { PublicVehicleInfo } from "../types";

export function publicVehicleQueryKey(publicToken: string) {
  return ["public-portal", publicToken, "vehicle"] as const;
}

export function usePublicVehicle(publicToken: string | undefined) {
  const query = useQuery<PublicVehicleInfo>({
    queryKey: publicVehicleQueryKey(publicToken ?? ""),
    queryFn: () => fetchPublicVehicle(publicToken!),
    enabled: Boolean(publicToken),
    retry: false,
    staleTime: 60_000,
  });

  return {
    vehicle: query.data,
    isLoading: query.isLoading,
    isNotFound: query.error instanceof ApiRequestError && query.error.status === 404,
    error: query.error,
  };
}
