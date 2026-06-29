import { type DocumentExtraction, ExtractionStatus } from "@passhub/shared";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AIExtractionResultPanel } from "@/components/AIExtractionResultPanel";

vi.mock("@/lib/api-client", () => ({
  apiFetch: vi.fn(() => Promise.resolve(null)),
  ApiRequestError: class extends Error {},
}));

beforeEach(() => {
  vi.clearAllMocks();
});

function makeExtraction(overrides: Partial<DocumentExtraction> = {}): DocumentExtraction {
  return {
    id: "22222222-2222-2222-2222-222222222222",
    document_id: "11111111-1111-1111-1111-111111111111",
    document_version_id: "33333333-3333-3333-3333-333333333333",
    vehicle_id: "44444444-4444-4444-4444-444444444444",
    status: ExtractionStatus.Completed,
    provider: "openai",
    model: "gpt-4o-mini",
    prompt_version: "drivepass-document-extraction-v1",
    extracted_data: {
      document_type: "PADRON",
      confidence_score: 0.95,
      fields: { plate: { value: "ABCD12", confidence: 0.98 } },
      warnings: [],
      requires_review: false,
    },
    confidence_score: 0.95,
    warnings: [],
    requires_review: false,
    input_tokens: 100,
    output_tokens: 50,
    total_tokens: 150,
    estimated_cost_usd: 0.001,
    processing_time_ms: 250,
    error_message: null,
    confirmed_at: null,
    rejected_at: null,
    ...overrides,
  };
}

function renderPanel(extraction: DocumentExtraction) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AIExtractionResultPanel extraction={extraction} />
    </QueryClientProvider>,
  );
}

describe("AIExtractionResultPanel", () => {
  it("renders detected fields as editable inputs", () => {
    renderPanel(makeExtraction());
    expect(screen.getByText("Plate")).toBeInTheDocument();
    expect(screen.getByDisplayValue("ABCD12")).toBeInTheDocument();
  });

  it("sends an edited field as an override after confirming the dialog", async () => {
    const { apiFetch } = await import("@/lib/api-client");
    renderPanel(makeExtraction());

    fireEvent.change(screen.getByDisplayValue("ABCD12"), { target: { value: "WXYZ34" } });
    fireEvent.click(screen.getByRole("button", { name: "Confirmar y actualizar" }));
    // Opening the dialog renders a second button with the same label —
    // the dialog's own confirm action.
    const dialogButtons = screen.getAllByRole("button", { name: "Confirmar y actualizar" });
    fireEvent.click(dialogButtons.at(-1)!);

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/intelligence/extractions/22222222-2222-2222-2222-222222222222/confirm",
        { method: "POST", body: JSON.stringify({ fields: { plate: "WXYZ34" } }) },
      ),
    );
  });

  it("renders warnings when present", () => {
    renderPanel(
      makeExtraction({
        requires_review: true,
        warnings: ["Extracted plate 'ABCD12' does not match this vehicle's plate 'ZZZZ99'."],
        extracted_data: {
          document_type: "PADRON",
          confidence_score: 0.6,
          fields: { plate: { value: "ABCD12", confidence: 0.9 } },
          warnings: ["Extracted plate 'ABCD12' does not match this vehicle's plate 'ZZZZ99'."],
          requires_review: true,
        },
      }),
    );

    expect(screen.getByText("Requiere revisión")).toBeInTheDocument();
    expect(screen.getByText(/does not match/)).toBeInTheDocument();
  });

  it("asks for confirmation before confirming the extraction", async () => {
    const { apiFetch } = await import("@/lib/api-client");
    renderPanel(makeExtraction());

    fireEvent.click(screen.getByRole("button", { name: "Confirmar y actualizar" }));

    expect(screen.getByText("Confirmar extracción")).toBeInTheDocument();
    expect(apiFetch).not.toHaveBeenCalled();

    const dialogButtons = screen.getAllByRole("button", { name: "Confirmar y actualizar" });
    fireEvent.click(dialogButtons.at(-1)!);

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/intelligence/extractions/22222222-2222-2222-2222-222222222222/confirm",
        { method: "POST" },
      ),
    );
  });

  it("disables the confirm button after a successful confirmation", async () => {
    renderPanel(makeExtraction());

    fireEvent.click(screen.getByRole("button", { name: "Confirmar y actualizar" }));
    const dialogButtons = screen.getAllByRole("button", { name: "Confirmar y actualizar" });
    fireEvent.click(dialogButtons.at(-1)!);

    expect(await screen.findByRole("button", { name: "Confirmado" })).toBeDisabled();
  });

  it("re-enables confirm for a new extraction after reprocessing", async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const first = makeExtraction();
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <AIExtractionResultPanel extraction={first} />
      </QueryClientProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Confirmar y actualizar" }));
    const dialogButtons = screen.getAllByRole("button", { name: "Confirmar y actualizar" });
    fireEvent.click(dialogButtons.at(-1)!);
    expect(await screen.findByRole("button", { name: "Confirmado" })).toBeDisabled();

    // Simulate reprocessing: a brand-new extraction (different id) for the
    // same document replaces the one just confirmed.
    const second = makeExtraction({ id: "55555555-5555-5555-5555-555555555555" });
    rerender(
      <QueryClientProvider client={queryClient}>
        <AIExtractionResultPanel extraction={second} />
      </QueryClientProvider>,
    );

    expect(
      screen.getByRole("button", { name: "Confirmar y actualizar" }),
    ).not.toBeDisabled();
  });
});
