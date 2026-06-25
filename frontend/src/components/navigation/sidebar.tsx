"use client";

import {
  BarChart3,
  Building2,
  ChevronRight,
  CreditCard,
  FileText,
  KeyRound,
  LayoutDashboard,
  ListChecks,
  Package,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

const mainNav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/companies", label: "Empresas", icon: Building2 },
  { href: "/customers", label: "Clientes", icon: Users },
  { href: "/products", label: "Productos", icon: Package },
  { href: "/dte", label: "DTE Emitidos", icon: FileText },
];

const saasNav = [
  { href: "/subscription", label: "Plan & Consumo", icon: CreditCard },
  { href: "/api-keys", label: "API Keys", icon: KeyRound },
  { href: "/onboarding", label: "Onboarding", icon: ListChecks },
];

const adminNav = [
  { href: "/superadmin", label: "SuperAdmin", icon: ShieldCheck },
  { href: "/settings", label: "Configuración", icon: Settings },
];

function NavItem({ href, label, icon: Icon }: { href: string; label: string; icon: React.ElementType }) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(href + "/");
  return (
    <Link
      href={href}
      className={cn(
        "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all",
        "text-muted-foreground hover:bg-muted hover:text-foreground",
        active && "bg-primary/10 text-primary hover:bg-primary/15 hover:text-primary"
      )}
    >
      <Icon className={cn("h-4 w-4 shrink-0 transition-transform group-hover:scale-105", active && "text-primary")} />
      <span className="truncate">{label}</span>
      {active && <ChevronRight className="ml-auto h-3 w-3 opacity-60" />}
    </Link>
  );
}

export function Sidebar() {
  const { activeCompany } = useAuthStore();

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r bg-card lg:flex">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
          O
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold leading-tight">OhmEFACT</p>
          <p className="text-xs text-muted-foreground">Facturación SaaS</p>
        </div>
      </div>

      {/* Empresa activa */}
      {activeCompany && (
        <div className="border-b px-4 py-3">
          <p className="mb-1 text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
            Empresa activa
          </p>
          <p className="truncate text-xs font-semibold">{activeCompany.legal_name}</p>
          <p className="text-[10px] text-muted-foreground">{activeCompany.rut}</p>
        </div>
      )}

      {/* Navegación */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        <p className="mb-1 px-3 text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
          Gestión
        </p>
        {mainNav.map((item) => <NavItem key={item.href} {...item} />)}

        <div className="my-3 border-t" />
        <p className="mb-1 px-3 text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
          Plataforma SaaS
        </p>
        {saasNav.map((item) => <NavItem key={item.href} {...item} />)}

        <div className="my-3 border-t" />
        <p className="mb-1 px-3 text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
          Administración
        </p>
        {adminNav.map((item) => <NavItem key={item.href} {...item} />)}
      </nav>

      {/* Footer plan */}
      <div className="border-t p-3">
        <div className="rounded-lg border bg-muted/40 p-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-primary">
            <BarChart3 className="h-3.5 w-3.5" />
            Plan PyME activo
          </div>
          <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-muted">
            <div className="h-full w-[12%] rounded-full bg-primary" />
          </div>
          <p className="mt-1 text-[10px] text-muted-foreground">6/500 DTE este mes</p>
        </div>
      </div>
    </aside>
  );
}

