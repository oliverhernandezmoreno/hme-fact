import { isMockMode } from "@/lib/env";
import { MOCK_COMPANIES, MOCK_TOKEN, MOCK_USER } from "@/lib/mocks";
import { apiClient } from "@/services/api-client";

import type { LoginFormValues } from "../schemas/auth.schema";

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

const delay = (ms = 600) => new Promise((r) => setTimeout(r, ms));

export async function login(payload: LoginFormValues): Promise<TokenResponse & { user?: typeof MOCK_USER; company?: typeof MOCK_COMPANIES[0] }> {
  if (isMockMode) {
    await delay();
    if (payload.email === "admin@ohmefact.cl" || payload.email !== "") {
      return { access_token: MOCK_TOKEN, token_type: "bearer", user: MOCK_USER, company: MOCK_COMPANIES[0] };
    }
    throw { status: 401, message: "Credenciales inválidas" };
  }
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

