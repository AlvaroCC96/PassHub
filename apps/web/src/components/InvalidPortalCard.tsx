interface InvalidPortalCardProps {
  onBack?: () => void;
}

export function InvalidPortalCard({ onBack }: InvalidPortalCardProps) {
  return (
    <div
      role="main"
      className="flex flex-col items-center gap-6 py-8 text-center"
    >
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-slate-100 text-4xl dark:bg-slate-800">
        🔗
      </div>

      <div>
        <p className="text-5xl font-black text-slate-200 dark:text-slate-700">
          404
        </p>
        <h2 className="mt-2 text-xl font-bold text-slate-900 dark:text-white">
          Este acceso ya no existe
        </h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          El enlace puede haber sido desactivado o regenerado.
          <br />
          Solicita un nuevo enlace al propietario del vehículo.
        </p>
      </div>

      {onBack && (
        <button
          type="button"
          onClick={onBack}
          className="rounded-xl bg-slate-100 px-6 py-3 text-sm font-semibold text-slate-900 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
        >
          ← Volver
        </button>
      )}
    </div>
  );
}
