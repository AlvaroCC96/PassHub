import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VehicleForm } from "@/components/VehicleForm";

describe("VehicleForm", () => {
  it("renders every requested field", () => {
    render(
      <VehicleForm onSubmit={vi.fn()} isSubmitting={false} submitLabel="Add vehicle" />,
    );

    for (const label of [
      "Plate",
      "Brand",
      "Model",
      "Year",
      "Color",
      "VIN",
      "Engine number",
      "Nickname",
      "Fuel type",
      "Transmission",
    ]) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
  });

  it("blocks submission and shows inline errors when required fields are missing", () => {
    const onSubmit = vi.fn();
    render(<VehicleForm onSubmit={onSubmit} isSubmitting={false} submitLabel="Add vehicle" />);

    fireEvent.click(screen.getByRole("button", { name: "Add vehicle" }));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText("Plate is required")).toBeInTheDocument();
    expect(screen.getByText("Brand is required")).toBeInTheDocument();
    expect(screen.getByText("Model is required")).toBeInTheDocument();
  });

  it("submits normalized values once required fields are filled", () => {
    const onSubmit = vi.fn();
    render(<VehicleForm onSubmit={onSubmit} isSubmitting={false} submitLabel="Add vehicle" />);

    // `Field` pairs a <span> with its input via layout, not `<label for>`,
    // so the inputs are queried by role/order rather than accessible name.
    const [plateInput, brandInput, modelInput] = screen.getAllByRole("textbox");
    fireEvent.change(plateInput!, { target: { value: "abcd12" } });
    fireEvent.change(brandInput!, { target: { value: "Toyota" } });
    fireEvent.change(modelInput!, { target: { value: "Yaris" } });

    fireEvent.click(screen.getByRole("button", { name: "Add vehicle" }));

    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onSubmit.mock.calls[0]?.[0]).toMatchObject({ plate: "abcd12", brand: "Toyota", model: "Yaris" });
  });
});
