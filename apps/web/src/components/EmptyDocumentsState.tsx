export function EmptyDocumentsState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 px-6 py-16 text-center dark:border-slate-700">
      <span className="text-4xl" aria-hidden="true">
        📄
      </span>
      <h3 className="mt-4 text-base font-semibold">No documents yet</h3>
      <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
        This vehicle's document checklist hasn't loaded yet — try refreshing the page.
      </p>
    </div>
  );
}
