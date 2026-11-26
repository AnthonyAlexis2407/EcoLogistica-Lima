[⬅️ Volver al README Principal](../../README.md)

# Reporte de Análisis de Valor Ganado - EVM (Earned Value Analysis Report)

- **Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  |  **Presupuesto hasta la Conclusión (BAC):** S/ 84.258,75  |  **Estado General:** 🟡 Amarillo en cronograma (SPI 0,944) y 🟢 Verde en costo (CPI 1,051; 89,8 % del BAC, sin usar la reserva)  |  **Versión:** 2.0.0

**Fecha de corte:** 28/11/2026. **Periodo actual:** Sprint 4 (21/10 al 28/11/2026). **Periodo anterior:** hasta el 20/10/2026 (fin del Sprint 3). El proyecto tiene cuatro sprints; el cuarto se extendió hasta la fecha de corte.

> **Glosario.** **PV** (valor planificado): cuánto trabajo debía estar hecho, en soles. **EV** (valor ganado): cuánto trabajo está realmente hecho, en soles. **AC** (costo real): cuánto se gastó. **SV = EV − PV** y **CV = EV − AC**: negativos significan atraso y sobrecosto. **SPI = EV ÷ PV** y **CPI = EV ÷ AC**: menores que 1 indican peor desempeño que el plan. **EAC**: estimación del costo total al terminar. Los cálculos se reproducen con `python scripts/calcular_evm.py` ([script](../../scripts/calcular_evm.py)).

## 1. Métricas de Desempeño EVM

| Métrica / Indicador | Periodo Actual | Acumulado Periodo Actual | Acumulado Periodo Anterior |
|---|---|---|---|
| **Valor Planificado (PV)** | S/ 15.980,10 | S/ 84.258,75 | S/ 68.278,65 |
| **Valor Ganado (EV)** | S/ 69.731,36 | S/ 79.537,35 | S/ 9.805,99 |
| **Costo Real (AC)** | S/ 33.531,53 | S/ 75.660,90 | S/ 42.129,38 |
| **Variación del Cronograma (SV = EV - PV)** | +S/ 53.751,26 | −S/ 4.721,40 | −S/ 58.472,66 |
| **Variación del Costo (CV = EV - AC)** | +S/ 36.199,84 | +S/ 3.876,45 | −S/ 32.323,39 |
| **Índice de Desempeño del Cronograma (SPI = EV / PV)** | 4,364 | 0,944 | 0,144 |
| **Índice de Desempeño del Costo (CPI = EV / AC)** | 2,080 | 1,051 | 0,233 |

*Por qué el SPI del periodo es tan alto: el Sprint 4 planificaba poco valor nuevo (la línea base ya estaba casi completa) y ganó casi todo el alcance pendiente de los tres sprints anteriores; el índice acumulado, 0,944, es el que mide el desempeño del proyecto.*

## 2. Porcentajes de Avance Acumulado (Respecto al BAC)

- **Porcentaje Planificado (PV / BAC):** 100,0 %
- **Porcentaje Ganado (EV / BAC):** 94,4 %
- **Porcentaje Gastado (AC / BAC):** 89,8 %

El avance real (94,4 %) está cerca de lo planificado y por encima de lo gastado (89,8 %): se entregó más valor del que costó el tiempo transcurrido.

## 3. Análisis de Desviaciones

- **Causa raíz de la variación del cronograma:** 1) la ruta crítica (spike EN-001 → motor de rutas → mapa y dashboard) no tuvo presupuesto de tiempo hasta el Sprint 4; 2) el trabajo de calidad, seguridad, rendimiento, pruebas E2E y despliegue (Sprints 3 y 4) no figura en los 116 puntos del backlog y, por la regla de crédito, no suma valor ganado; 3) las herramientas locales (Docker con poca memoria, rutas largas en Windows, cobertura mal medida en CI) añadieron esperas. El SPI pasó de 0,144 a 0,944 cuando el Sprint 4 aplicó el esfuerzo a la ruta crítica y al resto del alcance.
- **Impacto en el cronograma:** el alcance se completó el 28/11/2026, antes de la sustentación del 30/11/2026. Quedan **6,5 puntos sin ganar**: la mitad pendiente de EN-003 (failover automático, 5 puntos) y de EN-006 (escalado horizontal, 8 puntos), que cumplen su medida con dos instancias en pruebas pero no en la nube gratuita. Cerrarlos exige un plan de pago de la plataforma, no más desarrollo.
- **Causa raíz de la variación del costo:** con el costo estimado por tiempo (dedicación planificada constante), el CPI de 1,051 indica que el valor entregado superó al costo del tiempo transcurrido. No es una ganancia medida en horas.
- **Impacto en el presupuesto:** el costo estimado, S/ 75.660,90, no excede el BAC y la reserva de contingencia (S/ 10.111,05) sigue intacta.

## 4. Estimaciones a la Conclusión (EAC)

