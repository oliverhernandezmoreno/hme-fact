import type { UUID } from "@/types/api";

export type Company = {
  id: UUID;
  rut: string;
  legal_name: string;
  fantasy_name?: string | null;
  giro?: string | null;
  address?: string | null;
  comuna?: string | null;
  city?: string | null;
  sii_resolution_number?: number | null;
  sii_resolution_date?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type CompanyPayload = {
  rut: string;
  legal_name: string;
  fantasy_name?: string;
  giro?: string;
  address?: string;
  comuna?: string;
  city?: string;
  sii_resolution_number?: number | null;
  sii_resolution_date?: string | null;
};
