"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { companySchema, type CompanyFormValues } from "../schemas/company.schema";
import { useCompanyMutations } from "../hooks/use-companies";

export function CompanyForm({ onDone }: { onDone?: () => void }) {
  const { create } = useCompanyMutations();
  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companySchema),
    defaultValues: { rut: "", legal_name: "", fantasy_name: "", giro: "", city: "" }
  });

  return (
    <form
      className="grid gap-4 md:grid-cols-2"
      onSubmit={form.handleSubmit((values) => create.mutate(values, { onSuccess: onDone }))}
    >
      <FormField label="RUT" error={form.formState.errors.rut}>
        <Input placeholder="76123456-7" {...form.register("rut")} />
      </FormField>
      <FormField label="Razon social" error={form.formState.errors.legal_name}>
        <Input {...form.register("legal_name")} />
      </FormField>
      <FormField label="Nombre fantasia">
        <Input {...form.register("fantasy_name")} />
      </FormField>
      <FormField label="Giro">
        <Input {...form.register("giro")} />
      </FormField>
      <FormField label="Comuna">
        <Input {...form.register("comuna")} />
      </FormField>
      <FormField label="Ciudad">
        <Input {...form.register("city")} />
      </FormField>
      <FormField label="Direccion" className="md:col-span-2">
        <Input {...form.register("address")} />
      </FormField>
      <div className="md:col-span-2">
        <Button disabled={create.isPending}>Guardar empresa</Button>
      </div>
    </form>
  );
}
