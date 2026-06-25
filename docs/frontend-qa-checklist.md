# Checklist de Calidad Frontend - hmEFact (Fase QA)

## Resumen de la Auditoría (UX/UI y Técnico)
Se ejecutó una revisión integral de la experiencia de usuario, consistencia del diseño y seguridad tipográfica en Next.js. El sistema funciona sólidamente en entorno simulado (`NEXT_PUBLIC_USE_MOCKS=true`) y se encuentra preparado para demos a prospectos comerciales (Ecommerce, POS).

### 1. Estructura y Compilación ✅
- [x] **Linting (ESLint):** Se validó que el código cumple los estándares de React Hooks y TypeScript, ajustando la sincronización de estados (ej. en modales y selectores).
- [x] **Construcción (Next.js Build):** No existen rutas rotas ni dependencias ausentes en producción.
- [x] **Limpieza de Errores React:** Se mitigaron errores críticos como "Hydration Mismatch" vinculados a la hidratación SSR de los íconos de Modo Oscuro/Claro (next-themes).

### 2. Flujos Funcionales en Modo Mocks ✅
- [x] **Login Flawless:** El flujo simula la carga y genera la cookie en modo local instantáneamente.
- [x] **Selección de Empresa:** El `CompanySwitcher` permite visualizar en el Topbar y Sidebar qué entorno fiscal está operando el usuario (rut, legal_name).
- [x] **Emisión DTE (End-to-End):**
  - Corrección mayor de usabilidad: Se implementó el control de valor estricto (`value={form.watch()}`) en Comboboxes de Cliente y Producto para evitar que perdieran estado visual al recalcular totales.
  - Generación de `Empty States` funcionales cuando las tablas están vacías.
- [x] **Integration Hub:** Las pantallas para Shopify, WooCommerce y Webhooks operan, con generación de payloads de ejemplo y URLs HMAC.

### 3. UX y Aspectos Visuales ✅
- [x] **Consistencia de Shadcn UI:** Badges de colores normalizados (Verde para Aceptado/Conectado, Outline para Borrador, Info para Novedades).
- [x] **Modales Responsivos:** Se restringió el max-height y se habilitó el overflow interno para asegurar usabilidad en pantallas pequeñas y tablets.
- [x] **Retroalimentación Constante:** Uso de `<LoadingSpinner />` en botones y uso intensivo de Toasts (`sonner`) para notificar copiado al portapapeles y acciones de guardado.

### 4. Checklist Pendiente (Próximas fases) ⏳
- [ ] Implementar la firma de los archivos XML en el frontend usando certificados (Local Cryptography).
- [ ] Incorporar validaciones dinámicas para "Nota de Crédito" obligando a referenciar el Folio de un DTE anterior.
- [ ] Testear la generación física de PDFs en el entorno Mock utilizando un generador HTML temporal.

---
**Resultado:** El frontend es altamente demostrable, robusto a fallos de cliente y escalable a los requerimientos de la Fase 8 (Firma Digital).
