import { LoadingSpinner } from "@/components/feedback/loading-spinner";

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <LoadingSpinner label="Cargando plataforma" />
    </div>
  );
}
