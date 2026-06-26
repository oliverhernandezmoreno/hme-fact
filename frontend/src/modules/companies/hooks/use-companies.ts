"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { useAuthStore } from "@/stores/auth-store";
import { queryKeys } from "@/services/query-keys";

import { createCompany, listCompanies, updateCompany } from "../services/companies.service";

export function useCompanies() {
  const setActiveCompany = useAuthStore((state) => state.setActiveCompany);
  const activeCompany = useAuthStore((state) => state.activeCompany);

  return useQuery({
    queryKey: queryKeys.companies,
    queryFn: async () => {
      const companies = await listCompanies();
      const exists = companies.some((c) => c.id === activeCompany?.id);
      if ((!activeCompany || !exists) && companies[0]) {
        setActiveCompany(companies[0]);
      }
      return companies;
    }
  });
}

export function useCompanyMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: createCompany,
    onSuccess: () => {
      toast.success("Empresa creada");
      void queryClient.invalidateQueries({ queryKey: queryKeys.companies });
    }
  });

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateCompany>[1] }) =>
      updateCompany(id, payload),
    onSuccess: () => {
      toast.success("Empresa actualizada");
      void queryClient.invalidateQueries({ queryKey: queryKeys.companies });
    }
  });

  return { create, update };
}
