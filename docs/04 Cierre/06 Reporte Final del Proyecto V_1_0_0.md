[⬅️ Volver al README Principal](../../README.md)

# Reporte Final del Proyecto (Final Project Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  |  **Fecha de Cierre:** 28/11/2026 (fecha de corte; la sustentación es el 30/11/2026)  |  **Versión:** 1.0.0

> **Cómo leer este reporte.** Resume todo el proyecto: qué se quería, qué se logró, cuánto costó, qué problemas hubo y si fue un éxito. Distingue el trabajo **predictivo** (plan, hitos y presupuesto de la línea base) del **adaptativo** (sprints, backlog y mejoras). Líder del proyecto: Perez Ordoñez Anthony Alexis. Equipo: Fernandez Condor Jhon Smith, Perez Ordoñez Anthony Alexis y Tovar Arias Michael Aldo. Los cálculos están en el [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).

## 1. Descripción General del Proyecto

**Problema.** DistriRápido S.A.C., distribuidora de Lima, reparte pedidos de última milla con rutas armadas a mano: recorre más kilómetros de los necesarios, emite más CO₂ y no cumple siempre las ventanas horarias de las bodegas ([Acta de constitución](../01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_0.md) y [Declaración de la visión](../01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_0.md)).

**Solución.** EcoLogística Lima es una aplicación web que registra la flota y los pedidos, **planifica las rutas** con un algoritmo de optimización que respeta capacidad, Pico y Placa y ventanas horarias, las **muestra en un mapa**, **calcula el CO₂ evitado** (y su equivalente en árboles) y **exporta reportes**. Está publicada en <https://ecologistica-lima.onrender.com>.

**Objetivos del Acta (metas de negocio).** Reducir la distancia recorrida en un 20 %, disminuir el CO₂ en un 25 % y cumplir el 95 % de las ventanas de entrega. **Restricciones:** 4 iteraciones hasta el 16/11/2026, entrega el 23/11/2026, presupuesto de USD 22.469,00 más 12 % de reserva, límite de 45 segundos para el optimizador.

**Enfoque híbrido.** Predictivo: Acta, presupuesto, hoja de ruta y valor ganado. Adaptativo: Scrum con 5 sprints, backlog en Jira, GitFlow con Pull Requests, integración y despliegue continuos.

## 2. Resumen de Desempeño

- **2.1 Alcance (Predictivo y Adaptativo):**
  - Objetivos y criterios de éxito: **Predictivo:** 20 ítems del backlog (116 puntos), 10 requisitos funcionales y 10 no funcionales. **Adaptativo:** entregar incrementos verificados con definición de hecho (criterios en tres rutas, cobertura ≥ 80 %, 0 hallazgos, documentación versionada y aceptación del PO).
  - Evidencia de cumplimiento: **39,5 de 116 puntos ganados (34,1 %)**: completos US-001, US-003 y EN-005; parciales (50 %) EN-001, EN-002, EN-007, EN-009, US-005, US-007, US-008, US-009 y US-010. Requisitos funcionales: 3 cumplidos (RF-001, RF-002 y RF-003 en su MVP), 4 parciales (RF-004, RF-005, RF-006 y RF-010) y 3 sin implementar (RF-007, RF-008 y RF-009). Resultado ambiental medido: el plan optimizado recorre entre 93 % y 97 % menos kilómetros que un viaje por pedido (línea base sin optimizar; no es comparable con una ruta manual real).
  - Variaciones, causas y su impacto: SV −USD 14.817,92 (SPI 0,341). Causas: ruta crítica sin presupuesto de tiempo, trabajo de calidad no planificado y herramientas locales limitadas. Impacto: 8 ítems (50 puntos) pasan al backlog de mantenimiento. Detalle en el [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md).
