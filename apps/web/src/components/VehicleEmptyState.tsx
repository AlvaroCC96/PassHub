import { Link } from "react-router-dom";

export function VehicleEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 px-6 py-16 text-center dark:border-slate-700">
      <span className="text-4xl" aria-hidden="true">
        🚗
      </span>
      <h3 className="mt-4 text-base font-semibold">No vehicles yet</h3>
      <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
        Add your first vehicle to start building its digital identity in DrivePass.
      </p>
      <Link
        to="/app/drive/vehicles/new"
        className="mt-6 inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700"
      >
        Add Vehicle
      </Link>
    </div>
  );
}
