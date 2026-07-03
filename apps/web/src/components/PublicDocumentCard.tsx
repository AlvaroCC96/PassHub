import { DOCUMENT_TYPE_LABELS, DocumentType } from "@passhub/shared";
import type { PublicDocument } from "@/public-access/types";

interface PublicDocumentCardProps {
  document: PublicDocument;
  onView: (id: string) => void;
  isLoading?: boolean;
}

const STATUS_CONFIG: Record<
  string,
  { label: string; dot: string; text: string }
> = {
  VALID: {
    label: "Vigente",
    dot: "bg-emerald-500",
    text: "text-emerald-700 dark:text-emerald-400",
  },
  EXPIRING_SOON: {
    label: "Por vencer",
    dot: "bg-amber-500",
    text: "text-amber-700 dark:text-amber-400",
  },
  EXPIRED: {
    label: "Vencido",
    dot: "bg-red-500",
    text: "text-red-700 dark:text-red-400",
  },
  UPLOADED: {
    label: "Cargado",
    dot: "bg-slate-400",
    text: "text-slate-600 dark:text-slate-400",
  },
  MISSING: {
    label: "No disponible",
    dot: "bg-slate-300",
    text: "text-slate-500 dark:text-slate-500",
  },
  REJECTED: {
    label: "No disponible",
    dot: "bg-slate-300",
    text: "text-slate-500 dark:text-slate-500",
  },
};

const STATUS_DEFAULT = {
  label: "No disponible",
  dot: "bg-slate-300",
  text: "text-slate-500 dark:text-slate-500",
};

export function PublicDocumentCard({
  document,
  onView,
  isLoading,
}: PublicDocumentCardProps) {
  const label =
    DOCUMENT_TYPE_LABELS[document.type as DocumentType] ?? document.type;
  const statusCfg = STATUS_CONFIG[document.status] ?? STATUS_DEFAULT;

  return (
    <div className="flex items-center justify-between rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200 dark:bg-slate-800 dark:ring-slate-700">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-xl dark:bg-slate-700">
          📄
        </div>
        <div>
          <p className="font-medium text-slate-900 dark:text-white">{label}</p>
          <div className="mt-0.5 flex items-center gap-1.5">
            <span
              className={`inline-block h-2 w-2 rounded-full ${statusCfg.dot}`}
              aria-hidden="true"
            />
            <span className={`text-xs font-medium ${statusCfg.text}`}>
              {statusCfg.label}
            </span>
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => onView(document.id)}
        disabled={isLoading}
        className="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-brand-700 disabled:cursor-wait disabled:opacity-50"
      >
        {isLoading ? "Abriendo…" : "Ver"}
      </button>
    </div>
  );
}
