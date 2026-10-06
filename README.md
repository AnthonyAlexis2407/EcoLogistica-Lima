# Taller-2 - EcoLogística Lima

## Proyecto Final de Carrera - Optimizador de Rutas Sostenibles

### Integrantes del Equipo:
- Fernandez Condor Jhon Smith
- Perez Ordoñez Anthony Alexis
- Tovar Arias Michael Aldo

### Descripción
Sistema web para optimizar rutas de última milla con enfoque sostenible, aplicando metaheurísticas (Algoritmos Genéticos, Búsqueda Tabú) para reducir costos y emisiones de CO₂.

## Fase 01: Inicio del Proyecto

- [Selección del enfoque del proyecto](docs/01%20Inicio/01.%20Selecci%C3%B3n%20del%20enfoque%20del%20proyecto%20V_1_0_0.md)
- [Acta de constitución](docs/01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_0.md)
- [Declaración de la visión](docs/01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_0.md)
- [Registro de supuestos y restricciones](docs/01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_0.md)
- [Registro de interesados](docs/01%20Inicio/05.%20Registro%20de%20interesados%20V_1_0_0.md)
- [Requisitos funcionales](docs/01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md)
- [Requisitos no funcionales](docs/01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md)
- [Usuarios](docs/01%20Inicio/08.%20Usuarios%20V_1_0_0.md)
- [Reglas de negocio](docs/01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_0.md)
- [Stack tecnológico](docs/01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md)
- [Base de datos](docs/01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md)
- [Modelo C4](docs/01%20Inicio/12.%20Modelo%20C4%20V_1_0_0.md)
- [Restricciones](docs/01%20Inicio/13.%20Restricciones%20V_1_0_0.md)

## Fase 02: Planificación del Proyecto

- [Transformando a ágil](docs/02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md)
- [Artefactos Jira](docs/02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md)
- [Registro de riesgos](docs/02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md)
- [Presupuesto del proyecto](docs/02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)

## Fase 03: Implementación - Sprint 2

Los informes siguientes corresponden al Sprint 2 y están actualizados al 05/10/2026 (versión 2.1.0 de cada documento; el historial de cada uno conserva la versión 1.0.0 del Sprint 1). Se basan en evidencia verificada: pruebas del backend (16 pasan, cobertura 67 %), compilación del frontend y consulta a Jira. No se declara demostración a stakeholders ni aceptación del Product Owner porque el repositorio no contiene evidencia de ellas.

- [Informe de estado del proyecto](docs/03%20Implementaci%C3%B3n/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md)
- [Registro de Impedimentos](docs/03%20Implementaci%C3%B3n/02%20Registro%20de%20Impedimentos%20V_1_0_0.md)
- [Revisión del Sprint](docs/03%20Implementaci%C3%B3n/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)
- [Retrospectiva del Sprint](docs/03%20Implementaci%C3%B3n/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)

## Estructura del código fuente

- [Frontend](src/frontend/README.md): React 18, TypeScript y Vite; inicio de sesión, vehículos y pedidos consumiendo la API.
- [Backend](src/backend/README.md): FastAPI con SQLAlchemy asíncrono; autenticación JWT, vehículos, pedidos y pruebas de aceptación y regresión.

## Convención de versionado y nombres de archivo

- El **nombre** de cada archivo conserva el sufijo `V_1_0_0` que exigen las consignas de entrega. La **versión vigente** (Semantic Versioning) de cada documento está en su encabezado (`Versión`) y en su historial (*Historial de Control de Cambios* o *Control de versiones*).
- En los 4 informes de Implementación la versión mayor coincide con el número de sprint: `2.x.x` = Sprint 2.
- Documentos con versión distinta de 1.0.0 al 05/10/2026:

| Documento | Versión | Última actualización | Motivo |
|---|---|---|---|
| Fase 01 · 04 Registro de supuestos y restricciones | 1.1.0 | 08/09/2026 | Corrección de R01 (presupuesto S/ 16,300) |
| Fase 01 · 08 Usuarios | 1.2.0 | 05/10/2026 | RBAC implementado; DEF-002 y DEF-003 corregidos |
| Fase 01 · 10 Stack tecnológico | 1.1.0 | 05/10/2026 | Decisiones de implementación (ORM, SQLite en desarrollo, bcrypt/JWT) |
| Fase 01 · 11 Base de datos | 1.1.0 | 05/10/2026 | Modelo implementado frente al DDL; campos de bloqueo de cuenta |
| Fase 01 · 12 Modelo C4 | 1.1.0 | 05/10/2026 | Estado de implementación por contenedor |
| Fase 02 · 02 Artefactos Jira | 1.1.0 | 05/10/2026 | Estado real de Jira (sprint, versión, fechas) |
| Fase 02 · 03 Registro de riesgos | 1.1.0 | 05/10/2026 | Reevaluación de RSK-05 y nuevos RSK-09 a RSK-11 |
| Fase 03 · 01 a 04 (informes del sprint) | 2.1.0 | 05/10/2026 | Sprint 2 |
