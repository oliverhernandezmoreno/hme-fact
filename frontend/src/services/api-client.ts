import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

import { env } from "@/lib/env";
import { useAuthStore } from "@/stores/auth-store";
import type { ApiError } from "@/types/api";

function normalizeError(error: AxiosError): ApiError {
  const payload = error.response?.data as { detail?: unknown; message?: string } | undefined;
  const detail = payload?.detail;
  const message =
    typeof detail === "string"
      ? detail
      : payload?.message ?? error.message ?? "Error de comunicacion con el backend";

  return {
    status: error.response?.status ?? 0,
    message,
    details: detail,
    retryable: error.response?.status ? error.response.status >= 500 : true
  };
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  timeout: 30_000,
  withCredentials: true,
  headers: {
    Accept: "application/json"
  }
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken, activeCompany } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  if (activeCompany?.id) {
    config.headers["X-Company-ID"] = activeCompany.id;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const normalized = normalizeError(error);
    if (normalized.status === 401) {
      useAuthStore.getState().clearSession();
      if (typeof window !== "undefined") {
        document.cookie = `${env.NEXT_PUBLIC_AUTH_COOKIE_NAME}=; Max-Age=0; path=/`;
      }
    }
    return Promise.reject(normalized);
  }
);