- **2.2 Calidad:**
  - Requisitos y criterios de aceptación: escenarios de calidad RNF-001 a RNF-010 con umbral medible y criterios Gherkin de cada RF ([Requisitos funcionales](../01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md) y [no funcionales](../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md)); estándares del curso: W3C, ISO/IEC 25010, OWASP Top 10, Green Software y WCAG.
  - Resultados de verificación y validación: **verificación:** 96 pruebas de backend (94,1 % de cobertura), 81 de frontend, 152 ejecuciones E2E (100 %) en Chromium, Firefox, WebKit y móvil, SonarQube con Quality Gate aprobado, `ruff`, `bandit`, `eslint` y `tsc` sin errores. **Validación:** SUS 79,4 (A-) con datos simulados y 30 sondeos a producción con 100 % de disponibilidad. Detalle en la [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%205/01%20Matriz%20de%20cumplimiento%20V_1_0_0.md).
  - Requisitos eximidos o variaciones: sin implementar y diferidos al mantenimiento: RF-007 (re-optimización), RF-008 (app del conductor), RF-009 (notificaciones), RNF-008 (cifrado de campos), RNF-010 (portabilidad offline); sin medir: RNF-003 (failover), RNF-004 (tareas de conductores) y prueba de penetración de RNF-002. Variaciones de formato: reportes en CSV y no en PDF.
- **2.3 Cronograma**

