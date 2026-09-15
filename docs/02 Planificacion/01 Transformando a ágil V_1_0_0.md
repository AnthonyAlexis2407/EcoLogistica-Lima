# Transformando a Ágil: De Requisitos a Backlog

## Metadatos
- **Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles
- **Integrantes:**
  - Fernandez Condor Jhon Smith
  - Perez Ordoñez Anthony Alexis
  - Tovar Arias Michael Aldo
- **Fecha:** 08 de septiembre de 2026
- **Versión:** 1.0.0

[← Volver al README Principal](../../README.md)

---

## A. Metodología de Transformación

La línea base de requisitos (Documento 06: Requisitos Funcionales y Documento 07: Requisitos No Funcionales, en `docs/01 Inicio/`) se transforma en elementos de trabajo ágil bajo dos reglas:

1. **Requerimientos Funcionales (RF) → Épicas → Historias de Usuario (US).** Los 10 RF se agrupan temáticamente en **6 Épicas** según el módulo funcional al que pertenecen. Cada RF se descompone en exactamente una Historia de Usuario, manteniendo trazabilidad 1 a 1 (RF-00X → US-00X).
2. **Requerimientos No Funcionales (RNF) → Historias Técnicas (Enablers).** Los 10 RNF se transforman en **Enablers** bajo una épica transversal de Arquitectura y Calidad, ya que no entregan valor de negocio visible por sí solos pero son condición de aceptación de todo el sistema (RNF-00X → EN-00X).

| Épica | Nombre | RF de origen |
|---|---|---|
| **EP-01** | Gestión de Flota y Conductores | RF-001, RF-008 |
| **EP-02** | Gestión de Pedidos y Clientes | RF-002, RF-009 |
| **EP-03** | Optimización y Ejecución de Rutas | RF-003, RF-007 |
| **EP-04** | Visualización y Geolocalización | RF-004 |
| **EP-05** | Sostenibilidad, Dashboard y Reportes | RF-005, RF-006, RF-010 |
| **EP-06** | Arquitectura, Seguridad y Calidad Transversal | RNF-001 a RNF-010 |

---

## B y C. Historias de Usuario y Criterios de Aceptación (BDD/Gherkin)

### EP-01: Gestión de Flota y Conductores

**ID:** US-001
**Título:** Registrar y administrar vehículos de la flota
**Épica Relacionada:** EP-01 Gestión de Flota y Conductores

**Redacción:**
Como **administrador de flota**,
quiero **registrar, editar y dar de baja vehículos con su ficha técnica**,
para **mantener un catálogo confiable disponible para la asignación de rutas**.

**Criterios de Aceptación:**

Escenario: Registro exitoso de un vehículo nuevo
Dado un administrador de flota autenticado
Cuando registra un vehículo con placa única, capacidad y tipo de combustible válidos
Entonces el sistema lo agrega al catálogo activo disponible para asignación de rutas

Escenario: Rechazo de placa duplicada
Dado un intento de registrar una placa ya existente en el catálogo
Cuando el administrador guarda el formulario
Entonces el sistema rechaza el registro por duplicidad y señala la placa en conflicto

---

**ID:** US-002
**Título:** Gestionar conductores y capturar evidencia de entrega en campo
**Épica Relacionada:** EP-01 Gestión de Flota y Conductores

**Redacción:**
Como **conductor**,
quiero **confirmar cada entrega con foto o firma digital, incluso sin conexión**,
para **dejar evidencia verificable del cumplimiento del pedido**.

**Criterios de Aceptación:**

Escenario: Confirmación de entrega con evidencia
Dado un conductor en la ubicación de una parada pendiente
Cuando captura foto o firma digital del receptor y confirma la entrega
Entonces el sistema marca el pedido como "Entregado" con marca de tiempo y geolocalización

Escenario: Captura de evidencia en modo offline
Dado un conductor sin conexión al momento de capturar la evidencia
Cuando confirma la entrega en modo offline
Entonces el sistema almacena la evidencia localmente y la sincroniza automáticamente al recuperar conectividad, sin duplicar el registro

---

### EP-02: Gestión de Pedidos y Clientes

**ID:** US-003
**Título:** Registrar pedidos con ventana horaria y ubicación
**Épica Relacionada:** EP-02 Gestión de Pedidos y Clientes

**Redacción:**
Como **operador logístico**,
quiero **registrar un pedido con dirección, ventana horaria y peso de carga**,
para **incorporarlo a la cola de planificación diaria**.

**Criterios de Aceptación:**

