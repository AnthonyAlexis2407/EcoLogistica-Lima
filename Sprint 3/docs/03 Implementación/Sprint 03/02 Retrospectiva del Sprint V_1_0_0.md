# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 3 (periodo 07/10/2026 al 20/10/2026)  
**Fecha de retrospectiva:** 20/10/2026  
**Versión del documento:** 1.0.0

[← Volver al README Principal](../../../../README.md)

**Base del análisis.** Igual que en el Sprint 2, este análisis se apoya en evidencia verificable (historial de Git, informes de SonarQube, `npm audit`, axe-core, pruebas) y no atribuye opiniones a integrantes. Las fechas y responsables de las acciones son propuestas que el equipo debe confirmar en su sesión de retrospectiva.

## ¿Qué aprendimos?

- **Medir antes de afirmar.** Con SonarQube salieron 7 bugs que nadie había visto (promesas sin capturar errores) y la cobertura real era 65 %, no la que se suponía. Lo que no se mide no se corrige.
- **Las herramientas automáticas no lo ven todo.** Los valores escritos a mano en la interfaz (`isAdmin = true`, un UUID de bodega fijo, cifras ficticias en el Dashboard) y el desbordamiento horizontal en móvil los encontró la revisión manual, no Sonar ni axe.
- **Accesibilidad y calidad de código se solapan.** Las incidencias `S6848` de Sonar y los fallos `button-name` de axe se resolvieron con el mismo cambio (roles ARIA y nombres accesibles).
- **Actualizar dependencias puede cambiar otras cifras.** Al subir Vitest a la versión 5 para eliminar 6 vulnerabilidades de desarrollo, la cobertura del frontend se midió con más detalle y bajó de 99,8 % a 94,4 %; hay que explicar los cambios de métrica, no solo mostrarlos.
- **El estándar evoluciona.** OWASP Top 10:2025 reordenó categorías (SSRF dentro de A01, cadena de suministro, manejo de condiciones excepcionales); la plantilla de la consigna usa nombres anteriores y hubo que documentar la equivalencia.
- **La dependencia crítica sigue sin atenderse.** Dos sprints después, el motor de optimización (EN-001, RSK-05) no tiene avance, mientras la calidad del resto mejoró mucho.

## ¿Qué estamos haciendo bien?

- Se pasó de 0 pruebas del frontend y 16 del backend a **60 y 34** en verde, con cobertura global de **92,8 %** y Quality Gate en PASSED.
- Cada hallazgo se corrigió y quedó protegido por una prueba o una regla (por ejemplo, el registro de eventos de seguridad tiene su prueba y evita datos personales).
- Backend y frontend siguen separados en `src/backend` y `src/frontend`, con un `.gitignore` que excluye dependencias, bases locales, secretos, informes de cobertura y `.scannerwork/`.
- Los informes conservan el historial de versiones y distinguen lo corregido de lo pendiente, sin declarar demostraciones ni pruebas de penetración que no se hicieron.
- El análisis es reproducible: `sonar-project.properties`, `.coveragerc` y los comandos del Documento 03 permiten repetirlo.

## ¿Qué podemos hacer mejor?

### Personas

- Repartir la revisión de las tres evaluaciones (calidad, seguridad, accesibilidad) entre integrantes distintos al que implementó la corrección; hoy quien corrige también evalúa.
- Reservar en cada sprint una sesión de retrospectiva y otra de revisión con el docente, con acta de asistentes y decisiones.
- Capacitar al equipo en lectores de pantalla (NVDA o VoiceOver) para cubrir lo que axe-core no detecta.

### Relaciones

- Agendar la demostración al inicio del sprint y registrar la decisión del Product Owner por historia (US-001 y US-003 siguen sin aceptación formal, IMP-003).
- Comunicar de inmediato que el spike EN-001 sigue sin iniciarse y acordar con el docente si se prioriza en el Sprint 4 y qué alcance del backlog se recorta.
- Validar con el cliente ficticio DistriRápido el diseño de bloqueo de cuenta y la política de datos personales antes de implementar EN-008.

### Procesos

- Convertir la Definition of Done en una lista verificable por Pull Request: Quality Gate en verde, cobertura ≥ 80 %, `npm audit` sin altas ni críticas y 0 incumplimientos de axe.
- Trabajar con ramas y Pull Requests con al menos un revisor (IMP-009) en lugar de commits directos a `main`.
- Revisar manualmente, además de las herramientas, tres puntos que ellas no cubren: valores fijos en la interfaz, reflujo en móvil y veracidad de los mensajes de estado.
- Cerrar el sprint en Jira el día de su fin y crear el siguiente con objetivo y alcance (IMP-004).

### Herramientas

- Configurar CI con GitHub Actions: `pytest --cov`, `vitest --coverage`, SonarQube, `npm audit`, `pip-audit` y axe-core sobre las pantallas principales.
- Fijar las versiones del backend (archivo de bloqueo) para dejar de usar rangos abiertos `>=`.
- Añadir Lighthouse o WAVE como segunda herramienta de accesibilidad, para no depender de una sola.
- Exigir `SECRET_KEY` por variable de entorno en lugar del valor de desarrollo.

### Acciones a realizar

| Acción | Dimensión | Responsable (propuesto) | Fecha objetivo | Evidencia de cierre |
|---|---|---|---|---|
| Realizar la demostración a stakeholders y completar la tabla de registro del Documento 01 | Relaciones | Perez Ordoñez Anthony Alexis | 23/10/2026 | Tabla completa con fecha, asistentes y decisión por historia; US-001 y US-003 en "Hecho" en Jira |
| Cerrar EL Sprint 1 y crear el siguiente sprint con objetivo y alcance | Procesos | Perez Ordoñez Anthony Alexis | 23/10/2026 | Tablero de Jira actualizado |
| Crear el flujo de CI (pruebas, cobertura, SonarQube, `npm audit`, `pip-audit`, axe) y proteger la rama `main` con Pull Request y un revisor | Herramientas / Procesos | Equipo completo | 30/10/2026 | Pipeline en verde en un Pull Request y regla de rama protegida |
| Exigir `SECRET_KEY` por entorno, restringir CORS, añadir cabeceras de seguridad y ocultar `/docs` en producción | Herramientas | Fernandez Condor Jhon Smith | 30/10/2026 | Pruebas y Documento 04 actualizado (A02) |
| Iniciar el spike EN-001 (GA, Búsqueda Tabú y OR-Tools frente a 45 s) con tiempo acotado y resultados reproducibles | Procesos | Fernandez Condor Jhon Smith | Primera semana del Sprint 4 | Script versionado con datos de entrada, tiempos y conclusión |
| Probar con NVDA o VoiceOver el recorrido de inicio de sesión, alta de vehículo y alta de pedido; implementar la trampa de foco en los modales | Personas / Herramientas | Tovar Arias Michael Aldo | 30/10/2026 | Documento 05 en versión 1.1.0 |
| Ejecutar la prueba de penetración de EN-002 e implementar el cifrado de campos y la anonimización de EN-008 | Procesos | Equipo completo | Cierre del Sprint 4 | Informe de prueba y pruebas automatizadas de cada criterio |
| Rotar la revisión: quien corrige no evalúa el mismo hallazgo | Personas | Equipo completo | Desde el Sprint 4 | Campo "revisor" en cada Pull Request |

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 20/10/2026 | Sprint 3: primera retrospectiva basada en las evaluaciones de calidad, seguridad y accesibilidad. |
