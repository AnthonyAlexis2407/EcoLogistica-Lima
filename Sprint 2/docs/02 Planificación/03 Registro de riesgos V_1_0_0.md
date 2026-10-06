# Registro de Riesgos del Proyecto

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
| **Baja (1-6)** | 1 | RSK-07 |

**Observación:** el único riesgo de severidad **Alta** (RSK-05) recae directamente sobre el núcleo técnico del proyecto (el motor de optimización bajo RNF-001), por lo que su mitigación —un *spike* técnico comparativo en el primer Sprint— se recomienda como parte del *Sprint Goal* del Sprint 1.

## Actualización del Sprint 2 (05/10/2026)

### Reevaluación de RSK-05

El spike comparativo que debía reducir este riesgo en el Sprint 1 no se ejecutó y el motor de optimización no tiene avance (IMP-010). **Probabilidad 3 → 4; severidad 15 → 20 (Alta).** La mitigación pasa a ser la primera tarea del siguiente sprint, con tiempo acotado y resultados reproducibles.

### Riesgos nuevos

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) | Responsable |
|---|---|---|---|---|---|---|---|---|
| **RSK-09** | Retraso del cronograma: al 05/10/2026 el motor de optimización (EP-03) no tiene avance y 18 de 20 ítems (108 de 116 pts) no tienen criterios verificados, con entrega el 23/11/2026. | Cronograma | 4 | 5 | **20 (Alta)** | Iniciar el spike EN-001 en el siguiente sprint; priorizar US-005 sobre ítems de menor valor; cerrar Sprint 1 y medir la velocidad real para recalcular la fecha. | Acordar con el Product Owner un alcance mínimo viable (US-005 con un solo algoritmo y dashboard básico) y diferir los enablers de escalabilidad y failover. | Perez Ordoñez Anthony Alexis y Fernandez Condor Jhon Smith |
| **RSK-10** | Defectos de seguridad no detectados por pruebas que no usan el flujo real: DEF-001, DEF-002 y DEF-003 se encontraron recién en el Sprint 2. | Seguridad / Calidad | 3 | 4 | **12 (Media)** | Pruebas de aceptación con `get_db` real y roles reales para cada historia; revisión OWASP (EN-002); revisión por pares. | No aceptar historias con defectos de seguridad abiertos y corregirlos antes de cada demostración. | Fernandez Condor Jhon Smith |
| **RSK-11** | Ausencia de CI, lint y revisión por pares: la Definition of Done no es verificable y los defectos pueden llegar a la rama principal. | Proceso / Herramientas | 4 | 3 | **12 (Media)** | Pipeline en GitHub Actions con `pytest --cov` y `npm run build`; ramas y Pull Requests con revisor; protección de la rama principal. | Revisión cruzada manual antes de cada demostración hasta contar con el pipeline. | Equipo completo |

### Resumen de exposición actualizado

| Nivel de Severidad | Cantidad de Riesgos | IDs |
|---|---|---|
| **Alta (15-25)** | 2 | RSK-05 (reevaluado a 20), RSK-09 |
| **Media (8-12)** | 8 | RSK-01, RSK-02, RSK-03, RSK-04, RSK-06, RSK-08, RSK-10, RSK-11 |
| **Baja (1-6)** | 1 | RSK-07 |

La reserva de contingencia del 12 % (Documento 04 de Planificación) cubre la materialización parcial de RSK-05 y RSK-09 únicamente si se recorta el alcance; no cubre una extensión del plazo de entrega.

## Historial de Control de Cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 08/09/2026 | Creación del registro con RSK-01 a RSK-08. |
| 1.1.0 | 05/10/2026 | Reevaluación de RSK-05 (severidad 20) y alta de RSK-09, RSK-10 y RSK-11 a partir de la verificación técnica y la consulta a Jira del Sprint 2; la matriz original no se modifica. |

---

[← Volver al README Principal](../../README.md)
