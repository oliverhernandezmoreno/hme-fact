import { apiClient } from "@/services/api-client";
import type { ListParams } from "@/types/api";

import type { Customer, CustomerPayload } from "../types";

export async function listCustomers(params: ListParams = {}): Promise<Customer[]> {
  const response = await apiClient.get<Customer[]>("/customers", { params });
  return response.data;
}

export async function createCustomer(payload: CustomerPayload): Promise<Customer> {
  const response = await apiClient.post<Customer>("/customers", payload);
  return response.data;
}

export async function updateCustomer(id: string, payload: Partial<CustomerPayload>): Promise<Customer> {
  const response = await apiClient.patch<Customer>(`/customers/${id}`, payload);
  return response.data;
}
