import { DocumentStatus } from "@passhub/shared";

const STYLES: Record<DocumentStatus, string> = {
  [DocumentStatus.Missing]: "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  [DocumentStatus.Uploaded]: "bg-sky-100 text-sky-700 dark:bg-sky-500/20 dark:text-sky-400",
  [DocumentStatus.Valid]: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400",
  [DocumentStatus.ExpiringSoon]: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400",
  [DocumentStatus.Expired]: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
  [DocumentStatus.Rejected]: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
  [DocumentStatus.NotApplicable]: "bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500",
};

const LABELS: Record<DocumentStatus, string> = {
  [DocumentStatus.Missing]: "Missing",
  [DocumentStatus.Uploaded]: "Uploaded",
  [DocumentStatus.Valid]: "Valid",
  [DocumentStatus.ExpiringSoon]: "Expiring soon",
  [DocumentStatus.Expired]: "Expired",
  [DocumentStatus.Rejected]: "Rejected",
  [DocumentStatus.NotApplicable]: "Not applicable",
};

export function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  );
}
