import { z } from "zod";

export const dteItemSchema = z.object({
  product_id: z.string().optional(),
  description: z.string().min(2, "Descripcion requerida"),
  quantity: z.number().positive("Cantidad invalida"),
  unit_price: z.number().min(0, "Precio invalido"),
  tax_exempt: z.boolean().default(false)
});

export const dteIssueSchema = z.object({
  customer_id: z.string().uuid("Selecciona cliente"),
  dte_type: z.number().pipe(
    z.union([
      z.literal(33),
      z.literal(34),
      z.literal(39),
      z.literal(41),
      z.literal(56),
      z.literal(61)
    ])
  ),
  issue_date: z.string().min(1, "Fecha requerida"),
  due_date: z.string().optional(),
  items: z.array(dteItemSchema).min(1, "Agrega al menos una linea"),
  reference: z
    .object({
      dte_type: z.number().optional(),
      folio: z.number().optional(),
      date: z.string().optional(),
      code: z.number().optional(),
      reason: z.string().optional()
    })
    .optional()
});

export type DTEIssueFormValues = z.infer<typeof dteIssueSchema>;
export type DTEIssueFormInput = z.input<typeof dteIssueSchema>;

export function calculateDteTotals(
  items: Array<{ quantity: number; unit_price: number; tax_exempt?: boolean } & Record<string, unknown>>
) {
  const net = items
    .filter((item) => !item.tax_exempt)
    .reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const exempt = items
    .filter((item) => item.tax_exempt)
    .reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const iva = Math.round(net * 0.19);
  return {
    net,
    exempt,
    iva,
    total: net + exempt + iva
  };
}
