# Registro de Riesgos del Proyecto

## Metadatos
- **Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles
- **Integrantes:**
  - Fernandez Condor Jhon Smith
  - Perez Ordoñez Anthony Alexis
  - Tovar Arias Michael Aldo
- **Fecha:** 08 de septiembre de 2026 (actualizado el 28 de noviembre de 2026)
- **Versión:** 1.5.0

[← Volver al README Principal](../../README.md)

---

## Metodología de Evaluación (PMBOK / CMMI)

**Severidad (Exposición) = Probabilidad (1 a 5) × Impacto (1 a 5)**

- **Probabilidad:** 1 (Muy baja) a 5 (Muy alta)
- **Impacto:** 1 (Insignificante) a 5 (Catastrófico)
- **Severidad:** Low (1-6), Medium (8-12), High (15-25)

## Matriz de Evaluación de Riesgos

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) | Responsable |
|---|---|---|---|---|---|---|---|---|
| **RSK-01** | Indisponibilidad de servicios Cloud en el proveedor por límites de cuota. | Técnica / Infraestructura | 2 | 4 | **8 (Media)** | Monitorear consumo de cuotas e implementar alertas de umbral al 70%. | Migrar temporalmente los contenedores a una cuenta secundaria de respaldo. | Tovar Arias Michael Aldo (BD/Infra) |
| **RSK-02** | Curva de aprendizaje elevada en el framework del frontend. | Recursos Humanos / Capacidades | 3 | 3 | **9 (Media)** | Realizar 2 jornadas de *Pair Programming* y pases de conocimiento al inicio del Sprint. | Reasignar las tareas de mayor complejidad al integrante con más experiencia en React. | Perez Ordoñez Anthony Alexis (Frontend/PM) |
| **RSK-03** | Caída o indisponibilidad de la API de tráfico/mapas en tiempo real (Google Maps API). | Técnica / Dependencia Externa | 3 | 4 | **12 (Media)** | Implementar *circuit breaker* y monitoreo activo de la disponibilidad de la API. | Activar el fallback ya documentado (S05) hacia OpenStreetMap con datos de tráfico históricos. | Fernandez Condor Jhon Smith (Backend) |
| **RSK-04** | Presupuesto insuficiente frente al escalamiento hacia 1,000 pedidos/día (R06). | Financiera | 2 | 5 | **10 (Media)** | Control de gastos quincenal y arquitectura con auto-scaling para evitar sobreaprovisionamiento. | Priorizar el backlog para diferir funcionalidades no críticas (ej. compensación de carbono) a una fase posterior. | Perez Ordoñez Anthony Alexis (PM) |
| **RSK-05** | Incumplimiento del límite de 45 segundos del optimizador (RNF-001) en escenarios reales de alta complejidad combinatoria. | Técnica / Algorítmica | 3 | 5 | **15 (Alta)** | *Spike técnico* en el Sprint 1 para comparar rendimiento de GA vs. Búsqueda Tabú vs. OR-Tools antes de comprometer el diseño final. | Reducir el alcance del vecindario de búsqueda o aplicar paralelización de la metaheurística bajo presión de tiempo. | Fernandez Condor Jhon Smith (Backend) |
| **RSK-06** | Baja adopción de la app móvil por parte de conductores con brecha digital (alfabetización básica, dispositivos de gama baja). | Social / Adopción | 4 | 3 | **12 (Media)** | Pruebas de usabilidad tempranas con conductores reales y capacitación presencial mensual (Documento 05). | Habilitar un canal de soporte telefónico/presencial para conductores que no logren usar la app. | Perez Ordoñez Anthony Alexis (PM) |
| **RSK-07** | Cambio normativo durante el desarrollo (Pico y Placa, Ley N° 29733 o D.S. 033-2012-MTC). | Normativa / Legal | 2 | 3 | **6 (Baja)** | Revisión trimestral del marco normativo vigente con el docente/Product Owner académico. | Ajustar las reglas de negocio (RN-002, RN-008) y desplegar el cambio en el siguiente Sprint disponible. | Tovar Arias Michael Aldo (BD) |
| **RSK-08** | Indisponibilidad temporal de un integrante del equipo (enfermedad, examen, etc.) durante un Sprint. | Recursos Humanos | 2 | 4 | **8 (Media)** | Documentación continua y *pair programming* para evitar dependencia de una sola persona por módulo. | Redistribuir sus tareas del Sprint entre los dos integrantes restantes, priorizando el *Sprint Goal*. | Equipo completo |

## Resumen de Exposición al Riesgo (línea base v1.0.0, 08/09/2026)

| Nivel de Severidad | Cantidad de Riesgos | IDs |
|---|---|---|
| **Alta (15-25)** | 1 | RSK-05 |
| **Media (8-12)** | 6 | RSK-01, RSK-02, RSK-03, RSK-04, RSK-06, RSK-08 |
| **Baja (1-6)** | 2 | RSK-07, RSK-16 |

