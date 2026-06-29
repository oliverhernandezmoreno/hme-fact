"use client";
import { useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plug, ShoppingCart, Store, Code, Settings } from "lucide-react";
import { IntegrationConfigModal } from "./integration-config-modal";

const INTEGRATIONS = [
  {
    id: "shopify",
    name: "Shopify",
    description: "Sincroniza órdenes automáticamente y emite boletas/facturas electrónicas.",
    icon: ShoppingCart,
    status: "active",
  },
  {
    id: "woocommerce",
    name: "WooCommerce",
    description: "Emisión automática de DTEs basada en webhooks de pedidos de WooCommerce.",
    icon: Store,
    status: "inactive",
  },
  {
    id: "mercadolibre",
    name: "Mercado Libre",
    description: "Próximamente. Integración oficial vía OAuth.",
    icon: ShoppingCart,
    status: "coming_soon",
  },
  {
    id: "pos_generic",
    name: "POS Genérico",
    description: "API optimizada para Punto de Venta con soporte offline (idempotency).",
    icon: Code,
    status: "inactive",
  },
];

export function IntegrationsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);

  const handleConfigure = (name: string) => {
    setSelectedIntegration(name);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Integration Hub</h2>
        <p className="text-muted-foreground">Conecta tu ecommerce, POS o ERP para automatizar la emisión de documentos.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {INTEGRATIONS.map((integration) => {
          const Icon = integration.icon;
          return (
            <Card key={integration.id} className="relative overflow-hidden">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  {integration.status === "active" && <Badge variant="success">Conectado</Badge>}
                  {integration.status === "inactive" && <Badge variant="default">Desconectado</Badge>}
                  {integration.status === "coming_soon" && <Badge variant="info">Próximamente</Badge>}
                </div>
                <CardTitle className="mt-4">{integration.name}</CardTitle>
                <CardDescription className="h-10 line-clamp-2">{integration.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-2">
                  <Button 
                    className="w-full" 
                    variant={integration.status === "active" ? "outline" : "default"}
                    disabled={integration.status === "coming_soon"}
                    onClick={() => handleConfigure(integration.name)}
                  >
                    {integration.status === "active" ? (
                      <>
                        <Settings className="mr-2 h-4 w-4" />
                        Configurar
                      </>
                    ) : (
                      <>
                        <Plug className="mr-2 h-4 w-4" />
                        Conectar
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <IntegrationConfigModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        integrationName={selectedIntegration}
      />
    </div>
  );
}
