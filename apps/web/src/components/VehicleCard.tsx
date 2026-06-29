import type { Vehicle } from "@passhub/shared";
import { Link } from "react-router-dom";
import { FavoriteBadge } from "@/components/FavoriteBadge";
import { VehicleStatusBadge } from "@/components/VehicleStatusBadge";

interface VehicleCardProps {
  vehicle: Vehicle;
  onToggleFavorite?: () => void;
}

export function VehicleCard({ vehicle, onToggleFavorite }: VehicleCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 transition hover:border-brand-400 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-start justify-between">
        <span className="text-3xl" aria-hidden="true">
          🚗
        </span>
        <div className="flex items-center gap-2">
          <FavoriteBadge active={vehicle.favorite} onClick={onToggleFavorite} />
          <VehicleStatusBadge status={vehicle.status} />
        </div>
      </div>

      <Link to={`/app/drive/vehicles/${vehicle.id}`} className="mt-3 block">
        <h3 className="text-base font-semibold">{vehicle.nickname ?? `${vehicle.brand} ${vehicle.model}`}</h3>
        <p className="mt-1 font-mono text-sm tracking-wide text-slate-500 dark:text-slate-400">
          {vehicle.plate}
        </p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {vehicle.brand} {vehicle.model} · {vehicle.year}
        </p>
      </Link>
    </div>
  );
}
