"""
Política HTTP de rendimiento y sostenibilidad (Informe Green IT).

- ETag y Cache-Control en los GET de la API: el cliente revalida y recibe 304 sin cuerpo cuando
  los datos no cambiaron (WSG 4.2).
- Archivos del frontend compilado con caché inmutable para /assets (nombres con hash) y
  revalidación para index.html (WSG 4.2).
- Cabeceras de seguridad en cada respuesta (OWASP A02).

La compresión Brotli/Gzip (WSG 4.3) se agrega en main.py con BrotliMiddleware.
"""

import hashlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}

# La API solo se carga desde el mismo origen; img-src data: permite el favicon incrustado.
CSP_FRONTEND = (
    "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; connect-src 'self'; frame-ancestors 'none'"
)

CACHE_INMUTABLE = "public, max-age=31536000, immutable"
CACHE_REVALIDAR = "no-cache"

# Rutas de la API cuyo contenido no se guarda ni se revalida (sesión) o que informan estado vivo.
_SIN_ETAG = ("/api/auth", "/api/health")


def _normalizar_etag(valor: str) -> str:
    return valor.strip().removeprefix("W/")


def _coincide_etag(cabecera: str | None, etag: str) -> bool:
    if not cabecera:
        return False
    return any(_normalizar_etag(parte) == etag for parte in cabecera.split(","))


def _con_seguridad(response: Response) -> Response:
    for nombre, valor in CABECERAS_SEGURIDAD.items():
        response.headers.setdefault(nombre, valor)
    return response


async def politica_http(request: Request, call_next):
    """Middleware: cabeceras de seguridad y ETag/Cache-Control para los GET de la API."""
    response = await call_next(request)
    if "cache-control" in response.headers:  # ya lo fijó la ruta (archivos estáticos)
        return _con_seguridad(response)

    ruta = request.url.path
    es_lectura_api = (
        request.method == "GET"
        and ruta.startswith("/api/")
        and not ruta.startswith(_SIN_ETAG)
        and response.status_code == 200
    )
    if not es_lectura_api:
        response.headers["Cache-Control"] = "no-store"
        return _con_seguridad(response)

    cuerpo = b"".join([trozo async for trozo in response.body_iterator])
    etag = '"' + hashlib.sha256(cuerpo).hexdigest()[:32] + '"'
    cabeceras = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
    cabeceras["ETag"] = etag
    cabeceras["Cache-Control"] = "private, no-cache"
    if _coincide_etag(request.headers.get("if-none-match"), etag):
        # El 304 conserva las cabeceras (incluidas las de CORS) pero no lleva cuerpo ni su tipo.
        sin_cuerpo = {k: v for k, v in cabeceras.items() if k.lower() not in ("content-type", "content-length")}
        return _con_seguridad(Response(status_code=304, headers=sin_cuerpo))
    return _con_seguridad(Response(content=cuerpo, status_code=response.status_code, headers=cabeceras))


def montar_frontend(app: FastAPI, dist: Path) -> bool:
    """
    Sirve el frontend compilado (Vite) desde la misma API; devuelve False si no existe `dist`.

    Se atiende en el manejador del 404 y no con una ruta comodín: una ruta `/{ruta:path}` hace
    que FastAPI deje de redirigir `/api/vehiculos` a `/api/vehiculos/` (respondería 405).
    """
    raiz = dist.resolve()
    indice = raiz / "index.html"
    if not indice.is_file():
        return False

    async def manejar_404(request: Request, exc: StarletteHTTPException):
        ruta = request.url.path.lstrip("/")
        if request.method not in ("GET", "HEAD") or ruta == "api" or ruta.startswith("api/"):
            return await http_exception_handler(request, exc)
        candidato = (raiz / ruta).resolve()
        if ruta and candidato.is_file() and raiz in candidato.parents:
            cache = CACHE_INMUTABLE if ruta.startswith("assets/") else CACHE_REVALIDAR
            return FileResponse(candidato, headers={"Cache-Control": cache})
        # Rutas de la SPA (React Router): se entrega index.html.
        return FileResponse(indice, headers={
            "Cache-Control": CACHE_REVALIDAR,
            "Content-Security-Policy": CSP_FRONTEND,
        })

    app.add_exception_handler(404, manejar_404)
    return True
