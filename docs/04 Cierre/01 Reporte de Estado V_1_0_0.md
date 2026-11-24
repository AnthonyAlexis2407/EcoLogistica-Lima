[⬅️ Volver al README Principal](../../README.md)

# Reporte de Estado del Proyecto (Status Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.
- **Fecha de Corte:** 28/11/2026
- **Versión:** 1.0.0

**Periodo reportado:** Sprint 5 (17/11/2026 al 28/11/2026), comparado con el periodo anterior, Sprint 4 (21/10/2026 al 16/11/2026). Líder del proyecto: Perez Ordoñez Anthony Alexis.

> **Cómo leer este reporte.** Es un resumen ejecutivo. Los cálculos de cronograma y costo están en el [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) y en el [Reporte de Valor Ganado (EVM)](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md). Los valores de costo se **estiman** con los supuestos declarados en el EVM porque el equipo no llevó una bitácora de horas.

## 1. Información de Alcance

- **Logros completados:**
  - **Motor de optimización de rutas (RF-003, EN-001, EN-005):** algoritmo de ahorros de Clarke-Wright con mejora 2-opt. Planifica 1.000 pedidos en menos de 1 segundo y los 50 pedidos de la prueba E2E en 4 a 31 milisegundos, muy por debajo del límite de 45 segundos (RNF-001).
  - **Reglas de negocio en la planificación:** exclusión por Pico y Placa sin exoneración (RN-002), rechazo explícito de pedidos con ventana horaria imposible y bloqueo de vehículos sin factor de emisión de CO₂.
  - **Mapa interactivo de rutas (RF-004, US-007):** mapa con Leaflet y OpenStreetMap, más una tabla equivalente en texto (accesible).
  - **Dashboard con datos reales (RF-005, US-008)**, **CO₂ evitado y árboles equivalentes (RF-010, US-010)** y **reportes CSV exportables (RF-006, US-009)** con protección contra inyección de fórmulas.
  - **Pruebas automáticas:** 96 del backend (cobertura 94,1 %), 81 del frontend y **152 ejecuciones E2E (100 %)** en Chromium, Firefox, WebKit y móvil; los cuatro flujos de GitHub Actions en verde.
  - **Producción:** aplicación publicada en <https://ecologistica-lima.onrender.com> con despliegue automático.
  - **Documentación de cierre:** matriz de cumplimiento de requisitos y estándares ([Sprint 5](../03%20Inplementaci%C3%B3n/Sprint%205/01%20Matriz%20de%20cumplimiento%20V_1_0_0.md)) y los siete documentos de esta carpeta.
