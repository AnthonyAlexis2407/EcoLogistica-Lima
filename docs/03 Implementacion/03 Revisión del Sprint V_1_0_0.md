# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 2 (periodo de trabajo del 23/09/2026 al 06/10/2026)  
**Fecha de revisión:** 05/10/2026  
**Versión del documento:** 2.1.0

[← Volver al README Principal](../../README.md)

## Alcance y objetivo del periodo

Jira no contiene todavía un Sprint 2 ni su objetivo (IMP-004). El objetivo efectivo del periodo, reconstruido a partir de la evidencia (commits del 29/09/2026 y verificación del 05/10/2026), fue **cerrar con evidencia verificable el arrastre del Sprint 1**: gestión de flota (US-001), registro de pedidos (US-003) y base de seguridad (EN-002, EN-008). La referencia formal sigue siendo el objetivo de **EL Sprint 1** en Jira: habilitar registro y autenticación segura, gestión básica de flota y registro de pedidos con validación de capacidad, sobre una base de seguridad verificada, y reducir el riesgo RSK-05 antes del Sprint 2.

| Parte del objetivo de EL Sprint 1 | Resultado verificado al 05/10/2026 |
|---|---|
| Registro y autenticación segura de usuarios | **Cumplido en parte:** registro, inicio de sesión con JWT, hash bcrypt, RBAC y bloqueo tras 3 intentos funcionan (bloqueo corregido en este periodo, DEF-001). Falta revisión OWASP/pentest; el registro público ya solo admite el rol BODEGA (DEF-003 corregido) |
| Gestión básica de flota | **Cumplido:** US-001 con criterios verificados por prueba |
| Registro de pedidos con validación de capacidad | **Cumplido:** US-003 con criterios verificados por prueba; DEF-002 corregido (una bodega solo registra pedidos propios) |
| Base de seguridad verificada | **No cumplido del todo:** EN-008 solo cubre el hash de contraseñas; sin cifrado de campos ni anonimización |
| Reducir RSK-05 (spike del motor) | **No cumplido:** el spike EN-001 no tiene avance |

## Historias de Usuario completadas en este Sprint

Se consideran completadas con evidencia las historias cuyos escenarios de aceptación del Documento 01 de Planificación están cubiertos por pruebas que pasan. Aún no están aceptadas por el Product Owner ni figuran como "Hecho" en Jira.

| ID | Jira | Historia | Detalle de lo logrado | Evidencia |
|---|---|---|---|---|
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | Alta, edición y baja lógica de vehículos (estado `FUERA_DE_SERVICIO`, sin borrado físico); placa normalizada y única (409 ante duplicado); solo el rol ADMIN_FLOTA modifica la flota y OPERADOR y AUDITOR leen (coincide con el Documento 08); el registro público ya no permite autoasignarse ese rol (DEF-003 corregido). Pantalla de gestión en el frontend | `test_us001_registro_valido_y_rechazo_de_placa_duplicada`, `test_us001_baja_logica_conserva_el_registro` |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | Alta de pedidos con dirección, coordenadas, peso y ventana horaria (la ventana final debe ser posterior a la inicial); estado inicial `PENDIENTE`; rechazo con 422 si el peso excede la mayor capacidad de la flota disponible; cancelación lógica; la bodega solo lista y registra pedidos propios (403 si usa otra bodega; DEF-002 corregido) | `test_us003_pedido_valido_y_rechazo_por_exceso_de_capacidad`, `test_rn010_bodega_solo_lista_sus_propios_pedidos`, `test_rn010_bodega_no_puede_registrar_pedido_para_otra_bodega` |

**Enablers:** EN-002 (EL-18) **parcial** (1 de 2 criterios verificado); EN-008 (EL-24) **parcial** (solo hash de contraseñas); EN-001 (EL-17) **no iniciado**.

**Resultado de las pruebas (05/10/2026):** 16 pasan y ninguna queda marcada como `xfail`; cobertura 67 % (meta del DoD: 80 %). La compilación del frontend es correcta.

## Demostración del trabajo completado

**Demostración técnica reproducible.** El incremento se puede ejecutar y comprobar con las instrucciones del Informe de estado (`pytest`, `python -m app.seed`, `uvicorn`, `npm ci && npm run build`). Esta verificación es interna del equipo y es la evidencia en la que se apoya este documento.

**Demostración a stakeholders:** el repositorio y Jira no contienen acta, captura, enlace ni aceptación del docente/Product Owner o del cliente ficticio DistriRápido. **No se registra como realizada** y no se atribuye ninguna observación o aprobación a terceros (IMP-003).

Guion de la demostración pendiente:

1. Iniciar sesión con distintos roles y mostrar que cada uno ve solo lo que le corresponde.
2. Registrar un vehículo, reintentar la misma placa y mostrar el rechazo; dar de baja el vehículo y comprobar que el registro se conserva.
3. Registrar un pedido válido y otro que exceda la capacidad de la flota; mostrar el mensaje de rechazo.
4. Fallar tres inicios de sesión y mostrar el bloqueo de 15 minutos.
5. Mostrar la suite de pruebas y que una bodega no puede registrar pedidos para otra ni crear usuarios administradores desde el registro público.
6. Registrar para cada historia la decisión del PO: aceptada, cambios solicitados o no presentada, con asistentes y fecha.

## Pendientes

- **Decisión del PO:** aceptar o pedir cambios en US-001 y US-003; con la decisión, actualizar sus estados en Jira (IMP-003, IMP-004).
- **Cierre de Jira:** cerrar EL Sprint 1, crear EL Sprint 2 con objetivo y alcance, y recalcular la velocidad con puntos aceptados.
- **EN-002:** revisión OWASP/pentest. **EN-008:** cifrado de campos personales y anonimización.
- **EN-001:** spike del motor de optimización (RSK-05) y, a continuación, US-005; es la ruta crítica del cronograma (IMP-010).
- **Calidad (IMP-005, IMP-009):** cobertura ≥ 80 %, lint, CI y revisión por pares.
- **Historias del backlog sin iniciar:** 15 ítems adicionales (US-002, US-004 a US-010, EN-003 a EN-007, EN-009, EN-010), con trazabilidad a RF-001 a RF-010 y RNF-001 a RNF-010.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Sprint 1: revisión documental; separaba alcance planificado de entregas aceptadas (commit `246e72d`). |
| 2.0.0 | 05/10/2026 | Sprint 2: historias verificadas por prueba automatizada, resultado frente al objetivo del sprint, guion de demostración y pendientes actualizados. |
| 2.1.0 | 05/10/2026 | Se registran como corregidos DEF-002 y DEF-003; resultado de pruebas actualizado a 16 en verde y pendientes depurados. |
