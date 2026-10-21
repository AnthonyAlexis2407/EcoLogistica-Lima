# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 3 (periodo 07/10/2026 al 20/10/2026; cerrado el 20/10/2026, etiqueta `sprint-3-cierre`)  
**Fecha de retrospectiva:** 20/10/2026  
**Versión del documento:** 1.1.0

[← Volver al README Principal](../../../README.md)

**Base del análisis.** Esta retrospectiva se hace con el sprint ya cerrado (ver la [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)) y se apoya en evidencia verificable: historial de Git, informes de SonarQube, `npm audit`, axe-core y pruebas. No atribuye opiniones a integrantes. Las fechas y responsables de las acciones son propuestas que el equipo debe confirmar.

## Seguimiento de las acciones de la retrospectiva del Sprint 2

| Acción del Sprint 2 | Resultado | Evidencia |
|---|---|---|
| Subir la cobertura de 67 % a ≥ 80 % | **Cumplida** (92,7 %) | [Doc. 03](03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) |
| Configurar CI y lint | **Parcial**: CI creado en este sprint; el lint sigue sin script | `.github/workflows/ci.yml`, IMP-009 |
| Trabajar con ramas y Pull Requests con revisor | **Parcial**: GitFlow documentado y rama `feature/` usada; faltan los Pull Requests en el remoto y la protección de `main` | [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) |
| Ratificar el diseño de DEF-002 y DEF-003 | **Cumplida**: documentado en el Documento 08 versión 1.3.0 | [Doc. 08](../../01%20Inicio/08.%20Usuarios%20V_1_0_0.md) |
| Decidir el rol `ADMINISTRADOR` y los ✅ fijos del panel | **Cumplida**: rol eliminado; el Dashboard usa datos reales | IMP-008 resuelto |
| Presentar US-001 y US-003 al PO y registrar la decisión | **No cumplida**: sin demostración registrada | IMP-003 |
| Iniciar el spike EN-001 | **No cumplida** | IMP-010 |
| Completar EN-002 (pentest) y EN-008 | **No cumplida** | IMP-014 |

**Lectura:** se cumplieron 3 de 8 acciones y 2 quedaron parciales. Todo lo que dependía solo del código y de herramientas se hizo; lo que no se hizo exige coordinación con terceros (el Product Owner) o una decisión de prioridad (el spike). Es el patrón que esta retrospectiva ataca.

## ¿Qué aprendimos?

- **Medir antes de afirmar.** Con SonarQube salieron 7 bugs que nadie había visto (promesas sin capturar errores) y la cobertura real era 65 %, no la que se suponía.
- **Las herramientas automáticas no lo ven todo.** Los valores escritos a mano en la interfaz (`isAdmin = true`, un UUID de bodega fijo, cifras ficticias en el Dashboard) y el desbordamiento horizontal en móvil los encontró la revisión manual, no Sonar ni axe.
- **Accesibilidad y calidad de código se solapan.** La incidencia `S6848` de Sonar y el fallo `button-name` de axe se resolvieron con el mismo cambio (roles ARIA y nombres accesibles).
- **Actualizar dependencias cambia otras cifras.** Al subir Vitest a la versión 5 para eliminar 6 vulnerabilidades de desarrollo, la cobertura del frontend bajó de 99,8 % a 94,4 % por una medición más fina; hay que explicar los cambios de métrica, no solo mostrarlos.
- **Un criterio de aceptación sin ruta gold deja huecos.** Las pruebas cubrían rutas felices e infelices por separado; el flujo completo de punta a punta (administrador, bodega, pedido y cancelación) no existía hasta este sprint.
- **Los documentos se desfasan en silencio.** La decisión pendiente sobre el rol `ADMINISTRADOR` y las rutas a carpetas por sprint hicieron que la documentación contradijera al código; la reorganización a `docs/` y `src/` únicos eliminó las copias duplicadas.
- **El estándar evoluciona.** OWASP Top 10:2025 reordenó categorías (SSRF dentro de A01, cadena de suministro, manejo de condiciones excepcionales) y hubo que documentar la equivalencia con la plantilla.

### Análisis de causa raíz del problema principal

**Problema:** dos sprints después, el motor de optimización (EN-001, RSK-05) no tiene avance, mientras la calidad del resto mejoró mucho.

1. ¿Por qué no hay avance? Porque el trabajo del sprint se ocupó en corregir y medir lo ya construido.
2. ¿Por qué se priorizó eso? Porque es trabajo que no depende de un algoritmo desconocido y produce resultados visibles rápido.
3. ¿Por qué no se acotó el spike? Porque no tiene tiempo máximo ni criterio de salida definidos.
4. ¿Por qué no se definieron? Porque el backlog trata EN-001 como una historia grande y no como una investigación con presupuesto de tiempo.
5. ¿Por qué no se detectó antes? Porque ninguna ceremonia evalúa el avance de la ruta crítica contra la fecha de entrega del 23/11/2026.

**Causa raíz:** falta de un control de ruta crítica con un presupuesto de tiempo para el spike. **Contramedida:** acción 5 de la tabla.

## ¿Qué estamos haciendo bien?

