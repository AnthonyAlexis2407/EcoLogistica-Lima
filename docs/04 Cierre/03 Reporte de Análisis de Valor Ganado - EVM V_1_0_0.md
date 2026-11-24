[⬅️ Volver al README Principal](../../README.md)

# Reporte de Análisis de Valor Ganado - EVM (Earned Value Analysis Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  |  **Presupuesto hasta la Conclusión (BAC):** USD 22.469,00  |  **Estado General:** 🔴 Rojo en alcance (SPI 0,341) y 🟢 Verde en gasto (89,8 % del BAC, sin usar la reserva)  |  **Versión:** 1.0.0

**Fecha de corte:** 28/11/2026. **Periodo actual:** Sprint 5 (17/11 al 28/11/2026). **Periodo anterior:** hasta el 16/11/2026 (fin del Sprint 4).

> **Glosario.** **PV** (valor planificado): cuánto trabajo debía estar hecho, en dólares. **EV** (valor ganado): cuánto trabajo está realmente hecho, en dólares. **AC** (costo real): cuánto se gastó. **SV = EV − PV** y **CV = EV − AC**: negativos significan atraso y sobrecosto. **SPI = EV ÷ PV** y **CPI = EV ÷ AC**: menores que 1 indican peor desempeño que el plan. **EAC**: estimación del costo total al terminar. Los cálculos se reproducen con `python scripts/calcular_evm.py` ([script](../../scripts/calcular_evm.py)).

## 1. Métricas de Desempeño EVM

| Métrica / Indicador | Periodo Actual | Acumulado Periodo Actual | Acumulado Periodo Anterior |
|---|---|---|---|
| **Valor Planificado (PV)** | USD 0,00 | USD 22.469,00 | USD 22.469,00 |
| **Valor Ganado (EV)** | USD 5.036,16 | USD 7.651,08 | USD 2.614,93 |
| **Costo Real (AC)** | USD 2.751,31 | USD 20.176,24 | USD 17.424,94 |
| **Variación del Cronograma (SV = EV - PV)** | +USD 5.036,16 | −USD 14.817,92 | −USD 19.854,07 |
| **Variación del Costo (CV = EV - AC)** | +USD 2.284,85 | −USD 12.525,16 | −USD 14.810,01 |
| **Índice de Desempeño del Cronograma (SPI = EV / PV)** | No definido (PV = 0) | 0,341 | 0,116 |
| **Índice de Desempeño del Costo (CPI = EV / AC)** | 1,830 | 0,379 | 0,150 |

*Por qué el PV del periodo actual es cero: la línea base completaba el 100 % del alcance el 16/11/2026 (Iteración 4); todo lo ganado después es trabajo que debió estar hecho antes.*

## 2. Porcentajes de Avance Acumulado (Respecto al BAC)

- **Porcentaje Planificado (PV / BAC):** 100,0 %
- **Porcentaje Ganado (EV / BAC):** 34,1 %
- **Porcentaje Gastado (AC / BAC):** 89,8 %

El avance real (34,1 %) es la tercera parte del planificado y está muy por debajo de lo gastado (89,8 %).

## 3. Análisis de Desviaciones

- **Causa raíz de la variación del cronograma:** 1) la ruta crítica (spike EN-001 → motor de rutas → mapa y dashboard) no tuvo presupuesto de tiempo y empezó en el Sprint 5; 2) el trabajo de calidad, seguridad, rendimiento, pruebas E2E y despliegue (Sprints 3 a 5) no figura en los 116 puntos del backlog y, por la regla de crédito, no suma valor ganado; 3) las herramientas locales (Docker con poca memoria, rutas largas en Windows, cobertura mal medida en CI) añadieron esperas. El SPI mejoró de 0,116 a 0,341 cuando el Sprint 5 aplicó el esfuerzo a la ruta crítica, lo que confirma la causa.
- **Impacto en el cronograma:** el alcance planificado no se completa antes de la sustentación del 30/11/2026. Quedan **76,5 puntos sin ganar**: 50 en 8 ítems sin iniciar (US-002, US-004, US-006, EN-003, EN-004, EN-006, EN-008 y EN-010) y 26,5 como la mitad pendiente de 9 ítems parciales. A la velocidad del Sprint 5 (26 puntos en 12 días) completarlos requeriría unas 5 semanas más.
- **Causa raíz de la variación del costo:** no es una ineficiencia medida en horas. Con el costo estimado por tiempo (dedicación planificada constante) y el valor ganado bajo por el alcance diferido, el CPI queda en 0,379. En el periodo actual el CPI fue 1,830: el esfuerzo del Sprint 5 se concentró en entregables con valor ganado.
- **Impacto en el presupuesto:** el costo estimado, USD 20.176,24, no excede el BAC y la reserva de contingencia (USD 2.696,28) sigue intacta. El impacto es de **valor**: terminar todo el alcance original al CPI acumulado costaría USD 59.251,76 (ver sección 4), unas 2,6 veces el BAC, que no está financiado.

## 4. Estimaciones a la Conclusión (EAC)

