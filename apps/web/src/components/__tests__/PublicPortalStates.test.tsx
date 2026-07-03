import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BlockedPortalCard } from "@/components/BlockedPortalCard";
import { EmptyDocumentsCard } from "@/components/EmptyDocumentsCard";
import { InvalidPortalCard } from "@/components/InvalidPortalCard";
import { PublicDocumentCard } from "@/components/PublicDocumentCard";
import { PublicVehicleCard } from "@/components/PublicVehicleCard";
import { SessionExpiredDialog } from "@/components/SessionExpiredDialog";
import type { PublicDocument, PublicVehicleInfo } from "@/public-access/types";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const mockVehicle: PublicVehicleInfo = {
  vehicle: "Chevrolet Groove Premier",
  year: 2022,
  requires_pin: true,
  enabled: true,
  locked: false,
};

const mockDocument: PublicDocument = {
  id: "doc-1",
  type: "SOAP",
  status: "VALID",
};

// ── InvalidPortalCard ─────────────────────────────────────────────────────────

describe("InvalidPortalCard", () => {
  it("renders 404 title and description", () => {
    render(<InvalidPortalCard />);
    expect(screen.getByText("Este acceso ya no existe")).toBeInTheDocument();
    expect(screen.getByText(/enlace puede haber sido/i)).toBeInTheDocument();
  });

  it("calls onBack when back button is clicked", () => {
    const onBack = vi.fn();
    render(<InvalidPortalCard onBack={onBack} />);
    screen.getByRole("button", { name: /volver/i }).click();
    expect(onBack).toHaveBeenCalledOnce();
  });
});

// ── BlockedPortalCard ─────────────────────────────────────────────────────────

describe("BlockedPortalCard", () => {
  it("renders blocked title and generic message without lockedAt", () => {
    render(<BlockedPortalCard />);
    expect(
      screen.getByText("Acceso bloqueado temporalmente"),
    ).toBeInTheDocument();
    expect(screen.getByText(/Demasiados intentos/)).toBeInTheDocument();
  });

  it("shows retry button when countdown expires (no lockedAt)", () => {
    const onRetry = vi.fn();
    render(<BlockedPortalCard onRetry={onRetry} />);
    const btn = screen.getByRole("button", { name: /intentar/i });
    btn.click();
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("shows countdown when lockedAt is recent", () => {
    render(<BlockedPortalCard lockedAt={Date.now()} />);
    // countdown display should be present (MM:SS format)
    expect(screen.getByRole("status", { hidden: true })?.textContent ?? "").toMatch(
      /\d+:\d{2}/,
    );
  });
});

// ── EmptyDocumentsCard ────────────────────────────────────────────────────────

describe("EmptyDocumentsCard", () => {
  it("renders the no-documents message", () => {
    render(<EmptyDocumentsCard />);
    expect(
      screen.getByText("No existen documentos disponibles."),
    ).toBeInTheDocument();
  });
});

// ── PublicVehicleCard ─────────────────────────────────────────────────────────

describe("PublicVehicleCard", () => {
  it("renders vehicle name and year", () => {
    render(<PublicVehicleCard info={mockVehicle} />);
    expect(screen.getByText("Chevrolet Groove Premier")).toBeInTheDocument();
    expect(screen.getByText("2022")).toBeInTheDocument();
  });

  it("shows verified status when not locked", () => {
    render(<PublicVehicleCard info={mockVehicle} />);
    expect(screen.getByText(/🔓 Verificado/)).toBeInTheDocument();
  });

  it("shows blocked status when locked", () => {
    render(<PublicVehicleCard info={{ ...mockVehicle, locked: true }} />);
    expect(screen.getByText(/🔒 Bloqueado/)).toBeInTheDocument();
  });
});

// ── PublicDocumentCard ────────────────────────────────────────────────────────

describe("PublicDocumentCard", () => {
  it("renders document type label and status", () => {
    render(<PublicDocumentCard document={mockDocument} onView={vi.fn()} />);
    expect(screen.getByText("SOAP")).toBeInTheDocument();
    expect(screen.getByText("Vigente")).toBeInTheDocument();
  });

  it("calls onView with document id when Ver is clicked", () => {
    const onView = vi.fn();
    render(<PublicDocumentCard document={mockDocument} onView={onView} />);
    screen.getByRole("button", { name: "Ver" }).click();
    expect(onView).toHaveBeenCalledWith("doc-1");
  });

  it("shows loading state when isLoading", () => {
    render(
      <PublicDocumentCard document={mockDocument} onView={vi.fn()} isLoading />,
    );
    expect(screen.getByText("Abriendo…")).toBeInTheDocument();
  });

  it("renders expiring_soon status with yellow label", () => {
    render(
      <PublicDocumentCard
        document={{ ...mockDocument, status: "EXPIRING_SOON" }}
        onView={vi.fn()}
      />,
    );
    expect(screen.getByText("Por vencer")).toBeInTheDocument();
  });
});

// ── SessionExpiredDialog ──────────────────────────────────────────────────────

describe("SessionExpiredDialog", () => {
  it("renders nothing when closed", () => {
    render(<SessionExpiredDialog isOpen={false} onDismiss={vi.fn()} />);
    expect(screen.queryByText("Sesión expirada")).not.toBeInTheDocument();
  });

  it("renders dialog content when open", () => {
    render(<SessionExpiredDialog isOpen onDismiss={vi.fn()} />);
    expect(screen.getByText("Sesión expirada")).toBeInTheDocument();
  });

  it("calls onDismiss when Ingresar PIN is clicked", () => {
    const onDismiss = vi.fn();
    render(<SessionExpiredDialog isOpen onDismiss={onDismiss} />);
    screen.getByRole("button", { name: "Ingresar PIN" }).click();
    expect(onDismiss).toHaveBeenCalledOnce();
  });
});
