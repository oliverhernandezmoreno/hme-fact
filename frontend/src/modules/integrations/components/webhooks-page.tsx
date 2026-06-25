"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PlusCircle, Activity } from "lucide-react";
import { toast } from "sonner";

export function WebhooksPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Outbound Webhooks</h2>
          <p className="text-muted-foreground">Notifica a tus sistemas externos sobre el estado de emisión de DTEs en tiempo real.</p>
        </div>
        <Button onClick={() => toast.success("Modal de creación de Webhook simulado")}>
          <PlusCircle className="mr-2 h-4 w-4" />
          Nuevo Endpoint
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Endpoints Suscritos</CardTitle>
          <CardDescription>Tus sistemas que reciben eventos HMAC firmados por hmEFact.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Mock Webhook List */}
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-green-100 p-2 dark:bg-green-900">
                  <Activity className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm font-medium">ERP Sync (https://api.mi-erp.com/webhook/dte)</p>
                  <p className="text-xs text-muted-foreground">Eventos: dte.issued, dte.rejected</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="success">Saludable</Badge>
                <Button variant="outline" size="sm" onClick={() => toast.info("Generando firma de prueba...")}>Probar</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
