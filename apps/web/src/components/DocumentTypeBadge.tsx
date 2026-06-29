import { DOCUMENT_TYPE_LABELS, type DocumentType } from "@passhub/shared";

export function DocumentTypeBadge({ type }: { type: DocumentType }) {
  return (
    <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
      {DOCUMENT_TYPE_LABELS[type]}
    </span>
  );
}
