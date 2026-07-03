import { useEffect, useState } from "react";

interface BlockedPortalCardProps {
  /** Epoch ms when the lockout started. Shows a 15-min countdown. */
  lockedAt?: number;
  onRetry?: () => void;
}

const LOCKOUT_SECONDS = 15 * 60;

function useCountdown(startEpochMs: number | undefined) {
  const [remaining, setRemaining] = useState(() => {
    if (!startEpochMs) return 0;
    const elapsed = Math.floor((Date.now() - startEpochMs) / 1000);
    return Math.max(0, LOCKOUT_SECONDS - elapsed);
  });

  useEffect(() => {
    if (!startEpochMs || remaining === 0) return;
    const id = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startEpochMs) / 1000);
      setRemaining(Math.max(0, LOCKOUT_SECONDS - elapsed));
    }, 1000);
    return () => clearInterval(id);
  }, [startEpochMs, remaining]);

  const mins = Math.floor(remaining / 60);
  const secs = remaining % 60;
  return { remaining, display: `${mins}:${String(secs).padStart(2, "0")}` };
}

export function BlockedPortalCard({ lockedAt, onRetry }: BlockedPortalCardProps) {
  const { remaining, display } = useCountdown(lockedAt);

  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-6 py-8 text-center"
    >
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-red-100 text-4xl dark:bg-red-900/30">
        🔒
      </div>

      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">
          Acceso bloqueado temporalmente
        </h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Demasiados intentos fallidos.
        </p>
      </div>

      {lockedAt && remaining > 0 ? (
        <div className="rounded-2xl bg-red-50 px-6 py-4 dark:bg-red-900/20">
          <p className="text-xs text-red-600 dark:text-red-400">
            Intenta nuevamente en
          </p>
          <p
            role="status"
            className="mt-1 font-mono text-3xl font-bold text-red-600 dark:text-red-400"
            aria-live="polite"
            aria-label={`${Math.floor(remaining / 60)} minutos ${remaining % 60} segundos`}
          >
            {display}
          </p>
        </div>
      ) : (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Intenta nuevamente en 15 minutos.
        </p>
      )}

      {(remaining === 0 || !lockedAt) && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-xl bg-brand-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand-700"
        >
          Intentar de nuevo
        </button>
      )}
    </div>
  );
}
