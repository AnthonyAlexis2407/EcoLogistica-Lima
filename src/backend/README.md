# Backend — EcoLogística Lima API

API REST construida con **FastAPI** (Python 3.12+) + **SQLAlchemy** asíncrono.

## Stack

| Componente | Tecnología |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async) |
| BD (desarrollo) | SQLite + aiosqlite |
| BD (producción) | PostgreSQL 16 + PostGIS |
| Auth | JWT (python-jose) + bcrypt (passlib) |

## Instalación

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
# Sembrar datos de prueba
python -m app.seed

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --port 8000
```

## Documentación de la API

Con el servidor corriendo, acceder a:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Credenciales de prueba (seed)

| Rol | Email | Contraseña |
|---|---|---|
| ADMIN_FLOTA | admin@ecologistica.pe | Admin2026! |
| OPERADOR | operador@ecologistica.pe | Operador2026! |
| BODEGA | bodega@tienda.pe | Bodega2026! |

## Estructura

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Punto de entrada FastAPI
│   ├── config.py          # Configuración (pydantic-settings)
│   ├── database.py        # Motor SQLAlchemy async
│   ├── models.py          # Modelos ORM
│   ├── schemas.py         # Schemas Pydantic (validación)
│   ├── auth.py            # JWT + bcrypt + RBAC + lockout
│   ├── seed.py            # Datos semilla
│   ├── consultas.py       # Patrón LIKE seguro para las búsquedas
│   ├── rendimiento.py     # ETag, caché, cabeceras de seguridad y servicio del frontend compilado
│   └── routers/
│       ├── auth_router.py      # /api/auth/*
│       ├── vehiculos_router.py # /api/vehiculos/*
│       └── pedidos_router.py   # /api/pedidos/*
└── requirements.txt
```

## Listados paginados

`GET /api/vehiculos/` y `GET /api/pedidos/` devuelven **12 registros por página** (parámetros `page`, `limit` hasta 50, `estado` y `q` para buscar por placa/combustible o por dirección). El total viaja en la cabecera `X-Total-Count`. Las respuestas de datos llevan `ETag` y `Cache-Control: private, no-cache` (el cliente recibe 304 si no cambiaron) y se comprimen con Brotli o Gzip desde 1 KB.

## Servir el frontend desde la API

Si existe `src/frontend/dist` (compilado con `VITE_API_URL=""`), la API lo sirve en `/` con caché inmutable para `/assets` y `index.html` con revalidación y `Content-Security-Policy`. La ruta se cambia con la variable `FRONTEND_DIST`. Con `ENVIRONMENT=production` se exige una `SECRET_KEY` propia y se oculta `/docs`.

## Endpoints Sprint 1

| Método | Ruta | Descripción | Historia |
|---|---|---|---|
| POST | /api/auth/register | Registrar usuario (público solo con rol BODEGA; otros roles requieren un ADMIN_FLOTA autenticado) | EN-002 |
| POST | /api/auth/login | Login con JWT | EN-002 |
| GET | /api/auth/me | Perfil actual | EN-002 |
| GET | /api/vehiculos/ | Listar vehículos | US-001 |
| POST | /api/vehiculos/ | Registrar vehículo | US-001 |
| PUT | /api/vehiculos/{id} | Actualizar vehículo | US-001 |
| DELETE | /api/vehiculos/{id} | Baja lógica | US-001 |
| GET | /api/pedidos/ | Listar pedidos | US-003 |
| POST | /api/pedidos/ | Registrar pedido | US-003 |
| PUT | /api/pedidos/{id} | Actualizar pedido | US-003 |
| DELETE | /api/pedidos/{id} | Cancelar pedido | US-003 |
## Pruebas

```bash
PYTHONPATH=src/backend python -m pytest src/backend/tests -q --cov=src/backend/app    # 51 pasan; cobertura 88 % (09/11/2026)
```

- `tests/test_api.py`: pruebas de integración básicas (usan una sesión de base de datos compartida).
- `tests/test_rendimiento.py`: paginación de 12, ETag y 304, compresión Brotli/Gzip, caché del frontend y servicio de archivos.
- `tests/test_criterios_aceptacion.py`: escenarios de aceptación con la dependencia `get_db` real y los roles del seed (ADMIN_FLOTA, OPERADOR, BODEGA): US-001, US-003, EN-002 y RN-010.
- Incluye pruebas de regresión de los defectos corregidos en el Sprint 2: **DEF-001** (el bloqueo de cuenta no persistía), **DEF-002** (una BODEGA registraba pedidos para otra bodega) y **DEF-003** (el registro público permitía autoasignarse un rol de administración).

El estado por historia y los impedimentos están en `docs/03 Implementación`.
