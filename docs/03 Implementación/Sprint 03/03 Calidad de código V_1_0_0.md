# Evaluación de Calidad de Código — SonarQube

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha de Análisis:** 2026-10-21 (nueva medición con SonarQube 26.10 sobre las 36 pruebas del backend y las 60 del frontend)  
**Versión del Análisis:** V_1_0_0 (documento 1.2.0)

[← Volver al README Principal](../../../README.md)

**Alcance:** código de `src` (backend FastAPI en Python y frontend React/TypeScript), 2 721 líneas de código medidas el 21/10/2026. Herramienta: SonarQube Community (imagen `sonarqube:community`) con el scanner `sonar-scanner-cli`, proyecto `ecologistica-lima`. La configuración está en [`sonar-project.properties`](../../../sonar-project.properties) y excluye `seed.py` (script de datos de prueba).

## 1. Resumen Ejecutivo de Quality Gate

- **Estado del Quality Gate:** PASSED (compuerta "Sonar way": estado OK; al ser la primera ejecución en una instancia nueva no hay código nuevo, así que la compuerta no tiene condiciones incumplidas; las métricas globales se reportan abajo)
- **Porcentaje de Cobertura de Pruebas (Coverage):** 92,7 % global (94,5 % de líneas), medido por SonarQube con los informes de `pytest` y Vitest
- **Duplicación de Código:** 2,2 % (6 bloques duplicados)

Detalle de la cobertura por capa, según las herramientas de cada una:

| Capa | Pruebas | Cobertura | Herramienta |
|---|---|---|---|
| Backend (`app/`, sin `seed.py`) | 36 pasan | 86 % | `pytest --cov` |
| Frontend (`src/`) | 60 pasan | 94,4 % de líneas | Vitest 5 + v8 |

El Quality Gate estándar solo evalúa código nuevo; por eso se reporta además la cobertura global, que es la que exige el DoD del proyecto (≥ 80 %).

## 2. Métricas Principales

| Categoría | Cantidad Detectada | Severidad (Bloqueante / Alta / Media / Baja) |
|---|---|---|
| Bugs | 0 (primer análisis: 7) | Alta (los 7 iniciales eran de severidad MAJOR) |
| Vulnerabilidades | 0 | — |
| Code Smells | 0 (primer análisis: 4) | Media (los 4 iniciales eran de severidad MAJOR) |
| Security Hotspots | 0 | — |

Calificaciones de Sonar: fiabilidad A, seguridad A, mantenibilidad A, revisión de seguridad A.

## 3. Plan de Remediación y Deuda Técnica

- **Deuda Técnica Estimada:** 0 min (primer análisis: 20 min)
- **Principales hallazgos y acciones correctivas:**
  1. **7 bugs `typescript:S9383` (promesas sin esperar ni capturar errores)** en `AuthContext.tsx` (1), `PedidosPage.tsx` (3) y `VehiculosPage.tsx` (3). Un error de red al recargar la lista o verificar el token podía quedar sin manejar. **Corrección aplicada:** `await load()` dentro de los bloques `try/catch` y `void` en los `useEffect` y en `verifyToken()`.
  2. **4 code smells `typescript:S6848` (elementos no nativos con manejador de clic)** en los modales de `PedidosPage.tsx` y `VehiculosPage.tsx`. **Corrección aplicada:** el fondo del modal lleva `role="presentation"` y el cuadro `role="dialog" aria-modal="true"`. Esto mejora además la accesibilidad (ver documento 05).
  3. **Cobertura inicial de 65 % global.** El backend estaba en 72 % y el frontend sin pruebas. **Corrección aplicada:** 17 pruebas nuevas de routers en el backend (de 16 a 36) y 60 pruebas con Vitest en el frontend; la cobertura global pasó a 92,7 %.
  4. **Informe de cobertura del backend ignorado por Sonar (0 %).** `coverage.xml` usaba rutas absolutas. **Corrección aplicada:** `.coveragerc` con `relative_files = True` y ejecución de `pytest` desde la raíz del repositorio.
  5. **Dependencias de desarrollo con vulnerabilidades conocidas** (`npm audit`: 2 críticas, 2 altas y 2 moderadas en `vite`, `vitest`, `tinypool` y `source-map-js`; ninguna en producción). **Corrección aplicada:** `npm audit fix` y actualización de Vitest y su plugin de cobertura a la versión 5; el resultado es 0 vulnerabilidades y las pruebas siguen en verde. Con el nuevo motor de cobertura las cifras del frontend se midieron con más detalle y bajaron de 99,8 % a 94,4 %.
  6. **Accesibilidad (documento 05):** la auditoría con axe-core encontró 11 incumplimientos de regla en 5 pantallas (contraste de color, filtros sin etiqueta y botones de cierre sin nombre) y desbordamiento horizontal en móvil. **Corrección aplicada:** colores base con contraste ≥ 4,5:1, `aria-label` en filtros y botones de cierre, cierre con Escape y diseño adaptable; ahora 0 incumplimientos.
  7. **Valores escritos a mano en la interfaz** (detectados en la revisión posterior al escaneo, no por Sonar): permisos `isAdmin = true` y `canCreate = true`, un UUID de bodega fijo y cifras de impacto ficticias en el Dashboard. **Corrección aplicada:** los botones dependen del rol del usuario, la bodega la resuelve el servidor y el Dashboard calcula sus cifras con datos reales.
