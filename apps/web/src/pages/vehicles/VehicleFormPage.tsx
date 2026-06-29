import type { VehicleInput } from "@passhub/shared";
import { useNavigate, useParams } from "react-router-dom";
import { ApiRequestError } from "@/lib/api-client";
import { BackLink } from "@/components/BackLink";
import { Loading } from "@/components/Loading";
import { VehicleForm } from "@/components/VehicleForm";
import { useCreateVehicle } from "@/vehicles/useCreateVehicle";
import { useUpdateVehicle } from "@/vehicles/useUpdateVehicle";
import { useVehicle } from "@/vehicles/useVehicle";

export function VehicleFormPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const isEditing = Boolean(vehicleId);
  const navigate = useNavigate();

  const { vehicle, isLoading } = useVehicle(vehicleId);
  const createVehicle = useCreateVehicle();
  const updateVehicle = useUpdateVehicle(vehicleId ?? "");

  const mutation = isEditing ? updateVehicle : createVehicle;

  const handleSubmit = (values: VehicleInput) => {
    mutation.mutate(values, {
      onSuccess: (saved) => navigate(`/app/drive/vehicles/${saved.id}`),
    });
  };

  if (isEditing && isLoading) return <Loading />;
  if (isEditing && !vehicle) return null;

  return (
    <div className="mx-auto max-w-2xl">
      <BackLink
        to={isEditing ? `/app/drive/vehicles/${vehicleId}` : "/app/drive/vehicles"}
        label={isEditing ? "Back to vehicle" : "Back to My Vehicles"}
      />

      <h1 className="text-2xl font-semibold">{isEditing ? "Edit Vehicle" : "Add Vehicle"}</h1>
      <div className="mt-6">
        <VehicleForm
          initialValues={vehicle ?? undefined}
          onSubmit={handleSubmit}
          isSubmitting={mutation.isPending}
          submitLabel={isEditing ? "Save changes" : "Add vehicle"}
          errorMessage={
            mutation.error instanceof ApiRequestError ? mutation.error.message : null
          }
        />
      </div>
    </div>
  );
}
