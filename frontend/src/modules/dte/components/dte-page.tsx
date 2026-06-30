"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { FileText, RefreshCw, Send, AlertTriangle } from "lucide-react";
import { useState } from "react";

import { DataTable } from "@/components/data-table/data-table";
import { EmptyState } from "@/components/feedback/empty-state";
import { StatusBadge } from "@/components/feedback/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { formatCurrency, formatDate } from "@/lib/utils";

import { useDTEList, useDTEMutations } from "../hooks/use-dte";
import type { DTE } from "../types";
import { DTEIssueForm } from "./dte-issue-form";

export function DTEPage() {
  const [open, setOpen] = useState(false);
  const { data = [], isLoading } = useDTEList();
  const { send, refreshStatus, downloadPdf } = useDTEMutations();
  const contingencyDtes = data.filter((d) => d.status === "contingency");
  const hasContingency = contingencyDtes.length > 0;

  const columns: ColumnDef<DTE>[] = [
    { accessorKey: "folio", header: "Folio" },
    { accessorKey: "dte_type", header: "Tipo" },
    { accessorKey: "issue_date", header: "Fecha", cell: ({ row }) => formatDate(row.original.issue_date) },
    { accessorKey: "total_amount", header: "Total", cell: ({ row }) => formatCurrency(Number(row.original.total_amount)) },
    { accessorKey: "status", header: "Estado", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
    {
      id: "actions",
      header: "Acciones",
      cell: ({ row }) => {
        const dte = row.original;
        const isContingency = dte.status === "contingency";
        const hasPdf = ["generated", "sent", "accepted", "rejected", "contingency"].includes(dte.status);
        return (
          <div className="flex gap-2">
            {hasPdf && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => downloadPdf.mutate({ id: dte.id, folio: dte.folio })}
                title="Descargar PDF"
                disabled={downloadPdf.isPending}
              >
                <FileText className="h-4 w-4 text-rose-600 dark:text-rose-400" />
              </Button>
            )}
            <Button
              variant={isContingency ? "default" : "outline"}
              size="sm"
              onClick={() => send.mutate(dte.id)}
              className={isContingency ? "bg-amber-600 hover:bg-amber-700 text-white" : ""}
              title={isContingency ? "Reintentar Envío a SII" : "Enviar a SII"}
            >
              <Send className="h-4 w-4" />
              {isContingency && <span className="ml-1 text-xs">Reintentar</span>}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => refreshStatus.mutate(dte.id)}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        );
      }
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Documentos tributarios</h1>
          <p className="text-sm text-muted-foreground">Emision, envio SII y tracking tributario.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <FileText className="h-4 w-4" />
              Emitir DTE
            </Button>
          </DialogTrigger>
          <DialogContent className="max-h-[90vh] max-w-5xl overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Emitir documento</DialogTitle>
            </DialogHeader>
            <DTEIssueForm />
          </DialogContent>
        </Dialog>
      </div>

      {hasContingency && (
        <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-4 text-amber-800 dark:text-amber-300">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">Documentos en Contingencia</h4>
              <p className="text-xs text-amber-700/90 dark:text-amber-400/90 mt-0.5">
                Hay {contingencyDtes.length} documento{contingencyDtes.length > 1 ? "s" : ""} en estado de contingencia. 
                Se han firmado digitalmente de forma exitosa y son válidos fiscalmente, pero no se pudieron transmitir debido a caídas externas en los servidores del SII. 
                Los reintentos programados del sistema los enviarán de forma automática, o bien puedes forzar la transmisión presionando <strong>Reintentar</strong> en la lista de acciones.
              </p>
            </div>
          </div>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Estado tributario</CardTitle>
          <CardDescription>Estados normalizados: draft, generated, sent, accepted, rejected, error, contingency.</CardDescription>
        </CardHeader>
        <CardContent>
          {!data.length && !isLoading ? (
            <EmptyState
              icon={FileText}
              title="Sin documentos"
              description="Emite facturas, boletas o notas de credito desde el formulario tributario."
            />
          ) : (
            <DataTable columns={columns} data={data} searchPlaceholder="Buscar DTE" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
