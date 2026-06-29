import { Link } from "react-router-dom";
import { BackLink } from "@/components/BackLink";
import { Loading } from "@/components/Loading";
import { VehicleCard } from "@/components/VehicleCard";
import { VehicleEmptyState } from "@/components/VehicleEmptyState";
import { useSetFavoriteVehicle } from "@/vehicles/useSetFavoriteVehicle";
import { useVehicles } from "@/vehicles/useVehicles";

const ADD_VEHICLE_LINK_CLASSES =
  "inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700";

export function VehicleListPage() {
  const { vehicles, isLoading } = useVehicles();
  const setFavorite = useSetFavoriteVehicle();

  return (
    <div>
      <BackLink to="/app/drive" label="Back to DrivePass" />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">My Vehicles</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Manage the vehicles registered to your DrivePass account.
          </p>
        </div>
        {vehicles.length > 0 && (
          <Link to="/app/drive/vehicles/new" className={ADD_VEHICLE_LINK_CLASSES}>
            Add Vehicle
          </Link>
        )}
      </div>

      <div className="mt-6">
        {isLoading ? (
          <Loading />
        ) : vehicles.length === 0 ? (
          <VehicleEmptyState />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {vehicles.map((vehicle) => (
              <VehicleCard
                key={vehicle.id}
                vehicle={vehicle}
                onToggleFavorite={() => setFavorite.mutate(vehicle.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
