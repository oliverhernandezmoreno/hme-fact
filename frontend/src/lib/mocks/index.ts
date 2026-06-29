/**
 * Mock data completa para hmEFact.
 * Activar con: NEXT_PUBLIC_USE_MOCKS=true
 */
import type { Company } from "@/modules/companies/types";
import type { Customer } from "@/modules/customers/types";
import type { DTE } from "@/modules/dte/types";
import type { Product } from "@/modules/products/types";

// ── Auth ──────────────────────────────────────────────────────────────────────

export const MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock.token";

export const MOCK_USER = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "admin@ohmefact.cl",
  fullName: "Oliver Hernández M.",
};

// ── Companies ─────────────────────────────────────────────────────────────────

export const MOCK_COMPANIES: Company[] = [
  {
    id: "11111111-1111-1111-1111-111111111111",
    rut: "76.123.456-7",
    legal_name: "TechCorp Chile SpA",
    fantasy_name: "TechCorp",
    giro: "Desarrollo de Software",
    address: "Av. Providencia 1234",
    comuna: "Providencia",
    city: "Santiago",
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "22222222-2222-2222-2222-222222222222",
    rut: "77.987.654-3",
    legal_name: "Retail Demo Ltda.",
    fantasy_name: "RetailDemo",
    giro: "Comercio al por menor",
    address: "Calle Merced 456",
    comuna: "Santiago",
    city: "Santiago",
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
];

export const MOCK_ACTIVE_COMPANY = MOCK_COMPANIES[0]!;

// ── Customers ─────────────────────────────────────────────────────────────────

export const MOCK_CUSTOMERS: Customer[] = [
  {
    id: "c1000001-0000-0000-0000-000000000001",
    company_id: "11111111-1111-1111-1111-111111111111",
    rut: "12.345.678-9",
    legal_name: "Empresa Cliente Alpha SpA",
    email: "alpha@cliente.cl",
    phone: "+56 9 1111 2222",
    address: "Los Conquistadores 1700",
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "c1000001-0000-0000-0000-000000000002",
    company_id: "11111111-1111-1111-1111-111111111111",
    rut: "98.765.432-1",
    legal_name: "Beta Inversiones SA",
    email: "beta@inversiones.cl",
    phone: "+56 9 3333 4444",
    address: "Apoquindo 3000",
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "c1000001-0000-0000-0000-000000000003",
    company_id: "11111111-1111-1111-1111-111111111111",
    rut: "11.222.333-4",
    legal_name: "Gamma Retail Ltda.",
    email: "gamma@retail.cl",
    phone: "+56 9 5555 6666",
    address: "Irarrázaval 2000",
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
];

// ── Products ──────────────────────────────────────────────────────────────────

export const MOCK_PRODUCTS: Product[] = [
  {
    id: "p0000001-0000-0000-0000-000000000001",
    company_id: "11111111-1111-1111-1111-111111111111",
    sku: "SRV-001",
    name: "Consultoría Técnica (hr)",
    description: "Hora de consultoría técnica especializada",
    unit_price: "85000",
    unit: "hr",
    tax_exempt: false,
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "p0000001-0000-0000-0000-000000000002",
    company_id: "11111111-1111-1111-1111-111111111111",
    sku: "LIC-001",
    name: "Licencia Software Anual",
    description: "Licencia de uso anual por usuario",
    unit_price: "250000",
    unit: "un",
    tax_exempt: false,
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "p0000001-0000-0000-0000-000000000003",
    company_id: "11111111-1111-1111-1111-111111111111",
    sku: "CAP-001",
    name: "Capacitación corporativa",
    description: "Módulo de capacitación presencial",
    unit_price: "120000",
    unit: "un",
    tax_exempt: false,
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "p0000001-0000-0000-0000-000000000004",
    company_id: "11111111-1111-1111-1111-111111111111",
    sku: "VIA-001",
    name: "Viáticos y gastos",
    description: "Reembolso de viáticos",
    unit_price: "35000",
    unit: "un",
    tax_exempt: true,
    is_active: true,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
];

// ── DTE ───────────────────────────────────────────────────────────────────────

export const MOCK_DTES: DTE[] = [
  {
    id: "d0000001-0000-0000-0000-000000000001",
    company_id: "11111111-1111-1111-1111-111111111111",
    customer_id: "c1000001-0000-0000-0000-000000000001",
    dte_type: 33,
    folio: 1001,
    issue_date: "2026-06-01",
    total_amount: "595000",
    net_amount: "500000",
    exempt_amount: "0",
    tax_amount: "95000",
    status: "accepted",
    sii_track_id: "TRK-001",
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "d0000001-0000-0000-0000-000000000002",
    company_id: "11111111-1111-1111-1111-111111111111",
    customer_id: "c1000001-0000-0000-0000-000000000002",
    dte_type: 33,
    folio: 1002,
    issue_date: "2026-06-05",
    total_amount: "297500",
    net_amount: "250000",
    exempt_amount: "0",
    tax_amount: "47500",
    status: "sent",
    sii_track_id: "TRK-002",
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "d0000001-0000-0000-0000-000000000003",
    company_id: "11111111-1111-1111-1111-111111111111",
    customer_id: "c1000001-0000-0000-0000-000000000003",
    dte_type: 39,
    folio: 201,
    issue_date: "2026-06-10",
    total_amount: "47600",
    net_amount: "40000",
    exempt_amount: "0",
    tax_amount: "7600",
    status: "generated",
    sii_track_id: null,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "d0000001-0000-0000-0000-000000000004",
    company_id: "11111111-1111-1111-1111-111111111111",
    customer_id: "c1000001-0000-0000-0000-000000000001",
    dte_type: 33,
    folio: 1003,
    issue_date: "2026-06-15",
    total_amount: "1190000",
    net_amount: "1000000",
    exempt_amount: "0",
    tax_amount: "190000",
    status: "draft",
    sii_track_id: null,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "d0000001-0000-0000-0000-000000000005",
    company_id: "11111111-1111-1111-1111-111111111111",
    customer_id: "c1000001-0000-0000-0000-000000000002",
    dte_type: 61,
    folio: 51,
    issue_date: "2026-06-18",
    total_amount: "119000",
    net_amount: "100000",
    exempt_amount: "0",
    tax_amount: "19000",
    status: "rejected",
    sii_track_id: "TRK-003",
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
  {
    id: "d0000001-0000-0000-0000-000000000006",
    company_id: "11111111-1111-1111-1111-111111111111",
    customer_id: "c1000001-0000-0000-0000-000000000003",
    dte_type: 33,
    folio: 1004,
    issue_date: "2026-06-20",
    total_amount: "892500",
    net_amount: "750000",
    exempt_amount: "0",
    tax_amount: "142500",
    status: "queued",
    sii_track_id: null,
    created_at: "2026-06-24T00:00:00Z",
    updated_at: "2026-06-24T00:00:00Z",
  },
];

// ── Subscription ──────────────────────────────────────────────────────────────

export const MOCK_SUBSCRIPTION = {
  id: "sub-0001",
  plan_code: "pyme",
  plan_name: "PyME",
  status: "active",
  current_period_start: "2026-06-01",
  current_period_end: "2026-06-30",
  cancel_at_period_end: false,
};

export const MOCK_USAGE = {
  plan_code: "pyme",
  plan_name: "PyME",
  period_month: 6,
  period_year: 2026,
  dtes_used: 6,
  dtes_limit: 500,
  api_calls_used: 42,
  api_rate_limit_per_min: 60,
  users_used: 3,
  users_limit: 10,
  storage_used_bytes: 2_097_152,
  storage_limit_mb: 5120,
  api_access: true,
};

export const MOCK_PLANS = [
  { code: "starter", name: "Starter", price: 0, currency: "CLP", billing_cycle: "monthly", features: { dte_limit: 50, users_limit: 2, api_access: false }, sort_order: 1 },
  { code: "pyme", name: "PyME", price: 29990, currency: "CLP", billing_cycle: "monthly", features: { dte_limit: 500, users_limit: 10, api_access: true, api_rate_limit_per_min: 60 }, sort_order: 2 },
  { code: "business", name: "Business", price: 79990, currency: "CLP", billing_cycle: "monthly", features: { dte_limit: 2000, users_limit: 50, api_access: true, api_rate_limit_per_min: 300 }, sort_order: 3 },
  { code: "enterprise", name: "Enterprise", price: 0, currency: "CLP", billing_cycle: "monthly", features: { dte_limit: -1, users_limit: -1, api_access: true, api_rate_limit_per_min: 1000 }, sort_order: 4 },
];

export const MOCK_BILLING_EVENTS = [
  { id: "be-001", event_type: "activation", amount: 0, currency: "CLP", description: "Plan PyME (trial) activado", created_at: "2026-06-01T00:00:00Z" },
  { id: "be-002", event_type: "upgrade", amount: 29990, currency: "CLP", description: "Plan cambiado: Starter → PyME", created_at: "2026-06-05T10:30:00Z" },
];

// ── API Keys ──────────────────────────────────────────────────────────────────

export const MOCK_API_KEYS = [
  { id: "key-001", name: "Integración ERP", prefix: "ohm_k1x9", scopes: ["read", "dte", "customers"], is_active: true, expires_at: "2027-06-24T00:00:00Z", last_used_at: "2026-06-24T10:15:00Z", created_at: "2026-01-15T00:00:00Z" },
  { id: "key-002", name: "WooCommerce Plugin", prefix: "ohm_w4r2", scopes: ["dte", "customers", "products"], is_active: true, expires_at: null, last_used_at: "2026-06-23T20:00:00Z", created_at: "2026-03-01T00:00:00Z" },
  { id: "key-003", name: "Legacy (revocada)", prefix: "ohm_l9z5", scopes: ["read"], is_active: false, expires_at: null, last_used_at: null, created_at: "2025-12-01T00:00:00Z" },
];

// ── SuperAdmin Metrics ────────────────────────────────────────────────────────

export const MOCK_SAAS_METRICS = {
  snapshot_date: "2026-06-24",
  mrr: 1499500,
  arr: 17994000,
  active_companies: 42,
  trial_companies: 8,
  suspended_companies: 2,
  total_users: 215,
  dtes_this_month: 4820,
  api_calls_this_month: 38200,
  churn_rate_pct: 0.0238,
  plan_distribution: { starter: 15, pyme: 20, business: 7, enterprise: 0 },
  history: Array.from({ length: 6 }, (_, i) => ({
    date: `2026-0${i + 1}-01`,
    mrr: 800000 + i * 120000,
    active_companies: 25 + i * 3,
  })),
};

export const MOCK_SUPERADMIN_COMPANIES = [
  { id: "11111111-1111-1111-1111-111111111111", rut: "76.123.456-7", legal_name: "TechCorp Chile SpA", is_active: true, plan: "pyme", created_at: "2026-01-15T00:00:00Z" },
  { id: "22222222-2222-2222-2222-222222222222", rut: "77.987.654-3", legal_name: "Retail Demo Ltda.", is_active: true, plan: "starter", created_at: "2026-03-01T00:00:00Z" },
  { id: "33333333-3333-3333-3333-333333333333", rut: "78.111.222-5", legal_name: "Ecommerce Plus SpA", is_active: false, plan: "business", created_at: "2026-02-15T00:00:00Z" },
  { id: "44444444-4444-4444-4444-444444444444", rut: "79.444.555-6", legal_name: "Consultora Norte SA", is_active: true, plan: "pyme", created_at: "2026-04-10T00:00:00Z" },
];

// ── Onboarding ────────────────────────────────────────────────────────────────

export const MOCK_ONBOARDING = {
  company_id: "11111111-1111-1111-1111-111111111111",
  current_step: 5,
  total_steps: 8,
  completed_steps: [1, 2, 3, 4],
  skipped_steps: [],
  progress_pct: 50,
  is_completed: false,
  next_step: 5,
  next_step_label: "Configuración de correo",
  step_labels: {
    1: "Datos de empresa",
    2: "Configuración tributaria",
    3: "Certificado digital",
    4: "Carga de CAF",
    5: "Configuración de correo",
    6: "Logo corporativo",
    7: "Usuario administrador",
    8: "Validación final",
  },
};