| Hito / Entrega | Enfoque | Fecha Planificada | Fecha Real | Variación / Impacto |
|---|---|---|---|---|
| Iteración 1: análisis y diseño (flota) | Predictivo | 14/09/2026 | 22/09/2026 (cierre del Sprint 1) | +8 días; sin impacto en la ruta crítica |
| Iteración 2: flota, pedidos y rutas | Predictivo | 05/10/2026 | 05/10/2026 flota y pedidos; rutas el 28/11/2026 | Flota y pedidos a tiempo; el motor de rutas +54 días (ruta crítica) |
| Iteración 3: dashboard, reportes y mapas | Predictivo | 26/10/2026 | 28/11/2026 | +33 días; dependía del motor de rutas |
| Calidad, seguridad y accesibilidad (SonarQube, OWASP, WCAG, CI) | Adaptativo | No planificado | 20/10/2026 al 21/10/2026 | Trabajo adicional del Sprint 3 |
| Reducción del impacto ambiental (Green IT) | Adaptativo | No planificado | 09/11/2026 al 16/11/2026 | Trabajo adicional del Sprint 4 (PR #2 y #3) |
| Pruebas E2E, CI/CD, despliegue y usabilidad | Adaptativo | No planificado | 17/11/2026 | Trabajo adicional (PR #4 a #6) |
| Iteración 4: optimización y pruebas finales | Predictivo | 16/11/2026 | 28/11/2026 | +12 días |
| Entrega del proyecto | Predictivo | 23/11/2026 | 28/11/2026 (código y reportes de cierre) | +5 días |
| Sustentación final | Predictivo | 30/11/2026 | 30/11/2026 | Según lo previsto |

- **2.4 Costo:** Presupuesto aprobado (y rango de tolerancia): **USD 22.469,00** más reserva de contingencia del 12 % (USD 2.696,28), total USD 25.165,28; no se fijó una tolerancia formal, por lo que se toma la reserva como límite. | Costo final real del proyecto: **USD 20.634,97 estimados al 30/11/2026** (USD 20.176,24 al corte del 28/11/2026), calculado con la dedicación planificada porque no hay bitácora de horas. | Análisis de variaciones e impacto: el gasto no excede el presupuesto aprobado ni toca la reserva. El valor ganado es el 34,1 % del BAC (CPI 0,379), de modo que el problema es de alcance entregado y no de sobrecosto. Terminar el alcance original costaría USD 59.251,76 (EAC), por lo que se propone reducir el alcance (ver EVM).

## 3. Resumen de Riesgos, Incidentes e Impedimentos

| ID / Descripción | Tipo (Riesgo/Incidente/Impedimento) | Impacto Real | Respuesta Aplicada |
|---|---|---|---|
| RSK-05: el optimizador no cumple los 45 s | Riesgo (alto) | **No se materializó:** 50 pedidos en 4 a 31 ms y 1.000 en menos de 1 s; la ruta crítica llegó 54 días tarde | Algoritmo de Clarke-Wright con 2-opt y límite de tiempo; pruebas de rendimiento en E2E |
| RSK-09: retraso del cronograma | Riesgo (alto) | **Se materializó:** SPI 0,341; 50 puntos diferidos | Sprint 5 dedicado a la ruta crítica (SPI de 0,116 a 0,341); re-baselining propuesto |
| DEF-001, DEF-002 y DEF-003 (bloqueo de cuenta, aislamiento de bodegas, registro público con rol de administración) | Incidente de seguridad | Detectados en el Sprint 2, antes de cualquier despliegue | Corregidos y protegidos con pruebas de regresión |
| IMP-009 / RSK-11: sin integración continua ni lint | Impedimento (herramientas) | DoD no verificable hasta el Sprint 3 | CI creado el 20/10/2026; ESLint, Ruff y Bandit incorporados en el Sprint 4 |
| IMP-012 a IMP-015: rutas largas en Windows, cobertura en CI y SonarQube | Impedimento (herramientas) | Retrasos de verificación (horas) | Estructura de carpetas, `concurrency greenlet` y normalización de cobertura (`preparar_cobertura.py`) |
| RSK-14: poca memoria para Docker | Riesgo (herramientas) | Se materializó: Docker se detenía en ejecuciones largas | Suite completa en GitHub Actions; script por tandas para uso local |
| RSK-13: datos no persistentes con SQLite en Render gratuito | Riesgo | Vigente: los datos de demostración se recargan al reiniciar | Documentado; migración a PostgreSQL en el mantenimiento |
| RSK-12: configuración insegura por defecto | Riesgo | No se materializó | `ENVIRONMENT=production`, clave propia, `/docs` oculto, cabeceras de seguridad |
| INC-01: `npm audit` con `picomatch` bloqueaba el CI | Incidente | Un día de CI en rojo (17/11/2026) | Auditoría bloqueante solo de dependencias de producción (PR #6) |
| Aceptación del Product Owner pendiente (IMP-003) | Impedimento (stakeholders) | US-001 y US-003 sin acta de aceptación | Guion de demostración y tabla de registro listos para la sustentación |

## 4. Evaluación del Éxito y Cierre

- **Satisfacción de los interesados (Stakeholders):** evaluación de usabilidad con la escala SUS: **79,4 (A-)**, por encima del umbral de 68; los datos son **simulados con fines académicos** y se repetirán con usuarios reales ([Usabilidad](../03%20Inplementaci%C3%B3n/Sprint%204/04%20Usabilidad%20V_1_0_0.md)). Metas del Acta: el plan reduce la distancia y el CO₂ muy por encima del 20 % y 25 % frente a una línea base sin optimizar, pero la medición con rutas reales de DistriRápido queda pendiente. La aceptación formal del Product Owner se registra en la sustentación.
- **Satisfacción y reconocimiento del equipo:** el [mood chart y los tableros de retrospectiva](05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md) recogen el clima del equipo por sprint. Reconocimiento: la mejora de SPI de 0,116 a 0,341 en el último sprint y la solución de problemas de herramientas (HSTS de `.app`, memoria de Docker, cobertura en CI).
- **Transición operativa y cierre administrativo:** aplicación **en producción** con despliegue automático desde `main` ([Guía de despliegue](../03%20Inplementaci%C3%B3n/Sprint%204/05%20Gu%C3%ADa%20de%20despliegue.md)); código, flujos de Actions, `README` con índice y enlaces de ida y vuelta verificados (script `verificar_enlaces.py`); backlog de mantenimiento con los 8 ítems diferidos; riesgos abiertos transferidos (RSK-13 y RSK-15). Pendientes de cierre: apuntar Render a `main`, el video final y la demostración con el Product Owner.

## Referencias cruzadas

- [Reporte de Estado](01%20Reporte%20de%20Estado%20V_1_0_0.md), [Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) y [EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- [Lecciones Aprendidas](07%20Reporte%20Final%20de%20Lecciones%20Aprendidas%20V_1_0_0.md) y [Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
- Informes de sprint: [Sprint 1](../03%20Inplementaci%C3%B3n/Sprint%2001/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md), [Sprint 2](../03%20Inplementaci%C3%B3n/Sprint%2002/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md), [Sprint 3](../03%20Inplementaci%C3%B3n/Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) y [Sprint 4](../03%20Inplementaci%C3%B3n/Sprint%204/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).
