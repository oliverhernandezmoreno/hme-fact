import { DashboardOverview } from "@/modules/dashboard/components/dashboard-overview";
import { TenantReadinessCard } from "@/modules/onboarding/components/TenantReadinessCard";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <TenantReadinessCard />
      <DashboardOverview />
    </div>
  );
}
