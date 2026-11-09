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
| 3 | Imágenes WebP/AVIF con `<picture>` | Ilustración del Dashboard con `<picture>`: AVIF y WebP adaptativos (280 y 560 px) y PNG de respaldo |
| 4 | `React.lazy` y `Suspense` | Igual, más arranque de la aplicación tras el primer pintado |
| 5 | Sustituir librerías por APIs nativas | Se eliminó la fuente tipográfica externa (Google Fonts) por la pila de fuentes del sistema y se verificó que no existen `moment` ni `lodash` |
| 6 | Inlining de SVG | Favicon SVG y hoja de estilos incrustados en el HTML; los íconos ya son componentes SVG en línea |
| 7 | `Cache-Control`, ETag y React Query | `Cache-Control` inmutable para `/assets`, ETag con respuesta 304 en API y archivos, y revalidación |
| 8 | Compresión Brotli/Gzip en Express | `BrotliMiddleware` con respaldo Gzip en FastAPI |

---

## 2. Metodología de medición

Todas las cifras de este documento fueron **medidas**, no estimadas; se indica el comando que las reproduce.

| Aspecto | Detalle |
|---|---|
| Herramienta de rendimiento | Google Lighthouse 12.8.2, categoría `performance`, HeadlessChrome 156 |
| Perfil móvil (por defecto de Lighthouse) | Red 4G simulada (RTT 150 ms, 1 638 kbps de bajada) y CPU 4 veces más lenta |
| Perfil de escritorio (complementario) | Preset `desktop` de Lighthouse |
| Repeticiones | 3 corridas por escenario intermedio y **8 corridas en el escenario final**; se reporta la **mediana** y el rango |
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
python scripts/generar_ilustracion_hero.py
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
| Sin imágenes optimizadas | El banner del Dashboard no tenía ninguna imagen; el único PNG del repositorio era de la plantilla de Vite y no se usaba |

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

### 4.3 Optimización 3: imágenes AVIF y WebP con `<picture>` (WSG 2.9)

**Diagnóstico.** La interfaz no mostraba ninguna imagen: el banner del Dashboard se dibujaba solo con CSS, y el único PNG del repositorio (`hero.png`, 13 057 B) venía de la plantilla de Vite y no se usaba. Una prueba previa con ese PNG mostró que convertir **no siempre reduce**: su versión WebP pesó 13 680 B (+4,8 %) y solo AVIF ahorró (10 335 B, −20,8 %). Por eso cada conversión se mide antes de adoptarla.

**Implementación.** Se incorporó una ilustración decorativa al banner del Dashboard (una ruta de entrega con una hoja, el tema del proyecto). La genera `scripts/generar_ilustracion_hero.py`, que la exporta en dos anchos (280 px para pantallas normales y 560 px para las de alta densidad) y tres formatos, e imprime la tabla de pesos. Se eliminaron además los cinco recursos sin uso (40 470 B). Para usar otra imagen de marca basta cambiar la función `dibujar()` por la carga del archivo; el resto del proceso es el mismo.

ANTES (`DashboardPage.tsx`): sin imagen.

```tsx
<div className="hero-banner">
  <div className="hero-text">{/* ... */}</div>
  <div>{/* botones */}</div>
</div>
```

DESPUÉS:

```tsx
<picture className="hero-ilustracion">
  <source type="image/avif" srcSet="/img/hero-rutas-280.avif 280w, /img/hero-rutas-560.avif 560w" sizes="280px" />
  <source type="image/webp" srcSet="/img/hero-rutas-280.webp 280w, /img/hero-rutas-560.webp 560w" sizes="280px" />
  <img src="/img/hero-rutas-560.png" width="280" height="160" alt="" loading="lazy" decoding="async" />
</picture>
```

La imagen es decorativa, por lo que lleva `alt=""` (WCAG 1.1.1); declara `width` y `height` para evitar saltos de diseño (CLS), se carga de forma diferida y solo se oculta en pantallas de menos de 1 100 px.

