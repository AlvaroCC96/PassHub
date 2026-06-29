import { Button } from "@passhub/ui";
import { useConfirmDialog } from "@/components/useConfirmDialog";
import { useConfirmExtraction } from "@/intelligence/useConfirmExtraction";

interface ConfirmExtractionButtonProps {
  extractionId: string;
  /** Field overrides the user edited — only the ones that differ from the
   * AI's own value, so unedited fields stay attributed to "ai". */
  fieldOverrides?: Record<string, string | null>;
}

export function ConfirmExtractionButton({ extractionId, fieldOverrides }: ConfirmExtractionButtonProps) {
  const confirmExtraction = useConfirmExtraction(extractionId);
  const { confirm, dialog } = useConfirmDialog();

  const handleClick = async () => {
    const ok = await confirm({
      title: "Confirmar extracción",
      message:
        "Esto actualizará el vehículo y/o el documento con los datos detectados. ¿Deseas continuar?",
      confirmLabel: "Confirmar y actualizar",
    });
    if (!ok) return;
    confirmExtraction.mutate({ fields: fieldOverrides });
  };

  // `isSuccess` hides/disables the button immediately on the client —
  // waiting for the query invalidation to refetch and re-render before
  // disabling it left a window where a second click re-submitted a
  // confirm that the server had already applied, surfacing as a 409.
  const disabled = confirmExtraction.isPending || confirmExtraction.isSuccess;

  return (
    <>
      <Button type="button" onClick={handleClick} disabled={disabled}>
        {confirmExtraction.isPending
          ? "Confirmando…"
          : confirmExtraction.isSuccess
            ? "Confirmado"
            : "Confirmar y actualizar"}
      </Button>
      {dialog}
    </>
  );
}
