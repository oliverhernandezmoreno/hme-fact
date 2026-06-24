import type { ReactNode } from "react";

import { SaasLayout } from "@/layouts/saas-layout";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <SaasLayout>{children}</SaasLayout>;
}
