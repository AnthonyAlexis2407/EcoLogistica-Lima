# Reporte de Seguridad OWASP Top 10 (2025)

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Herramienta de Escaneo:** SonarQube Community (análisis estático) y revisión manual del código; `npm audit` para dependencias del frontend  
**Fecha de Evaluación:** 2026-10-20  
**Versión del Documento:** 1.1.0

[← Volver al README Principal](../../../README.md)

**Alcance y método.** Código de `src` (backend FastAPI y frontend React). Este informe usa la lista oficial **OWASP Top 10:2025** publicada en <https://top10.owasp.org/2025>. Dos aclaraciones sobre la plantilla de la consigna: (1) la lista 2025 reorganizó varias categorías respecto de la plantilla (por ejemplo, SSRF se integró en A01, *Vulnerable and Outdated Components* pasó a ser *Software Supply Chain Failures* y se añadió *Mishandling of Exceptional Conditions*), por eso la matriz usa los nombres oficiales de 2025; (2) SonarQube Community **no detectó ningún hotspot ni vulnerabilidad** en este código (0 y 0), así que la columna de hallazgos de Sonar queda vacía en la mayoría de filas y el estado de cada categoría se apoya en la revisión manual indicada. Ningún resultado de esta tabla sustituye una prueba de penetración, que no se ha realizado (EN-002 sigue parcial).

## 1. Matriz de Cumplimiento OWASP Top 10 2025

