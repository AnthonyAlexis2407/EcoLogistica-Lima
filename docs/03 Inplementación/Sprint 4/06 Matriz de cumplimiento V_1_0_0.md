# Matriz de cumplimiento de requisitos y estándares

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis
**Sprint:** Sprint 4 (calidad, automatización, implementación final y cierre; periodo 21/10/2026 al 28/11/2026)
**Fecha de verificación:** 24/11/2026 (actualizada al corte del 28/11/2026)
**Versión del documento:** 2.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Reporte de Estado](../../04%20Cierre/01%20Reporte%20de%20Estado%20V_1_0_0.md) · [Reporte Final](../../04%20Cierre/06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md)

## Resumen

Este documento responde a una pregunta: **¿el proyecto cumple lo que se pidió?** Se revisó cada requisito funcional (RF), cada requisito no funcional (RNF), cada regla de negocio y cada estándar del curso contra el código, las pruebas y los informes. Cada fila indica el estado, la evidencia que se puede abrir y, cuando falta algo, qué falta.

| Grupo | Total | ✅ Cumple | 🟡 Parcial | ❌ No implementado |
|---|---|---|---|---|
| Requisitos funcionales (RF) | 10 | 10 | 0 | 0 |
| Requisitos no funcionales (RNF) | 10 | 8 | 2 | 0 |
| Reglas de negocio (RN) | 10 | 10 | 0 | 0 |
| Estándares del curso | 5 | 4 | 1 | 0 |

**Cómo se verificó.** Lectura de los criterios de aceptación de los documentos [06. Requisitos funcionales](../../01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md), [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) y [09. Reglas de negocio](../../01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_0.md); ejecución de las pruebas (**175 de backend con 93,4 % de cobertura y 3 más contra PostgreSQL real en CI, 108 de frontend y {E2E} ejecuciones E2E** en tres navegadores y móvil) y revisión del código fuente.

**Efecto de la auditoría.** Al comparar el producto con los criterios se hallaron brechas en casi todos los requisitos; todas se cerraron con código y pruebas: ventanas horarias como restricción dura, volumen, zonas protegidas, Pico y Placa, factor de CO₂ obligatorio, registro de accesos denegados, ciclo de vida de la ruta y cierre "Completada", app del conductor con evidencia y modo sin conexión, incidencias con re-optimización, notificaciones, cifrado y anonimización de datos personales, filtros del dashboard, reportes en Excel y PDF, administración de usuarios, conductores y parámetros, caché de resultados, base de datos PostgreSQL y alta disponibilidad medida. El análisis de seguridad también halló un defecto propio, la **enumeración de usuarios en el inicio de sesión**, que se corrigió.

## 1. Requisitos funcionales

