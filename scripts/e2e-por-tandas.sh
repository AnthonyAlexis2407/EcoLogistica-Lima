#!/usr/bin/env bash
# Ejecuta la suite E2E en tandas cortas (un navegador x un archivo de pruebas) con reintentos.
# Pensado para equipos con poca memoria, donde Docker Desktop puede detenerse durante una ejecución larga.
# Cada tanda deja sus informes en src/frontend/resultados-e2e/<navegador>-<archivo>/.
#
#   bash scripts/e2e-por-tandas.sh            # todos los navegadores
#   bash scripts/e2e-por-tandas.sh firefox    # solo uno
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
COMPOSE="docker compose -f docker-compose.e2e.yml"
LOGS=src/frontend/resultados-e2e/logs
mkdir -p "$LOGS"
BITACORA="$LOGS/bitacora.log"
: > "$BITACORA"

docker_listo() { docker info > /dev/null 2>&1; }

asegurar_docker() {
  if ! docker_listo; then
    echo "[$(date +%T)] Docker detenido: iniciando Docker Desktop" | tee -a "$BITACORA"
    "$LOCALAPPDATA/Programs/DockerDesktop/Docker Desktop.exe" > /dev/null 2>&1 &
    for _ in $(seq 1 60); do docker_listo && break; sleep 5; done
  fi
  $COMPOSE up -d --build servidor > /dev/null 2>&1
}

if [ "$#" -gt 0 ]; then PROYECTOS=("$@"); else PROYECTOS=(chromium firefox webkit movil); fi

for proyecto in "${PROYECTOS[@]}"; do
  if [ "$proyecto" = "movil" ]; then ARCHIVOS=(movil); else
    ARCHIVOS=(autenticacion vehiculos pedidos roles rendimiento disponibilidad)
  fi
  for archivo in "${ARCHIVOS[@]}"; do
    for intento in 1 2 3 4; do
      asegurar_docker
      etiqueta="$proyecto-$archivo"
      $COMPOSE run --rm -e ETIQUETA="$etiqueta" e2e bash /work/scripts/e2e-contenedor.sh \
        --project="$proyecto" "e2e/$archivo.spec.ts" --reporter=line > "$LOGS/$etiqueta.log" 2>&1
      codigo=$?
      # 0 = todo pasó, 1 = hubo pruebas fallidas (resultado válido); otro código = Docker falló: reintentar.
      if [ "$codigo" -le 1 ] && grep -qaE "[0-9]+ (passed|failed)" "$LOGS/$etiqueta.log"; then
        echo "[$(date +%T)] $etiqueta: código $codigo (intento $intento)" | tee -a "$BITACORA"
        break
      fi
      echo "[$(date +%T)] $etiqueta: Docker falló (código $codigo), reintento $intento" | tee -a "$BITACORA"
    done
  done
done
echo "FIN" | tee -a "$BITACORA"
