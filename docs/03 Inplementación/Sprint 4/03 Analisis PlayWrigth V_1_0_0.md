# Pruebas E2E y monitoreo con Playwright

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4  
**Fecha de la ejecución analizada:** 16/11/2026  
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Usabilidad](04%20Usabilidad%20V_1_0_0.md) · [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md)

## Resumen en una mirada

| Pregunta | Respuesta |
|---|---|
| ¿Qué se probó? | La aplicación completa (interfaz + API) tal como se publica: la imagen Docker de producción |
| ¿En qué navegadores? | Chromium, Firefox y WebKit (los tres motores de Playwright) más un móvil emulado (Pixel 7) |
| ¿Cuántas pruebas? | **130 ejecuciones: 130 pasan, 0 fallan (100 %)** |
| ¿Qué tan rápido responde? | API con mediana de **1,5 a 3,3 ms** (el límite es 500 ms); inicio de sesión con FCP/LCP de **35 a 56 ms** (límite 2 500 ms) |
| ¿Está disponible? | **100 % en 90 sondeos** (30 por navegador) y resiste caídas de red y errores 500 sin romperse |
| ¿Dónde se ve? | [Ejecución en GitHub Actions](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44017578661) (flujo `Tests`, con el informe HTML y las trazas como artefactos) |

## Glosario

| Término | Significado |
|---|---|
| **E2E** (*End-to-End*) | Prueba de punta a punta: un navegador real hace lo mismo que una persona (abrir la página, escribir, pulsar) |
| **Headless** | Navegador sin ventana visible, usado en servidores |
| **Web Vitals** | Métricas de Google sobre la experiencia de carga: TTFB, FCP, LCP y CLS |
| **TTFB** | Tiempo hasta que llega el primer byte de la respuesta del servidor |
| **FCP** | Primer pintado: cuándo aparece el primer texto o imagen |
| **LCP** | Pintado del contenido más grande: cuándo se ve la parte principal de la página |
| **CLS** | Cuánto se mueve el diseño mientras carga (0 = nada se mueve) |
| **Uptime** | Porcentaje de tiempo en que el sistema responde |
| **Mediana / p95** | Valor central y valor que el 95 % de las mediciones no supera |

## 1. Configuración del entorno de pruebas

### 1.1 Arquitectura de carpetas

```text
src/frontend/
├── playwright.config.ts        configuración: navegadores, reportes, tiempos
├── e2e/                        pruebas E2E (una por tema)
│   ├── datos.ts                cuentas de demostración y funciones de ayuda
│   ├── preparacion.setup.ts    inicia sesión una vez por rol y guarda la sesión
│   ├── autenticacion.spec.ts   inicio y cierre de sesión, bloqueo, validación
│   ├── vehiculos.spec.ts       US-001: alta, edición, baja, búsqueda, paginación
│   ├── pedidos.spec.ts         US-003: alta, rechazo por capacidad, cancelación
│   ├── roles.spec.ts           permisos por rol y aislamiento de bodegas
│   ├── rendimiento.spec.ts     Web Vitals y tiempos de la API
│   ├── disponibilidad.spec.ts  códigos HTTP, uptime y resiliencia ante fallas
│   ├── movil.spec.ts           diseño adaptable en un móvil emulado
│   ├── smoke.spec.ts           prueba de humo del entorno desplegado
│   └── evidencias.spec.ts      capturas de pantalla a demanda (E2E_EVIDENCIAS=1)
├── .auth/                      sesiones guardadas (ignorada por Git)
├── playwright-report/          informe HTML (ignorada por Git)
└── test-results/               resultados, métricas y trazas (ignorada por Git)
scripts/resumen_playwright.py   arma las tablas de este documento desde los resultados
docker-compose.e2e.yml          entorno local: imagen de producción + contenedor de Playwright
```

### 1.2 Navegadores evaluados

