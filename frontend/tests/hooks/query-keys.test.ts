import { describe, expect, it } from "vitest";

import { queryKeys } from "@/services/query-keys";

describe("query keys", () => {
  it("builds stable DTE detail key", () => {
    expect(queryKeys.dte("abc")).toEqual(["dte", "abc"]);
  });
});
