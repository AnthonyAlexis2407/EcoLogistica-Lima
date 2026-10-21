# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 3 (Implementación, calidad de código y evaluación; periodo 07/10/2026 al 20/10/2026, contiguo al Sprint 2)  
**Fecha de revisión:** 20/10/2026  
**Versión del documento:** 1.1.0

[← Volver al README Principal](../../../README.md)

## Cierre formal del sprint

El Sprint 3 se cerró el **20/10/2026**, antes de esta revisión y de la retrospectiva ([Documento 02](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)), con la etiqueta Git `sprint-3-cierre` sobre el último commit del sprint. Los sprints anteriores quedaron cerrados con `sprint-1-cierre` (29/09/2026) y `sprint-2-cierre` (06/10/2026). El tablero de Jira se sincroniza aparte (IMP-004, administrativo): la revisión y la retrospectiva no dependen de él.

## Objetivo del sprint

Dejar el incremento de los Sprints 1 y 2 en un estado **medible y defendible**: evaluar su calidad con SonarQube, su seguridad con OWASP Top 10:2025 y su accesibilidad con WCAG 2.2 AA; corregir lo encontrado; y alinear la documentación con el código real. El sprint no añade historias nuevas del backlog: consolida US-001 y US-003 y reduce la deuda de calidad que impedía cumplir la Definition of Done (DoD).

## Historias de Usuario completadas en este Sprint

Una historia se considera **completada** cuando cumple la **definición de hecho (DoD)**: (1) sus criterios de aceptación pasan en las tres rutas (feliz, infeliz y gold) mediante pruebas automatizadas; (2) la cobertura global es ≥ 80 %; (3) SonarQube no tiene bugs ni vulnerabilidades abiertos; (4) no hay incumplimientos WCAG AA en axe-core; (5) la documentación afectada está versionada; y (6) el Product Owner la acepta. Las cinco primeras son verificables por el equipo; la sexta sigue pendiente.

| ID | Jira | Historia | Qué cambió en el Sprint 3 | Estado frente a la DoD |
|---|---|---|---|---|
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | Botones de alta, edición y baja según el rol real (antes `isAdmin = true` fijo); filtro y botón de cierre con nombre accesible; cierre del modal con Escape; pruebas por rol | Puntos 1 a 5 cumplidos; **falta la aceptación del PO** |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | Bodega resuelta por el servidor (antes UUID fijo en la interfaz); `canCreate` por rol; modal accesible | Puntos 1 a 5 cumplidos; **falta la aceptación del PO** |
| EN-002 | EL-18 | Hardening de autenticación y protección OWASP | Evaluación OWASP Top 10:2025 ([Doc. 04](04%20OWASP%20V_1_0_0.md)); `DEBUG` en `False`; `ENVIRONMENT=production` rechaza la clave por defecto; CORS acotado; cabeceras de seguridad; rol `ADMINISTRADOR` eliminado; registro de eventos de seguridad | **Parcial**: falta la prueba de penetración |
| EN-008 | EL-24 | Cifrado y anonimización de datos personales | Sin cambios; los registros de seguridad evitan correos y contraseñas (Ley N° 29733) | **Parcial**: sin cifrado de campos ni anonimización |
| EN-001 | EL-17 | Spike del motor de optimización dentro de 45 s | Sin avance | **No iniciado** |

### Criterios de aceptación por ruta

| Historia | Ruta feliz | Ruta infeliz | Ruta gold (flujo completo) |
|---|---|---|---|
| US-001 | Registrar un vehículo con placa única (201) y listarlo | Placa duplicada (409); un OPERADOR no puede registrar flota (403) | El administrador registra la flota, la bodega registra su pedido sobre ella y lo cancela |
| US-003 | Pedido válido en estado PENDIENTE (201) | Peso mayor que la capacidad de la flota (422); pedido de otra bodega (403) | La bodega se autentica, registra su pedido, lo ve en su listado y lo cancela |
| EN-002 | Inicio de sesión correcto con JWT de 60 min | Tres intentos fallidos bloquean la cuenta 15 min (423); el registro público no concede rol de administración (403) | Un ADMIN_FLOTA crea un usuario con otro rol y este accede solo a lo que su rol permite |

Pruebas que lo respaldan: `test_us001_*`, `test_us003_*`, `test_rn010_*`, `test_en002_*`, `test_ruta_gold_flujo_completo_de_flota_y_pedidos` y `test_rol_inexistente_administrador_no_obtiene_acceso` en [`test_criterios_aceptacion.py`](../../../src/backend/tests/test_criterios_aceptacion.py), además de las pruebas por rol de [`VehiculosPage.test.tsx`](../../../src/frontend/src/__tests__/VehiculosPage.test.tsx) y [`PedidosPage.test.tsx`](../../../src/frontend/src/__tests__/PedidosPage.test.tsx).

### Resultados medibles frente al Sprint 2

