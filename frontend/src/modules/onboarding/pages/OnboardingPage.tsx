"use client";

import React, { useEffect } from "react";
import { OnboardingShell } from "../components/OnboardingShell";
import { useOnboardingStore } from "../stores/useOnboardingStore";

export function OnboardingPage() {
  const { loadSession, isLoading, error, session } = useOnboardingStore();

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Cargando Onboarding Engine...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="bg-destructive/10 text-destructive p-6 rounded-lg max-w-md text-center">
          <h2 className="font-bold text-lg mb-2">Error de conexión</h2>
          <p>{error}</p>
          <button 
            onClick={loadSession}
            className="mt-4 px-4 py-2 bg-destructive text-destructive-foreground rounded-md text-sm font-medium"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (!session) return null;

  return <OnboardingShell />;
}
