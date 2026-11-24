[⬅️ Volver al README Principal](../../README.md)

# Reporte de Estado del Proyecto (Status Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.
- **Fecha de Corte:** 28/11/2026
- **Versión:** 2.0.0

**Periodo reportado:** Sprint 4 (21/10/2026 al 28/11/2026), comparado con el periodo anterior, Sprint 3 (06/10/2026 al 20/10/2026). El proyecto tiene cuatro sprints; el cuarto se extendió hasta la fecha de corte para cerrar todo el alcance. Líder del proyecto: Perez Ordoñez Anthony Alexis.

> **Cómo leer este reporte.** Es un resumen ejecutivo. Los cálculos de cronograma y costo están en el [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) y en el [Reporte de Valor Ganado (EVM)](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md). Los valores de costo se **estiman** con los supuestos declarados en el EVM porque el equipo no llevó una bitácora de horas.

## 1. Información de Alcance

- **Logros completados:**
  - **Motor de optimización de rutas (RF-003, EN-001, EN-005):** ahorros de Clarke-Wright con mejora 2-opt y **ventanas horarias, capacidad de peso y volumen, Pico y Placa y zonas protegidas como restricciones duras**; caché de planes; búsqueda tabú opcional. Planifica 1.000 pedidos en menos de 1 segundo (límite de 45 s, RNF-001). El estudio comparativo EN-001 con búsqueda tabú, algoritmo genético y OR-Tools se ejecutó y está publicado.
  - **Ciclo completo de la ruta (RF-007, RF-008, RF-010):** planificar, asignar conductor, iniciar, entregar con firma o foto, reprogramar, re-optimizar ante vía cerrada, accidente, avería o pedido cancelado (y de forma automática ante un retraso) y completar la ruta registrando el CO₂ evitado y los árboles equivalentes.
  - **App del conductor (RF-004, RF-008, RNF-004, RNF-010):** PWA instalable que abre sin conexión, con mapa, seguimiento de desvío de más de 500 m, entrega en 3 toques y sincronización idempotente.
  - **Portal y notificaciones (RF-009):** avisos de asignación con hora estimada, salida en ruta, retraso, reprogramación y entrega, aislados por bodega (RN-010).
  - **Dashboard, reportes y administración (RF-005, RF-006):** filtros por distrito y fechas, combustible ahorrado, reportes CSV, Excel y PDF (el auditor los recibe sin datos personales), administración de usuarios, conductores, parámetros del algoritmo y zonas protegidas.
  - **Datos y seguridad (RNF-002, RNF-008):** datos personales y de ubicación cifrados con AES-SIV, anonimización en 5 días hábiles, suite de pruebas ofensivas automáticas, HSTS y base PostgreSQL de producción.
  - **Pruebas automáticas:** 175 del backend (93,4 % de cobertura) más 3 contra PostgreSQL real, 108 del frontend y **{E2E} ejecuciones E2E** en Chromium, Firefox, WebKit y móvil; los flujos de GitHub Actions en verde.
  - **Producción:** aplicación publicada en <https://ecologistica-lima.onrender.com> con despliegue automático.
  - **Documentación de cierre:** [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%204/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md) y los siete documentos de esta carpeta.
- **Cambios al alcance (adiciones, eliminaciones o modificaciones):**
  - **Sin eliminaciones ni diferimientos:** los 20 ítems del backlog (116 puntos) están implementados; dos de ellos, EN-003 (failover) y EN-006 (escalado), cumplen su medida en pruebas con dos instancias pero no en la nube gratuita y por eso ganan el 50 % de sus puntos.
  - **Modificaciones:** los reportes se entregan en tres formatos (CSV, Excel y PDF); la persistencia pasa de SQLite a PostgreSQL en producción; la caché de resultados vive en el proceso y no en Redis.
  - **Adiciones:** administración de usuarios, conductores, parámetros y zonas protegidas, y el portal de privacidad (solicitudes de eliminación), necesarios para cumplir RF-008, RN-003 y RN-008.
