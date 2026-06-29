import type { ApiError } from "@passhub/shared";
import { getAccessToken } from "@/lib/auth-token-store";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string,
  ) {
    super(message);
  }
}

/** Every request sends cookies (`credentials: "include"`) so the refresh-token
 * and CSRF cookies reach the API even though frontend and backend are
 * different origins in development. The access token, if present, is
 * attached from in-memory state — it is never read from any storage API. */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const accessToken = getAccessToken();
  // FormData (file uploads) must NOT get an explicit Content-Type — the
  // browser sets one with the correct multipart boundary itself. Forcing
  // application/json here would silently strip that boundary.
  const isFormData = init?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiError | null;
    throw new ApiRequestError(
      body?.error.message ?? response.statusText,
      response.status,
      body?.error.code ?? "unknown_error",
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}