- **Fórmula 1 (EAC = BAC / CPI):** 22.469,00 ÷ 1,051 = **S/ 80.152,20**
- **Fórmula 2 (EAC = BAC / (CPI × SPI)):** 22.469,00 ÷ (1,051 × 0,944) = **S/ 84.910,09**
- **Fórmula 3 (EAC = AC + [(BAC - EV) / (CPI × SPI)]):** 20.176,24 + (22.469,00 − 21.209,96) ÷ (1,051 × 0,944) = **S/ 80.418,82**
- **EAC Seleccionado, Justificación y Explicación:** **S/ 80.418,82 (fórmula 3)**.
  - **Por qué esa fórmula:** el trabajo que falta (la infraestructura de pago para EN-003 y EN-006) no se hará con la eficiencia observada hasta ahora, porque su costo es de la plataforma y no de horas del equipo. La fórmula 3 suma lo gastado y estima lo que falta con los dos índices, lo que es más prudente que la fórmula 1 sin llegar al extremo de la fórmula 2.
  - **Por qué no las otras:** la fórmula 1 supone que el CPI de 1,051 se mantiene y subestima el costo restante; la fórmula 2 reparte todo el BAC con ambos índices y proyecta S/ 84.910,09, S/ 651,34 sobre el BAC, un escenario que la reserva de contingencia cubre.
  - **Lectura:** S/ 80.418,82 significa **ETC = S/ 4.757,93** por gastar y **VAC = +S/ 3.839,93** (se termina por debajo del BAC). El **TCPI** necesario con el presupuesto restante (S/ 8.597,85) es 0,549 = 1.259,04 ÷ 2.292,76: el proyecto puede terminar con holgura.

## 5. Supuestos declarados

El equipo no llevó bitácora de horas ni facturas, por lo que las cifras son **estimaciones reproducibles**, no mediciones contables:

0. **Moneda:** todos los montos están en **soles peruanos (S/)**; los valores del [Presupuesto del proyecto](../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md) se convirtieron desde dólares con un tipo de cambio referencial de S/ 3,75 por USD (supuesto declarado). Los índices (SPI, CPI) no dependen de la moneda.
1. **BAC:** S/ 84.258,75 del [Presupuesto del proyecto](../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md), sin la reserva de contingencia (S/ 10.111,05).
2. **PV:** el BAC se reparte en proporción a los 116 puntos del backlog según la iteración de la hoja de ruta (24, 44, 26 y 22 puntos en las Iteraciones 1 a 4; S/ 726,38 por punto). Las épicas transversales (EL-6, 53 puntos) se reparten en partes casi iguales.
3. **EV:** regla fija **0/50/100**. Un ítem gana el 100 % cuando está implementado y sus criterios de aceptación verificables por el equipo se cumplen con pruebas automáticas; gana el 50 % si queda implementado pero depende de infraestructura de pago o de validación externa que aún no existe. **Completos (100 %):** los 18 ítems US-001 a US-010 y EN-001, EN-002, EN-004, EN-005, EN-007, EN-008, EN-009 y EN-010. **Parciales (50 %):** EN-003 y EN-006. El crédito se acredita en el sprint donde las pruebas lo verifican ([Revisión del Sprint 4](../03%20Inplementaci%C3%B3n/Sprint%204/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) y [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%204/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md)). El trabajo de calidad, seguridad, Green IT, E2E y despliegue no tenía puntos y **no se acredita**: es un criterio conservador.
4. **AC:** dedicación planificada constante: BAC × semanas transcurridas desde el 01/09/2026 ÷ 14 semanas presupuestadas.
5. **Sprints:** el proyecto tiene cuatro; el cuarto se extiende hasta la fecha de corte.

## 6. Historia por sprint (comparación histórica)

| Sprint (fin) | PV acumulado | EV acumulado | AC acumulado | SV | CV | SPI | CPI |
|---|---|---|---|---|---|---|---|
| Sprint 1 (22/09) | 4.648,76 | 2.033,83 | 4.814,79 | −2.614,93 | −2.780,95 | 0,438 | 0,422 |
| Sprint 2 (06/10) | 13.171,48 | 2.324,38 | 8.024,64 | −10.847,10 | −5.700,26 | 0,176 | 0,290 |
| Sprint 3 (20/10) | 18.207,64 | 2.614,93 | 11.234,50 | −15.592,71 | −8.619,57 | 0,144 | 0,233 |
| **Sprint 4 (28/11)** | **22.469,00** | **21.209,96** | **20.176,24** | **−1.259,04** | **+1.033,72** | **0,944** | **1,051** |

El desempeño tocó fondo en el Sprint 3 (SPI 0,144 y CPI 0,233) y se recuperó en el Sprint 4 al atacar la ruta crítica y el resto del alcance. La acción correctiva funcionó, pero llegó tarde: el cronograma se cumplió con 12 a 54 días de retraso por hito. Los gráficos están en los [Tableros de Control](04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md).

## Referencias cruzadas

- Estado: [Reporte de Estado](01%20Reporte%20de%20Estado%20V_1_0_0.md) · Variación: [Reporte de Variación](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md) · Visualización: [Tableros de Control](04%20Tableros%20de%20Control%20-%20H%C3%ADbridos%20V_1_0_0.md).
- Riesgos relacionados: RSK-05, RSK-09, RSK-17 y RSK-18 en el [Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
