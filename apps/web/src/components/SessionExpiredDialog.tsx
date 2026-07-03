interface SessionExpiredDialogProps {
  isOpen: boolean;
  onDismiss: () => void;
}

export function SessionExpiredDialog({
  isOpen,
  onDismiss,
}: SessionExpiredDialogProps) {
  if (!isOpen) return null;

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="session-expired-title"
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center"
    >
      <div className="w-full max-w-sm animate-slide-up rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <div className="text-center">
          <span className="text-4xl" aria-hidden="true">
            ⏱️
          </span>
          <h2
            id="session-expired-title"
            className="mt-3 text-lg font-bold text-slate-900 dark:text-white"
          >
            Sesión expirada
          </h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            La sesión expiró. Ingresa nuevamente tu PIN para continuar.
          </p>
        </div>

        <button
          type="button"
          onClick={onDismiss}
          className="mt-6 w-full rounded-xl bg-brand-600 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand-700"
        >
          Ingresar PIN
        </button>
      </div>
    </div>
  );
}
