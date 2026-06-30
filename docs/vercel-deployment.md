# Guía de Despliegue en Vercel para hmEfact (Frontend)

Este documento detalla los pasos para desplegar el frontend de **Next.js** en **Vercel** y conectarlo de manera exitosa con el backend alojado en **Railway**.

---

## 1. Requisitos Previos

1. Tener la URL pública de tu backend en Railway (ej. `https://hme-fact-production.up.railway.app`).
2. Una cuenta en [Vercel](https://vercel.com/) (puedes iniciar sesión con tu cuenta de GitHub).
3. El código del repositorio actualizado y subido a GitHub.

---

## 2. Configuración del Proyecto en Vercel

1. Inicia sesión en **Vercel** y haz clic en el botón **"Add New"** -> **"Project"**.
2. Selecciona tu repositorio de GitHub `hme-fact`.
3. En la pantalla de configuración del proyecto:
   * **Project Name:** Elige un nombre (ej. `hme-fact-frontend`).
   * **Framework Preset:** Selecciona **Next.js** (Vercel lo detecta automáticamente).
   * **Root Directory:** Dado que es un monorepo, haz clic en **Edit** y selecciona la carpeta **`frontend`**.

---

## 3. Variables de Entorno en Vercel

En la sección **"Environment Variables"** de la configuración de Vercel, agrega las siguientes variables de entorno para conectar tu backend de producción:

| Nombre de Variable | Valor | Descripción |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<tu-url-de-railway>.up.railway.app/api/v1` | URL base de la API del backend en Railway |
| `NEXT_PUBLIC_USE_MOCKS` | `false` | Indica al frontend que consuma la API real en lugar de datos simulados |
| `NEXT_PUBLIC_APP_NAME` | `HME Fact` | Nombre de la aplicación |
| `NEXT_PUBLIC_ENABLE_POS` | `true` | Habilita el punto de venta (opcional) |
| `NEXT_PUBLIC_ENABLE_INVENTORY`| `true` | Habilita control de inventario (opcional) |
| `NEXT_PUBLIC_ENABLE_ANALYTICS`| `true` | Habilita módulo de analíticas (opcional) |
| `NEXT_PUBLIC_ENABLE_BILLING`  | `true` | Habilita el módulo de suscripciones/billing (opcional) |
| `NEXT_PUBLIC_AUTH_COOKIE_NAME`| `hme_fact_token` | Nombre de la cookie para la sesión |

Una vez ingresadas las variables, haz clic en **Deploy**. Vercel compilará la aplicación y la publicará en cuestión de minutos, asignándote una URL del tipo `https://tu-proyecto.vercel.app`.

---

## 4. Configurar CORS en el Backend (Railway)

Para que el navegador permita al frontend de Vercel hacer peticiones al backend de Railway sin errores de CORS (Cross-Origin Resource Sharing):

1. Copia la URL que te asignó Vercel (ej. `https://hme-fact-frontend.vercel.app`).
2. Ve al panel de tu servicio del **backend** en **Railway** -> pestaña **Variables**.
3. Añade o actualiza la variable **`BACKEND_CORS_ORIGINS`** utilizando un formato de lista JSON con las URLs permitidas. Por ejemplo:
   ```json
   ["https://tu-app-de-vercel.vercel.app", "http://localhost:3000"]
   ```
4. Guarda los cambios. Railway redesplegará el backend con la nueva política de CORS activa.
