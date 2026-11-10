# Informe de Reducción del Impacto Ambiental y Optimización (Green IT)

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Versión del documento:** 1.0.0  
**Fecha:** 09/11/2026 (redacción simplificada y referencias cruzadas: 10/11/2026)  
**Rama de trabajo:** `feature/green-it`

[← Volver al README Principal](../../../README.md) · [Documento 02: Estándares de ingeniería de software](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md)

---

## En resumen

EcoLogística Lima ayuda a reducir las emisiones de CO2 en el reparto de mercadería. Sería contradictorio que el propio programa gastara energía de más. Por eso **revisamos nuestra aplicación, la mejoramos de 8 maneras distintas y medimos el resultado**.

| Qué medimos (página de inicio de sesión, en celular simulado) | ANTES | DESPUÉS |
|---|---|---|
| Puntaje de rendimiento (de 0 a 100) | 93 | **100** |
| Tiempo hasta ver lo primero en pantalla | 2,61 segundos | **0,67 segundos** |
| Datos descargados | 105 397 bytes | **68 966 bytes** |
| Archivos pedidos al servidor | 7 | **3** |
| Carbono emitido en cada carga de la página | 15,62 miligramos | **10,22 miligramos** |

**En una frase:** la página aparece casi cuatro veces más rápido (74 % menos de espera), descarga un tercio menos de datos y emite un tercio menos de carbono.

