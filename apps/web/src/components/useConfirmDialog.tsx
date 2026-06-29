import { useCallback, useRef, useState } from "react";
import { ConfirmDialog } from "@/components/ConfirmDialog";

interface ConfirmOptions {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "default" | "danger";
}

/** SweetAlert-style confirmation: `await confirm({...})` resolves `true`/
 * `false` once the user picks an option, instead of the blocking native
 * `window.confirm`. Render the returned `dialog` node anywhere in the
 * component's JSX (it's `null` until `confirm()` is called). One hook
 * instance per component — concurrent calls would share the same dialog. */
export function useConfirmDialog() {
  const [options, setOptions] = useState<ConfirmOptions | null>(null);
  const resolveRef = useRef<((value: boolean) => void) | null>(null);

  const confirm = useCallback((opts: ConfirmOptions) => {
    setOptions(opts);
    return new Promise<boolean>((resolve) => {
      resolveRef.current = resolve;
    });
  }, []);

  const handleConfirm = () => {
    resolveRef.current?.(true);
    setOptions(null);
  };

  const handleCancel = () => {
    resolveRef.current?.(false);
    setOptions(null);
  };

  const dialog = options && (
    <ConfirmDialog
      isOpen
      title={options.title}
      message={options.message}
      confirmLabel={options.confirmLabel}
      cancelLabel={options.cancelLabel}
      variant={options.variant}
      onConfirm={handleConfirm}
      onCancel={handleCancel}
    />
  );

  return { confirm, dialog };
}