| Categoría OWASP 2025 | Estado en Proyecto (Limpio / Vulnerable / Bajo Revisión) | Hallazgos de SonarQube y revisión manual |
|---|---|---|
| A01:2025 - Broken Access Control (incluye SSRF) | **Bajo revisión** | Sonar: 0. Control por rol en cada endpoint con `require_roles` (Documento 08); una bodega solo lista y registra pedidos propios (DEF-002 corregido, con pruebas); el registro público solo admite el rol BODEGA (DEF-003 corregido). Hallazgos de revisión: el rol `ADMINISTRADOR`, que no existe en el Documento 08 y que `require_roles` trataba como superusuario, **se eliminó del código** (IMP-008 resuelto, con prueba de regresión); los botones de la interfaz estaban habilitados para todos los roles (`isAdmin = true`, `canCreate = true`), corregido en este sprint. SSRF: no aplica, el servidor no hace peticiones salientes. |
| A02:2025 - Security Misconfiguration | **Bajo revisión** (corregido en el código, falta el despliegue) | Sonar: 0. Corregido: `DEBUG` en `False` por defecto; la variable `ENVIRONMENT=production` rechaza el arranque con la `SECRET_KEY` por defecto y oculta `/docs`, `/redoc` y `/openapi.json`; CORS limitado a los métodos GET, POST, PUT y DELETE y a las cabeceras `Authorization` y `Content-Type`; cada respuesta lleva `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Cache-Control: no-store` (prueba `test_ruta_gold_flujo_completo_de_flota_y_pedidos`). Pendientes: CSP y HSTS (dependen del servidor TLS del despliegue); la base SQLite de desarrollo no es la de producción (PostgreSQL). |
| A03:2025 - Software Supply Chain Failures | **Bajo revisión** | `npm audit`: 6 vulnerabilidades en dependencias de desarrollo (2 críticas, 2 altas, 2 moderadas en `vite`, `vitest`, `tinypool`, `source-map-js`) y **0 en producción**. **Corregido:** `npm audit fix` y actualización de Vitest a la versión 5; ahora 0 vulnerabilidades. Pendientes: `requirements.txt` del backend usa rangos abiertos (`>=`) sin archivo de bloqueo y no se ejecutó `pip-audit`; no hay CI que repita la auditoría. |
| A04:2025 - Cryptographic Failures | **Bajo revisión** | Sonar: 0. Contraseñas con bcrypt y sal; JWT firmado con HS256 y vencimiento de 60 min. Pendientes: EN-008 sigue parcial (no hay cifrado de campos personales ni anonimización, Ley N° 29733); el token se guarda en `localStorage`; TLS depende del despliegue y no está versionado; la clave de firma por defecto es de desarrollo (ver A02). |
| A05:2025 - Injection | **Limpio** | Sonar: 0 vulnerabilidades. Todo el acceso a datos usa el ORM SQLAlchemy con parámetros; no hay SQL construido con texto. Entradas validadas con Pydantic (tipos, longitudes, rangos). El frontend no usa `dangerouslySetInnerHTML`, `innerHTML` ni `eval` (0 coincidencias) y React escapa el contenido. |
| A06:2025 - Insecure Design | **Bajo revisión** | Sonar: 0. Reglas de negocio aplicadas en servidor (placa única, capacidad máxima, ventana horaria, aislamiento por bodega). Hallazgos de diseño: el bloqueo por correo (3 intentos / 15 min) permite que un tercero bloquee la cuenta de otra persona (denegación de servicio dirigida) y no hay límite por IP; cuando el `bodega_id` de un pedido no existe, un usuario no BODEGA queda asociado a la primera bodega registrada en lugar de recibir un error (probado, pero discutible). |
| A07:2025 - Authentication Failures | **Bajo revisión** | Sonar: 0. Bloqueo de cuenta tras 3 intentos (DEF-001 corregido, con prueba de regresión); contraseña mínima de 8 caracteres; mensaje genérico ante correo inexistente. Hallazgos: el mensaje "Intentos restantes" solo aparece para correos existentes, lo que permite enumerar usuarios (se mantiene porque lo pide el criterio de EN-002); no hay cierre de sesión del lado del servidor ni revocación de tokens; no hay segundo factor. |
| A08:2025 - Software or Data Integrity Failures | **Bajo revisión** | Sonar: 0. El JWT se valida con el algoritmo fijado (`algorithms=[HS256]`); no hay deserialización de datos no confiables; los paquetes se instalan con `package-lock.json`. Pendientes: sin CI/CD, sin firma ni verificación de artefactos, sin revisión por pares obligatoria (IMP-009). |
| A09:2025 - Security Logging and Alerting Failures | **Vulnerable** (parcialmente corregido) | El código no tenía ningún registro de eventos de seguridad. **Corregido:** el logger `ecologistica.security` registra inicios de sesión fallidos, cuentas bloqueadas y altas de usuarios (con `usuario_id`, sin correos ni contraseñas, Ley N° 29733), con una prueba que lo verifica. Pendientes: no hay alertas ni almacenamiento centralizado de los registros, y no se registran accesos denegados (403) ni cambios de datos. |
| A10:2025 - Mishandling of Exceptional Conditions | **Limpio** (con observación) | Sonar encontró 7 bugs `S9383` (promesas sin capturar errores) en el frontend: **corregidos** (0 bugs ahora). El backend revierte la transacción ante cualquier excepción (`get_db`) y devuelve códigos HTTP coherentes (401, 403, 404, 409, 422, 423). Observación: no hay un manejador global de excepciones que devuelva un formato de error uniforme. |

**Resumen:** 2 categorías limpias, 7 bajo revisión y 1 vulnerable (A09, con corrección parcial aplicada en este sprint). SonarQube reporta 0 vulnerabilidades y 0 hotspots; las debilidades listadas provienen de la revisión manual.

## 2. Detalles de Security Hotspots y Vulnerabilidades Críticas

SonarQube Community no generó **Security Hotspots** para este proyecto (calificación de seguridad A, revisión de seguridad A). Los puntos de mayor riesgo, identificados por revisión manual y tratados como hotspots del equipo, son:

