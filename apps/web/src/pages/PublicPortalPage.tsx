import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { BlockedPortalCard } from "@/components/BlockedPortalCard";
import { EmptyDocumentsCard } from "@/components/EmptyDocumentsCard";
import { InvalidPortalCard } from "@/components/InvalidPortalCard";
import { PinPad } from "@/components/PinPad";
import { PublicDocumentCard } from "@/components/PublicDocumentCard";
import { PublicVehicleCard } from "@/components/PublicVehicleCard";
import { SessionExpiredDialog } from "@/components/SessionExpiredDialog";
import { ApiRequestError } from "@/lib/api-client";
import { clearPublicSessionToken, storePublicSessionToken } from "@/public-access/session";
import { useDownloadDocument } from "@/public-access/hooks/useDownloadDocument";
import { useLogoutPublicSession } from "@/public-access/hooks/useLogoutPublicSession";
import { usePublicDocuments } from "@/public-access/hooks/usePublicDocuments";
import { usePublicVehicle } from "@/public-access/hooks/usePublicVehicle";
import { useVerifyPin } from "@/public-access/hooks/useVerifyPin";
import type { PortalView } from "@/public-access/types";

export function PublicPortalPage() {
  const { publicToken } = useParams<{ publicToken: string }>();
  const navigate = useNavigate();

  const [view, setView] = useState<PortalView>("loading");
  const [pin, setPin] = useState("");
  const [pinError, setPinError] = useState<string | null>(null);
  const [lockedAt, setLockedAt] = useState<number | undefined>();
  const [showSessionExpired, setShowSessionExpired] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const { vehicle, isLoading: vehicleLoading, isNotFound, error: vehicleError } =
    usePublicVehicle(publicToken);
  const verifyPin = useVerifyPin(publicToken ?? "");
  const { documents, isLoading: docsLoading, error: docsError } =
    usePublicDocuments(publicToken, view === "documents");
  const downloadDocument = useDownloadDocument(publicToken ?? "");
  const logout = useLogoutPublicSession(publicToken ?? "");

  // Transition from loading → first view
  useEffect(() => {
    if (vehicleLoading) return;
    if (isNotFound || (vehicleError instanceof ApiRequestError && vehicleError.status === 404)) {
      setView("invalid");
      return;
    }
    if (!vehicle) return;
    if (vehicle.locked) {
      setView("blocked");
      return;
    }
    if (!vehicle.requires_pin) {
      setView("documents");
      return;
    }
    setView("pin");
  }, [vehicleLoading, vehicle, isNotFound, vehicleError]);

  // Detect 401 on documents → session expired
  useEffect(() => {
    if (
      docsError instanceof ApiRequestError &&
      docsError.status === 401 &&
      view === "documents"
    ) {
      setShowSessionExpired(true);
    }
  }, [docsError, view]);

  const handlePinSubmit = (submittedPin: string) => {
    if (!publicToken) return;
    setPinError(null);
    verifyPin.mutate(submittedPin, {
      onSuccess: (data) => {
        storePublicSessionToken(data.session_token);
        setPin("");
        setView("documents");
      },
      onError: (err) => {
        setPin("");
        if (err instanceof ApiRequestError) {
          if (err.status === 423) {
            setLockedAt(Date.now());
            setView("blocked");
          } else if (err.status === 400) {
            // Extract remaining attempts from message if possible
            const match = err.message.match(/\d+/);
            const attemptsLeft = match
              ? `Intentos restantes: ${match[0]}.`
              : "Vuelve a intentarlo.";
            setPinError(`PIN incorrecto. ${attemptsLeft}`);
          } else {
            setPinError("Error al verificar el PIN.");
          }
        } else {
          setPinError("Error de conexión. Inténtalo de nuevo.");
        }
      },
    });
  };

  const handleSessionExpiredDismiss = () => {
    setShowSessionExpired(false);
    setPin("");
    setPinError(null);
    setView("pin");
  };

  const handleLogout = () => {
    logout.mutate(undefined, {
      onSettled: () => {
        clearPublicSessionToken();
        setPin("");
        setPinError(null);
        setView("pin");
      },
    });
  };

  const handleViewDocument = (documentId: string) => {
    setDownloadingId(documentId);
    downloadDocument.mutate(documentId, {
      onSettled: () => setDownloadingId(null),
      onError: (err) => {
        if (err instanceof ApiRequestError && err.status === 401) {
          setShowSessionExpired(true);
        }
      },
    });
  };

  // ── Loading ──
  if (view === "loading") {
    return (
      <PortalShell>
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 animate-pulse rounded-full bg-white/20" />
          <div className="h-4 w-40 animate-pulse rounded-full bg-white/20" />
        </div>
      </PortalShell>
    );
  }

  // ── Invalid / 404 ──
  if (view === "invalid") {
    return (
      <PortalShell>
        <PortalCard>
          <InvalidPortalCard onBack={() => navigate(-1)} />
        </PortalCard>
      </PortalShell>
    );
  }

  // ── Blocked ──
  if (view === "blocked") {
    return (
      <PortalShell>
        <PortalCard>
          <BlockedPortalCard
            lockedAt={lockedAt}
            onRetry={() => {
              setLockedAt(undefined);
              setView("pin");
            }}
          />
        </PortalCard>
      </PortalShell>
    );
  }

  // ── PIN entry ──
  if (view === "pin") {
    return (
      <PortalShell>
        <div className="flex w-full max-w-sm flex-col gap-6">
          {/* Header card */}
          <div className="rounded-2xl bg-white/10 p-6 text-center backdrop-blur-sm">
            <span className="text-6xl" aria-hidden="true">🚗</span>
            {vehicle && (
              <>
                <h1 className="mt-3 text-xl font-bold text-white">
                  {vehicle.vehicle}
                </h1>
                <p className="text-white/70">{vehicle.year}</p>
              </>
            )}
            <div className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white">
              🔒 Protegido
            </div>
          </div>

          {/* PIN card */}
          <div className="rounded-2xl bg-white p-8 shadow-2xl dark:bg-slate-900">
            <p className="mb-6 text-center text-sm text-slate-500 dark:text-slate-400">
              Ingresa tu PIN para acceder a la documentación autorizada.
            </p>
            <PinPad
              value={pin}
              onChange={setPin}
              onSubmit={handlePinSubmit}
              disabled={verifyPin.isPending}
              error={pinError}
            />

            {verifyPin.isPending && (
              <div className="mt-6 flex flex-col items-center gap-2 text-center">
                <span className="text-3xl" aria-hidden>🔓</span>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Validando acceso…
                </p>
              </div>
            )}
          </div>
        </div>
      </PortalShell>
    );
  }

  // ── Documents ──
  return (
    <PortalShell>
      <div className="flex w-full max-w-sm flex-col gap-4">
        {/* Vehicle wallet card */}
        {vehicle && <PublicVehicleCard info={vehicle} />}

        {/* Documents section */}
        <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
          <h2 className="mb-3 text-base font-semibold text-slate-900 dark:text-white">
            Documentos
          </h2>

          {docsLoading && (
            <div className="flex flex-col gap-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-16 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"
                />
              ))}
            </div>
          )}

          {!docsLoading && documents.length === 0 && <EmptyDocumentsCard />}

          {!docsLoading && documents.length > 0 && (
            <div className="flex flex-col gap-3">
              {documents.map((doc) => (
                <PublicDocumentCard
                  key={doc.id}
                  document={doc}
                  onView={handleViewDocument}
                  isLoading={downloadingId === doc.id}
                />
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur-sm">
          <p className="text-xs text-white/60">
            🛡️ Protegido por PassHub
          </p>
          <p className="mt-0.5 text-xs text-white/50">
            Sesión expira automáticamente por seguridad.
          </p>
          <button
            type="button"
            onClick={handleLogout}
            disabled={logout.isPending}
            className="mt-3 rounded-lg bg-white/10 px-4 py-2 text-xs font-medium text-white/80 transition-colors hover:bg-white/20 disabled:opacity-50"
          >
            {logout.isPending ? "Cerrando…" : "Cerrar sesión"}
          </button>
        </div>
      </div>

      <SessionExpiredDialog
        isOpen={showSessionExpired}
        onDismiss={handleSessionExpiredDismiss}
      />
    </PortalShell>
  );
}

// ── Layout shell ──────────────────────────────────────────────────────────────

function PortalShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-brand-900 to-slate-900 px-4 py-10">
      {/* PassHub logo */}
      <div className="mb-6 text-center">
        <p className="text-xs font-semibold uppercase tracking-widest text-white/40">
          PassHub
        </p>
      </div>

      {children}
    </div>
  );
}

function PortalCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
      {children}
    </div>
  );
}
