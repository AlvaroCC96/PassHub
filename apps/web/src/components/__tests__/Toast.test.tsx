import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Toast } from "@/components/Toast";

describe("Toast", () => {
  it("renders nothing when toast is null", () => {
    render(<Toast toast={null} />);
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("renders message when toast is present", () => {
    render(<Toast toast={{ id: 1, message: "Link copiado correctamente.", type: "success" }} />);
    expect(screen.getByText("Link copiado correctamente.")).toBeInTheDocument();
  });

  it("shows dismiss button when onDismiss is provided", () => {
    const onDismiss = vi.fn();
    render(
      <Toast
        toast={{ id: 1, message: "Mensaje", type: "success" }}
        onDismiss={onDismiss}
      />,
    );
    screen.getByRole("button", { name: "Cerrar" }).click();
    expect(onDismiss).toHaveBeenCalledOnce();
  });
});
