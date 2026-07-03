import type { Toast as ToastType } from "@/hooks/useToast";

interface ToastProps {
  toast: ToastType | null;
  onDismiss?: () => void;
}

const TYPE_STYLES = {
  success: "bg-slate-900 text-white dark:bg-white dark:text-slate-900",
  error: "bg-red-600 text-white",
  info: "bg-brand-600 text-white",
};

export function Toast({ toast, onDismiss }: ToastProps) {
  if (!toast) return null;

  const style = TYPE_STYLES[toast.type ?? "success"];

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-6 left-1/2 z-[60] -translate-x-1/2 animate-fade-in"
    >
      <div
        className={`flex items-center gap-2 rounded-full px-5 py-3 text-sm font-medium shadow-lg ${style}`}
      >
        {toast.type === "success" && <span aria-hidden>✓</span>}
        {toast.message}
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            className="ml-1 opacity-70 hover:opacity-100"
            aria-label="Cerrar"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
