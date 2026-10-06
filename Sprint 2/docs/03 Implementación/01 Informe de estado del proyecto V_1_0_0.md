# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 2 (periodo de trabajo del 23/09/2026 al 06/10/2026, contiguo al Sprint 1 de Jira: 08/09/2026 - 22/09/2026)  
**Fecha de corte del informe:** 05/10/2026  
**Versión del documento:** 2.1.0

[← Volver al README Principal](../../README.md)

## Resumen ejecutivo

**Estado general: en riesgo de cronograma, con avance técnico verificable.** El 29/09/2026 se versionó el primer incremento de código (commits `f9887dc` y `2cb7d36`: API FastAPI, interfaz React y pruebas). Durante el Sprint 2 ese incremento se verificó contra los criterios de aceptación del backlog y se corrigieron tres defectos de seguridad encontrados en la verificación: DEF-001 (el bloqueo de cuenta no persistía), DEF-002 (una bodega podía registrar pedidos a nombre de otra) y DEF-003 (el registro público permitía autoasignarse un rol de administración). Cada uno quedó protegido por una prueba de regresión.

Base de comparación en Jira (consulta del 05/10/2026, proyecto EL): el sprint **EL Sprint 1** (tablero 2) corrió del 08/09 al 22/09/2026 con 5 ítems y 26 puntos (EL-7, EL-9, EL-17, EL-18, EL-24), pero **sigue en estado "activo" y los 5 ítems continúan "En curso"**; no existe aún un Sprint 2 en Jira. Por eso este informe reporta el trabajo del periodo contra los criterios de aceptación del Documento 01 de Planificación y no contra estados de Jira.

| Indicador al corte (05/10/2026) | Valor | Referencia | Lectura |
|---|---|---|---|
| Puntos del Sprint 1 con criterios de aceptación verificados por prueba automatizada | 8 de 26 (31 %): US-001 y US-003 | 26 pts comprometidos | Avance real, pendiente de aceptación del Product Owner |
| Pruebas automatizadas del backend | 16 pasan, ninguna marcada `xfail` | Todas en verde | Cumple |
| Cobertura de código (`app/`) | 67 % | DoD: ≥ 80 % | Brecha de 13 puntos |
| Compilación del frontend (`vite build`) | Correcta (1599 módulos) | Build sin errores | Cumple |
| Análisis estático / CI | No configurado (sin script de lint ni pipeline) | DoD: análisis estático sin vulnerabilidades críticas | Brecha |
| Historias aceptadas por el PO en Jira | 0 | - | Pendiente |
| Backlog total sin criterios verificados | 18 de 20 ítems (108 de 116 pts), incluido todo el motor de optimización | Entrega 23/11/2026 | Riesgo de cronograma (ver RSK-09) |

## Historias de Usuario completadas en este Sprint

Se considera **"completada con evidencia"** una historia cuyos escenarios Gherkin del Documento 01 de Planificación están cubiertos por pruebas automatizadas que pasan. Ninguna figura todavía como "Hecho" en Jira ni aceptada por el Product Owner.

| ID | Jira | Historia | Criterios de aceptación (Doc. 01) | Evidencia verificable | Estado al corte |
|---|---|---|---|---|---|
| US-001 | EL-7 | Registrar y administrar vehículos de la flota | Registro exitoso con placa única; rechazo de placa duplicada | `test_us001_registro_valido_y_rechazo_de_placa_duplicada` (201 y 409) y `test_us001_baja_logica_conserva_el_registro`; `vehiculos_router.py`; `VehiculosPage.tsx` | **Criterios verificados**; pendiente de aceptación del PO |
| US-003 | EL-9 | Registrar pedidos con ventana horaria y ubicación | Registro válido en estado Pendiente; rechazo por exceso de capacidad | `test_us003_pedido_valido_y_rechazo_por_exceso_de_capacidad` (201 y 422); `pedidos_router.py`; `PedidosPage.tsx` (ubicación por coordenadas) | **Criterios verificados**; pendiente de aceptación del PO. Defecto relacionado DEF-002 corregido, con prueba de regresión |
| EN-002 | EL-18 | Hardening de autenticación y protección OWASP | Bloqueo tras 3 intentos fallidos por 15 min; pentest sin hallazgos críticos | JWT, bcrypt y RBAC en `auth.py`; `test_en002_cuenta_se_bloquea_tras_tres_intentos_fallidos` pasa desde la corrección `fix(auth)` de este sprint (DEF-001); no se ejecutó pentest; el registro público ya solo admite el rol BODEGA (DEF-003 corregido) | **Parcial**: 1 de 2 criterios verificado |
| EN-008 | EL-24 | Cifrado y anonimización de datos personales | Campos personales cifrados (AES-256 / TLS 1.3); anonimización en ≤ 5 días hábiles | Solo hash bcrypt de contraseñas; TLS depende del despliegue y no está versionado; sin cifrado de campos ni anonimización | **Parcial**: criterios del enabler no verificados |
| EN-001 | EL-17 | Spike del motor de optimización dentro de 45 s | Resultados reproducibles de GA, Búsqueda Tabú y/u OR-Tools | No hay código, datos ni resultados en el repositorio | **No iniciado** (en Jira figura "En curso") |

