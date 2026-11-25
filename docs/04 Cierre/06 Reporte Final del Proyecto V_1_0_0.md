[⬅️ Volver al README Principal](../../README.md)

# Reporte Final del Proyecto (Final Project Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  |  **Fecha de Cierre:** 28/11/2026 (fecha de corte; la sustentación es el 30/11/2026)  |  **Versión:** 2.0.0

> **Cómo leer este reporte.** Resume todo el proyecto: qué se quería, qué se logró, cuánto costó, qué problemas hubo y si fue un éxito. Distingue el trabajo **predictivo** (plan, hitos y presupuesto de la línea base) del **adaptativo** (sprints, backlog y mejoras). Líder del proyecto: Perez Ordoñez Anthony Alexis. Equipo: Fernandez Condor Jhon Smith, Perez Ordoñez Anthony Alexis y Tovar Arias Michael Aldo. Los cálculos están en el [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).

## 1. Descripción General del Proyecto

**Problema.** DistriRápido S.A.C., distribuidora de Lima, reparte pedidos de última milla con rutas armadas a mano: recorre más kilómetros de los necesarios, emite más CO₂ y no cumple siempre las ventanas horarias de las bodegas ([Acta de constitución](../01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_0.md) y [Declaración de la visión](../01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_0.md)).

**Solución.** EcoLogística Lima es una plataforma web que registra la flota y los pedidos, **planifica las rutas** con un algoritmo de optimización que respeta capacidad, volumen, Pico y Placa, zonas protegidas y ventanas horarias, las **muestra en un mapa**, guía al conductor con una **app instalable que funciona sin conexión** (entrega con firma o foto), **re-optimiza** ante incidencias, **avisa a las bodegas**, **calcula el CO₂ evitado** (y su equivalente en árboles al completar cada ruta) y **exporta reportes** en CSV, Excel y PDF. Protege los datos personales con cifrado y permite su anonimización. Está publicada en <https://ecologistica-lima.onrender.com>.

**Objetivos del Acta (metas de negocio).** Reducir la distancia recorrida en un 20 %, disminuir el CO₂ en un 25 % y cumplir el 95 % de las ventanas de entrega. **Restricciones:** 4 iteraciones hasta el 16/11/2026, entrega el 23/11/2026, presupuesto de USD 22.469,00 más 12 % de reserva, límite de 45 segundos para el optimizador.

**Enfoque híbrido.** Predictivo: Acta, presupuesto, hoja de ruta y valor ganado. Adaptativo: Scrum con 3 sprints y una etapa final, backlog en Jira, GitFlow con Pull Requests, integración y despliegue continuos.

## 2. Resumen de Desempeño

- **2.1 Alcance (Predictivo y Adaptativo):**
  - Objetivos y criterios de éxito: **Predictivo:** 20 ítems del backlog (116 puntos), 10 requisitos funcionales, 10 no funcionales y 10 reglas de negocio. **Adaptativo:** entregar incrementos verificados con definición de hecho (criterios en tres rutas, cobertura ≥ 80 %, 0 hallazgos, documentación versionada y aceptación del PO).
  - Evidencia de cumplimiento: **109,5 de 116 puntos ganados (94,4 %)**: 18 ítems completos y 2 con el 50 % (EN-003 y EN-006). Requisitos funcionales: **10 de 10 cumplidos**. Reglas de negocio: **10 de 10**. Requisitos no funcionales: 8 cumplen y 2 (RNF-003 y RNF-006) cumplen en pruebas pero no en la nube gratuita. Resultado ambiental medido en el motor: el plan optimizado recorre entre 85 % y 94 % menos kilómetros que un viaje por pedido (50, 250 y 1.000 pedidos; línea base sin optimizar, no comparable con una ruta manual real) y cumple el 100 % de las ventanas planificadas por construcción.
  - Variaciones, causas y su impacto: SV −USD 1.259,04 (SPI 0,944) por la mitad de EN-003 y EN-006. Causas: ruta crítica sin presupuesto de tiempo hasta la etapa final, trabajo de calidad no planificado y herramientas locales limitadas. Detalle en el [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md).