- **Información de calidad (defectos o incidentes detectados):**
  - **Brechas frente a los criterios de aceptación (auditoría de requisitos):** se hallaron brechas en casi todos los requisitos funcionales y no funcionales; **todas se cerraron** con código y pruebas (ver la [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%204/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md)).
  - **Defecto de seguridad hallado y corregido:** el inicio de sesión revelaba si un correo existía (el mensaje de intentos restantes solo aparecía para cuentas reales). Ahora un correo desconocido recibe la misma respuesta, el mismo contador de intentos y el mismo bloqueo, y el tiempo de respuesta se iguala con un cálculo bcrypt de relleno.
  - **Incidente del service worker:** la PWA no se registraba porque el arranque diferido de la aplicación ocurre después del evento `load`; se detectó con la prueba E2E sin conexión y se corrigió.
  - **Incidente de dependencias (CI):** `npm audit` marcó `picomatch` en herramientas de desarrollo; se resolvió el 17/11/2026 (PR #6).

## 2. Información de Cronograma

- **Actividades/Hitos planificados pero no completados:**
  - Ninguna actividad del backlog queda sin construir, pero varias llegaron tarde frente a la hoja de ruta: el hito "Iteración 4: optimización y pruebas finales" (16/11/2026) se completó el 28/11/2026, 12 días después; el spike EN-001 (Iteración 2, 05/10/2026) se cerró 54 días tarde; el dashboard, los reportes y el mapa (Iteración 3, 26/10/2026) llegaron el 28/11/2026, 33 días tarde.
  - Pendientes que dependen de terceros: la demostración en vivo con el Product Owner, el SUS con usuarios reales, la auditoría de seguridad externa y el plan de pago de la plataforma para habilitar conmutación y escalado en la nube.
- **Causa raíz de las desviaciones:**
  1. **Control de la ruta crítica ausente:** los Sprints 2 y 3 se dedicaron a los entregables de cada inspección (calidad y seguridad, Green IT), mientras la ruta crítica (EN-001 → US-005 → US-007 → US-008) no tenía presupuesto de tiempo propio. Es la causa raíz ya identificada en la [Retrospectiva del Sprint 3](../03%20Inplementaci%C3%B3n/Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).
  2. **Herramientas y entorno:** rutas de más de 260 caracteres en Windows (IMP-012), cobertura mal medida en CI (IMP-013), memoria insuficiente de Docker (IMP-014, RSK-14) y lectura de cobertura en SonarQube (IMP-015) consumieron tiempo de verificación; la suite completa se ejecuta en GitHub Actions.
- **Impacto en próximos hitos o en la ruta crítica:** la ruta crítica quedó completa el 28/11/2026. La sustentación del 30/11/2026 no se afecta.
- **Acciones correctivas o preventivas planificadas:** (1) fijar con el docente, al inicio de cada sprint, la fecha de la demostración; (2) reservar presupuesto de tiempo para la ruta crítica en cada plan de sprint; (3) activar el plan de pago de la plataforma para cerrar EN-003 y EN-006; (4) repetir el SUS con usuarios reales.

## 3. Información de Costos

- **Fondos ejecutados en este periodo:** USD 8.941,74 estimados para el Sprint 4. El acumulado estimado es **USD 20.176,24**, el 89,8 % del presupuesto hasta la conclusión (BAC) de USD 22.469,00.
- **Causa raíz de la variación (mano de obra, materiales o estimaciones):** el costo se estima con la dedicación planificada constante (BAC × semanas transcurridas ÷ 14 semanas) porque no existe bitácora de horas. La variación de costo acumulada es **+USD 1.033,72** (CPI 1,051): el valor ganado, USD 21.209,96, es el 94,4 % del BAC con el 89,8 % del costo. En el periodo, el Sprint 4 ganó USD 18.595,03 con un costo estimado de USD 8.941,74 (CPI del periodo 2,080), porque concentró la implementación de casi todo el alcance.
- **Impacto en el presupuesto general o reserva de contingencia:** el costo estimado no supera el presupuesto aprobado. La reserva de contingencia de USD 2.696,28 (12 %) no se usó. La estimación a la conclusión es **USD 21.445,02** (EAC), USD 1.023,98 por debajo del BAC.
- **Acciones correctivas o preventivas planificadas:** registrar las horas reales por integrante y sprint desde la primera iteración del próximo proyecto; mantener la reserva intacta; presupuestar aparte el plan de pago de la plataforma (base de datos y varias instancias), que hoy es gratuito y no forma parte del BAC.

## 4. Proyección (Look Ahead)

- **Logros/Entregables planificados para el próximo periodo (29/11/2026 al 30/11/2026):**
  - Sustentación final del 30/11/2026: 10 minutos de gestión y cierre y 10 minutos de demostración técnica.
  - Video MP4 de 5 minutos (1 minuto de presentación de la idea y 4 de demostración funcional) en `docs/05 Video proyecto`.
  - Fusionar el Pull Request del cierre y apuntar el servicio de Render a la rama `main`.
  - Completar la tabla de la demostración con el docente y registrar la aceptación de las historias.
- **Costos planificados para el próximo periodo:** USD 458,55 estimados, correspondientes a 2 días a la dedicación planificada (USD 1.604,93 por semana).

## 5. Riesgos, Incidentes y Comentarios

- **Nuevos riesgos identificados:**
  - **RSK-17:** la base PostgreSQL gratuita de Render caduca a los 30 días y borra los datos (probabilidad 3, impacto 3, severidad 9). Mitigación: pasar a un plan de pago para operar y conservar un respaldo; está advertido en la [Guía de despliegue](../03%20Inplementaci%C3%B3n/Sprint%204/05%20Gu%C3%ADa%20de%20despliegue.md).
  - **RSK-18:** perder o cambiar `DATA_ENCRYPTION_KEY` deja ilegibles los datos personales cifrados (probabilidad 2, impacto 5, severidad 10). Mitigación: guardar la clave en un gestor de secretos y no rotarla sin migrar los datos.
  - **RSK-15 y RSK-16** (video de cierre y dependencia de las teselas de OpenStreetMap) siguen vigentes con sus mitigaciones.
- **Nuevos incidentes (Issues) surgidos:**
  - **INC-01 (resuelto):** aviso de dependencia `picomatch` bloqueaba el CI (PR #6, 17/11/2026).
  - **INC-02 (abierto):** el servicio de Render sigue apuntando a la rama `feature/sprint-4`; se cambia a `main` en su panel.
  - **INC-03 (resuelto):** enumeración de usuarios en el inicio de sesión.
  - **INC-04 (resuelto):** el service worker no se registraba tras el arranque diferido.
- **Comentarios relevantes:** los datos de la evaluación de usabilidad (SUS 79,4) son simulados con fines académicos y se reemplazarán con usuarios reales; los valores de costo son estimaciones declaradas; la aceptación del Product Owner sigue pendiente de la demostración en vivo.

## Referencias cruzadas

- Cronograma y costo en detalle: [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) y [Reporte de EVM](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- Visualización: [Tableros de Control](04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md) y [Radiadores de Información](05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md).
- Cierre: [Reporte Final](06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md) y [Lecciones Aprendidas](07%20Reporte%20Final%20de%20Lecciones%20Aprendidas%20V_1_0_0.md).
- Registro de riesgos: [03 Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
