# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4 (calidad, automatización, implementación final y cierre; periodo 21/10/2026 al 28/11/2026)  
**Fecha de revisión:** 16/11/2026 (actualizada el 17/11/2026 tras el despliegue en producción y el 28/11/2026 con el cierre del sprint)  
**Versión del documento:** 2.0.0

[← Volver al README principal](../../../README.md) · [Matriz de cumplimiento](06%20Matriz%20de%20cumplimiento%20V_1_0_0.md) · [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) · [Usabilidad](04%20Usabilidad%20V_1_0_0.md)

## Resumen del sprint

**Objetivo.** Probar la aplicación de punta a punta en tres navegadores, automatizar la calidad y el despliegue con GitHub Actions, medir la usabilidad con la escala SUS y dejar la aplicación lista para publicarse en producción.

| Indicador | Sprint 3 (20/10/2026) | Sprint 4 (16/11/2026) | Fuente |
|---|---|---|---|
| Pruebas E2E (Playwright) | no existían | **130 de 130 pasan** (Chromium, Firefox, WebKit, móvil y humo) | [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |
| Pruebas unitarias del frontend | 60 | **70** pasan | Vitest, flujo `Tests` |
| Lint y análisis estático | sin script de lint | **0 errores**: ESLint, Ruff, Bandit y `tsc` | flujo `CI` |
| Flujos de GitHub Actions | 1 (`ci.yml`) | **4**: `CI`, `Tests`, `Deploy Production` y Green IT, todos en verde en `main` | [Actions](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions) |
| Web Vitals (inicio de sesión) | sin medir con Playwright | TTFB 4–8 ms, FCP/LCP 32–46 ms, CLS 0 | [Análisis Playwright, sección 3](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |
| Tiempo de respuesta de la API | medido con script en Green IT | contenedor: mediana **2,1 a 6,4 ms**, p95 máximo 14,2 ms; producción desde internet: mediana **295 ms**, p95 383 ms (límite 500 ms) | Análisis Playwright |
| Disponibilidad | sin medir | **100 %** en 90 sondeos (contenedor) y en 30 sondeos a producción | Análisis Playwright |
| Usabilidad (SUS) | sin medir | **79,4** (A-), datos simulados con fines académicos | [Usabilidad](04%20Usabilidad%20V_1_0_0.md) |
| Producción | no existía | **Publicada en Render**: <https://ecologistica-lima.onrender.com>; despliegue automático desde `main` con prueba de humo (3 de 3) | [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |

### Actualización de cierre (28/11/2026)

El proyecto tiene cuatro sprints, por lo que este sprint se extendió hasta la fecha de corte para **implementar todo lo que faltaba del backlog**. Antes de programar se auditó el producto contra los criterios de aceptación de los documentos de requisitos y reglas de negocio ([Matriz de cumplimiento](06%20Matriz%20de%20cumplimiento%20V_1_0_0.md)); las brechas halladas se cerraron con código y pruebas.

| Indicador | 16/11/2026 | 28/11/2026 | Fuente |
|---|---|---|---|
| Ítems del backlog en "Hecho" (de 20) | 2 (US-001 y US-003) | **18**, con EN-003 y EN-006 en curso al 50 % | [Reporte de EVM](../../04%20Cierre/03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md) |
| Valor ganado acumulado | USD 2.614,93 (11,6 % del BAC) | **USD 21.209,96 (94,4 %)** | Reporte de EVM |
| Requisitos funcionales que cumplen (de 10) | 3 | **10** | [Matriz de cumplimiento](06%20Matriz%20de%20cumplimiento%20V_1_0_0.md) |
| Requisitos no funcionales que cumplen (de 10) | 2 | **8** (los otros 2 cumplen en pruebas, no en la nube gratuita) | Matriz de cumplimiento |
| Pruebas del backend | cobertura mínima del 80 % | **175 pruebas, 93,4 % de cobertura**, y 3 contra PostgreSQL real en CI | flujo `Tests` |
| Pruebas unitarias del frontend | 70 | **108** | Vitest, flujo `Tests` |
| Pruebas E2E (Playwright) | 130 | **{E2E}** (Chromium, Firefox, WebKit, móvil y humo) | [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |

## Historias de Usuario completadas en este Sprint

Una historia se considera **completada** cuando cumple la definición de hecho (DoD) del proyecto ([`CONTRIBUTING.md`](../../../CONTRIBUTING.md)): criterios de aceptación verificados en las rutas feliz, infeliz y de validación; pruebas automáticas en verde; cero hallazgos de lint y de seguridad; documentación versionada; y aceptación del Product Owner. En este sprint las cinco primeras se verifican con la suite E2E; la aceptación del Product Owner sigue pendiente (ver Pendientes).

| Código | Título | Criterios de aceptación verificados | Enlaces de trazabilidad |
|---|---|---|---|
| **US-001** (Jira EL-7) | Registrar y administrar vehículos de la flota | Ruta feliz: registrar un vehículo y verlo en la tabla. Ruta infeliz: la placa duplicada se rechaza dentro del formulario. Validación: la capacidad vacía no se envía. Además: editar la capacidad, dar de baja solo tras confirmar y conservar el registro, búsqueda y filtro por estado en el servidor, paginación de 13 vehículos de 12 en 12, y solo el rol autorizado ve los botones de alta. **7 casos × 3 navegadores = 21 ejecuciones, todas pasan.** | Pull Request [#4](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/4) (fusionado en `main` el 17/11/2026, commit `9fc4653`); commit [`9785069`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/9785069) (suite E2E), commit [`4753e89`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/4753e89) (versión final de las pruebas), código de prueba [`vehiculos.spec.ts`](../../../src/frontend/e2e/vehiculos.spec.ts), ejecución [Tests 44020768263](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768263) |
| **US-003** (Jira EL-9) | Registrar pedidos con ventana horaria y ubicación | Ruta feliz: el pedido queda en estado PENDIENTE. Ruta infeliz: un peso mayor que la capacidad de la flota se rechaza con un mensaje claro y el formulario sigue abierto. Validación: el peso debe ser mayor que cero y no sale ninguna petición. Además: cancelar solo tras confirmar y sin ofrecer cancelar dos veces, y filtro por estado en el servidor. Mejora de usabilidad: el formulario explica el formato de las coordenadas. **6 casos × 3 navegadores = 18 ejecuciones, todas pasan.** | Pull Request [#4](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/4) (fusionado en `main`, commit `9fc4653`); commit [`9785069`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/9785069), commit [`a2e4adb`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/a2e4adb) (ayuda de coordenadas), commit [`4753e89`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/4753e89), código de prueba [`pedidos.spec.ts`](../../../src/frontend/e2e/pedidos.spec.ts), ejecución [Tests 44020768263](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768263) |

### Habilitadores técnicos del sprint

Trabajo de calidad y entrega que no tiene ficha propia en Jira; cada uno se verifica con evidencia pública.

| Habilitador | Resultado verificado | Enlaces de trazabilidad |
|---|---|---|
| Pruebas E2E con Playwright | 130 de 130 ejecuciones en verde; Web Vitals, tiempos de la API, uptime y resiliencia | [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md), commit [`9785069`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/9785069) |
| CI/CD con GitHub Actions | `ci.yml`, `tests.yml` y `deploy-production.yml` en verde en `main`; el despliegue usa los GitHub Secrets `RENDER_DEPLOY_HOOK_URL` y `PRODUCTION_URL` y termina con la prueba de humo en producción ([Deploy Production 44020768595](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768595)) | [`ci.yml`](../../../.github/workflows/ci.yml), [`tests.yml`](../../../.github/workflows/tests.yml), [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml), commits [`5a26da0`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/5a26da0) y [`840c1c7`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/840c1c7) (correcciones tras la primera ejecución real) |
| Lint y análisis estático | ESLint, Ruff, Bandit y `tsc` sin errores en CI | [`eslint.config.js`](../../../src/frontend/eslint.config.js), [`pyproject.toml`](../../../pyproject.toml) |
| Imagen Docker y producción en Render | Una imagen sirve la API y el frontend; se construye en cada CI y está publicada en <https://ecologistica-lima.onrender.com> | [`Dockerfile`](../../../Dockerfile), [`render.yaml`](../../../render.yaml), [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |
| Evaluación SUS | SUS 79,4 (A-); dos mejoras aplicadas y verificadas | [Usabilidad](04%20Usabilidad%20V_1_0_0.md), commit [`a2e4adb`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/a2e4adb) |
| Reducción del impacto ambiental (Green IT) | FCP de 0,67 s, imagen AVIF/WebP, compresión Brotli, caché con revalidación y umbrales bloqueantes de Lighthouse | Pull Requests [#2](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/2) y [#3](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/3); commits [`07d1493`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/07d1493) y [`da3b873`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/da3b873); [Informe Green IT](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) |

**Pull Request de cierre del sprint.** El trabajo del sprint se integró en `main` con el [Pull Request #4](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/4), fusionado el 17/11/2026 (commit de fusión `9fc4653`). `main` solo recibe cambios por Pull Request, por lo que cada commit enlazado arriba queda dentro de ese historial verificable.

### Trabajo completado entre el 17/11 y el 28/11/2026

Cada fila enlaza el código y las pruebas que lo verifican; el detalle por requisito está en la [Matriz de cumplimiento](06%20Matriz%20de%20cumplimiento%20V_1_0_0.md).

| Ítem del backlog | Resultado verificado | Evidencia |
|---|---|---|
| **US-005** Rutas optimizadas y **EN-001/EN-005** motor | Ventanas horarias, capacidad de peso y volumen, Pico y Placa y zonas protegidas (rodeadas) como restricciones duras; caché de matrices y planes; estados de la ruta; estudio comparativo de algoritmos ejecutado | [`optimizador.py`](../../../src/backend/app/optimizador.py), [`servicios.py`](../../../src/backend/app/servicios.py), [`test_optimizador.py`](../../../src/backend/tests/test_optimizador.py), [`spike_algoritmos.py`](../../../scripts/spike_algoritmos.py) |
| **US-002, EN-004, EN-010** conductores, entrega de baja fricción y app sin conexión | Alta y baja de conductores, entrega con firma o foto en 3 toques, reprogramación, PWA instalable, cola de acciones idempotente y sincronización al volver la red | [`conductor_router.py`](../../../src/backend/app/routers/conductor_router.py), [`ConductorPage.tsx`](../../../src/frontend/src/pages/ConductorPage.tsx), [`offline.ts`](../../../src/frontend/src/offline.ts), [`sw.js`](../../../src/frontend/public/sw.js), [`conductor.spec.ts`](../../../src/frontend/e2e/conductor.spec.ts), [`pwa.spec.ts`](../../../src/frontend/e2e/pwa.spec.ts) |
| **US-006** Re-optimización ante incidencias | Vía cerrada, accidente, avería (redistribuye en otros vehículos) y pedido cancelado; retraso que rompe una ventana dispara el recálculo automático; cada recálculo mide su tiempo | `reoptimizar_ruta` en [`servicios.py`](../../../src/backend/app/servicios.py), [`test_ciclo_ruta.py`](../../../src/backend/tests/test_ciclo_ruta.py) |
| **US-004** Notificaciones | Avisos de asignación con hora estimada, salida en ruta, retraso, reprogramación y entrega en el portal de la bodega; sin canal queda pendiente de contacto | [`notificaciones_router.py`](../../../src/backend/app/routers/notificaciones_router.py), [`NotificacionesPage.tsx`](../../../src/frontend/src/pages/NotificacionesPage.tsx) |
| **US-007 a US-010** mapa, dashboard, reportes y compensación | Mapa del operador y del conductor; filtros por distrito y fechas; combustible ahorrado; reportes CSV, Excel y PDF (el auditor sin datos personales); emisión y árboles al completar la ruta | [`indicadores_router.py`](../../../src/backend/app/routers/indicadores_router.py), [`reportes_router.py`](../../../src/backend/app/routers/reportes_router.py), [`DashboardPage.tsx`](../../../src/frontend/src/pages/DashboardPage.tsx), [`RutasPage.tsx`](../../../src/frontend/src/pages/RutasPage.tsx) |
| **EN-002** Seguridad | Suite de pruebas ofensivas automáticas; el inicio de sesión ya no revela si un correo existe; HSTS y política de permisos | [`test_seguridad_ofensiva.py`](../../../src/backend/tests/test_seguridad_ofensiva.py), [`auth.py`](../../../src/backend/app/auth.py) |
| **EN-008** Cifrado y anonimización | Datos personales y de ubicación cifrados con AES-SIV; solicitudes de eliminación con plazo de 5 días hábiles y anonimización | [`cifrado.py`](../../../src/backend/app/cifrado.py), [`admin_router.py`](../../../src/backend/app/routers/admin_router.py), [Documento 11, sección 6](../../01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md) |
| **EN-007** Accesibilidad | axe-core sin incumplimientos WCAG 2.2 AA en todas las pantallas; diálogos con foco atrapado y cierre con Escape | [`accesibilidad.spec.ts`](../../../src/frontend/e2e/accesibilidad.spec.ts), [`Modal.tsx`](../../../src/frontend/src/components/Modal.tsx) |
| **EN-009** Caché | Una corrida repetida usa menos del 70 % de la CPU (medido) | [`test_escalabilidad.py`](../../../src/backend/tests/test_escalabilidad.py) |
| **EN-003 y EN-006** (50 %) Conmutación por falla y escalado | Dos instancias detrás de un balanceador con PostgreSQL; RTO medido; degradación de 250 a 1.000 pedidos medida. Falta habilitarlo en la nube (plan de pago) | [`docker-compose.failover.yml`](../../../docker-compose.failover.yml), [`medir_rto.py`](../../../scripts/medir_rto.py), `test_escalabilidad.py` |
| **Datos persistentes en producción** (RSK-13) | La producción usa una base PostgreSQL gestionada; las pruebas del flujo completo corren contra PostgreSQL real en CI | [`render.yaml`](../../../render.yaml), [`test_postgres.py`](../../../src/backend/tests/test_postgres.py) |
| **Monitoreo** (acción 8 de la Retrospectiva) | Prueba de humo cada hora contra producción, con el tiempo de respuesta en el resumen | [`monitoreo.yml`](../../../.github/workflows/monitoreo.yml) |

## Demostración del trabajo completado

### Qué se demostró y en qué entorno

La demostración técnica de este sprint es **reproducible y automatizada**: la suite E2E de Playwright recorre la aplicación como lo haría una persona, en tres navegadores, y deja informes como evidencia.

| Aspecto | Detalle |
|---|---|
| **Fecha** | 16/11/2026 |
| **Entorno** | Imagen Docker de producción levantada en un ejecutor limpio de GitHub Actions (entorno equivalente a *staging*, efímero). **Producción pública en Render** (<https://ecologistica-lima.onrender.com>), donde `deploy-production.yml` despliega desde `main` y ejecuta la prueba de humo (3 de 3). El primer entorno corre la suite completa y el segundo confirma que el despliegue quedó operativo |
| **Quién la ejecutó** | Los flujos `Tests` y `Deploy Production` de GitHub Actions, disparados por la fusión del Pull Request #4 en `main` (17/11/2026) |
| **Evidencia** | [Tests 44020768263](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768263): informe HTML y resultados como artefactos y anotación con el resumen completo; [Deploy Production 44020768595](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768595): despliegue y prueba de humo en producción; mediciones de disponibilidad de producción en el [Análisis Playwright, sección 4.2](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |

**Funcionalidades exhibidas (con su prueba):**

1. **Inicio de sesión y seguridad:** ingreso correcto, intentos restantes, bloqueo tras tres fallos y rutas protegidas ([`autenticacion.spec.ts`](../../../src/frontend/e2e/autenticacion.spec.ts)).
2. **Gestión de flota (US-001):** alta, edición, baja con confirmación, búsqueda, filtro y paginación.
3. **Gestión de pedidos (US-003):** alta con rechazo por capacidad, cancelación con confirmación y filtro por estado.
4. **Permisos por rol:** el operador consulta pero no modifica; cada bodega solo ve lo suyo ([`roles.spec.ts`](../../../src/frontend/e2e/roles.spec.ts)).
5. **Rendimiento y disponibilidad:** Web Vitals, tiempos de la API por debajo de 500 ms, 100 % de uptime y resistencia a caídas de red ([Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)).
6. **Móvil:** ninguna pantalla se desplaza en horizontal en un Pixel 7 emulado.
7. **App del conductor:** iniciar la ruta, entregar con firma en 3 toques, reprogramar y trabajar sin conexión con sincronización posterior ([`conductor.spec.ts`](../../../src/frontend/e2e/conductor.spec.ts) y [`pwa.spec.ts`](../../../src/frontend/e2e/pwa.spec.ts)).
8. **Accesibilidad:** axe-core en todas las pantallas, foco atrapado en los diálogos y menú operable con teclado ([`accesibilidad.spec.ts`](../../../src/frontend/e2e/accesibilidad.spec.ts)).
9. **Administración y privacidad:** conductores, parámetros del algoritmo, zonas protegidas, reportes sin datos personales para el auditor y solicitudes de eliminación ([`administracion.spec.ts`](../../../src/frontend/e2e/administracion.spec.ts)).

### Retroalimentación recibida

| Fuente | Retroalimentación | Tratamiento |
|---|---|---|
| Evaluación de usabilidad SUS (datos simulados con fines académicos) | Nota 79,4 (A-); el aprendizaje inicial es lo más débil (65 puntos con poca experiencia) y las coordenadas escritas a mano y el factor de CO₂ confundían | Dos mejoras aplicadas (ayuda de formato en coordenadas y explicación del factor de CO₂) y tres propuestas priorizadas en [Usabilidad](04%20Usabilidad%20V_1_0_0.md) |
| Primera ejecución de las pruebas | Cinco supuestos erróneos del entorno y de las pruebas | Corregidos y documentados en el [Análisis Playwright, sección 2.4](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |
| Primera ejecución de Actions | Fallos de Ruff, de un entorno mal declarado y de la selección de pruebas de Vitest | Corregidos en los commits [`5a26da0`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/5a26da0) y [`840c1c7`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/840c1c7) |

### Guion de la demostración en vivo a stakeholders (docente / Product Owner y DistriRápido)

1. **Inicio de sesión:** ingresar como administrador; mostrar el mensaje de intentos restantes y el bloqueo.
2. **Control por rol:** entrar como operador y como bodega y comparar qué botones ve cada uno.
3. **Ruta gold:** como administrador registrar un vehículo; como bodega registrar un pedido, verlo y cancelarlo.
4. **Ayudas de usabilidad:** abrir el formulario de pedido y mostrar la explicación de coordenadas.
5. **Informe Playwright:** abrir el informe HTML y mostrar los tres navegadores en verde y las métricas.
6. **Automatización:** mostrar los flujos `CI` y `Tests` en verde y la imagen de producción.
7. **Ciclo completo:** como operador optimizar, asignar un conductor y registrar una vía cerrada; como conductor entregar con firma, probar el modo sin conexión y terminar la ruta; como bodega ver los avisos; como administrador ver los indicadores y descargar un reporte.

### Registro de la demostración en vivo

| Fecha | Asistentes | Incremento mostrado | Observaciones | Decisión por historia (US-001 / US-003) |
|---|---|---|---|---|
| Sin fecha asignada todavía (se agenda con el docente; acción 2 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)) | Docente / Product Owner y equipo | Guion anterior, rama `feature/sprint-4` | Aún no hay observaciones de terceros; no se atribuyen | Sin decisión: ambas historias siguen en "aceptación pendiente" |

## Pendientes

| Elemento | Estado | Justificación | Tratamiento posterior |
|---|---|---|---|
| **Aceptación del Product Owner** de las historias | Pendiente | Requiere agendar la reunión de demostración con el docente | Acción 2 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |
| **Rama de producción** en Render | Pendiente (acción del equipo) | El servicio sigue apuntando a `feature/sprint-4`; el Blueprint nuevo agrega la base PostgreSQL y la clave de cifrado | Cambiar la rama a `main` y sincronizar el Blueprint, según la [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |
| **EN-003 y EN-006** en la nube | Parcial (50 %) | Cumplen su medida con dos instancias en CI; el plan gratuito de Render ofrece una instancia | Plan de pago de la plataforma |
| **SUS con usuarios reales** | Deuda de validación | La evaluación de este sprint usa datos simulados | Acción 3 de la Retrospectiva |
| **Prueba con lector de pantalla** y en un Android físico de gama baja | Deuda de validación | Requiere una sesión con NVDA o VoiceOver y un dispositivo real | Mantenimiento |
| **Auditoría de seguridad externa** | Deuda | La suite ofensiva automática no sustituye a un tercero | Mantenimiento |
| **SonarQube dentro de `ci.yml`** y versiones fijas del backend | Deuda técnica | SonarQube se ejecuta en local | Mantenimiento |
| **Correo y SMS reales** | Deuda | El canal real es el portal; el correo por SMTP está listo, sin configurar | Contratar proveedor |
## Referencias cruzadas

- Plan de mejora: [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md). Evidencia técnica: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) y [Usabilidad](04%20Usabilidad%20V_1_0_0.md).
- Sprint anterior: [Revisión del Sprint 3](../Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Estado de los ítems: [Artefactos Jira](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md) y [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
- Documentos actualizados en este sprint: [06. Requisitos funcionales](../../01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md) (1.2.0), [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) (1.2.0), [10. Stack tecnológico](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md) (1.6.0), [11. Base de datos](../../01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md) (1.3.0), [12. Modelo C4](../../01%20Inicio/12.%20Modelo%20C4%20V_1_0_0.md) (1.4.0) y [03 Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md) (1.5.0).
- Cierre del proyecto: [Matriz de cumplimiento](06%20Matriz%20de%20cumplimiento%20V_1_0_0.md) y los siete documentos de [`docs/04 Cierre`](../../04%20Cierre/01%20Reporte%20de%20Estado%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Sprint 4: primera revisión con historias completadas, habilitadores técnicos, demostración reproducible y pendientes. |
| 1.1.0 | 17/11/2026 | Se registran el Pull Request #4 fusionado, el despliegue automático en producción con su prueba de humo y las cifras de `main`; los pendientes se redactan con su causa y su tratamiento. |
| 2.0.0 | 28/11/2026 | El sprint se extiende hasta el cierre del proyecto: se registra la implementación de todo el backlog, las nuevas cifras de pruebas, la demostración ampliada y los pendientes reales. |
