import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AIExtractionButton } from "@/components/AIExtractionButton";

vi.mock("@/lib/api-client", () => ({
  apiFetch: vi.fn(() => Promise.resolve(null)),
  ApiRequestError: class extends Error {},
}));

beforeEach(() => {
  vi.clearAllMocks();
});

function renderButton(hasExtraction: boolean) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AIExtractionButton documentId="11111111-1111-1111-1111-111111111111" hasExtraction={hasExtraction} />
    </QueryClientProvider>,
  );
}

describe("AIExtractionButton", () => {
  it("renders 'Analizar con IA' when there is no prior extraction", () => {
    renderButton(false);
    expect(screen.getByRole("button", { name: "Analizar con IA" })).toBeInTheDocument();
  });

  it("renders 'Reanalizar con IA' when an extraction already exists", () => {
    renderButton(true);
    expect(screen.getByRole("button", { name: "Reanalizar con IA" })).toBeInTheDocument();
  });

  it("shows a loading modal while the extraction request is in flight", async () => {
    const { apiFetch } = await import("@/lib/api-client");
    let resolveRequest: (value: unknown) => void = () => {};
    vi.mocked(apiFetch).mockImplementationOnce(
      () => new Promise((resolve) => { resolveRequest = resolve; }),
    );
    renderButton(false);

    fireEvent.click(screen.getByRole("button", { name: "Analizar con IA" }));

    expect(await screen.findByText("Analizando información con IA…")).toBeInTheDocument();
    resolveRequest(null);
  });
});
