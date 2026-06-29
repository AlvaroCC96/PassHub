import { Spinner } from "@passhub/ui";

export function LoadingModal({ isOpen, message }: { isOpen: boolean; message: string }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex w-full max-w-sm flex-col items-center gap-4 rounded-xl bg-white p-8 text-center shadow-lg dark:bg-slate-900">
        <Spinner size="lg" />
        <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{message}</p>
      </div>
    </div>
  );
}
