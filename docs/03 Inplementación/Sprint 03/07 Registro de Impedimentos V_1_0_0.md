# Registro de impedimentos

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 3 (periodo 07/10/2026 al 20/10/2026)  
**Fecha de revisión del registro:** 09/11/2026  
**Versión del documento:** 3.2.0

[← Volver al README Principal](../../../README.md)

## Criterio de registro

Este registro contiene **solo los impedimentos del Sprint 3 que no dependen de la intervención de los integrantes del equipo**: limitaciones del entorno de ejecución, comportamientos de las herramientas y fallos de componentes de terceros que bloquearon o retrasaron el trabajo. Las tareas pendientes del equipo, las decisiones de planificación y los defectos propios se gestionan en el tablero del proyecto, la Revisión y la Retrospectiva, y no se registran aquí.

Cada entrada conserva su identificador desde que se abre. La numeración continúa la del [Registro de impedimentos del Sprint 2](../Sprint%2002/02%20Registro%20de%20Impedimentos%20V_1_0_0.md), que llegó a IMP-011. La prioridad combina el impacto en el objetivo del sprint (medir y mejorar la calidad) y en la fecha de cierre (20/10/2026).

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
|---|---|---|---|---|---|---|---|---|
| IMP-012 | 20/10/2026 | **Entorno / herramientas (Git en Windows):** al clonar el repositorio, `git checkout` se interrumpió con "Filename too long" porque varias rutas superaban los 260 caracteres de Windows. Quedaron archivos sin restaurar (el árbol de trabajo aparecía con borrados). Impacto: no se podía trabajar con una copia local completa. | Media | Ejecución de Git en el entorno de desarrollo | 20/10/2026 | Resuelto | 20/10/2026 | Se habilitó `core.longpaths=true` y se restauró el árbol con `git reset --hard HEAD`; se recuperaron los 131 archivos. |
| IMP-013 | 20/10/2026 | **Herramienta / integración continua (GitHub Actions):** la primera ejecución del flujo falló con una cobertura del backend de 67 %, frente al 86 % medido en local. Causa: con Python 3.12, coverage.py no sigue el código asíncrono de SQLAlchemy sin la opción `concurrency = greenlet`; en Python 3.14 sí lo hacía. Impacto: el umbral de 80 % bloqueaba el flujo aunque las pruebas pasaban. | Alta | Ejecución del flujo en GitHub Actions | 20/10/2026 | Resuelto | 20/10/2026 | `.coveragerc` ahora declara `concurrency = greenlet,thread`; el flujo pasa en verde con las mismas 36 pruebas. |
| IMP-014 | 20/10/2026 | **Entorno / herramientas (SonarQube en Docker Desktop):** el escáner de SonarQube fallaba con `ENOMEM` en el analizador de JavaScript y con `unexpected end of stream` al subir el informe. Causa: Docker Desktop disponía de 3,4 GB de memoria, compartidos con el servidor, y el montaje de carpetas de Windows (`-v`) hacía fallar la lectura de directorios. Impacto: el análisis no terminaba. | Alta | Ejecución del escáner | 21/10/2026 | Resuelto | 21/10/2026 | Se copió el código al contenedor con `docker cp` en lugar de montarlo, se enlazó el escáner a la red del contenedor de SonarQube (`--link`) y se limitó la memoria de Node.js y de Java; el análisis terminó con éxito. Detalle en el Documento 03. |
| IMP-015 | 21/10/2026 | **Herramienta / SonarQube (lectura de cobertura):** SonarQube mostraba 0 % de cobertura aunque las pruebas pasaban. Causa: Vitest escribe las rutas del informe `lcov` relativas a `src/frontend` y coverage.py las del XML relativas a `src/backend/app`, mientras SonarQube las resuelve desde la raíz del proyecto y no las asocia a ningún archivo. Impacto: el Quality Gate no reflejaba las pruebas existentes. | Media | Análisis de SonarQube | 21/10/2026 | Resuelto | 21/10/2026 | `scripts/preparar_cobertura.py` reescribe las rutas de ambos informes; la cobertura global medida es 92,7 %. |
| IMP-016 | 20/10/2026 | **Componentes de terceros:** `npm audit` reportó 6 vulnerabilidades en dependencias de desarrollo (`vite`, `vitest`, `tinypool` y `source-map-js`): 2 críticas, 2 altas y 2 moderadas; ninguna en producción. Impacto: riesgo en el entorno de desarrollo y en el criterio de dependencias sin vulnerabilidades críticas de la definición de hecho. | Media | Auditoría de dependencias (`npm audit`) | 20/10/2026 | Resuelto | 20/10/2026 | `npm audit fix` y actualización de Vitest y su plugin de cobertura a la versión 5; el resultado es 0 vulnerabilidades y las pruebas siguen en verde. |

## Seguimiento y escalamiento

Los impedimentos se revisan al inicio y al cierre de cada sprint y conservan su identificador y la fecha real de resolución. Un impedimento abierto que supere su fecha tope se eleva al Product Owner académico para acordar impacto y replanificación. Resumen al corte del 09/11/2026: **5 registrados, 5 resueltos, 0 en curso y 0 abiertos**.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Sprint 1: creación del registro con IMP-001 a IMP-003. |
| 2.0.0 | 05/10/2026 | Sprint 2: se actualizan IMP-001 a IMP-003 y se abren IMP-004 a IMP-011. |
| 3.0.0 | 20/10/2026 | Sprint 3: registro acumulado con IMP-012 a IMP-014. |
| 3.1.0 | 20/10/2026 | Se actualizan IMP-004, IMP-008, IMP-009 e IMP-012. |
| 3.2.0 | 09/11/2026 | Se reestructura el registro: el Sprint 3 solo conserva los impedimentos ajenos a la intervención de los integrantes (IMP-012 a IMP-016); las tareas pendientes del equipo se retiran del registro. |
