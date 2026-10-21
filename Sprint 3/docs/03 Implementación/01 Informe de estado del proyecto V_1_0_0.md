# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 3 (periodo 07/10/2026 al 20/10/2026)  
**Fecha de corte del informe:** 20/10/2026  
**Versión del documento:** 3.0.0

[← Volver al README Principal](../../README.md)

## Resumen ejecutivo

**Estado general: calidad técnica en verde, cronograma en riesgo.** El Sprint 3 evaluó el código con SonarQube, OWASP Top 10:2025 y WCAG 2.2 AA y corrigió lo encontrado. El Quality Gate está en PASSED, con 0 bugs, 0 vulnerabilidades y 92,8 % de cobertura. La brecha principal sigue siendo funcional: el motor de optimización (EN-001, US-005) no se ha iniciado y la entrega es el 23/11/2026 (RSK-05, RSK-09).

| Indicador al corte (20/10/2026) | Valor | Referencia | Lectura |
|---|---|---|---|
| Pruebas del backend / frontend | 34 / 60 pasan | Todas en verde | Cumple (Sprint 2: 16 / 0) |
| Cobertura global (SonarQube) | 92,8 % | DoD: ≥ 80 % | Cumple (Sprint 2: 67 % solo backend) |
| Quality Gate | PASSED | PASSED | Cumple ([Doc. 03](Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md)) |
| Bugs / vulnerabilidades / hotspots | 0 / 0 / 0 | 0 | Cumple (primer análisis: 7 bugs, 4 code smells) |
| Duplicación / deuda técnica | 2,2 % / 0 min | ≤ 3 % / 0 | Cumple |
| Vulnerabilidades en dependencias | 0 (antes 6 de desarrollo) | 0 | Cumple |
| OWASP Top 10:2025 | 2 categorías limpias, 6 bajo revisión, 2 vulnerables con corrección parcial | Sin críticas abiertas | Parcial ([Doc. 04](Sprint%2003/04%20OWASP%20V_1_0_0.md)) |
| WCAG 2.2 AA (axe-core, 6 pantallas) | 0 incumplimientos (antes 11) | 0 | Cumple en lo automático ([Doc. 05](Sprint%2003/05%20WCAG%20V_1_0_0.md)) |
| Historias aceptadas por el PO en Jira | 0 | — | Pendiente (IMP-003) |
| Backlog total sin criterios verificados | 18 de 20 ítems (108 de 116 pts), incluido el motor de optimización | Entrega 23/11/2026 | Riesgo de cronograma |

## Historias de Usuario completadas en este Sprint

| ID | Jira | Historia | Estado al corte |
|---|---|---|---|
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | **Criterios verificados**, con control por rol en la interfaz y accesibilidad corregida; pendiente de aceptación del PO |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | **Criterios verificados**, bodega resuelta por el servidor; pendiente de aceptación del PO |
| EN-002 | EL-18 | Hardening de autenticación y protección OWASP | **Parcial**: bloqueo y registro de eventos verificados; falta la prueba de penetración |
| EN-008 | EL-24 | Cifrado y anonimización de datos personales | **Parcial** |
| EN-001 | EL-17 | Spike del motor de optimización | **No iniciado** |

Detalle en la [Revisión del Sprint](Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).

## Demostración del trabajo completado

La verificación técnica del 20/10/2026 es reproducible con los comandos del [Documento 03](Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md). La demostración a stakeholders sigue **sin registrarse**; el guion y la tabla de registro están en la [Revisión del Sprint](Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).

## Pendientes

- Demostración y aceptación del PO (IMP-003); cierre del Sprint 1 y creación del siguiente en Jira (IMP-004).
- Spike EN-001 y arranque de US-005 (IMP-010), ruta crítica del cronograma.
- Endurecimiento de configuración (IMP-012), accesibilidad pendiente (IMP-013) y prueba de penetración, cifrado y cadena de suministro (IMP-014).
- CI con revisión por pares (IMP-009).

Registro completo en el [Registro de Impedimentos](02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Sprint 1: informe documental con corte al 29/09/2026 (commit `246e72d`). |
| 2.0.0 | 05/10/2026 | Sprint 2: reescritura con evidencia verificada. |
| 2.1.0 | 05/10/2026 | DEF-002 y DEF-003 corregidos; 16 pruebas en verde. |
| 3.0.0 | 20/10/2026 | Sprint 3: indicadores de SonarQube, OWASP 2025 y WCAG; cobertura 92,8 %; estado actualizado de historias y pendientes. |
