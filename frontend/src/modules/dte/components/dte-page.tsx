"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { FileText, RefreshCw, Send } from "lucide-react";
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
  const { send, refreshStatus } = useDTEMutations();

  const columns: ColumnDef<DTE>[] = [
    { accessorKey: "folio", header: "Folio" },
    { accessorKey: "dte_type", header: "Tipo" },
    { accessorKey: "issue_date", header: "Fecha", cell: ({ row }) => formatDate(row.original.issue_date) },
    { accessorKey: "total_amount", header: "Total", cell: ({ row }) => formatCurrency(Number(row.original.total_amount)) },
    { accessorKey: "status", header: "Estado", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
    {
      id: "actions",
      header: "Acciones",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => send.mutate(row.original.id)}>
            <Send className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => refreshStatus.mutate(row.original.id)}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      )
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
      <Card>
        <CardHeader>
          <CardTitle>Estado tributario</CardTitle>
          <CardDescription>Estados normalizados: draft, generated, sent, accepted, rejected, error.</CardDescription>
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
