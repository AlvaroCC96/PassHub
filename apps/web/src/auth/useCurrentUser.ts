import type { CurrentUser } from "@passhub/shared";
import { useAuth } from "@/auth/useAuth";

/** Thin accessor over the session already loaded by `AuthProvider`. A
 * TanStack Query wrapper isn't needed here since the user is fetched once
 * as part of session bootstrap, not refetched per-component. */
export function useCurrentUser(): { user: CurrentUser | null; isLoading: boolean } {
  const { user, status } = useAuth();
  return { user, isLoading: status === "loading" };
}
