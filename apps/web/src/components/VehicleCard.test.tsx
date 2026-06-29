import { FuelType, Transmission, VehicleStatus, type Vehicle } from "@passhub/shared";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { VehicleCard } from "@/components/VehicleCard";

function makeVehicle(overrides: Partial<Vehicle> = {}): Vehicle {
  return {
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
    ...overrides,
  };
}

describe("VehicleCard", () => {
  it("renders plate, brand, model and year", () => {
    render(
      <MemoryRouter>
        <VehicleCard vehicle={makeVehicle()} />
      </MemoryRouter>,
    );

    expect(screen.getByText("ABCD12")).toBeInTheDocument();
    expect(screen.getByText("Toyota Yaris · 2022")).toBeInTheDocument();
  });

  it("links to the vehicle detail page", () => {
    render(
      <MemoryRouter>
        <VehicleCard vehicle={makeVehicle()} />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link")).toHaveAttribute(
      "href",
      "/app/drive/vehicles/11111111-1111-1111-1111-111111111111",
    );
  });

  it("calls onToggleFavorite when the favorite badge is clicked", () => {
    const onToggleFavorite = vi.fn();
    render(
      <MemoryRouter>
        <VehicleCard vehicle={makeVehicle({ favorite: false })} onToggleFavorite={onToggleFavorite} />
      </MemoryRouter>,
    );

    screen.getByRole("button", { name: "Mark as favorite" }).click();
    expect(onToggleFavorite).toHaveBeenCalledOnce();
  });
});
