import { useParams } from "react-router-dom";
import { BackLink } from "@/components/BackLink";
import { DocumentList } from "@/components/DocumentList";
import { DocumentSummaryCard } from "@/components/DocumentSummaryCard";
import { Loading } from "@/components/Loading";
import { useDocumentStatusSummary } from "@/documents/useDocumentStatusSummary";
import { useDocuments } from "@/documents/useDocuments";
import { useVehicle } from "@/vehicles/useVehicle";

export function DocumentsPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const { vehicle, isLoading: isVehicleLoading } = useVehicle(vehicleId);
  const { documents, isLoading: areDocumentsLoading } = useDocuments(vehicleId ?? "");
  const { summary } = useDocumentStatusSummary(vehicleId ?? "");

  if (isVehicleLoading || areDocumentsLoading) return <Loading />;
  if (!vehicle || !vehicleId) return null;

  return (
    <div>
      <BackLink to={`/app/drive/vehicles/${vehicleId}`} label="Back to vehicle" />

      <h1 className="text-2xl font-semibold">
        {vehicle.nickname ?? `${vehicle.brand} ${vehicle.model}`}
      </h1>
      <p className="font-mono text-sm tracking-wide text-slate-500 dark:text-slate-400">
        {vehicle.plate}
      </p>

      {summary && (
        <div className="mt-6">
          <DocumentSummaryCard summary={summary} />
        </div>
      )}

      <div className="mt-6">
        <DocumentList vehicleId={vehicleId} documents={documents} />
      </div>
    </div>
  );
}