| Proyecto | Motor / dispositivo | Qué ejecuta |
|---|---|---|
| `setup` | (sin navegador) | Guarda una sesión por rol (administrador, operador y bodega) |
| `chromium` | Chrome de escritorio | Todas las pruebas de escritorio |
| `firefox` | Firefox de escritorio | Todas las pruebas de escritorio |
| `webkit` | Safari de escritorio | Todas las pruebas de escritorio |
| `movil` | Pixel 7 emulado | Diseño adaptable (WCAG 1.4.10) |
| `smoke` | Chrome de escritorio | Prueba de humo contra cualquier URL (producción) |

### 1.3 Configuración (`playwright.config.ts`)

```ts
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:8000';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,                       // cada prueba usa datos propios (sufijo aleatorio)
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.E2E_WORKERS ? Number(process.env.E2E_WORKERS) : process.env.CI ? 2 : undefined,
  timeout: 30_000,
  expect: { timeout: 7_000 },
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/resultados.json' }],
  ],
  use: {
    baseURL,
    locale: 'es-PE',
    timezoneId: 'America/Lima',
    trace: 'retain-on-failure',              // traza completa para depurar fallos
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [ /* setup, chromium, firefox, webkit, smoke y movil (ver 1.2) */ ],
});
```

Decisiones de diseño, todas siguiendo la guía de Playwright del curso:

- **Una sesión guardada por rol** (`storageState`): no se repite el inicio de sesión en cada prueba.
- **Localizadores por rol y etiqueta** (`getByRole`, `getByLabel`): se parecen a cómo una persona ve la página y resisten cambios de estilo.
- **Aserciones con espera automática** (`expect(...).toBeVisible()`): sin pausas fijas.
- **Datos únicos por prueba** (sufijo aleatorio): permite el paralelismo y que los tres navegadores usen la misma base sin pisarse.

### 1.4 Cómo se ejecuta

| Entorno | Comando |
|---|---|
| Local con Docker (misma imagen que producción) | `docker compose -f docker-compose.e2e.yml up --build --abort-on-container-exit --exit-code-from e2e` |
| Contra un sitio ya desplegado | `E2E_BASE_URL=https://<url> npx playwright test --project=smoke` |
| GitHub Actions | Flujo [`tests.yml`](../../../.github/workflows/tests.yml): construye la imagen, la levanta, instala los navegadores y ejecuta todo en modo headless; guarda `playwright-report` y `test-results` como artefactos |

## 2. Pruebas End-to-End

### 2.1 Resultados de la ejecución

Datos de la ejecución del flujo `Tests` del 16/11/2026 ([ver en Actions](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44017578661)):

| Navegador | Pruebas | Pasan | Fallan | Inestables | Éxito | Duración |
|---|---|---|---|---|---|---|
| Chromium | 41 | 41 | 0 | 0 | 100,0 % | 29 s |
| Firefox | 41 | 41 | 0 | 0 | 100,0 % | 50 s |
| WebKit | 41 | 41 | 0 | 0 | 100,0 % | 68 s |
| Móvil (Pixel 7) | 4 | 4 | 0 | 0 | 100,0 % | 2 s |
| Humo (`smoke`) | 3 | 3 | 0 | 0 | 100,0 % | 0 s |
| **Total** | **130** | **130** | **0** | **0** | **100,0 %** | |

Por tema de prueba (pasan / total):

| Archivo | Chromium | Firefox | WebKit | Móvil | Humo |
|---|---|---|---|---|---|
| `autenticacion.spec.ts` | 6/6 | 6/6 | 6/6 | — | — |
| `vehiculos.spec.ts` | 7/7 | 7/7 | 7/7 | — | — |
| `pedidos.spec.ts` | 6/6 | 6/6 | 6/6 | — | — |
| `roles.spec.ts` | 7/7 | 7/7 | 7/7 | — | — |
| `rendimiento.spec.ts` | 3/3 | 3/3 | 3/3 | — | — |
| `disponibilidad.spec.ts` | 12/12 | 12/12 | 12/12 | — | — |
| `movil.spec.ts` | — | — | — | 4/4 | — |
| `smoke.spec.ts` | — | — | — | — | 3/3 |

