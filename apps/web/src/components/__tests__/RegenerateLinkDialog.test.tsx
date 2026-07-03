import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RegenerateLinkDialog } from "@/components/RegenerateLinkDialog";

describe("RegenerateLinkDialog", () => {
  it("renders nothing when closed", () => {
    render(<RegenerateLinkDialog isOpen={false} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.queryByText(/regenerar/i)).not.toBeInTheDocument();
  });

  it("renders warning message when open", () => {
    render(<RegenerateLinkDialog isOpen onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByText("Regenerar enlace público")).toBeInTheDocument();
    expect(screen.getByText(/dejará de funcionar/)).toBeInTheDocument();
  });

  it("calls onConfirm when Regenerar is clicked", () => {
    const onConfirm = vi.fn();
    render(<RegenerateLinkDialog isOpen onConfirm={onConfirm} onCancel={vi.fn()} />);
    screen.getByRole("button", { name: "Regenerar" }).click();
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it("calls onCancel when Cancelar is clicked", () => {
    const onCancel = vi.fn();
    render(<RegenerateLinkDialog isOpen onConfirm={vi.fn()} onCancel={onCancel} />);
    screen.getByRole("button", { name: "Cancelar" }).click();
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("disables buttons when isLoading", () => {
    render(<RegenerateLinkDialog isOpen isLoading onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Regenerando…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancelar" })).toBeDisabled();
  });
});
