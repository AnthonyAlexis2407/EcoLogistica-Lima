# Matriz de cumplimiento de requisitos y estándares

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis
**Sprint:** Sprint 5 (cierre; periodo 17/11/2026 al 28/11/2026)
**Fecha de verificación:** 24/11/2026 (actualizada al corte del 28/11/2026)
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Reporte de Estado](../../04%20Cierre/01%20Reporte%20de%20Estado%20V_1_0_0.md) · [Reporte Final](../../04%20Cierre/06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md)

## Resumen

Este documento responde a una pregunta: **¿el proyecto cumple lo que se pidió?** Se revisó cada requisito funcional (RF), cada requisito no funcional (RNF) y cada estándar del curso contra el código, las pruebas y los informes. Cada fila indica el estado, la evidencia que se puede abrir y, cuando falta algo, qué falta y qué se hará.

| Grupo | Total | ✅ Cumple | 🟡 Parcial | ❌ No implementado |
|---|---|---|---|---|
| Requisitos funcionales (RF) | 10 | 3 | 4 | 3 |
| Requisitos no funcionales (RNF) | 10 | 2 | 6 | 2 |
| Estándares del curso | 5 | 2 | 3 | 0 |

**Cómo se verificó.** Lectura de los criterios de aceptación de los documentos [06. Requisitos funcionales](../../01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md) y [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md), ejecución de las pruebas (96 de backend con 94,1 % de cobertura, 81 de frontend y 152 ejecuciones E2E en tres navegadores y móvil) y revisión del código fuente. **Efecto de la auditoría:** se detectaron 7 brechas frente a los criterios; se cerraron 4 (Pico y Placa, ventanas imposibles, factor de CO₂ obligatorio y registro de accesos denegados) y 3 quedan abiertas (filtros del dashboard, PDF y cierre de ruta "Completada").

## 1. Requisitos funcionales

| Requisito | Estado | Evidencia | Brecha y tratamiento |
|---|---|---|---|
| **RF-001** Gestión de flota vehicular | ✅ Cumple | [`vehiculos_router.py`](../../../src/backend/app/routers/vehiculos_router.py), `test_us001_*` en [`test_criterios_aceptacion.py`](../../../src/backend/tests/test_criterios_aceptacion.py), [`vehiculos.spec.ts`](../../../src/frontend/e2e/vehiculos.spec.ts) | Registro, edición, baja lógica, placa única y roles verificados en tres navegadores |
| **RF-002** Gestión de pedidos | ✅ Cumple | [`pedidos_router.py`](../../../src/backend/app/routers/pedidos_router.py), `test_us003_*` y `test_rn010_*`, [`pedidos.spec.ts`](../../../src/frontend/e2e/pedidos.spec.ts) | Validación de capacidad (422), aislamiento por bodega (RN-010) y cancelación verificados |
| **RF-003** Rutas optimizadas | ✅ Cumple (MVP) | [`optimizador.py`](../../../src/backend/app/optimizador.py), [`rutas_router.py`](../../../src/backend/app/routers/rutas_router.py), [`test_optimizador.py`](../../../src/backend/tests/test_optimizador.py) (20 pruebas), [`test_rutas_api.py`](../../../src/backend/tests/test_rutas_api.py), [`rutas.spec.ts`](../../../src/frontend/e2e/rutas.spec.ts) | **Gold:** planifica con capacidad y Pico y Placa. **Feliz:** excluye vehículos restringidos y lo informa. **Infeliz:** informa los pedidos no asignables (peso, flota o ventana imposible). *Límite del MVP:* las ventanas horarias se **evalúan y se informan** (cada parada muestra "en ventana" o "fuera de ventana") pero no son una restricción dura de la búsqueda; la distancia es en línea recta |
| **RF-004** Mapa interactivo | 🟡 Parcial | [`RutasPage.tsx`](../../../src/frontend/src/pages/RutasPage.tsx), [`RutasPage.test.tsx`](../../../src/frontend/src/__tests__/RutasPage.test.tsx), `rutas.spec.ts` | Mapa Leaflet con recorrido y paradas numeradas para el operador y tabla equivalente en texto. **Falta:** versión para el conductor en la app móvil, seguimiento GPS y modo sin conexión (dependen de RF-008) |
| **RF-005** Dashboard operativo y ambiental | 🟡 Parcial | [`indicadores_router.py`](../../../src/backend/app/routers/indicadores_router.py), [`DashboardPage.tsx`](../../../src/frontend/src/pages/DashboardPage.tsx), `test_indicadores_*` | Muestra km, CO₂, cumplimiento de ventanas y ahorro frente a la línea base, con estado vacío explícito. **Falta:** combustible ahorrado, filtros por distrito y rango de fechas |
| **RF-006** Reportes exportables | 🟡 Parcial | [`reportes_router.py`](../../../src/backend/app/routers/reportes_router.py), `test_reporte_*` y `test_csv_*`, `rutas.spec.ts` | Tres reportes CSV (abre en Excel) en menos de 1 s, con protección contra inyección de fórmulas y registro del acceso denegado sin datos personales. **Falta:** formato PDF; los reportes incluyen la dirección de entrega de cada pedido |
| **RF-007** Re-optimización dinámica | ❌ No implementado | — | Alternativa manual: cancelar la ruta y volver a optimizar (`POST /api/rutas/{id}/cancelar`). Diferido al backlog de mantenimiento (US-006) |
| **RF-008** Conductores y app de campo | ❌ No implementado | — | Requiere la app móvil (PWA) y evidencia de entrega; diferido (US-002 y EN-010) |
| **RF-009** Portal y notificaciones a clientes | ❌ No implementado | — | La bodega ve el estado de sus pedidos (por ejemplo, ASIGNADO) en el módulo de pedidos, pero no hay notificaciones; diferido (US-004) |
| **RF-010** Compensación de carbono | 🟡 Parcial | [`optimizador.py`](../../../src/backend/app/optimizador.py), `test_emision_por_km_segun_combustible`, `test_vehiculo_sin_factor_*` | Calcula el CO₂ evitado, lo acumula, aplica el factor reducido de híbridos y eléctricos y lo traduce a árboles (21,77 kg de CO₂ por árbol al año, 48 libras, supuesto documentado en la [Visión](../../01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_0.md)). Bloquea los vehículos sin factor. **Falta:** acumular al cerrar una ruta en estado "Completada" (no existe aún el cierre por el conductor) |

