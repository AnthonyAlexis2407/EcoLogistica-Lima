# Informe de Reducción del Impacto Ambiental y Optimización (Green IT)

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Versión del documento:** 1.0.0  
**Fecha:** 09/11/2026  
**Rama de trabajo:** `feature/green-it`

[← Volver al README Principal](../../../README.md) · [Documento 02: Estándares de ingeniería de software](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md)

---

## 1. Introducción y propósito

La eficiencia computacional influye directamente en la sostenibilidad digital (*Green IT*): cada byte que no se transfiere, cada consulta que no recorre toda una tabla y cada instrucción de JavaScript que no se ejecuta reducen la energía consumida en los centros de datos, en las redes y en los dispositivos del usuario. EcoLogística Lima tiene la sostenibilidad como pilar del producto (reducción de CO₂ en rutas de última milla), por lo que su propio software debe cumplir el mismo criterio.

Este informe documenta la auditoría, la refactorización y la medición realizadas sobre la aplicación. Su propósito es:

1. Identificar los cuellos de botella del sistema original con mediciones reproducibles.
2. Aplicar ocho optimizaciones full-stack, mostrando el código ANTES y DESPUÉS de cada una.
3. Medir el efecto con Lighthouse y con un benchmark propio de la API, y estimar la huella de carbono con el modelo Sustainable Web Design v4 (SWDM v4).
4. Verificar que la mejora no compromete la funcionalidad: la suite de pruebas pasa completa tras los cambios.

### 1.1 Adaptación al stack real del proyecto

El informe de referencia de la asignatura describe un stack MERN (MongoDB, Express, React, Node). **EcoLogística Lima no usa MERN**: su stack aprobado (Documento 10 de Inicio) es FastAPI (Python) + React + TypeScript + SQLAlchemy sobre SQLite en desarrollo y PostgreSQL en producción. Por tanto, cada una de las ocho áreas de optimización se implementó con su equivalente directo en el stack real; no se simularon tecnologías que el proyecto no tiene.

| # | Área de optimización (referencia MERN) | Equivalente aplicado en EcoLogística Lima |
|---|---|---|
| 1 | `.select()`, `.lean()` e índices en MongoDB | Columnas explícitas en SQLAlchemy (sin hidratar entidades ORM) e índices en SQLite/PostgreSQL |
| 2 | Paginación backend y frontend de 12 registros | Parámetros `page` y `limit` (12 por defecto) con cabecera `X-Total-Count` y paginador en React |
| 3 | Imágenes WebP/AVIF con `<picture>` | Auditoría de imágenes: el sistema no entrega imágenes raster; se eliminaron los recursos sin uso y se midió la conversión (ver 3.3) |
| 4 | `React.lazy` y `Suspense` | Igual: carga diferida por ruta y chunk de librerías |
| 5 | Sustituir librerías por APIs nativas | Se eliminó la fuente tipográfica externa (Google Fonts) por la pila de fuentes del sistema y se verificó que no existen `moment` ni `lodash` |
| 6 | Inlining de SVG | Favicon SVG incrustado como `data:` URI; los íconos ya son componentes SVG en línea |
| 7 | `Cache-Control`, ETag y React Query | `Cache-Control` inmutable para `/assets`, ETag con respuesta 304 en API y archivos, y revalidación |
| 8 | Compresión Brotli/Gzip en Express | `BrotliMiddleware` con respaldo Gzip en FastAPI |

---

## 2. Metodología de medición

Todas las cifras de este documento fueron **medidas**, no estimadas; se indica el comando que las reproduce.

| Aspecto | Detalle |
|---|---|
| Herramienta de rendimiento | Google Lighthouse 12.8.2, categoría `performance`, Chrome en modo sin interfaz |
| Perfil de dispositivo | Móvil (valor por defecto de Lighthouse, con red 4G simulada y CPU ralentizada) y, de forma complementaria, escritorio |
| Repeticiones | 3 corridas por escenario; se reporta la **mediana** |
| Pantalla auditada | Inicio de sesión (`/`), la única pantalla accesible sin credenciales |
| Escenario ANTES | Rama `main` en el commit `8981ee6`, compilada y servida con `vite preview` |
| Escenario DESPUÉS | Rama `feature/green-it`, compilada con `VITE_API_URL=""` y servida por FastAPI en un contenedor Docker (Python 3.12) |
| Benchmark de la API | `scripts/medir_api.py`: 1 000 vehículos y 1 000 pedidos en SQLite en memoria, llamadas en el mismo proceso, mediana de 200 repeticiones |
| Modelo de carbono | SWDM v4 con `scripts/calcular_swdm.py` |

