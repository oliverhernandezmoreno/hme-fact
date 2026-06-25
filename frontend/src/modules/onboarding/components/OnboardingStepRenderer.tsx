import React from "react";
import { useOnboardingStore } from "../stores/useOnboardingStore";
import { CompanyProfileForm } from "./forms/CompanyProfileForm";
import { TaxConfigurationForm } from "./forms/TaxConfigurationForm";
import { CertificateUploadForm } from "./forms/CertificateUploadForm";
import { CafUploadForm } from "./forms/CafUploadForm";

// Temporary mock components for rendering
const WelcomeScreen = () => <div>Pantalla de Bienvenida. Haz click en Continuar.</div>;
const FirstDteWizard = () => <div>Emisión de tu primer DTE.</div>;

export function OnboardingStepRenderer({ step }: { step: any }) {
  const { completeStep } = useOnboardingStore();

  const handleComplete = () => {
    completeStep(step.code, { simulated_data: true });
  };

  const renderComponent = () => {
    switch (step.component_type) {
      case "welcome_screen":
        return <WelcomeScreen />;
      case "company_profile_form":
        return <CompanyProfileForm stepCode={step.code} />;
      case "tax_configuration_form":
        return <TaxConfigurationForm stepCode={step.code} />;
      case "certificate_upload_form":
        return <CertificateUploadForm stepCode={step.code} />;
      case "caf_upload_form":
        return <CafUploadForm stepCode={step.code} />;
      case "first_dte_wizard":
        return <FirstDteWizard />;
      default:
        return <div>Component Type "{step.component_type}" not mapped.</div>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">{step.title}</h2>
        <p className="text-muted-foreground mt-2">{step.description}</p>
      </div>

      <div className="bg-card border border-border rounded-lg p-6 min-h-[400px]">
        {renderComponent()}
      </div>

      <div className="flex justify-end space-x-4">
        {step.skippable && (
          <button className="px-4 py-2 text-sm font-medium border border-border rounded-md hover:bg-secondary">
            Saltar este paso
          </button>
        )}
        <button 
          onClick={() => {
            // If it's a form, submit the form by clicking its hidden submit button
            const formBtn = document.getElementById(`submit-${step.code}`);
            if (formBtn) {
              formBtn.click();
            } else {
              handleComplete(); // Fallback for simple screens
            }
          }}
          className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Guardar y Continuar
        </button>
      </div>
    </div>
  );
}
