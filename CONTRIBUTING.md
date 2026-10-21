# Guía de contribución

[← Volver al README Principal](README.md)

## Flujo de ramas (GitFlow simplificado)

| Rama | Uso | Se fusiona hacia |
|---|---|---|
| `main` | Versiones cerradas al final de cada sprint; cada cierre lleva la etiqueta `sprint-N-cierre`. | — |
| `develop` | Integración continua del trabajo del sprint. | `main` al cerrar el sprint |
| `feature/<tema>` | Una historia o un cambio acotado (por ejemplo `feature/sprint-3-reorganizacion`). | `develop` por Pull Request |
| `fix/<tema>` | Corrección de un defecto (por ejemplo `fix/def-004-bloqueo`). | `develop` por Pull Request |

Reglas: no se hace commit directo a `main` ni a `develop`; todo Pull Request necesita un revisor distinto del autor y el CI en verde.

## Mensajes de commit

Formato `tipo(ámbito): resumen`, con tipos `feat`, `fix`, `docs`, `test`, `refactor` y `chore`. Ejemplo: `fix(auth): persistir el contador de intentos antes de lanzar la excepción`.

## Definición de hecho (DoD)

1. Los criterios de aceptación pasan en las rutas feliz, infeliz y gold mediante pruebas automatizadas.
2. Cobertura global ≥ 80 %.
3. SonarQube sin bugs ni vulnerabilidades abiertos; `npm audit` sin vulnerabilidades altas ni críticas.
4. Sin incumplimientos WCAG AA en axe-core.
5. Documentos afectados actualizados y versionados (ver abajo).
6. Aceptación del Product Owner.

## Comprobaciones locales antes de abrir un Pull Request

```bash
PYTHONPATH=src/backend python -m pytest src/backend/tests --cov=src/backend/app --cov-config=.coveragerc
```

```bash
cd src/frontend && npm ci && npm run typecheck && npm run test:coverage && npm run build
```

## Versionado de documentos

El nombre de cada archivo conserva el sufijo `V_1_0_0` que exigen las consignas; la versión vigente (Semantic Versioning) figura en el encabezado y en el "Control de versiones" de cada documento. La versión mayor de los informes de Implementación coincide con el sprint (`3.x.x` = Sprint 3). Todo cambio en el código que contradiga un documento obliga a actualizarlo y subir su versión en el mismo Pull Request.

## Estructura y archivos que no se suben

El código vive en `src/backend` y `src/frontend`; la documentación, en `docs/`. El `.gitignore` excluye dependencias, bases locales, secretos, copias temporales (`*~`, `*.bak`), informes de cobertura y archivos comprimidos.
