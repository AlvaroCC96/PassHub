export interface SpinnerProps {
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASSES: Record<NonNullable<SpinnerProps["size"]>, string> = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-[3px]",
};

export function Spinner({ size = "md" }: SpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={`animate-spin rounded-full border-slate-300 border-t-brand-600 dark:border-slate-700 dark:border-t-brand-400 ${SIZE_CLASSES[size]}`}
    />
  );
}
