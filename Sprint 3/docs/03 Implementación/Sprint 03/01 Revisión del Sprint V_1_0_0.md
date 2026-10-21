# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 3 (Implementación, calidad de código y evaluación; periodo 07/10/2026 al 20/10/2026, contiguo al Sprint 2)  
**Fecha de revisión:** 20/10/2026  
**Versión del documento:** 1.0.0

[← Volver al README Principal](../../../../README.md)

## Objetivo del sprint

Dejar el incremento de los Sprints 1 y 2 en un estado **medible y defendible**: evaluar su calidad con SonarQube, su seguridad con OWASP Top 10:2025 y su accesibilidad con WCAG 2.2 AA; corregir lo encontrado; y alinear la documentación con el código real. Este sprint no añade historias de usuario nuevas del backlog: consolida US-001 y US-003 y reduce la deuda de calidad que impedía cumplir la Definition of Done (DoD).

## Historias de Usuario completadas en este Sprint

Se aplica la misma definición de "completada con evidencia" del Sprint 2, ampliada con la **Definition of Done** del proyecto: criterios Gherkin cubiertos por pruebas en verde, cobertura global ≥ 80 %, 0 bugs y 0 vulnerabilidades en SonarQube, 0 incumplimientos de reglas WCAG AA en axe-core y documentación versionada.

| ID | Jira | Historia | Qué cambió en el Sprint 3 | Cumple la DoD | Evidencia |
|---|---|---|---|---|---|
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | Botones de alta, edición y baja según el rol real (antes `isAdmin = true` fijo); filtro y botón de cierre con nombre accesible; cierre del modal con Escape; pruebas nuevas por rol | Sí (técnica); **pendiente de aceptación del PO** | [`VehiculosPage.test.tsx`](../../../../Sprint%202/src/frontend/src/__tests__/VehiculosPage.test.tsx), `test_us001_*` |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | Bodega resuelta por el servidor (antes UUID fijo en la interfaz); `canCreate` por rol; modal accesible | Sí (técnica); **pendiente de aceptación del PO** | [`PedidosPage.test.tsx`](../../../../Sprint%202/src/frontend/src/__tests__/PedidosPage.test.tsx), `test_us003_*`, `test_rn010_*` |
| EN-002 | EL-18 | Hardening de autenticación y protección OWASP | Evaluación OWASP Top 10:2025 ([Doc. 04](04%20OWASP%20V_1_0_0.md)); `DEBUG` en `False` por defecto; registro de eventos de seguridad (`ecologistica.security`); aviso por `SECRET_KEY` por defecto | **Parcial**: falta la prueba de penetración | `test_eventos_de_seguridad_se_registran_sin_datos_personales` |
| EN-008 | EL-24 | Cifrado y anonimización de datos personales | Sin cambios; los registros de seguridad evitan correos y contraseñas (Ley N° 29733) | **Parcial** (sin cifrado de campos ni anonimización) | [Doc. 04](04%20OWASP%20V_1_0_0.md), A04 |
| EN-001 | EL-17 | Spike del motor de optimización dentro de 45 s | Sin avance | **No iniciado** | — |

### Resultados medibles frente al Sprint 2

| Indicador | Sprint 2 (05/10/2026) | Sprint 3 (20/10/2026) | Meta DoD | Fuente |
|---|---|---|---|---|
| Pruebas del backend | 16 | **34** pasan | todas en verde | `pytest` |
| Pruebas del frontend | 0 | **60** pasan | todas en verde | Vitest 5 |
| Cobertura global | 67 % (solo backend) | **92,8 %** | ≥ 80 % | SonarQube |
| Quality Gate | no configurado | **PASSED** | PASSED | [Doc. 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) |
| Bugs / Code smells (primer análisis → final) | sin medir | 7 → **0** / 4 → **0** | 0 | [Doc. 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) |
| Vulnerabilidades y Security Hotspots | sin medir | **0** / **0** | 0 | SonarQube |
| Deuda técnica | sin medir | 20 min → **0 min** | 0 | SonarQube |
| Duplicación | sin medir | 2,2 % | ≤ 3 % | SonarQube |
| Vulnerabilidades en dependencias (`npm audit`) | sin medir | 6 → **0** | 0 | `npm audit` |
| Incumplimientos WCAG AA (axe-core) | sin medir | 11 → **0** en 6 pantallas | 0 | [Doc. 05](05%20WCAG%20V_1_0_0.md) |

