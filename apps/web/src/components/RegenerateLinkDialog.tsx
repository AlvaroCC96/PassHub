interface RegenerateLinkDialogProps {
  isOpen: boolean;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function RegenerateLinkDialog({
  isOpen,
  isLoading,
  onConfirm,
  onCancel,
}: RegenerateLinkDialogProps) {
  if (!isOpen) return null;

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="regen-dialog-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    >
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-2xl dark:bg-amber-900/30">
          ⚠️
        </div>

        <h2
          id="regen-dialog-title"
          className="mt-4 text-lg font-bold text-slate-900 dark:text-white"
        >
          Regenerar enlace público
        </h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Al regenerar el enlace, cualquier tarjeta NFC o enlace compartido
          anteriormente <strong>dejará de funcionar</strong>. Las sesiones
          activas serán cerradas inmediatamente.
        </p>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isLoading}
            className="flex-1 rounded-xl bg-amber-500 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-amber-600 disabled:opacity-50"
          >
            {isLoading ? "Regenerando…" : "Regenerar"}
          </button>
        </div>
      </div>
    </div>
  );
}
