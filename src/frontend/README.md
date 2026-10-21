# Frontend — EcoLogística Lima

Panel web de EcoLogística Lima, construido con **React 18, TypeScript y Vite 6**, con React Router 7 y CSS propio (`src/index.css`).

## Estado al 05/10/2026

| Ruta | Pantalla | Historia | Estado |
|---|---|---|---|
| `/login` | Inicio de sesión (JWT) | EN-002 | Funcional |
| `/` | Inicio: conteos de vehículos y pedidos por estado | - | Funcional; la tarjeta "Impacto CO₂" es un marcador sin datos |
| `/vehiculos` | Gestión de flota | US-001 | Funcional |
| `/pedidos` | Registro y consulta de pedidos | US-003 | Funcional; la ubicación se captura como latitud/longitud (sin mapa) |

Las rutas están protegidas por sesión. Aún no hay mapa, rutas optimizadas, dashboard ambiental, reportes ni app del conductor (EP-03 a EP-05).

> El bloque "Resumen del Sprint 1" del inicio es texto fijo; no es evidencia de aceptación. El estado verificado de cada historia está en `docs/03 Implementación`.

## Cómo correrlo

```bash
cd src/frontend
npm ci
npm run dev        # http://localhost:5173
npm run build      # compilación de producción (carpeta dist/, ignorada por Git)
```

El backend debe estar corriendo (`src/backend`). Si no usa `http://localhost:8000`, crear un archivo `.env` (ignorado por Git) con:

```
VITE_API_URL=http://localhost:8000
```

## Estructura

```
src/
├── main.tsx            # Punto de entrada
├── App.tsx             # Rutas, ruta protegida y barra lateral
├── AuthContext.tsx     # Sesión y token
├── api.ts              # Cliente HTTP hacia la API (auth, vehículos, pedidos)
├── index.css           # Estilos
└── pages/              # LoginPage, DashboardPage, VehiculosPage, PedidosPage
```

## Pendientes

- Script de lint: existe `eslint.config.js`, pero falta el script en `package.json` y las dependencias de ESLint.
- Pruebas del frontend y ejecución en CI (ver IMP-009 del Registro de Impedimentos).
