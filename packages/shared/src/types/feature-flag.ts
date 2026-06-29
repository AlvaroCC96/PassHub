import type { ModuleCode } from "./module-code";

export enum FeatureFlagScope {
  Global = "GLOBAL",
  Module = "MODULE",
  User = "USER",
}

/** Mirrors `FeatureFlagResponse` returned by `GET /api/v1/platform/feature-flags`. */
export interface FeatureFlag {
  key: string;
  description: string;
  enabled: boolean;
  scope: FeatureFlagScope;
  module_code: ModuleCode | null;
}
