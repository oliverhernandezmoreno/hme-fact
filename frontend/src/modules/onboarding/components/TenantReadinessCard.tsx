"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "../stores/useOnboardingStore";
import { AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react";

export function TenantReadinessCard() {
  const router = useRouter();
  const { session, loadSession, isLoading } = useOnboardingStore();

  useEffect(() => {
    if (!session) {
      loadSession();
    }
  }, [session, loadSession]);

  if (isLoading) {
    return (
      <div className="bg-card border border-border rounded-xl p-6 shadow-sm animate-pulse">
        <div className="h-6 bg-secondary w-1/3 rounded mb-4" />
        <div className="h-4 bg-secondary w-full rounded mb-2" />
        <div className="h-4 bg-secondary w-2/3 rounded" />
      </div>
    );
  }

  // If no session found or it's 100% completed, don't render the card (unless we want to show a success message)
  if (!session || session.progress_percentage === 100) {
    return null;
  }

  const pendingSteps = session.steps.filter(s => s.status !== "completed" && s.status !== "skipped");
  const nextRecommendedStep = session.steps.find(s => s.code === session.next_recommended_step);

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/40 dark:to-indigo-950/40 border border-blue-200 dark:border-blue-900 rounded-xl p-6 shadow-sm mb-6">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <h3 className="font-semibold text-lg text-blue-900 dark:text-blue-100 flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span>Configuración de Empresa Incompleta</span>
          </h3>
          <p className="text-sm text-blue-700 dark:text-blue-300 max-w-2xl">
            Tu empresa se encuentra al {session.progress_percentage}% de configuración. 
            Para poder emitir Facturas Electrónicas (DTEs) válidas ante el SII, debes completar los pasos restantes.
          </p>
        </div>
        <div className="text-right">
          <span className="text-3xl font-bold text-blue-700 dark:text-blue-300">{session.progress_percentage}%</span>
        </div>
      </div>

      <div className="mt-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Important pending states summary */}
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center space-x-2 bg-white dark:bg-black/20 px-3 py-1.5 rounded-full border border-blue-100 dark:border-blue-800">
            {session.steps.find(s => s.code === "digital_certificate")?.status === "completed" ? (
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            ) : (
              <div className="w-2 h-2 rounded-full bg-amber-500" />
            )}
            <span className="text-blue-900 dark:text-blue-200 font-medium">Certificado Digital</span>
          </div>

          <div className="flex items-center space-x-2 bg-white dark:bg-black/20 px-3 py-1.5 rounded-full border border-blue-100 dark:border-blue-800">
            {session.steps.find(s => s.code === "caf_upload")?.status === "completed" ? (
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            ) : (
              <div className="w-2 h-2 rounded-full bg-amber-500" />
            )}
            <span className="text-blue-900 dark:text-blue-200 font-medium">Folios CAF</span>
          </div>
        </div>

        {/* Action Button */}
        <button 
          onClick={() => router.push("/onboarding")}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm whitespace-nowrap"
        >
          <span>
            {nextRecommendedStep 
              ? `Continuar: ${nextRecommendedStep.title}` 
              : "Reanudar Configuración"}
          </span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
