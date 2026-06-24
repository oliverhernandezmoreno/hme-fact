"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Plus, Users } from "lucide-react";
import { useState } from "react";

import { DataTable } from "@/components/data-table/data-table";
import { EmptyState } from "@/components/feedback/empty-state";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

import { useCustomers } from "../hooks/use-customers";
import type { Customer } from "../types";
import { CustomerForm } from "./customer-form";

const columns: ColumnDef<Customer>[] = [
  { accessorKey: "rut", header: "RUT" },
  { accessorKey: "legal_name", header: "Razon social" },
  { accessorKey: "giro", header: "Giro" },
  { accessorKey: "email", header: "Correo" },
  { accessorKey: "city", header: "Ciudad" }
];

export function CustomersPage() {
  const [open, setOpen] = useState(false);
  const { data = [], isLoading } = useCustomers();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Clientes</h1>
          <p className="text-sm text-muted-foreground">Busqueda, filtros y mantenimiento de receptores.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4" />
              Nuevo cliente
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-3xl">
            <DialogHeader>
              <DialogTitle>Crear cliente</DialogTitle>
            </DialogHeader>
            <CustomerForm onDone={() => setOpen(false)} />
          </DialogContent>
        </Dialog>
      </div>
      {!data.length && !isLoading ? (
        <EmptyState icon={Users} title="Sin clientes" description="Agrega clientes para emitir facturas y boletas." />
      ) : (
        <DataTable columns={columns} data={data} searchPlaceholder="Buscar cliente" />
      )}
    </div>
  );
}
