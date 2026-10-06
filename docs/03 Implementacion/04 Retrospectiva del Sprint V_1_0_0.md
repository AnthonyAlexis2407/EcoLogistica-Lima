# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 2 (periodo de trabajo del 23/09/2026 al 06/10/2026)  
**Fecha de retrospectiva:** 05/10/2026  
**Versión del documento:** 2.1.0

[← Volver al README Principal](../../README.md)

## Base del análisis

No existe acta de una sesión de retrospectiva con el equipo. Este análisis se apoya en evidencia verificable (historial de Git, consulta a Jira, resultado de pruebas, cobertura y compilación del 05/10/2026), no atribuye opiniones ni logros individuales a integrantes y debe validarse en una conversación del equipo antes de darse por cerrado. Las fechas y responsables de las acciones son propuestas a confirmar.

## ¿Qué aprendimos?

- **Una prueba que reemplaza la base de datos real puede ocultar defectos graves.** Las 6 pruebas originales pasaban mientras el bloqueo de cuenta (EN-002) no funcionaba: usaban una sesión compartida y nunca ejercitaban el rollback real de `get_db`. La prueba de regresión nueva, con la dependencia real, falla sin la corrección y pasa con ella.
- **Los escenarios Gherkin del backlog se convierten directamente en pruebas.** Las 5 pruebas de aceptación nuevas (más 2 que documentan defectos abiertos) salieron de los escenarios de US-001, US-003, EN-002 y RN-010; hubo trazabilidad sin esfuerzo adicional entre requisito, historia y prueba.
- **Documentación y código deben cerrarse juntos.** El código se versionó el 29/09/2026, siete días después del fin planificado del Sprint 1 (22/09), y los informes del mismo día todavía decían "no hay código bajo `src/`".
- **Un estado de Jira que no se mantiene deja de ser evidencia.** EL Sprint 1 sigue activo después de su fecha de fin, los 5 ítems siguen "En curso" y no hay Sprint 2: no se puede medir velocidad.
- **Un ✅ escrito a mano en la interfaz no es una prueba.** El panel de inicio marca EN-002 y EN-008 como logrados; la verificación mostró que EN-002 estaba roto y EN-008 es parcial.
- **La seguridad hay que probarla con roles reales.** Al hacerlo apareció DEF-003 (el registro público acepta cualquier rol y permite autoasignarse ADMIN_FLOTA), que ninguna prueba original cubría y que invalidaba en la práctica el RBAC; se corrigió en el mismo periodo junto con DEF-002.
- **La dependencia crítica se pospuso.** El motor de optimización (RSK-05) debía abordarse antes de la Iteración 2 y no tiene avance; es el principal riesgo del cronograma.

## ¿Qué estamos haciendo bien?

- Hay un backend (FastAPI, SQLAlchemy asíncrono, JWT, bcrypt y RBAC) y un frontend (React, TypeScript y Vite) separados en `src/backend` y `src/frontend`, con un `.gitignore` que excluye dependencias, bases locales y variables de entorno.
- La API aplica reglas del dominio ya definidas en la documentación: placa única, baja lógica sin borrado físico, validación de capacidad vehicular, ventana horaria coherente y aislamiento de lectura por bodega (RN-010).
- El defecto DEF-001 se detectó, se corrigió y quedó protegido por una prueba de regresión en el mismo periodo, y DEF-002 y DEF-003 se documentaron primero como `xfail` en vez de ocultarse y se corrigieron en el mismo periodo, con pruebas de regresión.
- Los commits de código recientes usan una convención legible (`feat`, `fix`, `docs`) y los informes separan con honestidad lo verificado de lo pendiente.
- La trazabilidad RF → historia → clave de Jira → prueba se mantiene en el backlog y en los informes.

## ¿Qué podemos hacer mejor?

### Personas

- Repartir la responsabilidad de cierre de cada historia (código, pruebas, evidencia y estado en Jira) para que no dependa de una sola persona; hoy el código y la gestión llegaron por caminos separados.
- Reservar tiempo explícito por sprint para una sesión de retrospectiva y otra de revisión con el docente, con asistentes y decisiones registradas.

### Relaciones

