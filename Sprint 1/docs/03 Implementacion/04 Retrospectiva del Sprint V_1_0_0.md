# Retrospectiva del Sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 1 (planificado del 08/09/2026 al 21/09/2026)  
**Fecha de retrospectiva documental:** 29/09/2026  
**Versión del documento:** 1.0.0

[← Volver al README Principal](../../README.md)

## Alcance y limitación

No se encontró acta de retrospectiva, tablero histórico, métricas de flujo ni testimonios del equipo. Lo siguiente es un análisis documental preliminar basado en los artefactos versionados; no atribuye opiniones, conflictos ni logros personales a integrantes. El equipo debe validarlo en una conversación retrospectiva y completar los datos empíricos.

## ¿Qué aprendimos?

- El proyecto ya definió con anticipación requisitos de alto riesgo: privacidad y geolocalización conforme a la Ley N.° 29733, autenticación y el límite de 45 segundos para el optimizador. Deben convertirse en criterios de aceptación y pruebas tempranas, no quedarse solo en documentos de diseño.
- Tener un backlog creado no equivale a tener un sprint ejecutado: las tareas manuales de planificación y las evidencias del tablero deben cerrarse y conservarse para que el estado pueda auditarse.
- La trazabilidad entre RF/RNF, historias Jira, commits, pruebas y aceptación es indispensable para un producto que gestiona pedidos, rutas y datos sensibles.
- La evidencia disponible no permite medir velocidad, calidad del incremento ni cumplimiento del objetivo. El equipo deberá registrar esas métricas en el siguiente ciclo en vez de estimarlas retrospectivamente.

## ¿Qué estamos haciendo bien?

- Inicio y Planificación describen el problema de última milla de DistriRápido y las necesidades locales de Lima, incluidos tráfico, direcciones referenciales y conectividad variable.
- Existe una línea base funcional con criterios de aceptación y una priorización de Jira; el backlog mapea historias a épicas y requisitos.
- Se asignaron responsabilidades nominales de backend, frontend/gestión y base de datos, y se identificaron riesgos, entre ellos el rendimiento del motor de optimización.
- El stack planeado (FastAPI, React y PostgreSQL/PostGIS) mantiene una separación clara entre frontend y backend, que ahora queda reflejada en la estructura inicial del repositorio.

## ¿Qué podemos hacer mejor?

### Personas

- Confirmar disponibilidad y capacidad por integrante antes de comprometer puntos; rotar conocimiento mediante revisión de código y sesiones breves de transferencia para reducir dependencia por módulo.
- Acordar quién mantiene evidencia de pruebas, decisiones y aceptación para que la responsabilidad documental no quede implícita.

### Relaciones

- Acordar una fecha de revisión con el docente/Product Owner al inicio del sprint y registrar oportunamente feedback de conductores, administradores y cliente.
- Mantener una comunicación sin sorpresas: escalar bloqueos de Jira, acceso a datos o servicios externos tan pronto afecten el objetivo.

### Procesos

- Completar Sprint Planning en Jira antes de empezar: objetivo, historias comprometidas, criterios de aceptación, estimaciones y responsables.
- Definir Definition of Done mínima: código revisado, pruebas ejecutadas, requisitos de privacidad y seguridad comprobados cuando apliquen, documentación y aceptación registradas.
- Hacer seguimiento frecuente del tablero y cerrar el Sprint Review y la retrospectiva con decisiones accionables; no inferir estado desde el backlog priorizado.

### Herramientas

- Mantener en Git la aplicación, pruebas y evidencias no sensibles; enlazar cada cambio con su historia Jira.
- Configurar CI para pruebas/lint y proteger secretos con variables de entorno ignoradas por Git; nunca versionar credenciales, geolocalización real ni datos personales.
- Usar un mecanismo acordado para guardar actas y capturas de Jira con fecha, manteniendo enlaces relativos desde la documentación.

### Acciones a realizar

| Acción | Responsable | Fecha objetivo | Evidencia de cierre |
|---|---|---|---|
| Confirmar en Jira si Sprint 1 se inició, su alcance real y estados finales; corregir la trazabilidad documental con el Product Owner | Perez Ordoñez Anthony Alexis | 30/09/2026 | Sprint/acta consultados; estados y decisión de replanificación registrados |
| Localizar y vincular commits, pruebas y resultados del incremento; determinar qué criterios de US-001, US-003, EN-002 y EN-008 están demostrados | Fernandez Condor Jhon Smith y equipo | 02/10/2026 | Enlaces reproducibles a código/pruebas o lista aprobada del trabajo restante |
| Confirmar si se realizó la demo; documentar asistentes, observaciones y aceptación, o agendarla si sigue pendiente | Perez Ordoñez Anthony Alexis | 02/10/2026 | Acta de revisión con decisiones por historia |
| Establecer Definition of Done, plantilla de captura de evidencia y revisión periódica del tablero para el siguiente sprint | Equipo completo | Antes de iniciar el siguiente sprint | Acuerdos incorporados al tablero y aplicados en la planificación |

Las fechas son compromisos propuestos a partir de esta revisión documental y deben ser confirmados por el equipo. Esta retrospectiva deberá complementarse con la conversación real del equipo y sus observaciones antes de considerarse retrospectiva validada.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Creación del análisis preliminar basado en evidencia documental disponible; acciones propuestas sujetas a validación del equipo. |