**Observación:** el único riesgo de severidad **Alta** (RSK-05) recae directamente sobre el núcleo técnico del proyecto (el motor de optimización bajo RNF-001), por lo que su mitigación —un *spike* técnico comparativo en el primer Sprint— se recomienda como parte del *Sprint Goal* del Sprint 1.

## Actualización del Sprint 2 (05/10/2026)

### Reevaluación de RSK-05

El spike comparativo que debía reducir este riesgo en el Sprint 1 no se ejecutó y el motor de optimización no tiene avance (IMP-010). **Probabilidad 3 → 4; severidad 15 → 20 (Alta).** La mitigación pasa a ser la primera tarea del siguiente sprint, con tiempo acotado y resultados reproducibles.

### Riesgos nuevos

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) | Responsable |
|---|---|---|---|---|---|---|---|---|
| **RSK-09** | Retraso del cronograma: al 05/10/2026 el motor de optimización (EP-03) no tiene avance y 18 de 20 ítems (108 de 116 pts) no tienen criterios verificados, con entrega el 23/11/2026. | Cronograma | 4 | 5 | **20 (Alta)** | Iniciar el spike EN-001 en el siguiente sprint; priorizar US-005 sobre ítems de menor valor; cerrar Sprint 1 y medir la velocidad real para recalcular la fecha. | Acordar con el Product Owner un alcance mínimo viable (US-005 con un solo algoritmo y dashboard básico) y diferir los enablers de escalabilidad y failover. | Perez Ordoñez Anthony Alexis y Fernandez Condor Jhon Smith |
| **RSK-10** | Defectos de seguridad no detectados por pruebas que no usan el flujo real: DEF-001, DEF-002 y DEF-003 se encontraron recién en el Sprint 2. | Seguridad / Calidad | 3 | 4 | **12 (Media)** | Pruebas de aceptación con `get_db` real y roles reales para cada historia; revisión OWASP (EN-002); revisión por pares. | No aceptar historias con defectos de seguridad abiertos y corregirlos antes de cada demostración. | Fernandez Condor Jhon Smith |
| **RSK-11** | Ausencia de CI, lint y revisión por pares: la Definition of Done no es verificable y los defectos pueden llegar a la rama principal. | Proceso / Herramientas | 4 | 3 | **12 (Media)** | Pipeline en GitHub Actions con `pytest --cov` y `npm run build`; ramas y Pull Requests con revisor; protección de la rama principal. **Actualización 20/10/2026:** el pipeline ya existe (`.github/workflows/ci.yml`) y se adoptó GitFlow (`CONTRIBUTING.md`); falta activar la protección de rama en GitHub. | Revisión cruzada manual antes de cada demostración hasta contar con el pipeline. | Equipo completo |
| **RSK-12** | Configuración insegura por defecto (clave de firma de desarrollo, CORS amplio, documentación de la API expuesta) que llegue a un despliegue real (OWASP A02). | Seguridad / Configuración | 3 | 4 | **12 (Media)** | Sprint 3: variable `ENVIRONMENT`; en `production` se rechaza la clave por defecto y se oculta `/docs`; CORS acotado y cabeceras de seguridad. Pendiente: TLS y HSTS en el despliegue. | No desplegar sin `.env`; rotar la clave si se expuso. | Fernandez Condor Jhon Smith |

### Riesgos añadidos en la etapa final

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) | Responsable |
|---|---|---|---|---|---|---|---|---|
| **RSK-13** | Pérdida de datos en producción: SQLite en el disco temporal del plan gratuito se reinicia con cada despliegue o reinicio. | Datos / Infraestructura | 4 | 3 | **12 (Media)** | Cargar datos de demostración al arrancar (`SEED_DEMO_DATA`); declarar la limitación en la [Guía de despliegue](../03%20Inplementaci%C3%B3n/Etapa%20final/05%20Gu%C3%ADa%20de%20despliegue.md); migrar a PostgreSQL con controlador asíncrono (acción 6 de la [Retrospectiva](../03%20Inplementaci%C3%B3n/Etapa%20final/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)). | No registrar datos reales en producción hasta contar con PostgreSQL. | Fernandez Condor Jhon Smith |
| **RSK-14** | Equipos de desarrollo con poca memoria: Docker se detiene durante las ejecuciones largas de la suite E2E y retrasa la verificación local. | Herramientas / Recursos | 4 | 2 | **8 (Media)** | Ejecutar la suite completa en GitHub Actions; en el equipo local usar `scripts/e2e-por-tandas.sh` (tandas cortas con reintentos). | Verificar solo con la prueba de humo local y confiar en Actions para la suite completa. | Equipo completo |

