const PLACEHOLDER_CARDS = ["Vehicles", "Documents", "NFC Access", "AI Extraction", "Expiration Alerts"];

export function DrivePassPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">DrivePass</h1>
      <p className="mt-1 text-slate-600 dark:text-slate-400">Digital Vehicle Identity</p>
      <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
        This module is ready to be implemented in Sprint 2.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {PLACEHOLDER_CARDS.map((title) => (
          <div
            key={title}
            className="rounded-xl border border-dashed border-slate-300 p-5 text-slate-400 dark:border-slate-700 dark:text-slate-500"
          >
            <h3 className="text-base font-medium">{title}</h3>
            <p className="mt-1 text-sm">Not implemented yet.</p>
          </div>
        ))}
      </div>
    </div>
  );
}
