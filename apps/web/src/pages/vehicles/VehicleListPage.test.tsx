import { FuelType, Transmission, VehicleStatus, type Vehicle } from "@passhub/shared";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AuthContext, type AuthContextValue } from "@/auth/AuthContext";
import { VehicleListPage } from "@/pages/vehicles/VehicleListPage";

const AUTHENTICATED_AUTH: AuthContextValue = {
  status: "authenticated",
  user: null,
  loginWithGoogle: async () => {},
  restoreSession: async () => true,
  logout: async () => {},
};

const sampleVehicle: Vehicle = {
  id: "11111111-1111-1111-1111-111111111111",
  plate: "ABCD12",
  brand: "Toyota",
  model: "Yaris",
  year: 2022,
  color: "Red",
  vin: null,
  engine_number: null,
  nickname: null,
  fuel_type: FuelType.Unknown,
  transmission: Transmission.Unknown,
  favorite: false,
  status: VehicleStatus.Active,
};

vi.mock("@/lib/api-client", () => ({
  apiFetch: vi.fn(() => Promise.resolve([])),
  ApiRequestError: class extends Error {},
}));

function renderListPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={AUTHENTICATED_AUTH}>
        <MemoryRouter>
          <VehicleListPage />
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  );
}

describe("VehicleListPage", () => {
  it("renders the empty state when there are no vehicles", async () => {
    renderListPage();

    expect(await screen.findByText("No vehicles yet")).toBeInTheDocument();
  });

  it("renders a card per vehicle once loaded", async () => {
    const { apiFetch } = await import("@/lib/api-client");
    vi.mocked(apiFetch).mockResolvedValueOnce([sampleVehicle]);

    renderListPage();

    expect(await screen.findByText("ABCD12")).toBeInTheDocument();
    expect(screen.getByText("Add Vehicle")).toBeInTheDocument();
  });
});