## 2. Requisitos no funcionales

| Requisito | Estado | Medida (SLA) frente al resultado | Evidencia y tratamiento |
|---|---|---|---|
| **RNF-001** Rendimiento | ✅ Cumple | ≤ 45 s (p95) frente a **4 a 31 ms** con 50 pedidos y **< 1 s** con 1.000 | `test_cincuenta_pedidos_dentro_del_sla_*`, `test_mil_pedidos_*` y la prueba E2E de RNF-001 ([Análisis Playwright](../Sprint%204/03%20Analisis%20PlayWrigth%20V_1_0_0.md)) |
| **RNF-002** Seguridad | 🟡 Parcial | 0 % de vulnerabilidades altas explotables, con pentest | OWASP Top 10:2025 evaluado ([Sprint 3](../Sprint%2003/04%20OWASP%20V_1_0_0.md)); bloqueo de cuenta, RBAC, JWT, CSP y cabeceras, auditoría de accesos denegados, protección contra CSV injection. **Falta:** prueba de penetración |
| **RNF-003** Disponibilidad | 🟡 Parcial | RTO ≤ 60 s y ≥ 99,5 % mensual frente a 100 % en 30 sondeos | Comprobación de salud y despliegue verificado ([Guía de despliegue](../Sprint%204/05%20Gu%C3%ADa%20de%20despliegue.md)). **Falta:** failover y medición mensual (monitoreo por hora planificado) |
| **RNF-004** Usabilidad | 🟡 Parcial | ≤ 3 toques y ≤ 20 s con conductores | SUS 79,4 con datos simulados ([Usabilidad](../Sprint%204/04%20Usabilidad%20V_1_0_0.md)). **Falta:** medir tareas de conductores (requiere la app móvil) |
| **RNF-005** Mantenibilidad | ✅ Cumple | Cobertura ≥ 80 % en el módulo de optimización frente a **98 %** | `optimizador.py` es Python puro y desacoplado de la API y la base de datos. La integración de una nueva metaheurística en ≤ 3 días no se midió |
| **RNF-006** Escalabilidad | 🟡 Parcial | Degradación ≤ 10 % con 1.000 pedidos/día | 1.000 pedidos se planifican en < 1 s (prueba unitaria). **Falta:** medición de extremo a extremo y escalado horizontal (EN-006) |
| **RNF-007** Accesibilidad | 🟡 Parcial | WCAG 2.1 AA con axe-core y revisión manual | WCAG 2.2 AA con 0 incumplimientos en axe-core ([Sprint 3](../Sprint%2003/05%20WCAG%20V_1_0_0.md)); el mapa tiene alternativa textual, etiquetas ARIA y se verifica en móvil sin desbordamiento. **Falta:** prueba con lector de pantalla |
| **RNF-008** Seguridad de datos | ❌ No implementado | 100 % de campos personales cifrados | Solo las contraseñas están protegidas (bcrypt); sin cifrado de campos ni anonimización (EN-008, Ley N.° 29733). Diferido |
| **RNF-009** Eficiencia energética | 🟡 Parcial | ≥ 30 % menos de ciclos de CPU con caché | Green IT: compresión Brotli, caché con revalidación, FCP de 0,67 s, imagen AVIF/WebP ([Informe](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md)); CO₂ evitado por ruta. **Falta:** medir ciclos de CPU del optimizador con y sin caché |
| **RNF-010** Portabilidad | ❌ No implementado | Funcional offline y sincronización en ≤ 5 min | El panel web es adaptable y se verifica en un móvil emulado; el modo sin conexión depende de la app del conductor (EN-010). Diferido |

