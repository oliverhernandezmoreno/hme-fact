import { z } from "zod";

export const companySchema = z.object({
  rut: z.string().min(8, "RUT requerido").max(12),
  legal_name: z.string().min(2, "Razon social requerida"),
  fantasy_name: z.string().optional(),
  giro: z.string().optional(),
  address: z.string().optional(),
  comuna: z.string().optional(),
  city: z.string().optional(),
  sii_resolution_number: z.number().int().positive().optional().nullable(),
  sii_resolution_date: z.string().optional().nullable()
});

export type CompanyFormValues = z.infer<typeof companySchema>;
