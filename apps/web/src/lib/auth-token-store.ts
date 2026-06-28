/**
 * Holds the access token in memory only — never localStorage, never a
 * non-HttpOnly cookie. A plain module-level variable (not React state) so
 * `api-client.ts` can read it on every request without importing React or
 * depending on `AuthContext`.
 */
let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}