La rúbrica pide 100 % de éxito en los flujos críticos en los tres navegadores: se cumple. Para que el análisis sea honesto, la sección 2.4 cuenta lo que falló antes de llegar a este resultado.

### 2.2 Casos críticos cubiertos

| Tema | Casos (ruta feliz, infeliz y validación) | Historia / norma |
|---|---|---|
| **Autenticación** | El administrador entra al Dashboard; una clave incorrecta informa los intentos restantes; tres intentos fallidos bloquean la cuenta aunque luego se use la clave correcta; el formulario vacío no envía nada al servidor; una ruta protegida sin sesión redirige al inicio de sesión; cerrar sesión borra el token | EN-002, RNF-002 |
| **Vehículos** | Registrar un vehículo y verlo en la tabla; placa duplicada rechazada dentro del formulario; capacidad vacía no se envía; editar la capacidad; dar de baja solo tras confirmar y conservar el registro; búsqueda y filtro por estado en el servidor; paginación (13 vehículos, de 12 en 12) | US-001 |
| **Pedidos** | Registrar un pedido en estado PENDIENTE; peso mayor que la capacidad rechazado con mensaje claro; peso debe ser mayor que cero; cancelar solo tras confirmar y sin ofrecer cancelar dos veces; filtro por estado pedido al servidor; ayuda de coordenadas asociada a los campos | US-003 |
| **Roles** | El administrador ve el botón de alta; el operador consulta pero no modifica y la API le responde 403; la bodega solo ve sus pedidos, no puede pedir a nombre de otra y no ve la gestión de flota; el registro público no permite autoasignarse un rol de administración | RN-010, EN-002 |
| **Móvil** | El inicio de sesión cabe en pantalla y responde a toques; Dashboard, Vehículos y Pedidos no se desplazan en horizontal | WCAG 1.4.10 |

### 2.3 Código fuente relevante

**Ruta feliz de autenticación** (`autenticacion.spec.ts`):

```ts
test('ruta feliz: el administrador entra al Dashboard', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/login$/);               // sin sesión, lo envía al inicio de sesión

  await page.getByLabel('Correo electrónico').fill(USUARIOS.admin.email);
  await page.getByLabel('Contraseña').fill(USUARIOS.admin.password);
  await page.getByRole('button', { name: 'Ingresar' }).click();

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('Administrador de Flota')).toBeVisible();
});
```

**Ruta infeliz: bloqueo de cuenta** (`autenticacion.spec.ts`):

```ts
test('ruta infeliz: tres intentos fallidos bloquean la cuenta aunque luego se use la clave correcta', async ({ page, request }) => {
  const cuenta = await crearCuentaDePrueba(request);      // cuenta nueva: no afecta a otras pruebas
  await page.goto('/login');
  for (let intento = 0; intento < 3; intento++) {
    await page.getByLabel('Correo electrónico').fill(cuenta.email);
    await page.getByLabel('Contraseña').fill('clave-equivocada');
    await page.getByRole('button', { name: 'Ingresar' }).click();
    await expect(page.getByText(/Credenciales inválidas|Cuenta bloqueada/)).toBeVisible();
  }
  await page.getByLabel('Contraseña').fill(cuenta.password);
  await page.getByRole('button', { name: 'Ingresar' }).click();
  await expect(page.getByText(/Cuenta bloqueada por múltiples intentos fallidos/)).toBeVisible();
});
```

**Validación de formulario** (`pedidos.spec.ts`): comprueba que el navegador bloquea el envío y que no sale ninguna petición:

