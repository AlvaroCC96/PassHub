import type { PublicVehicleInfo } from "@/public-access/types";

interface PublicVehicleCardProps {
  info: PublicVehicleInfo;
  children?: React.ReactNode;
}

export function PublicVehicleCard({ info, children }: PublicVehicleCardProps) {
  return (
    <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-6 text-white shadow-2xl dark:from-slate-800 dark:to-slate-700">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">
            PassHub DrivePass
          </p>
          <h1 className="mt-1 text-2xl font-bold leading-tight">{info.vehicle}</h1>
          <p className="mt-0.5 text-slate-300">{info.year}</p>
        </div>
        <span className="text-5xl" aria-hidden="true">🚗</span>
      </div>

      {/* Divider */}
      <div className="my-4 h-px bg-white/10" />

      {/* Status */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-400">Estado de acceso</span>
        <span className={`font-semibold ${info.locked ? "text-red-400" : "text-emerald-400"}`}>
          {info.locked ? "🔒 Bloqueado" : "🔓 Verificado"}
        </span>
      </div>

      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