Comandos de reproducción:

```bash
cd src/frontend && VITE_API_URL="" npm run build
PYTHONPATH=src/backend python -m uvicorn app.main:app --port 8000
npx lighthouse@12 http://localhost:8000/ --only-categories=performance --output=json
PYTHONPATH=src/backend python scripts/medir_api.py
python scripts/calcular_swdm.py
```

---

## 3. Diagnóstico inicial (estado ANTES)

La auditoría del commit `8981ee6` encontró estos problemas reales:

| Hallazgo | Evidencia |
|---|---|
| Fuente tipográfica externa que bloquea el renderizado | `@import` de Google Fonts en `index.css`: 1 hoja de estilos de terceros (1 395 B) y 1 archivo de fuente (27 301 B) |
| Favicon que apunta a un archivo inexistente | `index.html` enlazaba `/vite.svg`, pero ese archivo no estaba en `public/`: 2 peticiones inútiles (1 068 B) |
| Recursos sin uso en el repositorio | `hero.png` (13 057 B), `react.svg` (4 126 B), `vite.svg` (8 710 B), `favicon.svg` (9 522 B) e `icons.svg` (5 055 B) |
| Un solo paquete JavaScript con todas las pantallas | `index.js` de 226 263 B (70 831 B transferidos) aunque el inicio de sesión solo necesita una parte |
| Listados sin paginación efectiva | Valor por defecto de 50 filas por llamada y filtrado en el navegador |
| Respuestas sin compresión ni caché reutilizable | La API marcaba todo como `Cache-Control: no-store` y sin ETag, y el JSON viajaba sin comprimir; los archivos del frontend no tenían caché de larga duración (Lighthouse en escritorio: *Serve static assets with an efficient cache policy*, 0,5) |
| Índice ausente | `vehiculos.estado` y `pedidos.creado_en` se recorrían completos |

**Métricas de referencia (móvil, mediana de 3 corridas):**

| Indicador | Valor ANTES |
|---|---|
| Puntaje de rendimiento (Lighthouse) | **93 / 100** |
| First Contentful Paint (FCP) | 2,61 s |
| Largest Contentful Paint (LCP) | 2,61 s |
| Total Blocking Time (TBT) | 0 ms |
| Cumulative Layout Shift (CLS) | 0 |
| Peso total transferido | 105 397 B (102,9 KiB) |
| Número de peticiones HTTP | 7 |

Lighthouse marcó como fallidas las auditorías *Eliminate render-blocking resources*, *Preconnect to required origins* y *Reduce unused JavaScript*.

---

## 4. Detalle técnico de las 8 optimizaciones

### 4.1 Optimización 1: consultas magras e índices (WSG 3.16)

**Diagnóstico.** Los listados consultaban la entidad ORM completa y dos columnas de uso frecuente no tenían índice.

**Implementación.** Los listados seleccionan solo las columnas que expone el esquema de salida y devuelven filas planas, sin hidratar entidades ORM (equivalente a `.select()` más `.lean()` de Mongoose). Se agregaron los índices `idx_vehiculos_estado` e `idx_pedidos_creado_en`.

ANTES (`vehiculos_router.py`):

```python
query = select(Vehiculo)
if estado:
    query = query.where(Vehiculo.estado == estado.upper())
query = query.offset(skip).limit(limit)
result = await db.execute(query)
return result.scalars().all()
```

DESPUÉS:

```python
_COLUMNAS = (
    Vehiculo.vehiculo_id, Vehiculo.placa, Vehiculo.capacidad_kg,
    Vehiculo.tipo_combustible, Vehiculo.factor_emision_co2, Vehiculo.estado,
)

filas = await db.execute(
    select(*_COLUMNAS).where(*filtros).order_by(Vehiculo.placa)
    .offset((page - 1) * limit).limit(limit)
)
return [dict(fila) for fila in filas.mappings()]
```

ANTES (`models.py`): sin índice en `estado`. DESPUÉS:

```python
__table_args__ = (Index("idx_vehiculos_estado", "estado"),)
```