```ts
test('validación: el peso debe ser mayor que cero', async ({ page }) => {
  let altas = 0;
  page.on('request', (r) => { if (r.method() === 'POST' && r.url().includes('/api/pedidos')) altas++; });
  const dialogo = await abrirFormularioDeAlta(page);

  await dialogo.getByLabel('Peso del Paquete (kg) *').fill('0');
  await dialogo.getByRole('button', { name: 'Registrar Pedido' }).click();

  expect(await dialogo.getByLabel('Peso del Paquete (kg) *')
    .evaluate((el: HTMLInputElement) => !el.validity.valid)).toBe(true);
  expect(altas).toBe(0);
});
```

**Sesión guardada por rol** (`preparacion.setup.ts`): se inicia sesión una sola vez y las pruebas la reutilizan con `test.use({ storageState: archivoSesion('operador') })`.

### 2.4 Lo que falló antes de llegar al 100 %

Ejecutar las pruebas sobre la aplicación real destapó cinco problemas; ninguno era un defecto del sistema, sino supuestos erróneos de las pruebas o del entorno. Se documentan porque son el aprendizaje del sprint ([Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)):

| N.º | Síntoma | Causa | Corrección |
|---|---|---|---|
| 1 | Todas las pruebas de interfaz fallaban con `ERR_SSL_PROTOCOL_ERROR` | El servicio de pruebas se llamaba `app`; `.app` es un dominio con HTTPS obligatorio (HSTS) en Chromium | Renombrar el servicio a `servidor` |
| 2 | La lista vacía de pedidos no mostraba "Sin pedidos que coincidan" | Sin filtros el texto es "Sin pedidos registrados" | Ajustar el texto esperado |
| 3 | Editar la capacidad no mostraba `2.750` | El navegador formatea según la región: `2,750` | Aceptar ambos separadores |
| 4 | `/docs` no devolvía 404 en producción | Las rutas desconocidas devuelven la aplicación (200); lo oculto es Swagger | Comprobar que no aparezca Swagger ni el esquema OpenAPI |
| 5 | La cancelación fallaba en Firefox y WebKit (el localizador encontraba 2 y 4 filas) | Los tres navegadores comparten la base y el localizador solo usaba el prefijo de la dirección | Usar la dirección completa, que es única por prueba |

Además, Vitest recogía por error los archivos de `e2e/` como pruebas unitarias; se excluyó la carpeta en `vite.config.ts` (las pruebas unitarias siguen en 70 de 70).

## 3. Monitoreo de rendimiento

Las pruebas de [`rendimiento.spec.ts`](../../../src/frontend/e2e/rendimiento.spec.ts) miden con las APIs estándar del navegador (`PerformanceObserver` y *Navigation Timing*), sin herramientas externas, y guardan cada medición en `test-results/metricas/`. Los límites son los de Core Web Vitals ("bueno") y el presupuesto de 500 ms para la API que fija la rúbrica.

### 3.1 Web Vitals de la pantalla de inicio de sesión

| Navegador | TTFB | FCP | LCP | CLS | DOM cargado | Carga total | Bytes |
|---|---|---|---|---|---|---|---|
| Chromium | 6 ms | 56 ms | 56 ms | 0,000 | 16 ms | 17 ms | 4 665 |
| Firefox | 6 ms | 54 ms | 54 ms | 0,000 | 38 ms | 46 ms | 4 665 |
| WebKit | 3 ms | 35 ms | 35 ms | 0,000 | 16 ms | 21 ms | 5 034 |
| **Límite "bueno"** | **< 800 ms** | **< 1 800 ms** | **< 2 500 ms** | **< 0,1** | | | |

Los cuatro indicadores cumplen con holgura en los tres navegadores. La pantalla pesa unos 4,7 KB transferidos gracias a la compresión Brotli, el CSS incrustado y la carga diferida del JavaScript ([Informe Green IT](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md)).

### 3.2 Tiempos de respuesta de la API

Cada ruta se llama 15 veces con sesión de administrador (la de salud, sin sesión):

