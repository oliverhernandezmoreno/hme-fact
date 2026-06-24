import { apiClient } from "@/services/api-client";

import type { Company, CompanyPayload } from "../types";

export async function listCompanies(): Promise<Company[]> {
  const response = await apiClient.get<Company[]>("/companies");
  return response.data;
}

export async function createCompany(payload: CompanyPayload): Promise<Company> {
  const response = await apiClient.post<Company>("/companies", payload);
  return response.data;
}

export async function updateCompany(id: string, payload: Partial<CompanyPayload>): Promise<Company> {
  const response = await apiClient.patch<Company>(`/companies/${id}`, payload);
  return response.data;
}
