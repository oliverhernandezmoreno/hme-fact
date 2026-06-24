"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { queryKeys } from "@/services/query-keys";

import { createProduct, listProducts, updateProduct } from "../services/products.service";

export function useProducts() {
  return useQuery({
    queryKey: queryKeys.products,
    queryFn: () => listProducts({ limit: 500 })
  });
}

export function useProductMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: createProduct,
    onSuccess: () => {
      toast.success("Producto creado");
      void queryClient.invalidateQueries({ queryKey: queryKeys.products });
    }
  });

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateProduct>[1] }) =>
      updateProduct(id, payload),
    onSuccess: () => {
      toast.success("Producto actualizado");
      void queryClient.invalidateQueries({ queryKey: queryKeys.products });
    }
  });

  return { create, update };
}
