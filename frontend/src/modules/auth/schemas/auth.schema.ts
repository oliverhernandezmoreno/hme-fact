import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Ingresa un correo valido"),
  password: z.string().min(8, "La clave debe tener al menos 8 caracteres")
});

export type LoginFormValues = z.infer<typeof loginSchema>;
