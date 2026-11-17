# Taller-2 - EcoLogística Lima

[![CI](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/ci.yml/badge.svg)](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/ci.yml)
[![Tests](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/tests.yml/badge.svg)](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/tests.yml)
[![Deploy Production](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/deploy-production.yml/badge.svg)](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/deploy-production.yml)
[![Green IT](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/green-audit.yml/badge.svg)](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/workflows/green-audit.yml)

## Proyecto Final de Carrera - Optimizador de Rutas Sostenibles

**Aplicación en producción:** <https://ecologistica-lima.onrender.com> (Render; estado de salud en <https://ecologistica-lima.onrender.com/api/health>). En el plan gratuito el servicio se duerme tras 15 minutos sin uso: la primera visita puede tardar hasta 1 minuto.

### Integrantes del Equipo
- Fernandez Condor Jhon Smith
- Perez Ordoñez Anthony Alexis (líder del proyecto)
- Tovar Arias Michael Aldo

### Descripción
Sistema web para optimizar rutas de última milla con enfoque sostenible, aplicando metaheurísticas (Algoritmos Genéticos, Búsqueda Tabú) para reducir costos y emisiones de CO₂.

## Estructura del repositorio

```text
docs/
  01 Inicio/            documentos de la fase de inicio (versión vigente de cada uno)
  02 Planificación/     documentos de la fase de planificación
  03 Inplementación/
    Sprint 01/          informes del Sprint 1
    Sprint 02/          informes del Sprint 2
    Sprint 03/          informes y evaluaciones del Sprint 3
    Sprint 4/           revisión, retrospectiva, Playwright, usabilidad (SUS) y guía de despliegue
    reduccion del impacto ambiental/   informe Green IT y estándares de ingeniería de software
src/
  backend/              API FastAPI (Python) y sus pruebas (tests/)
  frontend/             interfaz React + TypeScript + Vite; pruebas E2E en e2e/ y playwright.config.ts
.github/workflows/      ci.yml (calidad), tests.yml (pruebas y E2E), deploy-production.yml (despliegue) y green-audit.yml (Green IT)
.github/pull_request_template.md   plantilla de Pull Request
lighthouserc.json       umbrales de Lighthouse CI
Dockerfile, render.yaml imagen de producción y plano de despliegue
docker-compose.e2e.yml  entorno local de pruebas E2E (misma imagen que producción)
pyproject.toml          configuración de Ruff y Bandit
scripts/                medición de la API, SWDM v4, cobertura, verificación de enlaces, resumen de Playwright y cálculo SUS
CONTRIBUTING.md         flujo de ramas, DoD y versionado
sonar-project.properties, .coveragerc
```

Cada sprint cerrado tiene una etiqueta Git: `sprint-1-cierre`, `sprint-2-cierre` y `sprint-3-cierre`. Los datos sensibles (secretos de despliegue) no están en el repositorio: viven en GitHub Secrets.

## Fase 01: Inicio del Proyecto

- [01. Selección del enfoque del proyecto](docs/01%20Inicio/01.%20Selecci%C3%B3n%20del%20enfoque%20del%20proyecto%20V_1_0_0.md)
- [02. Acta de constitución](docs/01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_0.md)
- [03. Declaración de la visión](docs/01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_0.md)
- [04. Registro de supuestos y restricciones](docs/01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_0.md)
- [05. Registro de interesados](docs/01%20Inicio/05.%20Registro%20de%20interesados%20V_1_0_0.md)
- [06. Requisitos funcionales](docs/01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md)
- [07. Requisitos no funcionales](docs/01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md)
- [08. Usuarios](docs/01%20Inicio/08.%20Usuarios%20V_1_0_0.md)
- [09. Reglas de negocio](docs/01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_0.md)
- [10. Stack tecnológico](docs/01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md)
- [11. Base de datos](docs/01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md)
- [12. Modelo C4](docs/01%20Inicio/12.%20Modelo%20C4%20V_1_0_0.md)
- [13. Restricciones](docs/01%20Inicio/13.%20Restricciones%20V_1_0_0.md)

## Fase 02: Planificación del Proyecto

- [01 Transformando a ágil](docs/02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md)
- [02 Artefactos Jira](docs/02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md)
- [03 Registro de riesgos](docs/02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md)
- [04 Presupuesto del proyecto](docs/02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)

