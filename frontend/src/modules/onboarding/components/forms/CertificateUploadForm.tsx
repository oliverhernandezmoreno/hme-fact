import React, { useState } from "react";
import { useOnboardingStore } from "../../stores/useOnboardingStore";
import { UploadCloud, FileType2, Key } from "lucide-react";

export function CertificateUploadForm({ stepCode }: { stepCode: string }) {
  const { completeStep } = useOnboardingStore();
  const [file, setFile] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Debes seleccionar un archivo .pfx o .p12");
      return;
    }
    if (!password) {
      setError("La contraseña del certificado es obligatoria");
      return;
    }
    setError("");
    
    // In a real app we'd use FormData to POST /api/v1/certificates/upload
    // For now we mock the state completion
    await completeStep(stepCode, { fileName: file.name, passwordLength: password.length });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (selected.name.endsWith(".p12") || selected.name.endsWith(".pfx")) {
        setFile(selected);
        setError("");
      } else {
        setFile(null);
        setError("Formato inválido. Solo se permiten archivos .p12 o .pfx");
      }
    }
  };

  return (
    <form id={`form-${stepCode}`} onSubmit={handleSubmit} className="space-y-6">
      
      {/* Drag & Drop Area */}
      <div className="border-2 border-dashed border-border rounded-xl p-10 flex flex-col items-center justify-center text-center bg-secondary/20 hover:bg-secondary/40 transition-colors cursor-pointer relative">
        <input 
          type="file" 
          accept=".pfx,.p12" 
          onChange={handleFileChange}
          className="absolute inset-0 opacity-0 cursor-pointer" 
        />
        {file ? (
          <>
            <FileType2 className="w-12 h-12 text-primary mb-4" />
            <p className="font-medium text-lg">{file.name}</p>
            <p className="text-sm text-muted-foreground mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </>
        ) : (
          <>
            <UploadCloud className="w-12 h-12 text-muted-foreground mb-4" />
            <h4 className="font-medium text-lg">Sube tu Certificado Digital</h4>
            <p className="text-sm text-muted-foreground mt-2 max-w-sm">
              Arrastra aquí tu archivo .p12 o .pfx emitido por E-Sign, Acepta, Paperless u otro proveedor acreditado.
            </p>
          </>
        )}
      </div>

      <div className="space-y-2 max-w-md">
        <label className="text-sm font-medium flex items-center space-x-2">
          <Key className="w-4 h-4" /> 
          <span>Contraseña del Certificado</span>
        </label>
        <input 
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="********" 
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
        />
        <p className="text-xs text-muted-foreground mt-1">
          La contraseña será encriptada con AES-256 GCM.
        </p>
      </div>

      {error && <div className="text-sm font-medium text-destructive">{error}</div>}

      <button type="submit" id={`submit-${stepCode}`} className="hidden">Guardar</button>
    </form>
  );
}
