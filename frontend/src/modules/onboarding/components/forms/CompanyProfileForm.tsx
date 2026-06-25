import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useOnboardingStore } from "../../stores/useOnboardingStore";

const companySchema = z.object({
  rut: z.string().min(8, "RUT inválido").max(12, "RUT demasiado largo"),
  legal_name: z.string().min(3, "La Razón Social debe tener al menos 3 caracteres"),
  giro: z.string().min(3, "El giro comercial es requerido"),
  address: z.string().min(5, "Dirección requerida"),
  comuna: z.string().min(3, "Comuna requerida"),
});

type CompanyFormValues = z.infer<typeof companySchema>;

export function CompanyProfileForm({ stepCode }: { stepCode: string }) {
  const { completeStep } = useOnboardingStore();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<CompanyFormValues>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      rut: "",
      legal_name: "",
      giro: "",
      address: "",
      comuna: "",
    }
  });

  const onSubmit = async (data: CompanyFormValues) => {
    // Save to the API or Store
    await completeStep(stepCode, data);
  };

  return (
    <form id={`form-${stepCode}`} onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label className="text-sm font-medium">RUT Empresa</label>
          <input 
            {...register("rut")} 
            placeholder="Ej: 76.123.456-7" 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.rut && <span className="text-xs text-destructive">{errors.rut.message}</span>}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Razón Social</label>
          <input 
            {...register("legal_name")} 
            placeholder="Ej: Comercializadora Acme SpA" 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.legal_name && <span className="text-xs text-destructive">{errors.legal_name.message}</span>}
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-sm font-medium">Giro Comercial (Principal)</label>
          <input 
            {...register("giro")} 
            placeholder="Ej: Venta al por menor de artículos de ferretería" 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.giro && <span className="text-xs text-destructive">{errors.giro.message}</span>}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Dirección Casa Matriz</label>
          <input 
            {...register("address")} 
            placeholder="Ej: Av. Providencia 1234" 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.address && <span className="text-xs text-destructive">{errors.address.message}</span>}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Comuna</label>
          <input 
            {...register("comuna")} 
            placeholder="Ej: Providencia" 
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
          />
          {errors.comuna && <span className="text-xs text-destructive">{errors.comuna.message}</span>}
        </div>
      </div>
      
      {/* Hidden button to hook into renderer actions if needed, or we rely on the parent button */}
      <button type="submit" id={`submit-${stepCode}`} className="hidden">Guardar</button>
    </form>
  );
}
