import { apiClient } from "@/services/api-client";
import type { ListParams } from "@/types/api";

import type { DTE, DTEIssuePayload, DTEStatusResponse } from "../types";

export async function listDTE(params: ListParams = {}): Promise<DTE[]> {
  const response = await apiClient.get<DTE[]>("/dte", { params });
  return response.data;
}

export async function createDTE(payload: DTEIssuePayload): Promise<DTE> {
  const response = await apiClient.post<DTE>("/dte", payload);
  return response.data;
}

export async function generateDteXml(id: string): Promise<string> {
  const response = await apiClient.post<string>(`/dte/${id}/generate-xml`, undefined, {
    responseType: "text"
  });
  return response.data;
}

export async function sendDTE(id: string): Promise<DTEStatusResponse> {
  const response = await apiClient.post<DTEStatusResponse>(`/dte/${id}/send`);
  return response.data;
}

export async function getDTEStatus(id: string): Promise<DTEStatusResponse> {
  const response = await apiClient.get<DTEStatusResponse>(`/dte/${id}/status`);
  return response.data;
}
