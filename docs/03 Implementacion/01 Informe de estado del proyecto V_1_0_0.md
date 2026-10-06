# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 1 (planificado del 08/09/2026 al 21/09/2026)  
**Fecha de corte del informe:** 29/09/2026  
**Versión del documento:** 1.0.0

[← Volver al README Principal](../../README.md)

## Resumen ejecutivo

El plan de Sprint 1 priorizó la seguridad de acceso y datos, el registro de vehículos y el registro de pedidos con ventana horaria y ubicación. Sin embargo, la evidencia versionada disponible no permite confirmar que el sprint se haya creado/iniciado en Jira, que alguna historia haya sido aceptada ni que se haya realizado una demostración. El documento de planificación de Jira del 08/09/2026 señalaba como tareas manuales pendientes la creación del sprint y la captura de sus evidencias; al corte de este informe no hay en el repositorio tablero exportado, actas, capturas ni implementación bajo `src/` que prueben su cierre.

Por rigor, el avance de historias se informa como **no verificable**, no como cero esfuerzo ni como completado. Se requiere confirmación del equipo y consulta del Jira vigente para establecer el estado real.

## Historias de Usuario completadas en este Sprint

**Historias completadas con evidencia verificable en este repositorio: ninguna confirmada.** Las siguientes son historias previstas para Sprint 1, no resultados de implementación:

| ID interno | Jira | Historia planificada | Criterio de aceptación relevante | Estado verificable al corte |
|---|---|---|---|---|
| EN-002 | EL-18 | Hardening de autenticación y protección OWASP | Acceso autenticado protegido frente a ataques contemplados en RNF-002 | No verificable; no hay pruebas, código ni evidencia de Jira adjunta |
| EN-008 | EL-24 | Cifrado y anonimización de datos personales | Datos personales protegidos conforme a RNF-008 y Ley N.° 29733 | No verificable; no hay pruebas, código ni evidencia de Jira adjunta |
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | Alta válida de vehículo y rechazo de placa duplicada | No verificable; no hay aplicación ni pruebas adjuntas |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | Registro de pedido válido y validación de capacidad | No verificable; no hay aplicación ni pruebas adjuntas |
| EN-001 (spike opcional) | EL-17 | Comparar alternativas del motor dentro del SLA de 45 segundos | Resultados reproducibles de GA, Búsqueda Tabú y/o OR-Tools | No se confirma que fuera comprometido o ejecutado; no hay resultados adjuntos |

La selección y objetivo originales constan en [Artefactos Jira](../02%20Planificacion/02%20Artefactos%20Jira%20V_1_0_0.md). Los IDs y criterios se mantienen vinculados al backlog; no se presentan como entregas aceptadas.

## Demostración del trabajo completado

No se encontró acta, captura, enlace de demo ni evidencia de aceptación de stakeholders. En consecuencia, **no se puede afirmar que se haya realizado una demostración**. La demo de cierre deberá mostrar, si ya están implementados, los flujos de autenticación segura, alta/edición de vehículos y registro de pedidos con sus validaciones; deberá acompañarse de resultados de pruebas y confirmación de aceptación del Product Owner académico/cliente.

La demostración queda pendiente de coordinación y registro. No se atribuyen comentarios ni aprobación a stakeholders sin evidencia.

## Pendientes

- Confirmar en Jira si Sprint 1 se creó e inició, su alcance definitivo, responsables, estados, cierre y aceptación.
- Adjuntar evidencias del tablero, historias aceptadas, pruebas de seguridad y funcionales, resultados del spike si fue ejecutado, y acta/captura de la demo.
- Si no se ejecutaron las historias planificadas, acordar con el Product Owner su replanificación y actualizar el backlog sin alterar retroactivamente la línea base.
- Registrar decisiones, impedimentos reales, responsables y fechas de resolución; actualizar este informe cuando exista evidencia.
- Mantener el objetivo de negocio: facilitar las operaciones de última milla de DistriRápido en Lima, reduciendo recorridos e impacto ambiental sin vulnerar ventanas horarias, capacidad vehicular, privacidad ni restricciones viales.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Creación del informe con corte al 29/09/2026; se separa explícitamente lo planificado de lo verificable. |