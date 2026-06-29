import { useConfirmDialog } from "@/components/useConfirmDialog";
import { useRejectExtraction } from "@/intelligence/useRejectExtraction";

export function RejectExtractionButton({ extractionId }: { extractionId: string }) {
  const rejectExtraction = useRejectExtraction(extractionId);
  const { confirm, dialog } = useConfirmDialog();

  const handleClick = async () => {
    const ok = await confirm({
      title: "Rechazar extracción",
      message: "No se aplicará ningún dato detectado. ¿Deseas rechazar esta extracción?",
      confirmLabel: "Rechazar extracción",
      variant: "danger",
    });
    if (!ok) return;
    rejectExtraction.mutate();
  };

  const disabled = rejectExtraction.isPending || rejectExtraction.isSuccess;

  return (
    <>
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        className="rounded-md bg-red-50 px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20"
      >
        {rejectExtraction.isPending
          ? "Rechazando…"
          : rejectExtraction.isSuccess
            ? "Rechazado"
            : "Rechazar extracción"}
      </button>
      {dialog}
    </>
  );
}