**Evidencia (`EXPLAIN QUERY PLAN` de SQLite):**

| Consulta | Sin índice | Con índice |
|---|---|---|
| `vehiculos WHERE estado = ?` | `SCAN vehiculos` | `SEARCH vehiculos USING INDEX idx_vehiculos_estado (estado=?)` |
| `pedidos ORDER BY creado_en DESC LIMIT 12` | `SCAN pedidos` + `USE TEMP B-TREE FOR ORDER BY` | `SCAN pedidos USING INDEX idx_pedidos_creado_en` (sin ordenación temporal) |

**Resultado medido y limitación.** En el benchmark con 1 000 filas el tiempo de servidor **no cambió de forma apreciable** (vehículos: 5,50 ms a 5,74 ms; pedidos: 7,13 ms a 6,49 ms, dentro del ruido de la medición). El beneficio de esta optimización está en la escalabilidad (el plan de consulta pasa de recorrer toda la tabla a buscar por índice) y en la menor memoria por no crear entidades; no se afirma una mejora de tiempo a este volumen.

### 4.2 Optimización 2: paginación en backend y frontend (WSG 4.3)

**Diagnóstico.** El listado devolvía hasta 50 filas por llamada y el navegador filtraba el resultado. La búsqueda solo alcanzaba lo ya descargado.

**Implementación.** El backend recibe `page` (mínimo 1), `limit` (12 por defecto, máximo 50), `estado` y `q`; informa el total en la cabecera `X-Total-Count`. El frontend pide páginas de 12, muestra un paginador y envía la búsqueda al servidor con un retraso de 300 ms (`useDebounced`) para no consultar por cada tecla.

ANTES (backend):

```python
skip: int = Query(0, ge=0),
limit: int = Query(50, ge=1, le=100),
```

DESPUÉS (backend):

```python
page: int = Query(1, ge=1),
limit: int = Query(12, ge=1, le=50),
...
response.headers["X-Total-Count"] = str(total or 0)
```

ANTES (frontend, `VehiculosPage.tsx`):

```tsx
const data = await vehiculosApi.list(token);
setVehiculos(data);
...
const filtered = vehiculos.filter((v) => v.placa.toLowerCase().includes(searchTerm.toLowerCase()) /* ... */);
```

DESPUÉS (frontend):

```tsx
const data = await vehiculosApi.listPage(token, {
  estado: statusFilter || undefined, q: busqueda || undefined, page, limit: PAGE_SIZE,
});
setVehiculos(data.items);
setTotal(data.total);
...
<Paginador page={page} total={total} pageSize={PAGE_SIZE} onChange={setPage} />
```

**Evidencia (bytes por llamada, con compresión):**

| Listado | ANTES (50 filas) | DESPUÉS (página de 12) | Reducción |
|---|---|---|---|
| Vehículos | 8 601 B | 446 B | 94,8 % |
| Pedidos | 18 001 B | 555 B | 96,9 % |

Pruebas: `test_listado_de_vehiculos_pagina_de_12_y_informa_el_total`, `test_listado_de_pedidos_pagina_busca_y_conserva_el_aislamiento_por_bodega` y las de `Paginador`, `VehiculosPage` y `PedidosPage`.

### 4.3 Optimización 3: imágenes WebP/AVIF con `<picture>` (WSG 2.9)

**Diagnóstico.** La interfaz **no muestra ninguna imagen raster**: los íconos son SVG en línea y el banner del Dashboard se dibuja con CSS. El único PNG del repositorio, `hero.png` (13 057 B), venía de la plantilla de Vite y no se usaba. Por tanto, no existe una imagen que convertir en producción.

**Implementación.** La acción correcta fue **no enviar bytes que nadie ve**: se eliminaron `hero.png`, `react.svg`, `vite.svg`, `favicon.svg` e `icons.svg` (40 470 B en total; 14 577 B de ellos se copiaban a `dist/`). Para no dejar la regla sin respaldo, se midió la conversión del PNG con Pillow 11:

| Formato | Tamaño | Variación frente al PNG |
|---|---|---|
| PNG original (343 × 361 px, con transparencia) | 13 057 B | — |
| WebP (calidad 80) | 13 680 B | **+4,8 % (más pesado)** |
| AVIF (calidad 50) | 10 335 B | −20,8 % |

