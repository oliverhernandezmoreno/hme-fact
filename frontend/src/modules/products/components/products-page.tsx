"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Package, Plus } from "lucide-react";
import { useState } from "react";

import { DataTable } from "@/components/data-table/data-table";
import { EmptyState } from "@/components/feedback/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { formatCurrency } from "@/lib/utils";

import { useProducts } from "../hooks/use-products";
import type { Product } from "../types";
import { ProductForm } from "./product-form";

const columns: ColumnDef<Product>[] = [
  { accessorKey: "sku", header: "SKU" },
  { accessorKey: "name", header: "Producto" },
  { accessorKey: "unit", header: "Unidad" },
  { accessorKey: "unit_price", header: "Precio", cell: ({ row }) => formatCurrency(Number(row.original.unit_price)) },
  { accessorKey: "tax_exempt", header: "IVA", cell: ({ row }) => (row.original.tax_exempt ? <Badge>Exento</Badge> : <Badge variant="info">Afecto</Badge>) }
];

export function ProductsPage() {
  const [open, setOpen] = useState(false);
  const { data = [], isLoading } = useProducts();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Productos</h1>
          <p className="text-sm text-muted-foreground">Catalogo preparado para stock e inventario.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4" />
              Nuevo producto
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Crear producto</DialogTitle>
            </DialogHeader>
            <ProductForm onDone={() => setOpen(false)} />
          </DialogContent>
        </Dialog>
      </div>
      {!data.length && !isLoading ? (
        <EmptyState icon={Package} title="Sin productos" description="Crea productos y servicios para emitir DTE rapidamente." />
      ) : (
        <DataTable columns={columns} data={data} searchPlaceholder="Buscar producto" />
      )}
    </div>
  );
}
