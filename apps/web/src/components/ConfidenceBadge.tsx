type ConfidenceBand = "high" | "medium" | "low";

const STYLES: Record<ConfidenceBand, string> = {
  high: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400",
  low: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
};

const LABELS: Record<ConfidenceBand, string> = {
  high: "Confianza alta",
  medium: "Confianza media",
  low: "Confianza baja",
};

/** Mirrors `confidence_band` in
 * `apps/api/src/modules/intelligence/domain/rules.py` — >=0.90 high,
 * >=0.70 medium, otherwise low (including unknown/`null`). */
function band(confidence: number | null): ConfidenceBand {
  if (confidence === null) return "low";
  if (confidence >= 0.9) return "high";
  if (confidence >= 0.7) return "medium";
  return "low";
}

export function ConfidenceBadge({ confidence }: { confidence: number | null }) {
  const value = band(confidence);
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[value]}`}
    >
      {LABELS[value]}
    </span>
  );
}
