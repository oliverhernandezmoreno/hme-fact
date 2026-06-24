export const queryKeys = {
  dashboard: ["dashboard"] as const,
  companies: ["companies"] as const,
  customers: ["customers"] as const,
  products: ["products"] as const,
  dtes: ["dte"] as const,
  dte: (id: string) => ["dte", id] as const
};
