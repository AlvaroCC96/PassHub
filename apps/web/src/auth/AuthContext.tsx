import type { CurrentUser } from "@passhub/shared";
import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { apiFetch, ApiRequestError } from "@/lib/api-client";
import { setAccessToken } from "@/lib/auth-token-store";
import { CSRF_HEADER_NAME, getCsrfToken } from "@/lib/csrf";
import type { AccessTokenResponse, LoginInitiateResponse } from "@/auth/types";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

export interface AuthContextValue {
  status: AuthStatus;
  user: CurrentUser | null;
  loginWithGoogle: () => Promise<void>;
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
    void restoreSession();
  }, [restoreSession]);

  const loginWithGoogle = useCallback(async () => {
    const { authorization_url } = await apiFetch<LoginInitiateResponse>("/auth/login", {
      method: "POST",
    });
    window.location.href = authorization_url;
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
