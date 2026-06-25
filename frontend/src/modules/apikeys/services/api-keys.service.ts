/**
 * Servicio de API Keys — soporta modo mock.
 */
import { isMockMode } from "@/lib/env";
import { MOCK_API_KEYS } from "@/lib/mocks";
import { apiClient } from "@/services/api-client";

const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms));

export type APIKey = {
  id: string;
  name: string;
  prefix: string;
  scopes: string[];
  is_active: boolean;
  expires_at: string | null;
  last_used_at: string | null;
  created_at: string;
};

export type GeneratedAPIKey = {
  id: string;
  name: string;
  prefix: string;
  raw_key: string;
  warning: string;
};

export async function listAPIKeys(): Promise<APIKey[]> {
  if (isMockMode) { await delay(); return MOCK_API_KEYS as APIKey[]; }
  const r = await apiClient.get<APIKey[]>("/api-keys");
  return r.data;
}

export async function createAPIKey(name: string, scopes?: string[], expires_in_days?: number): Promise<GeneratedAPIKey> {
  if (isMockMode) {
    await delay(800);
    return {
      id: crypto.randomUUID(),
      name,
      prefix: `ohm_${Math.random().toString(36).slice(2, 8)}`,
      raw_key: `ohm_${Math.random().toString(36).slice(2, 8)}.${crypto.randomUUID().replace(/-/g, "")}`,
      warning: "Guarda esta clave de forma segura — no se mostrará de nuevo.",
    };
  }
  const r = await apiClient.post<GeneratedAPIKey>("/api-keys", { name, scopes, expires_in_days });
  return r.data;
}

export async function revokeAPIKey(id: string): Promise<void> {
  if (isMockMode) { await delay(600); return; }
  await apiClient.delete(`/api-keys/${id}`);
}

export async function rotateAPIKey(id: string): Promise<GeneratedAPIKey> {
  if (isMockMode) {
    await delay(800);
    return {
      id: crypto.randomUUID(),
      name: "Key rotada",
      prefix: `ohm_${Math.random().toString(36).slice(2, 8)}`,
      raw_key: `ohm_${Math.random().toString(36).slice(2, 8)}.${crypto.randomUUID().replace(/-/g, "")}`,
      warning: "Guarda esta clave de forma segura — no se mostrará de nuevo.",
    };
  }
  const r = await apiClient.post<GeneratedAPIKey>(`/api-keys/${id}/rotate`);
  return r.data;
}
