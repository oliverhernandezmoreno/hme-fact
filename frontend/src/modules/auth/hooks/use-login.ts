"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { env } from "@/lib/env";
import { useAuthStore } from "@/stores/auth-store";

import { login } from "../services/auth.service";

export function useLogin() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setSession = useAuthStore((state) => state.setSession);

  return useMutation({
    mutationFn: login,
    onSuccess: (token, variables) => {
      setSession(token.access_token, { email: variables.email });
      document.cookie = `${env.NEXT_PUBLIC_AUTH_COOKIE_NAME}=${token.access_token}; path=/; SameSite=Lax`;
      toast.success("Sesion iniciada");
      router.push(searchParams.get("next") ?? "/dashboard");
    },
    onError: () => {
      toast.error("Credenciales invalidas");
    }
  });
}