| Requisito | Estado | Evidencia | Cómo se cumple y límites |
|---|---|---|---|
| **RF-001** Gestión de flota vehicular | ✅ Cumple | [`vehiculos_router.py`](../../../src/backend/app/routers/vehiculos_router.py), [`test_criterios_aceptacion.py`](../../../src/backend/tests/test_criterios_aceptacion.py), [`vehiculos.spec.ts`](../../../src/frontend/e2e/vehiculos.spec.ts) | Registro, edición, baja lógica, placa única, capacidad de peso y de volumen; roles verificados en tres navegadores |
| **RF-002** Gestión de pedidos | ✅ Cumple | [`pedidos_router.py`](../../../src/backend/app/routers/pedidos_router.py), [`PedidosPage.tsx`](../../../src/frontend/src/pages/PedidosPage.tsx), [`pedidos.spec.ts`](../../../src/frontend/e2e/pedidos.spec.ts) | Dirección, peso, volumen y ventana horaria; ubicación elegida en un mapa o con coordenadas; distrito asignado por cercanía; rechazo por capacidad de peso o de volumen (422); aislamiento por bodega; búsqueda sobre datos cifrados |
| **RF-003** Rutas optimizadas | ✅ Cumple | [`optimizador.py`](../../../src/backend/app/optimizador.py), [`rutas_router.py`](../../../src/backend/app/routers/rutas_router.py), [`test_optimizador.py`](../../../src/backend/tests/test_optimizador.py), [`test_rutas_api.py`](../../../src/backend/tests/test_rutas_api.py), [`rutas.spec.ts`](../../../src/frontend/e2e/rutas.spec.ts) | **Feliz:** planifica con capacidad, volumen, **ventanas horarias duras**, Pico y Placa y zonas protegidas. **Infeliz:** informa los pedidos no asignables y su motivo (peso, volumen, ventana imposible, destino dentro de una zona protegida o falta de vehículos). Un tramo que cruzaría una zona protegida se rodea. La distancia es en línea recta (no usa la red vial ni el tráfico) |
| **RF-004** Mapa interactivo | ✅ Cumple | [`RutasPage.tsx`](../../../src/frontend/src/pages/RutasPage.tsx), [`ConductorPage.tsx`](../../../src/frontend/src/pages/ConductorPage.tsx), [`conductor_router.py`](../../../src/backend/app/routers/conductor_router.py), [`conductor.spec.ts`](../../../src/frontend/e2e/conductor.spec.ts) | Mapa Leaflet con recorrido y paradas para el operador y para el conductor; la posición se compara con el trazado cada minuto y un desvío de más de 500 m recalcula la ruta; sin conexión se muestra la última ruta descargada. Cada mapa tiene su tabla equivalente en texto |
| **RF-005** Dashboard operativo y ambiental | ✅ Cumple | [`indicadores_router.py`](../../../src/backend/app/routers/indicadores_router.py), [`DashboardPage.tsx`](../../../src/frontend/src/pages/DashboardPage.tsx), [`test_admin_privacidad.py`](../../../src/backend/tests/test_admin_privacidad.py) | Kilómetros, CO₂, árboles, **combustible ahorrado**, cumplimiento de ventanas y compensación confirmada, con **filtros por distrito y por rango de fechas** (se prueba que los totales cambian con el filtro) |
| **RF-006** Reportes exportables | ✅ Cumple | [`reportes_router.py`](../../../src/backend/app/routers/reportes_router.py), [`exportar.py`](../../../src/backend/app/exportar.py), [`administracion.spec.ts`](../../../src/frontend/e2e/administracion.spec.ts) | Pedidos, rutas y ambiental en **CSV, Excel y PDF**, con filtros; protección contra inyección de fórmulas; el **auditor recibe los reportes sin direcciones ni coordenadas**; el acceso denegado se registra sin datos personales |
| **RF-007** Re-optimización dinámica | ✅ Cumple | [`servicios.py`](../../../src/backend/app/servicios.py) (`reoptimizar_ruta`), [`test_ciclo_ruta.py`](../../../src/backend/tests/test_ciclo_ruta.py) | Vía cerrada y accidente reordenan lo que falta evitando el área; una avería interrumpe la ruta, pone el vehículo en mantenimiento y redistribuye los pedidos en otros vehículos; un pedido cancelado se retira. Cada incidencia mide su tiempo (límite 45 s). Un retraso que pone en riesgo una ventana dispara el recálculo automático (RN-005) |
| **RF-008** Conductores y app de campo | ✅ Cumple | [`admin_router.py`](../../../src/backend/app/routers/admin_router.py), [`conductor_router.py`](../../../src/backend/app/routers/conductor_router.py), [`ConductorPage.tsx`](../../../src/frontend/src/pages/ConductorPage.tsx), [`conductor.spec.ts`](../../../src/frontend/e2e/conductor.spec.ts) | Alta y baja de conductores; asignación de ruta (un conductor, una ruta abierta); entrega con **firma o foto obligatoria** (RN-007), reprogramación con motivo y **sincronización sin conexión idempotente** (clave única por acción) |
| **RF-009** Portal y notificaciones a clientes | ✅ Cumple | [`servicios.py`](../../../src/backend/app/servicios.py) (`Notificador`), [`notificaciones_router.py`](../../../src/backend/app/routers/notificaciones_router.py), [`NotificacionesPage.tsx`](../../../src/frontend/src/pages/NotificacionesPage.tsx) | Avisos de asignación (con hora estimada), salida en ruta, retraso, reprogramación y entrega en el portal de la bodega, aislados por cuenta (RN-010). Sin canal de contacto, el aviso queda "no entregado" y aparece al operador como pendiente de contacto. **Límite:** el canal real es el portal; el correo funciona por SMTP si se configura (no está activado en la demostración) y el SMS no tiene proveedor |
| **RF-010** Compensación de carbono | ✅ Cumple | [`servicios.py`](../../../src/backend/app/servicios.py) (`completar_ruta`), tabla `emisiones_co2`, [`test_ciclo_ruta.py`](../../../src/backend/tests/test_ciclo_ruta.py) | Al completar la ruta se registra la emisión, el CO₂ evitado y los árboles equivalentes (21,77 kg de CO₂ por árbol al año); solo cuentan las rutas completadas (RN-009); sin factor de emisión no se planifica ni se cierra el vehículo |