| Ruta | Navegador | Mediana | p95 | Máximo | Código |
|---|---|---|---|---|---|
| `/api/health` | Chromium / Firefox / WebKit | 1,5 / 2,6 / 1,6 ms | 3,4 / 4,0 / 2,6 ms | 3,4 / 4,0 / 2,6 ms | 200 |
| `/api/vehiculos/` | Chromium / Firefox / WebKit | 2,8 / 3,3 / 2,8 ms | 3,7 / 5,1 / 3,7 ms | 3,7 / 5,1 / 3,7 ms | 200 |
| `/api/pedidos/` | Chromium / Firefox / WebKit | 2,8 / 3,0 / 2,9 ms | 3,5 / 3,9 / 3,1 ms | 3,5 / 3,9 / 3,1 ms | 200 |
| `/api/vehiculos/count` | Chromium / Firefox / WebKit | 2,1 / 2,1 / 2,2 ms | 2,4 / 2,8 / 2,3 ms | 2,4 / 2,8 / 2,3 ms | 200 |
| **Límite de la rúbrica** | | **< 500 ms** | **< 800 ms** | | |

La prueba falla si cualquier ruta supera esos límites o devuelve un código distinto de 200. Además, una prueba comprueba que la API comprime con Brotli y responde **304** cuando los datos no cambiaron (cabecera `ETag`), lo que ahorra transferencia ([Green IT](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md)).

### 3.3 Cómo leer estas cifras

- **Se miden dentro de la misma máquina** (el servidor y el navegador corren juntos en el ejecutor de GitHub Actions). Por eso son mucho menores que las de un usuario real por internet: sirven para detectar regresiones de la aplicación, no para prometer esos tiempos en producción.
- **Lab frente a campo:** Lighthouse ([`green-audit.yml`](../../../.github/workflows/green-audit.yml)) simula red lenta y un procesador más lento, y mide también TBT y Speed Index; Playwright mide con la red real del entorno. No se comparan uno a uno ([guía de Lighthouse](../reduccion%20del%20impacto%20ambiental/02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md)).
- **Contra producción**, `npx playwright test --project=smoke` y el flujo `deploy-production.yml` repiten la comprobación de salud y el tiempo de la página principal (menos de 3 s) con la red real.

## 4. Disponibilidad y resiliencia

### 4.1 Códigos de estado HTTP

