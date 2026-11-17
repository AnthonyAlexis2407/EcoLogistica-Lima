# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4 (periodo 21/10/2026 al 16/11/2026)  
**Fecha de retrospectiva:** 16/11/2026  
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) · [Usabilidad](04%20Usabilidad%20V_1_0_0.md)

**Cómo leer este documento.** Sigue la plantilla de la asignatura: primero lo aprendido, luego lo que funciona y por último lo que se puede mejorar, con acciones concretas. Se apoya en evidencia que cualquiera puede comprobar (historial de Git, informes de Playwright, flujos de GitHub Actions) y no atribuye opiniones a integrantes. Los responsables y las fechas de las acciones son propuestas que el equipo confirma en la sesión.

## Seguimiento de las acciones de la retrospectiva del Sprint 3

| # | Acción del Sprint 3 | Resultado | Evidencia |
|---|---|---|---|
| 1 | Demostración y aceptación del Product Owner (US-001 y US-003) | **Pendiente**: depende de una reunión con el docente; la tabla de la Revisión se completa cuando ocurra | [Revisión, sección Demostración](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 2 | Proteger `main` y añadir SonarQube al CI | **Parcial**: `main` solo recibe cambios por Pull Request (PR #2 y #3 fusionados); SonarQube sigue ejecutándose en local | [PR #2](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/2), [PR #3](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/3) |
| 3 | Agregar `npm run lint` y ejecutarlo en CI | **Cumplida**: ESLint (frontend), Ruff y Bandit (backend) corren en el flujo `ci.yml` con 0 errores | [`ci.yml`](../../../.github/workflows/ci.yml), [`eslint.config.js`](../../../src/frontend/eslint.config.js), [`pyproject.toml`](../../../pyproject.toml) |
| 4 | Probar con lector de pantalla y trampa de foco en modales | **No cumplida**: sin avance en el sprint | [Sprint 3, WCAG](../Sprint%2003/05%20WCAG%20V_1_0_0.md) |
| 5 | Spike EN-001 (motor de optimización, límite de 45 s) | **No cumplida**: sigue sin iniciarse; es la ruta crítica del proyecto | [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md) |
| 6 | Prueba de penetración (EN-002) y cifrado de campos (EN-008) | **No cumplida** | [Sprint 3, OWASP](../Sprint%2003/04%20OWASP%20V_1_0_0.md) |
| 7 | Fijar versiones, desplegar con TLS, CSP, HSTS y `ENVIRONMENT=production` | **Parcial**: la imagen de producción ya trabaja con `ENVIRONMENT=production` y con un usuario sin privilegios dentro del contenedor; el TLS y HSTS los entregará el proveedor al desplegar; las versiones del backend siguen en rangos `>=` | [`Dockerfile`](../../../Dockerfile), [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |
| 8 | Rotar la revisión (quien corrige no evalúa) | **No cumplida**: los Pull Requests no registran un revisor distinto del autor; falta el campo "revisor" obligatorio | [PR #3](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/3) |

**Lectura:** 1 acción cumplida, 2 parciales, 1 pendiente de terceros y 4 sin avance, de 8. Lo que depende solo de herramientas se hizo (lint, Pull Requests, imagen de producción); lo que exige a un tercero (aceptación del Product Owner) o una decisión de prioridad (el spike EN-001) se repite por tercer sprint. La acción 5 de este documento ataca justamente ese patrón.

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

- **Las herramientas locales tienen un límite.** El equipo de desarrollo tiene 7,4 GB de memoria con poco espacio libre y Docker Desktop se detenía durante las ejecuciones largas de los tres navegadores. Se resolvió dividiendo la ejecución en tandas cortas con reintentos ([`e2e-por-tandas.sh`](../../../scripts/e2e-por-tandas.sh)). La ejecución completa y confiable corresponde a GitHub Actions.
- **Una consigna con errores tipográficos también se cumple.** La carpeta pedida es `03 Inplementación` (sin la "m" correcta); se adoptó ese nombre en todo el repositorio y se actualizaron los enlaces, que se verifican automáticamente en cada cambio.

## ¿Qué estamos haciendo bien?

- **Calidad automatizada de punta a punta.** Tres flujos independientes: `ci.yml` (lint, análisis estático, compilación y dependencias), `tests.yml` (unitarias, integración y E2E con informes como artefactos) y `deploy-production.yml` (despliegue con Secrets y prueba de humo). Cada flujo usa permisos mínimos, versiones fijas de las acciones y caché.
- **Trazabilidad real.** Cada historia de usuario apunta a Pull Requests y commits verificables ([Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)) y a casos de prueba E2E con el código de la historia en el nombre (`US-001`, `US-003`).
- **Rutas feliz, infeliz y de validación en cada caso.** Las pruebas E2E cubren inicio de sesión, vehículos y pedidos con las tres rutas, además de permisos por rol, resiliencia y rendimiento.
- **Documentación limpia y comprobable.** El script [`verificar_enlaces.py`](../../../scripts/verificar_enlaces.py) revisa en cada cambio que ningún enlace ni ancla esté roto; cada documento enlaza de regreso al README.
- **Honestidad en los datos.** Lo que no se pudo medir en el entorno real se declara como tal (por ejemplo, la evaluación SUS se marca como simulada con fines académicos en su ficha técnica).
- **Seguridad por defecto en producción.** Sin Swagger, sin base de datos local con credenciales por defecto y con cabeceras de seguridad comprobadas por una prueba E2E.

## ¿Qué podemos hacer mejor?

### Personas

- **Un solo integrante concentra la configuración de CI/CD y despliegue.** Hay que repartirla: una segunda persona debe poder ejecutar y entender el despliegue (la [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) existe para eso).
- **La demostración sigue dependiendo del líder del proyecto.** Se asigna un suplente (Tovar Arias Michael Aldo).
- **Falta experiencia en pruebas de usabilidad con usuarios reales.** La evaluación SUS de este sprint es simulada; se necesita practicar con moderación, tareas guiadas y registro de observaciones.

### Relaciones

- **La aceptación del Product Owner lleva cuatro sprints abierta.** Se propone fijar la fecha de la demostración con el docente al **inicio** de cada sprint, no al final.
- **Comunicación frontend/backend.** Los textos de la interfaz y los formatos de números cambiaron sin avisar a quien escribe las pruebas; se acuerda un catálogo de textos de la interfaz que ambos lados usen como referencia.
- **Stakeholders.** Validar con DistriRápido (cliente ficticio) los hallazgos de usabilidad antes de aplicarlos.

### Procesos

- **Todo cambio por Pull Request con revisor.** Aplicar la regla 8 del Sprint 3: quien escribe una corrección no la fusiona.
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
| 1 | Cargar los secretos `RENDER_DEPLOY_HOOK_URL` y `PRODUCTION_URL` en GitHub (el servicio ya está **Live** en <https://ecologistica-lima.onrender.com> y la URL está en el README), cambiar la rama del servicio a `main` tras fusionar y ejecutar **Deploy Production** en verde | Herramientas | Perez Ordoñez Anthony Alexis | 18/11/2026 | Ejecución verde de `deploy-production.yml` y URL abierta con la pantalla de inicio de sesión |
| 2 | Realizar la demostración a los stakeholders (docente/Product Owner) y completar la tabla del Documento 01; pasar US-001 y US-003 a "Hecho" si la aceptan | Relaciones | Perez Ordoñez Anthony Alexis (suplente: Tovar Arias Michael Aldo) | 20/11/2026 | Tabla con fecha, asistentes y decisión por historia |
| 3 | Reemplazar los datos simulados del SUS por respuestas de al menos 5 usuarios reales con [`calcular_sus.py`](../../../scripts/calcular_sus.py) | Personas | Tovar Arias Michael Aldo | 20/11/2026 | CSV real versionado; SUS medio ≥ 68; ficha técnica sin la marca "simulada" |
| 4 | Ejecutar el spike EN-001 con tope de 3 días: GA, Búsqueda Tabú y OR-Tools medidos con 50 pedidos frente a 45 s | Procesos | Fernandez Condor Jhon Smith | 20/11/2026 | Script versionado con datos, tiempos y conclusión |
| 5 | Aplicar las tres mejoras de interfaz priorizadas en el Documento 04 y repetir la evaluación SUS | Herramientas | Tovar Arias Michael Aldo | 23/11/2026 | SUS medio sube al menos 3 puntos frente a esta medición |
| 6 | Migrar la persistencia a PostgreSQL (controlador asíncrono, variable `DATABASE_URL`) y probar que los datos sobreviven a un redespliegue | Herramientas | Fernandez Condor Jhon Smith | 23/11/2026 | Prueba E2E que crea un dato, redespliega y lo encuentra |
| 7 | Añadir SonarQube a `ci.yml` y fijar versiones del backend | Herramientas | Fernandez Condor Jhon Smith | 23/11/2026 | Quality Gate PASSED en Actions y archivo de versiones fijas |
| 8 | Programar la prueba de humo de Playwright cada hora contra producción y publicar el resultado | Procesos | Perez Ordoñez Anthony Alexis | 23/11/2026 | Historial de ejecuciones con disponibilidad ≥ 99 % |

## Referencias cruzadas

- Plan y resultados del sprint: [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).
- Evidencia técnica de las lecciones: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) y [Usabilidad](04%20Usabilidad%20V_1_0_0.md).
- Retrospectiva anterior: [Sprint 3, Documento 02](../Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).
- Despliegue: [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md). Riesgos: [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Sprint 4: primera retrospectiva, con seguimiento de las acciones del Sprint 3 y plan de mejora con responsables e indicadores. |
