import type { VehicleDocument } from "@passhub/shared";
import { DocumentCard } from "@/components/DocumentCard";
import { EmptyDocumentsState } from "@/components/EmptyDocumentsState";

interface DocumentListProps {
  vehicleId: string;
  documents: VehicleDocument[];
}

export function DocumentList({ vehicleId, documents }: DocumentListProps) {
  if (documents.length === 0) return <EmptyDocumentsState />;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {documents.map((document) => (
        <DocumentCard key={document.id} vehicleId={vehicleId} document={document} />
      ))}
    </div>
  );
}
