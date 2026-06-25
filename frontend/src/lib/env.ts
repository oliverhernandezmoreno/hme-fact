import { z } from "zod";

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().default("http://localhost:8000/api/v1"),
  NEXT_PUBLIC_APP_NAME: z.string().default("hmEFact"),
  NEXT_PUBLIC_AUTH_COOKIE_NAME: z.string().default("ohmefact_token"),
  NEXT_PUBLIC_USE_MOCKS: z.coerce.boolean().default(false),
  NEXT_PUBLIC_ENABLE_POS: z.coerce.boolean().default(false),
  NEXT_PUBLIC_ENABLE_INVENTORY: z.coerce.boolean().default(false),
  NEXT_PUBLIC_ENABLE_ANALYTICS: z.coerce.boolean().default(true),
  NEXT_PUBLIC_ENABLE_BILLING: z.coerce.boolean().default(true),
});

export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  NEXT_PUBLIC_AUTH_COOKIE_NAME: process.env.NEXT_PUBLIC_AUTH_COOKIE_NAME,
  NEXT_PUBLIC_USE_MOCKS: process.env.NEXT_PUBLIC_USE_MOCKS,
  NEXT_PUBLIC_ENABLE_POS: process.env.NEXT_PUBLIC_ENABLE_POS,
  NEXT_PUBLIC_ENABLE_INVENTORY: process.env.NEXT_PUBLIC_ENABLE_INVENTORY,
  NEXT_PUBLIC_ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS,
  NEXT_PUBLIC_ENABLE_BILLING: process.env.NEXT_PUBLIC_ENABLE_BILLING,
});

export const isMockMode = env.NEXT_PUBLIC_USE_MOCKS;
