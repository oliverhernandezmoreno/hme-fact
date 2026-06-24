import { apiClient } from "@/services/api-client";

import type { LoginFormValues } from "../schemas/auth.schema";

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

export async function login(payload: LoginFormValues): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.set("username", payload.email);
  form.set("password", payload.password);

  const response = await apiClient.post<TokenResponse>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  });
  return response.data;
}

export async function refreshToken(): Promise<TokenResponse | null> {
  return null;
}
