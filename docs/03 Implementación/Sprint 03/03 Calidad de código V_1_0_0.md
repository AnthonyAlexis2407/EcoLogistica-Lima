# Evaluación de Calidad de Código — SonarQube

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha de Análisis:** 2026-10-20  
**Versión del Análisis:** V_1_0_0 (documento 1.1.0)

[← Volver al README Principal](../../../README.md)

**Alcance:** código de `src` (backend FastAPI en Python y frontend React/TypeScript), 2 706 líneas de código (690 Python, 1293 TypeScript, 723 CSS) en 20 archivos. Herramienta: SonarQube Community (imagen `sonarqube:community`) con el scanner `sonar-scanner-cli`, proyecto `ecologistica-lima`. La configuración está en [`sonar-project.properties`](../../../sonar-project.properties) y excluye `seed.py` (script de datos de prueba).

## 1. Resumen Ejecutivo de Quality Gate

- **Estado del Quality Gate:** PASSED (compuerta "Sonar way": 3 condiciones sobre código nuevo en verde: cobertura 89,6 % ≥ 80 %, duplicación 1,8 % ≤ 3 % y 0 incidencias nuevas)
- **Porcentaje de Cobertura de Pruebas (Coverage):** 92,8 % global (94,7 % de líneas; quedan 44 de 824 líneas sin cubrir)
- **Duplicación de Código:** 2,2 % (6 bloques duplicados)

Detalle de la cobertura por capa, según las herramientas de cada una:

| Capa | Pruebas | Cobertura | Herramienta |
|---|---|---|---|
| Backend (`app/`, sin `seed.py`) | 36 pasan | 86 % | `pytest --cov` |
| Frontend (`src/`) | 60 pasan | 94,4 % de líneas | Vitest 5 + v8 |

Las 2 pruebas del backend más recientes (ruta gold y rol inexistente) se añadieron después del último análisis de Sonar; la cifra de Sonar corresponde a las 34 anteriores. El Quality Gate estándar solo evalúa código nuevo; por eso se reporta además la cobertura global, que es la que exige el DoD del proyecto (≥ 80 %).

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
  3. **Cobertura inicial de 65 % global.** El backend estaba en 72 % y el frontend sin pruebas. **Corrección aplicada:** 17 pruebas nuevas de routers en el backend (de 16 a 34) y 60 pruebas con Vitest en el frontend; la cobertura global pasó a 92,8 %.
  4. **Informe de cobertura del backend ignorado por Sonar (0 %).** `coverage.xml` usaba rutas absolutas. **Corrección aplicada:** `.coveragerc` con `relative_files = True` y ejecución de `pytest` desde la raíz del repositorio.
  5. **Dependencias de desarrollo con vulnerabilidades conocidas** (`npm audit`: 2 críticas, 2 altas y 2 moderadas en `vite`, `vitest`, `tinypool` y `source-map-js`; ninguna en producción). **Corrección aplicada:** `npm audit fix` y actualización de Vitest y su plugin de cobertura a la versión 5; el resultado es 0 vulnerabilidades y las pruebas siguen en verde. Con el nuevo motor de cobertura las cifras del frontend se midieron con más detalle y bajaron de 99,8 % a 94,4 %.
  6. **Accesibilidad (documento 05):** la auditoría con axe-core encontró 11 incumplimientos de regla en 5 pantallas (contraste de color, filtros sin etiqueta y botones de cierre sin nombre) y desbordamiento horizontal en móvil. **Corrección aplicada:** colores base con contraste ≥ 4,5:1, `aria-label` en filtros y botones de cierre, cierre con Escape y diseño adaptable; ahora 0 incumplimientos.
  7. **Valores escritos a mano en la interfaz** (detectados en la revisión posterior al escaneo, no por Sonar): permisos `isAdmin = true` y `canCreate = true`, un UUID de bodega fijo y cifras de impacto ficticias en el Dashboard. **Corrección aplicada:** los botones dependen del rol del usuario, la bodega la resuelve el servidor y el Dashboard calcula sus cifras con datos reales.
- **Deuda residual / siguiente paso:** 6 bloques duplicados (2,2 %; subió desde 1,5 % por las reglas CSS adaptables añadidas), por debajo del umbral de 3 %, que se revisarán cuando se refactoricen los formularios de Vehículos y Pedidos. El flujo de CI (`.github/workflows/ci.yml`) ya ejecuta pruebas con umbral de cobertura del 80 %, `tsc`, build y auditoría de dependencias en cada Pull Request; falta añadir el paso de SonarQube y activar la protección de rama (IMP-009).

## Cómo reproducir el análisis

```bash
docker run -d --name sonarqube-custom -p 9000:9000 sonarqube:community
# Crear el proyecto "ecologistica-lima" y un token en http://localhost:9000

(cd src/frontend && npm ci && npm run test:coverage)
PYTHONPATH=src/backend python -m pytest src/backend/tests --cov=src/backend/app \
  --cov-config=.coveragerc --cov-report=xml:src/backend/coverage.xml
docker run --rm -e SONAR_TOKEN -e SONAR_HOST_URL=http://host.docker.internal:9000 \
  -v "$PWD:/usr/src" sonarsource/sonar-scanner-cli
```

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-20 | Sprint 3: primer informe de SonarQube con las correcciones aplicadas. |
| 1.1.0 | 2026-10-20 | Se actualizan las pruebas del backend (36), se corrigen las rutas tras reorganizar `docs/` y `src/` y se registra el flujo de CI. |
