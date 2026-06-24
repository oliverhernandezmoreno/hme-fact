"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useCustomerMutations } from "../hooks/use-customers";
import { customerSchema, type CustomerFormValues } from "../schemas/customer.schema";

export function CustomerForm({ onDone }: { onDone?: () => void }) {
  const { create } = useCustomerMutations();
  const form = useForm<CustomerFormValues>({
    resolver: zodResolver(customerSchema),
    defaultValues: { rut: "", legal_name: "", giro: "", email: "", phone: "" }
  });

  return (
    <form
      className="grid gap-4 md:grid-cols-2"
      onSubmit={form.handleSubmit((values) => create.mutate(values, { onSuccess: onDone }))}
    >
      <FormField label="RUT" error={form.formState.errors.rut}>
        <Input {...form.register("rut")} />
      </FormField>
      <FormField label="Razon social" error={form.formState.errors.legal_name}>
        <Input {...form.register("legal_name")} />
      </FormField>
      <FormField label="Giro">
        <Input {...form.register("giro")} />
      </FormField>
      <FormField label="Correo" error={form.formState.errors.email}>
        <Input type="email" {...form.register("email")} />
      </FormField>
      <FormField label="Telefono">
        <Input {...form.register("phone")} />
      </FormField>
      <FormField label="Ciudad">
        <Input {...form.register("city")} />
      </FormField>
      <FormField label="Direccion" className="md:col-span-2">
        <Input {...form.register("address")} />
      </FormField>
      <div className="md:col-span-2">
        <Button disabled={create.isPending}>Guardar cliente</Button>
      </div>
    </form>
  );
}
