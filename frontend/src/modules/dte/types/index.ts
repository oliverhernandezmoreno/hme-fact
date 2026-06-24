import type { DTEStatus, UUID } from "@/types/api";

export type DTEType = 33 | 34 | 39 | 41 | 56 | 61;

export type DTE = {
  id: UUID;
  company_id: UUID;
  customer_id: UUID;
  dte_type: DTEType;
  folio: number;
  status: DTEStatus;
  issue_date: string;
  due_date?: string | null;
  net_amount: string;
  exempt_amount: string;
  tax_amount: string;
  total_amount: string;
  sii_track_id?: string | null;
  sent_at?: string | null;
  accepted_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type DTEStatusResponse = {
  dte_id: UUID;
  status: DTEStatus;
  provider: string;
  external_track_id?: string | null;
  provider_status?: string | null;
  detail?: string | null;
};

export type DTEItemDraft = {
  product_id?: UUID;
  description: string;
  quantity: number;
  unit_price: number;
  tax_exempt: boolean;
};

export type DTEIssuePayload = {
  customer_id: UUID;
  dte_type: DTEType;
  issue_date: string;
  due_date?: string;
  items: DTEItemDraft[];
  reference?: {
    dte_type?: number;
    folio?: number;
    date?: string;
    code?: number;
    reason?: string;
  };
};
