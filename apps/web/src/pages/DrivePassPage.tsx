import { Link } from "react-router-dom";
import { Loading } from "@/components/Loading";
import { VehicleCard } from "@/components/VehicleCard";
import { VehicleEmptyState } from "@/components/VehicleEmptyState";
import { useSetFavoriteVehicle } from "@/vehicles/useSetFavoriteVehicle";
import { useVehicles } from "@/vehicles/useVehicles";

const COMING_SOON_CARDS = ["Documents", "NFC Access", "AI Extraction", "Expiration Alerts"];

export function DrivePassPage() {
  const { vehicles, isLoading } = useVehicles();
  const setFavorite = useSetFavoriteVehicle();

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-semibold">DrivePass</h1>
        <p className="mt-1 text-slate-600 dark:text-slate-400">Digital Vehicle Identity</p>
      </div>

      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">My Vehicles</h2>
          {vehicles.length > 0 && (
            <Link to="/app/drive/vehicles" className="text-sm font-medium text-brand-600 dark:text-brand-400">
              View all →
            </Link>
          )}
        </div>
        <div className="mt-4">
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
      </section>

      <section>
        <h2 className="text-lg font-semibold">Coming up for DrivePass</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          This module is ready to be implemented in future sprints.
        </p>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {COMING_SOON_CARDS.map((title) => (
            <div
              key={title}
              className="rounded-xl border border-dashed border-slate-300 p-5 text-slate-400 dark:border-slate-700 dark:text-slate-500"
            >
              <h3 className="text-base font-medium">{title}</h3>
              <p className="mt-1 text-sm">Not implemented yet.</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
