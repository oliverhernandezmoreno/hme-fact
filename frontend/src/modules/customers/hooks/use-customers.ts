"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { queryKeys } from "@/services/query-keys";

import { createCustomer, listCustomers, updateCustomer } from "../services/customers.service";

export function useCustomers() {
  return useQuery({
    queryKey: queryKeys.customers,
    queryFn: () => listCustomers({ limit: 500 })
  });
}

export function useCustomerMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: createCustomer,
    onSuccess: () => {
      toast.success("Cliente creado");
      void queryClient.invalidateQueries({ queryKey: queryKeys.customers });
    }
  });

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateCustomer>[1] }) =>
      updateCustomer(id, payload),
    onSuccess: () => {
      toast.success("Cliente actualizado");
      void queryClient.invalidateQueries({ queryKey: queryKeys.customers });
    }
  });

  return { create, update };
}