| Indicador | Sprint 2 (05/10/2026) | Sprint 3 (20/10/2026) | Meta DoD | Fuente |
|---|---|---|---|---|
| Pruebas del backend | 16 | **36** pasan | todas en verde | `pytest` |
| Pruebas del frontend | 0 | **60** pasan | todas en verde | Vitest 5 |
| Cobertura global | 67 % (solo backend) | **92,8 %** (Sonar); backend 86 %, frontend 94,4 % | ≥ 80 % | SonarQube, `pytest --cov`, Vitest |
| Quality Gate | no configurado | **PASSED** | PASSED | [Doc. 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) |
| Bugs / Code smells (primer análisis → final) | sin medir | 7 → **0** / 4 → **0** | 0 | [Doc. 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) |
| Vulnerabilidades y Security Hotspots | sin medir | **0** / **0** | 0 | SonarQube |
| Deuda técnica | sin medir | 20 min → **0 min** | 0 | SonarQube |
| Duplicación | sin medir | 2,2 % | ≤ 3 % | SonarQube |
| Vulnerabilidades en dependencias (`npm audit`) | sin medir | 6 → **0** | 0 | `npm audit` |
| Incumplimientos WCAG AA (axe-core) | sin medir | 11 → **0** en 6 pantallas | 0 | [Doc. 05](05%20WCAG%20V_1_0_0.md) |
| Verificación de tipos (`tsc`) | no existía | **sin errores** | sin errores | `npm run typecheck` |
| Integración continua | no existía | **creada** (`.github/workflows/ci.yml`) | activa en cada PR | [Doc. 10 de Inicio](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md) |

## Demostración del trabajo completado

**Demostración técnica reproducible (verificada por el equipo el 20/10/2026).** Los resultados anteriores se reproducen con los comandos de "Cómo reproducir el análisis" del [Documento 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) y con `npm run typecheck`.

**Guion de la demostración a stakeholders** (docente/Product Owner y cliente ficticio DistriRápido):

1. **Accesibilidad:** recorrer inicio de sesión, Dashboard, Vehículos y Pedidos solo con teclado; abrir un modal y cerrarlo con Escape; mostrar la vista a 375 px sin desplazamiento horizontal.
2. **Control por rol:** iniciar sesión como ADMIN_FLOTA, OPERADOR y BODEGA y mostrar qué botones ve cada uno.
3. **Ruta gold:** como ADMIN_FLOTA registrar un vehículo; como BODEGA registrar un pedido, verlo en su listado y cancelarlo.
4. **Ruta infeliz:** repetir la placa (409), exceder la capacidad (422) y fallar tres inicios de sesión (bloqueo de 15 minutos).
5. **Seguridad:** mostrar las cabeceras de seguridad de la API y que `/docs` desaparece con `ENVIRONMENT=production`.
6. **Calidad:** mostrar SonarQube (Quality Gate PASSED, 0 bugs, 0 vulnerabilidades) y el reporte de axe-core sin incumplimientos.

**Registro de la demostración a stakeholders.** Se completa cuando se realice; hasta entonces no se declara como hecha ni se atribuyen observaciones a terceros (IMP-003):

| Fecha | Asistentes | Incremento mostrado | Observaciones | Decisión por historia (US-001 / US-003) |
|---|---|---|---|---|
| _por completar_ | _por completar_ | Guion anterior, etiqueta `sprint-3-cierre` | _por completar_ | _aceptada / cambios solicitados / no presentada_ |

## Pendientes

- **Aceptación del Product Owner (IMP-003):** realizar la demostración, completar la tabla anterior y pasar US-001 y US-003 a "Hecho".
- **EN-001 (RSK-05, ruta crítica):** iniciar el spike GA / Búsqueda Tabú / OR-Tools frente al límite de 45 s; sin él no puede comenzar US-005 (IMP-010).
- **EN-002:** ejecutar la prueba de penetración. **EN-008:** cifrado de campos personales y anonimización.
- **Seguridad (Doc. 04):** CSP y HSTS en el despliegue con TLS, rotar la `SECRET_KEY`, fijar versiones del backend y revisar el resultado de `pip-audit` (IMP-012, IMP-014).
- **Accesibilidad (Doc. 05):** prueba con lector de pantalla, trampa de foco en modales y tamaño de objetivos táctiles (IMP-013).
- **Calidad (IMP-009):** añadir SonarQube al CI y activar la protección de la rama `main` con revisor obligatorio.
- **Backlog sin iniciar:** 15 ítems (US-002, US-004 a US-010, EN-003 a EN-007, EN-009, EN-010), entre ellos el motor de optimización y el cálculo de CO₂.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 20/10/2026 | Sprint 3: primera revisión del sprint con indicadores de calidad, seguridad y accesibilidad. |
| 1.1.0 | 20/10/2026 | Se añaden el cierre formal del sprint, la definición de hecho, los criterios de aceptación por ruta (feliz, infeliz y gold) y la verificación de tipos y la integración continua; se retira del plan el cierre del sprint como pendiente. |
