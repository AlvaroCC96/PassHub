import { DocumentType } from "@passhub/shared";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocumentUploadModal } from "@/components/DocumentUploadModal";

vi.mock("@/lib/api-client", () => ({
  apiFetch: vi.fn(() => Promise.resolve(null)),
  ApiRequestError: class extends Error {},
}));

function renderModal(isOpen: boolean) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <DocumentUploadModal
        vehicleId="11111111-1111-1111-1111-111111111111"
        displayName="Padrón"
        isOpen={isOpen}
        onClose={() => {}}
        documentType={DocumentType.Padron}
      />
    </QueryClientProvider>,
  );
}

describe("DocumentUploadModal", () => {
  it("renders nothing when closed", () => {
    renderModal(false);

    expect(screen.queryByText(/Upload Padrón/)).not.toBeInTheDocument();
  });

  it("shows the upload form with title and disabled submit until a file is chosen", () => {
    renderModal(true);

    expect(screen.getByText("Upload Padrón")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Upload" })).toBeDisabled();
  });
});
