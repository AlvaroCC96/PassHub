import type { FeatureFlag } from "@passhub/shared";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/auth/useAuth";
import { apiFetch } from "@/lib/api-client";

const FEATURE_FLAGS_QUERY_KEY = ["platform", "feature-flags"] as const;

async function fetchFeatureFlags(): Promise<FeatureFlag[]> {
  return apiFetch<FeatureFlag[]>("/platform/feature-flags");
}

/** Every flag relevant to the current user (GLOBAL ones, plus MODULE ones
 * for modules they have enabled) — only fetched once a session exists. */
export function useFeatureFlags() {
  const { status } = useAuth();
  const query = useQuery({
    queryKey: FEATURE_FLAGS_QUERY_KEY,
    queryFn: fetchFeatureFlags,
    enabled: status === "authenticated",
  });

  return { flags: query.data ?? [], isLoading: query.isLoading };
}

/** `true` only once flags have loaded and the named flag is both present and
 * enabled — defaults to `false` while loading or if the flag is absent, so a
 * gated button never flashes on before flipping off. */
export function useFeatureFlag(key: string): boolean {
  const { flags } = useFeatureFlags();
  return flags.some((flag) => flag.key === key && flag.enabled);
}
