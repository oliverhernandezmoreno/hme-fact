import { useState } from "react";
import { CheckCircle2, Copy } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

interface IntegrationConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  integrationName: string | null;
}

export function IntegrationConfigModal({ isOpen, onClose, integrationName }: IntegrationConfigModalProps) {
  const [secret, setSecret] = useState("");
  const [isCopied, setIsCopied] = useState(false);

  // Mock UUID for the connection
  const connectionId = "conn_8a7b6c5d4e3f2g1h";
  const webhookUrl = `https://api.hmefact.cl/v1/webhooks/inbound/${integrationName?.toLowerCase()}/${connectionId}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(webhookUrl);
      setIsCopied(true);
      toast.success("URL de Webhook copiada al portapapeles");
      setTimeout(() => setIsCopied(false), 2000);
    } catch (_err) {
      toast.error("No se pudo copiar la URL");
    }
  };

  const handleSave = () => {
    if (!secret.trim()) {
      toast.error("Debes ingresar el Webhook Secret proporcionado por el proveedor.");
      return;
    }
    toast.success(`Configuración de ${integrationName} guardada exitosamente.`);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Configurar {integrationName}</DialogTitle>
          <DialogDescription>
            Sigue estos pasos para conectar {integrationName} con hmEFact y automatizar tu facturación.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Paso 1: Configurar Webhook URL */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">1. Configura el Webhook en {integrationName}</h4>
            <p className="text-xs text-muted-foreground">
              Copia la siguiente URL y pégala en la sección de Webhooks de {integrationName} (Evento: Creación de Orden).
            </p>
            <div className="flex items-center space-x-2">
              <Input readOnly value={webhookUrl} className="bg-muted font-mono text-xs" />
              <Button size="icon" variant="outline" onClick={handleCopy} className="shrink-0">
                {isCopied ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* Paso 2: Ingresar Secret HMAC */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">2. Ingresa el Webhook Secret</h4>
            <p className="text-xs text-muted-foreground">
              {integrationName} te proveerá un <strong>Secret Key</strong> para firmar los webhooks. Pégalo aquí para que hmEFact pueda validar la autenticidad (HMAC-SHA256).
            </p>
            <div className="space-y-1">
              <Label htmlFor="secret">HMAC Secret</Label>
              <Input
                id="secret"
                type="password"
                placeholder="ej. whsec_abc123..."
                value={secret}
                onChange={(e) => setSecret(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-2 border-t pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={handleSave}>
            Guardar Configuración
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