- Fijar con el docente/Product Owner la fecha de la revisión al iniciar el sprint, no al terminarlo; hoy la demostración a stakeholders no está registrada (IMP-003).
- Avisar de inmediato cuando una dependencia crítica (el motor de optimización) no avanza, en vez de descubrirlo al cierre del periodo.

### Procesos

- Cerrar el sprint en Jira el día de su fecha de fin y crear el siguiente con objetivo y alcance antes de empezar a trabajar (IMP-004).
- Adoptar una Definition of Done verificable: pruebas de aceptación que ejecuten el flujo real, cobertura ≥ 80 %, revisión por pares y evidencia enlazada en la historia antes de moverla a "Hecho".
- Trabajar con ramas y Pull Requests con al menos un revisor, y no con commits directos, para dejar rastro de la revisión (IMP-009).
- Empezar el siguiente sprint por el spike EN-001 con tiempo acotado y resultados reproducibles, porque desbloquea US-005.

### Herramientas

- Configurar un pipeline de CI (GitHub Actions) que ejecute `pytest --cov` y `npm run build` en cada Pull Request, y completar el script de lint del frontend (hoy la configuración de ESLint existe pero falta el script y la dependencia).
- Mantener las pruebas de aceptación contra el flujo real (`get_db` real y roles reales del seed) y dejar las pruebas con sesión compartida solo para pruebas unitarias.
- Reemplazar los ✅ estáticos del panel de inicio por datos de estado reales o por texto neutro, y mantener el README de cada carpeta de `src/` específico del proyecto (el del frontend traía el texto de la plantilla de Vite).

### Acciones a realizar

| Acción | Responsable (propuesto) | Fecha objetivo | Evidencia de cierre |
|---|---|---|---|
| Cerrar EL Sprint 1, crear EL Sprint 2 con objetivo y alcance, y actualizar estados según la decisión del PO | Perez Ordoñez Anthony Alexis | 07/10/2026 | Tablero con el Sprint 1 cerrado, Sprint 2 creado y estados actualizados |
| Presentar US-001 y US-003 al docente/PO y registrar la decisión por historia | Perez Ordoñez Anthony Alexis | 09/10/2026 | Acta con fecha, asistentes, observaciones y decisión; enlace desde la Revisión del Sprint |
| Ratificar con el equipo el diseño adoptado para DEF-003 (registro público solo BODEGA; otros roles los crea un ADMIN_FLOTA) y para DEF-002 | Fernandez Condor Jhon Smith y equipo | 09/10/2026 | Decisión registrada en el Documento 08 (sección 4) |
| Iniciar el spike EN-001 (GA, Búsqueda Tabú y OR-Tools frente a 45 s) con resultados reproducibles | Fernandez Condor Jhon Smith | Cierre del siguiente sprint | Notebook o script versionado con datos de entrada, tiempos y conclusión |
| Subir la cobertura de pruebas de 67 % a ≥ 80 % (routers de autenticación, pedidos y vehículos) | Fernandez Condor Jhon Smith | 12/10/2026 | Reporte `pytest --cov` con TOTAL ≥ 80 % |
| Configurar CI y lint, y adoptar ramas con Pull Requests y un revisor | Equipo completo | 14/10/2026 | Pipeline en verde en un Pull Request y regla de rama protegida |
| Decidir si el rol `ADMINISTRADOR` se elimina del código o se documenta en el Documento 08; ajustar los ✅ estáticos del panel | Tovar Arias Michael Aldo y Fernandez Condor Jhon Smith | 09/10/2026 | Decisión registrada en el Documento 08 y commit coherente |
| Completar EN-002 (revisión OWASP) y EN-008 (cifrado de campos y anonimización) | Equipo completo | Cierre del siguiente sprint | Pruebas y evidencia de cada criterio del Documento 01 |

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Sprint 1: análisis documental preliminar sin datos empíricos (commit `246e72d`). |
| 2.0.0 | 05/10/2026 | Sprint 2: análisis basado en evidencia verificada (pruebas, cobertura, Git y Jira), nuevos aprendizajes y plan de acción con responsables y fechas propuestos. |
| 2.1.0 | 05/10/2026 | DEF-002 y DEF-003 pasan de abiertos a corregidos; la acción asociada pasa a ratificar el diseño adoptado. |
