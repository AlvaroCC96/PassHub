import type { PlatformModule } from "@passhub/shared";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { useAuth } from "@/auth/useAuth";

const MODULES_QUERY_KEY = ["platform", "modules"] as const;

async function fetchModules(): Promise<PlatformModule[]> {
  return apiFetch<PlatformModule[]>("/platform/modules");
}

/** All ACTIVE/COMING_SOON modules for the current user, each flagged with
 * whether they have it enabled. Only fetches once a session exists — there
 * is no point calling an authenticated endpoint before that. */
export function usePlatformModules() {
  const { status } = useAuth();
  const query = useQuery({
    queryKey: MODULES_QUERY_KEY,
    queryFn: fetchModules,
    enabled: status === "authenticated",
  });

  return {
    modules: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
  };
}

export function useInvalidatePlatformModules() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: MODULES_QUERY_KEY });
}