| Situación | Resultado esperado | Verificado |
|---|---|---|
| Página principal | 200 y `text/html` | Sí |
| `/api/health` | 200 con `{"status":"ok"}` | Sí |
| Ruta de la interfaz que no existe | 200 (entrega la aplicación) | Sí |
| Ruta de la API que no existe | 404 en JSON con `detail` | Sí |
| Datos sin sesión o con token falso | 401 | Sí |
| Cuerpo inválido (placa vacía, capacidad negativa, combustible inexistente) | 422, nunca un error del servidor | Sí |
| Cabeceras de seguridad | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer` | Sí |
| Documentación de la API en producción | Oculta (no aparece Swagger ni el esquema OpenAPI) | Sí |

### 4.2 Uptime

Cada navegador hace 30 sondeos seguidos a `/api/health`, uno cada 150 ms:

| Navegador | Sondeos | Correctos | Disponibilidad | Latencia mediana | Latencia máxima |
|---|---|---|---|---|---|
| Chromium | 30 | 30 | 100,0 % | 3,3 ms | 6,6 ms |
| Firefox | 30 | 30 | 100,0 % | 3,6 ms | 11,0 ms |
| WebKit | 30 | 30 | 100,0 % | 4,0 ms | 10,7 ms |
| **Total** | **90** | **90** | **100,0 %** | | |

### 4.3 Manejo de errores de red

Con la intercepción de red de Playwright (`page.route`) se simulan fallas y se comprueba que la pantalla **no se rompe** ni lanza errores sin controlar (`pageerror`):

| Falla simulada | Comportamiento verificado |
|---|---|
| La API de vehículos no responde (conexión abortada) | La pantalla carga y muestra el estado vacío |
| La API de pedidos responde 500 | La pantalla muestra "Sin pedidos registrados"; sin errores no controlados |
| La API de vehículos tarda 1,5 s | Se ve "Cargando catálogo de flota..." y después la tabla |
| La API de salud está caída | La barra superior informa "API sin conexión" |
| La API de salud responde | La barra superior muestra "API conectada" |

### 4.4 Prueba de humo del entorno desplegado

[`smoke.spec.ts`](../../../src/frontend/e2e/smoke.spec.ts) no necesita cuentas ni datos: comprueba que `/api/health` responde 200, que aparece "Iniciar Sesión" con el título "EcoLogística Lima", que los datos siguen protegidos (401 sin sesión) y que la página principal responde en menos de 3 s. El flujo `deploy-production.yml` la ejecuta contra la URL de producción justo después de cada despliegue ([Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md)). En la ejecución de este informe corrió contra el contenedor de pruebas (3 de 3). Comprobación manual equivalente contra producción (<https://ecologistica-lima.onrender.com>, 16/11/2026): inicio 200 en 0,67 s, `/api/health` con `status: ok` y `/api/vehiculos/` sin sesión con 401.

## 5. Informes y evidencias

| Evidencia | Dónde está |
|---|---|
| **Informe HTML de Playwright** (lista navegable de pruebas, pasos, capturas y trazas) | Artefacto `playwright-report` de la [ejecución en Actions](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44017578661); se descarga, se descomprime y se abre `index.html` (o `npx playwright show-report`) |
| Resultados en JSON y métricas por navegador | Artefacto `playwright-resultados` (`resultados.json` y `metricas/*.json`) |
| Tablas de este documento | Anotación "Resumen completo de Playwright" del trabajo E2E y resumen del flujo; se regeneran con [`resumen_playwright.py`](../../../scripts/resumen_playwright.py) |
| Capturas de las pantallas clave | `E2E_EVIDENCIAS=1 npx playwright test --project=chromium e2e/evidencias.spec.ts` genera 8 imágenes en `test-results/evidencias/` |
| Trazas y videos de fallos | Se conservan solo si una prueba falla (`retain-on-failure`) |

Los artefactos se conservan 14 días en GitHub Actions; si caducan, basta ejecutar de nuevo el flujo `Tests`.

## 6. Conclusiones y límites

- La suite cumple lo pedido: tres navegadores, flujos críticos al 100 %, métricas exactas de rendimiento por debajo de los límites, resiliencia verificada y reportes como artefactos.
- Las cifras de rendimiento son de laboratorio (servidor y navegador en la misma máquina); la medición con red real depende de contar con la URL de producción (acción 1 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)).
- El uptime de 100 % corresponde a 90 sondeos de pocos segundos; el monitoreo continuo (una prueba de humo cada hora) está planificado en la acción 8.

## Referencias cruzadas

- Historias que cubre cada prueba: [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md); tareas de usuario equivalentes: [Usabilidad, sección 1.2](04%20Usabilidad%20V_1_0_0.md).
- Requisitos: [06. Requisitos funcionales](../../01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md), [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) y [09. Reglas de negocio](../../01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_0.md) (RN-010).
- Seguridad y accesibilidad verificadas por las pruebas: [Sprint 3, OWASP](../Sprint%2003/04%20OWASP%20V_1_0_0.md) y [Sprint 3, WCAG](../Sprint%2003/05%20WCAG%20V_1_0_0.md).
- Flujos de CI/CD: [`ci.yml`](../../../.github/workflows/ci.yml), [`tests.yml`](../../../.github/workflows/tests.yml) y [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml).
- Normas y guías: Web Vitals (web.dev), WCAG 2.2 (W3C), OWASP Top 10:2025 y las guías del curso "Automatización Web Moderna con Playwright" y "Dominando Google Lighthouse".

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Primera versión: configuración, 130 ejecuciones E2E en tres navegadores y móvil, Web Vitals, tiempos de la API, uptime y resiliencia. |
