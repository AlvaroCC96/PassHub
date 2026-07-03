import { apiFetch } from "@/lib/api-client";
import type {
  DownloadUrlResponse,
  PublicAccessConfig,
  PublicDocument,
  PublicLinkResponse,
  PublicVehicleInfo,
  VerifyPinResponse,
} from "./types";

// ── Private endpoints (auth required) ────────────────────────────────────────

export function fetchPublicAccess(vehicleId: string) {
  return apiFetch<PublicAccessConfig>(
    `/drivepass/vehicles/${vehicleId}/public-access/`,
  );
}

export function fetchSetupPublicAccess(vehicleId: string, pin: string) {
  return apiFetch<PublicAccessConfig>(
    `/drivepass/vehicles/${vehicleId}/public-access/setup`,
    { method: "POST", body: JSON.stringify({ pin }) },
  );
}

export function fetchSetPublicEnabled(vehicleId: string, enabled: boolean) {
  return apiFetch<PublicAccessConfig>(
    `/drivepass/vehicles/${vehicleId}/public-access/enabled`,
    { method: "PATCH", body: JSON.stringify({ enabled }) },
  );
}

export function fetchChangePin(
  vehicleId: string,
  old_pin: string,
  new_pin: string,
) {
  return apiFetch<void>(
    `/drivepass/vehicles/${vehicleId}/public-access/pin`,
    { method: "POST", body: JSON.stringify({ old_pin, new_pin }) },
  );
}

export function fetchRegenerateLink(vehicleId: string) {
  return apiFetch<PublicAccessConfig>(
    `/drivepass/vehicles/${vehicleId}/public-access/regenerate`,
    { method: "POST" },
  );
}

export function fetchPublicLink(vehicleId: string) {
  return apiFetch<PublicLinkResponse>(
    `/drivepass/vehicles/${vehicleId}/public-access/link`,
  );
}

// ── Public endpoints (no auth — session via HttpOnly cookie) ─────────────────

export function fetchPublicVehicle(publicToken: string) {
  return apiFetch<PublicVehicleInfo>(`/public/drive/${publicToken}/`);
}

export function fetchVerifyPin(publicToken: string, pin: string) {
  return apiFetch<VerifyPinResponse>(
    `/public/drive/${publicToken}/verify-pin`,
    { method: "POST", body: JSON.stringify({ pin }) },
  );
}

export function fetchPublicDocuments(publicToken: string) {
  return apiFetch<PublicDocument[]>(`/public/drive/${publicToken}/documents`);
}

export function fetchDocumentDownloadUrl(
  publicToken: string,
  documentId: string,
) {
  return apiFetch<DownloadUrlResponse>(
    `/public/drive/${publicToken}/documents/${documentId}/download-url`,
  );
}

export function fetchLogoutPublicSession(publicToken: string) {
  return apiFetch<void>(`/public/drive/${publicToken}/logout`, {
    method: "POST",
  });
}