## 2. Requisitos no funcionales

| Requisito | Estado | Medida (SLA) frente al resultado | Evidencia y límites |
|---|---|---|---|
| **RNF-001** Rendimiento | ✅ Cumple | ≤ 45 s (p95) frente a menos de 0,1 s con 50 pedidos y menos de 1 s con 1.000 | [`test_optimizador.py`](../../../src/backend/tests/test_optimizador.py), [`test_escalabilidad.py`](../../../src/backend/tests/test_escalabilidad.py) y la prueba E2E de RNF-001 ([Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)) |
| **RNF-002** Seguridad | ✅ Cumple | 0 vulnerabilidades altas explotables | [`test_seguridad_ofensiva.py`](../../../src/backend/tests/test_seguridad_ofensiva.py): inyección SQL, script en datos, JWT sin firma o con otra clave o vencido, rol inflado en el token, escalada de privilegios, acceso a datos ajenos, fuerza bruta, enumeración de usuarios, cuerpos desmesurados, secretos en respuestas y registro de eventos sin datos personales; HSTS, política de permisos y OWASP del [Sprint 3](../Sprint%2003/04%20OWASP%20V_1_0_0.md); Bandit, Ruff y auditoría de dependencias sin hallazgos. **Límite:** es una prueba ofensiva automática propia, no una auditoría de un tercero |
| **RNF-003** Disponibilidad | 🟡 Parcial | RTO ≤ 60 s y ≥ 99,5 % mensual | [`docker-compose.failover.yml`](../../../docker-compose.failover.yml) y [`medir_rto.py`](../../../scripts/medir_rto.py): dos instancias detrás de un balanceador; el trabajo «Conmutación por falla» de `tests.yml` detiene cada instancia y mide el RTO. `/api/health/ready` comprueba la base de datos. **Falta:** la producción gratuita de Render tiene una sola instancia, por lo que no hay conmutación allí, y la disponibilidad mensual no se midió |
| **RNF-004** Usabilidad | ✅ Cumple | ≤ 3 toques y ≤ 20 s | La prueba E2E «confirmar una entrega toma 3 toques y menos de 20 segundos» ([`conductor.spec.ts`](../../../src/frontend/e2e/conductor.spec.ts)): «Entregar», un trazo de firma y «Confirmar». El SUS de 79,4 usa datos simulados ([Usabilidad](04%20Usabilidad%20V_1_0_0.md)). **Límite:** no se midió con conductores reales |
| **RNF-005** Mantenibilidad | ✅ Cumple | Cobertura ≥ 80 % en el módulo de optimización; nueva metaheurística en ≤ 3 días-persona | `optimizador.py` con 96 % de cobertura; la búsqueda tabú se integró como un parámetro del administrador sin modificar pedidos, flota ni dashboard ([`algoritmos_alternativos.py`](../../../src/backend/app/algoritmos_alternativos.py)) |
| **RNF-006** Escalabilidad | 🟡 Parcial | Degradación ≤ 10 % con 1.000 pedidos/día | [`test_escalabilidad.py`](../../../src/backend/tests/test_escalabilidad.py): el tiempo de respuesta de la API con 1.000 pedidos no supera en más de 10 % al de 250, y 1.000 pedidos se planifican en menos de 1 s. **Falta:** el escalado automático en la nube (el plan gratuito no lo ofrece); con el balanceador de la prueba de conmutación se demuestra que la API se puede replicar |
| **RNF-007** Accesibilidad | ✅ Cumple | WCAG 2.1 AA con axe-core y revisión manual | [`accesibilidad.spec.ts`](../../../src/frontend/e2e/accesibilidad.spec.ts): axe-core sin incumplimientos WCAG 2.2 AA (A y AA) en todas las pantallas y pestañas, el diálogo de pedido con **foco atrapado**, cierre con Escape y retorno del foco, y menú operable con teclado. **Límite:** no se probó con un lector de pantalla |
| **RNF-008** Seguridad de datos | ✅ Cumple | 100 % de campos personales cifrados; solicitud atendida en ≤ 5 días hábiles | [`cifrado.py`](../../../src/backend/app/cifrado.py) y [Documento 11, sección 6](../../01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md): AES-SIV en nombre, correo, teléfono, licencia, direcciones, coordenadas y evidencia; las pruebas leen la base en bruto y comprueban que no hay datos en claro. Las solicitudes tienen un plazo de 5 días hábiles y una anonimización probada. TLS lo ofrece la plataforma y se refuerza con HSTS |
| **RNF-009** Eficiencia energética | ✅ Cumple | ≥ 30 % menos de ciclos de CPU con caché | `test_la_cache_reduce_al_menos_30_por_ciento_la_cpu_de_una_corrida_repetida`: una corrida repetida usa muy por debajo del 70 % de la CPU. La caché vive en el proceso (no es Redis); más Green IT en el [Informe](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) |
| **RNF-010** Portabilidad | ✅ Cumple | Funcional sin conexión; sincronización en ≤ 5 min | [`pwa.spec.ts`](../../../src/frontend/e2e/pwa.spec.ts) y [`conductor.spec.ts`](../../../src/frontend/e2e/conductor.spec.ts): manifiesto instalable, service worker con precarga, reapertura sin red, entrega guardada sin conexión y sincronizada al volver la señal (inmediatamente y cada 30 s). **Límite:** no se probó en un dispositivo físico de gama baja; el móvil se emula con un Pixel 7 |

