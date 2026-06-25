import React, { useState } from "react";
import { useOnboardingStore } from "../../stores/useOnboardingStore";
import { UploadCloud, FileCode2, CheckCircle2 } from "lucide-react";

export function CafUploadForm({ stepCode }: { stepCode: string }) {
  const { completeStep } = useOnboardingStore();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [parsedData, setParsedData] = useState<any>(null); // To mock the parsing response

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Debes seleccionar el archivo XML del CAF");
      return;
    }
    setError("");
    
    // In a real application, we would create a FormData object and POST it to /api/v1/caf/upload
    // Here we simulate the backend parsing logic and response
    setTimeout(() => {
      setSuccess(true);
      setParsedData({
        dte_type: 33, // Factura Electrónica
        folio_from: 1,
        folio_to: 100
      });
      // Complete step in the state machine
      completeStep(stepCode, { fileName: file.name, parsed: true });
    }, 800);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (selected.name.toLowerCase().endsWith(".xml")) {
        setFile(selected);
        setError("");
        setSuccess(false);
      } else {
        setFile(null);
        setError("Formato inválido. El CAF debe ser un archivo .xml descargado del SII.");
      }
    }
  };

  return (
    <form id={`form-${stepCode}`} onSubmit={handleSubmit} className="space-y-6">
      
      <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-300">Precaución de Seguridad</h4>
        <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
          El archivo CAF contiene la Llave Privada de autorización. 
          Nunca compartas este archivo por correo ni WhatsApp. Súbelo directamente desde el portal del SII a hmEFACT.
        </p>
      </div>

      <div className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-colors cursor-pointer relative ${
        success ? "border-green-500 bg-green-50 dark:bg-green-900/20" : "border-border bg-secondary/20 hover:bg-secondary/40"
      }`}>
        <input 
          type="file" 
          accept=".xml" 
          onChange={handleFileChange}
          className="absolute inset-0 opacity-0 cursor-pointer" 
          disabled={success}
        />
        
        {success ? (
          <>
            <CheckCircle2 className="w-12 h-12 text-green-500 mb-4" />
            <h4 className="font-medium text-lg text-green-700 dark:text-green-400">CAF Procesado Correctamente</h4>
            {parsedData && (
              <div className="mt-4 flex space-x-4 text-sm font-medium">
                <span className="bg-background px-3 py-1 rounded shadow-sm">DTE: {parsedData.dte_type}</span>
                <span className="bg-background px-3 py-1 rounded shadow-sm">Rango: {parsedData.folio_from} - {parsedData.folio_to}</span>
              </div>
            )}
          </>
        ) : file ? (
          <>
            <FileCode2 className="w-12 h-12 text-primary mb-4" />
            <p className="font-medium text-lg">{file.name}</p>
            <p className="text-sm text-muted-foreground mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </>
        ) : (
          <>
            <UploadCloud className="w-12 h-12 text-muted-foreground mb-4" />
            <h4 className="font-medium text-lg">Sube el XML de Folios</h4>
            <p className="text-sm text-muted-foreground mt-2 max-w-sm">
              Arrastra aquí el archivo .xml que descargaste desde la plataforma del SII.
            </p>
          </>
        )}
      </div>

      {error && <div className="text-sm font-medium text-destructive">{error}</div>}

      <button type="submit" id={`submit-${stepCode}`} className="hidden">Guardar</button>
    </form>
  );
}
