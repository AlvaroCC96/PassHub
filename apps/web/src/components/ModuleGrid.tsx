import type { PlatformModule } from "@passhub/shared";
import { ModuleCard } from "@/components/ModuleCard";

interface ModuleGridProps {
  modules: PlatformModule[];
  onEnableModule?: (module: PlatformModule) => void;
}

export function ModuleGrid({ modules, onEnableModule }: ModuleGridProps) {
  if (modules.length === 0) return null;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {modules.map((module) => (
        <ModuleCard
          key={module.code}
          module={module}
          onEnable={onEnableModule ? () => onEnableModule(module) : undefined}
        />
      ))}
    </div>
  );
}
