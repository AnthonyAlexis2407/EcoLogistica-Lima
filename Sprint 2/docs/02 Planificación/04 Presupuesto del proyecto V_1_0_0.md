# Presupuesto del Proyecto

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

> **Nota de alcance:** este documento modela el costo de construir EcoLogística Lima **como si fuera desarrollado por un equipo profesional completo**, valorizando cada rol funcional a tarifa de mercado durante las 14 semanas del proyecto (Documento 02, Acta de Constitución, `docs/01 Inicio/`). Es un ejercicio de costeo técnico independiente del presupuesto académico de ejecución del curso (S/ 16,300), que cubre únicamente los gastos reales de infraestructura y documentación del equipo de 3 estudiantes.

## 1. Costo de Recursos Humanos (CAPEX)

Cálculo: **Costo = Horas Asignadas × Tarifa Hora (USD)**, sobre 14 semanas de proyecto. Cada integrante del equipo cubre uno o más roles funcionales (ver Documento 08, `docs/01 Inicio/`).

| Rol | Horas Asignadas | Tarifa/Hora (USD) | Costo (USD) | Integrante que lo cubre |
|---|---|---|---|---|
| Project Manager | 140 | $ 20.00 | $ 2,800.00 | Perez Ordoñez Anthony Alexis |
| Software Architect | 110 | $ 28.00 | $ 3,080.00 | Fernandez Condor Jhon Smith |
| Senior Developer (Backend + Algoritmo) | 350 | $ 22.00 | $ 7,700.00 | Fernandez Condor Jhon Smith |
| Junior Developer (Frontend) | 280 | $ 14.00 | $ 3,920.00 | Perez Ordoñez Anthony Alexis |
| QA Engineer | 140 | $ 15.00 | $ 2,100.00 | Tovar Arias Michael Aldo |
| UI/UX Designer | 85 | $ 16.00 | $ 1,360.00 | Perez Ordoñez Anthony Alexis |
| **Subtotal Recursos Humanos** | **1,105** | — | **$ 20,960.00** | — |

## 2. Costo de Licenciamiento y Herramientas

| Ítem | Detalle | Costo (USD) |
|---|---|---|
| IDE / Entornos de desarrollo | Licencias de equipo (PyCharm/WebStorm) | $ 300.00 |
| Atlassian Jira Software | Plan Standard, 3 usuarios × 4 meses | $ 150.00 |
| Figma | Plan Profesional, 3 editores × 4 meses | $ 144.00 |
| SonarQube / CodeQL | Plan Cloud básico × 4 meses | $ 40.00 |
| Dominio (.pe / .com) | Registro anual | $ 15.00 |
| Certificado SSL | Let's Encrypt (gratuito) | $ 0.00 |
| **Subtotal Licenciamiento** | — | **$ 649.00** |

## 3. Costo de Infraestructura Cloud y Servicios (OPEX)

| Ítem | Detalle | Costo (USD) |
|---|---|---|
| Instancias de cómputo | 2× VM (API + Worker de optimización), 4 meses | $ 240.00 |
| Base de datos gestionada | PostgreSQL + PostGIS, instancia pequeña, 4 meses | $ 200.00 |
| Almacenamiento de objetos | Evidencias fotográficas (S3-compatible), 4 meses | $ 40.00 |
| API de mapas y tráfico | Google Maps API (consumo de desarrollo y pruebas) | $ 300.00 |
| Caché / colas | Redis gestionado, 4 meses | $ 60.00 |
| CI/CD | GitHub Actions (excedente sobre plan gratuito) | $ 20.00 |
| **Subtotal Infraestructura Cloud** | — | **$ 860.00** |

## 4. Reserva de Contingencia

Conforme al Documento 03 (Registro de Riesgos), donde 1 riesgo califica como **Alto** y 6 como **Medio**, se aplica una reserva de contingencia del **12%** sobre el subtotal del proyecto (dentro del rango sugerido de 10%-15%).

## Tabla Resumen Financiera

| Categoría | Costo Subtotal (USD) | Porcentaje del Total |
|---|---|---|
| **1. Recursos Humanos (CAPEX)** | $ 20,960.00 | 93.3% |
| **2. Licenciamiento de Software** | $ 649.00 | 2.9% |
| **3. Infraestructura Cloud (OPEX)** | $ 860.00 | 3.8% |
| **SUBTOTAL DE PROYECTO** | **$ 22,469.00** | **100.0%** |
| **4. Reserva de Contingencia (12%)** | $ 2,696.28 | N/A |
| **PRESUPUESTO TOTAL ESTIMADO** | **$ 25,165.28** | **100.0%** |

## Justificación de la Consolidación

- El **93.3%** del presupuesto corresponde a Recursos Humanos, consistente con un proyecto de software cuyo mayor riesgo técnico (RSK-05) recae en el diseño e implementación del motor de optimización, lo que justifica la mayor asignación de horas al rol de Senior Developer/Backend.
- El **6.7%** restante (licenciamiento + infraestructura) refleja una arquitectura deliberadamente ligera en costos fijos (FastAPI asíncrono, PostgreSQL/PostGIS, caché con Redis — Documento 10), alineada con el criterio de Eficiencia Energética (RNF-009) y con la restricción presupuestal del curso (R01).
- La reserva de contingencia del 12% cubre específicamente la materialización parcial del riesgo RSK-05 (rediseño del algoritmo) y RSK-04 (presión presupuestal ante escalamiento), sin necesidad de una re-negociación de alcance con el docente/Product Owner académico.

---

[← Volver al README Principal](../../README.md)
