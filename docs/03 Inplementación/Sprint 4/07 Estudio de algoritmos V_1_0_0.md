# Estudio comparativo de algoritmos de rutas (spike EN-001)

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4  
**Fecha de la medición:** 24/11/2026  
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Matriz de cumplimiento](06%20Matriz%20de%20cumplimiento%20V_1_0_0.md)

## Resumen en una mirada

| Pregunta | Respuesta |
|---|---|
| ¿Qué se comparó? | Cuatro formas de armar las rutas de reparto: **Clarke-Wright con 2-opt** (el motor del producto), ese mismo más **búsqueda tabú**, un **algoritmo genético** y **Google OR-Tools** |
| ¿Quién ganó? | En calidad, la búsqueda tabú y OR-Tools quedan casi empatadas; en tiempo, Clarke-Wright con 2-opt es de 100 a 1.000 veces más rápido |
| ¿Qué se decidió? | Mantener Clarke-Wright con 2-opt como motor por defecto, ofrecer la búsqueda tabú como opción del administrador y dejar OR-Tools solo como referencia de este estudio |
| ¿Por qué? | Cumple de sobra el límite de 45 s, no agrega dependencias a la imagen y la búsqueda tabú mejora hasta un 3 % los kilómetros cuando conviene gastar un poco más de tiempo |

## Glosario

- **Ruta de vehículos con capacidad (CVRP):** decidir qué camión visita qué pedidos y en qué orden para recorrer la menor distancia, sin pasar la capacidad de cada camión.
- **Clarke-Wright:** método clásico que empieza con un viaje por pedido y va uniendo viajes mientras ahorre distancia.
- **2-opt:** mejora que invierte tramos de una ruta mientras la haga más corta.
- **Búsqueda tabú:** mejora que mueve un pedido de una ruta a otra y recuerda los movimientos recientes para no volver atrás.
- **Algoritmo genético:** imita la evolución: combina recorridos "padres" para crear "hijos" y se queda con los mejores.
- **OR-Tools:** biblioteca de Google para problemas de rutas; se usa aquí como referencia de calidad.

## 1. Método

Se generaron instancias reproducibles en Lima (pedidos de 20 a 150 kg, camiones de 1.500 kg, salida y regreso al depósito) de **50, 150 y 400 pedidos**, con **3 semillas** por tamaño. Cada algoritmo tuvo como máximo **10 segundos** por corrida. Se verificó que todos cubrieran cada pedido una sola vez y respetaran la capacidad. Las ventanas horarias no se incluyeron porque OR-Tools las trata distinto; las restricciones propias del producto (ventanas, volumen y zonas protegidas) las aplica el motor y se prueban aparte.

Reproducir: `python scripts/spike_algoritmos.py --tamanos 50 150 400 --semillas 3 --limite 10` (para incluir OR-Tools: `pip install ortools`). El código está en [`spike_algoritmos.py`](../../../scripts/spike_algoritmos.py) y las alternativas, en [`algoritmos_alternativos.py`](../../../src/backend/app/algoritmos_alternativos.py).

## 2. Resultados

Promedio de las 3 semillas por tamaño (menos kilómetros es mejor; «vs. base» compara con Clarke-Wright + 2-opt):

| Pedidos | Algoritmo | Km totales | vs. base | Tiempo (s) | Rutas |
|---|---|---|---|---|---|
| 50 | Clarke-Wright + 2-opt (base) | 176,8 | 0,0 % | 0,00 | 3,3 |
| 50 | + búsqueda tabú | 175,7 | -0,6 % | 0,07 | 3,3 |
| 50 | Algoritmo genético | 195,9 | +10,8 % | 1,98 | 3,3 |
| 50 | OR-Tools (búsqueda local guiada) | 176,0 | -0,5 % | 10,26 | 3,3 |
| 150 | Clarke-Wright + 2-opt (base) | 375,8 | 0,0 % | 0,01 | 9,0 |
| 150 | + búsqueda tabú | 364,7 | -3,0 % | 0,30 | 9,0 |
| 150 | Algoritmo genético | 581,5 | +54,7 % | 4,86 | 9,0 |
| 150 | OR-Tools (búsqueda local guiada) | 367,8 | -2,1 % | 10,00 | 9,0 |
| 400 | Clarke-Wright + 2-opt (base) | 763,5 | 0,0 % | 0,08 | 23,0 |
| 400 | + búsqueda tabú | 759,6 | -0,5 % | 1,36 | 23,0 |
| 400 | Algoritmo genético | 2.643,3 | +246,2 % | 10,00 | 23,3 |
| 400 | OR-Tools (búsqueda local guiada) | 805,4 | +5,5 % | 10,01 | 23,0 |

## 3. Análisis

- **Clarke-Wright + 2-opt** resuelve 400 pedidos en 0,08 s. Su calidad es buena porque parte de una construcción pensada para este problema.
- **La búsqueda tabú** lo mejora entre 0,5 % y 3,0 % con pocas décimas de segundo; es la mejora más barata y por eso se ofrece como opción.
- **El algoritmo genético** queda muy por debajo: con rutas gigantes y una división simple por capacidad necesita muchas más generaciones de las que cabe en 10 s; empeora al crecer el problema. Con otro diseño (por ejemplo, con la división óptima de Prins) podría mejorar, pero no compensa frente a las alternativas.
- **OR-Tools** iguala a la búsqueda tabú con 50 y 150 pedidos, pero usa los 10 s completos y con 400 pedidos queda un 5,5 % peor en ese tiempo. Además es una dependencia grande (decenas de megabytes) que iría contra la imagen única y liviana del proyecto (Green IT).

## 4. Decisión

1. El motor por defecto sigue siendo **Clarke-Wright + 2-opt**: cumple el límite de 45 s (RNF-001) con 1.000 pedidos en alrededor de 1 s.
2. La **búsqueda tabú** queda disponible: el administrador la activa en *Administración → Parámetros del algoritmo*, sin tocar los módulos de pedidos, flota ni dashboard (RNF-005).
3. **OR-Tools** y el **algoritmo genético** quedan solo para este estudio.

## 5. Limitaciones

- Distancias en línea recta, sin tráfico ni red vial, y una sola clase de camión.
- Instancias aleatorias: con pedidos agrupados en zonas, las diferencias pueden cambiar.
- Solo tres semillas por tamaño; es un estudio de decisión, no una comparación estadística.

## Referencias cruzadas

- Requisitos: RNF-001 y RNF-005 en [07. Requisitos no funcionales](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md). Riesgo: RSK-05 en el [Registro de riesgos](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
- Motor y decisiones de diseño: [10. Stack tecnológico, sección 7](../../01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 28/11/2026 | Primera versión: comparación de cuatro algoritmos con tres tamaños y tres semillas, y decisión de diseño. |
