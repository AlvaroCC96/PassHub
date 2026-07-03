import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PinPad } from "@/components/PinPad";

function makePinPad(
  overrides: Partial<Parameters<typeof PinPad>[0]> = {},
) {
  const props = {
    value: "",
    onChange: vi.fn(),
    onSubmit: vi.fn(),
    ...overrides,
  };
  return { ...props, rendered: render(<PinPad {...props} />) };
}

describe("PinPad", () => {
  it("renders 4 empty dot indicators initially", () => {
    makePinPad();
    const dots = screen
      .getByLabelText("PIN: 0 de 4 dígitos")
      .querySelectorAll("div");
    expect(dots).toHaveLength(4);
  });

  it("fills dots as digits are entered", () => {
    const { rendered, onChange } = makePinPad({ value: "12" });
    const dots = rendered.container.querySelectorAll(
      "[aria-label='PIN: 2 de 4 dígitos'] > div",
    );
    // filled dots have brand color class
    const filled = Array.from(dots).filter((d) =>
      d.className.includes("bg-brand-600"),
    );
    expect(filled).toHaveLength(2);
    expect(onChange).not.toHaveBeenCalled(); // only click triggers onChange
  });

  it("calls onChange when a digit button is pressed", () => {
    const onChange = vi.fn();
    makePinPad({ value: "", onChange });
    fireEvent.click(screen.getByRole("button", { name: "5" }));
    expect(onChange).toHaveBeenCalledWith("5");
  });

  it("calls onChange with truncated value on backspace", () => {
    const onChange = vi.fn();
    makePinPad({ value: "123", onChange });
    fireEvent.click(screen.getByRole("button", { name: "Borrar" }));
    expect(onChange).toHaveBeenCalledWith("12");
  });

  it("shows error message when error prop is set", () => {
    makePinPad({ error: "PIN incorrecto. Intentos restantes: 3." });
    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent("PIN incorrecto. Intentos restantes: 3.");
  });

  it("disables all digit buttons when disabled", () => {
    makePinPad({ disabled: true });
    const buttons = screen
      .getAllByRole("button")
      .filter((b) => b.getAttribute("aria-label") !== "Borrar");
    buttons.forEach((b) => expect(b).toBeDisabled());
  });
});
