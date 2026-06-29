import { OverallDocumentStatus, type DocumentStatusSummary } from "@passhub/shared";

const OVERALL_STYLES: Record<OverallDocumentStatus, string> = {
  [OverallDocumentStatus.Complete]: "text-emerald-600 dark:text-emerald-400",
  [OverallDocumentStatus.Incomplete]: "text-amber-600 dark:text-amber-400",
  [OverallDocumentStatus.Warning]: "text-amber-600 dark:text-amber-400",
  [OverallDocumentStatus.Expired]: "text-red-600 dark:text-red-400",
};

const OVERALL_LABELS: Record<OverallDocumentStatus, string> = {
  [OverallDocumentStatus.Complete]: "Complete",
  [OverallDocumentStatus.Incomplete]: "Incomplete",
  [OverallDocumentStatus.Warning]: "Needs attention",
  [OverallDocumentStatus.Expired]: "Expired documents",
};

export function DocumentSummaryCard({ summary }: { summary: DocumentStatusSummary }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Document status</h2>
        <span className={`text-sm font-semibold ${OVERALL_STYLES[summary.overall_status]}`}>
          {OVERALL_LABELS[summary.overall_status]}
        </span>
      </div>

      <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className="h-full rounded-full bg-brand-600 transition-all"
          style={{ width: `${summary.completion_percentage}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
        {summary.completion_percentage}% complete
      </p>

      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Required</dt>
          <dd className="font-medium">{summary.required_documents}</dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Uploaded</dt>
          <dd className="font-medium">{summary.uploaded_documents}</dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Missing</dt>
          <dd className="font-medium">{summary.missing_required_documents}</dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Expiring/Expired</dt>
          <dd className="font-medium">
            {summary.expiring_soon_documents + summary.expired_documents}
          </dd>
        </div>
      </dl>
    </div>
  );
}
