# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4 (calidad, automatización y cierre; periodo 21/10/2026 al 16/11/2026)  
**Fecha de revisión:** 16/11/2026  
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) · [Usabilidad](04%20Usabilidad%20V_1_0_0.md)

## Resumen del sprint

**Objetivo.** Probar la aplicación de punta a punta en tres navegadores, automatizar la calidad y el despliegue con GitHub Actions, medir la usabilidad con la escala SUS y dejar la aplicación lista para publicarse en producción.

| Indicador | Sprint 3 (20/10/2026) | Sprint 4 (16/11/2026) | Fuente |
|---|---|---|---|
| Pruebas E2E (Playwright) | no existían | **130 de 130 pasan** (Chromium, Firefox, WebKit, móvil y humo) | [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |
| Pruebas unitarias del frontend | 60 | **70** pasan | Vitest, flujo `Tests` |
| Lint y análisis estático | sin script de lint | **0 errores**: ESLint, Ruff, Bandit y `tsc` | flujo `CI` |
| Flujos de GitHub Actions | 1 (`ci.yml`) | **3 exigidos + 1 de Green IT**; `CI`, `Tests` y Green IT en verde | [Actions](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions) |
| Web Vitals (inicio de sesión) | sin medir con Playwright | TTFB 3–6 ms, FCP/LCP 35–56 ms, CLS 0 | [Análisis Playwright, sección 3](03%20Analisis%20PlayWrigth%20V_1_0_0.md) |
| Tiempo de respuesta de la API | medido con script en Green IT | mediana **1,5 a 3,3 ms**, p95 máximo 5,1 ms (límite 500 ms) | Análisis Playwright |
| Disponibilidad | sin medir | **100 %** en 90 sondeos | Análisis Playwright |
| Usabilidad (SUS) | sin medir | **79,4** (A-), datos simulados con fines académicos | [Usabilidad](04%20Usabilidad%20V_1_0_0.md) |
| Imagen de producción | no existía | **Docker de dos etapas**, usuario sin privilegios | [`Dockerfile`](../../../Dockerfile) |

## Historias de Usuario completadas en este Sprint

Una historia se considera **completada** cuando cumple la definición de hecho (DoD) del proyecto ([`CONTRIBUTING.md`](../../../CONTRIBUTING.md)): criterios de aceptación verificados en las rutas feliz, infeliz y de validación; pruebas automáticas en verde; cero hallazgos de lint y de seguridad; documentación versionada; y aceptación del Product Owner. En este sprint las cinco primeras se verifican con la suite E2E; la aceptación del Product Owner sigue pendiente (ver Pendientes).

| Código | Título | Criterios de aceptación verificados | Enlaces de trazabilidad |
|---|---|---|---|
| **US-001** (Jira EL-7) | Registrar y administrar vehículos de la flota | Ruta feliz: registrar un vehículo y verlo en la tabla. Ruta infeliz: la placa duplicada se rechaza dentro del formulario. Validación: la capacidad vacía no se envía. Además: editar la capacidad, dar de baja solo tras confirmar y conservar el registro, búsqueda y filtro por estado en el servidor, paginación de 13 vehículos de 12 en 12, y solo el rol autorizado ve los botones de alta. **7 casos × 3 navegadores = 21 ejecuciones, todas pasan.** | Commit [`9785069`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/9785069) (suite E2E), commit [`4753e89`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/4753e89) (versión final de las pruebas), código de prueba [`vehiculos.spec.ts`](../../../src/frontend/e2e/vehiculos.spec.ts), ejecución [Tests 44017578661](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44017578661) |
| **US-003** (Jira EL-9) | Registrar pedidos con ventana horaria y ubicación | Ruta feliz: el pedido queda en estado PENDIENTE. Ruta infeliz: un peso mayor que la capacidad de la flota se rechaza con un mensaje claro y el formulario sigue abierto. Validación: el peso debe ser mayor que cero y no sale ninguna petición. Además: cancelar solo tras confirmar y sin ofrecer cancelar dos veces, y filtro por estado en el servidor. Mejora de usabilidad: el formulario explica el formato de las coordenadas. **6 casos × 3 navegadores = 18 ejecuciones, todas pasan.** | Commit [`9785069`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/9785069), commit [`a2e4adb`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/a2e4adb) (ayuda de coordenadas), commit [`4753e89`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/4753e89), código de prueba [`pedidos.spec.ts`](../../../src/frontend/e2e/pedidos.spec.ts), ejecución [Tests 44017578661](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44017578661) |

### Habilitadores técnicos del sprint

Trabajo de calidad y entrega que no tiene ficha propia en Jira; cada uno se verifica con evidencia pública.

| Habilitador | Resultado verificado | Enlaces de trazabilidad |
|---|---|---|
| Pruebas E2E con Playwright | 130 de 130 ejecuciones en verde; Web Vitals, tiempos de la API, uptime y resiliencia | [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md), commit [`9785069`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/9785069) |
| CI/CD con GitHub Actions | `ci.yml` y `tests.yml` en verde; `deploy-production.yml` listo y a la espera de los secretos del proveedor | [`ci.yml`](../../../.github/workflows/ci.yml), [`tests.yml`](../../../.github/workflows/tests.yml), [`deploy-production.yml`](../../../.github/workflows/deploy-production.yml), commits [`5a26da0`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/5a26da0) y [`840c1c7`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/840c1c7) (correcciones tras la primera ejecución real) |
| Lint y análisis estático | ESLint, Ruff, Bandit y `tsc` sin errores en CI | [`eslint.config.js`](../../../src/frontend/eslint.config.js), [`pyproject.toml`](../../../pyproject.toml) |
| Imagen Docker de producción | Una imagen sirve la API y el frontend; se construye en cada CI | [`Dockerfile`](../../../Dockerfile), [`render.yaml`](../../../render.yaml), [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |
| Evaluación SUS | SUS 79,4 (A-); dos mejoras aplicadas y verificadas | [Usabilidad](04%20Usabilidad%20V_1_0_0.md), commit [`a2e4adb`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/a2e4adb) |
| Reducción del impacto ambiental (Green IT) | FCP de 0,67 s, imagen AVIF/WebP, compresión Brotli, caché con revalidación y umbrales bloqueantes de Lighthouse | Pull Requests [#2](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/2) y [#3](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/pull/3); commits [`07d1493`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/07d1493) y [`da3b873`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/da3b873); [Informe Green IT](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) |

**Pull Request de cierre del sprint.** Todo el trabajo de este sprint vive en la rama `feature/sprint-4`; su Pull Request hacia `main` se abre desde [la comparación de ramas](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/compare/main...feature/sprint-4) (la rama `main` solo recibe cambios por Pull Request). Hasta que se fusione, los commits enlazados arriba son la referencia verificable.

## Demostración del trabajo completado

### Qué se demostró y en qué entorno

La demostración técnica de este sprint es **reproducible y automatizada**: la suite E2E de Playwright recorre la aplicación como lo haría una persona, en tres navegadores, y deja informes como evidencia.

| Aspecto | Detalle |
|---|---|
| **Fecha** | 16/11/2026 |
| **Entorno** | Imagen Docker de producción levantada en un ejecutor limpio de GitHub Actions (entorno equivalente a *staging*, efímero). La URL pública de producción se activará al configurar el servicio y sus secretos (ver Pendientes) |
| **Quién la ejecutó** | El flujo `Tests` en GitHub Actions, disparado por el commit [`4753e89`](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/commit/4753e89) |
| **Evidencia** | [Ejecución 44017578661](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44017578661): informe HTML y resultados como artefactos; anotación con el resumen completo |

**Funcionalidades exhibidas (con su prueba):**

1. **Inicio de sesión y seguridad:** ingreso correcto, intentos restantes, bloqueo tras tres fallos y rutas protegidas ([`autenticacion.spec.ts`](../../../src/frontend/e2e/autenticacion.spec.ts)).
2. **Gestión de flota (US-001):** alta, edición, baja con confirmación, búsqueda, filtro y paginación.
3. **Gestión de pedidos (US-003):** alta con rechazo por capacidad, cancelación con confirmación y filtro por estado.
4. **Permisos por rol:** el operador consulta pero no modifica; cada bodega solo ve lo suyo ([`roles.spec.ts`](../../../src/frontend/e2e/roles.spec.ts)).
5. **Rendimiento y disponibilidad:** Web Vitals, tiempos de la API por debajo de 500 ms, 100 % de uptime y resistencia a caídas de red ([Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)).
6. **Móvil:** ninguna pantalla se desplaza en horizontal en un Pixel 7 emulado.

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

### Registro de la demostración en vivo

| Fecha | Asistentes | Incremento mostrado | Observaciones | Decisión por historia (US-001 / US-003) |
|---|---|---|---|---|
| Sin fecha asignada todavía (se agenda con el docente; acción 2 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)) | Docente / Product Owner y equipo | Guion anterior, rama `feature/sprint-4` | Aún no hay observaciones de terceros; no se atribuyen | Sin decisión: ambas historias siguen en "aceptación pendiente" |

## Pendientes

| Elemento | Estado | Justificación | Tratamiento posterior |
|---|---|---|---|
| **Aceptación del Product Owner** de US-001 y US-003 | Pendiente (4.º sprint) | Requiere una reunión con el docente | Acción 2 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) (20/11/2026) |
| **Despliegue público** en Render | Flujo listo; falta crear el servicio y los secretos `RENDER_DEPLOY_HOOK_URL` y `PRODUCTION_URL` | Son datos secretos de la cuenta del equipo; hasta entonces `deploy-production.yml` avisa de que faltan | Acción 1 (18/11/2026), guiada por la [Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md) |
| **EN-001**: motor de optimización dentro de 45 s | No iniciado (RSK-05, ruta crítica) | Tercer sprint sin avance | Acción 4 (spike de 3 días, 20/11/2026) |
| **EN-002**: prueba de penetración | Parcial | Falta la prueba de penetración; las pruebas E2E ya verifican bloqueo, roles, cabeceras y `/docs` oculto | Acción de la [Retrospectiva del Sprint 3](../Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |
| **EN-008**: cifrado y anonimización de datos personales | No iniciado | Sin cambios | Backlog |
| **EN-009**: reducción de recómputo con caché | Parcial | La caché HTTP (ETag y 304) está hecha y probada; la caché de resultados depende del motor (EN-001) | Tras EN-001 |
| **Datos persistentes en producción** | Deuda técnica (RSK-13) | SQLite en el disco temporal del plan gratuito reinicia los datos | Acción 6: migrar a PostgreSQL |
| **SUS con usuarios reales** | Deuda de validación | La evaluación de este sprint usa datos simulados | Acción 3 (20/11/2026) |
| **SonarQube dentro de `ci.yml`** y versiones fijas del backend | Deuda técnica | SonarQube se ejecuta en local | Acción 7 (23/11/2026) |
| **Prueba con lector de pantalla** y trampa de foco en modales | Deuda de accesibilidad | Sin avance en el sprint | [Sprint 3, WCAG](../Sprint%2003/05%20WCAG%20V_1_0_0.md) |
| **Backlog sin iniciar** | 14 ítems: US-002, US-004 a US-010, EN-003 a EN-007 y EN-010, entre ellos el motor y el mapa | Dependen de EN-001 | Se recortará el alcance con el docente si el spike no avanza (RSK-09) |

## Referencias cruzadas

- Plan de mejora: [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md). Evidencia técnica: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md) y [Usabilidad](04%20Usabilidad%20V_1_0_0.md).
- Sprint anterior: [Revisión del Sprint 3](../Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Estado de los ítems: [Artefactos Jira](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md) y [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
- Documentos actualizados en este sprint: [10. Stack tecnológico](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md) (1.4.0), [12. Modelo C4](../../01%20Inicio/12.%20Modelo%20C4%20V_1_0_0.md) (1.2.0) y [03 Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md) (1.3.0).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Sprint 4: primera revisión con historias completadas, habilitadores técnicos, demostración reproducible y pendientes. |
