"use client";

import { Bell, Building2, Lock, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { isMockMode } from "@/lib/env";
import { useAuthStore } from "@/stores/auth-store";

export default function SettingsPage() {
  const { activeCompany, user } = useAuthStore();
  const { theme, setTheme } = useTheme();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Configuración</h1>
        <p className="text-sm text-muted-foreground">Ajustes de la plataforma, empresa y preferencias.</p>
      </div>

      {/* Empresa */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Building2 className="h-4 w-4 text-primary" /> Datos de empresa
          </CardTitle>
          <CardDescription>Información fiscal registrada en OhmEFACT</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div><label className="mb-1 block text-xs text-muted-foreground">RUT</label><Input value={activeCompany?.rut ?? ""} readOnly className="bg-muted/40" /></div>
          <div><label className="mb-1 block text-xs text-muted-foreground">Razón Social</label><Input value={activeCompany?.legal_name ?? ""} readOnly className="bg-muted/40" /></div>
          <div><label className="mb-1 block text-xs text-muted-foreground">Nombre Fantasía</label><Input value={activeCompany?.fantasy_name ?? ""} readOnly className="bg-muted/40" /></div>
          <div><label className="mb-1 block text-xs text-muted-foreground">Email</label><Input value={activeCompany?.email ?? ""} readOnly className="bg-muted/40" /></div>
          <Button className="sm:col-span-2" onClick={() => toast.info("Edición de empresa — disponible con backend activo")}>Editar datos</Button>
        </CardContent>
      </Card>

      {/* Usuario */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><Lock className="h-4 w-4 text-primary" /> Cuenta de usuario</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div><label className="mb-1 block text-xs text-muted-foreground">Email</label><Input value={user?.email ?? ""} readOnly className="bg-muted/40" /></div>
          <div><label className="mb-1 block text-xs text-muted-foreground">Nombre</label><Input value={user?.fullName ?? ""} readOnly className="bg-muted/40" /></div>
          <Button variant="outline" onClick={() => toast.info("Cambio de contraseña — disponible con backend activo")}>Cambiar contraseña</Button>
          <Button variant="outline" onClick={() => toast.info("MFA — disponible en Fase 7")}>Activar 2FA (MFA)</Button>
        </CardContent>
      </Card>

      {/* Apariencia */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><Bell className="h-4 w-4 text-primary" /> Apariencia</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Button variant={theme === "light" ? "default" : "outline"} size="sm" onClick={() => setTheme("light")}>
            <Sun className="mr-2 h-4 w-4" /> Claro
          </Button>
          <Button variant={theme === "dark" ? "default" : "outline"} size="sm" onClick={() => setTheme("dark")}>
            <Moon className="mr-2 h-4 w-4" /> Oscuro
          </Button>
          <Button variant={theme === "system" ? "default" : "outline"} size="sm" onClick={() => setTheme("system")}>Sistema</Button>
        </CardContent>
      </Card>

      {/* Status modo mock */}
      {isMockMode && (
        <div className="flex items-center gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <Badge variant="outline" className="border-amber-400 text-amber-700">MOCK MODE</Badge>
          <span>El frontend está en modo mock. Conecta el backend para habilitar cambios persistentes.</span>
        </div>
      )}
    </div>
  );
}