## Demostración del trabajo completado

**Demostración técnica reproducible (verificada por el equipo el 20/10/2026).** Los resultados anteriores se reproducen con los comandos de la sección "Cómo reproducir el análisis" del [Documento 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md): pruebas del backend y del frontend con cobertura, análisis de SonarQube y auditoría de axe-core.

**Guion de la demostración a stakeholders** (docente/Product Owner y cliente ficticio DistriRápido):

1. **Accesibilidad:** recorrer inicio de sesión, Dashboard, Vehículos y Pedidos solo con teclado; abrir un modal y cerrarlo con Escape; mostrar la vista a 375 px sin desplazamiento horizontal.
2. **Control por rol:** iniciar sesión como ADMIN_FLOTA, OPERADOR y BODEGA y mostrar qué botones ve cada uno (ya no son valores fijos).
3. **Seguridad:** fallar tres inicios de sesión y mostrar el bloqueo de 15 minutos y el evento registrado sin datos personales.
4. **Panel de inicio:** mostrar que "API conectada / sin conexión" refleja `/api/health` y que las cifras del Dashboard salen de datos reales.
5. **Calidad:** mostrar el tablero de SonarQube (Quality Gate PASSED, 0 bugs, 0 vulnerabilidades, 92,8 % de cobertura) y el reporte de axe-core sin incumplimientos.

**Registro de la demostración a stakeholders.** Se completa al realizarla; hasta entonces no se declara como hecha ni se atribuyen observaciones a terceros (impedimento IMP-003):

| Fecha | Asistentes | Incremento mostrado | Observaciones | Decisión por historia (US-001 / US-003) |
|---|---|---|---|---|
| _por completar_ | _por completar_ | Guion anterior, versión del 20/10/2026 | _por completar_ | _aceptada / cambios solicitados / no presentada_ |

## Pendientes

- **Aceptación del Product Owner (IMP-003):** realizar la demostración, completar la tabla anterior y pasar US-001 y US-003 a "Hecho" en Jira.
- **Gestión en Jira (IMP-004):** cerrar EL Sprint 1, crear el sprint siguiente con objetivo y alcance, y recalcular la velocidad con puntos aceptados.
- **EN-001 (RSK-05, ruta crítica):** iniciar el spike GA / Búsqueda Tabú / OR-Tools frente al límite de 45 s; sin él no puede comenzar US-005 (IMP-010).
- **EN-002:** ejecutar la prueba de penetración. **EN-008:** cifrado de campos personales y anonimización.
- **Seguridad (Doc. 04, plan de acción):** exigir `SECRET_KEY` por entorno, restringir CORS, añadir cabeceras de seguridad, fijar versiones del backend y ejecutar `pip-audit`.
- **Accesibilidad (Doc. 05):** prueba con lector de pantalla, trampa de foco en modales, tamaño de objetivos táctiles (2.5.8).
- **Calidad (IMP-009):** integración continua (GitHub Actions) con `pytest --cov`, Vitest, SonarQube, `npm audit` y axe-core en cada Pull Request, con revisión por pares.
- **Backlog sin iniciar:** 15 ítems (US-002, US-004 a US-010, EN-003 a EN-007, EN-009, EN-010), entre ellos todo el motor de optimización y el cálculo de CO₂.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 20/10/2026 | Sprint 3: primera revisión del sprint con indicadores de calidad, seguridad y accesibilidad y registro de la demostración pendiente. |
