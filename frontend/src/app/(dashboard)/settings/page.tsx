import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Configuracion</h1>
        <p className="text-sm text-muted-foreground">Base para roles, sucursales, POS y billing SaaS.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Roadmap operacional</CardTitle>
          <CardDescription>Preparado para modulos futuros sin acoplar la operacion actual.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {["Multi-sucursal", "POS", "Inventario", "Analytics", "Roles avanzados", "Marketplace"].map((item) => (
            <div key={item} className="rounded-lg border p-4 text-sm font-medium">
              {item}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