Escenario: Registro válido de un pedido
Dado un operador logístico autenticado con permisos de registro
Cuando ingresa dirección válida, ventana horaria y peso de carga dentro de los límites del catálogo de vehículos
Entonces el sistema crea el pedido en estado "Pendiente de asignación" y lo agrega a la cola de planificación

Escenario: Rechazo por exceso de capacidad
Dado un pedido cuyo peso declarado excede la capacidad máxima de cualquier vehículo de la flota activa
Cuando el usuario intenta guardarlo
Entonces el sistema rechaza el registro y muestra el motivo específico de la incompatibilidad de capacidad

---

**ID:** US-004
**Título:** Notificar al cliente el estado y ETA de su pedido
**Épica Relacionada:** EP-02 Gestión de Pedidos y Clientes

**Redacción:**
Como **dueño de bodega**,
quiero **recibir notificaciones del estado y la hora estimada de mi pedido**,
para **planificar la recepción de mercadería sin llamar a soporte**.

**Criterios de Aceptación:**

Escenario: Notificación de salida a ruta
Dado un pedido que cambia de estado a "En ruta"
Cuando el sistema detecta el cambio
Entonces envía una notificación al dueño de bodega con la hora estimada de llegada

Escenario: Notificación de retraso con motivo
Dado un pedido que sufrirá un retraso por re-optimización
Cuando se actualiza la hora estimada de llegada
Entonces el sistema notifica al dueño de bodega la nueva ventana y el motivo general del retraso, sin exponer datos de otros clientes

---

### EP-03: Optimización y Ejecución de Rutas

**ID:** US-005
**Título:** Generar rutas optimizadas para la flota disponible
**Épica Relacionada:** EP-03 Optimización y Ejecución de Rutas

**Redacción:**
Como **operador logístico**,
quiero **ejecutar la planificación diaria y obtener rutas optimizadas**,
para **minimizar distancia, tiempo y emisiones de CO₂**.

**Criterios de Aceptación:**

Escenario: Optimización respetando restricciones
Dado un conjunto de pedidos pendientes y vehículos disponibles dentro de la ventana operativa del día
Cuando el operador ejecuta la planificación
Entonces el sistema retorna una o más rutas optimizadas respetando ventanas horarias, capacidad vehicular y restricciones de Pico y Placa

Escenario: Pedidos no asignables reportados explícitamente
Dado un conjunto de pedidos cuyas ventanas horarias son matemáticamente incompatibles con la flota disponible
Cuando se ejecuta la optimización
Entonces el sistema reporta explícitamente los pedidos no asignables en lugar de generar una ruta inválida

---

**ID:** US-006
**Título:** Re-optimizar una ruta ante una incidencia
**Épica Relacionada:** EP-03 Optimización y Ejecución de Rutas

**Redacción:**
Como **operador logístico**,
quiero **recalcular una ruta en curso cuando ocurre una incidencia**,
para **mantener el cumplimiento de entrega sin replanificar todo desde cero**.

**Criterios de Aceptación:**

Escenario: Re-optimización por vía cerrada
Dado una ruta en curso y un reporte de vía cerrada en el tramo siguiente
Cuando el operador confirma la incidencia
Entonces el sistema recalcula únicamente el tramo afectado y notifica la nueva secuencia al conductor en menos de 45 segundos

Escenario: Cancelación de un pedido en ruta
Dado un pedido cancelado por el cliente mientras el vehículo ya está en ruta
Cuando el operador marca el pedido como cancelado
Entonces el sistema retira la parada correspondiente y reordena las paradas restantes sin afectar las ya completadas

---

### EP-04: Visualización y Geolocalización

**ID:** US-007
**Título:** Visualizar la ruta asignada en un mapa interactivo
**Épica Relacionada:** EP-04 Visualización y Geolocalización

**Redacción:**
Como **conductor**,
quiero **ver mi ruta y el orden de paradas en un mapa**,
para **navegar sin depender de nomenclatura oficial de calles**.

**Criterios de Aceptación:**

Escenario: Visualización de ruta asignada
Dado una ruta ya optimizada y asignada a un vehículo
Cuando el conductor abre el detalle de la ruta en la app móvil
Entonces el sistema muestra el mapa con el orden de paradas y el tramo restante

Escenario: Uso del mapa en modo sin conexión
Dado un conductor sin señal de datos móviles
Cuando abre la app en una zona sin cobertura
Entonces el sistema muestra la última ruta descargada en caché local con una notificación de "modo sin conexión"

---

### EP-05: Sostenibilidad, Dashboard y Reportes