- **2.2 Calidad:**
  - Requisitos y criterios de aceptación: escenarios de calidad RNF-001 a RNF-010 con umbral medible y criterios Gherkin de cada RF ([Requisitos funcionales](../01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md) y [no funcionales](../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md)); estándares del curso: W3C, ISO/IEC 25010, OWASP Top 10, Green Software y WCAG.
  - Resultados de verificación y validación: **verificación:** 175 pruebas de backend (93,4 % de cobertura) y 3 contra PostgreSQL real, 108 de frontend, {E2E} ejecuciones E2E (100 %) en Chromium, Firefox, WebKit y móvil, pruebas ofensivas de seguridad, axe-core sin incumplimientos WCAG 2.2 AA, SonarQube con Quality Gate aprobado (21/10/2026), `ruff`, `bandit`, `eslint` y `tsc` sin errores. **Validación:** SUS 79,4 (A-) con datos simulados y 30 sondeos a producción con 100 % de disponibilidad. Detalle en la [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Etapa%20final/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md).
  - Requisitos eximidos o variaciones: cumplen en pruebas pero no en la nube gratuita RNF-003 (conmutación por falla) y RNF-006 (escalado automático); sin probar con lector de pantalla, con conductores reales en un Android físico ni con una auditoría de seguridad externa. Variaciones de formato: los reportes se entregan en tres formatos y la caché de resultados vive en el proceso en lugar de Redis.
- **2.3 Cronograma**

