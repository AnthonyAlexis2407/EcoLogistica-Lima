[⬅️ Volver al README Principal](../../README.md)

# Reporte de Variación (Variance Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  |  **Periodo Reportado:** acumulado del 01/09/2026 al 28/11/2026, con el Sprint 5 (17/11/2026 al 28/11/2026) como periodo actual  |  **Fecha de Corte:** 28/11/2026  |  **Versión:** 1.0.0

> **Cómo leer este reporte.** Compara lo planificado con lo real en tres dimensiones. La línea base es la del Acta de constitución y la hoja de ruta de Jira (116 puntos de historia, USD 22.469,00). Los puntos ganados siguen la regla 0/50/100 explicada en el [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md); los costos son estimaciones con supuestos declarados. SV es la variación de cronograma, CV la de costo, SPI y CPI sus índices.

## 1. Variación de Cronograma

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados** | A la fecha de corte la línea base preveía el **100 % del alcance**: 116 puntos de historia entregados (Iteración 1 hasta el 14/09, Iteración 2 hasta el 05/10, Iteración 3 hasta el 26/10 e Iteración 4 hasta el 16/11/2026, con entrega el 23/11/2026). Valor planificado acumulado: **USD 22.469,00**. |
| **Resultados Reales** | **39,5 puntos ganados de 116 (34,1 %)**: 3 ítems completos (US-001, US-003 y EN-005) y 9 parciales con el 50 % acreditado (EN-001, EN-002, EN-007, EN-009, US-005, US-007, US-008, US-009 y US-010). Siguen sin iniciar 8 ítems (50 puntos). Valor ganado acumulado: **USD 7.651,08**. Hitos: motor de rutas el 28/11/2026 (planificado el 16/11), dashboard y reportes el 28/11/2026 (planificado el 26/10). |
| **Variación Obtenida** | **SV = −USD 14.817,92** y **SPI = 0,341**: el proyecto entregó la tercera parte del alcance planificado a la fecha. Historia: SPI 0,000 (Sprint 1), 0,154 (Sprint 2), 0,128 (Sprint 3), 0,116 (Sprint 4) y 0,341 (Sprint 5). En el periodo actual el valor planificado es 0 (la línea base ya estaba completa), por lo que el SPI del periodo no se define; el Sprint 5 ganó USD 5.036,16, el 22,4 % del BAC. |
| **Causa Raíz** | 1) **Sin control de la ruta crítica:** el spike EN-001 y el motor de rutas no tuvieron presupuesto de tiempo ni criterio de salida; los sprints se ocuparon con los entregables de cada inspección (calidad y seguridad, Green IT, pruebas E2E, CI/CD). 2) **Trabajo no planificado de calidad:** seguridad (DEF-001 a DEF-003), SonarQube, accesibilidad, rendimiento y despliegue no figuraban en el backlog y no generan valor ganado. 3) **Herramientas y entorno:** rutas largas en Windows, cobertura de CI mal medida y poca memoria para Docker retrasaron verificaciones (IMP-012 a IMP-015, RSK-14). 4) **Dependencias externas:** la demostración y la aceptación del Product Owner no tienen fecha. |
| **Respuesta Planificada** | Aprobar con el Product Owner el **re-baselining** (8 ítems, 50 puntos, al backlog de mantenimiento; 3 cambios de alcance de calidad incorporados) que lleva el SPI a 0,721; ejecutar el spike comparativo de algoritmos con tope de 3 días; fijar la fecha de la demostración al inicio de cada sprint; vigilar la ruta crítica en cada revisión de sprint. |

