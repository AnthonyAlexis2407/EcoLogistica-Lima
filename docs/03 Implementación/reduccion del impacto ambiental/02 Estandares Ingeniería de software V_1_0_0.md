# Estándares de Ingeniería de Software y Guía de Desarrollo Verde

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Versión del documento:** 1.0.0  
**Fecha:** 09/11/2026

[← Volver al README Principal](../../../README.md) · [Documento 01: Informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md)

---

## 1. Propósito y alcance

Este documento fundamenta las refactorizaciones del [Informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) en tres normativas internacionales (ISO/IEC 25010, principios de la Green Software Foundation y las directrices del W3C), define reglas de desarrollo verde para el backend y el frontend, y describe el flujo de automatización y versionado que las hace verificables. Aplica al stack real del proyecto: FastAPI (Python), React con TypeScript y SQLAlchemy.

---

## 2. Estándares internacionales aplicados

### 2.1 ISO/IEC 25010 (calidad del producto de software)

| Característica | Subcaracterística | Cómo se aplicó | Evidencia |
|---|---|---|---|
| **Eficiencia de desempeño** | Comportamiento temporal | Eliminación de la fuente externa bloqueante, *code splitting* y compresión | FCP móvil de 2,61 s a 1,46 s; respuesta de listados de 5,7 ms (vehículos) y 6,5 ms (pedidos), sin pérdida de tiempo (Documento 01, secciones 4 y 5) |
| | Utilización de recursos | Menos bytes y peticiones; consultas sin hidratar entidades ORM | Peso de 105 397 B a 68 867 B; peticiones de 7 a 4 |
| | Capacidad | Paginación de 12 filas e índices: la respuesta no crece con la tabla | Listados de 8 601 B y 18 001 B a 446 B y 555 B |
| **Mantenibilidad** | Modularidad | Pantallas como módulos cargados bajo demanda; middleware de política HTTP aislado en `rendimiento.py` | Un archivo por pantalla; chunk `vendor` separado |
| | Reusabilidad | `Paginador`, `useDebounced` y `patron_like` se reutilizan en dos listados | Dos usos de cada uno |
| | Analizabilidad | Dependencias reducidas a 4 y recursos sin uso eliminados | `npm ls` con 4 dependencias de producción |
| | Capacidad de ser probado | Cada optimización tiene una prueba automatizada | 51 pruebas del backend y 69 del frontend |
| | Capacidad de ser modificado | Política de caché y compresión centralizadas en un punto, no repartidas por router | `app.middleware("http")(politica_http)` |

### 2.2 Principios de la Green Software Foundation (GSF)

| Principio GSF | Definición | Aplicación en el proyecto | Estado |
|---|---|---|---|
| **Eficiencia de carbono** | Emitir la mínima cantidad de carbono por unidad de trabajo | Menos bytes por carga: de 15,62 mg a 10,21 mg CO₂e (SWDM v4) | Aplicado y medido |
| **Eficiencia energética** | Usar la menor energía posible por unidad de trabajo | Paginación, compresión y caché HTTP evitan transferencias y cómputo repetidos | Aplicado y medido |
| **Eficiencia de hardware** | Usar el hardware (servidor y dispositivo) de la forma más ligera | Menos JavaScript ejecutado en el inicio (el segmento "dispositivos" pesa 53,7 % del carbono de una carga); fuente del sistema en lugar de descarga | Aplicado; el ahorro de CPU del dispositivo no se midió |
| **Conciencia del carbono** | Hacer más trabajo cuando la electricidad es más limpia y menos cuando es más sucia | No se implementó: el sistema no tiene tareas diferibles. Se prevé para el motor de optimización de rutas (EN-001), cuyos cálculos pesados podrían programarse en horas de menor intensidad | Propuesto, no aplicado |

La GSF define otros principios (medición, compromisos climáticos, carbono incorporado y modelado de la demanda); este proyecto aplica la **medición** con SWDM v4 y el cálculo de intensidad por carga (equivalente a la Software Carbon Intensity con una carga como unidad funcional: 10,21 mg CO₂e por carga inicial).

