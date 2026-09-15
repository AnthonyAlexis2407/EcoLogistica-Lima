# Evidencia de Configuración en Atlassian Jira Software

## Metadatos
- **Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles
- **Integrantes:**
  - Fernandez Condor Jhon Smith
  - Perez Ordoñez Anthony Alexis
  - Tovar Arias Michael Aldo
- **Fecha:** 08 de septiembre de 2026
- **Versión:** 1.0.0

[← Volver al README Principal](../../README.md)

---

> ✅ **Estado actual:** el proyecto Scrum **EL — "EcoLogística Lima"** ya existe en `https://metaupsworkspace-33172362.atlassian.net`, con las 6 épicas y las 20 historias/enablers del backlog **creados vía API y verificados**. Lo que falta (Sprint 1, Hoja de ruta, columnas del tablero, Versión de release) requiere pasos manuales en la interfaz de Jira — no hay endpoint de API disponible para crearlos automáticamente. Las 5 evidencias fotográficas siguen pendientes: deben tomarse de este mismo proyecto real, recortadas exclusivamente al panel del elemento a demostrar (sin escritorio, sin pestañas del navegador — penalización del 50% de la sección si se incumple).

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

**[ 📷 EVIDENCIA 2 — BACKLOG PRIORIZADO: entrar a `https://metaupsworkspace-33172362.atlassian.net/jira/software/projects/EL/boards/.../backlog` y pegar aquí la captura recortada exclusivamente al panel de Backlog, mostrando la columna de Story Points y las épicas agrupadas. ]**

## 3. Roadmap del Proyecto (Épicas en Línea de Tiempo) — PENDIENTE (manual)

| Épica | Inicio | Fin | Iteración |
|---|---|---|---|
| EL-6 Arquitectura, Seguridad y Calidad Transversal | 08 sep 2026 | 23 nov 2026 | Transversal (todas) |
| EL-1 Gestión de Flota y Conductores | 08 sep 2026 | 14 sep 2026 | Iteración 1 |
| EL-2 Gestión de Pedidos y Clientes | 15 sep 2026 | 05 oct 2026 | Iteración 2 |
| EL-3 Optimización y Ejecución de Rutas | 15 sep 2026 | 05 oct 2026 | Iteración 2 |
| EL-4 Visualización y Geolocalización | 06 oct 2026 | 26 oct 2026 | Iteración 3 |
| EL-5 Sostenibilidad, Dashboard y Reportes | 06 oct 2026 | 16 nov 2026 | Iteraciones 3-4 |

Pendiente de ubicar en la Hoja de Ruta de Jira (no expuesto por API; hacerlo manualmente arrastrando cada épica a su rango de fechas).

**[ 📷 EVIDENCIA 1 — ROADMAP DEL PROYECTO: pegar aquí la captura recortada exclusivamente al panel de Hoja de Ruta de Jira, mostrando las 6 épicas (EL-1 a EL-6) ubicadas en la línea de tiempo. ]**

## 4. Sprint 1: Planificación y Objetivo — PENDIENTE (manual)

- **Duración:** 2 semanas (08 sep 2026 – 21 sep 2026).
- **Ítems a incluir:** EL-18 (5), EL-24 (5), EL-7 (3), EL-9 (5), y opcionalmente un *spike* acotado sobre EL-17 (≈21 puntos).

**Sprint Goal (pegar en el campo "Objetivo del sprint" al crear el Sprint 1 en Jira):**
> "Al finalizar el Sprint 1, el equipo habrá habilitado el registro y autenticación segura de usuarios, la gestión básica de flota (CRUD de vehículos) y el registro de pedidos con validación de capacidad — sobre una base de seguridad verificada (JWT + cifrado de datos personales) — y contará con los resultados del *spike* comparativo de metaheurísticas que reduce el riesgo RSK-05 antes de comprometer el diseño del motor de optimización en el Sprint 2."

**[ 📷 EVIDENCIA 3 — SPRINT PLANNING & SPRINT GOAL: pegar aquí la captura recortada exclusivamente al panel de planificación del Sprint 1 en Jira, mostrando los ítems seleccionados (EL-18, EL-24, EL-7, EL-9) y el Sprint Goal redactado en la cabecera. ]**

## 5. Tablero Scrum Activo — PENDIENTE (manual)

Columnas del flujo de trabajo a configurar: **Pendiente → En curso → En revisión/QA → Hecho**.

**[ 📷 EVIDENCIA 4 — TABLERO SCRUM ACTIVO: pegar aquí la captura recortada exclusivamente al panel del tablero del proyecto EL, mostrando tarjetas distribuidas en las 4 columnas durante el Sprint 1 en curso. ]**

## 6. Gestión de Versiones / Release — PENDIENTE (manual)

- **Versión a crear en Jira:** `v1.0.0-MVP`
- **Historias asociadas:** las 20 historias/enablers (EL-7 a EL-26) del backlog priorizado (sección 2), vinculadas a esta versión como entregable de fin de proyecto (23 nov 2026, según Documento 02).

**[ 📷 EVIDENCIA 5 — GESTIÓN DE VERSIONES/RELEASE: pegar aquí la captura recortada exclusivamente al módulo de Releases del proyecto EL, mostrando la versión `v1.0.0-MVP` creada y su asociación de historias. ]**

---

## Pasos manuales pendientes antes de la entrega

1. **Backlog:** ✅ Ya creado y verificado — no requiere acción.
2. **Sprint 1:** crear el sprint desde el Backlog, arrastrar los ítems de la sección 4, redactar el Sprint Goal y pulsar "Iniciar sprint".
3. **Hoja de ruta:** ubicar las 6 épicas en el Roadmap con las fechas de la sección 3.
4. **Tablero:** confirmar/ajustar las 4 columnas en Configuración del tablero → Columnas.
5. **Versión:** crear `v1.0.0-MVP` en Releases y asignarla a las 20 historias/enablers.
6. Tomar las 5 capturas **recortadas exclusivamente al panel correspondiente** y reemplazar cada marcador `[ 📷 EVIDENCIA N ]` de este archivo por la imagen real, en el mismo orden.

---

[← Volver al README Principal](../../README.md)