## Fase 03: Implementación

### Sprint 1
- [Informe de estado del proyecto](docs/03%20Inplementaci%C3%B3n/Sprint%2001/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md)
- [Registro de Impedimentos](docs/03%20Inplementaci%C3%B3n/Sprint%2001/02%20Registro%20de%20Impedimentos%20V_1_0_0.md)
- [Revisión del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%2001/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)
- [Retrospectiva del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%2001/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)

### Sprint 2
- [Informe de estado del proyecto](docs/03%20Inplementaci%C3%B3n/Sprint%2002/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md)
- [Registro de Impedimentos](docs/03%20Inplementaci%C3%B3n/Sprint%2002/02%20Registro%20de%20Impedimentos%20V_1_0_0.md)
- [Revisión del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%2002/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)
- [Retrospectiva del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%2002/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)

### Sprint 3
- [01 Revisión del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md)
- [02 Retrospectiva del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)
- [03 Calidad de código (SonarQube)](docs/03%20Inplementaci%C3%B3n/Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md)
- [04 Seguridad OWASP Top 10 2025](docs/03%20Inplementaci%C3%B3n/Sprint%2003/04%20OWASP%20V_1_0_0.md)
- [05 Accesibilidad WCAG](docs/03%20Inplementaci%C3%B3n/Sprint%2003/05%20WCAG%20V_1_0_0.md)
- [06 Informe de estado del proyecto](docs/03%20Inplementaci%C3%B3n/Sprint%2003/06%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md)
- [07 Registro de Impedimentos](docs/03%20Inplementaci%C3%B3n/Sprint%2003/07%20Registro%20de%20Impedimentos%20V_1_0_0.md)

### Sprint 4 (vigente)
- [01 Revisión del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%204/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md): historias completadas con enlaces a commits y pull requests, demostración y pendientes.
- [02 Retrospectiva del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%204/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md): aprendizajes y plan de mejora con responsables e indicadores.
- [03 Análisis Playwright](docs/03%20Inplementaci%C3%B3n/Sprint%204/03%20Analisis%20PlayWrigth%20V_1_0_0.md): pruebas E2E en Chromium, Firefox y WebKit, Web Vitals, tiempos de la API, disponibilidad y resiliencia.
- [04 Usabilidad (SUS)](docs/03%20Inplementaci%C3%B3n/Sprint%204/04%20Usabilidad%20V_1_0_0.md): evaluación cuantitativa con la escala SUS (datos simulados con fines académicos).
- [05 Guía de despliegue](docs/03%20Inplementaci%C3%B3n/Sprint%204/05%20Gu%C3%ADa%20de%20despliegue.md): cómo llega la aplicación a producción y cómo configurar los secretos.

**Producción:** la aplicación se despliega sola desde `main` y está activa en <https://ecologistica-lima.onrender.com>; la prueba de humo de Playwright confirma cada despliegue ([última ejecución](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768595)).

**Estado de los flujos de trabajo:** las insignias de la parte superior se actualizan solas con la última ejecución en la rama `main`. [`ci.yml`](.github/workflows/ci.yml) verifica el estilo, el análisis estático, la compilación y las dependencias; [`tests.yml`](.github/workflows/tests.yml) ejecuta las pruebas unitarias, de integración y E2E y guarda los informes como artefactos; [`deploy-production.yml`](.github/workflows/deploy-production.yml) despliega con GitHub Secrets.

## Reducción del impacto ambiental (Green IT)

Carpeta `docs/03 Inplementación/reduccion del impacto ambiental/`; cada documento enlaza de regreso a este README y entre sí.

- [01 Informe de reducción del impacto ambiental](docs/03%20Inplementaci%C3%B3n/reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md): ocho optimizaciones con código ANTES y DESPUÉS, mediciones con Lighthouse y cálculo SWDM v4.
- [02 Estándares de ingeniería de software y guía de desarrollo verde](docs/03%20Inplementaci%C3%B3n/reduccion%20del%20impacto%20ambiental/02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md): ISO/IEC 25010, GSF, W3C WSG, matriz de mapeo y flujos de CI/CD.

## Cómo verificar el proyecto

