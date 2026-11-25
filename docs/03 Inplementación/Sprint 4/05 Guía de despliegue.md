# Guía de despliegue a producción

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4  
**Versión del documento:** 2.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)

Esta guía explica, paso a paso y sin conocimientos previos, cómo la aplicación llega a producción y cómo configurar el servicio una sola vez. Complementa el flujo [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml).

**Estado al 17/11/2026:** el servicio `ecologistica-lima` está publicado en Render y responde en <https://ecologistica-lima.onrender.com>. Los secretos `RENDER_DEPLOY_HOOK_URL` y `PRODUCTION_URL` están cargados en GitHub y el Pull Request #4 ya se fusionó en `main`, lo que ejecutó el flujo `Deploy Production` de punta a punta en verde ([ejecución 44020768595](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768595)). Ajuste pendiente: el servicio de Render aún apunta a la rama `feature/sprint-4`; hay que cambiarla a `main` en **Settings → Build & Deploy → Branch**.

**Cambios del cierre (28/11/2026):** el `render.yaml` ahora define también una **base PostgreSQL gestionada**, la clave de cifrado de los datos personales y la comprobación de salud `/api/health/ready`. Para aplicarlos hay que seguir la sección 2.5.

**Primera ejecución real (17/11/2026), paso por paso:**

| Etapa | Duración | Qué hizo |
|---|---|---|
| Verificar antes de desplegar | 1 min 48 s | Pruebas del backend y construcción de la imagen Docker |
| Disparar el despliegue | 1 s | Llamó al Deploy Hook de Render con el secreto |
| Esperar a que la aplicación responda | 0 s | `/api/health` ya respondía (ver la limitación de la sección 3) |
| Prueba de humo en producción (Playwright) | 5 s | 3 de 3 pruebas contra la URL pública |
| **Total del trabajo "Desplegar a producción"** | **1 min 4 s** | |

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

### 2.3 Guardar los secretos en GitHub (realizado el 17/11/2026)

En GitHub: repositorio → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secreto | Valor | Para qué se usa |
|---|---|---|
| `RENDER_DEPLOY_HOOK_URL` | URL del Deploy Hook (paso 2.2) | Disparar el despliegue |
| `PRODUCTION_URL` | URL pública del servicio, sin barra final (paso 2.1) | Esperar a que responda y ejecutar la prueba de humo |

### 2.4 Comprobar

1. **Actions** → **Deploy Production** → **Run workflow** (rama `main`), o simplemente fusionar un Pull Request en `main`.
2. Todos los pasos deben quedar en verde (ver la tabla de la primera ejecución real).
3. Abrir la URL: debe verse la pantalla "Iniciar Sesión".
4. Comprobar la salud: `curl https://ecologistica-lima.onrender.com/api/health` debe devolver `{"status":"ok", ...}`.

### 2.5 Aplicar los cambios del cierre: PostgreSQL y clave de cifrado

1. En Render: servicio → **Settings → Build & Deploy → Branch** y elegir **`main`** (una vez fusionado el Pull Request del cierre).
2. En Render: **Blueprints** → el Blueprint del repositorio → **Sync** (o **Manual sync**). Render propone crear la base `ecologistica-db` y las variables `DATABASE_URL` y `DATA_ENCRYPTION_KEY`; confirmar con **Apply**. La cuenta gratuita admite **una** base PostgreSQL; si ya existe otra, créela con otro nombre o use un plan de pago.
3. Si prefiere hacerlo a mano: crear una base PostgreSQL en Render y copiar su *Internal Database URL* en la variable `DATABASE_URL` del servicio (la API acepta `postgres://` y `postgresql://`); agregar `DATA_ENCRYPTION_KEY` con un valor largo y aleatorio.
4. Esperar el despliegue y comprobar `https://ecologistica-lima.onrender.com/api/health/ready`: debe responder `{"status":"ok","db":"ok", ...}`.
5. **Guardar `DATA_ENCRYPTION_KEY` en un lugar seguro.** Si se pierde o cambia, los datos personales ya cifrados no se pueden leer (RSK-18). No la comparta ni la escriba en el repositorio.
6. **Base gratuita:** Render elimina la base PostgreSQL gratuita a los 30 días (RSK-17). Para operar de verdad hay que pasar a un plan de pago o exportar un respaldo antes de ese plazo.

