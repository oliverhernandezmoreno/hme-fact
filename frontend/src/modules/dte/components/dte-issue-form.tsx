"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Trash2 } from "lucide-react";
import { useFieldArray, useForm, useWatch } from "react-hook-form";

import { FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useCustomers } from "@/modules/customers/hooks/use-customers";
import { useProducts } from "@/modules/products/hooks/use-products";
import { formatCurrency } from "@/lib/utils";

import { useDTEMutations } from "../hooks/use-dte";
import {
  calculateDteTotals,
  dteIssueSchema,
  type DTEIssueFormInput,
  type DTEIssueFormValues
} from "../schemas/dte.schema";

export function DTEIssueForm({ dteType = 33 }: { dteType?: 33 | 39 | 61 }) {
  const { data: customers = [] } = useCustomers();
  const { data: products = [] } = useProducts();
  const { create } = useDTEMutations();
  const form = useForm<DTEIssueFormInput, unknown, DTEIssueFormValues>({
    resolver: zodResolver(dteIssueSchema),
    defaultValues: {
      dte_type: dteType,
      issue_date: new Date().toISOString().slice(0, 10),
      items: [{ description: "", quantity: 1, unit_price: 0, tax_exempt: false }]
    }
  });
  const items = useWatch({ control: form.control, name: "items" }) ?? [];
  const totals = calculateDteTotals(items);
  const itemArray = useFieldArray({ control: form.control, name: "items" });

  function applyProduct(index: number, productId: string) {
    const product = products.find((item) => item.id === productId);
    if (!product) return;
    form.setValue(`items.${index}.product_id`, product.id);
    form.setValue(`items.${index}.description`, product.name);
    form.setValue(`items.${index}.unit_price`, Number(product.unit_price));
    form.setValue(`items.${index}.tax_exempt`, product.tax_exempt);
  }

  return (
    <form className="space-y-6" onSubmit={form.handleSubmit((values) => create.mutate(values))}>
      <Card>
        <CardHeader>
          <CardTitle>Documento tributario</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <FormField label="Tipo DTE" error={form.formState.errors.dte_type}>
            <Select
              value={String(form.watch("dte_type"))}
              onValueChange={(value) => form.setValue("dte_type", Number(value) as 33 | 39 | 61)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="33">Factura electronica</SelectItem>
                <SelectItem value="39">Boleta electronica</SelectItem>
                <SelectItem value="61">Nota de credito</SelectItem>
              </SelectContent>
            </Select>
          </FormField>
          <FormField label="Cliente" error={form.formState.errors.customer_id}>
            <Select onValueChange={(value) => form.setValue("customer_id", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar cliente" />
              </SelectTrigger>
              <SelectContent>
                {customers.map((customer) => (
                  <SelectItem key={customer.id} value={customer.id}>
                    {customer.legal_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <FormField label="Fecha emision" error={form.formState.errors.issue_date}>
            <Input type="date" {...form.register("issue_date")} />
          </FormField>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Lineas del documento</CardTitle>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => itemArray.append({ description: "", quantity: 1, unit_price: 0, tax_exempt: false })}
          >
            <Plus className="h-4 w-4" />
            Agregar
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {itemArray.fields.map((field, index) => (
            <div key={field.id} className="grid gap-3 rounded-lg border p-3 lg:grid-cols-[1.3fr_1.5fr_.7fr_.9fr_.5fr_auto]">
              <Select onValueChange={(value) => applyProduct(index, value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Producto" />
                </SelectTrigger>
                <SelectContent>
                  {products.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      {product.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input placeholder="Descripcion" {...form.register(`items.${index}.description`)} />
              <Input
                type="number"
                min="0"
                step="0.01"
                {...form.register(`items.${index}.quantity`, { valueAsNumber: true })}
              />
              <Input
                type="number"
                min="0"
                {...form.register(`items.${index}.unit_price`, { valueAsNumber: true })}
              />
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" {...form.register(`items.${index}.tax_exempt`)} />
                Exento
              </label>
              <Button type="button" variant="ghost" size="icon" onClick={() => itemArray.remove(index)}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <Card className="lg:col-start-2">
          <CardHeader>
            <CardTitle>Totales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span>Neto</span>
              <strong>{formatCurrency(totals.net)}</strong>
            </div>
            <div className="flex justify-between">
              <span>Exento</span>
              <strong>{formatCurrency(totals.exempt)}</strong>
            </div>
            <div className="flex justify-between">
              <span>IVA 19%</span>
              <strong>{formatCurrency(totals.iva)}</strong>
            </div>
            <div className="flex justify-between border-t pt-3 text-base">
              <span>Total</span>
              <strong>{formatCurrency(totals.total)}</strong>
            </div>
            <Button className="w-full" disabled={create.isPending}>
              Emitir DTE
            </Button>
          </CardContent>
        </Card>
      </div>
    </form>
  );
}
