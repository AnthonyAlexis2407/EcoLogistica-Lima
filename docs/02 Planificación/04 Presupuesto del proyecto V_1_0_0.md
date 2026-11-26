# Presupuesto del Proyecto

## Metadatos
- **Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles
- **Integrantes:**
  - Fernandez Condor Jhon Smith
  - Perez Ordoñez Anthony Alexis
  - Tovar Arias Michael Aldo
- **Fecha:** 08 de septiembre de 2026
- **Versión:** 1.1.0

[← Volver al README Principal](../../README.md)

---

> **Nota de alcance:** este documento modela el costo de construir EcoLogística Lima **como si fuera desarrollado por un equipo profesional completo**, valorizando cada rol funcional a tarifa de mercado durante las 14 semanas del proyecto (Documento 02, Acta de Constitución, `docs/01 Inicio/`). Es un ejercicio de costeo técnico independiente del presupuesto académico de ejecución del curso (S/ 16,300), que cubre únicamente los gastos reales de infraestructura y documentación del equipo de 3 estudiantes.

> **Moneda (versión 1.1.0):** todos los montos están en **soles peruanos (S/)**. Los valores originales en dólares se convirtieron con un tipo de cambio referencial de **S/ 3,75 por USD** (supuesto declarado; no es una cotización oficial). Historial: 1.0.0 en dólares; 1.1.0 en soles el 28/11/2026.

## 1. Costo de Recursos Humanos (CAPEX)

Cálculo: **Costo = Horas Asignadas × Tarifa Hora (S/)**, sobre 14 semanas de proyecto. Cada integrante del equipo cubre uno o más roles funcionales (ver Documento 08, `docs/01 Inicio/`).

| Rol | Horas Asignadas | Tarifa/Hora (S/) | Costo (S/) | Integrante que lo cubre |
|---|---|---|---|---|
| Project Manager | 140 | S/ 75.00 | S/ 10,500.00 | Perez Ordoñez Anthony Alexis |
| Software Architect | 110 | S/ 105.00 | S/ 11,550.00 | Fernandez Condor Jhon Smith |
| Senior Developer (Backend + Algoritmo) | 350 | S/ 82.50 | S/ 28,875.00 | Fernandez Condor Jhon Smith |
| Junior Developer (Frontend) | 280 | S/ 52.50 | S/ 14,700.00 | Perez Ordoñez Anthony Alexis |
| QA Engineer | 140 | S/ 56.25 | S/ 7,875.00 | Tovar Arias Michael Aldo |
| UI/UX Designer | 85 | S/ 60.00 | S/ 5,100.00 | Perez Ordoñez Anthony Alexis |
| **Subtotal Recursos Humanos** | **1,105** | — | **S/ 78,600.00** | — |

## 2. Costo de Licenciamiento y Herramientas

| Ítem | Detalle | Costo (S/) |
|---|---|---|
| IDE / Entornos de desarrollo | Licencias de equipo (PyCharm/WebStorm) | S/ 1,125.00 |
| Atlassian Jira Software | Plan Standard, 3 usuarios × 4 meses | S/ 562.50 |
| Figma | Plan Profesional, 3 editores × 4 meses | S/ 540.00 |
| SonarQube / CodeQL | Plan Cloud básico × 4 meses | S/ 150.00 |
| Dominio (.pe / .com) | Registro anual | S/ 56.25 |
| Certificado SSL | Let's Encrypt (gratuito) | S/ 0.00 |
| **Subtotal Licenciamiento** | — | **S/ 2,433.75** |

## 3. Costo de Infraestructura Cloud y Servicios (OPEX)

| Ítem | Detalle | Costo (S/) |
|---|---|---|
| Instancias de cómputo | 2× VM (API + Worker de optimización), 4 meses | S/ 900.00 |
| Base de datos gestionada | PostgreSQL + PostGIS, instancia pequeña, 4 meses | S/ 750.00 |
| Almacenamiento de objetos | Evidencias fotográficas (S3-compatible), 4 meses | S/ 150.00 |
| API de mapas y tráfico | Google Maps API (consumo de desarrollo y pruebas) | S/ 1,125.00 |
| Caché / colas | Redis gestionado, 4 meses | S/ 225.00 |
| CI/CD | GitHub Actions (excedente sobre plan gratuito) | S/ 75.00 |
| **Subtotal Infraestructura Cloud** | — | **S/ 3,225.00** |

## 4. Reserva de Contingencia

Conforme al Documento 03 (Registro de Riesgos), donde 1 riesgo califica como **Alto** y 6 como **Medio**, se aplica una reserva de contingencia del **12%** sobre el subtotal del proyecto (dentro del rango sugerido de 10%-15%).

## Tabla Resumen Financiera

| Categoría | Costo Subtotal (S/) | Porcentaje del Total |
|---|---|---|
| **1. Recursos Humanos (CAPEX)** | S/ 78,600.00 | 93.3% |
| **2. Licenciamiento de Software** | S/ 2,433.75 | 2.9% |
| **3. Infraestructura Cloud (OPEX)** | S/ 3,225.00 | 3.8% |
| **SUBTOTAL DE PROYECTO** | **S/ 84,258.75** | **100.0%** |
| **4. Reserva de Contingencia (12%)** | S/ 10,111.05 | N/A |
| **PRESUPUESTO TOTAL ESTIMADO** | **S/ 94,369.80** | **100.0%** |

## Justificación de la Consolidación

- El **93.3%** del presupuesto corresponde a Recursos Humanos, consistente con un proyecto de software cuyo mayor riesgo técnico (RSK-05) recae en el diseño e implementación del motor de optimización, lo que justifica la mayor asignación de horas al rol de Senior Developer/Backend.
- El **6.7%** restante (licenciamiento + infraestructura) refleja una arquitectura deliberadamente ligera en costos fijos (FastAPI asíncrono, PostgreSQL/PostGIS, caché con Redis — Documento 10), alineada con el criterio de Eficiencia Energética (RNF-009) y con la restricción presupuestal del curso (R01).
- La reserva de contingencia del 12% cubre específicamente la materialización parcial del riesgo RSK-05 (rediseño del algoritmo) y RSK-04 (presión presupuestal ante escalamiento), sin necesidad de una re-negociación de alcance con el docente/Product Owner académico.

---

[← Volver al README Principal](../../README.md)