## 3. Reglas de negocio

| Regla | Estado | Dónde se cumple y se prueba |
|---|---|---|
| **RN-001** Bloqueo por intentos fallidos | ✅ | [`auth.py`](../../../src/backend/app/auth.py); `test_la_fuerza_bruta_bloquea_la_cuenta`; E2E de autenticación |
| **RN-002** Pico y Placa | ✅ | `vehiculos_aptos` en [`servicios.py`](../../../src/backend/app/servicios.py); `test_vehiculo_restringido_por_pico_y_placa_*` |
| **RN-003** Zonas protegidas | ✅ | Matriz de distancias con rodeo en [`optimizador.py`](../../../src/backend/app/optimizador.py); administración de zonas; pruebas de zona en el optimizador y la API |
| **RN-004** Capacidad de peso y volumen | ✅ | Restricción dura en la construcción y la mejora de rutas; `test_el_volumen_es_restriccion_dura` |
| **RN-005** Re-optimización por riesgo de ventana | ✅ | `_entregar` en [`conductor_router.py`](../../../src/backend/app/routers/conductor_router.py); `test_un_retraso_que_rompe_ventanas_dispara_la_reoptimizacion_automatica` |
| **RN-006** CO₂ por tipo de combustible | ✅ | Factores por combustible y por vehículo en `optimizador.py` |
| **RN-007** Entrega con evidencia | ✅ | 422 sin firma ni foto; botón «Confirmar» deshabilitado; `test_la_entrega_exige_evidencia` |
| **RN-008** Cifrado y eliminación de datos personales | ✅ | [`cifrado.py`](../../../src/backend/app/cifrado.py) y [`admin_router.py`](../../../src/backend/app/routers/admin_router.py) (anonimización) |
| **RN-009** Compensación solo de rutas completadas | ✅ | `completar_ruta`; `test_la_compensacion_solo_cuenta_rutas_completadas` |
| **RN-010** Aislamiento por bodega | ✅ | Pedidos, notificaciones y avisos filtrados por cuenta; pruebas de acceso ajeno |

## 4. Estándares del curso

