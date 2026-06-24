"use client";

import { LogOut, Menu, Moon, Search, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { usePathname, useRouter } from "next/navigation";

import { CompanySwitcher } from "@/components/navigation/company-switcher";
import { Button } from "@/components/ui/button";
import { env } from "@/lib/env";
import { useAuthStore } from "@/stores/auth-store";

export function Topbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const clearSession = useAuthStore((state) => state.clearSession);
  const user = useAuthStore((state) => state.user);

  const crumbs = pathname
    .split("/")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1));

  function logout() {
    clearSession();
    document.cookie = `${env.NEXT_PUBLIC_AUTH_COOKIE_NAME}=; Max-Age=0; path=/`;
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background/95 px-4 backdrop-blur md:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <Button variant="ghost" size="icon" className="lg:hidden">
          <Menu className="h-5 w-5" />
        </Button>
        <div className="hidden text-sm text-muted-foreground md:block">
          {crumbs.length ? crumbs.join(" / ") : "Dashboard"}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="hidden lg:block">
          <CompanySwitcher />
        </div>
        <Button variant="ghost" size="icon">
          <Search className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
        <div className="hidden rounded-md border px-3 py-2 text-sm md:block">
          {user?.email ?? "Usuario"}
        </div>
        <Button variant="ghost" size="icon" onClick={logout}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
