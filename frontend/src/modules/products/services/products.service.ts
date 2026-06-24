import { apiClient } from "@/services/api-client";
import type { ListParams } from "@/types/api";

import type { Product, ProductPayload } from "../types";

export async function listProducts(params: ListParams = {}): Promise<Product[]> {
  const response = await apiClient.get<Product[]>("/products", { params });
  return response.data;
}

export async function createProduct(payload: ProductPayload): Promise<Product> {
  const response = await apiClient.post<Product>("/products", payload);
  return response.data;
}

export async function updateProduct(id: string, payload: Partial<ProductPayload>): Promise<Product> {
  const response = await apiClient.patch<Product>(`/products/${id}`, payload);
  return response.data;
}