- **Hotspot #1 — Clave de firma por defecto (A02/A04).** `src/backend/app/config.py`, línea 25: `SECRET_KEY` tiene un valor de desarrollo escrito en el código. Si se despliega sin `.env`, cualquiera que lea el repositorio podría firmar tokens válidos. *Mitigación aplicada:* aviso en el arranque (`main.py`) y, con `ENVIRONMENT=production`, el arranque se aborta si se usa el valor por defecto. *Pendiente:* rotar la clave en el despliegue real.
- **Hotspot #2 — Eco de SQL en registros (A02).** `config.py`, línea 19, y `database.py`, línea 12 (`echo=settings.DEBUG`): con `DEBUG = True` los registros incluían las sentencias SQL. *Mitigación aplicada:* `DEBUG` ahora es `False` por defecto; se activa solo con `.env` en desarrollo.
- **Hotspot #3 — Falta de registro de eventos de seguridad (A09).** Sin registro no era posible detectar fuerza bruta ni cuentas bloqueadas. *Mitigación aplicada:* logger `ecologistica.security` en `routers/auth_router.py` (inicios fallidos, bloqueos y altas), con la prueba `test_eventos_de_seguridad_se_registran_sin_datos_personales`.
- **Hotspot #4 — Dependencias de desarrollo con vulnerabilidades críticas (A03).** `vitest`/`tinypool` (ejecución de código por contaminación de prototipos) y `vite` (servidor de desarrollo). No afectan al código desplegado (0 en producción). *Mitigación aplicada:* actualización a Vitest 5 y `npm audit fix`; 0 vulnerabilidades.
- **Hotspot #5 — Token en `localStorage` (A04/A07).** `AuthContext.tsx`: un ataque XSS podría leer el token. Hoy no se encontró ningún punto de XSS (A05 limpio), pero el riesgo persiste. *Pendiente:* migrar a una cookie `HttpOnly` con `SameSite` y añadir una política CSP.

## 3. Pruebas de seguridad que respaldan las correcciones

| Defecto / control | Prueba automatizada |
|---|---|
| DEF-001 bloqueo de cuenta (A07) | `test_en002_cuenta_se_bloquea_tras_tres_intentos_fallidos` |
| DEF-002 aislamiento por bodega (A01) | `test_rn010_bodega_no_puede_registrar_pedido_para_otra_bodega`, `test_rn010_bodega_solo_lista_sus_propios_pedidos` |
| DEF-003 registro con rol de administración (A01) | `test_en002_registro_publico_no_permite_autoasignarse_rol_de_administracion` |
| Control por rol en la interfaz (A01) | pruebas de Vehículos y Pedidos por rol en `src/frontend/src/__tests__` |
| Registro de eventos sin datos personales (A09) | `test_eventos_de_seguridad_se_registran_sin_datos_personales` |
| Rol `ADMINISTRADOR` inexistente sin acceso (A01) | `test_rol_inexistente_administrador_no_obtiene_acceso` |
| Cabeceras de seguridad y flujo completo (A02) | `test_ruta_gold_flujo_completo_de_flota_y_pedidos` |

## 4. Plan de acción propuesto

1. ~~Exigir `SECRET_KEY` por entorno, cabeceras de seguridad, CORS acotado y ocultar `/docs`~~ **Hecho el 20/10/2026** (A02). Pendiente: CSP y HSTS en el despliegue con TLS.
2. Rotar la `SECRET_KEY` y definir `ENVIRONMENT=production` en el entorno real.
3. Fijar versiones del backend con un archivo de bloqueo y ejecutar `pip-audit` y `npm audit` en CI (A03/A08, IMP-009).
4. Implementar EN-008 (cifrado de campos personales y anonimización) y servir todo por TLS (A04).
5. Evaluar límite de intentos por IP, alertas por bloqueos repetidos y registro de accesos denegados (A06/A07/A09).
6. Ejecutar la prueba de penetración pendiente de EN-002 para cerrar el criterio.

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-20 | Sprint 3: primera evaluación contra OWASP Top 10:2025 con las correcciones aplicadas. |
| 1.1.0 | 2026-10-20 | Se cierran en el código el rol `ADMINISTRADOR`, la clave por defecto en producción, CORS, `/docs` y las cabeceras de seguridad; A02 pasa de Vulnerable a Bajo revisión. |