**Evidencia (pesos medidos de cada variante):**

| Ancho | PNG (respaldo) | WebP | Reducción WebP | AVIF | Reducción AVIF |
|---|---|---|---|---|---|
| 280 px | 17 393 B | 7 988 B | 54,1 % | 3 913 B | 77,5 % |
| 560 px | 39 905 B | 15 164 B | 62,0 % | 7 958 B | **80,1 %** |

En Chrome, la variante elegida fue `hero-rutas-560.avif` con 7 867 B transferidos, frente a los 39 905 B del PNG. La ilustración vive en el Dashboard, que exige sesión, por lo que **no forma parte de la página auditada con Lighthouse** (inicio de sesión) y no altera sus métricas. Prueba: `entrega la ilustración con AVIF y WebP adaptativos y respaldo PNG (picture)`.

### 4.4 Optimización 4: carga diferida y *code splitting* (WSG 3.7 y 3.3)

**Diagnóstico.** Las cuatro pantallas viajaban en un solo `index.js` de 226 263 B (70 831 B transferidos), aunque el inicio de sesión no usa Dashboard, Vehículos ni Pedidos. Lighthouse marcaba *Reduce unused JavaScript*.

**Implementación (parte 1: división por pantalla).**

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

**Implementación (parte 2: arranque tras el primer pintado).** El HTML ahora trae una pantalla de bienvenida (logotipo y título) con los estilos incrustados, y el JavaScript de la aplicación no se pide hasta que el navegador informa el primer pintado (`PerformanceObserver` de tipo `paint`, con respaldo a los 3 s). Entonces se precargan en paralelo los módulos y se importa la entrada.

ANTES (`index.html` compilado):

```html
<script type="module" crossorigin src="/assets/index-jqtqE8ZJ.js"></script>
<link rel="modulepreload" crossorigin href="/assets/vendor-oT4qkDZn.js">
<link rel="stylesheet" crossorigin href="/assets/index-DdVb1IjV.css">
```

DESPUÉS:

```html
<style>/* hoja de estilos incrustada */</style>
<meta name="precarga" content="/assets/vendor-oT4qkDZn.js,/assets/index-D7Y1-2wk.js">
<script>(function(){var m=document.querySelector('meta[name=precarga]').content.split(','),ok=0;
function ir(){if(ok++)return;m.forEach(function(h){var l=document.createElement('link');
l.rel='modulepreload';l.crossOrigin='';l.href=h;document.head.appendChild(l)});import(m[m.length-1])}
try{new PerformanceObserver(function(l,o){if(l.getEntriesByName('first-contentful-paint').length)
{o.disconnect();setTimeout(ir)}}).observe({type:'paint',buffered:true});setTimeout(ir,3000)}
catch(e){addEventListener('load',ir)}})()</script>
```

El plugin de `vite.config.ts` hace esta transformación al compilar. Como el script es en línea, el servidor calcula su hash SHA-256 al montar el frontend y lo agrega a la política `Content-Security-Policy` (`script-src 'self' 'sha256-…'`, sin `'unsafe-inline'`); prueba `test_csp_autoriza_solo_por_hash_los_scripts_en_linea`.

**Por qué se llegó a esta forma (medido).** Dos variantes intermedias (hoja de estilos incrustada con los módulos precargados desde el HTML, y arranque tras el evento `load`) dieron un FCP **bimodal**, de 0,7 s o 1,3 s según la corrida: cuando los módulos precargados terminaban de descargarse antes del primer pintado, Lighthouse los contaba dentro del FCP. La variante final no pide el JavaScript hasta después del primer pintado y las 8 corridas quedaron entre 0,64 s y 0,70 s.

**Evidencia (salida de `vite build`, tamaño sin comprimir / comprimido):**

