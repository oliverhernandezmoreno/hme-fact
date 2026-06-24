"use client";

import { AlertTriangle, CheckCircle2, FileText, TrendingUp } from "lucide-react";

import { Skeleton } from "@/components/feedback/skeleton";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useDTEList } from "@/modules/dte/hooks/use-dte";
import { formatCurrency, formatDate } from "@/lib/utils";

export function DashboardOverview() {
  const { data: dtes = [], isLoading } = useDTEList();
  const totalSales = dtes.reduce((sum, dte) => sum + Number(dte.total_amount), 0);
  const rejected = dtes.filter((dte) => dte.status === "rejected" || dte.status === "error").length;
  const accepted = dtes.filter((dte) => dte.status === "accepted").length;

  const metrics = [
    { label: "Ventas totales", value: formatCurrency(totalSales), icon: TrendingUp },
    { label: "DTE emitidos", value: String(dtes.length), icon: FileText },
    { label: "Aceptados SII", value: String(accepted), icon: CheckCircle2 },
    { label: "Rechazados/Error", value: String(rejected), icon: AlertTriangle }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard tributario</h1>
        <p className="text-sm text-muted-foreground">
          Vista operativa para ventas, documentos y control SII.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardDescription>{metric.label}</CardDescription>
              <metric.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-28" /> : <div className="text-2xl font-semibold">{metric.value}</div>}
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle>Actividad mensual</CardTitle>
            <CardDescription>Grafico preparado para analytics tributario y ventas.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex h-72 items-end gap-3 rounded-md border bg-muted/30 p-4">
              {[42, 58, 37, 76, 64, 88, 52, 91, 73, 84, 69, 96].map((height, index) => (
                <div key={index} className="flex flex-1 flex-col items-center gap-2">
                  <div className="w-full rounded-t bg-primary/80" style={{ height: `${height}%` }} />
                  <span className="text-[10px] text-muted-foreground">{index + 1}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Ultimos documentos</CardTitle>
            <CardDescription>Seguimiento reciente de DTE.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {dtes.slice(0, 6).map((dte) => (
              <div key={dte.id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium">DTE {dte.folio}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(dte.issue_date)}</p>
                </div>
                <p className="text-sm font-semibold">{formatCurrency(Number(dte.total_amount))}</p>
              </div>
            ))}
            {!dtes.length && !isLoading ? (
              <p className="text-sm text-muted-foreground">Aun no hay documentos emitidos.</p>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
