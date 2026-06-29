/** Mirrors `PlatformSettingResponse` returned by `GET /api/v1/platform/settings/public`. */
export interface PlatformSetting {
  key: string;
  value: unknown;
  description: string;
}
