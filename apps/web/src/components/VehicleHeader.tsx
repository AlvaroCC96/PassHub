import type { Vehicle } from "@passhub/shared";
import { FavoriteBadge } from "@/components/FavoriteBadge";
import { VehicleStatusBadge } from "@/components/VehicleStatusBadge";

interface VehicleHeaderProps {
  vehicle: Vehicle;
  onToggleFavorite?: () => void;
}

export function VehicleHeader({ vehicle, onToggleFavorite }: VehicleHeaderProps) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold">
            {vehicle.nickname ?? `${vehicle.brand} ${vehicle.model}`}
          </h1>
          <FavoriteBadge active={vehicle.favorite} onClick={onToggleFavorite} />
        </div>
        <p className="mt-1 font-mono text-sm tracking-wide text-slate-500 dark:text-slate-400">
          {vehicle.plate}
        </p>
      </div>
      <VehicleStatusBadge status={vehicle.status} />
    </div>
  );
}
