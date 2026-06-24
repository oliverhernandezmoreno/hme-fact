import type { UUID } from "@/types/api";

export type Product = {
  id: UUID;
  company_id: UUID;
  sku?: string | null;
  name: string;
  description?: string | null;
  unit: string;
  unit_price: string;
  tax_exempt: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ProductPayload = {
  sku?: string;
  name: string;
  description?: string;
  unit: string;
  unit_price: number;
  tax_exempt: boolean;
};