### 2.3 Directrices de sostenibilidad web del W3C (WSG)

Se usa el documento *Web Sustainability Guidelines (WSG)* del W3C, en su versión de borrador de nota de grupo del 16/10/2026 ([www.w3.org/TR/web-sustainability-guidelines](https://www.w3.org/TR/web-sustainability-guidelines/)). Es un borrador y no una recomendación. Las directrices usadas, con su numeración y título oficiales:

| Directriz WSG | Título oficial | Optimización relacionada |
|---|---|---|
| 2.9 | Optimize media to reduce resource use | 3 |
| 2.11 | Use optimized web typography | 5 |
| 3.3 | Modularize bandwidth-heavy components | 4 |
| 3.5 | Treat third parties the same as first parties | 5 |
| 3.7 | Defer the loading of non-critical resources | 4 |
| 3.12 | Use dependencies sparingly and maintain them | 5 |
| 3.16 | Reduce the number and complexity of database queries | 1 |
| 4.2 | Optimize caching and support offline access | 7 |
| 4.3 | Reduce data transfer with compression | 2, 6 y 8 |

**Equivalencia con las pautas citadas por la rúbrica.** La rúbrica de la asignatura menciona las pautas 1.2, 2.4 y 3.1. La numeración de la versión consultada del WSG es distinta; se establece esta equivalencia por tema, no por número:

| Pauta de la rúbrica | Tema | Directriz equivalente en el WSG consultado |
|---|---|---|
| 1.2 (optimización de medios) | Imágenes y formatos modernos | 2.9 |
| 2.4 (arquitectura y caché) | Caché determinista e inmutable | 4.2 |
| 3.1 (red y transferencia) | Compresión y reducción de datos | 4.3 |

---

## 3. Guía de desarrollo verde

### 3.1 Principios de diseño y su aplicación

| Principio | Regla en este proyecto | Ejemplo real del código |
|---|---|---|
| **Clean Code** | Nombres que dicen la intención; funciones cortas con una tarea; comentarios que explican el motivo, no el qué | `patron_like`, `montar_frontend`, `useDebounced` |
| **SOLID: responsabilidad única** | Un módulo, una razón de cambio | `rendimiento.py` solo trata caché, ETag y cabeceras; `Paginador` solo pinta la navegación |
| **SOLID: abierto/cerrado** | Ampliar con composición, no editando lo existente | La política HTTP se añade como middleware sin tocar los routers |
| **SOLID: inversión de dependencias** | Depender de abstracciones inyectadas | Los routers reciben la sesión y el rol con `Depends(...)`; las pruebas los reemplazan |
| **DRY** | Una sola fuente de cada regla | `patron_like` escapa los comodines de búsqueda para vehículos y pedidos; `PAGE_SIZE = 12` en un solo lugar |
| **YAGNI** | No construir lo que aún no se usa | No se añadió `<OptimizedPicture>` ni React Query sin necesidad medida (Documento 01, secciones 4.3 y 4.7) |

### 3.2 Normas para el backend (FastAPI, SQLAlchemy)

1. Los listados **seleccionan solo las columnas** del esquema de salida y devuelven filas planas, sin hidratar entidades ORM (WSG 3.16).
2. Todo endpoint de listado es **paginado** (`page`, `limit` con máximo 50) e informa el total en `X-Total-Count` (WSG 4.3).
3. Toda columna usada en `WHERE` u `ORDER BY` de un listado tiene **índice**; se verifica con `EXPLAIN QUERY PLAN` (WSG 3.16).
4. Las búsquedas de texto **escapan los comodines** de `LIKE` con `patron_like` (seguridad y corrección).
5. Las respuestas de 1 000 B o más se **comprimen** con Brotli o Gzip (WSG 4.3).
6. Los datos de lectura llevan **ETag** y `Cache-Control: private, no-cache`; la sesión y el estado vivo, `no-store` (WSG 4.2).
7. Los archivos con hash se sirven con `Cache-Control: public, max-age=31536000, immutable`; `index.html`, con `no-cache` (WSG 4.2).
8. Se prefiere **la biblioteca estándar** a una dependencia nueva; toda dependencia nueva se justifica por escrito en el Pull Request (WSG 3.12).

### 3.3 Normas para el frontend (React, TypeScript, Vite)

1. Las pantallas que no son la de entrada se cargan con **`React.lazy`** y `Suspense` (WSG 3.7).
2. Las librerías estables se separan en un chunk (`manualChunks`) para aprovechar la caché entre versiones (WSG 4.2).
3. **Sin fuentes ni hojas de estilos de terceros**: se usa la pila de fuentes del sistema (WSG 2.11 y 3.5).
4. **Sin recursos sin uso** en `public/` ni `src/assets/`: todo archivo enviado debe estar referenciado (WSG 3.2).
5. Una imagen raster solo se incorpora si cumple: formato AVIF o WebP **medido** frente al original, `width` y `height` declarados, `loading="lazy"` si está bajo el pliegue y `decoding="async"` (WSG 2.9).
6. Los íconos se usan como **SVG en línea**; los recursos pequeños y críticos se incrustan (`data:`) para ahorrar peticiones.
7. Los buscadores aplican **retraso (*debounce*)** de 300 ms antes de consultar al servidor.
8. Antes de agregar una librería se **mide su peso** (Bundlephobia o `vite build`) y se compara con la API nativa del navegador (`Intl`, `fetch`, `URLSearchParams`).

---

## 4. Matriz de mapeo directo: estándares y optimizaciones

| # | Optimización aplicada | ISO/IEC 25010 | Principio GSF | Directriz WSG | Evidencia |
|---|---|---|---|---|---|
| 1 | Consultas con columnas explícitas e índices | Eficiencia: utilización de recursos | Eficiencia de hardware | 3.16 | `EXPLAIN QUERY PLAN`; `test_listado_de_vehiculos_filtra_por_busqueda_y_estado` |
| 2 | Paginación de 12 filas con `X-Total-Count` | Eficiencia: capacidad | Eficiencia energética | 4.3 | 8 601 B a 446 B; pruebas de `Paginador` y de listados |
| 3 | Auditoría de imágenes (WebP/AVIF medidos) | Eficiencia: utilización de recursos | Eficiencia de carbono | 2.9 | PNG 13 057 B, WebP 13 680 B, AVIF 10 335 B; 40 470 B de recursos eliminados |
| 4 | `React.lazy`, `Suspense` y chunk `vendor` | Mantenibilidad: modularidad | Eficiencia de hardware | 3.7 y 3.3 | Chunks por pantalla en `vite build` |
| 5 | Fuente del sistema; sin librerías innecesarias | Mantenibilidad: analizabilidad | Eficiencia energética | 3.12, 3.5 y 2.11 | 2 peticiones de terceros menos; 4 dependencias de producción |
| 6 | Favicon incrustado y SVG en línea | Eficiencia: comportamiento temporal | Eficiencia de carbono | 4.3 | Peticiones de 7 a 4 |
| 7 | `Cache-Control` inmutable, ETag y 304 | Eficiencia: comportamiento temporal | Eficiencia energética | 4.2 | 304 de 534 B; pruebas de ETag |
| 8 | Compresión Brotli y Gzip | Eficiencia: capacidad | Eficiencia de carbono | 4.3 | 84 % a 91 % menos bytes en listados |

---

## 5. Automatización CI/CD verde (GitHub Actions)

### 5.1 Flujos del repositorio

| Archivo | Función |
|---|---|
| `.github/workflows/ci.yml` | Pruebas del backend con cobertura mínima de 80 %, tipos, pruebas y *build* del frontend, y auditoría de dependencias |
| `.github/workflows/green-audit.yml` | Auditoría Green IT con Lighthouse CI sobre la aplicación servida por FastAPI |
| `lighthouserc.json` | Umbrales de la auditoría: puntaje ≥ 0,9, TBT ≤ 85 ms, CLS ≤ 0,02 y peso ≤ 1,1 MB como **errores bloqueantes**; FCP ≤ 1,0 s y LCP ≤ 1,4 s como **advertencias** |
| `.github/pull_request_template.md` | Plantilla estándar de Pull Request |

El flujo `green-audit.yml`:

```yaml
name: Green IT & Performance Audit

on:
  push:
    branches: [main, develop, "feature/**", "fix/**"]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

permissions:
  contents: read

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
      - name: Compilar el frontend (mismo origen que la API)
        working-directory: src/frontend
        env:
          VITE_API_URL: ""
        run: npm ci && npm run build
      - name: Instalar dependencias del backend
        run: pip install -r src/backend/requirements.txt
      - name: Ejecutar Lighthouse CI
        run: npx --yes @lhci/cli@0.14.0 autorun --config=lighthouserc.json
```

(El archivo completo está en el repositorio; aquí se resume.) A diferencia de la plantilla de referencia, **no usa `|| true`**: si un umbral bloqueante falla, el flujo falla.

### 5.2 Buenas prácticas de la guía de GitHub Actions aplicadas

| Práctica | Aplicación |
|---|---|
| Permisos mínimos | `permissions: contents: read` en ambos flujos |
| Versiones fijas de las acciones | `actions/checkout@v4`, `setup-node@v4`, `setup-python@v5` y `@lhci/cli@0.14.0` |
| Caché de dependencias | `cache: npm` y `cache: pip` |
| Disparo manual | `workflow_dispatch` |
| Control de concurrencia | `concurrency` cancela ejecuciones obsoletas de la misma rama |
| Secretos | Ningún flujo usa secretos; no se publican credenciales. Si en el futuro se necesitaran, se guardan en *Settings, Secrets and variables, Actions* y se leen con `${{ secrets.NOMBRE }}` |
| Ruta y sintaxis | Archivos `.yml` en `.github/workflows/`, indentación de 2 espacios y sin tabuladores |

**Verificación.** El flujo `green-audit.yml` se ejecutó en GitHub y terminó en verde (ejecución 42620547976); `ci.yml` también.

---

## 6. Gestión de versiones y repositorio

### 6.1 Estructura de directorios

```text
docs/03 Implementación/
  Sprint 01/ · Sprint 02/ · Sprint 03/
  reduccion del impacto ambiental/
    01 Informe de reduccion del impacto ambiental V_1_0_0.md
    02 Estandares Ingeniería de software V_1_0_0.md
```

### 6.2 Versionado semántico

Los documentos nacen en la versión **1.0.0** (`V_1_0_0` en el nombre del archivo). El encabezado y el *Control de versiones* de cada documento registran la versión vigente: un cambio de redacción sube el parche (1.0.1), una sección nueva sube la versión menor (1.1.0) y una reestructuración sube la mayor (2.0.0). Al integrar el trabajo se crea la etiqueta anotada `green-it-v1.0.0`.

### 6.3 Flujo de trabajo con ramas y Pull Requests

Siguiendo la *guía de Pull Requests*, la rama `main` está protegida (Pull Request obligatorio, 1 aprobación y verificaciones de estado en verde) y no se hace *push* directo. Secuencia usada para este trabajo:

```bash
git checkout -b feature/green-it
mkdir -p "docs/03 Implementación/reduccion del impacto ambiental"
# se guardan en esa carpeta los dos documentos con sus nombres exactos
git add "docs/03 Implementación/reduccion del impacto ambiental/"
git commit -m "docs(green-it): add environmental impact report and software engineering standards"
git push -u origin feature/green-it
```

Después se abre el Pull Request de `feature/green-it` hacia `main`, con la plantilla de `.github/pull_request_template.md`; un compañero lo revisa (*Comment*, *Request changes* o *Approve*) y se integra con *Squash and merge* cuando el CI está en verde. Luego se actualiza la copia local y se elimina la rama:

```bash
git checkout main
git pull origin main
git branch -d feature/green-it
```

**Diferencia con la plantilla de referencia.** Esa plantilla termina con `git push origin main`. Con `main` protegida eso no corresponde: la integración se hace por Pull Request, como pide la guía de Pull Requests.

---

## 7. Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 09/11/2026 | Primera versión: normativas ISO/IEC 25010, GSF y W3C WSG, guía de desarrollo verde, matriz de mapeo de las 8 optimizaciones, flujos de CI/CD y gestión de versiones. |
