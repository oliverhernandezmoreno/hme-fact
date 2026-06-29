import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useOnboardingStore } from "../../stores/useOnboardingStore";

const taxSchema = z.object({
  sii_resolution_number: z.coerce.number().min(1, "Debe ser un número válido"),
  sii_resolution_date: z.string().min(10, "Fecha obligatoria"),
});

type TaxFormValues = z.infer<typeof taxSchema>;

export function TaxConfigurationForm({ stepCode }: { stepCode: string }) {
  const { completeStep } = useOnboardingStore();
  const { register, handleSubmit, formState: { errors } } = useForm<TaxFormValues>({
    resolver: zodResolver(taxSchema) as any,
  });

  const onSubmit = async (data: TaxFormValues) => {
    await completeStep(stepCode, data);
  };

  return (
    <form id={`form-${stepCode}`} onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-300">¿Dónde encuentro esta información?</h4>
        <p className="text-xs text-blue-700 dark:text-blue-400 mt-1">
          El SII te asigna una fecha y un número de resolución cuando te autoriza como facturador electrónico.
          Si eres facturador nuevo o de portal MiPyme, la resolución suele ser la número "80" o "0".
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label className="text-sm font-medium">N° de Resolución SII</label>
          <input 
            type="number"
            {...register("sii_resolution_number")} 
            placeholder="Ej: 80" 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.sii_resolution_number && <span className="text-xs text-destructive">{errors.sii_resolution_number.message}</span>}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Fecha de Resolución SII</label>
          <input 
            type="date"
            {...register("sii_resolution_date")} 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.sii_resolution_date && <span className="text-xs text-destructive">{errors.sii_resolution_date.message}</span>}
        </div>
      </div>
      
      <button type="submit" id={`submit-${stepCode}`} className="hidden">Guardar</button>
    </form>
  );
}
