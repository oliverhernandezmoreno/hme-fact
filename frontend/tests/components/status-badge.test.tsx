import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusBadge } from "@/components/feedback/status-badge";

describe("StatusBadge", () => {
  it("renders accepted state label", () => {
    render(<StatusBadge status="accepted" />);
    expect(screen.getByText("Aceptado")).toBeInTheDocument();
  });

  it("renders contingency state label", () => {
    render(<StatusBadge status="contingency" />);
    expect(screen.getByText("Contingencia")).toBeInTheDocument();
  });
});
