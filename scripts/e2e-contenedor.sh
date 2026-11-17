#!/usr/bin/env bash
# Uso: e2e-contenedor.sh [opciones de playwright], por ejemplo --project=firefox
# Ejecuta las pruebas E2E dentro del contenedor de Playwright (lo usa docker-compose.e2e.yml).
# Trabaja sobre una copia en /tmp porque en Docker Desktop para Windows Playwright no puede borrar y recrear
# carpetas dentro de un volumen montado. Al terminar copia los informes a src/frontend/resultados-e2e/.
set -u
ORIGEN=/work/src/frontend
TRABAJO=/tmp/e2e
DESTINO="$ORIGEN/resultados-e2e/${ETIQUETA:-completo}"

mkdir -p "$TRABAJO"
(cd "$ORIGEN" && tar cf - --exclude=node_modules --exclude=test-results --exclude=playwright-report --exclude=resultados-e2e .) | tar xf - -C "$TRABAJO"
ln -sfn "$ORIGEN/node_modules" "$TRABAJO/node_modules"

cd "$TRABAJO"
npx playwright test "$@"
codigo=$?

mkdir -p "$DESTINO"
cp -rf playwright-report test-results "$DESTINO"/ 2>/dev/null || true
exit "$codigo"
