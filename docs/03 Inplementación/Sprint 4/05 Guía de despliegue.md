# Guía de despliegue a producción

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4  
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)

Esta guía explica, paso a paso y sin conocimientos previos, cómo la aplicación llega a producción y cómo configurar el servicio una sola vez. Complementa el flujo [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml).

## 1. Cómo funciona el despliegue

```
 push a main  ──►  verificar (pruebas + imagen Docker)  ──►  desplegar (Deploy Hook)  ──►  esperar /api/health  ──►  prueba de humo con Playwright
 o etiqueta v*                                                       │
                                                                     └─ usa los secretos RENDER_DEPLOY_HOOK_URL y PRODUCTION_URL
```

1. Alguien fusiona una rama en `main` (o crea una etiqueta `v1.0.0`).
2. GitHub Actions ejecuta las pruebas del backend y comprueba que la imagen Docker se construye. Si algo falla, **no se despliega**.
3. Si todo pasa, el flujo llama al *Deploy Hook* del servicio en Render, que construye y publica la imagen definida en el [`Dockerfile`](../../../Dockerfile).
4. El flujo espera a que `/api/health` responda y ejecuta la prueba de humo de Playwright ([`smoke.spec.ts`](../../../src/frontend/e2e/smoke.spec.ts)) contra la URL pública.

No hay pasos manuales después de la configuración inicial. Ninguna credencial está en el código: se guardan como **GitHub Secrets** (datos cifrados que solo Actions puede leer).

## 2. Configuración inicial (se hace una vez)

> Estos pasos requieren una cuenta personal y datos secretos, por eso los realiza una persona del equipo y no el código.

### 2.1 Crear el servicio en Render

1. Entrar a <https://render.com> e iniciar sesión con la cuenta de GitHub.
2. **New +** → **Blueprint** → elegir el repositorio `EcoLogistica-Lima`. Render lee [`render.yaml`](../../../render.yaml) y propone el servicio `ecologistica-lima` (tipo Docker, plan gratuito).
3. Confirmar con **Apply**. Render genera por sí mismo la variable `SECRET_KEY` (aleatoria) y fija `ENVIRONMENT=production` y `SEED_DEMO_DATA=true`.
4. Cuando termine el primer despliegue, copiar la **URL pública** del servicio (por ejemplo `https://ecologistica-lima.onrender.com`).

### 2.2 Obtener el Deploy Hook

En Render: servicio → **Settings** → **Deploy Hook** → copiar la URL. Es secreta: quien la conozca puede disparar despliegues.

### 2.3 Guardar los secretos en GitHub

En GitHub: repositorio → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secreto | Valor | Para qué se usa |
|---|---|---|
| `RENDER_DEPLOY_HOOK_URL` | URL del Deploy Hook (paso 2.2) | Disparar el despliegue |
| `PRODUCTION_URL` | URL pública del servicio, sin barra final (paso 2.1) | Esperar a que responda y ejecutar la prueba de humo |

### 2.4 Comprobar

1. **Actions** → **Deploy Production** → **Run workflow** (rama `main`).
2. Todos los pasos deben quedar en verde. El enlace del entorno `production` muestra la URL operativa.
3. Abrir la URL: debe verse la pantalla "Iniciar Sesión".

## 3. Limitaciones conocidas (leer antes de presentar)

| Tema | Situación | Consecuencia | Tratamiento |
|---|---|---|---|
| Base de datos | El backend usa SQLite (archivo). En el plan gratuito de Render el disco es temporal. | Los datos se reinician cuando el servicio se reinicia o se vuelve a desplegar. | Por eso `SEED_DEMO_DATA=true` recarga los datos de demostración al arrancar. La migración a PostgreSQL está en el backlog y exige añadir el controlador asíncrono. |
| Arranque en frío | El plan gratuito se duerme tras 15 minutos sin tráfico. | La primera visita puede tardar hasta 1 minuto. | El flujo espera hasta 10 minutos a `/api/health` antes de probar. |
| Cuentas de demostración | `SEED_DEMO_DATA=true` crea usuarios con contraseñas de prueba conocidas ([`seed.py`](../../../src/backend/app/seed.py)). | Sirve para demostrar y para las pruebas E2E; **no debe usarse con datos reales**. | Con datos reales se pone `SEED_DEMO_DATA=false`. |
| TLS y cabeceras | Render entrega HTTPS con certificado propio. | Cumple el transporte seguro pedido en [OWASP A02](../Sprint%2003/04%20OWASP%20V_1_0_0.md). | HSTS lo aplica la plataforma. |

## 4. Variables de entorno de la aplicación

| Variable | Valor en producción | Descripción |
|---|---|---|
| `ENVIRONMENT` | `production` | Exige una `SECRET_KEY` propia y oculta `/docs` y `/openapi.json` |
| `SECRET_KEY` | generada por Render | Firma de los tokens de sesión (JWT). Nunca se versiona |
| `SEED_DEMO_DATA` | `true` solo en demostración | Carga datos de ejemplo al arrancar |
| `PORT` | la asigna Render | Puerto de escucha del contenedor |

## 5. Alternativas

El mismo [`Dockerfile`](../../../Dockerfile) sirve para Railway, Fly.io o un servidor propio (Docker/VPS). Solo cambiaría el paso "Disparar el despliegue" de `deploy-production.yml`.

## Referencias cruzadas

- Flujos de Actions: [`ci.yml`](../../../.github/workflows/ci.yml), [`tests.yml`](../../../.github/workflows/tests.yml), [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml).
- Prueba de humo y disponibilidad: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md).
- Seguridad de la configuración: [OWASP del Sprint 3](../Sprint%2003/04%20OWASP%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Primera versión: flujo de despliegue, configuración en Render y limitaciones conocidas. |
