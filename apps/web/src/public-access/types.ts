// ── Private management types ─────────────────────────────────────────────────

export interface PublicAccessConfig {
  enabled: boolean;
  public_token: string;
  public_url: string;
  failed_attempts: number;
  locked: boolean;
  status: "ACTIVE" | "DISABLED" | "LOCKED";
}

export interface PublicLinkResponse {
  url: string;
}

// ── Public portal types ───────────────────────────────────────────────────────

export interface PublicVehicleInfo {
  vehicle: string; // "Chevrolet Groove Premier"
  year: number;
  requires_pin: boolean;
  enabled: boolean;
  locked: boolean;
}

export interface PublicDocument {
  id: string;
  type: string; // DocumentType value
  status: string; // DocumentStatus value
}

export interface VerifyPinResponse {
  authenticated: boolean;
  expires_in: number; // seconds
}

export interface DownloadUrlResponse {
  url: string;
}

// ── Portal view state ─────────────────────────────────────────────────────────

export type PortalView = "loading" | "pin" | "documents" | "blocked" | "invalid";
