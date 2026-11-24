# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4 (periodo 21/10/2026 al 28/11/2026)  
**Fecha de retrospectiva:** 16/11/2026 (actualizada el 17/11/2026 y el 28/11/2026 con la retrospectiva de cierre)  
**Versión del documento:** 2.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) · [Usabilidad](04%20Usabilidad%20V_1_0_0.md)

**Cómo leer este documento.** Sigue la plantilla de la asignatura: primero lo aprendido, luego lo que funciona y por último lo que se puede mejorar, con acciones concretas. Se apoya en evidencia que cualquiera puede comprobar (historial de Git, informes de Playwright, flujos de GitHub Actions). Los obstáculos que describe son de **herramientas, entornos y procesos**; no se atribuyen a personas. Los responsables y las fechas de las acciones son propuestas que el equipo confirma en la sesión.

## Seguimiento de las acciones de la retrospectiva del Sprint 3

| # | Acción del Sprint 3 | Resultado | Evidencia |
|---|---|---|---|
| 1 | Demostración y aceptación del Product Owner (US-001 y US-003) | **Pendiente**: depende de una reunión con el docente; la tabla de la Revisión se completa cuando ocurra | [Revisión, sección Demostración](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 2 | Proteger `main` y añadir SonarQube al CI | **Parcial**: `main` solo recibe cambios por Pull Request (#2, #3 y #4 fusionados); SonarQube sigue ejecutándose en local | [PR #2](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/2), [PR #3](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/3), [PR #4](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/4) |
| 3 | Agregar `npm run lint` y ejecutarlo en CI | **Cumplida**: ESLint (frontend), Ruff y Bandit (backend) corren en el flujo `ci.yml` con 0 errores | [`ci.yml`](../../../.github/workflows/ci.yml), [`eslint.config.js`](../../../src/frontend/eslint.config.js), [`pyproject.toml`](../../../pyproject.toml) |
| 4 | Probar con lector de pantalla y trampa de foco en modales | **Pendiente**: requiere una sesión con NVDA o VoiceOver que no cupo en este sprint; se reprograma | [Sprint 3, WCAG](../Sprint%2003/05%20WCAG%20V_1_0_0.md) |
| 5 | Spike EN-001 (motor de optimización, límite de 45 s) | **Pendiente**: el tiempo del sprint se dedicó a pruebas E2E, CI/CD y despliegue; se reprograma con tope de 3 días (acción 4) | [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md) |
| 6 | Prueba de penetración (EN-002) y cifrado de campos (EN-008) | **Pendiente**: reprogramada; las pruebas E2E ya verifican bloqueo, roles, cabeceras y `/docs` oculto | [Sprint 3, OWASP](../Sprint%2003/04%20OWASP%20V_1_0_0.md) |
| 7 | Fijar versiones, desplegar con TLS, CSP, HSTS y `ENVIRONMENT=production` | **Parcial**: la imagen de producción trabaja con `ENVIRONMENT=production` y con un usuario sin privilegios dentro del contenedor; Render publica la aplicación con HTTPS; las versiones del backend siguen en rangos `>=` | [`Dockerfile`](../../../Dockerfile), [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |
| 8 | Rotar la revisión (quien corrige no evalúa) | **Parcial**: todo cambio llegó por Pull Request; la plantilla de Pull Request aún no incluye un campo "revisor" que deje constancia de la revisión cruzada | [PR #3](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/3) |

**Lectura:** de 8 acciones, 1 cumplida, 3 parciales y 4 pendientes (reprogramadas). Lo que dependía de herramientas se completó (lint, análisis estático, Pull Requests, imagen de producción y despliegue). Lo pendiente depende de una reunión con el docente o de reservar tiempo para trabajos que no cupieron en un sprint dedicado a calidad, pruebas y despliegue; las acciones 2 y 4 de este documento los reprograman con fecha e indicador.

## ¿Qué aprendimos?

**Técnicas**

- **Una prueba E2E encuentra lo que las pruebas unitarias no ven.** Al ejecutar Playwright por primera vez contra la imagen real, aparecieron tres supuestos erróneos que ninguna prueba unitaria detectaba: (1) la lista de pedidos vacía muestra "Sin pedidos registrados" y no "que coincidan" (el texto cambia si hay filtros); (2) los números se formatean según la región del navegador (`2,750` y no `2.750`); (3) las rutas desconocidas devuelven la aplicación con código 200, de modo que `/docs` oculto no responde 404, sino la pantalla de la aplicación.
- **El nombre del servidor importa.** Con el servicio de pruebas llamado `app`, Chromium forzaba HTTPS y todas las pruebas fallaban con `ERR_SSL_PROTOCOL_ERROR`: `.app` es un dominio de nivel superior con HTTPS obligatorio (HSTS precargado). Al renombrar el servicio a `servidor` se resolvió. La causa se encontró leyendo el error real y no probando a ciegas.
- **Pruebas que no dependen unas de otras.** Cada prueba crea sus propios datos con un sufijo aleatorio y cada rol reutiliza una sesión guardada (`storageState`). Así pueden correr en paralelo y en cualquier orden, y el bloqueo de cuenta por tres intentos fallidos no afecta a las demás.
- **Las métricas de rendimiento se miden con el navegador, no con estimaciones.** `PerformanceObserver` entrega TTFB, FCP, LCP y CLS reales; se complementan con los tiempos de la API medidos desde Playwright ([Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)).
- **Una imagen Docker de dos etapas sirve a la vez para probar y para producir.** La misma imagen se prueba en el equipo, en GitHub Actions y se despliega; así lo que se prueba es lo que se publica.

**Arquitectura**

- **Un solo servicio simplifica el despliegue.** La API (FastAPI) también entrega el frontend compilado; no hay CORS entre dominios ni dos servicios que sincronizar. El costo: cualquier ruta que no existe devuelve la aplicación (se documentó y se probó).
- **SQLite limita la producción.** Con disco temporal los datos se reinician al volver a desplegar; por eso existe la carga de datos de demostración y la migración a PostgreSQL pasa al backlog.

**Gestión**

- **Las herramientas locales tienen un límite.** Docker Desktop, con solo 7,4 GB de memoria disponibles en el equipo de desarrollo, se detenía durante las ejecuciones largas de los tres navegadores. Se resolvió dividiendo la ejecución en tandas cortas con reintentos ([`e2e-por-tandas.sh`](../../../scripts/e2e-por-tandas.sh)). La ejecución completa y confiable corresponde a GitHub Actions.
- **Los nombres exigidos se respetan literalmente.** La consigna fija la carpeta `03 Inplementación`; se adoptó ese nombre en todo el repositorio y se actualizaron los enlaces, que se verifican automáticamente en cada cambio.

## ¿Qué estamos haciendo bien?

- **Calidad automatizada de punta a punta.** Tres flujos independientes: `ci.yml` (lint, análisis estático, compilación y dependencias), `tests.yml` (unitarias, integración y E2E con informes como artefactos) y `deploy-production.yml` (despliegue con Secrets y prueba de humo). Cada flujo usa permisos mínimos, versiones fijas de las acciones y caché.
- **Trazabilidad real.** Cada historia de usuario apunta a Pull Requests y commits verificables ([Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)) y a casos de prueba E2E con el código de la historia en el nombre (`US-001`, `US-003`).
- **Rutas feliz, infeliz y de validación en cada caso.** Las pruebas E2E cubren inicio de sesión, vehículos y pedidos con las tres rutas, además de permisos por rol, resiliencia y rendimiento.
- **Documentación limpia y comprobable.** El script [`verificar_enlaces.py`](../../../scripts/verificar_enlaces.py) revisa en cada cambio que ningún enlace ni ancla esté roto; cada documento enlaza de regreso al README.
- **Honestidad en los datos.** Lo que no se pudo medir en el entorno real se declara como tal (por ejemplo, la evaluación SUS se marca como simulada con fines académicos en su ficha técnica).
- **Seguridad por defecto en producción.** Sin Swagger, sin base de datos local con credenciales por defecto y con cabeceras de seguridad comprobadas por una prueba E2E.
- **Despliegue verificado de punta a punta.** Al fusionar el Pull Request #4, `Deploy Production` pasó las pruebas previas, disparó el despliegue en Render y ejecutó la prueba de humo contra <https://ecologistica-lima.onrender.com> (3 de 3), todo sin pasos manuales ([ejecución 44020768595](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768595)).

## ¿Qué podemos hacer mejor?

### Personas

- **Conocimiento compartido de CI/CD y despliegue.** La [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) deja el procedimiento por escrito para que cualquier integrante pueda ejecutarlo y repetirlo.
- **Carga de trabajo del cierre.** Los scripts [`calcular_sus.py`](../../../scripts/calcular_sus.py), [`resumen_playwright.py`](../../../scripts/resumen_playwright.py) y [`e2e-por-tandas.sh`](../../../scripts/e2e-por-tandas.sh) automatizan tareas repetitivas; se propone seguir automatizando las mediciones de cada sprint.
- **Demostración en vivo.** El guion y las evidencias automáticas de la [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) permiten que cualquier integrante la presente; Tovar Arias Michael Aldo figura como suplente.
- **Evaluación SUS con usuarios reales.** El procedimiento, las tareas y el cálculo ya están definidos; falta convocar a los participantes (acción 3).

### Relaciones

- **La aceptación del Product Owner lleva cuatro sprints abierta.** Se propone fijar la fecha de la demostración con el docente al **inicio** de cada sprint, no al final.
- **Coordinación frontend/backend/pruebas.** Las pruebas E2E dependen de los textos de la interfaz y del formato regional de los números (por ejemplo `2,750` o `2.750`); un catálogo de textos de referencia evita desajustes entre la interfaz y las pruebas.
- **Stakeholders.** Validar con DistriRápido (cliente ficticio) los hallazgos de usabilidad antes de aplicarlos.

### Procesos

- **Revisión cruzada registrada.** Añadir el campo "revisor" a la plantilla de Pull Request (regla 8 del Sprint 3) para dejar constancia de la revisión.
- **Definición de hecho ampliada:** una historia está hecha solo si sus pruebas E2E pasan en los tres navegadores y los tres flujos de Actions están en verde.
- **Ejecutar la suite completa en Actions antes de cada revisión de sprint**, no en el equipo local.
- **Estimar con tiempo para el entorno.** El tiempo perdido en Docker y en memoria no estaba en la estimación; se agrega un margen del 20 % a las tareas de infraestructura.

### Herramientas

- **Memoria del equipo de desarrollo:** cerrar aplicaciones pesadas antes de ejecutar contenedores o usar un equipo con 16 GB; mientras tanto, ejecutar la suite por tandas.
- **PostgreSQL en producción** para conservar datos entre despliegues (requiere el controlador asíncrono `asyncpg`).
- **SonarQube dentro de `ci.yml`** y versiones fijas del backend (archivo de bloqueo).
- **Monitoreo continuo:** programar la prueba de humo de Playwright cada hora contra producción para medir el uptime real.

### Acciones a realizar

| # | Acción (SMART) | Dimensión | Responsable (propuesto) | Fecha objetivo | Indicador de cierre |
|---|---|---|---|---|---|
| 1 | Apuntar el servicio de Render a la rama `main` y comprobar que la espera de `deploy-production.yml` detecta la versión nueva y no la anterior (limitación descrita en la [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md), sección 3) | Herramientas | Perez Ordoñez Anthony Alexis | 18/11/2026 | Render muestra la rama `main` y una nueva ejecución de `Deploy Production` en verde |
| 2 | Realizar la demostración a los stakeholders (docente/Product Owner) y completar la tabla del Documento 01; pasar US-001 y US-003 a "Hecho" si la aceptan | Relaciones | Perez Ordoñez Anthony Alexis (suplente: Tovar Arias Michael Aldo) | 20/11/2026 | Tabla con fecha, asistentes y decisión por historia |
| 3 | Reemplazar los datos simulados del SUS por respuestas de al menos 5 usuarios reales con [`calcular_sus.py`](../../../scripts/calcular_sus.py) | Personas | Tovar Arias Michael Aldo | 20/11/2026 | CSV real versionado; SUS medio ≥ 68; ficha técnica sin la marca "simulada" |
| 4 | Ejecutar el spike EN-001 con tope de 3 días: GA, Búsqueda Tabú y OR-Tools medidos con 50 pedidos frente a 45 s | Procesos | Fernandez Condor Jhon Smith | 20/11/2026 | Script versionado con datos, tiempos y conclusión |
| 5 | Aplicar las tres mejoras de interfaz priorizadas en el Documento 04 y repetir la evaluación SUS | Herramientas | Tovar Arias Michael Aldo | 23/11/2026 | SUS medio sube al menos 3 puntos frente a esta medición |
| 6 | Migrar la persistencia a PostgreSQL (controlador asíncrono, variable `DATABASE_URL`) y probar que los datos sobreviven a un redespliegue | Herramientas | Fernandez Condor Jhon Smith | 23/11/2026 | Prueba E2E que crea un dato, redespliega y lo encuentra |
| 7 | Añadir SonarQube a `ci.yml` y fijar versiones del backend | Herramientas | Fernandez Condor Jhon Smith | 23/11/2026 | Quality Gate PASSED en Actions y archivo de versiones fijas |
| 8 | Programar la prueba de humo de Playwright cada hora contra producción y publicar el resultado | Procesos | Perez Ordoñez Anthony Alexis | 23/11/2026 | Historial de ejecuciones con disponibilidad ≥ 99 % |

## Retrospectiva de cierre (28/11/2026): seguimiento de las acciones del 16/11/2026

| # | Acción de la retrospectiva del 16/11 | Resultado al 28/11 | Evidencia |
|---|---|---|---|
| 1 | Apuntar Render a `main` | **Pendiente** (acción manual en el panel de Render) | [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md), sección 2.5; el flujo de despliegue ahora espera el commit informado por `/api/health` |
| 2 | Demostración con el Product Owner | **Pendiente**: depende de la reunión con el docente | [Revisión, sección Demostración](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 3 | SUS con usuarios reales | **Pendiente**: requiere convocar usuarios | [Usabilidad](04%20Usabilidad%20V_1_0_0.md) |
| 4 | Spike EN-001 con algoritmo genético, búsqueda tabú y OR-Tools | **Cumplida**: se ejecutó con 3 tamaños y 3 semillas; la búsqueda tabú se integró como opción del administrador | [`spike_algoritmos.py`](../../../scripts/spike_algoritmos.py) y [Informe del estudio](07%20Estudio%20de%20algoritmos%20V_1_0_0.md) |
| 5 | Mejoras de interfaz priorizadas y nuevo SUS | **Parcial**: la ubicación del pedido se elige ahora en un mapa (resuelve la confusión de coordenadas); no se repitió el SUS | [`MapaSelector.tsx`](../../../src/frontend/src/components/MapaSelector.tsx) |
| 6 | Migrar a PostgreSQL | **Cumplida en código y pruebas**: `render.yaml` define la base y el flujo completo corre contra PostgreSQL real en CI; falta sincronizar el Blueprint en Render | [`test_postgres.py`](../../../src/backend/tests/test_postgres.py), [`render.yaml`](../../../render.yaml) |
| 7 | SonarQube en `ci.yml` y versiones fijas | **Pendiente**: requiere un token de la organización | [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md) |
| 8 | Prueba de humo cada hora contra producción | **Cumplida**: el flujo existe y empieza a correr cuando se fusione en `main` (los flujos programados solo corren desde la rama por defecto) | [`monitoreo.yml`](../../../.github/workflows/monitoreo.yml) |

**Lectura:** de 8 acciones, 3 cumplidas, 1 parcial y 4 pendientes; lo pendiente depende de personas externas al código (docente, usuarios, panel de Render) o de credenciales (SonarQube).

### Qué funcionó y qué mejorar en el cierre

- **Funcionó:** auditar los criterios de aceptación contra el código y cerrar cada brecha con una prueba; las pruebas "halladoras" (suite ofensiva, E2E sin conexión, axe-core) encontraron defectos reales antes de entregar (enumeración de usuarios, registro del service worker, contraste de enlaces); medir en lugar de suponer (algoritmos, RTO, degradación 250 a 1.000).
- **Mejorar:** la auditoría y la ruta crítica llegaron en la última etapa y obligaron a una implementación masiva en pocos días; Docker local sin memoria obligó a depender de GitHub Actions para la suite completa; no hubo bitácora de horas.
- **Acciones de mantenimiento:** plan de pago de la plataforma (EN-003, EN-006), SUS con usuarios reales, prueba con lector de pantalla y en un Android físico, auditoría de seguridad externa, SonarQube en CI y proveedor de correo y SMS.

## Referencias cruzadas

- Plan y resultados del sprint: [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).
- Evidencia técnica de las lecciones: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) y [Usabilidad](04%20Usabilidad%20V_1_0_0.md).
- Retrospectiva anterior: [Sprint 3, Documento 02](../Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).
- Despliegue: [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md). Riesgos: [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Sprint 4: primera retrospectiva, con seguimiento de las acciones del Sprint 3 y plan de mejora con responsables e indicadores. |
| 1.1.0 | 17/11/2026 | Se registra el despliegue verificado en producción, se reformulan los obstáculos como asuntos de herramientas y procesos, y se actualizan el seguimiento y la acción 1. |
| 2.0.0 | 28/11/2026 | Retrospectiva de cierre: seguimiento de las 8 acciones, lo que funcionó y lo que se debe mejorar. |