La medición muestra que convertir **no siempre reduce**: para una ilustración pequeña con transparencia, WebP resultó más pesado y solo AVIF ahorró. Por eso la regla del Documento 02 exige medir cada conversión antes de adoptarla.

Cuando el producto incorpore imágenes (por ejemplo, una fotografía de evidencia de entrega), el patrón estándar es:

```tsx
<picture>
  <source srcSet="/img/evidencia-600.avif 600w, /img/evidencia-1200.avif 1200w" type="image/avif" />
  <source srcSet="/img/evidencia-600.webp 600w, /img/evidencia-1200.webp 1200w" type="image/webp" />
  <img src="/img/evidencia-1200.jpg" alt="Evidencia de entrega" width="1200" height="800"
       loading="lazy" decoding="async" />
</picture>
```

No se agregó un componente genérico `<OptimizedPicture>` sin uso, para respetar el principio YAGNI (Documento 02). **Esta área queda aplicada como auditoría y depuración, no como conversión en producción.**

### 4.4 Optimización 4: carga diferida y *code splitting* (WSG 3.7 y 3.3)

**Diagnóstico.** Las cuatro pantallas viajaban en un solo `index.js` de 226 263 B (70 831 B transferidos), aunque el inicio de sesión no usa Dashboard, Vehículos ni Pedidos. Lighthouse marcaba *Reduce unused JavaScript*.

ANTES (`App.tsx`):

```tsx
import DashboardPage from './pages/DashboardPage';
import VehiculosPage from './pages/VehiculosPage';
import PedidosPage from './pages/PedidosPage';
```

DESPUÉS:

```tsx
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const VehiculosPage = lazy(() => import('./pages/VehiculosPage'));
const PedidosPage = lazy(() => import('./pages/PedidosPage'));
...
<Suspense fallback={<div className="loading-spinner"><div className="spinner" /></div>}>
  <Routes>{/* rutas */}</Routes>
</Suspense>
```

Además, `vite.config.ts` separa `react`, `react-dom` y `react-router-dom` en un chunk `vendor`, que cambia poco entre versiones y se conserva en caché.

**Evidencia (salida de `vite build`, tamaño sin comprimir / comprimido):**

| Archivo | Tamaño | Gzip |
|---|---|---|
| `index` (entrada) | 16,54 kB | 6,02 kB |
| `vendor` | 180,64 kB | 59,47 kB |
| `DashboardPage` | 10,40 kB | 3,01 kB |
| `VehiculosPage` | 10,43 kB | 3,54 kB |
| `PedidosPage` | 9,96 kB | 3,33 kB |
| `Paginador` | 2,16 kB | 0,93 kB |

### 4.5 Optimización 5: dependencias y recursos de terceros (WSG 3.12, 3.5 y 2.11)

**Diagnóstico.** La dependencia de terceros más costosa no era una librería npm sino la **fuente tipográfica externa**: obligaba a abrir conexiones a dos dominios ajenos y bloqueaba el primer renderizado. Además se verificó que el proyecto no usa `moment` ni `lodash` (las fechas y números ya usan `Intl` mediante `toLocaleString('es-PE')`) y que solo declara 4 dependencias de producción (`react`, `react-dom`, `react-router-dom`, `lucide-react`).

