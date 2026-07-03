import { useCallback, useEffect, useRef, useState } from "react";

export interface Toast {
  id: number;
  message: string;
  type?: "success" | "error" | "info";
}

let _nextId = 0;

export function useToast(durationMs = 3000) {
  const [toast, setToast] = useState<Toast | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const show = useCallback(
    (message: string, type: Toast["type"] = "success") => {
      if (timerRef.current) clearTimeout(timerRef.current);
      setToast({ id: ++_nextId, message, type });
      timerRef.current = setTimeout(() => setToast(null), durationMs);
    },
    [durationMs],
  );

  const dismiss = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setToast(null);
  }, []);

  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current); }, []);

  return { toast, show, dismiss };
}
