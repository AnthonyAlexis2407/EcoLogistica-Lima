import { defineConfig, devices } from '@playwright/test';

/**
 * Pruebas End-to-End de EcoLogística Lima (Sprint 4).
 *
 * La aplicación bajo prueba es la imagen de producción: FastAPI sirviendo el frontend compilado.
 * - Local o CI: `E2E_BASE_URL` por defecto `http://localhost:8000`.
 * - Entorno desplegado: `E2E_BASE_URL=https://<url-de-produccion> npm run e2e:smoke`.
 *
 * Proyectos: una preparación de sesiones (`setup`) y los tres motores de navegador de Playwright
 * (Chromium, Firefox y WebKit), más una emulación de móvil para la prueba de diseño adaptable.
 */
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:8000';

// Las capturas de evidencia (e2e/evidencias.spec.ts) solo se ejecutan a demanda con E2E_EVIDENCIAS=1.
const ignorarEscritorio = process.env.E2E_EVIDENCIAS === '1' ? /(movil|smoke|rutas|conductor)\.spec\.ts/ : /(movil|smoke|rutas|conductor|evidencias)\.spec\.ts/;

export default defineConfig({
  testDir: './e2e',
  // Cada prueba usa datos únicos (sufijo aleatorio), por eso pueden correr en paralelo.
  fullyParallel: true,
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
    // El service worker de la PWA cachea navegaciones y solapa la intercepción de red (page.route) en WebKit;
    // solo pwa.spec.ts y conductor.spec.ts lo necesitan y lo habilitan por archivo.
    serviceWorkers: 'block',
    // Evidencias para depurar fallos con el Trace Viewer.
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: /preparacion\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
      testIgnore: ignorarEscritorio,
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
      testIgnore: ignorarEscritorio,
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
      testIgnore: ignorarEscritorio,
    },
    // Prueba de humo del entorno desplegado: no depende de cuentas ni de la preparación de sesiones.
    {
      name: 'smoke',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /smoke\.spec\.ts/,
    },
    // Rutas (RF-003) y conductor (RF-004): optimizar toma todos los pedidos pendientes de la base compartida y ambos
    // archivos limpian rutas y pedidos, por eso cada archivo es su propio proyecto y todos corren en cadena (uno a la vez),
    // solo cuando terminaron los demás.
    {
      name: 'rutas-chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup', 'chromium', 'firefox', 'webkit'],
      testMatch: /rutas\.spec\.ts/,
    },
    {
      name: 'conductor-chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['rutas-chromium'],
      testMatch: /conductor\.spec\.ts/,
    },
    {
      name: 'rutas-firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['conductor-chromium'],
      testMatch: /rutas\.spec\.ts/,
    },
    {
      name: 'conductor-firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['rutas-firefox'],
      testMatch: /conductor\.spec\.ts/,
    },
    {
      name: 'rutas-webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['conductor-firefox'],
      testMatch: /rutas\.spec\.ts/,
    },
    {
      name: 'conductor-webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['rutas-webkit'],
      testMatch: /conductor\.spec\.ts/,
    },
    {
      name: 'movil',
      use: { ...devices['Pixel 7'] },
      dependencies: ['setup'],
      testMatch: /movil\.spec\.ts/,
    },
  ],
});