- Se pasó de 0 pruebas del frontend y 16 del backend a **60 y 36** en verde, con cobertura global de **92,7 %** y Quality Gate en PASSED.
- Cada hallazgo se corrigió y quedó protegido por una prueba o una regla (por ejemplo, el registro de eventos de seguridad y el rol inexistente tienen su prueba).
- Backend y frontend están separados en `src/backend` y `src/frontend`, con un `.gitignore` que excluye dependencias, bases locales, secretos, copias temporales (`*~`) e informes de cobertura, y sin carpetas duplicadas por sprint.
- Los documentos conservan su historial de versiones y distinguen lo corregido de lo pendiente, sin declarar demostraciones ni pruebas que no se hicieron.
- El análisis es reproducible: `sonar-project.properties`, `.coveragerc`, el flujo de CI y los comandos del Documento 03 permiten repetirlo.
- Los sprints se cierran con una etiqueta Git antes de revisarlos, de modo que la revisión y la retrospectiva se hacen sobre un incremento congelado.

## ¿Qué podemos hacer mejor?

### Personas

- Quien implementa una corrección también la evalúa: repartir la revisión de las tres evaluaciones (calidad, seguridad y accesibilidad) a un integrante distinto del que corrigió.
- Falta capacitación en lectores de pantalla (NVDA o VoiceOver) para cubrir lo que axe-core no detecta (IMP-013).
- La demostración depende de una sola persona, el líder del proyecto: asignar un suplente para agendarla.

### Relaciones

- La aceptación del Product Owner lleva tres sprints pendiente (IMP-003): fijar con el docente la fecha de la demostración al inicio del sprint y no al final.
- Informar al docente que el spike EN-001 sigue sin iniciarse y acordar qué parte del backlog se recorta si no hay avance (RSK-09).
- Validar con el cliente ficticio DistriRápido el diseño de bloqueo de cuenta y la política de datos personales antes de implementar EN-008.

### Procesos

- Cerrar el sprint con etiqueta Git antes de revisar y retrospectar, y registrar la fecha de cierre en la Revisión.
- Aplicar la definición de hecho completa por historia (rutas feliz, infeliz y gold, cobertura ≥ 80 %, 0 bugs, 0 incumplimientos WCAG y documentación versionada).
- Trabajar con GitFlow: ramas `feature/*` hacia `develop` con Pull Request y un revisor, y `main` solo con versiones cerradas del sprint.
- Revisar manualmente tres puntos que las herramientas no cubren: valores fijos en la interfaz, reflujo en móvil y veracidad de los mensajes de estado.
- Dar al spike EN-001 un presupuesto de tiempo y un criterio de salida (ver acción 5).

### Herramientas

- Añadir SonarQube al flujo de CI y activar la protección de la rama `main` en GitHub.
- Añadir un script de lint del frontend (ESLint con su dependencia) y Lighthouse o WAVE como segunda herramienta de accesibilidad.
- Fijar las versiones del backend (archivo de bloqueo) en lugar de los rangos `>=`.
- Definir `ENVIRONMENT=production` y una `SECRET_KEY` propia en el entorno de despliegue.

### Acciones a realizar

| # | Acción | Dimensión | Responsable (propuesto) | Fecha objetivo | Indicador de cierre |
|---|---|---|---|---|---|
| 1 | Realizar la demostración y completar la tabla de registro del Documento 01; pasar US-001 y US-003 a "Hecho" si el PO las acepta | Relaciones | Perez Ordoñez Anthony Alexis (suplente: Tovar Arias Michael Aldo) | 23/10/2026 | Tabla con fecha, asistentes y decisión por historia |
| 2 | Activar la protección de `main` (Pull Request con 1 revisor y CI en verde) y añadir SonarQube a `ci.yml` | Herramientas / Procesos | Equipo completo | 30/10/2026 | Un Pull Request fusionado con CI verde y revisor |
| 3 | Agregar `npm run lint` con ESLint y ejecutarlo en CI | Herramientas | Perez Ordoñez Anthony Alexis | 30/10/2026 | 0 errores de lint en CI |
| 4 | Probar con NVDA o VoiceOver el recorrido de inicio de sesión, alta de vehículo y alta de pedido; implementar la trampa de foco en los modales | Personas / Herramientas | Tovar Arias Michael Aldo | 30/10/2026 | Documento 05 versión 1.1.0 con el resultado |
| 5 | Ejecutar el spike EN-001 con tope de 3 días y criterio de salida: GA, Búsqueda Tabú y OR-Tools medidos frente a 45 s con 50 pedidos; revisar el avance de la ruta crítica en cada revisión de sprint | Procesos | Fernandez Condor Jhon Smith | Primera semana del Sprint 4 | Script versionado con datos, tiempos y conclusión |
| 6 | Realizar la prueba de penetración de EN-002 e implementar el cifrado de campos y la anonimización de EN-008 | Procesos | Equipo completo | Cierre del Sprint 4 | Informe de prueba y pruebas automatizadas de cada criterio |
| 7 | Fijar versiones del backend, revisar `pip-audit` y desplegar con TLS, CSP, HSTS y `ENVIRONMENT=production` | Herramientas | Fernandez Condor Jhon Smith | Cierre del Sprint 4 | Documento 04 versión 1.2.0 con A02 en "Limpio" |
| 8 | Rotar la revisión: quien corrige un hallazgo no lo evalúa | Personas | Equipo completo | Desde el Sprint 4 | Campo "revisor" en cada Pull Request |

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 20/10/2026 | Sprint 3: primera retrospectiva basada en las evaluaciones de calidad, seguridad y accesibilidad. |
| 1.1.0 | 20/10/2026 | Se añaden el seguimiento de las acciones del Sprint 2, el análisis de causa raíz y acciones con indicador de cierre; el cierre del sprint pasa de acción a práctica adoptada. |
