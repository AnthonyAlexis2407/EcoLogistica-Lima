[⬅️ Volver al README Principal](../../README.md)

# Reporte de Variación (Variance Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  |  **Periodo Reportado:** acumulado del 01/09/2026 al 28/11/2026, con el Sprint 4 (21/10/2026 al 28/11/2026) como periodo actual  |  **Fecha de Corte:** 28/11/2026  |  **Versión:** 2.0.0

> **Cómo leer este reporte.** Compara lo planificado con lo real en tres dimensiones. La línea base es la del Acta de constitución y la hoja de ruta de Jira (116 puntos de historia, USD 22.469,00). Los puntos ganados siguen la regla 0/50/100 explicada en el [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md); los costos son estimaciones con supuestos declarados. SV es la variación de cronograma, CV la de costo, SPI y CPI sus índices.

## 1. Variación de Cronograma

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados** | A la fecha de corte la línea base preveía el **100 % del alcance**: 116 puntos de historia entregados (Iteración 1 hasta el 14/09, Iteración 2 hasta el 05/10, Iteración 3 hasta el 26/10 e Iteración 4 hasta el 16/11/2026, con entrega el 23/11/2026). Valor planificado acumulado: **USD 22.469,00**. |
| **Resultados Reales** | **109,5 puntos ganados de 116 (94,4 %)**: 18 ítems completos y 2 con el 50 % acreditado (EN-003, failover, y EN-006, escalado: cumplen su medida con dos instancias, pero no en la nube gratuita). No queda ningún ítem sin iniciar. Valor ganado acumulado: **USD 21.209,96**. Hitos: motor de rutas, mapa, dashboard y reportes el 28/11/2026 (planificados el 16/11 y el 26/10). |
| **Variación Obtenida** | **SV = −USD 1.259,04** y **SPI = 0,944**: el proyecto entregó el 94,4 % del valor planificado a la fecha. Historia: SPI 0,438 (Sprint 1), 0,176 (Sprint 2), 0,144 (Sprint 3) y 0,944 (Sprint 4). En el periodo actual se planificaron USD 4.261,36 y se ganaron USD 18.595,03 (SPI del periodo 4,364): el Sprint 4 recuperó el atraso acumulado de los tres sprints anteriores. |
| **Causa Raíz** | 1) **Sin control de la ruta crítica:** el spike EN-001 y el motor de rutas no tuvieron presupuesto de tiempo ni criterio de salida hasta el Sprint 4; los sprints anteriores se ocuparon con los entregables de cada inspección (calidad y seguridad, Green IT). 2) **Trabajo no planificado de calidad:** seguridad (DEF-001 a DEF-003), SonarQube, accesibilidad, rendimiento y despliegue no figuraban en el backlog y no generan valor ganado. 3) **Herramientas y entorno:** rutas largas en Windows, cobertura de CI mal medida y poca memoria para Docker retrasaron verificaciones (IMP-012 a IMP-015, RSK-14). 4) **Dependencias externas:** la demostración y la aceptación del Product Owner no tienen fecha; la conmutación por falla y el escalado automático requieren un plan de pago de la plataforma. |
| **Respuesta Planificada** | Contratar el plan de pago de la plataforma para cerrar EN-003 y EN-006 (6,5 puntos, USD 1.259,04 de valor pendiente); fijar la fecha de la demostración al inicio de cada sprint; vigilar la ruta crítica en cada revisión de sprint y reservarle tiempo propio. |