| Hito / Entrega | Enfoque | Fecha Planificada | Fecha Real | Variación / Impacto |
|---|---|---|---|---|
| Iteración 1: análisis y diseño (flota) | Predictivo | 14/09/2026 | 22/09/2026 (cierre del Sprint 1) | +8 días; sin impacto en la ruta crítica |
| Iteración 2: flota, pedidos y rutas | Predictivo | 05/10/2026 | 05/10/2026 flota y pedidos; rutas el 28/11/2026 | Flota y pedidos a tiempo; el motor de rutas +54 días (ruta crítica) |
| Iteración 3: dashboard, reportes y mapas | Predictivo | 26/10/2026 | 28/11/2026 | +33 días; dependía del motor de rutas |
| Calidad, seguridad y accesibilidad (SonarQube, OWASP, WCAG, CI) | Adaptativo | No planificado | 20/10/2026 al 21/10/2026 | Trabajo adicional del Sprint 3 |
| Reducción del impacto ambiental (Green IT) | Adaptativo | No planificado | 09/11/2026 al 16/11/2026 | Trabajo adicional de la etapa final (PR #2 y #3) |
| Pruebas E2E, CI/CD, despliegue y usabilidad | Adaptativo | No planificado | 17/11/2026 | Trabajo adicional (PR #4 a #6) |
| Iteración 4: optimización y pruebas finales (app del conductor, re-optimización, notificaciones, cifrado, PostgreSQL) | Predictivo | 16/11/2026 | 28/11/2026 | +12 días |
| Entrega del proyecto | Predictivo | 23/11/2026 | 28/11/2026 (código y reportes de cierre) | +5 días |
| Sustentación final | Predictivo | 30/11/2026 | 30/11/2026 | Según lo previsto |

- **2.4 Costo:** Presupuesto aprobado (y rango de tolerancia): **USD 22.469,00** más reserva de contingencia del 12 % (USD 2.696,28), total USD 25.165,28; no se fijó una tolerancia formal, por lo que se toma la reserva como límite. | Costo final real del proyecto: **USD 20.634,97 estimados al 30/11/2026** (USD 20.176,24 al corte del 28/11/2026), calculado con la dedicación planificada porque no hay bitácora de horas. | Análisis de variaciones e impacto: el gasto no excede el presupuesto aprobado ni toca la reserva. El valor ganado es el 94,4 % del BAC (CPI 1,051): se entregó más valor del que costó el tiempo transcurrido. La estimación a la conclusión (EAC) es USD 21.445,02, USD 1.023,98 por debajo del BAC (ver EVM). El plan de pago de la plataforma, necesario para cerrar EN-003 y EN-006, no forma parte del BAC.

## 3. Resumen de Riesgos, Incidentes e Impedimentos

| ID / Descripción | Tipo (Riesgo/Incidente/Impedimento) | Impacto Real | Respuesta Aplicada |
|---|---|---|---|
| RSK-05: el optimizador no cumple los 45 s | Riesgo (alto) | **No se materializó:** 1.000 pedidos en alrededor de 1 s; la ruta crítica llegó 54 días tarde | Algoritmo de Clarke-Wright con 2-opt y límite de tiempo; pruebas de rendimiento en E2E y estudio comparativo con otros algoritmos |
| RSK-09: retraso del cronograma | Riesgo (alto) | **Se materializó** (SPI 0,144 en el Sprint 3) y se recuperó (0,944) | Etapa final dedicado a la ruta crítica y al resto del alcance |
| DEF-001, DEF-002 y DEF-003 (bloqueo de cuenta, aislamiento de bodegas, registro público con rol de administración) | Incidente de seguridad | Detectados en el Sprint 2, antes de cualquier despliegue | Corregidos y protegidos con pruebas de regresión |
| INC-03: enumeración de usuarios en el inicio de sesión | Incidente de seguridad | Hallado por la suite ofensiva antes del cierre | Respuesta idéntica para correos desconocidos, con el mismo contador y bloqueo, y cálculo de relleno para igualar el tiempo |
| INC-04: el service worker no se registraba | Incidente | Hallado por la prueba E2E sin conexión; la app no abría sin red | Registro inmediato si el evento `load` ya ocurrió y lista de precarga generada en la compilación |
| IMP-009 / RSK-11: sin integración continua ni lint | Impedimento (herramientas) | DoD no verificable hasta el Sprint 3 | CI creado el 20/10/2026; ESLint, Ruff y Bandit incorporados en la etapa final |
| IMP-012 a IMP-015: rutas largas en Windows, cobertura en CI y SonarQube | Impedimento (herramientas) | Retrasos de verificación (horas) | Estructura de carpetas, `concurrency greenlet` y normalización de cobertura (`preparar_cobertura.py`) |
| RSK-14: poca memoria para Docker | Riesgo (herramientas) | Se materializó: Docker se detenía en ejecuciones largas | Suite completa en GitHub Actions; script por tandas para uso local |
| RSK-13: datos no persistentes con SQLite en Render gratuito | Riesgo | **Resuelto:** la producción usa una base PostgreSQL gestionada (definida en `render.yaml`) | Migración con pruebas contra PostgreSQL real en CI |
| RSK-17: la base PostgreSQL gratuita caduca a los 30 días | Riesgo | Vigente | Plan de pago para operar y respaldo; advertido en la guía de despliegue |
| RSK-18: perder la clave de cifrado deja ilegibles los datos | Riesgo | Vigente | Clave propia guardada como secreto y sin rotarla sin migrar |
| RSK-12: configuración insegura por defecto | Riesgo | No se materializó | `ENVIRONMENT=production`, clave propia, `/docs` oculto, cabeceras de seguridad y HSTS |
| INC-01: `npm audit` con `picomatch` bloqueaba el CI | Incidente | Un día de CI en rojo (17/11/2026) | Auditoría bloqueante solo de dependencias de producción (PR #6) |
| Aceptación del Product Owner pendiente (IMP-003) | Impedimento (stakeholders) | Las historias sin acta de aceptación | Guion de demostración y tabla de registro listos para la sustentación |

## 4. Evaluación del Éxito y Cierre

- **Satisfacción de los interesados (Stakeholders):** evaluación de usabilidad con la escala SUS: **79,4 (A-)**, por encima del umbral de 68; los datos son **simulados con fines académicos** y se repetirán con usuarios reales ([Usabilidad](../03%20Inplementaci%C3%B3n/Etapa%20final/04%20Usabilidad%20V_1_0_0.md)). Metas del Acta: el plan reduce la distancia y el CO₂ muy por encima del 20 % y 25 % frente a una línea base sin optimizar y cumple por construcción las ventanas planificadas, pero la medición con rutas reales de DistriRápido queda pendiente. La aceptación formal del Product Owner se registra en la sustentación.
- **Satisfacción y reconocimiento del equipo:** el [mood chart y los tableros de retrospectiva](05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md) recogen el clima del equipo por sprint. Reconocimiento: la recuperación del SPI de 0,144 a 0,944 en el último sprint y la solución de problemas de herramientas (HSTS de `.app`, memoria de Docker, cobertura en CI).
- **Transición operativa y cierre administrativo:** aplicación **en producción** con despliegue automático desde `main` ([Guía de despliegue](../03%20Inplementaci%C3%B3n/Etapa%20final/05%20Gu%C3%ADa%20de%20despliegue.md)); código, flujos de Actions, `README` con índice y enlaces de ida y vuelta verificados (script `verificar_enlaces.py`); backlog de mantenimiento con EN-003 y EN-006 (plan de pago de la plataforma); riesgos abiertos transferidos (RSK-15, RSK-17 y RSK-18). Pendientes de cierre: apuntar Render a `main`, el video final y la demostración con el Product Owner.

## Referencias cruzadas

- [Reporte de Estado](01%20Reporte%20de%20Estado%20V_1_0_0.md), [Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) y [EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- [Lecciones Aprendidas](07%20Reporte%20Final%20de%20Lecciones%20Aprendidas%20V_1_0_0.md) y [Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
- Informes de sprint: [Sprint 1](../03%20Inplementaci%C3%B3n/Sprint%2001/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md), [Sprint 2](../03%20Inplementaci%C3%B3n/Sprint%2002/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md), [Sprint 3](../03%20Inplementaci%C3%B3n/Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) y [Etapa final](../03%20Inplementaci%C3%B3n/Etapa%20final/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).