| Archivo | Tamaño | Gzip |
|---|---|---|
| `index` (entrada) | 16,52 kB | 6,01 kB |
| `vendor` | 180,64 kB | 59,47 kB |
| `DashboardPage` | 10,40 kB | 3,01 kB |
| `VehiculosPage` | 10,43 kB | 3,54 kB |
| `PedidosPage` | 9,96 kB | 3,34 kB |
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

### 4.6 Optimización 6: reducción de peticiones HTTP e *inlining* (WSG 4.3)

**Diagnóstico.** El favicon apuntaba a `/vite.svg`, un archivo inexistente: el servidor respondía con el `index.html` de reserva, y el navegador hacía dos peticiones inútiles. Además, la hoja de estilos era un archivo aparte que bloqueaba el primer pintado.

ANTES (`index.html`):

```html
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
<link rel="stylesheet" crossorigin href="/assets/index-DdVb1IjV.css">
```

DESPUÉS:

```html
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E...%3C/svg%3E" />
<style>/* hoja de estilos incrustada al compilar */</style>
```

Los íconos de la interfaz (`lucide-react`) ya son componentes SVG en línea: no generan peticiones. **Resultado medido: de 7 a 3 peticiones en la carga inicial** (documento, chunk `vendor` y script de entrada). El costo es que `index.html` pesa 4,7 kB comprimido en lugar de 0,6 kB; se compensa con la eliminación del archivo CSS (3,8 kB) y de su petición.

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

**Evidencia medida.** Revalidar `index.html` con el ETag devuelve 304 sin cuerpo; los archivos de `/assets` no se vuelven a pedir. Pruebas: `test_get_de_la_api_lleva_etag_y_responde_304_si_no_cambio`, `test_frontend_revalida_con_304_cuando_el_archivo_no_cambio` y `test_frontend_assets_con_cache_inmutable_e_index_con_revalidacion`.

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

### 5.1 Resultado final frente a los umbrales de referencia

Móvil (perfil por defecto de Lighthouse), escenario final: **8 corridas**, mediana y rango.

| Métrica | Umbral de referencia | ANTES (mediana de 3) | DESPUÉS (mediana de 8) | Rango DESPUÉS | Corridas que cumplen |
|---|---|---|---|---|---|
| Puntaje de rendimiento | ≥ 90 | 93 | **100** | 100 a 100 | 8 de 8 |
| First Contentful Paint | ≤ 1,0 s | 2,613 s | **0,674 s** | 0,640 a 0,701 s | 8 de 8 |
| Largest Contentful Paint | ≤ 1,4 s | 2,613 s | **0,674 s** | 0,640 a 0,701 s | 8 de 8 |
| Total Blocking Time | ≤ 85 ms | 0 ms | **0 ms** | 0 a 85,5 ms | 7 de 8 (una corrida dio 85,5 ms) |
| Cumulative Layout Shift | ≤ 0,02 | 0 | **0** | 0 | 8 de 8 |
| Peso transferido | ≤ 1,1 MB | 105 397 B | **68 966 B** (0,07 MB) | constante | 8 de 8 |
| Peticiones HTTP | sin umbral | 7 | **3** | constante | — |

Escritorio (perfil complementario), mediana de 3 corridas:

| Métrica | ANTES | DESPUÉS |
|---|---|---|
| Puntaje de rendimiento | 100 (corridas: 98, 100, 100) | 100 |
| FCP / LCP | 0,540 s | 0,227 s |
| Peso transferido | 106 836 B | 68 966 B |
| Peticiones HTTP | 7 | 3 |

### 5.2 Efecto de cada etapa (móvil)

| Etapa | Puntaje | FCP y LCP | Peso | Peticiones | Corridas |
|---|---|---|---|---|---|
| 0. ANTES (`main`, `vite preview`) | 93 | 2,613 s | 105 397 B | 7 | 3 |
| 1. Frontend optimizado (sin fuente externa, favicon incrustado, *code splitting*), `vite preview` | 100 | 1,365 s | 70 981 B | 4 | 3 |
| 2. Etapa 1 servida por FastAPI con Brotli y caché (Docker) | 100 | 1,455 s | 68 867 B | 4 | 3 |
| 3. Etapa 2 con hoja de estilos incrustada, pantalla de bienvenida y arranque tras el primer pintado | 100 | **0,674 s** | **68 966 B** | **3** | 8 |