## 2. Variación de Costo

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados** | Presupuesto hasta la conclusión (BAC) de **USD 22.469,00** (recursos humanos USD 20.960,00, licencias USD 649,00 e infraestructura USD 860,00), más una reserva de contingencia del 12 % (USD 2.696,28) que se gestiona aparte. Costo previsto a la fecha de corte con la dedicación planificada: **USD 20.176,24** (BAC × 12,571 semanas ÷ 14 semanas presupuestadas). |
| **Resultados Reales** | **Costo real estimado: USD 20.176,24** (89,8 % del BAC). Es una estimación porque no hay bitácora de horas ni de facturas del equipo; se asume la dedicación planificada constante. Periodo actual: USD 8.941,74. |
| **Variación Obtenida** | **CV = +USD 1.033,72** y **CPI = 1,051**: por cada dólar gastado se obtuvo 1,05 dólares de valor. Acumulado anterior (20/10/2026): CV −USD 8.619,57 y CPI 0,233. En el periodo actual el CPI fue 2,080 (CV +USD 9.653,29). Frente al presupuesto aprobado el costo **no se excede** (89,8 % del BAC, sin tocar la reserva). |
| **Causa Raíz** | El costo se gastó al ritmo previsto y el valor ganado alcanzó casi todo el alcance cuando se aplicó el esfuerzo a la ruta crítica en el Sprint 4. Al estimar el costo por tiempo, la variación favorable refleja que se entregó más valor que el costo estimado del tiempo transcurrido, no una eficiencia medida en horas. |
| **Respuesta Planificada** | Registrar horas reales por integrante y sprint; mantener la reserva de contingencia sin usar; presupuestar aparte el plan de pago de la plataforma, que hoy es gratuito. |

## 3. Variación de Calidad

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados (Métricas/Criterios)** | Cobertura de pruebas ≥ 80 %; 0 bugs y 0 vulnerabilidades (Quality Gate); WCAG 2.1 AA sin incumplimientos; motor de rutas ≤ 45 s (RNF-001); tiempo de la API < 500 ms; pruebas E2E con 100 % de éxito en tres navegadores; usabilidad SUS ≥ 68; disponibilidad con RTO ≤ 60 s (RNF-003); 0 vulnerabilidades altas explotables (RNF-002); cifrado de campos personales (RNF-008); degradación ≤ 10 % de 250 a 1.000 pedidos (RNF-006); 30 % menos de CPU con caché (RNF-009). |
| **Resultados Reales (Defectos/Pruebas)** | Cobertura backend **93,4 %** (175 pruebas y 3 contra PostgreSQL real) y frontend con 108 pruebas; Quality Gate PASSED en SonarQube (21/10/2026), 0 hallazgos de Ruff, Bandit, ESLint y `tsc` en CI; WCAG 2.2 AA con 0 incumplimientos en axe-core en todas las pantallas; motor de rutas con 1.000 pedidos en menos de 1 s; **254 ejecuciones E2E (0 fallos; 4 pasaron tras un reintento y 2 se omiten por diseño)** en Chromium, Firefox, WebKit y móvil; la prueba de conmutación mide el RTO con dos instancias en CI; SUS 79,4 con datos **simulados**. Defectos corregidos en el ciclo: DEF-001 a DEF-003 (seguridad), la enumeración de usuarios, el registro del service worker y los supuestos erróneos de las pruebas E2E. |
| **Variación Obtenida** | **Favorable** en cobertura (+13,4 puntos), rendimiento, pruebas E2E, accesibilidad, seguridad de datos y análisis estático. **Desfavorable** en: disponibilidad medida solo en pruebas con dos instancias, sin réplica en la producción gratuita (RNF-003); SUS sin usuarios reales; sin prueba con lector de pantalla ni en un Android físico de gama baja; sin auditoría de seguridad externa. |
| **Causa Raíz** | La calidad técnica se priorizó con herramientas automáticas (CI, E2E, análisis estático, pruebas ofensivas), que se pueden ejecutar sin terceros. Lo que falta depende de terceros o de infraestructura de pago: usuarios reales, dispositivos, auditoría externa y varias instancias en la nube. |
| **Respuesta Planificada** | Mantener los umbrales en CI (cobertura 80 %, auditoría de dependencias, E2E, pruebas ofensivas y de PostgreSQL); repetir el SUS con al menos 5 usuarios reales; contratar una prueba de seguridad externa; monitorear producción con una prueba de humo horaria. Detalle en la [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%204/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md). |

## Referencias cruzadas

- Estado y proyección: [Reporte de Estado](01%20Reporte%20de%20Estado%20V_1_0_0.md). Cálculos: [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- Evidencia de calidad: [Análisis Playwright](../03%20Inplementaci%C3%B3n/Sprint%204/03%20Analisis%20PlayWrigth%20V_1_0_0.md), [Usabilidad](../03%20Inplementaci%C3%B3n/Sprint%204/04%20Usabilidad%20V_1_0_0.md) y [Calidad de código del Sprint 3](../03%20Inplementaci%C3%B3n/Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md).
- Línea base: [Presupuesto del proyecto](../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md) y [Artefactos Jira](../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md).
