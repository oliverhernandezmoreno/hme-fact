import React from "react";
import { OnboardingStepper } from "./OnboardingStepper";
import { OnboardingStepRenderer } from "./OnboardingStepRenderer";
import { useOnboardingStore } from "../stores/useOnboardingStore";

export function OnboardingShell() {
  const { session } = useOnboardingStore();

  if (!session) return null;

  const currentStep = session.steps.find(s => s.code === session.current_step_code);

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Left Sidebar Stepper */}
      <OnboardingStepper />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-y-auto relative">
        {/* Top Header */}
        <header className="h-16 border-b border-border flex items-center px-8 bg-card shrink-0">
          <h1 className="font-bold text-xl tracking-tight">hmEFACT Onboarding</h1>
          <div className="ml-auto text-sm text-muted-foreground">
            Guardado automático activado
          </div>
        </header>

        {/* Dynamic Step Content */}
        <div className="flex-1 p-8 max-w-4xl mx-auto w-full">
          {currentStep ? (
            <OnboardingStepRenderer step={currentStep} />
          ) : (
            <div>Paso no encontrado</div>
          )}
        </div>
      </div>

      {/* Right Help Panel */}
      <div className="w-80 border-l border-border bg-card p-6 h-full flex flex-col">
        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mb-4">
          Ayuda Contextual
        </h3>
        {currentStep?.help_content ? (
          <div className="prose prose-sm dark:prose-invert">
            {currentStep.help_content}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Selecciona un paso para ver la ayuda disponible.
          </p>
        )}
      </div>
    </div>
  );
}
