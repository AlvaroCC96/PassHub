const CSRF_COOKIE_NAME = "ph_csrf_token";
export const CSRF_HEADER_NAME = "X-CSRF-Token";

/** Reads the non-HttpOnly CSRF cookie the backend pairs with the refresh-token
 * cookie. Echoed back as a header on `/auth/refresh` and `/auth/logout` —
 * the "double submit cookie" CSRF defense. */
export function getCsrfToken(): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${CSRF_COOKIE_NAME}=([^;]*)`));
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}
