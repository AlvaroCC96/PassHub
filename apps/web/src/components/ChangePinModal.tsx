import { useState } from "react";
import { ApiRequestError } from "@/lib/api-client";
import { useChangePin } from "@/public-access/hooks/useChangePin";

interface ChangePinModalProps {
  vehicleId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const PIN_RE = /^\d{4}$/;

export function ChangePinModal({
  vehicleId,
  isOpen,
  onClose,
  onSuccess,
}: ChangePinModalProps) {
  const [oldPin, setOldPin] = useState("");
  const [newPin, setNewPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [validationError, setValidationError] = useState("");
  const changePin = useChangePin(vehicleId);

  if (!isOpen) return null;

  const handleClose = () => {
    setOldPin("");
    setNewPin("");
    setConfirmPin("");
    setValidationError("");
    changePin.reset();
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError("");

    if (!PIN_RE.test(oldPin)) {
      setValidationError("El PIN actual debe tener exactamente 4 dígitos.");
      return;
    }
    if (!PIN_RE.test(newPin)) {
      setValidationError("El nuevo PIN debe tener exactamente 4 dígitos.");
      return;
    }
    if (newPin !== confirmPin) {
      setValidationError("Los PINs no coinciden.");
      return;
    }

    changePin.mutate(
      { old_pin: oldPin, new_pin: newPin },
      {
        onSuccess: () => {
          handleClose();
          onSuccess();
        },
      },
    );
  };

  const apiError =
    changePin.error instanceof ApiRequestError
      ? changePin.error.message
      : changePin.error
        ? "Error al cambiar el PIN. Inténtalo de nuevo."
        : null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="change-pin-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    >
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <h2
          id="change-pin-title"
          className="text-lg font-bold text-slate-900 dark:text-white"
        >
          Cambiar PIN
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          El PIN protege el acceso al portal público. Solo números, 4 dígitos.
        </p>

        <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-4">
          <PinField
            id="old-pin"
            label="PIN actual"
            value={oldPin}
            onChange={setOldPin}
            autoFocus
          />
          <PinField
            id="new-pin"
            label="Nuevo PIN"
            value={newPin}
            onChange={setNewPin}
          />
          <PinField
            id="confirm-pin"
            label="Confirmar nuevo PIN"
            value={confirmPin}
            onChange={setConfirmPin}
          />

          {(validationError || apiError) && (
            <p
              role="alert"
              className="rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400"
            >
              {validationError || apiError}
            </p>
          )}

          <div className="mt-2 flex gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={changePin.isPending}
              className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={changePin.isPending}
              className="flex-1 rounded-xl bg-brand-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
            >
              {changePin.isPending ? "Cambiando…" : "Cambiar PIN"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function PinField({
  id,
  label,
  value,
  onChange,
  autoFocus,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  autoFocus?: boolean;
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
      >
        {label}
      </label>
      <input
        id={id}
        type="password"
        inputMode="numeric"
        pattern="\d{4}"
        maxLength={4}
        value={value}
        onChange={(e) => onChange(e.target.value.replace(/\D/g, ""))}
        autoFocus={autoFocus}
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-center text-2xl tracking-[0.5em] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        placeholder="••••"
      />
    </div>
  );
}
