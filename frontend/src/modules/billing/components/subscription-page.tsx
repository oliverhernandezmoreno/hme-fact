"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BarChart3, CreditCard, FileText, RefreshCw, Users, Zap } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

import { Skeleton } from "@/components/feedback/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import { getBillingEvents, getMySubscription, getPlans, getUsage } from "@/modules/billing/services/subscription.service";

const STATUS_LABELS: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  active: { label: "Activa", variant: "default" },
  trial: { label: "Prueba", variant: "secondary" },
  suspended: { label: "Suspendida", variant: "destructive" },
  cancelled: { label: "Cancelada", variant: "destructive" },
};

function UsageBar({ used, limit, label }: { used: number; limit: number; label: string }) {
  const pct = limit <= 0 ? 0 : Math.min(100, (used / limit) * 100);
  const color = pct >= 90 ? "bg-destructive" : pct >= 75 ? "bg-amber-500" : "bg-primary";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{limit === -1 ? `${used} / ∞` : `${used} / ${limit}`}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${limit === -1 ? 10 : pct}%` }} />
      </div>
    </div>
  );
}

export function SubscriptionPage() {
  const { data: subscription, isLoading: loadingSub } = useQuery({
    queryKey: ["subscription"],
    queryFn: getMySubscription,
  });
  const { data: usage, isLoading: loadingUsage } = useQuery({
    queryKey: ["subscription-usage"],
    queryFn: getUsage,
  });
  const { data: plans = [] } = useQuery({
    queryKey: ["plans"],
    queryFn: getPlans,
  });
  const { data: events = [] } = useQuery({
    queryKey: ["billing-events"],
    queryFn: getBillingEvents,
  });

  const statusInfo = subscription ? (STATUS_LABELS[subscription.status] ?? { label: subscription.status, variant: "outline" as const }) : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Plan & Consumo</h1>
          <p className="text-sm text-muted-foreground">Gestiona tu suscripción y monitorea el uso de la plataforma.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => toast.info("Contactar ventas para upgrades")}>
          Cambiar plan
        </Button>
      </div>

      {/* Plan actual */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <CreditCard className="h-4 w-4 text-primary" /> Suscripción activa
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingSub ? (
              <div className="space-y-2"><Skeleton className="h-8 w-32" /><Skeleton className="h-4 w-48" /></div>
            ) : subscription ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-bold">{subscription.plan_name}</span>
                  {statusInfo && <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>}
                </div>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>Período: <strong>{subscription.current_period_start}</strong> → <strong>{subscription.current_period_end}</strong></p>
                  {subscription.cancel_at_period_end && (
                    <p className="flex items-center gap-1 text-amber-600">
                      <AlertTriangle className="h-3.5 w-3.5" /> Se cancelará al final del período
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Sin suscripción activa. <Link href="#planes" className="text-primary underline">Ver planes</Link></p>
            )}
          </CardContent>
        </Card>

        {/* Consumo del período */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <BarChart3 className="h-4 w-4 text-primary" /> Consumo del período
            </CardTitle>
            {usage && <CardDescription>{usage.period_year}-{String(usage.period_month).padStart(2, "0")}</CardDescription>}
          </CardHeader>
          <CardContent>
            {loadingUsage ? (
              <div className="space-y-3"><Skeleton className="h-6 w-full" /><Skeleton className="h-6 w-full" /><Skeleton className="h-6 w-full" /></div>
            ) : usage ? (
              <div className="space-y-4">
                <UsageBar used={usage.dtes_used} limit={usage.dtes_limit} label="DTE emitidos" />
                <UsageBar used={usage.users_used} limit={usage.users_limit} label="Usuarios" />
                <UsageBar used={Math.round(usage.storage_used_bytes / 1024 / 1024)} limit={usage.storage_limit_mb} label="Almacenamiento (MB)" />
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground flex items-center gap-1"><Zap className="h-3.5 w-3.5" /> API Calls</span>
                  <span className="font-medium">{usage.api_calls_used.toLocaleString()} llamadas</span>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>

      {/* Historial de eventos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-4 w-4 text-primary" /> Historial de facturación
          </CardTitle>
          <CardDescription>Últimos eventos de tu suscripción</CardDescription>
        </CardHeader>
        <CardContent>
          {events.length === 0 ? (
            <p className="text-sm text-muted-foreground">Sin eventos registrados.</p>
          ) : (
            <div className="space-y-2">
              {events.map((e) => (
                <div key={e.id} className="flex items-center justify-between rounded-lg border px-4 py-3">
                  <div>
                    <p className="text-sm font-medium">{e.description}</p>
                    <p className="text-xs text-muted-foreground">{new Date(e.created_at).toLocaleDateString("es-CL")}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">{e.amount > 0 ? formatCurrency(e.amount) : "—"}</p>
                    <Badge variant="outline" className="text-[10px]">{e.event_type}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Planes disponibles */}
      <div id="planes">
        <h2 className="mb-4 text-lg font-semibold">Planes disponibles</h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {plans.map((plan) => {
            const isCurrent = plan.code === subscription?.plan_code;
            return (
              <Card key={plan.code} className={isCurrent ? "border-primary/60 ring-1 ring-primary/30" : ""}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{plan.name}</CardTitle>
                    {isCurrent && <Badge variant="default" className="text-xs">Actual</Badge>}
                  </div>
                  <CardDescription className="text-xl font-bold text-foreground">
                    {plan.price === 0 ? (plan.sort_order === 4 ? "Contactar" : "Gratis") : formatCurrency(plan.price)}
                    {plan.price > 0 && <span className="text-sm font-normal text-muted-foreground">/mes</span>}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-1.5 text-sm">
                  <p className="flex items-center gap-2"><FileText className="h-3.5 w-3.5 text-muted-foreground" />
                    {(plan.features.dte_limit as number) === -1 ? "DTE ilimitados" : `${plan.features.dte_limit} DTE/mes`}
                  </p>
                  <p className="flex items-center gap-2"><Users className="h-3.5 w-3.5 text-muted-foreground" />
                    {(plan.features.users_limit as number) === -1 ? "Usuarios ilimitados" : `${plan.features.users_limit} usuarios`}
                  </p>
                  {!isCurrent && plan.price > 0 && (
                    <Button className="mt-3 w-full" size="sm" variant="outline"
                      onClick={() => toast.info(`Contactar a ventas para activar plan ${plan.name}`)}>
                      Activar plan
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
