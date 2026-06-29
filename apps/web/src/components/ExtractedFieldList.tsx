import type { ExtractedFieldValue } from "@passhub/shared";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";

function humanize(fieldName: string): string {
  return fieldName
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

interface ExtractedFieldListProps {
  fields: Record<string, ExtractedFieldValue>;
  /** Editable values, keyed by field name — when provided, every field
   * renders as a text input seeded with this value instead of plain text,
   * so the user can correct a value they don't trust before confirming
   * (e.g. the AI mixed up "vin" and "chassis_number"). */
  editedValues?: Record<string, string>;
  onFieldChange?: (fieldName: string, value: string) => void;
}

export function ExtractedFieldList({ fields, editedValues, onFieldChange }: ExtractedFieldListProps) {
  const entries = Object.entries(fields);
  if (entries.length === 0) return null;

  const editable = editedValues !== undefined && onFieldChange !== undefined;

  return (
    <dl className="divide-y divide-slate-100 dark:divide-slate-800">
      {entries.map(([name, field]) => (
        <div key={name} className="flex items-center justify-between gap-3 py-2 text-sm">
          <div className="flex-1">
            <dt className="text-slate-500 dark:text-slate-400">{humanize(name)}</dt>
            {editable ? (
              <input
                type="text"
                value={editedValues[name] ?? ""}
                onChange={(event) => onFieldChange(name, event.target.value)}
                placeholder="—"
                className="mt-0.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-sm font-medium dark:border-slate-700 dark:bg-slate-800"
              />
            ) : (
              <dd className="font-medium">{field.value ?? "—"}</dd>
            )}
          </div>
          <ConfidenceBadge confidence={field.confidence} />
        </div>
      ))}
    </dl>
  );
}