ANTES (`index.css`):

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
--font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
```

DESPUÉS:

```css
--font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
```

**Evidencia.** Se eliminaron 2 peticiones a dominios de terceros y 28 696 B de fuente y hoja de estilos; desapareció la auditoría *Preconnect to required origins*. Costo: la tipografía visual cambia a la del sistema operativo del usuario.

### 4.6 Optimización 6: reducción de peticiones HTTP e *inlining* de SVG (WSG 4.3)

**Diagnóstico.** El favicon apuntaba a `/vite.svg`, un archivo inexistente: el servidor respondía con el `index.html` de reserva, y el navegador hacía dos peticiones inútiles.

ANTES (`index.html`):

```html
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
```

DESPUÉS:

```html
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E...%3C/svg%3E" />
<meta name="theme-color" content="#047857" />
```

Los íconos de la interfaz (`lucide-react`) ya son componentes SVG en línea: no generan peticiones. **Resultado medido: de 7 a 4 peticiones en la carga inicial** (documento, script de entrada, chunk `vendor` y hoja de estilos).

### 4.7 Optimización 7: estrategia de caché (WSG 4.2)

**Diagnóstico.** La API marcaba todas sus respuestas con `Cache-Control: no-store` (una cabecera de seguridad aplicada por igual a datos y sesión), así que ningún dato podía reutilizarse ni revalidarse, y el frontend no tenía caché de larga duración: el navegador volvía a descargar todo en cada visita.

**Implementación (`app/rendimiento.py`).**

| Recurso | Política | Efecto |
|---|---|---|
| `/assets/*` (nombres con hash) | `public, max-age=31536000, immutable` | Visita de retorno: 0 bytes |
| `index.html` | `no-cache` + ETag | Revalida; responde 304 sin cuerpo |
| `GET /api/*` (datos) | `private, no-cache` + ETag | Revalida; responde 304 sin cuerpo si no hay cambios |
| `/api/auth/*` y `/api/health` | `no-store` | La sesión y el estado vivo nunca se guardan |

ANTES (`main.py`): una sola cabecera fija para toda respuesta.

```python
response.headers["Cache-Control"] = "no-store"
```

DESPUÉS (`rendimiento.py`):

```python
etag = '"' + hashlib.sha256(cuerpo).hexdigest()[:32] + '"'
cabeceras["ETag"] = etag
cabeceras["Cache-Control"] = "private, no-cache"
if _coincide_etag(request.headers.get("if-none-match"), etag):
    return _con_seguridad(Response(status_code=304, headers=sin_cuerpo))
```

**Evidencia medida.** Revalidar `index.html` con el ETag devuelve 304 con **534 B** de cabeceras y sin cuerpo (frente a 1 110 B de la primera carga); los archivos de `/assets` no se vuelven a pedir. Pruebas: `test_get_de_la_api_lleva_etag_y_responde_304_si_no_cambio`, `test_frontend_revalida_con_304_cuando_el_archivo_no_cambio` y `test_frontend_assets_con_cache_inmutable_e_index_con_revalidacion`.

**Equivalencia con React Query.** El proyecto no incorpora TanStack Query: sumaría una dependencia de unos 13 kB para un beneficio que el caché HTTP con ETag ya entrega (WSG 3.12, usar pocas dependencias).

### 4.8 Optimización 8: compresión Brotli y Gzip (WSG 4.3)

**Diagnóstico.** El JSON y los archivos viajaban sin comprimir.

ANTES (`main.py`): sin middleware de compresión. DESPUÉS:

```python
from brotli_asgi import BrotliMiddleware

app.middleware("http")(politica_http)
app.add_middleware(BrotliMiddleware, quality=5, minimum_size=1000, gzip_fallback=True)
```

**Evidencia medida (benchmark de la API, bytes por la red):**

| Respuesta | Sin comprimir | Con Brotli | Reducción | Costo en servidor (mediana) |
|---|---|---|---|---|
| Vehículos (50 filas) | 8 601 B | 1 372 B | 84,0 % | 5,74 ms a 6,27 ms |
| Pedidos (50 filas) | 18 001 B | 1 609 B | 91,1 % | 6,49 ms a 6,68 ms |
| Carga inicial del frontend (mismo build) | 70 981 B (gzip de `vite preview`) | 68 867 B | 3,0 % | no medido por separado |

La compresión suma entre 0,2 y 0,5 ms de CPU por respuesta de 1 KB o más; se aplica solo a cuerpos de 1 000 B o más. Prueba: `test_respuestas_grandes_se_comprimen_con_gzip_o_brotli`.

---

## 5. Comparación de métricas ANTES y DESPUÉS

Móvil (perfil por defecto de Lighthouse), mediana de 3 corridas:

| Métrica | ANTES | Frontend optimizado (servido con `vite preview`) | DESPUÉS (frontend + API con Brotli, en Docker) | Variación ANTES a DESPUÉS |
|---|---|---|---|---|
| Puntaje de rendimiento | 93 | 100 | **100** | +7 puntos |
| FCP | 2,613 s | 1,365 s | **1,455 s** | −1,158 s (−44,3 %) |
| LCP | 2,613 s | 1,365 s | **1,455 s** | −1,158 s (−44,3 %) |
| TBT | 0 ms | 0 ms | **0 ms** | sin cambio |
| CLS | 0 | 0 | **0** | sin cambio |
| Peso transferido | 105 397 B | 70 981 B | **68 867 B** | −36 530 B (−34,7 %) |
| Peticiones HTTP | 7 | 4 | **4** | −3 (−42,9 %) |

Escritorio (perfil complementario):

| Métrica | ANTES | DESPUÉS |
|---|---|---|
| Puntaje de rendimiento | 100 (corridas: 98, 100, 100) | 100 |
| FCP / LCP | 0,540 s | 0,466 s |
| Peso transferido | 106 836 B | 68 867 B |
| Peticiones HTTP | 7 | 4 |

### 5.1 Lectura honesta de los resultados

- **Lo que sí se logró:** el puntaje sube de 93 a 100; el tiempo hasta el primer contenido baja 44 % en móvil; el peso baja 34,7 % y las peticiones de 7 a 4. Las mejoras de la aplicación (sin fuente externa, favicon incrustado, *code splitting*) explican casi todo: el frontend servido con `vite preview` ya alcanza 1,365 s.
- **El servidor de FastAPI no añade velocidad en la carga inicial:** con la API en Docker el FCP fue 1,455 s, 0,09 s peor que con `vite preview` directo. Atribuimos esa diferencia al entorno (contenedor con carpeta montada desde Windows) y a la compresión dinámica, pero no la aislamos con una medición adicional. Su aporte real es la reducción de bytes (−2 114 B) y la caché de visitas posteriores.
- **Umbrales de referencia de la rúbrica:** puntaje ≥ 90, TBT ≤ 85 ms, CLS ≤ 0,02 y peso ≤ 1,1 MB **se cumplen** (TBT 0 ms, CLS 0, peso 0,07 MB). **FCP ≤ 1,0 s y LCP ≤ 1,4 s se cumplen en escritorio (0,47 s) pero no en móvil con red 4G simulada (1,46 s)**. En el flujo de CI (`lighthouserc.json`) esos dos límites están como advertencia por esta razón.
- **Los valores absolutos no son comparables con los del informe de referencia** (peso de 8,4 MB y puntaje 38): ese informe describe otra aplicación. Nuestro punto de partida ya era liviano (105 KB); la mejora relativa es la que corresponde a esta aplicación.

---

## 6. Análisis de impacto ambiental con SWDM v4

### 6.1 Modelo y constantes

El Sustainable Web Design Model v4 estima las emisiones de una transferencia de datos así:

```
Energía (kWh)    = Datos (GB) × Σ intensidad energética de los 3 segmentos (kWh/GB)
Emisiones (g)    = Energía (kWh) × Intensidad de la red eléctrica (g CO₂e/kWh)
```

| Segmento | Operación (kWh/GB) | Fabricación del equipo (kWh/GB) | Total (kWh/GB) |
|---|---|---|---|
| Centros de datos | 0,055 | 0,012 | 0,067 |
| Redes | 0,059 | 0,013 | 0,072 |
| Dispositivos del usuario | 0,080 | 0,081 | 0,161 |
| **Suma** | 0,194 | 0,106 | **0,300** |

Intensidad de la red eléctrica por defecto de SWDM v4: **494 g CO₂e/kWh** (promedio mundial, Ember). Emisiones por GB: 0,300 × 494 = **148,2 g CO₂e/GB**. Se usa 1 GB = 10⁹ bytes. Fuente: [Sustainable Web Design, *Estimating digital emissions*](https://sustainablewebdesign.org/estimating-digital-emissions/).

**Corrección respecto al informe de referencia.** La fórmula de esa plantilla usa 0,815 kWh/GB y 442 g/kWh, valores de la versión 3 del modelo, y sus resultados no son consistentes con su propia fórmula (por ejemplo, 8,4 MB por 0,815 por 442 da 2,96 g y no 2,15 g). Este informe aplica las constantes de la versión 4 y reproduce cada cálculo en `scripts/calcular_swdm.py`.

### 6.2 Cálculo por carga inicial de la aplicación

**ANTES: 105 397 B**

- Datos: 105 397 / 10⁹ = 0,000105397 GB
- Energía: 0,000105397 × 0,300 = 3,162 × 10⁻⁵ kWh (31,62 mWh)
- Emisiones: 3,162 × 10⁻⁵ × 494 = 0,015620 g = **15,62 mg CO₂e por carga**

**DESPUÉS: 68 867 B**

- Datos: 68 867 / 10⁹ = 0,000068867 GB
- Energía: 0,000068867 × 0,300 = 2,066 × 10⁻⁵ kWh (20,66 mWh)
- Emisiones: 2,066 × 10⁻⁵ × 494 = 0,010206 g = **10,21 mg CO₂e por carga**

Reducción: 15,62 − 10,21 = 5,41 mg por carga (**−34,7 %**, igual a la reducción de bytes porque el modelo es lineal en los datos).

Reparto de la carga DESPUÉS por segmento: centros de datos 2,28 mg, redes 2,45 mg y dispositivos del usuario 5,48 mg. El dispositivo es el segmento mayor (53,7 %), por lo que reducir el JavaScript ejecutado también importa.

### 6.3 Cálculo por llamada a la API

| Listado | Bytes ANTES | Bytes DESPUÉS | mg CO₂e ANTES | mg CO₂e DESPUÉS |
|---|---|---|---|---|
| Vehículos | 8 601 | 446 | 1,275 | 0,066 |
| Pedidos | 18 001 | 555 | 2,668 | 0,082 |

### 6.4 Proyección anual (supuesto explícito)

El sistema es de uso interno de DistriRápido y aún no tiene tráfico real, por lo que el volumen es un **supuesto ilustrativo**, no una medición: 50 usuarios × 250 días hábiles × 4 cargas iniciales al día = **50 000 cargas al año**. Se muestra también 500 000 para comparar con el informe de referencia.

| Cargas iniciales al año | Emisiones ANTES | Emisiones DESPUÉS | Ahorro anual |
|---|---|---|---|
| 50 000 | 0,781 kg CO₂e | 0,510 kg CO₂e | **0,271 kg CO₂e** |
| 500 000 | 7,810 kg CO₂e | 5,103 kg CO₂e | **2,707 kg CO₂e** |

Estas cifras son **modestas** porque la aplicación ya es liviana; el informe de referencia proyecta 935 kg al año porque parte de una página de 8,4 MB. El mayor ahorro se espera cuando crezca el volumen de datos: la paginación de 12 filas evita transferir el 95 % al 97 % de cada listado, y esa proporción se mantiene cuando las tablas tengan miles de registros.

---

## 7. Evidencias de validación

| Evidencia | Resultado |
|---|---|
| Pruebas del backend (Python 3.12, Docker) | **51 pasan**; cobertura 88 % (incluye `seed.py`, que no se prueba) |
| Pruebas del frontend (Vitest) | **69 pasan**; cobertura de líneas 94,95 % |
| Verificación de tipos (`tsc`) | Sin errores |
| Vulnerabilidades en dependencias (`npm audit`) | 0 |
| Flujo CI en GitHub Actions (`ci.yml`) | En verde en la rama `feature/green-it` |
| Flujo `green-audit.yml` con Lighthouse CI | En verde: el puntaje ≥ 0,9, el TBT ≤ 85 ms, el CLS ≤ 0,02 y el peso ≤ 1,1 MB pasaron como errores bloqueantes (ejecución 42620547976) |
| Benchmark de la API | `scripts/medir_api.py` (resultados en la sección 4) |
| Cálculo de carbono | `scripts/calcular_swdm.py` (resultados en la sección 6) |

---

## 8. Limitaciones

1. **Solo se auditó la pantalla de inicio de sesión.** Dashboard, Vehículos y Pedidos requieren credenciales; sus listados se evaluaron con el benchmark de la API, no con Lighthouse.
2. **Servidores distintos entre ANTES y DESPUÉS** (`vite preview` y FastAPI en Docker); por eso se incluye la columna intermedia que aísla el efecto del frontend.
3. **El benchmark de la API se ejecuta en el mismo proceso, con SQLite en memoria**: mide serialización y compresión, no la red ni PostgreSQL. Con 1 000 filas no demuestra mejora de tiempo en las consultas.
4. **La conversión de imágenes se midió con un solo archivo** (la ilustración de plantilla); no generaliza a fotografías.
5. **La intensidad eléctrica de 494 g/kWh es el promedio mundial**; la del Perú es distinta y no se usó por no contar con una fuente verificada en esta auditoría.
6. **Lighthouse varía entre corridas** (una corrida de escritorio ANTES dio 98 puntos); se reporta la mediana de 3.

---

## 9. Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 09/11/2026 | Primer informe Green IT: ocho optimizaciones con código ANTES y DESPUÉS, mediciones con Lighthouse y benchmark propio, y cálculo SWDM v4. |
