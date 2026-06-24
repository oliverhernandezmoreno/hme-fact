import type { ReactNode } from "react";
import type { FieldError } from "react-hook-form";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

export function FormField({
  label,
  error,
  children,
  hint,
  className
}: {
  label: string;
  error?: FieldError | string;
  children: ReactNode;
  hint?: string;
  className?: string;
}) {
  const message = typeof error === "string" ? error : error?.message;

  return (
    <div className={cn("space-y-2", className)}>
      <Label>{label}</Label>
      {children}
      {hint && !message ? <p className="text-xs text-muted-foreground">{hint}</p> : null}
      {message ? <p className="text-xs font-medium text-destructive">{message}</p> : null}
    </div>
  );
}
