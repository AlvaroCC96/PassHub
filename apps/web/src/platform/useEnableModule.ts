import type { ModuleCode, PlatformModule } from "@passhub/shared";
import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { useInvalidatePlatformModules } from "@/platform/usePlatformModules";

export function useEnableModule() {
  const invalidate = useInvalidatePlatformModules();

  return useMutation({
    mutationFn: (code: ModuleCode) =>
      apiFetch<PlatformModule>(`/platform/modules/${code}/enable`, { method: "POST" }),
    onSuccess: () => invalidate(),
  });
}
