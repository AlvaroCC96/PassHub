import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DrivePassPage } from "@/pages/DrivePassPage";

describe("DrivePassPage", () => {
  it("renders the placeholder title, subtitle, and message", () => {
    render(<DrivePassPage />);

    expect(screen.getByRole("heading", { name: "DrivePass" })).toBeInTheDocument();
    expect(screen.getByText("Digital Vehicle Identity")).toBeInTheDocument();
    expect(screen.getByText("This module is ready to be implemented in Sprint 2.")).toBeInTheDocument();
  });

  it("renders all five placeholder module cards", () => {
    render(<DrivePassPage />);

    for (const title of ["Vehicles", "Documents", "NFC Access", "AI Extraction", "Expiration Alerts"]) {
      expect(screen.getByText(title)).toBeInTheDocument();
    }
  });
});
