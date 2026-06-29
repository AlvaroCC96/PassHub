import { ModuleCode, ModuleStatus, type PlatformModule } from "@passhub/shared";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { ModuleCard } from "@/components/ModuleCard";

function makeModule(overrides: Partial<PlatformModule> = {}): PlatformModule {
  return {
    code: ModuleCode.DrivePass,
    name: "DrivePass",
    description: "Digital vehicle identity and document vault.",
    icon: "car",
    route_path: "/app/drive",
    status: ModuleStatus.Active,
    is_core: false,
    sort_order: 1,
    is_enabled: false,
    ...overrides,
  };
}

function renderCard(module: PlatformModule, onEnable?: () => void) {
  return render(
    <MemoryRouter>
      <ModuleCard module={module} onEnable={onEnable} />
    </MemoryRouter>,
  );
}

describe("ModuleCard", () => {
  it("renders an enabled module as a link to its route", () => {
    renderCard(makeModule({ is_enabled: true }));

    const link = screen.getByRole("link", { name: /drivepass/i });
    expect(link).toHaveAttribute("href", "/app/drive");
  });

  it("renders a coming-soon module as locked, with no enable affordance", () => {
    renderCard(makeModule({ status: ModuleStatus.ComingSoon, is_enabled: false }));

    expect(screen.getByText("Coming soon")).toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("renders an active, not-yet-enabled module as an enable button", () => {
    const onEnable = vi.fn();
    renderCard(makeModule({ is_enabled: false }), onEnable);

    const button = screen.getByRole("button", { name: /drivepass/i });
    button.click();
    expect(onEnable).toHaveBeenCalledOnce();
  });
});