- **Deuda residual / siguiente paso:** 6 bloques duplicados (2,2 %; subió desde 1,5 % por las reglas CSS adaptables añadidas), por debajo del umbral de 3 %, que se revisarán cuando se refactoricen los formularios de Vehículos y Pedidos. El flujo de CI (`.github/workflows/ci.yml`) ya ejecuta pruebas con umbral de cobertura del 80 %, `tsc`, build y auditoría de dependencias en cada Pull Request; falta añadir el paso de SonarQube y activar la protección de rama (IMP-009).

## Cómo hacer que SonarQube lea la cobertura (detalles que importan)

La guía de laboratorio del curso (Análisis de código MegaBlog) pide cuatro cosas, que aquí se aplican y se completan con un paso extra:

1. **Rama principal con nombre propio:** al crear el proyecto local, "Main branch name" = `feature/analisis-codigo`, y el análisis se hace desde esa rama.
2. **`sonar-project.properties`** en la raíz con `sonar.sources`, `sonar.tests`, `sonar.exclusions` (sin `node_modules`, `coverage`, `dist`) y las rutas de los informes de cobertura (`sonar.javascript.lcov.reportPaths` y `sonar.python.coverage.reportPaths`).
3. **Generar la cobertura antes del escáner** (`npm run test:coverage` y `pytest --cov`); sin informes, Sonar muestra 0 %.
4. **Token del proyecto** generado en la interfaz (Locally → Generate), pasado como `SONAR_TOKEN`.
5. **Paso extra de este proyecto:** `python scripts/preparar_cobertura.py`. Vitest escribe las rutas del lcov relativas a `src/frontend` y coverage.py las del XML relativas a `src/backend/app`; Sonar las busca desde la raíz del repositorio y, si no coinciden, no asocia la cobertura a ningún archivo. El script las reescribe a `src/frontend/src/...` y `src/backend/app/...`.

## Cómo reproducir el análisis

```bash
docker run -d --name sonarqube-custom -p 9000:9000 sonarqube:community
# En http://localhost:9000: cambiar la contraseña, crear el proyecto "ecologistica-lima"
# (rama principal feature/analisis-codigo) y generar un token

(cd src/frontend && npm ci && npm run test:coverage)
PYTHONPATH=src/backend python -m pytest src/backend/tests --cov=src/backend/app \
  --cov-config=.coveragerc --cov-report=xml:src/backend/coverage.xml
python scripts/preparar_cobertura.py

docker create --name scan --link sonarqube-custom -e SONAR_TOKEN=<token> \
  -e SONAR_HOST_URL=http://sonarqube-custom:9000 sonarsource/sonar-scanner-cli
docker cp . scan:/usr/src
docker start -a scan
```

Notas de entorno (Docker Desktop en Windows, 3,4 GB de memoria): (a) copiar el código con `docker cp` en lugar de montarlo con `-v` evita el error `ENOMEM` del analizador de JavaScript; (b) enlazar el escáner a la red del contenedor de SonarQube (`--link`) evita que la subida del informe se corte con `unexpected end of stream` por el puerto del anfitrión; (c) conviene copiar el repositorio sin `node_modules` para que la lectura no tarde.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-20 | Sprint 3: primer informe de SonarQube con las correcciones aplicadas. |
| 1.1.0 | 2026-10-20 | Se actualizan las pruebas del backend (36), se corrigen las rutas tras reorganizar `docs/` y `src/` y se registra el flujo de CI. |
| 1.2.0 | 2026-10-21 | Nueva medición real con SonarQube 26.10 (cobertura 92,7 %, 2 721 líneas, 0 incidencias, Quality Gate OK); se documentan los pasos y el script que hacen que Sonar lea la cobertura. |
