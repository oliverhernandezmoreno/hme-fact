"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { queryKeys } from "@/services/query-keys";

import { createDTE, getDTEStatus, listDTE, sendDTE, downloadDTEPdf } from "../services/dte.service";

export function useDTEList() {
  return useQuery({
    queryKey: queryKeys.dtes,
    queryFn: () => listDTE({ limit: 500 })
  });
}

export function useDTEMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: createDTE,
    onSuccess: () => {
      toast.success("DTE creado");
      void queryClient.invalidateQueries({ queryKey: queryKeys.dtes });
    }
  });

  const send = useMutation({
    mutationFn: sendDTE,
    onSuccess: (status) => {
      toast.success(`DTE enviado: ${status.provider_status ?? status.status}`);
      void queryClient.invalidateQueries({ queryKey: queryKeys.dtes });
    }
  });

  const refreshStatus = useMutation({
    mutationFn: getDTEStatus,
    onSuccess: (status) => {
      toast.success(`Estado tributario: ${status.provider_status ?? status.status}`);
      void queryClient.invalidateQueries({ queryKey: queryKeys.dtes });
    }
  });

  const downloadPdf = useMutation({
    mutationFn: ({ id, folio }: { id: string; folio: number }) => downloadDTEPdf(id, folio),
    onError: (err: any) => {
      toast.error(err.message || "Error al descargar el PDF");
    }
  });

  return { create, send, refreshStatus, downloadPdf };
}
