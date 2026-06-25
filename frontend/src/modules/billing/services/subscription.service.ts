/**
 * Servicio de suscripciones — soporta modo mock.
 */
import { isMockMode } from "@/lib/env";
import { MOCK_BILLING_EVENTS, MOCK_PLANS, MOCK_SUBSCRIPTION, MOCK_USAGE } from "@/lib/mocks";
import { apiClient } from "@/services/api-client";

const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms));

export type Plan = {
  code: string;
  name: string;
  price: number;
  currency: string;
  billing_cycle: string;
  features: Record<string, number | boolean | string>;
  sort_order: number;
};

export type Subscription = {
  id: string;
  plan_code: string;
  plan_name: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
};

export type UsageSummary = {
  plan_code: string;
  plan_name: string;
  period_month: number;
  period_year: number;
  dtes_used: number;
  dtes_limit: number;
  api_calls_used: number;
  api_rate_limit_per_min: number;
  users_used: number;
  users_limit: number;
  storage_used_bytes: number;
  storage_limit_mb: number;
  api_access: boolean;
};

export type BillingEvent = {
  id: string;
  event_type: string;
  amount: number;
  currency: string;
  description: string;
  created_at: string;
};

export async function getPlans(): Promise<Plan[]> {
  if (isMockMode) { await delay(); return MOCK_PLANS as Plan[]; }
  const r = await apiClient.get<Plan[]>("/subscriptions/plans");
  return r.data;
}

export async function getMySubscription(): Promise<Subscription | null> {
  if (isMockMode) { await delay(); return MOCK_SUBSCRIPTION as Subscription; }
  try {
    const r = await apiClient.get<Subscription>("/subscriptions/my");
    return r.data;
  } catch {
    return null;
  }
}

export async function getUsage(): Promise<UsageSummary | null> {
  if (isMockMode) { await delay(); return MOCK_USAGE as UsageSummary; }
  try {
    const r = await apiClient.get<UsageSummary>("/subscriptions/usage");
    return r.data;
  } catch {
    return null;
  }
}

export async function getBillingEvents(): Promise<BillingEvent[]> {
  if (isMockMode) { await delay(); return MOCK_BILLING_EVENTS as BillingEvent[]; }
  const r = await apiClient.get<BillingEvent[]>("/subscriptions/billing-events");
  return r.data;
}

export async function activatePlan(plan_code: string, trial = false): Promise<void> {
  if (isMockMode) { await delay(800); return; }
  await apiClient.post("/subscriptions/activate", { plan_code, trial });
}

export async function cancelSubscription(): Promise<void> {
  if (isMockMode) { await delay(800); return; }
  await apiClient.post("/subscriptions/cancel");
}
