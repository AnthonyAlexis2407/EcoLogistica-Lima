# Evidencia de Configuración en Atlassian Jira Software

## Metadatos
- **Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles
- **Integrantes:**
  - Fernandez Condor Jhon Smith
  - Perez Ordoñez Anthony Alexis
  - Tovar Arias Michael Aldo
- **Fecha:** 08 de septiembre de 2026 (actualizado el 05 de octubre de 2026)
- **Versión:** 1.1.0

[← Volver al README Principal](../../README.md)

---

> ✅ **Estado verificado en Jira el 05/10/2026 (consulta por API):** el proyecto Scrum **EL — "EcoLogística Lima"** (`https://metaupsworkspace-33172362.atlassian.net`) contiene las 6 épicas y los 20 ítems del backlog con sus Story Points (116 pts); existe el sprint **EL Sprint 1** (tablero 2, 08/09 al 22/09/2026, objetivo registrado, 5 ítems asignados) y la versión **v1.0.0-MVP** (no lanzada) asociada a los 20 ítems. **Sigue sin resolverse:** EL Sprint 1 permanece "activo" después de su fecha de fin, sus 5 ítems continúan "En curso" y no existe Sprint 2 (IMP-004 del Registro de Impedimentos). Las capturas de Roadmap, tablero y versiones son evidencia aportada por el equipo; la API disponible no permite consultar esos tres paneles.

---

## 1. Jerarquía del Trabajo — YA CREADA EN JIRA

