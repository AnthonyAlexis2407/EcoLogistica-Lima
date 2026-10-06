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
│   └── routers/
│       ├── auth_router.py      # /api/auth/*
│       ├── vehiculos_router.py # /api/vehiculos/*
│       └── pedidos_router.py   # /api/pedidos/*
└── requirements.txt
```

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
python -m pytest -q --cov=app    # 16 passed; cobertura 67 % (05/10/2026)
```

- `tests/test_api.py`: pruebas de integración básicas (usan una sesión de base de datos compartida).
- `tests/test_criterios_aceptacion.py`: escenarios de aceptación con la dependencia `get_db` real y los roles del seed (ADMIN_FLOTA, OPERADOR, BODEGA): US-001, US-003, EN-002 y RN-010.
- Incluye pruebas de regresión de los defectos corregidos en el Sprint 2: **DEF-001** (el bloqueo de cuenta no persistía), **DEF-002** (una BODEGA registraba pedidos para otra bodega) y **DEF-003** (el registro público permitía autoasignarse un rol de administración).

El estado por historia y los impedimentos están en `docs/03 Implementación`.
