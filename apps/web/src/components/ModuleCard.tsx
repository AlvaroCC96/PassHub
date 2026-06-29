import { ModuleStatus, type PlatformModule } from "@passhub/shared";
import { Link } from "react-router-dom";
import { ComingSoonBadge } from "@/components/ComingSoonBadge";
import { getModuleIcon } from "@/lib/module-icons";

interface ModuleCardProps {
  module: PlatformModule;
  onEnable?: () => void;
}

export function ModuleCard({ module, onEnable }: ModuleCardProps) {
  const isLocked = module.status === ModuleStatus.ComingSoon;

  const content = (
    <>
      <div className="flex items-start justify-between">
        <span className="text-3xl" aria-hidden="true">
          {getModuleIcon(module.icon)}
        </span>
        {isLocked && <ComingSoonBadge />}
      </div>
      <h3 className="mt-3 text-base font-semibold">{module.name}</h3>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{module.description}</p>
    </>
  );

  const cardClasses =
    "rounded-xl border border-slate-200 bg-white p-5 transition dark:border-slate-800 dark:bg-slate-900";

  if (isLocked) {
    return <div className={`${cardClasses} opacity-60`}>{content}</div>;
  }

  if (module.is_enabled) {
    return (
      <Link to={module.route_path} className={`${cardClasses} hover:border-brand-400 hover:shadow-sm`}>
        {content}
      </Link>
    );
  }

  return (
    <button type="button" onClick={onEnable} className={`${cardClasses} text-left hover:border-brand-400`}>
      {content}
      <span className="mt-3 inline-block text-sm font-medium text-brand-600 dark:text-brand-400">
        Enable →
      </span>
    </button>
  );
}