| Tipo de ítem | Cantidad | Claves reales en Jira |
|---|---|---|
| Épica (Epic) | 6 | [EL-1](https://metaupsworkspace-33172362.atlassian.net/browse/EL-1) a [EL-6](https://metaupsworkspace-33172362.atlassian.net/browse/EL-6) |
| Historia de Usuario (Historia) | 10 | EL-7 a EL-16 |
| Historia Técnica / Enabler (Tarea) | 10 | EL-17 a EL-26 |

## 2. Backlog Priorizado con Story Points (Fibonacci) — YA CREADO

| Prioridad | Clave Jira | ID interno | Título | Épica | Story Points |
|---|---|---|---|---|---|
| 1 | EL-18 | EN-002 | Hardening de autenticación y protección OWASP | EL-6 | 5 |
| 2 | EL-24 | EN-008 | Cifrado y anonimización de datos personales (Ley 29733) | EL-6 | 5 |
| 3 | EL-7 | US-001 | Registrar y administrar vehículos de la flota | EL-1 | 3 |
| 4 | EL-9 | US-003 | Registrar pedidos con ventana horaria y ubicación | EL-2 | 5 |
| 5 | EL-17 | EN-001 | Motor de optimización dentro del SLA de 45 segundos | EL-6 | 8 |
| 6 | EL-11 | US-005 | Generar rutas optimizadas para la flota disponible | EL-3 | 13 |
| 7 | EL-13 | US-007 | Visualizar la ruta asignada en un mapa interactivo | EL-4 | 5 |
| 8 | EL-8 | US-002 | Gestionar conductores y capturar evidencia en campo | EL-1 | 8 |
| 9 | EL-26 | EN-010 | App de conductor offline-first en gama baja | EL-6 | 8 |
| 10 | EL-12 | US-006 | Re-optimizar una ruta ante una incidencia | EL-3 | 8 |
| 11 | EL-22 | EN-006 | Auto-scaling horizontal para 1,000 pedidos/día | EL-6 | 8 |
| 12 | EL-10 | US-004 | Notificar al cliente el estado y ETA de su pedido | EL-2 | 5 |
| 13 | EL-14 | US-008 | Consultar el dashboard de indicadores | EL-5 | 8 |
| 14 | EL-19 | EN-003 | Failover automático del backend | EL-6 | 5 |
| 15 | EL-21 | EN-005 | Módulo de optimización desacoplado y con pruebas | EL-6 | 5 |
| 16 | EL-16 | US-010 | Calcular y comunicar la compensación de carbono | EL-5 | 5 |
| 17 | EL-15 | US-009 | Exportar reportes operativos y ambientales | EL-5 | 3 |
| 18 | EL-23 | EN-007 | Cumplimiento WCAG 2.1 AA en el panel web | EL-6 | 3 |
| 19 | EL-20 | EN-004 | Flujo de confirmación de entrega de baja fricción | EL-6 | 3 |
| 20 | EL-25 | EN-009 | Reducción de recómputo mediante caché | EL-6 | 3 |

**Total del backlog: 116 Story Points**, verificados por consulta JQL (`project = EL ORDER BY key ASC`) contra el proyecto real.

**Evidencia 2 — Backlog Priorizado (captura del equipo).**
<img width="1518" height="856" alt="image" src="https://github.com/user-attachments/assets/0ee491a4-3c96-4538-90a7-31315e0a3be0" />

## 3. Roadmap del Proyecto (Épicas en Línea de Tiempo) — captura adjunta

| Épica | Inicio | Fin | Iteración |
|---|---|---|---|
| EL-6 Arquitectura, Seguridad y Calidad Transversal | 08 sep 2026 | 23 nov 2026 | Transversal (todas) |
| EL-1 Gestión de Flota y Conductores | 08 sep 2026 | 14 sep 2026 | Iteración 1 |
| EL-2 Gestión de Pedidos y Clientes | 15 sep 2026 | 05 oct 2026 | Iteración 2 |
| EL-3 Optimización y Ejecución de Rutas | 15 sep 2026 | 05 oct 2026 | Iteración 2 |
| EL-4 Visualización y Geolocalización | 06 oct 2026 | 26 oct 2026 | Iteración 3 |
| EL-5 Sostenibilidad, Dashboard y Reportes | 06 oct 2026 | 16 nov 2026 | Iteraciones 3-4 |

La ubicación de las épicas en la Hoja de Ruta no es consultable con la API disponible; la evidencia es la captura adjunta. Nota: según estas fechas, EP-02 y EP-03 correspondían a la Iteración 2 (hasta el 05/10/2026); al corte del Sprint 2 solo EP-02 tiene avance parcial (US-003) y EP-03 no tiene avance (IMP-010).

**Evidencia 1 — Roadmap del Proyecto (captura del equipo).**
<img width="1005" height="700" alt="image" src="https://github.com/user-attachments/assets/b56e0bae-9dc2-43d5-aa13-a78e1f2c9bb6" />


## 4. Sprint 1: Planificación y Objetivo — CREADO e INICIADO (verificado en Jira el 05/10/2026; sigue activo)

- **Duración registrada en Jira:** 2 semanas (08 sep 2026 – 22 sep 2026).
- **Ítems asignados en Jira:** EL-7 (3 pts), EL-9 (5), EL-17 (8), EL-18 (5) y EL-24 (5): 26 puntos. EL-17 (EN-001, spike del motor) quedó dentro del sprint, aunque sin avance.

**Sprint Goal registrado en Jira (EL Sprint 1):**
> "Al finalizar el Sprint 1, el equipo habrá habilitado el registro y autenticación segura de usuarios, la gestión básica de flota y el registro de pedidos con validación de capacidad, sobre una base de seguridad verificada, reduciendo el riesgo RSK-05 antes del Sprint 2."

**Evidencia 3 — Sprint Planning & Sprint Goal (captura del equipo).**
<img width="1487" height="557" alt="image" src="https://github.com/user-attachments/assets/d87fc41a-b0b8-4413-84fe-0abdc54e44a9" />




## 5. Tablero Scrum — captura adjunta

Flujo de trabajo previsto: **Por hacer → En curso → En revisión/QA → Hecho**. Estados observados por API al 05/10/2026: *Por hacer* (15 ítems y 6 épicas) y *En curso* (5 ítems del Sprint 1); ningún ítem en *Hecho*.

**Evidencia 4 — Tablero Scrum Activo (captura del equipo).**
<img width="1518" height="840" alt="image" src="https://github.com/user-attachments/assets/824be354-8ca6-4062-a07a-d095c05f0c40" />



## 6. Gestión de Versiones / Release — CREADA (verificado por API el 05/10/2026)

- **Versión en Jira:** `v1.0.0-MVP` (id 10000, no lanzada).
- **Historias asociadas:** las 20 historias/enablers (EL-7 a EL-26) del backlog priorizado (sección 2), vinculadas a esta versión como entregable de fin de proyecto (23 nov 2026, según Documento 02). Comprobado por API: los 20 ítems EL-7 a EL-26 tienen `v1.0.0-MVP` como versión de corrección.

**Evidencia 5 — Gestión de Versiones/Release (captura del equipo).**
<img width="1515" height="417" alt="image" src="https://github.com/user-attachments/assets/1ea159c1-ad9c-4ce6-a11e-92def7bfa7bd" />
<img width="1402" height="795" alt="image" src="https://github.com/user-attachments/assets/3425c914-e729-40e7-8bcd-c2e5dd2a3206" />


---

## Estado de los pasos al 05/10/2026

| Paso | Estado | Fuente de verificación |
|---|---|---|
| Backlog (6 épicas, 20 ítems, 116 pts) | Completo | Consulta JQL por API |
| Sprint 1 creado, con objetivo y 5 ítems | Completo; **sigue activo después del 22/09/2026** | Consulta por API (sprint id 1, tablero 2) |
| Cierre de Sprint 1 y creación de Sprint 2 | **Pendiente** (IMP-004); acción manual en Jira | Consulta por API: no existe Sprint 2 |
| Hoja de ruta con las 6 épicas | Captura adjunta | No consultable por API |
| Tablero con columnas del flujo | Captura adjunta | No consultable por API |
| Versión `v1.0.0-MVP` asociada a los 20 ítems | Completo (no lanzada) | Consulta por API |

## Historial de Control de Cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 08/09/2026 | Creación del documento con el backlog, los pasos manuales pendientes y los marcadores de evidencia; capturas aportadas por el equipo el 29/09/2026. |
| 1.1.0 | 05/10/2026 | Sincronización con el estado real de Jira: sprint creado y activo con 5 ítems (26 pts) y objetivo registrado; versión v1.0.0-MVP asociada; se corrigen fechas del sprint (22/09/2026), se sustituyen los marcadores de captura por pies de figura y se registra el sprint vencido sin cerrar. |

---

[← Volver al README Principal](../../README.md)