**ID:** US-008
**Título:** Consultar el dashboard de indicadores operativos y ambientales
**Épica Relacionada:** EP-05 Sostenibilidad, Dashboard y Reportes

**Redacción:**
Como **administrador de flota**,
quiero **ver distancia, combustible ahorrado y CO₂ evitado en un periodo**,
para **evaluar el desempeño ambiental del negocio**.

**Criterios de Aceptación:**

Escenario: Dashboard con datos agregados
Dado rutas completadas dentro del rango de fechas seleccionado
Cuando el administrador abre el dashboard
Entonces el sistema muestra los indicadores agregados (km, CO₂, combustible, % de cumplimiento) comparados contra la línea base

Escenario: Estado vacío explícito
Dado un rango de fechas sin rutas completadas
Cuando se solicita el dashboard
Entonces el sistema muestra un estado vacío explícito en lugar de valores en cero engañosos

---

**ID:** US-009
**Título:** Exportar reportes operativos y ambientales
**Épica Relacionada:** EP-05 Sostenibilidad, Dashboard y Reportes

**Redacción:**
Como **auditor externo**,
quiero **exportar un reporte en PDF/Excel de un periodo**,
para **verificar el cumplimiento ambiental sin acceso directo al sistema**.

**Criterios de Aceptación:**

Escenario: Exportación exitosa en PDF
Dado un rango de fechas con datos operativos disponibles
Cuando el administrador solicita exportar el reporte en PDF
Entonces el sistema genera el archivo con los indicadores del periodo y lo pone disponible para descarga en menos de 10 segundos

Escenario: Denegación a usuario sin permisos
Dado un usuario sin el rol autorizado para exportar reportes
Cuando intenta generar la exportación
Entonces el sistema deniega la acción y registra el intento en el log de auditoría

---

**ID:** US-010
**Título:** Calcular y comunicar la compensación de carbono
**Épica Relacionada:** EP-05 Sostenibilidad, Dashboard y Reportes

**Redacción:**
Como **administrador de flota**,
quiero **ver el CO₂ evitado traducido en árboles equivalentes**,
para **comunicar el impacto ambiental del proyecto de forma tangible**.

**Criterios de Aceptación:**

Escenario: Cálculo de compensación al cerrar una ruta
Dado una ruta completada con distancia optimizada y distancia base registradas
Cuando el sistema cierra la ruta
Entonces calcula el CO₂ evitado, lo acumula en el balance de sostenibilidad y lo traduce a su equivalente en árboles

Escenario: Bloqueo por falta de factor de emisión
Dado un vehículo sin factor de emisión configurado en su ficha técnica
Cuando se intenta cerrar su ruta
Entonces el sistema impide el cierre y solicita completar el dato antes de continuar

---

## EP-06: Arquitectura, Seguridad y Calidad Transversal (Enablers desde RNF)

**ID:** EN-001 | **Título:** Motor de optimización dentro del SLA de 45 segundos | **Origen:** RNF-001 (Rendimiento)
Escenario: Cómputo dentro del límite — Dado hasta 250 pedidos pendientes, cuando se ejecuta la planificación, entonces el tiempo total de cómputo es ≤ 45 segundos (percentil 95).
Escenario: Degradación acotada al escalar — Dado un incremento a 1,000 pedidos/día, cuando se ejecuta la planificación, entonces la degradación de tiempos de respuesta es ≤ 10% frente a la línea base.

**ID:** EN-002 | **Título:** Hardening de autenticación y protección OWASP | **Origen:** RNF-002 (Seguridad)
Escenario: Bloqueo por fuerza bruta — Dado un atacante que intenta 3 inicios de sesión fallidos, cuando alcanza el umbral, entonces el sistema bloquea la cuenta 15 minutos y registra el evento.
Escenario: Pentest sin hallazgos críticos — Dado un pentest de cierre de iteración, cuando se ejecuta sobre el API Gateway, entonces no se detectan vulnerabilidades críticas/altas del OWASP Top 10.

**ID:** EN-003 | **Título:** Failover automático del backend | **Origen:** RNF-003 (Disponibilidad)
Escenario: Recuperación ante caída de instancia — Dado una instancia caída en horario operativo, cuando ocurre el fallo, entonces el tráfico se redirige a una instancia sana en ≤ 60 segundos.
Escenario: Disponibilidad mensual — Dado un mes calendario completo, cuando se mide el uptime en ventana operativa, entonces la disponibilidad es ≥ 99.5%.