## 3. Estándares del curso

| Estándar | Estado | Cómo se aplicó | Evidencia |
|---|---|---|---|
| **W3C** (HTML, CSS y Web Sustainability Guidelines) | 🟡 Parcial | HTML semántico, hojas de estilo y buenas prácticas de sostenibilidad web | [Estándares de ingeniería de software](../reduccion%20del%20impacto%20ambiental/02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md). No se ejecutó el validador de marcado de W3C |
| **ISO/IEC 25010** (calidad del producto) | ✅ Cumple | Las ocho características se asignaron a requisitos y a evidencia: adecuación funcional (RF), eficiencia (RNF-001/006/009), compatibilidad (navegadores: E2E en tres motores), usabilidad (RNF-004/007), fiabilidad (RNF-003), seguridad (RNF-002/008), mantenibilidad (RNF-005) y portabilidad (RNF-010) | [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) y esta matriz |
| **OWASP Top 10** | 🟡 Parcial | Evaluación versión 2025 con correcciones: roles, bloqueo, CORS acotado, cabeceras, `/docs` oculto, CSV injection | [OWASP del Sprint 3](../Sprint%2003/04%20OWASP%20V_1_0_0.md). Falta la prueba de penetración |
| **Green Software** | ✅ Cumple | Medición con Lighthouse, SWDM v4 y optimizaciones con antes y después; CO₂ evitado por el optimizador | [Informe Green IT](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) y flujo `green-audit.yml` |
| **WCAG** | 🟡 Parcial | WCAG 2.2 AA con axe-core y diseño adaptable; la pantalla de rutas incluye alternativa textual del mapa | [WCAG del Sprint 3](../Sprint%2003/05%20WCAG%20V_1_0_0.md). Falta la prueba con lector de pantalla |

## 4. Restricciones realistas y gestión de cambios

| Aspecto | Cómo se atendió |
|---|---|
| **Costo del ciclo de vida** | Presupuesto por roles y licencias ([Documento 04 de Planificación](../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)); EVM con proyección al cierre ([Reporte de EVM](../../04%20Cierre/03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md)); mantenimiento con plan de migración a PostgreSQL y de monitoreo |
| **Cero carbono neto** | El planificador mide el CO₂ por ruta, el evitado y su equivalente en árboles; la aplicación aplica prácticas de Green IT |
| **Salud y seguridad pública / ética** | Control de acceso por rol, protección de datos personales (Ley N.° 29733) y auditoría de accesos denegados sin datos personales |
| **Gestión de cambios** | Cambios de alcance registrados en el [Reporte de Estado](../../04%20Cierre/01%20Reporte%20de%20Estado%20V_1_0_0.md) y propuesta de re-baselining en el [Reporte de EVM](../../04%20Cierre/03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md); versiones de los documentos con su historial de cambios |

## 5. Trabajo pendiente priorizado

| Prioridad | Brecha | Requisito | Tratamiento |
|---|---|---|---|
| 1 | Prueba de penetración | RNF-002 | Mantenimiento, con informe |
| 2 | Cierre de ruta en estado "Completada", filtros y PDF | RF-010, RF-005, RF-006 | Siguiente iteración |
| 3 | Cifrado de campos personales y anonimización | RNF-008 | Mantenimiento |
| 4 | App móvil del conductor, GPS y modo sin conexión | RF-008, RF-004, RNF-010 | Mantenimiento (US-002, EN-010) |
| 5 | Notificaciones y re-optimización | RF-009, RF-007 | Mantenimiento (US-004, US-006) |
| 6 | Medir usabilidad con usuarios reales y disponibilidad mensual | RNF-004, RNF-003 | Acciones 3 y 8 de la [Retrospectiva del Sprint 4](../Sprint%204/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 24/11/2026 | Primera matriz de cumplimiento: 10 RF, 10 RNF y 5 estándares verificados contra el código, las pruebas y los informes. |
