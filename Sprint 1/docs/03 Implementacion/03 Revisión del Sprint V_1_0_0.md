# Revisión del Sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 1 (planificado del 08/09/2026 al 21/09/2026)  
**Fecha de revisión documental:** 29/09/2026  
**Versión del documento:** 1.0.0

[← Volver al README Principal](../../README.md)

## Alcance planificado

La planificación priorizó autenticación segura (EL-18 / EN-002), cifrado y anonimización (EL-24 / EN-008), gestión de flota (EL-7 / US-001) y registro de pedidos (EL-9 / US-003). El spike comparativo del motor (EL-17 / EN-001) se describió como opcional. La selección definitiva debía confirmarse en la planificación manual de Jira.

## Historias de Usuario completadas en este Sprint

No se cuenta con estado de Jira, commits, pruebas ni evidencia de aceptación que permita marcar como completada alguna historia. Las historias siguientes corresponden al alcance previsto; su estado de entrega queda **pendiente de validación**, no aceptado:

| ID | Jira | Historia | Resultado que debe verificarse para aceptar |
|---|---|---|---|
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | Crear/editar/baja lógica de vehículos; placa única; pruebas de registro y rechazo de duplicado |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | Registrar pedido con ventana y carga; validar capacidad; admitir ubicación georreferenciada para direcciones referenciales |

**Enablers técnicos planificados:** EN-002 (EL-18, hardening de autenticación) y EN-008 (EL-24, protección de datos). Deben verificarse con pruebas de seguridad y evidencia de cifrado/anonimización antes de aceptar el incremento. EN-001 (EL-17) solo se evalúa si se confirma que el spike fue incorporado al sprint; se requieren datos de entrada, configuración, tiempos y resultados reproducibles.

## Demostración del trabajo completado

El repositorio no incluye evidencia de una demostración realizada, asistentes, fecha, aceptación ni observaciones de stakeholders. Por ello, esta revisión **no registra una demo como efectuada**. La demostración queda pendiente de confirmar y documentar con el docente/Product Owner académico y el cliente ficticio DistriRápido.

Guion de verificación para la revisión cuando el incremento esté disponible:

1. Mostrar autenticación y controles de seguridad previstos, sin exponer credenciales ni datos personales reales.
2. Registrar un vehículo con placa única y demostrar el rechazo de una placa duplicada.
3. Registrar un pedido con ventana horaria, peso y ubicación; demostrar la validación ante una carga incompatible.
4. Presentar resultados de pruebas y, si se ejecutó, el spike con comparación reproducible de alternativas frente al límite RNF-001 de 45 segundos.
5. Registrar para cada historia la decisión del Product Owner: aceptada, cambios solicitados o no presentada, junto con responsables y fechas.

## Pendientes

- Validar con Jira el alcance real y el estado de cierre de Sprint 1.
- Obtener evidencia de los criterios de aceptación de US-001 y US-003 y de los enablers de seguridad comprometidos.
- Confirmar si EN-001 fue parte del compromiso y, de ser así, documentar resultados medidos.
- Realizar o documentar la demo con asistentes, observaciones, decisiones y aceptación explícita; no atribuir aprobaciones sin registro.
- Replanificar historias no terminadas con el Product Owner y preservar la trazabilidad con los RF-001/RF-002, RNF-002/RNF-008 y las reglas de negocio aplicables.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Creación de la revisión documental; se separa alcance planificado de entregas aceptadas. |