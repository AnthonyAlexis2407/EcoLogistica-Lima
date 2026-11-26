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
Plataforma web para optimizar rutas de última milla con enfoque sostenible. Planifica las rutas de reparto con un algoritmo propio (Clarke-Wright, 2-opt y búsqueda tabú opcional) que respeta capacidad, volumen, ventanas horarias, Pico y Placa y zonas protegidas; guía al conductor con una app instalable que funciona sin conexión; re-optimiza ante incidencias; avisa a las bodegas; calcula el CO₂ evitado y su equivalente en árboles; y protege los datos personales con cifrado. Estado final: los 10 requisitos funcionales y las 10 reglas de negocio cumplen; 8 de los 10 requisitos no funcionales cumplen y 2 (conmutación por falla y escalado automático) cumplen en pruebas, pero necesitan un plan de pago de la plataforma para cumplir en la nube ([Matriz de cumplimiento](docs/03%20Inplementaci%C3%B3n/Sprint%204/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md)).

## Estructura del repositorio

```text
docs/
  01 Inicio/            documentos de la fase de inicio (versión vigente de cada uno)
  02 Planificación/     documentos de la fase de planificación
  03 Inplementación/
    Sprint 01/          informes del Sprint 1
    Sprint 02/          informes del Sprint 2
    Sprint 03/          informes y evaluaciones del Sprint 3
    Sprint 4/           revisión, retrospectiva, Playwright, usabilidad (SUS), guía de despliegue, matriz de cumplimiento y estudio de algoritmos
    reduccion del impacto ambiental/   informe Green IT y estándares de ingeniería de software
  04 Cierre/            siete documentos de gestión y cierre del proyecto (estado, variación, EVM, tableros, radiadores, final y lecciones)
  05 Video proyecto/    guion del video y el video MP4 de 5 minutos
src/
  backend/              API FastAPI (Python) y sus pruebas (tests/)
  frontend/             interfaz React + TypeScript + Vite; pruebas E2E en e2e/ y playwright.config.ts
.github/workflows/      ci.yml (calidad), tests.yml (pruebas, PostgreSQL, conmutación por falla y E2E), deploy-production.yml (despliegue), monitoreo.yml (prueba de humo por hora) y green-audit.yml (Green IT)
.github/pull_request_template.md   plantilla de Pull Request
lighthouserc.json       umbrales de Lighthouse CI
Dockerfile, render.yaml imagen de producción y plano de despliegue
docker-compose.e2e.yml  entorno local de pruebas E2E (misma imagen que producción)
docker-compose.failover.yml  dos instancias, balanceador y PostgreSQL para medir el RTO (docker/nginx-failover.conf)
pyproject.toml          configuración de Ruff y Bandit
scripts/                medición de la API, SWDM v4, cobertura, verificación de enlaces, resumen de Playwright, cálculo SUS y EVM, estudio de algoritmos y medición del RTO
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

### Sprint 4
- [01 Revisión del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%204/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md): historias completadas con enlaces a commits y pull requests, demostración y pendientes.
- [02 Retrospectiva del Sprint](docs/03%20Inplementaci%C3%B3n/Sprint%204/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md): aprendizajes y plan de mejora con responsables e indicadores.
- [03 Análisis Playwright](docs/03%20Inplementaci%C3%B3n/Sprint%204/03%20Analisis%20PlayWrigth%20V_1_0_0.md): pruebas E2E en Chromium, Firefox y WebKit, Web Vitals, tiempos de la API, disponibilidad y resiliencia.
- [04 Usabilidad (SUS)](docs/03%20Inplementaci%C3%B3n/Sprint%204/04%20Usabilidad%20V_1_0_0.md): evaluación cuantitativa con la escala SUS (datos simulados con fines académicos).
- [05 Guía de despliegue](docs/03%20Inplementaci%C3%B3n/Sprint%204/05%20Gu%C3%ADa%20de%20despliegue.md): cómo llega la aplicación a producción, cómo configurar los secretos y la base PostgreSQL.
- [06 Matriz de cumplimiento](docs/03%20Inplementaci%C3%B3n/Sprint%204/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md): verifica cada requisito funcional, no funcional, regla de negocio y estándar del curso contra el código, las pruebas y los informes, con la evidencia y los límites.
- [07 Estudio de algoritmos](docs/03%20Inplementaci%C3%B3n/Sprint%204/07%20Estudio%20de%20algoritmos%20V_1_0_0.md): comparación de Clarke-Wright, búsqueda tabú, algoritmo genético y OR-Tools (spike EN-001).

**Producción:** la aplicación se despliega sola desde `main` y está activa en <https://ecologistica-lima.onrender.com>; la prueba de humo de Playwright confirma cada despliegue ([última ejecución](https://github.com/AnthonyAlexis2407/EcoLogistica-Lima/actions/runs/44020768595)).

**Estado de los flujos de trabajo:** las insignias de la parte superior se actualizan solas con la última ejecución en la rama `main`. [`ci.yml`](.github/workflows/ci.yml) verifica el estilo, el análisis estático, la compilación y las dependencias; [`tests.yml`](.github/workflows/tests.yml) ejecuta las pruebas unitarias, de integración y E2E y guarda los informes como artefactos; [`deploy-production.yml`](.github/workflows/deploy-production.yml) despliega con GitHub Secrets.

**Novedades del producto (versión 4.0.0):** motor de rutas con restricciones duras (1.000 pedidos en alrededor de 1 s), mapa interactivo, app del conductor instalable y sin conexión, re-optimización ante incidencias, notificaciones a bodegas, administración, reportes CSV, Excel y PDF, dashboard con filtros, CO₂ evitado y compensación en árboles, datos personales cifrados y base PostgreSQL en producción.

## Fase 04: Cierre del Proyecto

Carpeta `docs/04 Cierre/`; cada documento enlaza de regreso a este README. Fecha de corte: 28/11/2026; sustentación: 30/11/2026.

- [01 Reporte de Estado](docs/04%20Cierre/01%20Reporte%20de%20Estado%20V_1_0_0.md): alcance, cronograma, costos, proyección y riesgos del último periodo.
- [02 Reporte de Variación](docs/04%20Cierre/02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md): planificado frente a real en cronograma, costo y calidad, con causa raíz y respuesta.
- [03 Reporte de Análisis de Valor Ganado - EVM](docs/04%20Cierre/03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md): PV, EV, AC, SV, CV, SPI, CPI y las tres fórmulas de EAC.
- [04 Tableros de Control - Híbridos](docs/04%20Cierre/04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md): semáforo por componente y gráficos de tendencia, flujo, burbujas y barras.
- [05 Radiadores de Información](docs/04%20Cierre/05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md): burndown, burnup, tablero Kanban, mood chart y tablero de retrospectiva.
- [06 Reporte Final del Proyecto](docs/04%20Cierre/06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md): descripción, desempeño, riesgos y evaluación del éxito.
- [07 Reporte Final de Lecciones Aprendidas](docs/04%20Cierre/07%20Reporte%20Final%20de%20Lecciones%20Aprendidas%20V_1_0_0.md): matriz de aprendizajes y conclusiones.

## Fase 05: Video del proyecto

- [Guion del video](docs/05%20Video%20proyecto/Guion%20del%20video.md): estructura minuto a minuto (1 minuto de presentación y 4 de demostración) y lista de verificación. El archivo `.mp4` va en esa misma carpeta.

## Reducción del impacto ambiental (Green IT)

Carpeta `docs/03 Inplementación/reduccion del impacto ambiental/`; cada documento enlaza de regreso a este README y entre sí.

- [01 Informe de reducción del impacto ambiental](docs/03%20Inplementaci%C3%B3n/reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md): ocho optimizaciones con código ANTES y DESPUÉS, mediciones con Lighthouse y cálculo SWDM v4.
- [02 Estándares de ingeniería de software y guía de desarrollo verde](docs/03%20Inplementaci%C3%B3n/reduccion%20del%20impacto%20ambiental/02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md): ISO/IEC 25010, GSF, W3C WSG, matriz de mapeo y flujos de CI/CD.

## Instalación y ejecución local

1. Backend: `cd src/backend && pip install -r requirements.txt && python -m app.seed && uvicorn app.main:app --port 8000` (variables opcionales: `SECRET_KEY`, `DATA_ENCRYPTION_KEY`, `DATABASE_URL`; ver `src/backend/README.md`).
2. Frontend: `cd src/frontend && npm ci && npm run dev` (o `npm run build` y la API lo sirve desde el mismo origen).
3. Cuentas de demostración (solo con datos semilla): `admin@ecologistica.pe / Admin2026!`, `operador@ecologistica.pe / Operador2026!`, `bodega@tienda.pe / Bodega2026!`, `conductor@ecologistica.pe / Conductor2026!`, `auditor@ecologistica.pe / Auditor2026!`.
4. Despliegue: [Guía de despliegue](docs/03%20Inplementaci%C3%B3n/Sprint%204/05%20Gu%C3%ADa%20de%20despliegue.md). Los montos del proyecto están en soles (S/).

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
# Recalcular el EVM y regenerar los gráficos de los tableros de cierre
python scripts/calcular_evm.py --graficos
# Estudio comparativo de algoritmos de rutas (spike EN-001); con `pip install ortools` incluye OR-Tools
python scripts/spike_algoritmos.py --tamanos 50 150 400 --semillas 3 --limite 10
# Pruebas contra PostgreSQL real (defina la URL de una base de pruebas: se vacía y recrea)
TEST_DATABASE_URL=postgresql+asyncpg://usuario:clave@localhost:5432/ecologistica PYTHONPATH=src/backend python -m pytest src/backend/tests/test_postgres.py -v
# Conmutación por falla: dos instancias, balanceador y PostgreSQL; mide el RTO deteniendo cada instancia
docker compose -f docker-compose.failover.yml up --build -d --wait && python scripts/medir_rto.py
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
| Inicio · 03 Declaración de la visión | 1.1.0 | 28/11/2026 | Factor de conversión de CO₂ a árboles (RF-010) |
| Inicio · 06 Requisitos funcionales | 1.2.0 | 28/11/2026 | Los diez requisitos implementados y verificados |
| Inicio · 07 Requisitos no funcionales | 1.2.0 | 28/11/2026 | Ocho requisitos cumplen y dos cumplen en pruebas |
| Inicio · 10 Stack tecnológico | 1.6.0 | 28/11/2026 | Cifrado, PostgreSQL, PWA, reportes y alta disponibilidad |
| Inicio · 11 Base de datos | 1.3.0 | 28/11/2026 | Modelo implementado (15 tablas) y clasificación de datos personales |
| Inicio · 12 Modelo C4 | 1.4.0 | 28/11/2026 | Estado de implementación final y componentes nuevos |
| Planificación · 02 Artefactos Jira | 1.1.0 | 05/10/2026 | Estado real de Jira |
| Planificación · 04 Presupuesto del proyecto | 1.1.0 | 28/11/2026 | Montos convertidos de dólares a soles (S/ 3,75 por USD) |
| Planificación · 03 Registro de riesgos | 1.5.0 | 28/11/2026 | Se añaden RSK-17 y RSK-18 y se actualiza el estado de los riesgos |
| Sprint 01 · Informe de estado | 1.1.0 | 20/10/2026 | Se retira la demostración del informe |
| Sprint 02 · Informe de estado, Revisión y Retrospectiva | 2.2.0 | 20/10/2026 | Criterios por ruta, cierre de sprint y rutas |
| Sprint 02 · Registro de Impedimentos | 2.1.0 | 05/10/2026 | DEF-002 y DEF-003 corregidos |
| Sprint 03 · 01 Revisión y 02 Retrospectiva | 1.1.0 | 20/10/2026 | Cierre formal, DoD y rutas de aceptación |
| Sprint 03 · 03 Calidad de código | 1.2.0 | 21/10/2026 | Medición real con SonarQube |
| Sprint 03 · 04 OWASP | 1.3.0 | 28/11/2026 | Se corrige la enumeración de usuarios y se cierra el cifrado de datos personales |
| Sprint 03 · 05 WCAG | 1.0.0 | 20/10/2026 | Primera evaluación |
| Sprint 03 · 06 Informe de estado | 3.1.0 | 20/10/2026 | Sprint 3 |
| Sprint 03 · 07 Registro de Impedimentos | 3.2.0 | 09/11/2026 | Solo impedimentos ajenos a la intervención del equipo |
| Green IT · 01 Informe de reducción del impacto ambiental | 1.0.0 | 10/11/2026 | Primera versión; redacción simplificada, glosario y referencias cruzadas |
| Green IT · 02 Estándares de ingeniería de software | 1.0.0 | 10/11/2026 | Primera versión; redacción simplificada, guía del YAML y referencias cruzadas |
| Sprint 4 · 03 Análisis Playwright | 2.0.0 | 28/11/2026 | Pruebas del cierre y ejecución final |
| Sprint 4 · 04 Usabilidad | 1.2.0 | 28/11/2026 | Selector de mapa aplicado |
| Sprint 4 · versiones iniciales de 01, 02 y 05 | 1.1.0 | 17/11/2026 | Primera versión del 16/11; actualizada con el despliegue en producción y las cifras de `main` |
| Sprint 4 · 01 Revisión, 02 Retrospectiva y 05 Guía de despliegue | 2.0.0 | 28/11/2026 | Cierre del sprint: implementación final, retrospectiva de cierre y PostgreSQL |
| Sprint 4 · 06 Matriz de cumplimiento | 2.0.0 | 28/11/2026 | Cumplimiento final de requisitos, reglas de negocio y estándares |
| Sprint 4 · 07 Estudio de algoritmos | 1.0.0 | 28/11/2026 | Primera versión |
| Cierre · 01 a 07 (Estado, Variación, EVM, Tableros, Radiadores, Final y Lecciones) | 2.0.0 | 28/11/2026 | Recalculados con el cierre del proyecto en cuatro sprints |
