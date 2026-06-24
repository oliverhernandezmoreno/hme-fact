import { LoginForm } from "@/modules/auth/components/login-form";

export default function LoginPage() {
  return (
    <main className="grid min-h-screen grid-cols-1 bg-background lg:grid-cols-[1fr_460px]">
      <section className="hidden bg-[radial-gradient(circle_at_20%_20%,rgba(14,116,144,0.18),transparent_32%),linear-gradient(135deg,#052f3d,#0f766e)] p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="text-lg font-semibold">HME Fact</div>
        <div>
          <p className="text-sm uppercase tracking-wide text-white/70">SaaS tributario</p>
          <h1 className="mt-3 max-w-2xl text-4xl font-semibold leading-tight">
            Facturacion electronica chilena para operaciones exigentes.
          </h1>
          <p className="mt-4 max-w-xl text-white/75">
            Multiempresa, SII-ready y preparada para ecommerce, POS e integraciones ERP.
          </p>
        </div>
      </section>
      <section className="flex items-center justify-center p-6">
        <LoginForm />
      </section>
    </main>
  );
}