| Estándar | Estado | Cómo se aplicó | Evidencia |
|---|---|---|---|
| **W3C** (HTML, CSS y Web Sustainability Guidelines) | 🟡 Parcial | HTML semántico, hojas de estilo y buenas prácticas de sostenibilidad web | [Estándares de ingeniería de software](../reduccion%20del%20impacto%20ambiental/02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md). No se ejecutó el validador de marcado de W3C |
| **ISO/IEC 25010** (calidad del producto) | ✅ Cumple | Las ocho características se asignaron a requisitos y a evidencia: adecuación funcional (RF), eficiencia (RNF-001/006/009), compatibilidad (tres motores de navegador), usabilidad (RNF-004/007), fiabilidad (RNF-003), seguridad (RNF-002/008), mantenibilidad (RNF-005) y portabilidad (RNF-010) | [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) y esta matriz |
| **OWASP Top 10** | ✅ Cumple | Evaluación versión 2025 con correcciones y la suite ofensiva automática; sin enumeración de usuarios; HSTS | [OWASP del Sprint 3](../Sprint%2003/04%20OWASP%20V_1_0_0.md) y `test_seguridad_ofensiva.py` |
| **Green Software** | ✅ Cumple | Medición con Lighthouse y SWDM v4; optimizaciones con antes y después; caché de planes; CO₂ evitado por el optimizador | [Informe Green IT](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) y flujo `green-audit.yml` |
| **WCAG** | ✅ Cumple | WCAG 2.2 AA con axe-core en todas las pantallas, foco atrapado y operación con teclado | `accesibilidad.spec.ts` y [WCAG del Sprint 3](../Sprint%2003/05%20WCAG%20V_1_0_0.md). Falta la prueba con lector de pantalla |

## 5. Restricciones realistas y gestión de cambios

| Aspecto | Cómo se atendió |
|---|---|
| **Costo del ciclo de vida** | Presupuesto por roles y licencias ([Documento 04 de Planificación](../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)); EVM con proyección al cierre ([Reporte de EVM](../../04%20Cierre/03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md)); la base PostgreSQL gratuita de Render caduca a los 30 días y pasa a un plan de pago para operar |
| **Cero carbono neto** | El planificador mide el CO₂ por ruta, el evitado y su equivalente en árboles; solo se compensa lo completado; la aplicación aplica prácticas de Green IT |
| **Salud y seguridad pública / ética** | Control de acceso por rol, datos personales cifrados y anonimizables (Ley N.° 29733) y auditoría de accesos denegados sin datos personales; zonas protegidas que ninguna ruta atraviesa |
| **Gestión de cambios** | Cambios de alcance y su efecto en el cronograma y el costo en el [Reporte de Variación](../../04%20Cierre/02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md); versiones de los documentos con su historial de cambios |

## 6. Límites que quedan abiertos

| Límite | Requisito | Qué haría falta |
|---|---|---|
| Conmutación por falla y escalado automático en producción | RNF-003, RNF-006 (EN-003, EN-006) | Un plan de pago de la plataforma con varias instancias, y medición mensual de disponibilidad |
| Auditoría de seguridad de un tercero | RNF-002 | Contratar una prueba de penetración externa |
| Prueba con lector de pantalla y con conductores reales en un Android de gama baja | RNF-007, RNF-004, RNF-010 | Sesiones con NVDA o VoiceOver y con usuarios finales |
| SUS con usuarios reales (los datos actuales son simulados) | RNF-004 | Aplicar el cuestionario a al menos cinco usuarios |
| Validador de marcado de W3C | Estándar W3C | Ejecutarlo sobre las páginas compiladas |
| Correo y SMS reales | RF-009 | Contratar un proveedor de SMS y configurar SMTP (el modo del portal ya funciona) |

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 24/11/2026 | Primera matriz de cumplimiento: 10 RF, 10 RNF y 5 estándares verificados contra el código, las pruebas y los informes. |
| 2.0.0 | 28/11/2026 | Se actualiza tras la implementación final: los 10 requisitos funcionales y las 10 reglas de negocio cumplen; 8 de 10 requisitos no funcionales cumplen y 2 cumplen en pruebas pero no en la nube gratuita. Se añaden las reglas de negocio y los límites abiertos. El documento pasa a la carpeta del Sprint 4. |
