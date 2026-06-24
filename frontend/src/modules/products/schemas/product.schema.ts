import { z } from "zod";

export const productSchema = z.object({
  sku: z.string().optional(),
  name: z.string().min(2, "Nombre requerido"),
  description: z.string().optional(),
  unit: z.string().min(1, "Unidad requerida").default("UN"),
  unit_price: z.number().min(0, "Precio invalido"),
  tax_exempt: z.boolean().default(false)
});

export type ProductFormValues = z.infer<typeof productSchema>;
export type ProductFormInput = z.input<typeof productSchema>;
