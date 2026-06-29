import { useDocumentVersions } from "@/documents/useDocumentVersions";

interface DocumentVersionListProps {
  vehicleId: string;
  documentId: string;
}

export function DocumentVersionList({ vehicleId, documentId }: DocumentVersionListProps) {
  const { versions, isLoading } = useDocumentVersions(vehicleId, documentId);

  if (isLoading) return null;
  if (versions.length === 0) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">No versions uploaded yet.</p>;
  }

  return (
    <ul className="divide-y divide-slate-200 dark:divide-slate-800">
      {versions.map((version) => (
        <li key={version.id} className="flex items-center justify-between py-3 text-sm">
          <div>
            <p className="font-medium">
              v{version.version_number} · {version.original_filename}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {new Date(version.uploaded_at).toLocaleString()} ·{" "}
              {(version.file_size_bytes / 1024).toFixed(0)} KB
            </p>
          </div>
          {version.is_current && (
            <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400">
              Current
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}