### Riesgos añadidos y actualizados en el cierre (28/11/2026)

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) | Responsable |
|---|---|---|---|---|---|---|---|---|
| **RSK-15** | El video de cierre (MP4 de 5 minutos) no se produce a tiempo o sin la calidad exigida. | Entregables / Cronograma | 3 | 4 | **12 (Media)** | [Guion minuto a minuto y lista de verificación](../05%20Video%20proyecto/Guion%20del%20video.md); grabar con la aplicación en producción. | Grabar una versión sencilla con la pantalla y la voz del equipo. | Perez Ordoñez Anthony Alexis |
| **RSK-16** | Las teselas del mapa dependen de un servicio externo (OpenStreetMap). | Técnica / Dependencia externa | 2 | 2 | **4 (Baja)** | Si no cargan, el recorrido, las paradas y la tabla equivalente siguen visibles; la CSP solo admite ese dominio. | Cambiar de proveedor de teselas en un solo archivo. | Fernandez Condor Jhon Smith |
| **RSK-17** | La base PostgreSQL gratuita de Render caduca a los 30 días y borra los datos de producción. | Datos / Infraestructura | 3 | 3 | **9 (Media)** | Advertido en la [Guía de despliegue](../03%20Inplementaci%C3%B3n/Etapa%20final/05%20Gu%C3%ADa%20de%20despliegue.md); pasar a un plan de pago para operar. | Exportar un respaldo antes del plazo y recargar los datos de demostración con `SEED_DEMO_DATA`. | Perez Ordoñez Anthony Alexis |
| **RSK-18** | Perder o cambiar la clave de cifrado `DATA_ENCRYPTION_KEY` deja ilegibles los datos personales ya cifrados (RNF-008). | Seguridad / Datos | 2 | 5 | **10 (Media)** | Guardar la clave en un gestor de secretos y no rotarla sin migrar los datos; no se escribe en el repositorio. | Restaurar la clave desde el gestor; si se perdió, anonimizar y volver a cargar los datos. | Fernandez Condor Jhon Smith |

**Estado de riesgos existentes al cierre.** **RSK-05** (límite de 45 s del optimizador): **no se materializó**; 50 pedidos se planifican en milisegundos y 1.000 en alrededor de 1 s, y el estudio comparativo confirmó el método ([Estudio de algoritmos](../03%20Inplementaci%C3%B3n/Etapa%20final/07%20Estudio%20de%20algoritmos%20V_1_0_0.md)). **RSK-09** (retraso del cronograma): **se materializó** (SPI 0,144 en el Sprint 3) y se **recuperó** (SPI 0,944 al cierre; [Reporte de Variación](../04%20Cierre/02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md)). **RSK-11** (sin CI ni lint): **mitigado** con los flujos de Actions, ESLint, Ruff y Bandit. **RSK-13** (datos no persistentes): **resuelto** con la base PostgreSQL de producción, que trae el riesgo nuevo RSK-17.

### Resumen de exposición actualizado

| Nivel de Severidad | Cantidad de Riesgos | IDs |
|---|---|---|
| **Alta (15-25)** | 2 | RSK-05 (reevaluado a 20), RSK-09 |
| **Media (8-12)** | 12 | RSK-01, RSK-02, RSK-03, RSK-04, RSK-06, RSK-08, RSK-10, RSK-11, RSK-14, RSK-15, RSK-17, RSK-18 |
| **Baja (1-6)** | 2 | RSK-07, RSK-16 |

La reserva de contingencia del 12 % (Documento 04 de Planificación) cubre la materialización parcial de RSK-05 y RSK-09 únicamente si se recorta el alcance; no cubre una extensión del plazo de entrega.

## Historial de Control de Cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 08/09/2026 | Creación del registro con RSK-01 a RSK-08. |
| 1.1.0 | 05/10/2026 | Reevaluación de RSK-05 (severidad 20) y alta de RSK-09, RSK-10 y RSK-11 a partir de la verificación técnica y la consulta a Jira del Sprint 2; la matriz original no se modifica. |
| 1.2.0 | 20/10/2026 | Sprint 3: se actualiza RSK-11 (CI creado) y se añade RSK-12 (configuración insegura por defecto). |
| 1.3.0 | 16/11/2026 | Etapa final: se añaden RSK-13 (datos no persistentes con SQLite en producción) y RSK-14 (memoria insuficiente para la suite E2E local); se actualiza el resumen de exposición. |
| 1.4.0 | 28/11/2026 | Cierre: se añaden RSK-15 y RSK-16 y se actualiza el estado de RSK-05 (no se materializó), RSK-09 (se materializó) y RSK-11 (mitigado). |
| 1.5.0 | 28/11/2026 | Se añaden RSK-17 (la base gratuita caduca) y RSK-18 (clave de cifrado); RSK-13 pasa a resuelto y se actualiza el estado de RSK-05 y RSK-09 con las cifras finales. |

---

[← Volver al README Principal](../../README.md)
