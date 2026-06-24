"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useProductMutations } from "../hooks/use-products";
import { productSchema, type ProductFormInput, type ProductFormValues } from "../schemas/product.schema";

export function ProductForm({ onDone }: { onDone?: () => void }) {
  const { create } = useProductMutations();
  const form = useForm<ProductFormInput, unknown, ProductFormValues>({
    resolver: zodResolver(productSchema),
    defaultValues: { sku: "", name: "", description: "", unit: "UN", unit_price: 0, tax_exempt: false }
  });

  return (
    <form
      className="grid gap-4 md:grid-cols-2"
      onSubmit={form.handleSubmit((values) => create.mutate(values, { onSuccess: onDone }))}
    >
      <FormField label="SKU">
        <Input {...form.register("sku")} />
      </FormField>
      <FormField label="Nombre" error={form.formState.errors.name}>
        <Input {...form.register("name")} />
      </FormField>
      <FormField label="Unidad" error={form.formState.errors.unit}>
        <Input {...form.register("unit")} />
      </FormField>
      <FormField label="Precio neto" error={form.formState.errors.unit_price}>
        <Input type="number" {...form.register("unit_price", { valueAsNumber: true })} />
      </FormField>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" {...form.register("tax_exempt")} />
        Producto exento
      </label>
      <div className="md:col-span-2">
        <Button disabled={create.isPending}>Guardar producto</Button>
      </div>
    </form>
  );
}
