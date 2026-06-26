export type UUID = string;

export type ApiError = {
  status: number;
  message: string;
  details?: unknown;
  retryable?: boolean;
};

export type ListParams = {
  offset?: number;
  limit?: number;
  search?: string;
};

export type DTEStatus =
  | "draft"
  | "generated"
  | "queued"
  | "sent"
  | "accepted"
  | "partially_accepted"
  | "rejected"
  | "error"
  | "contingency";

export type PaginatedState = {
  pageIndex: number;
  pageSize: number;
};
