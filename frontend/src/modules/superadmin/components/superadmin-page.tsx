"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, CreditCard, FileText, TrendingUp, Users, Zap } from "lucide-react";
import { toast } from "sonner";

import { Skeleton } from "@/components/feedback/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { isMockMode } from "@/lib/env";
import { MOCK_SAAS_METRICS, MOCK_SUPERADMIN_COMPANIES } from "@/lib/mocks";
import { formatCurrency } from "@/lib/utils";
import { apiClient } from "@/services/api-client";

async function getSaasMetrics() {
  if (isMockMode) { await new Promise(r => setTimeout(r, 500)); return MOCK_SAAS_METRICS; }
  const r = await apiClient.get("/superadmin/metrics");
  return r.data;
}

async function getSuperAdminCompanies() {
  if (isMockMode) { await new Promise(r => setTimeout(r, 400)); return MOCK_SUPERADMIN_COMPANIES; }
  const r = await apiClient.get("/superadmin/companies");
  return r.data;
}

const kpiCards = [
  { key: "mrr", label: "MRR", icon: CreditCard, format: "currency" },
  { key: "arr", label: "ARR", icon: TrendingUp, format: "currency" },
  { key: "active_companies", label: "Empresas Activas", icon: Building2, format: "number" },
  { key: "total_users", label: "Usuarios Totales", icon: Users, format: "number" },
  { key: "dtes_this_month", label: "DTE Emitidos (mes)", icon: FileText, format: "number" },
  { key: "api_calls_this_month", label: "API Calls (mes)", icon: Zap, format: "number" },
];

export function SuperAdminPage() {
  const { data: metrics, isLoading: loadingM } = useQuery({ queryKey: ["saas-metrics"], queryFn: getSaasMetrics });
  const { data: companies = [], isLoading: loadingC } = useQuery({ queryKey: ["sa-companies"], queryFn: getSuperAdminCompanies });

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">SuperAdmin — Platform</h1>
          <p className="text-sm text-muted-foreground">Métricas globales y gestión de empresas.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => toast.info("Actualizando métricas...")}>
          Refrescar
        </Button>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {kpiCards.map(({ key, label, icon: Icon, format }) => (
          <Card key={key}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardDescription>{label}</CardDescription>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loadingM ? (
                <Skeleton className="h-8 w-32" />
              ) : (
                <p className="text-2xl font-bold">
                  {format === "currency"
                    ? formatCurrency(metrics?.[key as keyof typeof metrics] as number ?? 0)
                    : (metrics?.[key as keyof typeof metrics] as number ?? 0).toLocaleString()}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Plan distribution */}
      {metrics && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Distribución de planes</CardTitle>
            <CardDescription>Empresas activas y en trial por plan</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              {Object.entries(metrics.plan_distribution).map(([plan, count]) => (
                <div key={plan} className="flex items-center gap-3 rounded-lg border px-4 py-3">
                  <div>
                    <p className="text-sm font-medium capitalize">{plan}</p>
                    <p className="text-2xl font-bold">{count as number}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Companies table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Empresas en plataforma</CardTitle>
          <CardDescription>{companies.length} empresas registradas</CardDescription>
        </CardHeader>
        <CardContent>
          {loadingC ? (
            <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-12 w-full" />)}</div>
          ) : (
            <div className="divide-y rounded-lg border">
              {companies.map((c: { id: string; rut: string; legal_name: string; is_active: boolean; plan: string; created_at: string }) => (
                <div key={c.id} className="flex items-center justify-between px-4 py-3">
                  <div>
                    <p className="text-sm font-medium">{c.legal_name}</p>
                    <p className="text-xs text-muted-foreground">{c.rut} · {new Date(c.created_at).toLocaleDateString("es-CL")}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="info" className="capitalize text-xs">{c.plan}</Badge>
                    <Badge variant={c.is_active ? "default" : "warning"} className="text-xs">
                      {c.is_active ? "Activa" : "Inactiva"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
