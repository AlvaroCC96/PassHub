import { useState } from "react";
import { useParams } from "react-router-dom";
import { BackLink } from "@/components/BackLink";
import { ChangePinModal } from "@/components/ChangePinModal";
import { Loading } from "@/components/Loading";
import { RegenerateLinkDialog } from "@/components/RegenerateLinkDialog";
import { Toast } from "@/components/Toast";
import { useToast } from "@/hooks/useToast";
import { ApiRequestError } from "@/lib/api-client";
import { usePublicAccess } from "@/public-access/hooks/usePublicAccess";
import { useRegenerateLink } from "@/public-access/hooks/useRegenerateLink";
import { useSetEnabled } from "@/public-access/hooks/useSetEnabled";
import { useSetupPublicAccess } from "@/public-access/hooks/useSetupPublicAccess";
import { useVehicle } from "@/vehicles/useVehicle";

const PIN_RE = /^\d{4}$/;

export function PublicAccessPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const { vehicle } = useVehicle(vehicleId);
  const { config, isLoading, isNotFound } = usePublicAccess(vehicleId);
  const setEnabled = useSetEnabled(vehicleId ?? "");
  const regenerate = useRegenerateLink(vehicleId ?? "");
  const setup = useSetupPublicAccess(vehicleId ?? "");
  const { toast, show: showToast } = useToast();

  const [showChangePinModal, setShowChangePinModal] = useState(false);
  const [showRegenDialog, setShowRegenDialog] = useState(false);
  const [setupPin, setSetupPin] = useState("");
  const [setupError, setSetupError] = useState("");

  if (isLoading) return <Loading />;

  const vehicleName = vehicle
    ? `${vehicle.brand} ${vehicle.model} ${vehicle.year}`
    : "Vehículo";

  const handleCopy = async () => {
    if (!config) return;
    try {
      await navigator.clipboard.writeText(config.public_url);
      showToast("Link copiado correctamente.");
    } catch {
      showToast("No se pudo copiar el link.", "error");
    }
  };

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
    <div className="mx-auto max-w-2xl">
      <BackLink
        to={`/app/drive/vehicles/${vehicleId}`}
        label={vehicleName}
      />

      <h1 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
        Acceso Público
      </h1>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        Comparte la documentación del vehículo de forma segura mediante un
        enlace público con PIN.
      </p>

      {/* ── Not configured ── */}
      {(isNotFound || !config) && (
        <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center dark:border-slate-700 dark:bg-slate-800/50">
          <span className="text-5xl" aria-hidden>🔐</span>
          <h2 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">
            Configura el acceso público
          </h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Crea un PIN de 4 dígitos para proteger el acceso al portal.
          </p>

          <form
            onSubmit={handleSetup}
            className="mx-auto mt-6 flex max-w-xs flex-col gap-4"
          >
            <input
              type="password"
              inputMode="numeric"
              pattern="\d{4}"
              maxLength={4}
              value={setupPin}
              onChange={(e) =>
                setSetupPin(e.target.value.replace(/\D/g, "").slice(0, 4))
              }
              placeholder="••••"
              aria-label="PIN de acceso"
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-center text-3xl tracking-[0.5em] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
            />
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
              className="rounded-xl bg-brand-600 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
            >
              {setup.isPending ? "Configurando…" : "Activar acceso público"}
            </button>
          </form>
        </div>
      )}

      {/* ── Configured ── */}
      {config && (
        <div className="mt-6 flex flex-col gap-4">
          {/* Status banner */}
          <div
            className={`flex items-center gap-3 rounded-2xl p-4 ${
              config.locked
                ? "bg-red-50 dark:bg-red-900/20"
                : config.enabled
                  ? "bg-emerald-50 dark:bg-emerald-900/20"
                  : "bg-slate-100 dark:bg-slate-800"
            }`}
          >
            <span className="text-2xl" aria-hidden>
              {config.locked ? "🔒" : config.enabled ? "🟢" : "🔴"}
            </span>
            <div>
              <p className="font-semibold text-slate-900 dark:text-white">
                {config.locked
                  ? "Acceso bloqueado"
                  : config.enabled
                    ? "Acceso activo"
                    : "Acceso desactivado"}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {config.locked
                  ? `${config.failed_attempts} intentos fallidos`
                  : config.enabled
                    ? "El portal público está disponible"
                    : "El portal público no está accesible"}
              </p>
            </div>
          </div>

          {/* URL card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Enlace público
            </p>
            <p className="mt-2 break-all font-mono text-sm text-slate-700 dark:text-slate-300">
              {config.public_url}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <QuickAction onClick={handleCopy}>🔗 Copiar link</QuickAction>
              <a
                href={config.public_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                🌐 Abrir portal
              </a>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <StatCard
              label="Intentos fallidos"
              value={String(config.failed_attempts)}
            />
            <StatCard
              label="Estado del token"
              value={config.status}
            />
          </div>

          {/* Actions */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <p className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">
              Acciones
            </p>
            <div className="flex flex-col gap-2">
              <ActionRow
                icon="🔑"
                title="Cambiar PIN"
                description="Actualiza el PIN de acceso al portal"
                onClick={() => setShowChangePinModal(true)}
              />
              <ActionRow
                icon={config.enabled ? "⏸" : "▶"}
                title={config.enabled ? "Desactivar acceso" : "Activar acceso"}
                description={
                  config.enabled
                    ? "Oculta el portal temporalmente"
                    : "Reactiva el enlace público"
                }
                onClick={() => setEnabled.mutate(!config.enabled)}
                isLoading={setEnabled.isPending}
              />
              <ActionRow
                icon="🔄"
                title="Regenerar enlace"
                description="Invalida el enlace actual y crea uno nuevo"
                onClick={() => setShowRegenDialog(true)}
                variant="warning"
              />
            </div>
          </div>
        </div>
      )}

      <ChangePinModal
        vehicleId={vehicleId ?? ""}
        isOpen={showChangePinModal}
        onClose={() => setShowChangePinModal(false)}
        onSuccess={() => showToast("PIN cambiado correctamente.")}
      />

      <RegenerateLinkDialog
        isOpen={showRegenDialog}
        isLoading={regenerate.isPending}
        onConfirm={() =>
          regenerate.mutate(undefined, {
            onSuccess: () => {
              setShowRegenDialog(false);
              showToast("Nuevo link generado correctamente.");
            },
          })
        }
        onCancel={() => setShowRegenDialog(false)}
      />

      <Toast toast={toast} />
    </div>
  );
}

function QuickAction({
  onClick,
  children,
}: {
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
    >
      {children}
    </button>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-lg font-bold text-slate-900 dark:text-white">
        {value}
      </p>
    </div>
  );
}

function ActionRow({
  icon,
  title,
  description,
  onClick,
  isLoading,
  variant = "default",
}: {
  icon: string;
  title: string;
  description: string;
  onClick: () => void;
  isLoading?: boolean;
  variant?: "default" | "warning";
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isLoading}
      className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left transition-colors disabled:opacity-50 ${
        variant === "warning"
          ? "hover:bg-amber-50 dark:hover:bg-amber-900/10"
          : "hover:bg-slate-50 dark:hover:bg-slate-800"
      }`}
    >
      <span className="text-xl" aria-hidden>
        {icon}
      </span>
      <div className="flex-1">
        <p
          className={`text-sm font-medium ${
            variant === "warning"
              ? "text-amber-700 dark:text-amber-400"
              : "text-slate-900 dark:text-white"
          }`}
        >
          {title}
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {description}
        </p>
      </div>
      {isLoading && (
        <span className="text-xs text-slate-400">Procesando…</span>
      )}
      {!isLoading && (
        <span className="text-slate-400" aria-hidden>›</span>
      )}
    </button>
  );
}
