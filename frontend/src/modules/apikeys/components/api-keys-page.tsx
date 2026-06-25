"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Copy, Eye, EyeOff, Key, Plus, RefreshCw, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Skeleton } from "@/components/feedback/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { createAPIKey, listAPIKeys, revokeAPIKey, rotateAPIKey } from "@/modules/apikeys/services/api-keys.service";

const VALID_SCOPES = ["read", "write", "dte", "customers", "products"] as const;

function RawKeyDisplay({ rawKey }: { rawKey: string }) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="rounded-lg border bg-muted/50 p-4">
      <p className="mb-2 flex items-center gap-2 text-sm font-medium text-amber-600">
        <AlertTriangle className="h-4 w-4" /> Guarda esta clave — no se mostrará de nuevo
      </p>
      <div className="flex items-center gap-2">
        <code className="flex-1 break-all rounded bg-background px-3 py-2 font-mono text-xs">
          {visible ? rawKey : rawKey.slice(0, 12) + "•".repeat(20)}
        </code>
        <Button variant="ghost" size="icon" onClick={() => setVisible((v) => !v)}>
          {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </Button>
        <Button variant="ghost" size="icon" onClick={() => { navigator.clipboard.writeText(rawKey); toast.success("Copiada"); }}>
          <Copy className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

export function APIKeysPage() {
  const qc = useQueryClient();
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyScopes, setNewKeyScopes] = useState<string[]>(["read", "dte", "customers"]);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: listAPIKeys,
  });

  const createMut = useMutation({
    mutationFn: () => createAPIKey(newKeyName, newKeyScopes),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["api-keys"] });
      setGeneratedKey(data.raw_key);
      setNewKeyName("");
      setCreating(false);
      toast.success("API Key generada");
    },
    onError: () => toast.error("Error al generar la API Key"),
  });

  const revokeMut = useMutation({
    mutationFn: revokeAPIKey,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["api-keys"] }); toast.success("API Key revocada"); },
    onError: () => toast.error("Error al revocar la API Key"),
  });

  const rotateMut = useMutation({
    mutationFn: rotateAPIKey,
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["api-keys"] });
      setGeneratedKey(data.raw_key);
      toast.success("API Key rotada");
    },
    onError: () => toast.error("Error al rotar la API Key"),
  });

  const activeKeys = keys.filter((k) => k.is_active);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">API Keys</h1>
          <p className="text-sm text-muted-foreground">Gestiona claves de acceso para integraciones externas.</p>
        </div>
        <Button onClick={() => setCreating(true)}>
          <Plus className="mr-2 h-4 w-4" /> Nueva API Key
        </Button>
      </div>

      {/* Raw key display (post-generation) */}
      {generatedKey && (
        <Card>
          <CardHeader><CardTitle className="text-base">🎉 API Key generada</CardTitle></CardHeader>
          <CardContent>
            <RawKeyDisplay rawKey={generatedKey} />
            <Button className="mt-3 w-full" variant="outline" onClick={() => setGeneratedKey(null)}>
              Entendido, cerrar
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Form crear key */}
      {creating && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Nueva API Key</CardTitle>
            <CardDescription>Selecciona el nombre y los scopes de acceso.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Nombre</label>
              <Input
                placeholder="Ej: Integración ERP, WooCommerce..."
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium">Scopes de acceso</label>
              <div className="flex flex-wrap gap-2">
                {VALID_SCOPES.map((scope) => (
                  <label key={scope} className="flex cursor-pointer items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm hover:bg-muted">
                    <input
                      type="checkbox"
                      checked={newKeyScopes.includes(scope)}
                      onChange={(e) =>
                        setNewKeyScopes(e.target.checked ? [...newKeyScopes, scope] : newKeyScopes.filter((s) => s !== scope))
                      }
                    />
                    {scope}
                  </label>
                ))}
              </div>
            </div>
            <div className="flex gap-2">
              <Button disabled={!newKeyName || createMut.isPending} onClick={() => createMut.mutate()}>
                {createMut.isPending ? "Generando..." : "Generar"}
              </Button>
              <Button variant="outline" onClick={() => setCreating(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Listado de keys */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Key className="h-4 w-4 text-primary" /> Claves activas ({activeKeys.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : keys.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              No hay API Keys. Genera la primera para integrar sistemas externos.
            </div>
          ) : (
            <div className="space-y-3">
              {keys.map((key) => (
                <div
                  key={key.id}
                  className={`flex items-center justify-between gap-4 rounded-lg border p-4 ${!key.is_active ? "opacity-50" : ""}`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate font-medium text-sm">{key.name}</p>
                      <Badge variant={key.is_active ? "default" : "warning"} className="text-xs">
                        {key.is_active ? "Activa" : "Revocada"}
                      </Badge>
                    </div>
                    <code className="text-xs text-muted-foreground">{key.prefix}••••••••</code>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {key.scopes.map((s) => (
                        <Badge key={s} variant="info" className="text-[10px]">{s}</Badge>
                      ))}
                    </div>
                    <p className="mt-1 text-[10px] text-muted-foreground">
                      {key.last_used_at ? `Último uso: ${new Date(key.last_used_at).toLocaleString("es-CL")}` : "Nunca usada"}
                      {key.expires_at ? ` · Expira: ${new Date(key.expires_at).toLocaleDateString("es-CL")}` : ""}
                    </p>
                  </div>
                  {key.is_active && (
                    <div className="flex shrink-0 gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => rotateMut.mutate(key.id)}
                        disabled={rotateMut.isPending}
                      >
                        <RefreshCw className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => revokeMut.mutate(key.id)}
                        disabled={revokeMut.isPending}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
