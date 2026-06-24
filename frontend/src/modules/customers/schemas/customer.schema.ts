import { z } from "zod";

export const customerSchema = z.object({
  rut: z.string().min(8, "RUT requerido").max(12),
  legal_name: z.string().min(2, "Razon social requerida"),
  giro: z.string().optional(),
  email: z.string().email("Correo invalido").optional().or(z.literal("")),
  phone: z.string().optional(),
  address: z.string().optional(),
  comuna: z.string().optional(),
  city: z.string().optional()
});

export type CustomerFormValues = z.infer<typeof customerSchema>;
