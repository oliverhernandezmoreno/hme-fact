import { describe, expect, it } from "vitest";

import { calculateDteTotals } from "@/modules/dte/schemas/dte.schema";

describe("calculateDteTotals", () => {
  it("calculates net, exempt, iva and total", () => {
    const totals = calculateDteTotals([
      { description: "Servicio", quantity: 2, unit_price: 1000, tax_exempt: false },
      { description: "Exento", quantity: 1, unit_price: 500, tax_exempt: true }
    ]);

    expect(totals.net).toBe(2000);
    expect(totals.exempt).toBe(500);
    expect(totals.iva).toBe(380);
    expect(totals.total).toBe(2880);
  });
});
