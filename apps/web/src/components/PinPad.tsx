import { useCallback, useEffect } from "react";

const PIN_LENGTH = 4;
const DIGITS = [
  ["1", "2", "3"],
  ["4", "5", "6"],
  ["7", "8", "9"],
  ["", "0", "⌫"],
];

interface PinPadProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (pin: string) => void;
  disabled?: boolean;
  error?: string | null;
}

export function PinPad({ value, onChange, onSubmit, disabled, error }: PinPadProps) {
  const handleKey = useCallback(
    (key: string) => {
      if (disabled) return;
      if (key === "⌫") {
        onChange(value.slice(0, -1));
      } else if (key !== "" && value.length < PIN_LENGTH) {
        const next = value + key;
        onChange(next);
        if (next.length === PIN_LENGTH) {
          setTimeout(() => onSubmit(next), 120);
        }
      }
    },
    [value, onChange, onSubmit, disabled],
  );

  // Keyboard support
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Backspace") handleKey("⌫");
      else if (e.key === "Enter" && value.length === PIN_LENGTH) onSubmit(value);
      else if (/^\d$/.test(e.key)) handleKey(e.key);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handleKey, value, onSubmit]);

  return (
    <div className="flex flex-col items-center gap-6">
      {/* PIN dots */}
      <div className="flex gap-4" aria-label={`PIN: ${value.length} de ${PIN_LENGTH} dígitos`}>
        {Array.from({ length: PIN_LENGTH }).map((_, i) => (
          <div
            key={i}
            className={`h-4 w-4 rounded-full border-2 transition-all duration-150 ${
              i < value.length
                ? "scale-110 border-brand-600 bg-brand-600"
                : "border-slate-400 bg-transparent dark:border-slate-500"
            } ${error ? "border-red-500 bg-red-500" : ""}`}
          />
        ))}
      </div>

      {/* Error message */}
      {error && (
        <p
          role="alert"
          className="text-center text-sm font-medium text-red-500 dark:text-red-400"
        >
          {error}
        </p>
      )}

      {/* Keypad */}
      <div className="grid grid-cols-3 gap-3">
        {DIGITS.flat().map((key, i) => {
          if (key === "") return <div key={i} />;

          const isBackspace = key === "⌫";
          return (
            <button
              key={i}
              type="button"
              onClick={() => handleKey(key)}
              disabled={disabled || (key === "" ? true : false)}
              aria-label={isBackspace ? "Borrar" : key}
              className={`
                flex h-16 w-16 items-center justify-center rounded-full text-xl font-semibold
                transition-all duration-100 active:scale-95 disabled:opacity-40
                ${
                  isBackspace
                    ? "text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                    : "bg-slate-100 text-slate-900 hover:bg-slate-200 active:bg-slate-300 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700 dark:active:bg-slate-600"
                }
              `}
            >
              {key}
            </button>
          );
        })}
      </div>
    </div>
  );
}
