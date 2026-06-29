import { Link, useNavigate, useParams } from "react-router-dom";
import { BackLink } from "@/components/BackLink";
import { Loading } from "@/components/Loading";
import { useConfirmDialog } from "@/components/useConfirmDialog";
import { VehicleHeader } from "@/components/VehicleHeader";
import { useDeleteVehicle } from "@/vehicles/useDeleteVehicle";
import { useSetFavoriteVehicle } from "@/vehicles/useSetFavoriteVehicle";
import { useVehicle } from "@/vehicles/useVehicle";

export function VehicleDetailPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const navigate = useNavigate();
  const { vehicle, isLoading } = useVehicle(vehicleId);
  const setFavorite = useSetFavoriteVehicle();
  const deleteVehicle = useDeleteVehicle();
  const { confirm, dialog } = useConfirmDialog();

  const handleDelete = async () => {
    if (!vehicleId) return;
    const ok = await confirm({
      title: "Eliminar vehículo",
      message: "Esto no se puede deshacer desde la app. ¿Deseas continuar?",
      confirmLabel: "Eliminar",
      variant: "danger",
    });
    if (!ok) return;
    deleteVehicle.mutate(vehicleId, { onSuccess: () => navigate("/app/drive/vehicles") });
  };

  if (isLoading) return <Loading />;
  if (!vehicle) return null;

  return (
    <div className="mx-auto max-w-2xl">
      <BackLink to="/app/drive/vehicles" label="Back to My Vehicles" />

      <VehicleHeader vehicle={vehicle} onToggleFavorite={() => setFavorite.mutate(vehicle.id)} />

      <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
        <Detail label="Brand" value={vehicle.brand} />
        <Detail label="Model" value={vehicle.model} />
        <Detail label="Year" value={String(vehicle.year)} />
        <Detail label="Color" value={vehicle.color} />
        <Detail label="VIN" value={vehicle.vin} />
        <Detail label="Engine number" value={vehicle.engine_number} />
        <Detail label="Fuel type" value={vehicle.fuel_type} />
        <Detail label="Transmission" value={vehicle.transmission} />
      </dl>

      <div className="mt-8 flex gap-3">
        <Link
          to={`/app/drive/vehicles/${vehicle.id}/documents`}
          className="inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700"
        >
          Documents
        </Link>
        <Link
          to={`/app/drive/vehicles/${vehicle.id}/edit`}
          className="inline-flex items-center justify-center rounded-md bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
        >
          Edit
        </Link>
        <button
          type="button"
          onClick={handleDelete}
          disabled={deleteVehicle.isPending}
          className="inline-flex items-center justify-center rounded-md bg-red-50 px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20"
        >
          {deleteVehicle.isPending ? "Removing…" : "Remove"}
        </button>
      </div>
      {dialog}
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className="font-medium">{value ?? "—"}</dd>
    </div>
  );
}
