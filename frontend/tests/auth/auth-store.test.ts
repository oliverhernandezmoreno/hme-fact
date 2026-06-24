import { describe, expect, it } from "vitest";

import { useAuthStore } from "@/stores/auth-store";

describe("auth store", () => {
  it("stores and clears JWT session", () => {
    useAuthStore.getState().setSession("token", { email: "demo@example.com" });
    expect(useAuthStore.getState().accessToken).toBe("token");

    useAuthStore.getState().clearSession();
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
