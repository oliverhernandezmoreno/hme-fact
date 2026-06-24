"use client";

import { Building2 } from "lucide-react";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useCompanies } from "@/modules/companies/hooks/use-companies";
import { useAuthStore } from "@/stores/auth-store";

export function CompanySwitcher() {
  const { data: companies = [] } = useCompanies();
  const activeCompany = useAuthStore((state) => state.activeCompany);
  const setActiveCompany = useAuthStore((state) => state.setActiveCompany);

  return (
    <div className="flex min-w-0 items-center gap-2">
      <Building2 className="h-4 w-4 text-muted-foreground" />
      <Select
        value={activeCompany?.id}
        onValueChange={(id) => setActiveCompany(companies.find((company) => company.id === id) ?? null)}
      >
        <SelectTrigger className="w-[220px]">
          <SelectValue placeholder="Seleccionar empresa" />
        </SelectTrigger>
        <SelectContent>
          {companies.map((company) => (
            <SelectItem key={company.id} value={company.id}>
              {company.fantasy_name || company.legal_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
