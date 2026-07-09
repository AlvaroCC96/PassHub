const SESSION_KEY = "ph_public_session";
export const PUBLIC_SESSION_HEADER = "X-Public-Session";

export function getPublicSessionToken(): string | null {
  return sessionStorage.getItem(SESSION_KEY);
}

export function storePublicSessionToken(token: string): void {
  sessionStorage.setItem(SESSION_KEY, token);
}

export function clearPublicSessionToken(): void {
  sessionStorage.removeItem(SESSION_KEY);
}
