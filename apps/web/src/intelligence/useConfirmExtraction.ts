import type { DocumentExtraction } from "@passhub/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import { extractionQueryKey } from "@/intelligence/useExtraction";

export interface ConfirmExtractionInput {
  /** Only the fields the user actually edited — omitted/empty confirms the
   * AI's own values unchanged. */
  fields?: Record<string, string | null>;
}

export function useConfirmExtraction(extractionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input?: ConfirmExtractionInput) =>
      apiFetch<DocumentExtraction>(`/intelligence/extractions/${extractionId}/confirm`, {
        method: "POST",
        body:
          input?.fields && Object.keys(input.fields).length > 0
            ? JSON.stringify({ fields: input.fields })
            : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionQueryKey(extractionId) });
      // Confirming may have updated the vehicle and/or the document's
      // issue/expiration dates — refresh every DrivePass query rather than
      // tracking exactly which vehicle/document this extraction belonged to.
      queryClient.invalidateQueries({ queryKey: ["drivepass"] });
    },
  });
}
