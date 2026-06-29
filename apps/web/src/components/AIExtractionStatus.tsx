import { ExtractionStatus } from "@passhub/shared";

const STYLES: Record<ExtractionStatus, string> = {
  [ExtractionStatus.Pending]: "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  [ExtractionStatus.Processing]: "bg-sky-100 text-sky-700 dark:bg-sky-500/20 dark:text-sky-400",
  [ExtractionStatus.Completed]:
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400",
  [ExtractionStatus.Failed]: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
  [ExtractionStatus.Confirmed]:
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400",
  [ExtractionStatus.Rejected]: "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
};

const LABELS: Record<ExtractionStatus, string> = {
  [ExtractionStatus.Pending]: "Pendiente",
  [ExtractionStatus.Processing]: "Procesando",
  [ExtractionStatus.Completed]: "Datos detectados",
  [ExtractionStatus.Failed]: "Análisis fallido",
  [ExtractionStatus.Confirmed]: "Confirmado",
  [ExtractionStatus.Rejected]: "Rechazado",
};

export function AIExtractionStatus({ status }: { status: ExtractionStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status]}`}
    >
      {LABELS[status]}
    </span>
  );
}