Nota de trazabilidad: el panel de inicio de la interfaz (`DashboardPage.tsx`) muestra ✅ fijo para US-001, US-003, EN-002 y EN-008. Esta verificación respalda el ✅ solo para US-001 y US-003; EN-002 quedó verificable recién tras corregir DEF-001 y EN-008 es parcial.

## Demostración del trabajo completado

**Demostración técnica reproducible (verificación del 05/10/2026).** Cualquier integrante puede reproducirla con los comandos siguientes; los resultados reportados arriba salen de esta ejecución:

```bash
cd src/backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q --cov=app          # 16 passed; cobertura 67 %
python -m app.seed && uvicorn app.main:app --reload --port 8000

cd ../frontend && npm ci && npm run build   # compilación correcta
npm run dev                                 # http://localhost:5173
```

Guion para la revisión con stakeholders: (1) iniciar sesión con un rol del seed; (2) registrar un vehículo y reintentar la misma placa para mostrar el rechazo; (3) registrar un pedido válido y otro cuyo peso exceda la capacidad de la flota; (4) fallar tres veces el inicio de sesión y mostrar el bloqueo de 15 minutos; (5) mostrar la suite de pruebas y que una bodega no puede registrar pedidos para otra ni crear usuarios administradores desde el registro público.

**Demostración a stakeholders:** no existe acta, captura, enlace ni registro de aceptación del docente/Product Owner o del cliente ficticio DistriRápido en el repositorio ni en Jira. Por eso **no se declara realizada**; queda pendiente de agendar y documentar (IMP-003). No se atribuyen comentarios ni aprobaciones a ningún stakeholder.

## Pendientes

- **Gestión en Jira (IMP-004):** cerrar EL Sprint 1, mover lo no terminado, crear y arrancar el Sprint 2 con objetivo y alcance, y actualizar los estados con la decisión del PO. Las herramientas de API disponibles no permiten crear ni cerrar sprints; es una acción manual del líder del proyecto.
- **Aceptación del PO:** presentar US-001 y US-003 y registrar su decisión; luego pasarlas a "Hecho" en Jira.
- **EN-002:** ejecutar la revisión OWASP/pentest del criterio pendiente. **EN-008:** implementar cifrado de campos personales y el procedimiento de anonimización.
- **EN-001 (RSK-05, riesgo alto):** iniciar el spike GA vs. Búsqueda Tabú vs. OR-Tools; es la dependencia crítica de US-005 y del cronograma (IMP-010).
- **Calidad:** subir la cobertura de 67 % a ≥ 80 % (los routers están entre 35 % y 46 %), agregar lint/CI y registrar revisión por pares con Pull Requests (IMP-005, IMP-009).
- **Alineación documental:** decidir si el rol `ADMINISTRADOR` (codificado en `require_roles` y usado en `tests/test_api.py`) se elimina o se documenta; ajustar los ✅ estáticos del panel de inicio (IMP-008).
- **Propuesta para el siguiente sprint (sujeta a planificación con el PO):** spike EN-001, cierre de EN-002 (revisión OWASP) y EN-008 y arranque de US-005.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 29/09/2026 | Sprint 1: informe documental con corte al 29/09/2026 (commit `246e72d`); el avance se declaraba no verificable por falta de evidencia. |
| 2.0.0 | 05/10/2026 | Sprint 2: reescritura con evidencia verificada (pruebas, cobertura, compilación, consulta a Jira) y estado por historia; reemplaza el estado "no verificable" de la 1.0.0. |
| 2.1.0 | 05/10/2026 | Se registran como corregidos DEF-002 y DEF-003 (con pruebas de regresión); la suite pasa a 16 pruebas en verde y se retiran los pendientes asociados. |
