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

## Pull Requests

1. Se crea la rama desde `develop` (`git checkout -b feature/<tema>`), se trabaja con commits descriptivos y se sube con `git push -u origin feature/<tema>`.
2. En GitHub se pulsa **Compare & pull request**, se verifica `base` y `compare`, se completa la plantilla de [`.github/pull_request_template.md`](.github/pull_request_template.md), se elige al menos un revisor y se crea el Pull Request.
3. El revisor inspecciona la pestaña **Files changed** y elige **Comment**, **Request changes** o **Approve**; si pide cambios, el autor sube un commit nuevo y el Pull Request se actualiza solo.
4. Con **Approved** y el CI en verde se integra con **Squash and merge**, se elimina la rama remota y se limpia la local (`git checkout main`, `git pull origin main`, `git branch -d feature/<tema>`).

### Protección de `main`

En *Settings, Branches* se crea una regla para `main` con: **Require a pull request before merging** con 1 aprobación, **Dismiss stale pull request approvals when new commits are pushed** y **Require status checks to pass before merging** con los controles `backend`, `frontend` y `audit`.

## Mensajes de commit

Formato `tipo(ámbito): resumen`, con tipos `feat`, `fix`, `docs`, `test`, `refactor` y `chore`. Ejemplo: `fix(auth): persistir el contador de intentos antes de lanzar la excepción`.

## Definición de hecho (DoD)

1. Los criterios de aceptación pasan en las rutas feliz, infeliz y gold mediante pruebas automatizadas.
2. Cobertura global ≥ 80 %.
3. SonarQube sin bugs ni vulnerabilidades abiertos; `npm audit` sin vulnerabilidades altas ni críticas.
4. Sin incumplimientos WCAG AA en axe-core.
5. Documentos afectados actualizados y versionados (ver abajo).
6. Aceptación del Product Owner.

## Automatización

- `.github/workflows/ci.yml`: pruebas, cobertura, tipos, *build* y auditoría de dependencias.
- `.github/workflows/green-audit.yml`: Lighthouse CI sobre la aplicación servida por FastAPI (umbrales en [`lighthouserc.json`](lighthouserc.json)).
- Ambos usan permisos mínimos (`contents: read`), versiones fijas de las acciones y caché de dependencias.

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
