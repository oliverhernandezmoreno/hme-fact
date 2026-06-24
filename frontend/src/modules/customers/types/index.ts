import type { UUID } from "@/types/api";

export type Customer = {
  id: UUID;
  company_id: UUID;
  rut: string;
  legal_name: string;
  giro?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  comuna?: string | null;
  city?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type CustomerPayload = {
  rut: string;
  legal_name: string;
  giro?: string;
  email?: string;
  phone?: string;
  address?: string;
  comuna?: string;
  city?: string;
};
