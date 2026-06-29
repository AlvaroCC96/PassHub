import { type DocumentExtraction, ExtractionStatus } from "@passhub/shared";
import { useEffect, useState } from "react";
import { AIExtractionStatus } from "@/components/AIExtractionStatus";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { ConfirmExtractionButton } from "@/components/ConfirmExtractionButton";
import { ExtractedFieldList } from "@/components/ExtractedFieldList";
import { ExtractionWarningList } from "@/components/ExtractionWarningList";
import { RejectExtractionButton } from "@/components/RejectExtractionButton";

function initialValues(extraction: DocumentExtraction): Record<string, string> {
  if (!extraction.extracted_data) return {};
  return Object.fromEntries(
    Object.entries(extraction.extracted_data.fields).map(([name, field]) => [
      name,
      field.value ?? "",
    ]),
  );
}

export function AIExtractionResultPanel({ extraction }: { extraction: DocumentExtraction }) {
  const [editedValues, setEditedValues] = useState<Record<string, string>>(() =>
    initialValues(extraction),
  );

  // Reset edits whenever a different extraction (e.g. after reprocessing) is shown.
  useEffect(() => {
    setEditedValues(initialValues(extraction));
  }, [extraction]);

  const fieldOverrides: Record<string, string | null> = {};
  if (extraction.extracted_data) {
    for (const [name, field] of Object.entries(extraction.extracted_data.fields)) {
      const original = field.value ?? "";
      const edited = editedValues[name] ?? "";
      if (edited !== original) {
        fieldOverrides[name] = edited === "" ? null : edited;
      }
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold">Datos detectados</h3>
        <div className="flex items-center gap-2">
          <AIExtractionStatus status={extraction.status} />
          {extraction.status === ExtractionStatus.Completed && (
            <ConfidenceBadge confidence={extraction.confidence_score} />
          )}
        </div>
      </div>

      {extraction.status === ExtractionStatus.Failed && (
        <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
          {extraction.error_message ?? "El análisis no pudo completarse."}
        </p>
      )}

      {extraction.extracted_data && (
        <>
          <div className="mt-3">
            <ExtractedFieldList
              fields={extraction.extracted_data.fields}
              editedValues={extraction.status === ExtractionStatus.Completed ? editedValues : undefined}
              onFieldChange={
                extraction.status === ExtractionStatus.Completed
                  ? (name, value) => setEditedValues((prev) => ({ ...prev, [name]: value }))
                  : undefined
              }
            />
          </div>
          {extraction.status === ExtractionStatus.Completed && (
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              ¿No confías en un valor? Edítalo antes de confirmar.
            </p>
          )}
          <div className="mt-3">
            <ExtractionWarningList warnings={extraction.warnings} />
          </div>
        </>
      )}

      {extraction.status === ExtractionStatus.Completed && (
        // `key={extraction.id}` forces a fresh mount per extraction —
        // without it, reprocessing reuses the same component instance and
        // `useMutation`'s `isSuccess` from the *previous* extraction's
        // confirm/reject stays stuck `true`, leaving the new extraction's
        // button permanently disabled.
        <div key={extraction.id} className="mt-4 flex flex-wrap gap-3">
          <ConfirmExtractionButton extractionId={extraction.id} fieldOverrides={fieldOverrides} />
          <RejectExtractionButton extractionId={extraction.id} />
        </div>
      )}
    </div>
  );
}
