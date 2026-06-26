"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { env } from "@/lib/env";
import { MOCK_ACTIVE_COMPANY } from "@/lib/mocks";
import { useAuthStore } from "@/stores/auth-store";

import { login } from "../services/auth.service";

export function useLogin() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setSession, setActiveCompany } = useAuthStore();

  return useMutation({
    mutationFn: login,
    onSuccess: (data, variables) => {
      setSession(data.access_token, data.user ?? { email: variables.email });
      // Set active company — from mock or first company from backend
      setActiveCompany(data.company ?? (env.NEXT_PUBLIC_USE_MOCKS ? MOCK_ACTIVE_COMPANY : null));
      document.cookie = `${env.NEXT_PUBLIC_AUTH_COOKIE_NAME}=${data.access_token}; path=/; SameSite=Lax`;
      toast.success("Sesión iniciada correctamente");
      router.push(searchParams.get("next") ?? "/dashboard");
    },
    onError: () => {
      toast.error("Credenciales inválidas. Verifica e intenta de nuevo.");
    }
  });
}