**Lo que no logramos, dicho con claridad** (el detalle está en la [sección 8](#8-límites-de-este-trabajo)):

- La mejora de la consulta a la base de datos no se notó en velocidad con mil registros ([4.1](#41-optimización-1-consultas-livianas-e-índices)).
- En una de las 8 mediciones, el tiempo de bloqueo de la página fue 0,5 milisegundos mayor que el límite ([5.1](#51-resultado-final-frente-a-los-límites-de-referencia)).
- El ahorro anual de carbono es pequeño, porque la aplicación ya era liviana ([6.4](#64-proyección-anual)).

## Cómo leer este documento

| Si usted quiere... | Vaya a... |
|---|---|
| Entender las palabras técnicas | [Glosario](#glosario-las-palabras-en-simple) |
| Saber por qué hicimos esto | [Sección 1](#1-propósito-por-qué-hicimos-este-trabajo) |
| Ver cómo se midió | [Sección 2](#2-cómo-medimos) |
| Ver las 8 mejoras, con el código ANTES y DESPUÉS | [Sección 4](#4-las-8-optimizaciones) |
| Ver los resultados | [Sección 5](#5-resultados-antes-y-después) |
| Ver el cálculo del carbono | [Sección 6](#6-impacto-ambiental-con-el-modelo-swdm-v4) |
| Ver en qué normas nos apoyamos | [Documento 02](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#2-normas-internacionales) |
| Entender la revisión automática en GitHub | [Documento 02, sección 5](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#5-automatización-con-github-actions) |

## Glosario: las palabras en simple

| Término | En simple |
|---|---|
| **Lighthouse** | Una herramienta gratuita de Google que "califica" una página web de 0 a 100 según su rendimiento. |
| **Puntaje de rendimiento** | Esa calificación. 90 o más se considera bueno. |
| **FCP (First Contentful Paint)** | El momento en que aparece **lo primero** en la pantalla (un texto, un logo). |
| **LCP (Largest Contentful Paint)** | El momento en que aparece **lo más grande** de la pantalla. |
| **TBT (Total Blocking Time)** | El tiempo en que la página se queda "congelada" y no responde a clics. |
| **CLS (Cumulative Layout Shift)** | Cuánto "saltan" los elementos mientras la página carga. 0 significa que nada se mueve. |
| **Peso o transferencia** | La cantidad de datos que se descargan. Un byte es la unidad básica; 1 KB son unos 1 000 bytes. |
| **Petición HTTP** | Cada archivo que el navegador le pide al servidor (la página, un estilo, una imagen...). |
| **API** | La parte del sistema que entrega los datos (vehículos, pedidos) a la pantalla. |
| **Caché** | Una copia guardada en el navegador, para no volver a descargar lo mismo. |
| **ETag y respuesta 304** | El ETag es una "huella" del contenido. Si no cambió, el servidor responde 304 ("sigue igual") sin reenviarlo. |
| **Compresión (Brotli y Gzip)** | "Empaquetar" los datos para que ocupen menos al viajar, como una maleta al vacío. |
| **AVIF y WebP** | Formatos modernos de imagen, más livianos que PNG o JPG. |
| **Paginación** | Mostrar los registros de a pocos (12 por página) en lugar de todos juntos. |
| **Índice (en base de datos)** | Como el índice de un libro: permite encontrar un dato sin leer todas las páginas. |
| **ORM** | Una capa que traduce entre el programa y la base de datos; crea un "objeto" por cada fila. |
| **Carga diferida (lazy loading)** | Descargar una parte del programa solo cuando se necesita. |
| **CSP (política de seguridad de contenido)** | Una regla del servidor que le dice al navegador qué scripts puede ejecutar. |
| **CO2e (dióxido de carbono equivalente)** | La unidad que resume el efecto de varios gases de invernadero en uno solo. |
| **kWh (kilovatio-hora)** | La unidad de energía de la factura de luz. |
| **SWDM v4** | Un modelo que estima el carbono emitido por transferir datos en la web. |
| **Mediana** | El valor del medio al ordenar varias mediciones. Ignora los valores extremos. |
| **ANTES y DESPUÉS** | El estado del programa antes y después de las mejoras. |

---

## 1. Propósito: por qué hicimos este trabajo

La eficiencia del software importa para el ambiente: cada dato que no se transmite, cada consulta que no recorre toda una tabla y cada instrucción que no se ejecuta ahorran energía en tres lugares: los centros de datos, las redes y el celular o computador del usuario. Este informe cuenta cómo se auditó la aplicación y qué se logró, con cuatro objetivos:

1. Encontrar con mediciones dónde se desperdiciaba (ver [sección 3](#3-punto-de-partida-estado-antes)).
2. Aplicar **8 optimizaciones**, mostrando el código ANTES y DESPUÉS de cada una ([sección 4](#4-las-8-optimizaciones)).
3. Medir el efecto con Lighthouse y con una prueba propia de la API, y estimar la huella de carbono ([secciones 5](#5-resultados-antes-y-después) y [6](#6-impacto-ambiental-con-el-modelo-swdm-v4)).
4. Comprobar que nada se rompió: todas las pruebas automáticas pasan ([sección 7](#7-pruebas-y-evidencias)).

Las normas que respaldan estas decisiones están en el [Documento 02](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#2-normas-internacionales).

### 1.1 Nuestro stack no es MERN: cómo lo adaptamos

El informe de referencia de la asignatura describe el stack **MERN** (MongoDB, Express, React y Node). **Nuestro proyecto no usa MERN.** Usa **FastAPI** (Python), **React** y **SQLAlchemy**, el stack aprobado en el [Documento 10 de Inicio](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md). No simulamos tecnologías que no tenemos: cada una de las 8 áreas se aplicó con su **equivalente directo**.

| # | Área de optimización (referencia MERN) | Lo que hicimos en nuestro stack | Detalle |
|---|---|---|---|
| 1 | `.select()`, `.lean()` e índices en MongoDB | Pedir solo las columnas necesarias, sin crear objetos de más, y agregar índices | [4.1](#41-optimización-1-consultas-livianas-e-índices) |
| 2 | Paginación de 12 registros | Páginas de 12 con el total en una cabecera y un paginador en la pantalla | [4.2](#42-optimización-2-paginación) |
| 3 | Imágenes WebP/AVIF con `<picture>` | Una ilustración con `<picture>`: AVIF, WebP y PNG de respaldo, en dos anchos | [4.3](#43-optimización-3-imágenes-avif-y-webp-con-picture) |
| 4 | `React.lazy` y `Suspense` | Lo mismo, más arrancar la aplicación después del primer pintado | [4.4](#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado) |
| 5 | Cambiar librerías por funciones nativas | Quitar la fuente tipográfica externa (Google Fonts) y confirmar que no usamos `moment` ni `lodash` | [4.5](#45-optimización-5-dependencias-y-recursos-de-terceros) |
| 6 | Incrustar SVG | Incrustar el favicon y la hoja de estilos en el HTML | [4.6](#46-optimización-6-menos-peticiones-con-elementos-incrustados) |
| 7 | `Cache-Control`, ETag y React Query | `Cache-Control` y ETag en la API y los archivos (sin agregar React Query) | [4.7](#47-optimización-7-caché) |
| 8 | Compresión Brotli y Gzip en Express | Compresión Brotli con respaldo Gzip en FastAPI | [4.8](#48-optimización-8-compresión-brotli-y-gzip) |

---

## 2. Cómo medimos

Todas las cifras son **medidas**, no estimadas, y cada una indica cómo se reproduce.

| Aspecto | Detalle |
|---|---|
| Herramienta de rendimiento | Google Lighthouse 12.8.2 (categoría de rendimiento) con HeadlessChrome 156 |
| Perfil móvil (el que usa Lighthouse por defecto) | Un celular simulado con red 4G (150 ms de demora y 1 638 kbps de bajada) y un procesador 4 veces más lento |
| Perfil de escritorio (complementario) | El perfil `desktop` de Lighthouse |
| Repeticiones | 3 mediciones en los pasos intermedios y **8 mediciones en el estado final**. Se informa la **mediana** y el rango |
| Pantalla medida | La de inicio de sesión, la única que se puede abrir sin credenciales |
| Estado ANTES | Rama `main`, commit `8981ee6`, compilada y servida con `vite preview` |
| Estado DESPUÉS | Rama `feature/green-it`, compilada con `VITE_API_URL=""` y servida por FastAPI en un contenedor Docker (Python 3.12) |
| Prueba de la API | [`scripts/medir_api.py`](../../../scripts/medir_api.py): 1 000 vehículos y 1 000 pedidos en una base en memoria; mediana de 200 repeticiones |
| Cálculo de carbono | [`scripts/calcular_swdm.py`](../../../scripts/calcular_swdm.py) con el modelo SWDM v4 |

Comandos para repetir las mediciones:

```bash
cd src/frontend && VITE_API_URL="" npm run build
PYTHONPATH=src/backend python -m uvicorn app.main:app --port 8000
npx lighthouse@12 http://localhost:8000/ --only-categories=performance --output=json
PYTHONPATH=src/backend python scripts/medir_api.py
python scripts/calcular_swdm.py
python scripts/generar_ilustracion_hero.py
```

---

## 3. Punto de partida (estado ANTES)

Se revisó el commit `8981ee6` y se encontraron estos problemas reales:

| Hallazgo | Evidencia | Lo resuelve |
|---|---|---|
| Una fuente tipográfica externa **frenaba** el primer pintado | `@import` de Google Fonts: una hoja de estilos de terceros (1 395 B) y un archivo de fuente (27 301 B) | [4.5](#45-optimización-5-dependencias-y-recursos-de-terceros) |
| El favicon apuntaba a un archivo que **no existía** | `index.html` enlazaba `/vite.svg`, ausente en `public/`: 2 peticiones inútiles (1 068 B) | [4.6](#46-optimización-6-menos-peticiones-con-elementos-incrustados) |
| **Cinco archivos sin uso** | `hero.png` (13 057 B), `react.svg` (4 126 B), `vite.svg` (8 710 B), `favicon.svg` (9 522 B) e `icons.svg` (5 055 B) | [4.3](#43-optimización-3-imágenes-avif-y-webp-con-picture) |
| Todo el programa en **un solo paquete** | `index.js` de 226 263 B (70 831 B transferidos), aunque el inicio de sesión usa solo una parte | [4.4](#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado) |
| Listados de **50 filas** y filtro en el navegador | Valor por defecto de 50 filas por llamada | [4.2](#42-optimización-2-paginación) |
| Respuestas **sin compresión** ni caché reutilizable | La API marcaba todo como `Cache-Control: no-store` y sin ETag; el JSON viajaba sin comprimir; los archivos no tenían caché de larga duración | [4.7](#47-optimización-7-caché) y [4.8](#48-optimización-8-compresión-brotli-y-gzip) |
| Falta de **índices** | `vehiculos.estado` y `pedidos.creado_en` se recorrían completos | [4.1](#41-optimización-1-consultas-livianas-e-índices) |
| **Ninguna imagen optimizada** | El banner del Dashboard no tenía imagen; el único PNG era de la plantilla de Vite y no se usaba | [4.3](#43-optimización-3-imágenes-avif-y-webp-con-picture) |

**Cifras de partida** (móvil, mediana de 3 mediciones):

| Indicador | Valor ANTES |
|---|---|
| Puntaje de rendimiento | **93 / 100** |
| Primer contenido (FCP) | 2,61 s |
| Contenido más grande (LCP) | 2,61 s |
| Tiempo de bloqueo (TBT) | 0 ms |
| Saltos de diseño (CLS) | 0 |
| Peso total | 105 397 B (102,9 KiB) |
| Peticiones | 7 |

Lighthouse marcó como fallidas tres revisiones: *Eliminate render-blocking resources* (hay algo que frena el primer pintado), *Preconnect to required origins* (conexiones a otros sitios) y *Reduce unused JavaScript* (programa que se descarga sin usarse).

---

## 4. Las 8 optimizaciones

Cada una sigue el mismo orden: **el problema**, **qué hicimos**, el código **ANTES y DESPUÉS**, **qué ganamos** y **dónde ver más** (la norma que la respalda y la prueba automática). La tabla que une las 8 con sus normas es la [matriz del Documento 02](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#4-matriz-de-mapeo).

### 4.1 Optimización 1: consultas livianas e índices

**El problema.** Cada vez que la pantalla pedía una lista, el programa construía un objeto completo por cada fila de la base de datos, y dos columnas muy consultadas no tenían índice.

**Qué hicimos.** Los listados piden solo las columnas que la pantalla necesita y devuelven filas simples, sin crear objetos de más (es el equivalente a `.select()` y `.lean()` de Mongoose). Además agregamos dos **índices** (`idx_vehiculos_estado` e `idx_pedidos_creado_en`), como el índice de un libro.

ANTES ([`vehiculos_router.py`](../../../src/backend/app/routers/vehiculos_router.py)):

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

El índice, en [`models.py`](../../../src/backend/app/models.py): ANTES no existía; DESPUÉS:

```python
__table_args__ = (Index("idx_vehiculos_estado", "estado"),)
```

**Qué ganamos.** Con el plan de consulta de SQLite se ve la diferencia:

| Consulta | Sin índice | Con índice |
|---|---|---|
| `vehiculos` filtrados por estado | Lee toda la tabla (`SCAN`) | Busca directamente (`SEARCH ... USING INDEX idx_vehiculos_estado`) |
| `pedidos` ordenados por fecha, los 12 últimos | Lee toda la tabla y ordena aparte (`TEMP B-TREE`) | Lee en orden con el índice (`USING INDEX idx_pedidos_creado_en`) |

**Una advertencia honesta.** Con 1 000 filas, el tiempo **no cambió de forma apreciable** (vehículos: de 5,50 ms a 5,74 ms; pedidos: de 7,13 ms a 6,49 ms; es ruido de medición). La ventaja es de **escalabilidad**: cuando las tablas crezcan, el índice evitará recorrerlas enteras. No afirmamos una mejora de velocidad a este tamaño.

**Dónde ver más.** Norma: [WSG 3.16](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Regla: [backend, puntos 1 y 3](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#32-reglas-para-el-backend) · Prueba: `test_listado_de_vehiculos_filtra_por_busqueda_y_estado` en [`test_rendimiento.py`](../../../src/backend/tests/test_rendimiento.py).

### 4.2 Optimización 2: paginación

**El problema.** El listado devolvía hasta 50 filas de una vez y el navegador las filtraba. Era más datos de los necesarios, y la búsqueda solo alcanzaba lo ya descargado.

**Qué hicimos.** Ahora el servidor entrega **12 registros por página** (acepta `page`, `limit` hasta 50, `estado` y `q` para buscar) e informa el total en la cabecera `X-Total-Count`. La pantalla muestra un paginador ([`Paginador.tsx`](../../../src/frontend/src/components/Paginador.tsx)) y envía la búsqueda al servidor esperando 300 milisegundos después de la última tecla ([`useDebounced.ts`](../../../src/frontend/src/useDebounced.ts)), para no consultar en cada letra.

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

ANTES (frontend, [`VehiculosPage.tsx`](../../../src/frontend/src/pages/VehiculosPage.tsx)):

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

**Qué ganamos** (bytes por llamada, ya comprimidos):

| Listado | ANTES (50 filas) | DESPUÉS (1 página de 12) | Reducción |
|---|---|---|---|
| Vehículos | 8 601 B | 446 B | 94,8 % |
| Pedidos | 18 001 B | 555 B | 96,9 % |

**Dónde ver más.** Norma: [WSG 4.3](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Regla: [backend, punto 2](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#32-reglas-para-el-backend) · Pruebas: `test_listado_de_vehiculos_pagina_de_12_y_informa_el_total`, `test_listado_de_pedidos_pagina_busca_y_conserva_el_aislamiento_por_bodega` y las de `Paginador`, `VehiculosPage` y `PedidosPage`.

### 4.3 Optimización 3: imágenes AVIF y WebP con picture

**El problema.** La aplicación no tenía ninguna imagen optimizada: el banner del Dashboard solo usaba colores (CSS), y el único PNG del repositorio (`hero.png`, 13 057 B) venía de una plantilla y no se usaba. Además, una prueba previa mostró algo que conviene saber: **convertir no siempre reduce**. Ese PNG pesaba 13 057 B, su versión WebP 13 680 B (4,8 % más) y solo AVIF ahorró (10 335 B, 20,8 % menos). Por eso cada conversión se mide antes de adoptarla.

**Qué hicimos.** Agregamos una ilustración al banner del Dashboard: una ruta de entrega con una hoja, que es el tema del proyecto. La genera el programa [`generar_ilustracion_hero.py`](../../../scripts/generar_ilustracion_hero.py), que produce **dos anchos** (280 px para pantallas comunes y 560 px para las de alta densidad) en **tres formatos** (AVIF, WebP y PNG de respaldo) y muestra una tabla con el peso de cada uno. También eliminamos los cinco archivos sin uso (40 470 B). Para usar otra imagen de la marca, basta reemplazar la función `dibujar()`: el resto del proceso es el mismo.

ANTES ([`DashboardPage.tsx`](../../../src/frontend/src/pages/DashboardPage.tsx)): sin imagen.

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

En simple: el navegador elige el **mejor formato que entienda** (AVIF primero, luego WebP y, si no, PNG) y el **ancho que le convenga**. La imagen es decorativa, por eso tiene `alt=""` (los lectores de pantalla la omiten); declara `width` y `height` para que la página no "salte" al cargarla; y se descarga de forma diferida.

**Qué ganamos** (peso medido de cada variante):

| Ancho | PNG (respaldo) | WebP | Ahorro WebP | AVIF | Ahorro AVIF |
|---|---|---|---|---|---|
| 280 px | 17 393 B | 7 988 B | 54,1 % | 3 913 B | 77,5 % |
| 560 px | 39 905 B | 15 164 B | 62,0 % | 7 958 B | **80,1 %** |

En el navegador Chrome, la variante elegida fue `hero-rutas-560.avif`, con 7 867 B transferidos frente a los 39 905 B del PNG. La imagen está en el Dashboard, que pide iniciar sesión, así que **no forma parte de la página medida con Lighthouse** y no cambia sus resultados.

**Dónde ver más.** Norma: [WSG 2.9](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Regla: [frontend, punto 5](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#33-reglas-para-el-frontend) · Prueba: `entrega la ilustración con AVIF y WebP adaptativos y respaldo PNG (picture)` en [`DashboardPage.test.tsx`](../../../src/frontend/src/__tests__/DashboardPage.test.tsx). Carbono de la imagen: [6.3](#63-cálculo-por-llamada-a-la-api-y-por-imagen).

### 4.4 Optimización 4: carga diferida y arranque tras el primer pintado

**El problema.** Las cuatro pantallas viajaban en un solo paquete de 226 263 B (70 831 B transferidos), aunque la de inicio de sesión no usa Dashboard, Vehículos ni Pedidos.

**Qué hicimos, en dos partes.**

*Parte 1: dividir por pantalla.* Cada pantalla se descarga solo cuando se necesita (`React.lazy` y `Suspense`). Además las librerías que casi no cambian (React y el enrutador) van en un paquete aparte llamado `vendor`, que se conserva en la caché entre versiones.

ANTES ([`App.tsx`](../../../src/frontend/src/App.tsx)):

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

*Parte 2: arrancar la aplicación después del primer pintado.* El HTML ahora trae una **pantalla de bienvenida** (logo y título) con los estilos incrustados, de modo que el navegador la dibuja de inmediato. El programa de la aplicación **no se pide hasta que el navegador avisa que ya pintó** (con un respaldo a los 3 segundos por si el aviso no llega). Después se descargan los módulos en paralelo y la aplicación toma el control.

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

Esta transformación la hace un complemento de [`vite.config.ts`](../../../src/frontend/vite.config.ts) al compilar. Como ese script va dentro del HTML, el servidor calcula su **huella SHA-256** y la agrega a la política de seguridad (CSP), así el navegador lo acepta **sin** abrir la puerta a otros scripts ([`rendimiento.py`](../../../src/backend/app/rendimiento.py); ver también la [auditoría OWASP](../Sprint%2003/04%20OWASP%20V_1_0_0.md)).

**Cómo llegamos a esta forma (medido).** Dos versiones intermedias daban un tiempo de primer contenido que **variaba** entre 0,7 s y 1,3 s según la medición. La causa: cuando los módulos precargados terminaban de bajar *antes* del primer pintado, Lighthouse los contaba como parte del tiempo. La versión final no pide el programa hasta después del primer pintado, y las 8 mediciones quedaron entre 0,64 s y 0,70 s.

**Qué ganamos** (resultado de `vite build`, tamaño sin comprimir y comprimido):

| Archivo | Tamaño | Comprimido (Gzip) |
|---|---|---|
| `index` (entrada) | 16,52 kB | 6,01 kB |
| `vendor` | 180,64 kB | 59,47 kB |
| `DashboardPage` | 10,40 kB | 3,01 kB |
| `VehiculosPage` | 10,43 kB | 3,54 kB |
| `PedidosPage` | 9,96 kB | 3,34 kB |
| `Paginador` | 2,16 kB | 0,93 kB |

**Dónde ver más.** Normas: [WSG 3.7 y 3.3](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Reglas: [frontend, puntos 1, 2 y 6](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#33-reglas-para-el-frontend) · Prueba: `test_csp_autoriza_solo_por_hash_los_scripts_en_linea` en [`test_rendimiento.py`](../../../src/backend/tests/test_rendimiento.py).

### 4.5 Optimización 5: dependencias y recursos de terceros

**El problema.** Lo más costoso de lo que usábamos de terceros no era una librería de programación, sino la **fuente tipográfica de Google**: obligaba al navegador a conectarse a dos sitios ajenos y frenaba el primer pintado.

**Qué hicimos.** Reemplazamos esa fuente por la **tipografía que ya trae el sistema operativo** del usuario. Además verificamos que el proyecto **no usa** `moment` ni `lodash` (las fechas y números ya usan funciones nativas del navegador con `toLocaleString('es-PE')`) y que solo declara **4 dependencias de producción**: `react`, `react-dom`, `react-router-dom` y `lucide-react`.

ANTES ([`index.css`](../../../src/frontend/src/index.css)):

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
--font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
```

DESPUÉS:

```css
--font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
```

**Qué ganamos.** Dos peticiones a sitios de terceros menos y 28 696 B menos de descarga; desapareció la revisión *Preconnect to required origins*. **El costo:** la letra ahora depende del sistema del usuario, así que se ve ligeramente distinta en cada equipo.

**Dónde ver más.** Normas: [WSG 3.12, 3.5 y 2.11](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Regla: [frontend, puntos 3, 4 y 9](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#33-reglas-para-el-frontend).

### 4.6 Optimización 6: menos peticiones con elementos incrustados

**El problema.** El favicon (el ícono de la pestaña) apuntaba a `/vite.svg`, un archivo inexistente: el servidor respondía con la página de reserva y el navegador hacía **dos peticiones inútiles**. Además, la hoja de estilos era un archivo aparte que frenaba el primer pintado.

**Qué hicimos.** Incrustamos el favicon y la hoja de estilos **dentro del propio HTML**. Los íconos de la interfaz (`lucide-react`) ya eran componentes SVG en línea, y no generan peticiones.

ANTES ([`index.html`](../../../src/frontend/index.html)):

```html
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
<link rel="stylesheet" crossorigin href="/assets/index-DdVb1IjV.css">
```

DESPUÉS:

```html
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E...%3C/svg%3E" />
<style>/* hoja de estilos incrustada al compilar */</style>
```

**Qué ganamos.** De **7 a 3 peticiones** en la carga inicial (el documento, el paquete `vendor` y el script de entrada). **El costo:** el HTML pesa 4,7 kB comprimido en lugar de 0,6 kB, pero se compensa con la desaparición del archivo CSS (3,8 kB) y de su petición.

**Dónde ver más.** Norma: [WSG 4.3](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Regla: [frontend, punto 7](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#33-reglas-para-el-frontend).

### 4.7 Optimización 7: caché

**El problema.** La API marcaba **toda** respuesta como no guardable (`Cache-Control: no-store`), una cabecera de seguridad pensada para la sesión que se aplicaba igual a los datos. Y los archivos del frontend no tenían caché de larga duración. Resultado: el navegador volvía a descargar todo en cada visita.

**Qué hicimos** (en [`rendimiento.py`](../../../src/backend/app/rendimiento.py)). Cada tipo de contenido recibe la política que le corresponde:

| Contenido | Política | Efecto |
|---|---|---|
| Archivos de `/assets` (con huella en el nombre) | `public, max-age=31536000, immutable` | En una visita posterior no se vuelven a pedir: **0 bytes** |
| `index.html` | `no-cache` con ETag | Se revisa cada vez y, si no cambió, responde 304 sin cuerpo |
| Datos de la API (`GET /api/*`) | `private, no-cache` con ETag | Igual: si los datos no cambiaron, 304 sin cuerpo |
| Sesión y estado en vivo (`/api/auth/*` y `/api/health`) | `no-store` | Nunca se guardan, por seguridad |

ANTES ([`main.py`](../../../src/backend/app/main.py)): una sola cabecera fija para todo.

```python
response.headers["Cache-Control"] = "no-store"
```

DESPUÉS ([`rendimiento.py`](../../../src/backend/app/rendimiento.py)):

```python
etag = '"' + hashlib.sha256(cuerpo).hexdigest()[:32] + '"'
cabeceras["ETag"] = etag
cabeceras["Cache-Control"] = "private, no-cache"
if _coincide_etag(request.headers.get("if-none-match"), etag):
    return _con_seguridad(Response(status_code=304, headers=sin_cuerpo))
```

**Qué ganamos.** Revisar `index.html` con su ETag devuelve 304 sin cuerpo, y los archivos de `/assets` no se piden de nuevo. **Sobre React Query:** no lo agregamos; sumaría otra librería para un beneficio que el caché del navegador con ETag ya entrega.

**Dónde ver más.** Norma: [WSG 4.2](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Reglas: [backend, puntos 6 y 7](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#32-reglas-para-el-backend) · Pruebas: `test_get_de_la_api_lleva_etag_y_responde_304_si_no_cambio`, `test_frontend_revalida_con_304_cuando_el_archivo_no_cambio` y `test_frontend_assets_con_cache_inmutable_e_index_con_revalidacion`.

### 4.8 Optimización 8: compresión Brotli y Gzip

**El problema.** Los datos JSON y los archivos viajaban sin comprimir.

**Qué hicimos.** Agregamos compresión **Brotli** (con **Gzip** de respaldo) para las respuestas de 1 000 bytes o más.

ANTES ([`main.py`](../../../src/backend/app/main.py)): sin compresión. DESPUÉS:

```python
from brotli_asgi import BrotliMiddleware

app.middleware("http")(politica_http)
app.add_middleware(BrotliMiddleware, quality=5, minimum_size=1000, gzip_fallback=True)
```

**Qué ganamos** (prueba de la API, bytes que viajan por la red):

| Respuesta | Sin comprimir | Con Brotli | Reducción | Costo en el servidor (mediana) |
|---|---|---|---|---|
| Vehículos (50 filas) | 8 601 B | 1 372 B | 84,0 % | de 5,74 ms a 6,27 ms |
| Pedidos (50 filas) | 18 001 B | 1 609 B | 91,1 % | de 6,49 ms a 6,68 ms |
| Carga inicial del frontend (mismo build) | 70 981 B (con Gzip de `vite preview`) | 68 867 B | 3,0 % | no medido por separado |

Comprimir suma entre 0,2 y 0,5 milisegundos de trabajo por respuesta; solo se hace con cuerpos de 1 000 B o más.

**Dónde ver más.** Norma: [WSG 4.3](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#23-w3c-web-sustainability-guidelines-wsg) · Regla: [backend, punto 5](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#32-reglas-para-el-backend) · Prueba: `test_respuestas_grandes_se_comprimen_con_gzip_o_brotli`.

---

## 5. Resultados: ANTES y DESPUÉS

### 5.1 Resultado final frente a los límites de referencia

Estos son los límites que pide la rúbrica. Medición en móvil, **8 mediciones** del estado final:

| Métrica (qué significa) | Límite | ANTES (mediana de 3) | DESPUÉS (mediana de 8) | Rango DESPUÉS | ¿Cumple? |
|---|---|---|---|---|---|
| Puntaje de rendimiento | 90 o más | 93 | **100** | 100 | 8 de 8 |
| FCP: aparece lo primero | 1,0 s o menos | 2,613 s | **0,674 s** | 0,640 a 0,701 s | 8 de 8 |
| LCP: aparece lo más grande | 1,4 s o menos | 2,613 s | **0,674 s** | 0,640 a 0,701 s | 8 de 8 |
| TBT: tiempo "congelada" | 85 ms o menos | 0 ms | **0 ms** | 0 a 85,5 ms | **7 de 8** (una dio 85,5 ms) |
| CLS: saltos de diseño | 0,02 o menos | 0 | **0** | 0 | 8 de 8 |
| Peso descargado | 1,1 MB o menos | 105 397 B | **68 966 B** (0,07 MB) | constante | 8 de 8 |
| Peticiones | sin límite | 7 | **3** | constante | — |

En computador de escritorio (perfil complementario), mediana de 3 mediciones:

| Métrica | ANTES | DESPUÉS |
|---|---|---|
| Puntaje de rendimiento | 100 (mediciones: 98, 100 y 100) | 100 |
| FCP y LCP | 0,540 s | 0,227 s |
| Peso descargado | 106 836 B | 68 966 B |
| Peticiones | 7 | 3 |

### 5.2 Efecto de cada etapa

Como "ANTES" y "DESPUÉS" usan servidores distintos, medimos también los pasos intermedios, para saber qué mejora produjo cada cambio (móvil):

| Etapa | Puntaje | FCP y LCP | Peso | Peticiones | Mediciones |
|---|---|---|---|---|---|
| 0. ANTES (`main`, con `vite preview`) | 93 | 2,613 s | 105 397 B | 7 | 3 |
| 1. Frontend optimizado (sin fuente externa, favicon incrustado, carga por pantalla) con `vite preview` | 100 | 1,365 s | 70 981 B | 4 | 3 |
| 2. La etapa 1 servida por FastAPI con Brotli y caché (Docker) | 100 | 1,455 s | 68 867 B | 4 | 3 |
| 3. La etapa 2 con estilos incrustados, pantalla de bienvenida y arranque tras el primer pintado | 100 | **0,674 s** | **68 966 B** | **3** | 8 |

### 5.3 Lectura honesta de los resultados

- **Lo que sí logramos.** El puntaje sube de 93 a 100; el FCP y el LCP bajan 74 % en móvil (de 2,61 s a 0,67 s); el peso baja 34,6 % y las peticiones pasan de 7 a 3. Los límites de FCP (1,0 s) y LCP (1,4 s) se cumplen en las 8 mediciones.
- **El TBT es la medida más inestable.** Su mediana es 0 ms, pero en 3 de las 16 mediciones de las dos últimas versiones dio entre 82 y 110 ms; en el estado final, una de 8 dio 85,5 ms, **medio milisegundo sobre el límite**. Lo atribuimos a la carga de nuestro equipo de pruebas (Windows con contenedor), pero **no lo verificamos** aislando el equipo.
- **El servidor de FastAPI no acelera por sí solo la primera carga.** En la etapa 2, el FCP fue 0,09 s peor que con `vite preview`. Su aporte real es reducir los bytes de las llamadas a la API (84 % a 97 %) y la caché en las visitas siguientes.
- **Las cifras absolutas no se comparan con el informe de referencia** (8,4 MB y puntaje 38): ese informe trata de otra aplicación. La nuestra ya era liviana (105 KB), así que lo que corresponde es mirar la mejora relativa.
- **Una consecuencia de la pantalla de bienvenida.** Mientras React arranca, el usuario ve el logo y el título; el formulario aparece cuando React toma el control, poco después del primer pintado (ese instante no se midió por separado). Si el navegador no avisa que pintó (por ejemplo, una pestaña en segundo plano), la aplicación arranca a los 3 s.

---

## 6. Impacto ambiental con el modelo SWDM v4

### 6.1 El modelo y sus constantes

El modelo **Sustainable Web Design (versión 4)** estima el carbono de transferir datos así:

```
Energía (kWh)  = Datos (GB) × Suma de las intensidades de los 3 segmentos (kWh por GB)
Emisiones (g)  = Energía (kWh) × Emisiones de la electricidad (g de CO2e por kWh)
```

En palabras simples: **más datos transferidos, más energía; más energía, más carbono.** El modelo reparte el gasto en tres lugares:

| Segmento | Operación (kWh/GB) | Fabricación del equipo (kWh/GB) | Total (kWh/GB) |
|---|---|---|---|
| Centros de datos | 0,055 | 0,012 | 0,067 |
| Redes | 0,059 | 0,013 | 0,072 |
| Dispositivos del usuario | 0,080 | 0,081 | 0,161 |
| **Suma** | 0,194 | 0,106 | **0,300** |

La electricidad se valora con **494 g de CO2e por kWh** (el promedio mundial que usa SWDM v4 por defecto). Entonces cada gigabyte emite 0,300 × 494 = **148,2 g de CO2e**. Se toma 1 GB = 10⁹ bytes. Fuente: [Sustainable Web Design, *Estimating digital emissions*](https://sustainablewebdesign.org/estimating-digital-emissions/).

**Corrección a la plantilla de referencia.** Esa plantilla usa 0,815 kWh/GB y 442 g/kWh, que son valores de la **versión 3** del modelo, y sus resultados no cuadran con su propia fórmula (por ejemplo, 8,4 MB × 0,815 × 442 da 2,96 g y no los 2,15 g que presenta). Aquí aplicamos las constantes de la versión 4 y cada cálculo se puede reproducir con [`calcular_swdm.py`](../../../scripts/calcular_swdm.py).

### 6.2 Cálculo por carga inicial

**ANTES: 105 397 B**

- Datos: 105 397 ÷ 10⁹ = 0,000105397 GB
- Energía: 0,000105397 × 0,300 = 3,162 × 10⁻⁵ kWh (31,62 mWh)
- Emisiones: 3,162 × 10⁻⁵ × 494 = 0,015620 g = **15,62 mg de CO2e por carga**

**DESPUÉS: 68 966 B**

- Datos: 68 966 ÷ 10⁹ = 0,000068966 GB
- Energía: 0,000068966 × 0,300 = 2,069 × 10⁻⁵ kWh (20,69 mWh)
- Emisiones: 2,069 × 10⁻⁵ × 494 = 0,010221 g = **10,22 mg de CO2e por carga**

**Diferencia:** 15,62 − 10,22 = 5,40 mg por carga, es decir **34,6 % menos**. Coincide con la reducción de bytes porque el modelo es proporcional a los datos.

Cómo se reparte la carga DESPUÉS: centros de datos 2,28 mg, redes 2,45 mg y dispositivos del usuario 5,49 mg. El **dispositivo del usuario es lo más grande (53,7 %)**, por eso también importa ejecutar menos programa (ver [4.4](#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado)).

### 6.3 Cálculo por llamada a la API y por imagen

| Recurso | Bytes ANTES | Bytes DESPUÉS | mg de CO2e ANTES | mg de CO2e DESPUÉS |
|---|---|---|---|---|
| Listado de vehículos ([4.2](#42-optimización-2-paginación)) | 8 601 | 446 | 1,275 | 0,066 |
| Listado de pedidos ([4.2](#42-optimización-2-paginación)) | 18 001 | 555 | 2,668 | 0,082 |
| Ilustración del Dashboard, PNG a AVIF de 560 px ([4.3](#43-optimización-3-imágenes-avif-y-webp-con-picture)) | 39 905 | 7 958 | 5,914 | 1,179 |

La ilustración en AVIF emite **80,1 % menos** que su respaldo PNG cada vez que se muestra.

### 6.4 Proyección anual

El sistema es de uso interno de DistriRápido y todavía no tiene tráfico real, así que el volumen es un **supuesto ilustrativo**, no una medición: 50 usuarios × 250 días hábiles × 4 cargas iniciales al día = **50 000 cargas al año**. Se muestra también 500 000 para comparar con el informe de referencia. Si el uso real es otro, basta cambiar el número en [`calcular_swdm.py`](../../../scripts/calcular_swdm.py).

| Escenario anual | Emisiones ANTES | Emisiones DESPUÉS | Ahorro al año |
|---|---|---|---|
| 50 000 cargas iniciales | 0,781 kg de CO2e | 0,511 kg de CO2e | **0,270 kg** |
| 500 000 cargas iniciales | 7,810 kg de CO2e | 5,110 kg de CO2e | **2,700 kg** |
| Ilustración, 50 000 vistas del Dashboard | 0,296 kg de CO2e | 0,059 kg de CO2e | **0,237 kg** |
| Ilustración, 500 000 vistas del Dashboard | 2,957 kg de CO2e | 0,590 kg de CO2e | **2,367 kg** |

Estas cifras son **modestas** porque la aplicación ya era liviana; el informe de referencia proyecta 935 kg al año porque parte de una página de 8,4 MB. Donde más se espera ahorrar es a medida que crezcan los datos: la paginación evita transferir entre el 95 % y el 97 % de cada listado, y esa proporción se mantiene aunque las tablas tengan miles de filas.

---

## 7. Pruebas y evidencias

| Evidencia | Resultado |
|---|---|
| Pruebas automáticas del backend (Python 3.12, en Docker) | **52 pasan**; cobertura 88 % (incluye `seed.py`, que no se prueba) |
| Pruebas automáticas del frontend (Vitest) | **70 pasan**; cobertura de líneas 94,95 % |
| Verificación de tipos (`tsc`) | Sin errores |
| Vulnerabilidades en dependencias (`npm audit`) | 0 |
| Funcionamiento en navegador | Se inició sesión con un usuario de datos de prueba en un servidor local; el Dashboard muestra la ilustración AVIF; sin errores en la consola ni violaciones de la política de seguridad |
| Revisión automática del CI (`ci.yml`) | En verde en la rama `feature/green-it` |
| Revisión automática de Lighthouse CI (`green-audit.yml`) | **En verde en GitHub Actions** (ejecución 42628243459, commit `da3b873`): puntaje, FCP, LCP, TBT, CLS y peso, todos como errores, sobre la mediana de 3 mediciones en el servidor de GitHub. Guía del archivo: [Documento 02, sección 5.2](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md#52-guía-del-archivo-green-audityml-paso-a-paso) |
| Prueba de la API | [`medir_api.py`](../../../scripts/medir_api.py) (resultados en la [sección 4](#4-las-8-optimizaciones)) |
| Cálculo de carbono | [`calcular_swdm.py`](../../../scripts/calcular_swdm.py) (resultados en la [sección 6](#6-impacto-ambiental-con-el-modelo-swdm-v4)) |
| Variantes de la ilustración | [`generar_ilustracion_hero.py`](../../../scripts/generar_ilustracion_hero.py) (resultados en la [sección 4.3](#43-optimización-3-imágenes-avif-y-webp-con-picture)) |

El detalle del análisis de calidad con SonarQube está en el [Documento 03 de Sprint 3](../Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md).

---

## 8. Límites de este trabajo

Lo que **no** hicimos o **no** podemos afirmar:

1. **Solo se midió con Lighthouse la pantalla de inicio de sesión.** Dashboard, Vehículos y Pedidos piden credenciales; sus listados se evaluaron con la prueba de la API y la ilustración con la medición de pesos, no con Lighthouse.
2. **Los servidores de ANTES y DESPUÉS son distintos** (`vite preview` y FastAPI en Docker). Por eso incluimos la [tabla por etapas](#52-efecto-de-cada-etapa), que separa el efecto de cada cambio.
3. **La prueba de la API corre en un solo programa, con una base en memoria.** Mide empaquetado y compresión, no la red ni PostgreSQL. Con 1 000 filas no muestra mejora de tiempo en las consultas ([4.1](#41-optimización-1-consultas-livianas-e-índices)).
4. **La ilustración la generamos nosotros por código**; no es una fotografía. Con una fotografía, las proporciones de ahorro de cada formato pueden ser distintas.
5. **Usamos 494 g/kWh, el promedio mundial.** La electricidad del Perú tiene otro valor, pero no contamos con una fuente verificada para usarlo.
6. **Lighthouse varía entre mediciones**, sobre todo el TBT. Por eso el estado final se midió 8 veces y se informa el rango, incluida la medición que superó el límite.
7. **El perfil móvil de Lighthouse es una simulación** (red y procesador limitados por software), no un celular real.

---

## 9. Documentos relacionados

| Documento | Relación |
|---|---|
| [02 Estándares de ingeniería de software](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md) | Normas que respaldan cada optimización, reglas de desarrollo verde y guía del archivo de automatización |
| [04 Seguridad OWASP (Sprint 3)](../Sprint%2003/04%20OWASP%20V_1_0_0.md) | Política de seguridad (CSP) y cabeceras |
| [03 Calidad de código (Sprint 3)](../Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) | Análisis con SonarQube y cobertura de pruebas |
| [10 Stack tecnológico (Inicio)](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md) | Por qué usamos FastAPI y React en lugar de MERN |
| [CONTRIBUTING.md](../../../CONTRIBUTING.md) | Ramas, Pull Requests y definición de hecho |

---

## 10. Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 09/11/2026 | Primer informe Green IT: ocho optimizaciones con código ANTES y DESPUÉS, mediciones con Lighthouse y prueba propia de la API, y cálculo con SWDM v4. El 10/11/2026, antes de integrarse a `main`, se simplificó la redacción y se agregaron resumen, glosario y referencias cruzadas. |
