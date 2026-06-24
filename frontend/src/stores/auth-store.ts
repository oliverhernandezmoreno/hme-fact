"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { Company } from "@/modules/companies/types";

export type AuthUser = {
  id?: string;
  email: string;
  fullName?: string;
};

type AuthState = {
  accessToken: string | null;
  user: AuthUser | null;
  activeCompany: Company | null;
  setSession: (token: string, user: AuthUser) => void;
  setActiveCompany: (company: Company | null) => void;
  clearSession: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      activeCompany: null,
      setSession: (accessToken, user) => set({ accessToken, user }),
      setActiveCompany: (activeCompany) => set({ activeCompany }),
      clearSession: () => set({ accessToken: null, user: null, activeCompany: null })
    }),
    {
      name: "hme-fact-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
        activeCompany: state.activeCompany
      })
    }
  )
);