### 5.3 Lectura honesta de los resultados

- **Lo que sí se logró:** el puntaje sube de 93 a 100; el FCP y el LCP bajan 74 % en móvil (de 2,61 s a 0,67 s); el peso baja 34,6 % y las peticiones de 7 a 3. Los umbrales de la rúbrica de FCP (≤ 1,0 s) y LCP (≤ 1,4 s) se cumplen en las 8 corridas.
- **El TBT es el indicador más ruidoso.** Su mediana es 0 ms, pero en 3 de las 16 corridas de las dos últimas variantes midió entre 82 y 110 ms; en el escenario final, una de 8 corridas dio 85,5 ms, medio milisegundo por encima del umbral. Se atribuye a la carga del equipo de pruebas (Windows con contenedor), no a la aplicación, pero no se verificó aislando el equipo.
- **El servidor de FastAPI no acelera por sí solo la carga inicial:** en la etapa 2 el FCP fue 0,09 s peor que con `vite preview` directo. Su aporte medible es la reducción de bytes en las llamadas a la API (84 % a 97 %) y la caché de las visitas de retorno.
- **Los valores absolutos no son comparables con los del informe de referencia** (peso de 8,4 MB y puntaje 38): ese informe describe otra aplicación. Nuestro punto de partida ya era liviano (105 KB); la mejora relativa es la que corresponde a esta aplicación.
- **Compromiso de la pantalla de bienvenida.** Mientras React arranca, el usuario ve el logotipo y el título; el formulario de inicio de sesión aparece cuando React monta, poco después del primer pintado (no se midió ese instante por separado). Si el navegador no informa el primer pintado (por ejemplo, una pestaña en segundo plano), el arranque ocurre a los 3 s.

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

**DESPUÉS: 68 966 B**

- Datos: 68 966 / 10⁹ = 0,000068966 GB
- Energía: 0,000068966 × 0,300 = 2,069 × 10⁻⁵ kWh (20,69 mWh)
- Emisiones: 2,069 × 10⁻⁵ × 494 = 0,010221 g = **10,22 mg CO₂e por carga**

Reducción: 15,62 − 10,22 = 5,40 mg por carga (**−34,6 %**, igual a la reducción de bytes porque el modelo es lineal en los datos).

Reparto de la carga DESPUÉS por segmento: centros de datos 2,28 mg, redes 2,45 mg y dispositivos del usuario 5,49 mg. El dispositivo es el segmento mayor (53,7 %), por lo que reducir el JavaScript ejecutado también importa.

### 6.3 Cálculo por llamada a la API y por imagen

| Recurso | Bytes ANTES | Bytes DESPUÉS | mg CO₂e ANTES | mg CO₂e DESPUÉS |
|---|---|---|---|---|
| Listado de vehículos | 8 601 | 446 | 1,275 | 0,066 |
| Listado de pedidos | 18 001 | 555 | 2,668 | 0,082 |
| Ilustración del Dashboard (PNG a AVIF, 560 px) | 39 905 | 7 958 | 5,914 | 1,179 |

La ilustración AVIF emite 80,1 % menos que su respaldo PNG cada vez que se muestra.

### 6.4 Proyección anual (supuesto explícito)

El sistema es de uso interno de DistriRápido y aún no tiene tráfico real, por lo que el volumen es un **supuesto ilustrativo**, no una medición: 50 usuarios × 250 días hábiles × 4 cargas iniciales al día = **50 000 cargas al año**. Se muestra también 500 000 para comparar con el informe de referencia.

