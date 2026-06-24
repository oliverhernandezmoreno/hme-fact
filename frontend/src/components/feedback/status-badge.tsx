import { Badge } from "@/components/ui/badge";
import type { DTEStatus } from "@/types/api";

const statusLabels: Record<DTEStatus, string> = {
  draft: "Borrador",
  generated: "Generado",
  queued: "En cola",
  sent: "Enviado",
  accepted: "Aceptado",
  partially_accepted: "Aceptado con reparos",
  rejected: "Rechazado",
  error: "Error"
};

const statusVariants: Record<DTEStatus, "default" | "success" | "warning" | "danger" | "info"> = {
  draft: "default",
  generated: "info",
  queued: "warning",
  sent: "info",
  accepted: "success",
  partially_accepted: "warning",
  rejected: "danger",
  error: "danger"
};

export function StatusBadge({ status }: { status: DTEStatus }) {
  return <Badge variant={statusVariants[status]}>{statusLabels[status]}</Badge>;
}
