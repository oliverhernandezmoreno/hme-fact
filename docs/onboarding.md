# Onboarding Empresarial — OhmEFACT Fase 6

## Wizard de 8 Pasos

| Paso | Descripción | Obligatorio |
|---|---|---|
| 1 | Datos de empresa (RUT, razón social, giro, dirección) | ✅ |
| 2 | Configuración tributaria (N° resolución SII, fecha) | ✅ |
| 3 | Certificado digital (PFX/P12) | ✅ |
| 4 | Carga de CAF (Código de Autorización de Folios) | ✅ |
| 5 | Configuración de correo (SMTP) | ⚡ Recomendado |
| 6 | Logo corporativo | ⚡ Opcional |
| 7 | Usuario administrador | ✅ |
| 8 | Validación final | ✅ |

## Endpoints

```
GET  /api/v1/onboarding                      → Progreso actual
POST /api/v1/onboarding/step/{n}             → Completar paso N con datos
POST /api/v1/onboarding/step/{n}/skip        → Saltar paso opcional
POST /api/v1/onboarding/complete             → Marcar como finalizado
```

## Ejemplo: Completar Paso 1

```bash
POST /api/v1/onboarding/step/1
X-Company-ID: <uuid>

{
  "data": {
    "legal_name": "Empresa Demo SpA",
    "fantasy_name": "DemoShop",
    "address": "Av. Providencia 1234",
    "comuna": "Providencia",
    "city": "Santiago"
  }
}

# Respuesta
{
  "step": 1,
  "completed": true,
  "is_onboarding_completed": false,
  "progress_pct": 12,
  "completed_steps": [1]
}
```

## Progreso

```json
{
  "current_step": 3,
  "total_steps": 8,
  "completed_steps": [1, 2],
  "skipped_steps": [],
  "progress_pct": 25,
  "is_completed": false,
  "next_step": 3,
  "next_step_label": "Certificado digital"
}
```

## Auto-completado

El wizard se marca automáticamente como completado cuando todos los pasos obligatorios están en `completed_steps` o `skipped_steps`.
