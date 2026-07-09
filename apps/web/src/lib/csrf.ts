const SESSION_KEY = "ph_csrf_token";
export const CSRF_HEADER_NAME = "X-CSRF-Token";

export function getCsrfToken(): string | null {
  return sessionStorage.getItem(SESSION_KEY);
}

export function storeCsrfToken(token: string): void {
  sessionStorage.setItem(SESSION_KEY, token);
}

/** On the OAuth callback page the API passes the initial CSRF token as a URL
 * fragment (#csrf=...) since the SPA can't read cross-origin cookies.
 * Call this once on mount, then clear the fragment from the browser URL. */
export function extractCsrfFromHash(): string | null {
  const params = new URLSearchParams(window.location.hash.slice(1));
  const token = params.get("csrf");
  if (token) {
    storeCsrfToken(token);
    history.replaceState(null, "", window.location.pathname + window.location.search);
  }
  return token;
}
