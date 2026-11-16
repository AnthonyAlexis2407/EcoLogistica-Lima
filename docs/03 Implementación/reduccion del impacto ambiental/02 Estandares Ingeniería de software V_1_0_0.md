# Estándares de Ingeniería de Software y Guía de Desarrollo Verde

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Versión del documento:** 1.0.0  
**Fecha:** 09/11/2026 (redacción simplificada y referencias cruzadas: 10/11/2026)

[← Volver al README Principal](../../../README.md) · [Documento 01: Informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md)

---

## En resumen

Este documento responde a una pregunta: **¿en qué reglas y normas nos apoyamos para mejorar el software, y cómo evitamos que esas mejoras se pierdan?** Es el compañero del [Informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md), que cuenta *qué* se mejoró y *cuánto*.

- **Tres normas internacionales** respaldan el trabajo: ISO/IEC 25010 (qué es un software de calidad), la Green Software Foundation (cómo emitir menos carbono) y las directrices web sostenibles del W3C. Ver [sección 2](#2-normas-internacionales).
- **Reglas de desarrollo verde** para el backend y el frontend, con ejemplos de nuestro propio código. Ver [sección 3](#3-guía-de-desarrollo-verde).
- **Una matriz** une cada una de las 8 optimizaciones con su norma y su prueba. Ver [sección 4](#4-matriz-de-mapeo).
- **Un archivo de automatización** (`green-audit.yml`) revisa en GitHub que el rendimiento no empeore. Ver [sección 5](#5-automatización-con-github-actions).
- **Trabajo en equipo ordenado**: ramas, Pull Requests y versiones. Ver [sección 6](#6-versiones-y-trabajo-en-equipo).

## Cómo leer este documento

| Si usted quiere... | Vaya a... |
|---|---|
| Entender las palabras técnicas | [Glosario](#glosario-las-palabras-en-simple) |
| Saber qué normas usamos | [Sección 2](#2-normas-internacionales) |
| Ver las reglas de programación | [Sección 3](#3-guía-de-desarrollo-verde) |
| Comprobar que cada mejora tiene respaldo | [Sección 4](#4-matriz-de-mapeo) |
| Entender el archivo de automatización | [Sección 5.2](#52-guía-del-archivo-green-audityml-paso-a-paso) |
| Ver cómo se versiona y se integra el trabajo | [Sección 6](#6-versiones-y-trabajo-en-equipo) |
| Ver las mediciones de cada mejora | [Informe, sección 5](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#5-resultados-antes-y-después) |

## Glosario: las palabras en simple

| Término | En simple |
|---|---|
| **ISO/IEC 25010** | Una norma internacional que describe qué características debe tener un software de buena calidad (rápido, fácil de mantener, seguro...). |
| **GSF (Green Software Foundation)** | Una organización que define cómo hacer software que consuma menos energía y emita menos carbono. |
| **W3C y WSG** | El W3C es el organismo que fija los estándares de la web. Las WSG son sus guías para hacer sitios web sostenibles. |
| **Clean Code** | "Código limpio": escribir de forma que otra persona lo entienda rápido. |
| **SOLID** | Cinco principios para ordenar el código. Aquí usamos tres: cada pieza hace una sola cosa, se amplía sin romper lo existente y depende de piezas intercambiables. |
| **DRY** | "No te repitas": cada regla se escribe en un solo lugar. |
| **YAGNI** | "No lo vas a necesitar": no se construye algo hasta que realmente haga falta. |
| **Middleware** | Una pieza que se coloca "en el camino" de cada respuesta del servidor para revisarla o completarla (por ejemplo, añadir cabeceras de seguridad). |
| **CI/CD** | Revisión y entrega automáticas: cada vez que alguien sube un cambio, un robot lo prueba. |
| **GitHub Actions** | El "robot" de GitHub que ejecuta esas revisiones automáticas. |
| **Workflow (flujo de trabajo)** | La lista de pasos que ese robot sigue. Se escribe en un archivo. |
| **YAML** | El formato de texto en que se escribe ese archivo. Usa sangrías (espacios) para organizar. |
| **LHCI (Lighthouse CI)** | Una versión automática de Lighthouse, la herramienta de Google que califica el rendimiento de una página. |
| **Rama (branch)** | Una copia de trabajo del proyecto donde se prueban cambios sin tocar la versión principal. |
| **Pull Request (PR)** | Una solicitud para incorporar los cambios de una rama a la principal; otra persona los revisa antes. |
| **Versionado semántico** | Numerar versiones como 1.0.0: el primer número cambia con rediseños grandes, el segundo con secciones nuevas y el tercero con correcciones pequeñas. |

Las palabras de rendimiento (FCP, LCP, TBT, caché, compresión...) están en el [glosario del Informe](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#glosario-las-palabras-en-simple).

---

## 1. Propósito y alcance

Este documento fundamenta las refactorizaciones del [Informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) en tres normas internacionales, define reglas de desarrollo verde para el backend y el frontend, y describe cómo la automatización y el control de versiones hacen que esas mejoras se puedan verificar.

Se aplica al stack real del proyecto: **FastAPI** (Python), **React con TypeScript** y **SQLAlchemy**. El stack se justifica en el [Documento 10 de Inicio](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md), y cómo se adaptaron las áreas del curso a él se explica en la [sección 1.1 del Informe](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#11-nuestro-stack-no-es-mern-cómo-lo-adaptamos).

---

## 2. Normas internacionales

### 2.1 ISO/IEC 25010 (calidad del software)

Esta norma divide la calidad de un software en características. Usamos dos: **eficiencia de desempeño** (qué tan rápido y liviano es) y **mantenibilidad** (qué tan fácil es cambiarlo sin romperlo).

| Característica | Subcaracterística | En simple | Cómo se aplicó | Evidencia |
|---|---|---|---|---|
| **Eficiencia de desempeño** | Comportamiento temporal | Qué tan rápido responde | Sin fuente externa que bloquea, carga por partes y compresión ([4.4](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado), [4.8](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#48-optimización-8-compresión-brotli-y-gzip)) | Primer contenido en móvil de 2,61 s a 0,67 s; listados de 5,7 ms (vehículos) y 6,5 ms (pedidos), sin pérdida de tiempo |
| | Utilización de recursos | Cuánto consume | Menos bytes y peticiones; consultas sin crear objetos de más ([4.1](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#41-optimización-1-consultas-livianas-e-índices)) | Peso de 105 397 B a 68 966 B; peticiones de 7 a 3 |
| | Capacidad | Si aguanta crecer | Paginación de 12 filas e índices: la respuesta no crece con la tabla ([4.2](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#42-optimización-2-paginación)) | Listados de 8 601 B y 18 001 B a 446 B y 555 B |
| **Mantenibilidad** | Modularidad | Piezas independientes | Pantallas cargadas por separado; política HTTP aislada en [`rendimiento.py`](../../../src/backend/app/rendimiento.py) | Un archivo por pantalla; paquete `vendor` separado |
| | Reusabilidad | Piezas que se reutilizan | `Paginador`, `useDebounced` y `patron_like` se usan en dos listados | Dos usos de cada uno |
| | Analizabilidad | Fácil de entender | Dependencias reducidas a 4 y recursos sin uso eliminados ([4.5](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#45-optimización-5-dependencias-y-recursos-de-terceros)) | `npm ls`: 4 dependencias de producción |
| | Capacidad de ser probado | Fácil de verificar | Cada optimización tiene una prueba automática ([Informe, sección 7](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#7-pruebas-y-evidencias)) | 52 pruebas del backend y 70 del frontend |
| | Capacidad de ser modificado | Fácil de cambiar | Caché y compresión en un solo punto, no repartidas por cada ruta | `app.middleware("http")(politica_http)` en [`main.py`](../../../src/backend/app/main.py) |

### 2.2 Green Software Foundation (GSF)

La GSF resume la sostenibilidad del software en principios. Aplicamos cuatro:

| Principio | En simple | Cómo lo aplicamos | Estado |
|---|---|---|---|
| **Eficiencia de carbono** | Emitir lo mínimo por cada tarea | Menos bytes por carga: de 15,62 mg a 10,22 mg de CO2e ([Informe, 6.2](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#62-cálculo-por-carga-inicial)); la ilustración AVIF emite 80,1 % menos que su PNG | Aplicado y medido |
| **Eficiencia energética** | Gastar la menor energía por tarea | Paginación, compresión y caché evitan transferir y calcular lo mismo una y otra vez | Aplicado y medido |
| **Eficiencia de hardware** | Usar equipos de forma ligera | Menos JavaScript al inicio (el dispositivo del usuario es el 53,7 % del carbono de una carga); fuente del sistema en lugar de descargar una | Aplicado; el ahorro de procesador del dispositivo no se midió |
| **Conciencia del carbono** | Trabajar más cuando la electricidad es más limpia | **No se implementó**: hoy no hay tareas que se puedan posponer. Se prevé para el motor de optimización de rutas (EN-001), cuyos cálculos pesados podrían programarse en horas de menor intensidad | Propuesto, no aplicado |

La GSF tiene otros principios (medición, compromisos climáticos, carbono incorporado y modelado de la demanda). Aquí se aplica la **medición**: el modelo SWDM v4 del [Informe, sección 6](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#6-impacto-ambiental-con-el-modelo-swdm-v4), que da 10,22 mg de CO2e por carga inicial (equivale a la "intensidad de carbono del software" de la GSF, tomando una carga como unidad).

### 2.3 W3C Web Sustainability Guidelines (WSG)

Son las guías del W3C para sitios web sostenibles. Usamos la versión de borrador del 16/10/2026 ([www.w3.org/TR/web-sustainability-guidelines](https://www.w3.org/TR/web-sustainability-guidelines/)). Es un borrador, no una recomendación final. Estas son las directrices usadas, con su número y título oficiales:

| Directriz | Título oficial (en inglés) | En simple | Optimización |
|---|---|---|---|
| 2.9 | Optimize media to reduce resource use | Optimizar imágenes y videos | [3](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#43-optimización-3-imágenes-avif-y-webp-con-picture) |
| 2.11 | Use optimized web typography | Usar tipografías livianas | [5](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#45-optimización-5-dependencias-y-recursos-de-terceros) |
| 3.3 | Modularize bandwidth-heavy components | Dividir lo pesado en partes | [4](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado) |
| 3.5 | Treat third parties the same as first parties | Revisar lo de terceros con el mismo rigor que lo propio | [5](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#45-optimización-5-dependencias-y-recursos-de-terceros) |
| 3.7 | Defer the loading of non-critical resources | Cargar después lo que no es urgente | [4](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado) |
| 3.12 | Use dependencies sparingly and maintain them | Usar pocas librerías y mantenerlas | [5](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#45-optimización-5-dependencias-y-recursos-de-terceros) |
| 3.16 | Reduce the number and complexity of database queries | Hacer menos y más simples consultas a la base de datos | [1](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#41-optimización-1-consultas-livianas-e-índices) |
| 4.2 | Optimize caching and support offline access | Aprovechar la caché | [7](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#47-optimización-7-caché) |
| 4.3 | Reduce data transfer with compression | Transferir menos datos con compresión | [2](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#42-optimización-2-paginación), [6](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#46-optimización-6-menos-peticiones-con-elementos-incrustados) y [8](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#48-optimización-8-compresión-brotli-y-gzip) |

**Equivalencia con las pautas que cita la rúbrica.** La rúbrica menciona las pautas 1.2, 2.4 y 3.1. En la versión del documento W3C que consultamos, la numeración es otra. Por eso la equivalencia se establece **por tema, no por número**:

| Pauta de la rúbrica | Tema | Directriz equivalente en el WSG consultado |
|---|---|---|
| 1.2 | Optimización de imágenes y formatos modernos | 2.9 |
| 2.4 | Caché determinista e inmutable | 4.2 |
| 3.1 | Compresión y reducción de datos | 4.3 |

---

## 3. Guía de desarrollo verde

### 3.1 Principios de diseño

| Principio | En simple | Cómo se ve en nuestro código |
|---|---|---|
| **Clean Code** | Nombres claros, funciones cortas, comentarios que explican el *porqué* | [`patron_like`](../../../src/backend/app/consultas.py), [`montar_frontend`](../../../src/backend/app/rendimiento.py), [`useDebounced`](../../../src/frontend/src/useDebounced.ts) |
| **SOLID: una sola responsabilidad** | Cada pieza hace una cosa | `rendimiento.py` solo trata caché, ETag y cabeceras; [`Paginador`](../../../src/frontend/src/components/Paginador.tsx) solo dibuja la navegación |
| **SOLID: abierto/cerrado** | Se amplía sin tocar lo que ya funciona | La política HTTP se añade como *middleware* sin modificar las rutas |
| **SOLID: inversión de dependencias** | Depender de piezas intercambiables | Las rutas reciben la sesión y el rol con `Depends(...)`; las pruebas los reemplazan |
| **DRY** | Cada regla en un solo lugar | `patron_like` protege la búsqueda de vehículos y pedidos; `PAGE_SIZE = 12` está definido una vez en [`api.ts`](../../../src/frontend/src/api.ts) |
| **YAGNI** | No construir lo que aún no se usa | No se agregó React Query ni un componente genérico de imagen: la ilustración usa `picture` directamente porque hay un solo uso ([Informe 4.3](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#43-optimización-3-imágenes-avif-y-webp-con-picture) y [4.7](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#47-optimización-7-caché)) |

### 3.2 Reglas para el backend

*(FastAPI y SQLAlchemy. Entre paréntesis, la directriz WSG de la [sección 2.3](#23-w3c-web-sustainability-guidelines-wsg) que respalda la regla.)*

1. Los listados **piden solo las columnas necesarias** y devuelven filas simples, sin crear objetos de más (WSG 3.16). Ver [Informe 4.1](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#41-optimización-1-consultas-livianas-e-índices).
2. Todo listado es **paginado** (`page` y `limit`, máximo 50) y dice el total en la cabecera `X-Total-Count` (WSG 4.3). Ver [Informe 4.2](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#42-optimización-2-paginación).
3. Toda columna usada para filtrar u ordenar un listado tiene un **índice**; se comprueba con `EXPLAIN QUERY PLAN` (WSG 3.16).
4. Las búsquedas de texto **escapan los comodines** de `LIKE` con `patron_like` (así `%` se busca como texto).
5. Las respuestas de 1 000 B o más se **comprimen** con Brotli o Gzip (WSG 4.3). Ver [Informe 4.8](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#48-optimización-8-compresión-brotli-y-gzip).
6. Los datos de lectura llevan **ETag** y `Cache-Control: private, no-cache`; la sesión y el estado en vivo, `no-store` (WSG 4.2). Ver [Informe 4.7](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#47-optimización-7-caché).
7. Los archivos con huella en el nombre se sirven con `Cache-Control: public, max-age=31536000, immutable`; el `index.html`, con `no-cache` (WSG 4.2).
8. Se prefiere **lo que ya trae Python** a una librería nueva; toda librería nueva se justifica por escrito en el Pull Request (WSG 3.12).

### 3.3 Reglas para el frontend

*(React, TypeScript y Vite.)*

1. Las pantallas que no son la de entrada se cargan **bajo demanda** con `React.lazy` y `Suspense` (WSG 3.7). Ver [Informe 4.4](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado).
2. Las librerías que casi no cambian van en un paquete aparte (`manualChunks`) para aprovechar la caché entre versiones (WSG 4.2).
3. **Sin fuentes ni hojas de estilo de terceros**: se usa la tipografía del sistema (WSG 2.11 y 3.5). Ver [Informe 4.5](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#45-optimización-5-dependencias-y-recursos-de-terceros).
4. **Sin archivos sin uso** en `public/` ni `src/assets/`: todo archivo enviado debe estar referenciado (WSG 3.2).
5. Una imagen solo se agrega si cumple esto: formato AVIF o WebP **medido** contra el original (una prueba mostró un WebP más pesado que su PNG), anchos adaptativos con `srcSet`, `width` y `height` declarados, `alt=""` si es decorativa, `loading="lazy"` si está más abajo en la pantalla y `decoding="async"` (WSG 2.9). Se genera con [`generar_ilustracion_hero.py`](../../../scripts/generar_ilustracion_hero.py). Ver [Informe 4.3](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#43-optimización-3-imágenes-avif-y-webp-con-picture).
6. El HTML trae los estilos incrustados y el JavaScript de la aplicación se pide **después del primer pintado**; los scripts en línea se autorizan en la política de seguridad (CSP) por su huella SHA-256, nunca con `'unsafe-inline'` (WSG 3.7). Ver [Informe 4.4](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado) y la [auditoría OWASP](../Sprint%2003/04%20OWASP%20V_1_0_0.md).
7. Los íconos se usan como **SVG en línea**, y los recursos pequeños y críticos se incrustan (`data:`) para ahorrar peticiones.
8. Los buscadores esperan **300 ms** después de la última tecla antes de consultar al servidor (*debounce*).
9. Antes de agregar una librería se **mide su peso** (Bundlephobia o `vite build`) y se compara con lo que ya ofrece el navegador (`Intl`, `fetch`, `URLSearchParams`).

---

## 4. Matriz de mapeo

Cada fila une una optimización con su norma y su evidencia. Si una mejora no apareciera aquí, no tendría respaldo; las 8 están.

| # | Optimización (detalle en el Informe) | ISO/IEC 25010 | Principio GSF | Directriz WSG | Evidencia |
|---|---|---|---|---|---|
| 1 | [Consultas livianas e índices](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#41-optimización-1-consultas-livianas-e-índices) | Eficiencia: utilización de recursos | Eficiencia de hardware | 3.16 | `EXPLAIN QUERY PLAN`; prueba `test_listado_de_vehiculos_filtra_por_busqueda_y_estado` |
| 2 | [Paginación de 12 filas](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#42-optimización-2-paginación) | Eficiencia: capacidad | Eficiencia energética | 4.3 | 8 601 B a 446 B; pruebas de `Paginador` y de listados |
| 3 | [Imágenes con `picture`](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#43-optimización-3-imágenes-avif-y-webp-con-picture) | Eficiencia: utilización de recursos | Eficiencia de carbono | 2.9 | 560 px: PNG 39 905 B, WebP 15 164 B (−62,0 %), AVIF 7 958 B (−80,1 %); 40 470 B de archivos eliminados; prueba de `picture` |
| 4 | [Carga diferida y arranque tras el primer pintado](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#44-optimización-4-carga-diferida-y-arranque-tras-el-primer-pintado) | Mantenibilidad: modularidad | Eficiencia de hardware | 3.7 y 3.3 | Paquetes por pantalla; primer contenido de 2,61 s a 0,67 s en 8 de 8 corridas |
| 5 | [Menos terceros y librerías](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#45-optimización-5-dependencias-y-recursos-de-terceros) | Mantenibilidad: analizabilidad | Eficiencia energética | 3.12, 3.5 y 2.11 | 2 peticiones de terceros menos; 4 dependencias de producción |
| 6 | [Menos peticiones](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#46-optimización-6-menos-peticiones-con-elementos-incrustados) | Eficiencia: comportamiento temporal | Eficiencia de carbono | 4.3 | Peticiones de 7 a 3 |
| 7 | [Caché](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#47-optimización-7-caché) | Eficiencia: comportamiento temporal | Eficiencia energética | 4.2 | Respuesta 304 sin cuerpo; pruebas de ETag |
| 8 | [Compresión](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#48-optimización-8-compresión-brotli-y-gzip) | Eficiencia: capacidad | Eficiencia de carbono | 4.3 | 84 % a 91 % menos bytes en los listados |

---

## 5. Automatización con GitHub Actions

**La idea.** Una mejora que nadie vigila se pierde con el tiempo. Por eso un "robot" de GitHub revisa el rendimiento cada vez que alguien sube un cambio. Si el rendimiento empeora más allá de los límites, el robot lo marca como fallo.

### 5.1 Los archivos del repositorio

| Archivo | Para qué sirve |
|---|---|
| [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) | Prueba el backend (cobertura mínima de 80 %), verifica tipos, prueba y compila el frontend, revisa las dependencias y **verifica que los enlaces y referencias cruzadas de la documentación sigan vivos** ([`verificar_enlaces.py`](../../../scripts/verificar_enlaces.py)) |
| [`.github/workflows/green-audit.yml`](../../../.github/workflows/green-audit.yml) | **Auditoría Green IT:** ejecuta Lighthouse CI sobre la aplicación servida por FastAPI |
| [`lighthouserc.json`](../../../lighthouserc.json) | Los límites de la auditoría (ver [5.2](#52-guía-del-archivo-green-audityml-paso-a-paso)) |
| [`.github/pull_request_template.md`](../../../.github/pull_request_template.md) | Plantilla que se completa al pedir una revisión ([6.3](#63-ramas-y-pull-requests)) |

### 5.2 Guía del archivo green-audit.yml paso a paso

Este es el archivo completo, tal como está en el repositorio:

```yaml
# Auditoría Green IT y rendimiento con Lighthouse CI (LHCI).
# Guía: "guía_github_actions" (permisos mínimos, versiones fijas, caché de dependencias, secretos).
name: Green IT & Performance Audit

on:
  push:
    branches: [main, develop, "feature/**", "fix/**"]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

# Principio de mínimo privilegio: el token solo lee el repositorio.
permissions:
  contents: read

concurrency:
  group: green-audit-${{ github.ref }}
  cancel-in-progress: true

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Obtener código del repositorio
        uses: actions/checkout@v4

      - name: Configurar Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
          cache-dependency-path: src/frontend/package-lock.json

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: src/backend/requirements.txt

      - name: Instalar dependencias del frontend
        working-directory: src/frontend
        run: npm ci

      - name: Compilar el frontend (mismo origen que la API)
        working-directory: src/frontend
        env:
          VITE_API_URL: ""
        run: npm run build

      - name: Instalar dependencias del backend
        run: pip install -r src/backend/requirements.txt

      - name: Ejecutar Lighthouse CI
        run: npx --yes @lhci/cli@0.14.0 autorun --config=lighthouserc.json

      - name: Publicar el reporte de auditoría
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reporte-lighthouse
          path: .lighthouseci/
          if-no-files-found: ignore
          retention-days: 14
```

**Cómo leerlo, bloque por bloque:**

| Bloque | Qué hace, en simple |
|---|---|
| `name` | El nombre que se ve en la pestaña **Actions** de GitHub. |
| `on` | **Cuándo se ejecuta:** al subir cambios a `main`, `develop`, `feature/**` o `fix/**`; al abrir o actualizar un Pull Request hacia `main` o `develop`; y a mano con un botón (`workflow_dispatch`). |
| `permissions` | El robot solo puede **leer** el repositorio. Si alguien robara su acceso, no podría modificar nada. |
| `concurrency` | Si llega un cambio nuevo en la misma rama, **cancela** la revisión anterior que ya quedó obsoleta. Ahorra energía y tiempo. |
| `jobs` y `runs-on` | Hay un solo trabajo, que corre en un servidor Linux (Ubuntu) de GitHub. |
| `actions/checkout@v4` | **Descarga** el código del repositorio al servidor. La versión está fijada. |
| `actions/setup-node@v4` | Instala Node.js 22 y guarda sus paquetes en **caché** para no bajarlos cada vez. |
| `actions/setup-python@v5` | Instala Python 3.12, también con caché. |
| `npm ci` | Instala las librerías del frontend exactamente como indica su archivo de bloqueo. |
| `npm run build` con `VITE_API_URL: ""` | **Compila** el frontend para que la propia API lo entregue (mismo origen). |
| `pip install` | Instala las librerías del backend. |
| `npx ... lhci ... autorun` | **El paso central.** Arranca el servidor, abre la página en Chrome tres veces y compara los resultados con los límites. La versión de la herramienta (`0.14.0`) está fijada. |
| `actions/upload-artifact@v4` con `if: always()` | Guarda el reporte completo **aunque la revisión falle**, para poder estudiarlo. |

**El archivo [`lighthouserc.json`](../../../lighthouserc.json)** contiene los límites. Todos son **errores**: si uno falla, la revisión falla.

| Clave | Qué hace |
|---|---|
| `startServerCommand` | El comando que arranca la API para auditarla. |
| `startServerReadyPattern` | El texto que indica que el servidor ya está listo (`Application startup complete`). |
| `numberOfRuns: 3` | Se mide tres veces; se usa la **mediana** (el valor del medio) para reducir el ruido. |
| `categories:performance` | Puntaje de rendimiento de 0,9 (90) o más. |
| `first-contentful-paint` | Primer contenido en 1 000 ms o menos. |
| `largest-contentful-paint` | Contenido más grande en 1 400 ms o menos. |
| `total-blocking-time` | Bloqueo total de 85 ms o menos. |
| `cumulative-layout-shift` | Saltos de diseño de 0,02 o menos. |
| `total-byte-weight` | Peso de 1 153 434 bytes (1,1 MB) o menos. |
| `upload` | Guarda el reporte en la carpeta `.lighthouseci`. |

A diferencia de la plantilla de referencia, **no usamos `|| true`**: esa instrucción habría ocultado los fallos y la revisión nunca fallaría.

**Reglas de escritura del YAML:** 2 espacios por nivel y nunca tabuladores; las claves distinguen mayúsculas de minúsculas; el archivo va en `.github/workflows/` con extensión `.yml`.

**Cómo ver el resultado:** en GitHub, pestaña **Actions**, flujo *Green IT & Performance Audit*. Una marca verde significa que se cumplieron todos los límites. Con los límites ya como errores, el flujo pasó en el servidor de GitHub (ejecución 42628243459). Los valores que obtuvimos en nuestro equipo están en el [Informe, sección 5.1](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md#51-resultado-final-frente-a-los-límites-de-referencia).

### 5.3 Buenas prácticas aplicadas

Siguen la *guía de GitHub Actions* del curso:

| Práctica | En simple | Cómo la aplicamos |
|---|---|---|
| Permisos mínimos | Dar al robot solo lo que necesita | `permissions: contents: read` en ambos flujos |
| Versiones fijas | Que un cambio ajeno no rompa el flujo | `checkout@v4`, `setup-node@v4`, `setup-python@v5` y `@lhci/cli@0.14.0` |
| Caché de dependencias | No descargar lo mismo en cada ejecución | `cache: npm` y `cache: pip` |
| Disparo manual | Poder ejecutarlo cuando se quiera | `workflow_dispatch` |
| Control de concurrencia | No gastar en revisiones obsoletas | `concurrency` con `cancel-in-progress` |
| Secretos | Nunca escribir claves en el código | Ningún flujo usa claves. Si hicieran falta, se guardan en *Settings, Secrets and variables, Actions* y se leen con `${{ secrets.NOMBRE }}` |
| Ruta y sintaxis | El archivo debe estar donde GitHub lo busca | `.github/workflows/`, sangría de 2 espacios y sin tabuladores |

---

## 6. Versiones y trabajo en equipo

### 6.1 Estructura de carpetas

```text
docs/03 Implementación/
  Sprint 01/ · Sprint 02/ · Sprint 03/
  reduccion del impacto ambiental/
    01 Informe de reduccion del impacto ambiental V_1_0_0.md
    02 Estandares Ingeniería de software V_1_0_0.md
```

### 6.2 Versionado semántico

Los documentos nacen en la versión **1.0.0** (por eso `V_1_0_0` va en el nombre del archivo). La versión vigente se lee en el encabezado y en el [control de versiones](#8-control-de-versiones) de cada documento. La regla: una corrección pequeña sube el último número (1.0.1), una sección nueva sube el del medio (1.1.0) y un rediseño completo sube el primero (2.0.0). Al integrar el trabajo se crea la etiqueta `green-it-v1.0.0`.

### 6.3 Ramas y Pull Requests

La rama `main` está **protegida**: no se puede subir directamente; exige un Pull Request, una aprobación y que las revisiones automáticas estén en verde. Es lo que indica la *guía de Pull Requests* y lo que describe [CONTRIBUTING.md](../../../CONTRIBUTING.md). Esta es la secuencia que usamos:

```bash
git checkout -b feature/green-it
mkdir -p "docs/03 Implementación/reduccion del impacto ambiental"
# se guardan en esa carpeta los dos documentos con sus nombres exactos
git add "docs/03 Implementación/reduccion del impacto ambiental/"
git commit -m "docs(green-it): add environmental impact report and software engineering standards"
git push -u origin feature/green-it
```

En palabras simples: se crea una **rama** de trabajo, se prepara la carpeta, se **agrega** (`git add`) lo nuevo, se **registra** (`git commit`) con un mensaje claro y se **sube** (`git push`) a GitHub.

Después, en GitHub se abre el Pull Request de `feature/green-it` hacia `main` usando la [plantilla](../../../.github/pull_request_template.md). Un compañero lo revisa y elige una de tres respuestas: *Comment* (comenta), *Request changes* (pide cambios) o *Approve* (aprueba). Con la aprobación y el robot en verde se integra con *Squash and merge*. Luego se limpia el entorno local:

```bash
git checkout main
git pull origin main
git branch -d feature/green-it
```

**Diferencia con la plantilla de referencia.** Esa plantilla termina con `git push origin main`. Con `main` protegida eso ya no corresponde: el cambio llega por Pull Request.

---

## 7. Documentos relacionados

| Documento | Relación |
|---|---|
| [01 Informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) | Qué se mejoró, cuánto y cómo se midió |
| [04 Seguridad OWASP (Sprint 3)](../Sprint%2003/04%20OWASP%20V_1_0_0.md) | Cabeceras de seguridad y política CSP |
| [03 Calidad de código (Sprint 3)](../Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) | Análisis de calidad con SonarQube y cobertura |
| [10 Stack tecnológico (Inicio)](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md) | Por qué usamos FastAPI y React |
| [CONTRIBUTING.md](../../../CONTRIBUTING.md) | Flujo de ramas, Pull Requests y definición de hecho |

---

## 8. Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 09/11/2026 | Primera versión: normas ISO/IEC 25010, GSF y W3C WSG, guía de desarrollo verde, matriz de mapeo de las 8 optimizaciones, flujos de CI/CD y gestión de versiones. El 10/11/2026, antes de integrarse a `main`, se simplificó la redacción y se agregaron glosario, guía del YAML paso a paso y referencias cruzadas. |