- **Fórmula 1 (EAC = BAC / CPI):** 22.469,00 ÷ 0,379 = **USD 59.251,76**
- **Fórmula 2 (EAC = BAC / (CPI × SPI)):** 22.469,00 ÷ (0,379 × 0,341) = **USD 174.005,16**
- **Fórmula 3 (EAC = AC + [(BAC - EV) / (CPI × SPI)]):** 20.176,24 + (22.469,00 − 7.651,08) ÷ (0,379 × 0,341) = **USD 134.929,65**
- **EAC Seleccionado, Justificación y Explicación:** **USD 59.251,76 (fórmula 1)**.
  - **Por qué esa fórmula:** vigila el costo, que es la restricción del proyecto (presupuesto cerrado y reserva de 12 %). Supone que la eficiencia de costo observada (CPI 0,379) se mantiene hasta terminar.
  - **Por qué no las otras:** las fórmulas 2 y 3 multiplican por el SPI (0,341). Ese índice no mide productividad, sino el alcance que se difirió; usarlo sobreestimaría el costo (hasta USD 174.005,16, 7,7 veces el BAC) y no representa un escenario realista.
  - **Lectura:** USD 59.251,76 significa **ETC = USD 39.075,51** por gastar y **VAC = −USD 36.782,76** (el BAC no alcanza). Para cerrar con el presupuesto restante (USD 2.292,76) haría falta un desempeño 6,46 veces mayor (TCPI = 14.817,92 ÷ 2.292,76). Ninguno es viable; de ahí la propuesta de reducir y re-baselinear el alcance.

## 5. Supuestos declarados

El equipo no llevó bitácora de horas ni facturas, por lo que las cifras son **estimaciones reproducibles**, no mediciones contables:

1. **BAC:** USD 22.469,00 del [Presupuesto del proyecto](../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md), sin la reserva de contingencia (USD 2.696,28).
2. **PV:** el BAC se reparte en proporción a los 116 puntos del backlog según la iteración de la hoja de ruta (24, 44, 26 y 22 puntos en las Iteraciones 1 a 4; USD 193,70 por punto). Las épicas transversales (EL-6, 53 puntos) se reparten en partes casi iguales.
3. **EV:** regla fija **0/50/100**: un ítem completo gana todos sus puntos, uno parcial el 50 % y uno sin iniciar 0. Completos: US-001 (3), US-003 (5) y EN-005 (5). Parciales (50 %): EN-001, EN-002, EN-007, EN-009, US-005, US-007, US-008, US-009 y US-010. El crédito se acredita en el sprint donde las pruebas lo verifican (Revisiones de Sprint y [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%205/01%20Matriz%20de%20cumplimiento%20V_1_0_0.md)).
4. **AC:** dedicación planificada constante: BAC × semanas transcurridas desde el 01/09/2026 ÷ 14 semanas presupuestadas.

## 6. Historia por sprint (comparación histórica)

| Sprint (fin) | PV acumulado | EV acumulado | AC acumulado | SV | CV | SPI | CPI |
|---|---|---|---|---|---|---|---|
| Sprint 1 (22/09) | 4.648,76 | 0,00 | 4.814,79 | −4.648,76 | −4.814,79 | 0,000 | 0,000 |
| Sprint 2 (06/10) | 13.171,48 | 2.033,83 | 8.024,64 | −11.137,65 | −5.990,81 | 0,154 | 0,253 |
| Sprint 3 (20/10) | 18.207,64 | 2.324,38 | 11.234,50 | −15.883,26 | −8.910,12 | 0,128 | 0,207 |
| Sprint 4 (16/11) | 22.469,00 | 2.614,93 | 17.424,94 | −19.854,07 | −14.810,01 | 0,116 | 0,150 |
| **Sprint 5 (28/11)** | **22.469,00** | **7.651,08** | **20.176,24** | **−14.817,92** | **−12.525,16** | **0,341** | **0,379** |

El desempeño tocó fondo en el Sprint 4 (SPI 0,116 y CPI 0,150) y se triplicó en el Sprint 5 al atacar la ruta crítica. La acción correctiva funcionó, pero llegó tarde. Los gráficos están en los [Tableros de Control](04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md).

## 7. Escenario de re-baselining propuesto (no aprobado)

Si el Product Owner aprobara mover los 8 ítems sin iniciar (50 puntos) al backlog de mantenimiento e incorporar el trabajo de calidad ya ejecutado como cambios de alcance (CR-01 calidad, seguridad y accesibilidad, 8 puntos; CR-02 Green IT, 8; CR-03 E2E, CI/CD, despliegue y usabilidad, 13; **puntos estimados de forma relativa por el equipo, pendientes de validar**), la línea base sería de 95 puntos (USD 236,52 por punto) con el mismo BAC:

| Indicador | Valor |
|---|---|
| EV / PV / AC | USD 16.201,33 / USD 22.469,00 / USD 20.176,24 |
| SV / CV | −USD 6.267,67 / −USD 3.974,91 |
| SPI / CPI | **0,721** / **0,803** |
| Porcentaje ganado | 72,1 % del BAC |
| EAC (fórmula 1) | USD 27.981,65 |

Este escenario **no sustituye** al reporte oficial: depende de una aprobación que aún no existe y de estimaciones nuevas.

## Referencias cruzadas

- Estado: [Reporte de Estado](01%20Reporte%20de%20Estado%20V_1_0_0.md) · Variación: [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) · Visualización: [Tableros de Control](04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md).
- Riesgos relacionados: RSK-05 y RSK-09 en el [Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
