import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AuthContext, type AuthContextValue } from "@/auth/AuthContext";
import { DrivePassPage } from "@/pages/DrivePassPage";

const UNAUTHENTICATED_AUTH: AuthContextValue = {
  status: "unauthenticated",
  user: null,
  loginWithGoogle: async () => {},
  restoreSession: async () => false,
  logout: async () => {},
};

function renderDrivePassPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={UNAUTHENTICATED_AUTH}>
        <MemoryRouter>
          <DrivePassPage />
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  );
}

describe("DrivePassPage", () => {
  it("renders the title and subtitle", () => {
    renderDrivePassPage();

    expect(screen.getByRole("heading", { name: "DrivePass" })).toBeInTheDocument();
    expect(screen.getByText("Digital Vehicle Identity")).toBeInTheDocument();
  });

  it("renders the empty state when there are no vehicles", () => {
    renderDrivePassPage();

    expect(screen.getByText("No vehicles yet")).toBeInTheDocument();
  });

  it("renders the remaining coming-soon module cards", () => {
    renderDrivePassPage();

    for (const title of ["Documents", "NFC Access", "AI Extraction", "Expiration Alerts"]) {
      expect(screen.getByText(title)).toBeInTheDocument();
    }
  });
});
