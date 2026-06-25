import React from "react";
import { useOnboardingStore } from "../stores/useOnboardingStore";
import { CheckCircle2, Circle, Lock } from "lucide-react";

export function OnboardingStepper() {
  const { session, setCurrentStep } = useOnboardingStore();

  if (!session) return null;

  return (
    <div className="w-64 border-r border-border bg-card p-6 h-full flex flex-col space-y-6">
      <div>
        <h3 className="font-semibold text-lg">Tu Progreso</h3>
        <div className="w-full bg-secondary h-2 rounded-full mt-2">
          <div 
            className="bg-primary h-2 rounded-full transition-all duration-500" 
            style={{ width: `${session.progress_percentage}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground mt-1">{session.progress_percentage}% Completado</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4">
        {session.steps.map((step, index) => {
          const isActive = session.current_step_code === step.code;
          const isCompleted = step.status === "completed";
          const isBlocked = !step.can_access;

          return (
            <div 
              key={step.code} 
              className={`flex flex-col space-y-1 ${isActive ? "opacity-100" : "opacity-60"} ${isBlocked ? "cursor-not-allowed" : "cursor-pointer"}`}
              onClick={() => {
                if (!isBlocked) setCurrentStep(step.code);
              }}
            >
              <div className="flex items-center space-x-3">
                {isCompleted ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                ) : isBlocked ? (
                  <Lock className="w-5 h-5 text-muted-foreground" />
                ) : isActive ? (
                  <div className="w-5 h-5 rounded-full border-2 border-primary bg-primary/20" />
                ) : (
                  <Circle className="w-5 h-5 text-muted-foreground" />
                )}
                <span className={`text-sm ${isActive ? "font-semibold text-foreground" : "text-muted-foreground"}`}>
                  {step.title}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
