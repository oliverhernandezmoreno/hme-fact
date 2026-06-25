import { isMockMode } from "@/lib/env";
import { MOCK_DTES } from "@/lib/mocks";
import { apiClient } from "@/services/api-client";
import type { ListParams } from "@/types/api";

import type { DTE, DTEIssuePayload, DTEStatusResponse } from "../types";

const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms));

export async function listDTE(params: ListParams = {}): Promise<DTE[]> {
  if (isMockMode) { await delay(); return MOCK_DTES; }
  const response = await apiClient.get<DTE[]>("/dte", { params });
  return response.data;
}

export async function createDTE(payload: DTEIssuePayload): Promise<DTE> {
  if (isMockMode) {
    await delay(800);
    const newDTE: DTE = {
      id: crypto.randomUUID(),
      company_id: "11111111-1111-1111-1111-111111111111",
      customer_id: payload.customer_id,
      dte_type: payload.dte_type,
      folio: Math.floor(Math.random() * 9000) + 1000,
      issue_date: payload.issue_date,
      total_amount: String(Math.round(payload.items.reduce((s, i) => s + i.quantity * i.unit_price, 0) * 1.19)),
      net_amount: String(Math.round(payload.items.reduce((s, i) => s + i.quantity * i.unit_price, 0))),
      exempt_amount: "0",
      tax_amount: String(Math.round(payload.items.reduce((s, i) => s + i.quantity * i.unit_price, 0) * 0.19)),
      status: "draft",
      sii_track_id: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    return newDTE;
  }
  const response = await apiClient.post<DTE>("/dte", payload);
  return response.data;
}

export async function generateDteXml(id: string): Promise<string> {
  if (isMockMode) { await delay(); return `<DTE id="${id}">mock xml</DTE>`; }
  const response = await apiClient.post<string>(`/dte/${id}/generate-xml`, undefined, { responseType: "text" });
  return response.data;
}

export async function sendDTE(id: string): Promise<DTEStatusResponse> {
  if (isMockMode) { await delay(600); return { dte_id: id, status: "sent", provider: "mock", detail: "Enviado al SII (mock)" }; }
  const response = await apiClient.post<DTEStatusResponse>(`/dte/${id}/send`);
  return response.data;
}

export async function getDTEStatus(id: string): Promise<DTEStatusResponse> {
  if (isMockMode) { await delay(); const dte = MOCK_DTES.find(d => d.id === id); return { dte_id: id, status: dte?.status ?? "draft", provider: "mock" }; }
  const response = await apiClient.get<DTEStatusResponse>(`/dte/${id}/status`);
  return response.data;
}