- **Cambios al alcance (adiciones, eliminaciones o modificaciones):**
  - **Modificación:** los reportes se entregan en CSV, que abre en Excel, y no en PDF (RF-006). El mapa atiende al operador; la versión para el conductor depende de la app móvil, que no se construyó (RF-004).
  - **Adición:** reglas de Pico y Placa, ventanas imposibles y factor de emisión obligatorio, que los criterios de aceptación de RF-003 y RF-010 exigían y estaban sin implementar.
  - **Diferimiento propuesto (pendiente de aprobación del Product Owner):** 8 ítems del backlog, equivalentes a 50 de 116 puntos, pasan al backlog de mantenimiento: US-002, US-004, US-006, EN-003, EN-004, EN-006, EN-008 y EN-010. Es la base del re-baselining que se plantea en el [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- **Información de calidad (defectos o incidentes detectados):**
  - **Brechas frente a los criterios de aceptación (auditoría del 24/11/2026):** 7 detectadas. Se cerraron 4 (Pico y Placa, ventanas imposibles, factor de CO₂ y registro de accesos denegados). Siguen abiertas 3: filtros por distrito y fechas en el dashboard (RF-005), exportación en PDF (RF-006) y cierre de ruta en estado "Completada" (RF-010).
  - **Incidente de dependencias (CI):** `npm audit` marcó `picomatch` (ReDoS, sin corrección publicada) en herramientas de desarrollo; se resolvió el 17/11/2026 auditando con bloqueo solo las dependencias de producción (PR #6).
  - **Defectos del producto en el periodo:** ninguno abierto; las pruebas nuevas no encontraron defectos en el código existente.

## 2. Información de Cronograma

- **Actividades/Hitos planificados pero no completados:**
  - Hito "Iteración 4: optimización y pruebas finales" (16/11/2026): el motor de optimización se completó el 28/11/2026, 12 días después de lo planificado.
  - Spike EN-001 (planificado para la Iteración 2, 05/10/2026): se cerró en el Sprint 5, 54 días tarde, y sin la comparación con algoritmo genético, búsqueda tabú y OR-Tools que pedía su criterio de salida.
  - Dashboard, reportes y mapa (Iteración 3, 26/10/2026): completados el 28/11/2026, 33 días tarde.
  - Sin cumplir: app móvil del conductor (RF-008), notificaciones a clientes (RF-009), re-optimización dinámica (RF-007), cifrado de campos personales (EN-008), prueba de penetración (EN-002) y la demostración en vivo con el Product Owner.
- **Causa raíz de las desviaciones:**
  1. **Control de la ruta crítica ausente:** los Sprints 2 a 4 se dedicaron a los entregables de cada inspección (calidad y seguridad, Green IT, pruebas E2E y CI/CD), mientras la ruta crítica (EN-001 → US-005 → US-007 → US-008) no tenía presupuesto de tiempo propio. Es la causa raíz ya identificada en la [Retrospectiva del Sprint 3](../03%20Inplementaci%C3%B3n/Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).
  2. **Herramientas y entorno:** rutas de más de 260 caracteres en Windows (IMP-012), cobertura mal medida en CI (IMP-013), memoria insuficiente de Docker (IMP-014, RSK-14) y lectura de cobertura en SonarQube (IMP-015) consumieron tiempo de verificación.
- **Impacto en próximos hitos o en la ruta crítica:** la ruta crítica quedó completa a nivel de MVP el 28/11/2026. La sustentación del 30/11/2026 no se afecta. Los 50 puntos diferidos no alcanzan a entregarse antes del cierre.
- **Acciones correctivas o preventivas planificadas:** (1) formalizar el re-baselining con el Product Owner; (2) abrir el backlog de mantenimiento con los 8 ítems diferidos, ordenados por riesgo; (3) ejecutar un spike comparativo formal de algoritmos con tope de 3 días; (4) fijar con el docente, al inicio de cada sprint, la fecha de la demostración.

## 3. Información de Costos

- **Fondos ejecutados en este periodo:** USD 2.751,31 estimados para el Sprint 5. El acumulado estimado es **USD 20.176,24**, el 89,8 % del presupuesto hasta la conclusión (BAC) de USD 22.469,00.
- **Causa raíz de la variación (mano de obra, materiales o estimaciones):** el costo se estima con la dedicación planificada constante (BAC × semanas transcurridas ÷ 14 semanas) porque no existe bitácora de horas. La variación de costo acumulada es de **−USD 12.525,16** (CPI 0,379) porque el valor ganado, USD 7.651,08, es el 34,1 % del BAC: el costo se gastó según lo previsto, pero el alcance entregado fue menor que el planificado. En el periodo, el Sprint 5 ganó USD 5.036,16 con un costo de USD 2.751,31 (CPI del periodo 1,830).
- **Impacto en el presupuesto general o reserva de contingencia:** el costo estimado no supera el presupuesto aprobado. La reserva de contingencia de USD 2.696,28 (12 %) no se usó. El impacto es de **valor**, no de sobrecosto: terminar todo el alcance original al ritmo actual costaría USD 59.251,76 (EAC), que no está financiado; por eso se propone reducir el alcance.
- **Acciones correctivas o preventivas planificadas:** registrar las horas reales por integrante y sprint desde la próxima iteración; aprobar el re-baselining para que el BAC se asigne al alcance que realmente se entrega; mantener la reserva de contingencia intacta hasta esa aprobación.

## 4. Proyección (Look Ahead)

- **Logros/Entregables planificados para el próximo periodo (29/11/2026 al 30/11/2026):**
  - Sustentación final del 30/11/2026: 10 minutos de gestión y cierre y 10 minutos de demostración técnica.
  - Video MP4 de 5 minutos (1 minuto de presentación de la idea y 4 de demostración funcional) en `docs/05 Video proyecto`.
  - Apuntar el servicio de Render a la rama `main` y fusionar los Pull Requests del cierre.
  - Completar la tabla de la demostración con el docente y registrar la aceptación de US-001 y US-003.
- **Costos planificados para el próximo periodo:** USD 458,55 estimados, correspondientes a 2 días a la dedicación planificada (USD 1.604,93 por semana).

## 5. Riesgos, Incidentes y Comentarios

- **Nuevos riesgos identificados:**
  - **RSK-15:** el video de cierre no se produce a tiempo o sin la calidad exigida (probabilidad 3, impacto 4, severidad 12). Mitigación: [guion minuto a minuto](../05%20Video%20proyecto/Guion%20del%20video.md) y lista de verificación listos.
  - **RSK-16:** las teselas del mapa dependen de un servicio externo (OpenStreetMap) (probabilidad 2, impacto 2, severidad 4). Mitigación: si no cargan, el recorrido, las paradas y la tabla siguen visibles; la política de seguridad solo admite ese dominio.
- **Nuevos incidentes (Issues) surgidos:**
  - **INC-01 (resuelto):** aviso de dependencia `picomatch` bloqueaba el CI (PR #6, 17/11/2026).
  - **INC-02 (abierto):** el servicio de Render sigue apuntando a la rama `feature/sprint-4`; se cambia a `main` en su panel.
- **Comentarios relevantes:** los datos de la evaluación de usabilidad (SUS 79,4) son simulados con fines académicos y se reemplazarán con usuarios reales; los valores de costo son estimaciones declaradas; la aceptación del Product Owner de US-001 y US-003 sigue pendiente de la demostración en vivo.

## Referencias cruzadas

- Cronograma y costo en detalle: [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) y [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- Visualización: [Tableros de Control](04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md) y [Radiadores de Información](05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md).
- Cierre: [Reporte Final](06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md) y [Lecciones Aprendidas](07%20Reporte%20Final%20de%20Lecciones%20Aprendidas%20V_1_0_0.md).
- Registro de riesgos: [03 Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
