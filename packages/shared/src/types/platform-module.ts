import type { ModuleCode } from "./module-code";
import type { ModuleStatus } from "./module-status";

/** Mirrors `PlatformModuleResponse` returned by `GET /api/v1/platform/modules`. */
export interface PlatformModule {
  code: ModuleCode;
  name: string;
  description: string;
  icon: string;
  route_path: string;
  status: ModuleStatus;
  is_core: boolean;
  sort_order: number;
  is_enabled: boolean;
}