**ID:** EN-004 | **Título:** Flujo de confirmación de entrega de baja fricción | **Origen:** RNF-004 (Usabilidad)
Escenario: Confirmación en pocos pasos — Dado un conductor sin capacitación previa mayor a 10 minutos, cuando confirma una entrega, entonces la tarea se completa en ≤ 3 toques y ≤ 20 segundos.

**ID:** EN-005 | **Título:** Módulo de optimización desacoplado y con pruebas | **Origen:** RNF-005 (Mantenibilidad)
Escenario: Integración de nueva metaheurística — Dado un cambio de Búsqueda Tabú a ACO, cuando se integra el nuevo algoritmo, entonces no se modifican los módulos de Pedidos, Flota o Dashboard.
Escenario: Cobertura mínima — Dado el módulo de optimización, cuando se ejecuta la suite de pruebas, entonces la cobertura unitaria es ≥ 80%.

**ID:** EN-006 | **Título:** Auto-scaling horizontal para 1,000 pedidos/día | **Origen:** RNF-006 (Escalabilidad)
Escenario: Crecimiento de carga — Dado un crecimiento de 250 a 1,000 pedidos/día, cuando se activa el auto-scaling, entonces el sistema procesa la carga sin rediseño de arquitectura.

**ID:** EN-007 | **Título:** Cumplimiento WCAG 2.1 AA en el panel web | **Origen:** RNF-007 (Accesibilidad)
Escenario: Navegación por teclado — Dado un usuario que navega solo con teclado, cuando recorre el panel web, entonces todos los componentes interactivos son alcanzables y operables.
Escenario: Auditoría automatizada — Dado el panel web antes de cada entrega, cuando se ejecuta axe-core, entonces no se detectan incumplimientos de nivel AA.

**ID:** EN-008 | **Título:** Cifrado y anonimización de datos personales (Ley 29733) | **Origen:** RNF-008 (Seguridad de Datos)
Escenario: Cifrado en reposo y tránsito — Dado datos personales almacenados, cuando se auditan los campos clasificados como personales, entonces el 100% están cifrados con AES-256/TLS 1.3.
Escenario: Derecho de eliminación — Dado una solicitud de baja de un conductor, cuando se procesa la solicitud, entonces sus datos se anonimizan en ≤ 5 días hábiles.

**ID:** EN-009 | **Título:** Reducción de recómputo mediante caché | **Origen:** RNF-009 (Eficiencia Energética)
Escenario: Reutilización de resultados recientes — Dado condiciones sin cambios significativos, cuando se solicita una nueva optimización, entonces el sistema reutiliza resultados cacheados en Redis.
Escenario: Medición mensual — Dado un mes de operación, cuando se mide el consumo de CPU por corrida, entonces se reduce ≥ 30% frente a una implementación sin caché.

**ID:** EN-010 | **Título:** App de conductor offline-first en dispositivos de gama baja | **Origen:** RNF-010 (Portabilidad)
Escenario: Funcionamiento en gama baja — Dado un Android 8.0+ con 2 GB de RAM, cuando se instala la PWA, entonces las funciones críticas (ver ruta, marcar entrega) operan sin conexión.
Escenario: Sincronización posterior — Dado evidencia capturada offline, cuando el dispositivo recupera señal, entonces la sincronización se completa en ≤ 5 minutos.

---

## D. Definition of Done (DoD) Global del Proyecto

Toda Historia de Usuario o Enabler se considera **"Done"** únicamente si cumple, sin excepción, los siguientes criterios:

1. **Cobertura de pruebas unitarias ≥ 80%** sobre el código nuevo o modificado.
2. **Análisis estático sin vulnerabilidades críticas ni altas** (SonarQube / CodeQL) en el pipeline de CI.
3. **Revisión de código (Peer Review) aprobada** por al menos un par técnico mediante Pull Request, sin comentarios bloqueantes pendientes.
4. **Despliegue automatizado ejecutable en ambiente de Staging/Pruebas**, verificado con un smoke test post-despliegue.
5. **Documentación de API/código actualizada** (OpenAPI/Swagger para endpoints nuevos o modificados; docstrings/README para módulos internos).
6. **Todos los Criterios de Aceptación (Gherkin) de la historia verificados y en estado "Pasa"**, incluyendo al menos un escenario negativo/borde.
7. **Sin regresiones**: la suite de pruebas de regresión automatizada se ejecuta en verde antes del cierre del Sprint.
8. **Validación funcional aceptada por el Product Owner académico (docente)** en la demo de cierre de iteración.

---

[← Volver al README Principal](../../README.md)
