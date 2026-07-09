import type { CurrentUser } from "@passhub/shared";
import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { apiFetch, ApiRequestError } from "@/lib/api-client";
import { setAccessToken } from "@/lib/auth-token-store";
import { CSRF_HEADER_NAME, getCsrfToken, storeCsrfToken, extractCsrfFromHash } from "@/lib/csrf";
import type { AccessTokenResponse } from "@/auth/types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

export interface AuthContextValue {
  status: AuthStatus;
  user: CurrentUser | null;
  loginWithGoogle: () => void;
  /** Bootstraps a session from the HttpOnly refresh-token cookie. Used both
   * on app mount (to survive a page reload) and by the OAuth callback page
   * (to mint the first access token after Google redirects back). */
  restoreSession: () => Promise<boolean>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function fetchCurrentUser(): Promise<CurrentUser> {
  return apiFetch<CurrentUser>("/auth/me");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<CurrentUser | null>(null);

  const restoreSession = useCallback(async (): Promise<boolean> => {
    try {
      const csrfToken = getCsrfToken();
      const tokens = await apiFetch<AccessTokenResponse>("/auth/refresh", {
        method: "POST",
        headers: csrfToken ? { [CSRF_HEADER_NAME]: csrfToken } : {},
      });
      storeCsrfToken(tokens.csrf_token);
      setAccessToken(tokens.access_token);
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      setStatus("authenticated");
      return true;
    } catch {
      setAccessToken(null);
      setUser(null);
      setStatus("unauthenticated");
      return false;
    }
  }, []);

  useEffect(() => {
    // On the OAuth callback page the initial CSRF token arrives in the URL
    // hash (#csrf=...). Extract and cache it before the first refresh call.
    extractCsrfFromHash();
    void restoreSession();
  }, [restoreSession]);

  const loginWithGoogle = useCallback(() => {
    // Navigate directly to GET /auth/login (first-party navigation to the API).
    // This ensures the oauth_state cookie is stored without third-party cookie
    // restrictions that Chrome applies to cookies set via cross-origin fetch.
    window.location.href = `${API_BASE}/auth/login`;
  }, []);

  const logout = useCallback(async () => {
    const csrfToken = getCsrfToken();
    try {
      await apiFetch<void>("/auth/logout", {
        method: "POST",
        headers: csrfToken ? { [CSRF_HEADER_NAME]: csrfToken } : {},
      });
    } catch (error) {
      if (!(error instanceof ApiRequestError)) throw error;
    } finally {
      setAccessToken(null);
      setUser(null);
      setStatus("unauthenticated");
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, loginWithGoogle, restoreSession, logout }),
    [status, user, loginWithGoogle, restoreSession, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