## 2. Variación de Costo

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados** | Presupuesto hasta la conclusión (BAC) de **USD 22.469,00** (recursos humanos USD 20.960,00, licencias USD 649,00 e infraestructura USD 860,00), más una reserva de contingencia del 12 % (USD 2.696,28) que se gestiona aparte. Costo previsto a la fecha de corte con la dedicación planificada: **USD 20.176,24** (BAC × 12,571 semanas ÷ 14 semanas presupuestadas). |
| **Resultados Reales** | **Costo real estimado: USD 20.176,24** (89,8 % del BAC). Es una estimación porque no hay bitácora de horas ni de facturas del equipo; se asume la dedicación planificada constante. Periodo actual: USD 2.751,31. |
| **Variación Obtenida** | **CV = −USD 12.525,16** y **CPI = 0,379**: por cada dólar gastado se obtuvo 0,38 dólares de valor. Acumulado anterior (16/11/2026): CV −USD 14.810,01 y CPI 0,150. En el periodo actual el CPI fue 1,830 (CV +USD 2.284,85), la primera mejora del proyecto. Frente al presupuesto aprobado el costo **no se excede** (89,8 % del BAC, sin tocar la reserva). |
| **Causa Raíz** | El costo se gastó al ritmo previsto, pero el valor ganado fue bajo por las causas del cronograma: alcance diferido y trabajo de calidad no acreditado en el backlog. Al estimar el costo por tiempo, la variación refleja solo el valor no entregado, no una ineficiencia medida en horas. |
| **Respuesta Planificada** | Registrar horas reales por integrante y sprint; reasignar el BAC al alcance re-baselineado (EV 72,1 % del BAC, CPI 0,803); mantener la reserva de contingencia sin usar; no autorizar gasto adicional para el alcance diferido sin una nueva estimación. |

## 3. Variación de Calidad

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados (Métricas/Criterios)** | Cobertura de pruebas ≥ 80 %; 0 bugs y 0 vulnerabilidades (Quality Gate); WCAG 2.1 AA sin incumplimientos; motor de rutas ≤ 45 s con 50 pedidos (RNF-001); tiempo de la API < 500 ms; pruebas E2E con 100 % de éxito en tres navegadores; usabilidad SUS ≥ 68; disponibilidad ≥ 99,5 % (RNF-003); 0 vulnerabilidades altas explotables verificadas con prueba de penetración (RNF-002); cifrado de campos personales (RNF-008). |
| **Resultados Reales (Defectos/Pruebas)** | Cobertura backend **94,1 %** (96 pruebas) y frontend con 81 pruebas; Quality Gate PASSED, 0 bugs y 0 vulnerabilidades en SonarQube (21/10/2026); WCAG 2.2 AA con 0 incumplimientos en axe-core; motor de rutas: **50 pedidos en 4 a 31 ms** y 1.000 pedidos en menos de 1 s; API con mediana de 2,1 a 6,4 ms en el contenedor y 295 ms en producción; **152 de 152 ejecuciones E2E (100 %)**; SUS 79,4 con datos **simulados**; disponibilidad 100 % en 30 sondeos a producción. Defectos corregidos en el ciclo: DEF-001, DEF-002 y DEF-003 (seguridad), 5 supuestos erróneos de las pruebas E2E y 7 brechas frente a los criterios de aceptación (4 cerradas, 3 abiertas). |
| **Variación Obtenida** | **Favorable** en cobertura (+14,1 puntos), rendimiento (el motor usa menos del 0,1 % del límite de 45 s), pruebas E2E, accesibilidad y análisis estático. **Desfavorable** en: prueba de penetración sin realizar (RNF-002), cifrado de campos sin implementar (RNF-008), disponibilidad medida con una muestra corta (RNF-003, sin failover), tiempo de tarea de conductores no medible sin la app móvil (RNF-004) y SUS sin usuarios reales. |
| **Causa Raíz** | La calidad técnica se priorizó con herramientas automáticas (CI, E2E, análisis estático), que se pueden ejecutar sin terceros. Lo que falta depende de terceros o de componentes sin construir: pentest, usuarios reales, app móvil, alta disponibilidad. |
| **Respuesta Planificada** | Mantener los umbrales en CI (cobertura 80 %, auditoría de dependencias, E2E); repetir el SUS con al menos 5 usuarios reales; programar la prueba de penetración y el cifrado de campos en el backlog de mantenimiento; monitorear producción con una prueba de humo horaria; cerrar las 3 brechas funcionales abiertas (filtros del dashboard, PDF y cierre de ruta). Detalle en la [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%205/01%20Matriz%20de%20cumplimiento%20V_1_0_0.md). |

## Referencias cruzadas

- Estado y proyección: [Reporte de Estado](01%20Reporte%20de%20Estado%20V_1_0_0.md). Cálculos: [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- Evidencia de calidad: [Análisis Playwright](../03%20Inplementaci%C3%B3n/Sprint%204/03%20Analisis%20PlayWrigth%20V_1_0_0.md), [Usabilidad](../03%20Inplementaci%C3%B3n/Sprint%204/04%20Usabilidad%20V_1_0_0.md) y [Calidad de código del Sprint 3](../03%20Inplementaci%C3%B3n/Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md).
- Línea base: [Presupuesto del proyecto](../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md) y [Artefactos Jira](../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md).
