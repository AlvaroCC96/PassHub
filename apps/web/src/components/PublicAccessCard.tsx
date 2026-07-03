import { useState } from "react";
import { Link } from "react-router-dom";
import { ApiRequestError } from "@/lib/api-client";
import { usePublicAccess } from "@/public-access/hooks/usePublicAccess";
import { useRegenerateLink } from "@/public-access/hooks/useRegenerateLink";
import { useSetEnabled } from "@/public-access/hooks/useSetEnabled";
import { useSetupPublicAccess } from "@/public-access/hooks/useSetupPublicAccess";
import { ChangePinModal } from "./ChangePinModal";
import { RegenerateLinkDialog } from "./RegenerateLinkDialog";
import { Toast } from "./Toast";
import { useToast } from "@/hooks/useToast";

interface PublicAccessCardProps {
  vehicleId: string;
}

const PIN_RE = /^\d{4}$/;

export function PublicAccessCard({ vehicleId }: PublicAccessCardProps) {
  const { config, isLoading, isNotFound } = usePublicAccess(vehicleId);
  const setEnabled = useSetEnabled(vehicleId);
  const regenerate = useRegenerateLink(vehicleId);
  const setup = useSetupPublicAccess(vehicleId);
  const { toast, show: showToast } = useToast();

  const [showChangePinModal, setShowChangePinModal] = useState(false);
  const [showRegenDialog, setShowRegenDialog] = useState(false);

  // Setup state (initial configuration)
  const [setupPin, setSetupPin] = useState("");
  const [setupError, setSetupError] = useState("");

  if (isLoading) {
    return (
      <Card>
        <div className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      </Card>
    );
  }

  // ── Initial setup ──────────────────────────────────────────────────────────
  if (isNotFound || !config) {
    const handleSetup = async (e: React.FormEvent) => {
      e.preventDefault();
      setSetupError("");
      if (!PIN_RE.test(setupPin)) {
        setSetupError("El PIN debe tener exactamente 4 dígitos numéricos.");
        return;
      }
      setup.mutate(setupPin, {
        onError: (err) => {
          setSetupError(
            err instanceof ApiRequestError
              ? err.message
              : "Error al configurar el acceso.",
          );
        },
      });
    };

    return (
      <Card>
        <SectionHeader />
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Configura un acceso público para compartir los documentos del vehículo
          de forma segura mediante un enlace con PIN.
        </p>

        <form onSubmit={handleSetup} className="mt-4 flex flex-col gap-3">
          <div>
            <label
              htmlFor="setup-pin"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Crear PIN de acceso (4 dígitos)
            </label>
            <input
              id="setup-pin"
              type="password"
              inputMode="numeric"
              pattern="\d{4}"
              maxLength={4}
              value={setupPin}
              onChange={(e) =>
                setSetupPin(e.target.value.replace(/\D/g, "").slice(0, 4))
              }
              placeholder="••••"
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-center text-2xl tracking-[0.5em] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>

          {setupError && (
            <p
              role="alert"
              className="rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400"
            >
              {setupError}
            </p>
          )}

          <button
            type="submit"
            disabled={setup.isPending}
            className="rounded-xl bg-brand-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {setup.isPending ? "Configurando…" : "Activar acceso público"}
          </button>
        </form>
      </Card>
    );
  }

  // ── Configured view ────────────────────────────────────────────────────────
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(config.public_url);
      showToast("Link copiado correctamente.");
    } catch {
      showToast("No se pudo copiar el link.", "error");
    }
  };

  const handleToggleEnabled = () => {
    setEnabled.mutate(!config.enabled);
  };

  const handleRegenerate = () => {
    regenerate.mutate(undefined, {
      onSuccess: () => {
        setShowRegenDialog(false);
        showToast("Nuevo link generado correctamente.");
      },
    });
  };

  return (
    <>
      <Card>
        <div className="flex items-start justify-between">
          <SectionHeader />
          <StatusBadge enabled={config.enabled} locked={config.locked} />
        </div>

        {/* Public URL */}
        <div className="mt-3 flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 dark:bg-slate-800">
          <span className="flex-1 truncate font-mono text-xs text-slate-600 dark:text-slate-300">
            {config.public_url}
          </span>
        </div>

        {/* Primary actions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <ActionButton onClick={handleCopy} icon="🔗">
            Copiar link
          </ActionButton>
          <a
            href={config.public_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            🌐 Abrir portal
          </a>
          <ActionButton
            onClick={() => setShowRegenDialog(true)}
            icon="🔄"
            variant="warning"
          >
            Regenerar link
          </ActionButton>
        </div>

        {/* Secondary actions */}
        <div className="mt-2 flex flex-wrap gap-2">
          <ActionButton
            onClick={() => setShowChangePinModal(true)}
            icon="🔑"
            variant="ghost"
          >
            Cambiar PIN
          </ActionButton>
          <ActionButton
            onClick={handleToggleEnabled}
            icon={config.enabled ? "⏸" : "▶"}
            variant="ghost"
            disabled={setEnabled.isPending}
          >
            {config.enabled ? "Desactivar" : "Activar"}
          </ActionButton>
          <Link
            to={`/app/drive/vehicles/${vehicleId}/public-access`}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-brand-600 transition-colors hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-brand-900/20"
          >
            Ver detalles →
          </Link>
        </div>

        {/* Stats */}
        <div className="mt-4 grid grid-cols-2 gap-2 border-t border-slate-100 pt-4 dark:border-slate-800 sm:grid-cols-3">
          <Stat label="Intentos fallidos" value={String(config.failed_attempts)} />
          <Stat
            label="Estado"
            value={config.locked ? "🔒 Bloqueado" : config.enabled ? "🟢 Activo" : "🔴 Inactivo"}
          />
        </div>
      </Card>

      <ChangePinModal
        vehicleId={vehicleId}
        isOpen={showChangePinModal}
        onClose={() => setShowChangePinModal(false)}
        onSuccess={() => showToast("PIN cambiado correctamente.")}
      />

      <RegenerateLinkDialog
        isOpen={showRegenDialog}
        isLoading={regenerate.isPending}
        onConfirm={handleRegenerate}
        onCancel={() => setShowRegenDialog(false)}
      />

      <Toast toast={toast} />
    </>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      {children}
    </div>
  );
}

function SectionHeader() {
  return (
    <div>
      <h2 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
        🌐 Acceso Público
      </h2>
    </div>
  );
}

function StatusBadge({
  enabled,
  locked,
}: {
  enabled: boolean;
  locked: boolean;
}) {
  if (locked) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
        🔒 Bloqueado
      </span>
    );
  }
  return enabled ? (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
      🟢 Activo
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
      🔴 Desactivado
    </span>
  );
}

function ActionButton({
  onClick,
  icon,
  children,
  variant = "default",
  disabled,
}: {
  onClick: () => void;
  icon: string;
  children: React.ReactNode;
  variant?: "default" | "warning" | "ghost";
  disabled?: boolean;
}) {
  const styles = {
    default:
      "border-slate-200 text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800",
    warning:
      "border-amber-200 text-amber-700 hover:bg-amber-50 dark:border-amber-800 dark:text-amber-400 dark:hover:bg-amber-900/20",
    ghost:
      "border-transparent text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800",
  };

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50 ${styles[variant]}`}
    >
      {icon} {children}
    </button>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-0.5 text-sm font-semibold text-slate-900 dark:text-white">
        {value}
      </p>
    </div>
  );
}
