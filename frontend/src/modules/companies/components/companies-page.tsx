"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Building2, Plus } from "lucide-react";
import { useState } from "react";

import { DataTable } from "@/components/data-table/data-table";
import { EmptyState } from "@/components/feedback/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { formatDate } from "@/lib/utils";

import { useCompanies } from "../hooks/use-companies";
import type { Company } from "../types";
import { CompanyForm } from "./company-form";

const columns: ColumnDef<Company>[] = [
  { accessorKey: "rut", header: "RUT" },
  { accessorKey: "legal_name", header: "Razon social" },
  { accessorKey: "giro", header: "Giro" },
  { accessorKey: "city", header: "Ciudad" },
  { accessorKey: "created_at", header: "Creada", cell: ({ row }) => formatDate(row.original.created_at) }
];

export function CompaniesPage() {
  const [open, setOpen] = useState(false);
  const { data = [], isLoading } = useCompanies();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Empresas</h1>
          <p className="text-sm text-muted-foreground">Multiempresa y configuracion tributaria.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4" />
              Nueva empresa
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-3xl">
            <DialogHeader>
              <DialogTitle>Crear empresa</DialogTitle>
            </DialogHeader>
            <CompanyForm onDone={() => setOpen(false)} />
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Configuracion tributaria</CardTitle>
          <CardDescription>Resolucion SII, giro, direccion y empresa activa.</CardDescription>
        </CardHeader>
        <CardContent>
          {!data.length && !isLoading ? (
            <EmptyState
              icon={Building2}
              title="Sin empresas"
              description="Crea la primera empresa para comenzar a emitir documentos tributarios."
            />
          ) : (
            <DataTable columns={columns} data={data} searchPlaceholder="Buscar empresa" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
