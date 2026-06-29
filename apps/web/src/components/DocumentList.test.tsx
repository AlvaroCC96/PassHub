import {
  DocumentStatus,
  DocumentType,
  DocumentVisibility,
  type VehicleDocument,
} from "@passhub/shared";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { DocumentList } from "@/components/DocumentList";

vi.mock("@/lib/api-client", () => ({
  apiFetch: vi.fn(() => Promise.resolve(null)),
  ApiRequestError: class extends Error {},
}));

function makeDocument(overrides: Partial<VehicleDocument> = {}): VehicleDocument {
  return {
    id: "22222222-2222-2222-2222-222222222222",
    document_type: DocumentType.Padron,
    display_name: "Padrón",
    status: DocumentStatus.Missing,
    visibility: DocumentVisibility.Private,
    is_required: true,
    issue_date: null,
    expiration_date: null,
    current_version_id: null,
    ...overrides,
  };
}

function renderList(documents: VehicleDocument[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DocumentList vehicleId="11111111-1111-1111-1111-111111111111" documents={documents} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("DocumentList", () => {
  it("renders the empty state when there are no documents", () => {
    renderList([]);

    expect(screen.getByText("No documents yet")).toBeInTheDocument();
  });

  it("renders a card per document once loaded", () => {
    renderList([makeDocument(), makeDocument({ id: "33333333-3333-3333-3333-333333333333", document_type: DocumentType.Soap, display_name: "SOAP" })]);

    expect(screen.getByText("Padrón")).toBeInTheDocument();
    expect(screen.getByText("SOAP")).toBeInTheDocument();
  });

  it("marks required documents", () => {
    renderList([makeDocument({ is_required: true })]);

    expect(screen.getByText("Required")).toBeInTheDocument();
  });
});