| Escenario anual | Emisiones ANTES | Emisiones DESPUÉS | Ahorro anual |
|---|---|---|---|
| 50 000 cargas iniciales | 0,781 kg CO₂e | 0,511 kg CO₂e | **0,270 kg CO₂e** |
| 500 000 cargas iniciales | 7,810 kg CO₂e | 5,110 kg CO₂e | **2,700 kg CO₂e** |
| Ilustración, 50 000 vistas del Dashboard | 0,296 kg CO₂e | 0,059 kg CO₂e | **0,237 kg CO₂e** |
| Ilustración, 500 000 vistas del Dashboard | 2,957 kg CO₂e | 0,590 kg CO₂e | **2,367 kg CO₂e** |

Estas cifras son **modestas** porque la aplicación ya es liviana; el informe de referencia proyecta 935 kg al año porque parte de una página de 8,4 MB. El mayor ahorro se espera cuando crezca el volumen de datos: la paginación de 12 filas evita transferir el 95 % al 97 % de cada listado, y esa proporción se mantiene cuando las tablas tengan miles de registros.

---

## 7. Evidencias de validación

| Evidencia | Resultado |
|---|---|
| Pruebas del backend (Python 3.12, Docker) | **52 pasan**; cobertura 88 % (incluye `seed.py`, que no se prueba) |
| Pruebas del frontend (Vitest) | **70 pasan**; cobertura de líneas 94,95 % |
| Verificación de tipos (`tsc`) | Sin errores |
| Vulnerabilidades en dependencias (`npm audit`) | 0 |
| Funcionamiento en navegador | Inicio de sesión con usuario de datos semilla en un servidor local, Dashboard con la ilustración AVIF, sin errores de consola ni violaciones de la política CSP |
| Flujo CI en GitHub Actions (`ci.yml`) | En verde en la rama `feature/green-it` |
| Flujo `green-audit.yml` con Lighthouse CI | **En verde en GitHub Actions** (ejecución 42628243459, commit `da3b873`): puntaje ≥ 0,9, FCP ≤ 1,0 s, LCP ≤ 1,4 s, TBT ≤ 85 ms, CLS ≤ 0,02 y peso ≤ 1,1 MB, todos como errores bloqueantes sobre la mediana de 3 corridas en el ejecutor de GitHub |
| Benchmark de la API | `scripts/medir_api.py` (resultados en la sección 4) |
| Cálculo de carbono | `scripts/calcular_swdm.py` (resultados en la sección 6) |
| Variantes de la ilustración | `scripts/generar_ilustracion_hero.py` (resultados en la sección 4.3) |

---

## 8. Limitaciones

1. **Solo se auditó la pantalla de inicio de sesión.** Dashboard, Vehículos y Pedidos requieren credenciales; sus listados se evaluaron con el benchmark de la API y la ilustración con la medición de pesos, no con Lighthouse.
2. **Servidores distintos entre ANTES y DESPUÉS** (`vite preview` y FastAPI en Docker); por eso se incluye la tabla por etapas que aísla cada efecto.
3. **El benchmark de la API se ejecuta en el mismo proceso, con SQLite en memoria**: mide serialización y compresión, no la red ni PostgreSQL. Con 1 000 filas no demuestra mejora de tiempo en las consultas.
4. **La ilustración es un recurso propio generado por código**, no una fotografía; la conversión de formatos de una fotografía puede dar proporciones distintas.
5. **La intensidad eléctrica de 494 g/kWh es el promedio mundial**; la del Perú es distinta y no se usó por no contar con una fuente verificada en esta auditoría.
6. **Lighthouse varía entre corridas**, sobre todo el TBT; por eso el escenario final se midió 8 veces y se reporta el rango, incluida la corrida que superó el umbral.
7. **El perfil móvil de Lighthouse es una simulación** (red y CPU limitadas por software), no un dispositivo real.

---

## 9. Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 09/11/2026 | Primer informe Green IT: ocho optimizaciones con código ANTES y DESPUÉS, mediciones con Lighthouse y benchmark propio, y cálculo SWDM v4. |
