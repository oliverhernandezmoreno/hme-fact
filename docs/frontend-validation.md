# Validación Frontend hmEFact

## Estado General
El frontend de hmEFact (Fase 5) ha sido revisado, corregido y está listo para ser levantado localmente en modo `Mock`. 

### Correcciones Aplicadas
- **TypeScript:** Se corrigieron múltiples errores de tipado (más de 20 problemas relacionados con diferencias entre los mocks y las interfaces oficiales de la API: `Company`, `Customer`, `Product`, `DTE`).
- **Dependencias:** Se instalaron las dependencias correctamente (`npm install`).
- **ESLint:** Se ejecutó `npm run lint --fix` para resolver miles de warnings de Next.js y reglas de calidad del código.
- **Limpieza:** Se removieron módulos huérfanos de la caché (`.next`).
- **Componentes UI:** Se alinearon las variantes de `Badge` (ej. uso de `warning`, `info`, `danger`) con la implementación de Shadcn UI que existe en el proyecto.

### Cómo Levantar Localmente
1. Ir al directorio frontend: `cd frontend`
2. Instalar dependencias si no lo has hecho: `npm install`
3. Asegurar que existe el archivo `.env.local` con las siguientes variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_USE_MOCKS=true
   ```
4. Levantar el entorno de desarrollo:
   ```bash
   npm run dev
   ```
5. Abrir en el navegador: [http://localhost:3000](http://localhost:3000)

### Modo Mock (`NEXT_PUBLIC_USE_MOCKS=true`)
El modo mock está 100% operativo. Permite simular:
- **Autenticación:** Sesión simulada de "Admin".
- **Compañía Activa:** TechCorp Chile SpA.
- **Entidades:** Clientes, Productos, DTEs simulados.
- **Flujos:** Creación de facturas y visualización de DTEs en estado borrador, enviado o generado (con insignias/badges funcionales).
- **Dashboard y Suscripción:** Métricas de MRR, ARR, empresas activas y uso de la suscripción mensual.

### Rutas Validadas
- `/login`
- `/dashboard`
- `/customers`
- `/products`
- `/dte` (Listado)
- `/dte/create` (Crear Factura / DTE)
- `/settings`
- `/billing` (Suscripción y planes)
- `/superadmin`
- `/apikeys`

### Pendientes / Next Steps (Fase 7)
- **Integración Real:** Probar las llamadas API con el backend levantado (`NEXT_PUBLIC_USE_MOCKS=false`) para verificar CORS y el intercambio de JWT.
- **Estados PDF:** Validar la visualización/descarga del XML y PDF real para DTEs.
- **Validación Formulario:** Añadir reglas más estrictas de RUT chileno en el cliente si es necesario (ej. módulo `rut.js`).
- **MFA:** La funcionalidad de Autenticación de Dos Factores (MFA) sugerida en el dashboard de Settings requiere backend.
