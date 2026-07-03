export function EmptyDocumentsCard() {
  return (
    <div className="flex flex-col items-center gap-4 py-10 text-center">
      <span className="text-4xl" aria-hidden="true">
        📂
      </span>
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No existen documentos disponibles.
      </p>
    </div>
  );
}