```bash
# Backend: pruebas con cobertura (desde la raíz)
PYTHONPATH=src/backend python -m pytest src/backend/tests --cov=src/backend/app --cov-config=.coveragerc -q
# Frontend: tipos, lint, pruebas unitarias y compilación
cd src/frontend && npm ci && npm run typecheck && npm run lint && npm run test:coverage && npm run build
# E2E con la imagen de producción (Docker): informes en src/frontend/resultados-e2e
docker compose -f docker-compose.e2e.yml up --build --abort-on-container-exit --exit-code-from e2e
# Verificar los enlaces y referencias cruzadas de la documentación
python scripts/verificar_enlaces.py
```

## Código fuente

- [Frontend](src/frontend/README.md): React 18, TypeScript y Vite.
- [Backend](src/backend/README.md): FastAPI con SQLAlchemy asíncrono, autenticación JWT, vehículos y pedidos.
- [Guía de contribución](CONTRIBUTING.md): GitFlow, Pull Requests, definición de hecho y versionado.

## Convención de versionado y nombres de archivo

- El **nombre** de cada archivo conserva el sufijo `V_1_0_0` que exigen las consignas. La **versión vigente** (Semantic Versioning) de cada documento está en su encabezado y en su control de versiones.
- En los informes de Implementación la versión mayor coincide con el sprint: `1.x.x`, `2.x.x` y `3.x.x`. Los documentos nuevos del Sprint 4 nacen en `1.0.0`, versión que exige su nombre de archivo.

| Documento | Versión | Última actualización | Motivo |
|---|---|---|---|
| Inicio · 04 Registro de supuestos y restricciones | 1.1.0 | 08/09/2026 | Corrección de R01 (presupuesto S/ 16,300) |
| Inicio · 08 Usuarios | 1.3.0 | 20/10/2026 | Se elimina el rol `ADMINISTRADOR` (IMP-008) |
| Inicio · 10 Stack tecnológico | 1.4.0 | 16/11/2026 | Sprint 4: Playwright, lint, CI/CD, Docker y Render |
| Inicio · 11 Base de datos | 1.1.0 | 05/10/2026 | Modelo implementado frente al DDL |
| Inicio · 12 Modelo C4 | 1.2.0 | 16/11/2026 | Vista de despliegue en producción (un solo contenedor) |
| Planificación · 02 Artefactos Jira | 1.1.0 | 05/10/2026 | Estado real de Jira |
| Planificación · 03 Registro de riesgos | 1.3.0 | 16/11/2026 | Se añaden RSK-13 y RSK-14 |
| Sprint 01 · Informe de estado | 1.1.0 | 20/10/2026 | Se retira la demostración del informe |
| Sprint 02 · Informe de estado, Revisión y Retrospectiva | 2.2.0 | 20/10/2026 | Criterios por ruta, cierre de sprint y rutas |
| Sprint 02 · Registro de Impedimentos | 2.1.0 | 05/10/2026 | DEF-002 y DEF-003 corregidos |
| Sprint 03 · 01 Revisión y 02 Retrospectiva | 1.1.0 | 20/10/2026 | Cierre formal, DoD y rutas de aceptación |
| Sprint 03 · 03 Calidad de código | 1.2.0 | 21/10/2026 | Medición real con SonarQube |
| Sprint 03 · 04 OWASP | 1.2.0 | 09/11/2026 | CSP aplicada al frontend servido por la API |
| Sprint 03 · 05 WCAG | 1.0.0 | 20/10/2026 | Primera evaluación |
| Sprint 03 · 06 Informe de estado | 3.1.0 | 20/10/2026 | Sprint 3 |
| Sprint 03 · 07 Registro de Impedimentos | 3.2.0 | 09/11/2026 | Solo impedimentos ajenos a la intervención del equipo |
| Green IT · 01 Informe de reducción del impacto ambiental | 1.0.0 | 10/11/2026 | Primera versión; redacción simplificada, glosario y referencias cruzadas |
| Green IT · 02 Estándares de ingeniería de software | 1.0.0 | 10/11/2026 | Primera versión; redacción simplificada, guía del YAML y referencias cruzadas |
| Sprint 4 · 01 Revisión, 02 Retrospectiva, 03 Análisis Playwright, 04 Usabilidad y 05 Guía de despliegue | 1.1.0 | 17/11/2026 | Primera versión del 16/11; actualizada con el despliegue en producción y las cifras de `main` |
