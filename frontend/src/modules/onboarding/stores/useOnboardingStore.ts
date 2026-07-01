import { create } from "zustand";
import { env } from "@/lib/env";
import { MOCK_ONBOARDING_SESSION } from "../mocks/onboardingMocks";

interface Step {
  code: string;
  title: string;
  description: string;
  component_type: string;
  status: string;
  required: boolean;
  skippable: boolean;
  can_access: boolean;
  can_complete: boolean;
  can_skip: boolean;
  blocking_reasons: string[];
  help_content?: string;
}

interface Session {
  session_id: string;
  workflow_code: string;
  status: string;
  progress_percentage: number;
  current_step_code: string;
  next_recommended_step: string;
  steps: Step[];
}

interface OnboardingState {
  session: Session | null;
  isLoading: boolean;
  error: string | null;
  loadSession: () => Promise<void>;
  completeStep: (stepCode: string, payload: any) => Promise<void>;
  setCurrentStep: (stepCode: string) => void;
}

export const useOnboardingStore = create<OnboardingState>((set, get) => ({
  session: null,
  isLoading: false,
  error: null,

  loadSession: async () => {
    set({ isLoading: true });
    // Simulate API delay
    await new Promise((r) => setTimeout(r, 800));

    if (env.NEXT_PUBLIC_USE_MOCKS) {
      set({ session: MOCK_ONBOARDING_SESSION as Session, isLoading: false });
    } else {
      // Real API call would go here
      set({ error: "Backend not connected yet", isLoading: false });
    }
  },

  setCurrentStep: (stepCode: string) => {
    const session = get().session;
    if (!session) return;
    
    // In a real app, we might also inform the backend of viewing the step
    set({ session: { ...session, current_step_code: stepCode } });
  },

  completeStep: async (stepCode: string, payload: any) => {
    // In mock mode, we manually update the state to simulate the backend Rule Engine
    if (env.NEXT_PUBLIC_USE_MOCKS) {
      const session = get().session;
      if (!session) return;

      const newSteps = session.steps.map(step => {
        if (step.code === stepCode) {
          return { ...step, status: "completed" };
        }
        // Very basic mock rule engine: unblock the next step if company_profile is completed
        if (stepCode === "company_profile" && (step.code === "tax_configuration" || step.code === "digital_certificate")) {
          return { ...step, can_access: true, status: "available", blocking_reasons: [] };
        }
        return step;
      });

      const nextStep = newSteps.find(s => s.status === "available")?.code || "first_dte";

      set({ 
        session: { 
          ...session, 
          steps: newSteps, 
          current_step_code: nextStep,
          progress_percentage: Math.min(100, session.progress_percentage + 20)
        } 
      });
    }
  }
}));