## 3. Limitaciones conocidas (leer antes de presentar)

| Tema | Situación | Consecuencia | Tratamiento |
|---|---|---|---|
| Base de datos | Producción usa PostgreSQL gestionado (sección 2.5); desarrollo y pruebas usan SQLite. | Los datos sobreviven a los reinicios y despliegues. La base gratuita caduca a los 30 días. | Plan de pago para operar. `SEED_DEMO_DATA=true` carga los datos de demostración al arrancar la primera vez (es idempotente). |
| Arranque en frío | El plan gratuito se duerme tras 15 minutos sin tráfico. | La primera visita puede tardar hasta 1 minuto. | El flujo espera hasta 10 minutos a `/api/health` antes de probar. |
| Cuentas de demostración | `SEED_DEMO_DATA=true` crea usuarios con contraseñas de prueba conocidas ([`seed.py`](../../../src/backend/app/seed.py)). | Sirve para demostrar y para las pruebas E2E; **no debe usarse con datos reales**. | Con datos reales se pone `SEED_DEMO_DATA=false`. |
| Espera de arranque | Mientras Render construye la versión nueva sigue atendiendo la anterior. | Antes, la espera podía terminar con la versión anterior. | **Resuelto en el cierre:** `/api/health` informa el commit (`RENDER_GIT_COMMIT`) y el flujo espera a que coincida con el de Actions; si la plataforma no lo informa o despliega otra referencia, avisa y continúa. |
| TLS y cabeceras | Render entrega HTTPS con certificado propio. | Cumple el transporte seguro pedido en [OWASP A02](../Sprint%2003/04%20OWASP%20V_1_0_0.md). | HSTS lo aplica la plataforma. |

## 4. Variables de entorno de la aplicación

| Variable | Valor en producción | Descripción |
|---|---|---|
| `ENVIRONMENT` | `production` | Exige una `SECRET_KEY` propia y oculta `/docs` y `/openapi.json` |
| `SECRET_KEY` | generada por Render | Firma de los tokens de sesión (JWT). Nunca se versiona |
| `DATABASE_URL` | la entrega Render desde la base `ecologistica-db` | Conexión a PostgreSQL (se acepta `postgres://` y `postgresql://`) |
| `DATA_ENCRYPTION_KEY` | generada por Render | Clave de cifrado de los datos personales; guardarla fuera del repositorio |
| `SEED_DEMO_DATA` | `true` solo en demostración | Carga datos de ejemplo al arrancar |
| `NOTIFICACIONES_MODO` | `portal` (por defecto) | Con `smtp` y las variables `SMTP_*` se envían además correos |
| `PORT` | la asigna Render | Puerto de escucha del contenedor |

## 5. Alternativas

El mismo [`Dockerfile`](../../../Dockerfile) sirve para Railway, Fly.io o un servidor propio (Docker/VPS). Solo cambiaría el paso "Disparar el despliegue" de `deploy-production.yml`.

## Referencias cruzadas

- Flujos de Actions: [`ci.yml`](../../../.github/workflows/ci.yml), [`tests.yml`](../../../.github/workflows/tests.yml), [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml) y [`monitoreo.yml`](../../../.github/workflows/monitoreo.yml) (prueba de humo cada hora).
- Prueba de humo y disponibilidad: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md).
- Seguridad de la configuración: [OWASP del Sprint 3](../Sprint%2003/04%20OWASP%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Primera versión: flujo de despliegue, configuración en Render y limitaciones conocidas. |
| 1.1.0 | 17/11/2026 | Se registran el servicio publicado, los secretos cargados, la primera ejecución real con sus tiempos y la limitación de la espera de arranque. |
| 2.0.0 | 28/11/2026 | Cierre: PostgreSQL y clave de cifrado en Render (sección 2.5), espera del commit desplegado, nuevas variables de entorno y monitoreo por hora. |
