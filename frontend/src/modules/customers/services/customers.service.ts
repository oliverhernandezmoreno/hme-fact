import { isMockMode } from "@/lib/env";
import { MOCK_CUSTOMERS } from "@/lib/mocks";
import { apiClient } from "@/services/api-client";
import type { ListParams } from "@/types/api";

import type { Customer, CustomerPayload } from "../types";

const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms));

export async function listCustomers(params: ListParams = {}): Promise<Customer[]> {
  if (isMockMode) { await delay(); return MOCK_CUSTOMERS; }
  const response = await apiClient.get<Customer[]>("/customers", { params });
  return response.data;
}

export async function createCustomer(payload: CustomerPayload): Promise<Customer> {
  if (isMockMode) {
    await delay(600);
    return { ...payload, id: crypto.randomUUID(), company_id: "11111111-1111-1111-1111-111111111111", is_active: true };
  }
  const response = await apiClient.post<Customer>("/customers", payload);
  return response.data;
}

export async function updateCustomer(id: string, payload: Partial<CustomerPayload>): Promise<Customer> {
  if (isMockMode) {
    await delay(600);
    const existing = MOCK_CUSTOMERS.find(c => c.id === id) ?? MOCK_CUSTOMERS[0]!;
    return { ...existing, ...payload };
  }
  const response = await apiClient.patch<Customer>(`/customers/${id}`, payload);
  return response.data;
}

