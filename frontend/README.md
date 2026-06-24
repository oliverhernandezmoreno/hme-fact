# HME Fact Frontend

Frontend SaaS enterprise para facturacion electronica chilena compatible con el backend FastAPI.

## Arquitectura

- `src/app`: rutas Next.js App Router, layouts, loading y error boundaries.
- `src/modules`: modulos de negocio por dominio: auth, companies, customers, products, dte y dashboard.
- `src/services`: cliente API centralizado, interceptors y query keys.
- `src/stores`: estado cliente con Zustand.
- `src/components`: UI reusable, tablas, feedback, forms y navegacion.
- `src/lib`: utilidades transversales, environment parsing y helpers.

## Estado

- Server state: TanStack Query para cache, revalidacion, mutaciones y optimistic-ready workflows.
- Client state: Zustand solo para sesion JWT, usuario y empresa activa.

## Backend

El cliente API apunta a `NEXT_PUBLIC_API_URL` y agrega automaticamente:

- `Authorization: Bearer <token>`
- `X-Company-ID: <activeCompany.id>`

## Comandos

```bash
npm install
npm run dev
npm run typecheck
npm run lint
npm run test
```

## Variables

Copiar `.env.example` a `.env.local` y ajustar `NEXT_PUBLIC_API_URL` si el backend no corre en `localhost:8000`.
