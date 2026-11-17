# Evaluación cuantitativa de usabilidad (SUS)

**Nombre del Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Perez Ordoñez Anthony Alexis  
**Sprint:** Sprint 4  
**Fecha de la evaluación:** 16/11/2026  
**Versión del documento:** 1.0.0

[← Volver al README principal](../../../README.md) · [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) · [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md)

## Resumen en una mirada

| Pregunta | Respuesta |
|---|---|
| ¿Qué se midió? | Qué tan fácil de usar es el sistema, según la escala SUS (10 preguntas, valoración de 1 a 5) |
| ¿A cuántas personas? | 8 participantes de los 5 roles del sistema |
| ¿Cuál fue el resultado? | **SUS medio = 79,4 de 100** (intervalo de confianza del 95 %: 69,7 a 89,0) |
| ¿Supera el estándar? | **Sí**: el umbral de aceptación es 68; incluso el límite inferior del intervalo (69,7) lo supera |
| ¿Qué nota recibe? | **A-** en la escala de letras; **"Bueno"** en la escala de adjetivos |
| ¿Qué falló? | El aprendizaje inicial: las personas con poca experiencia puntúan 65 y las de experiencia alta 89 |
| ¿Qué se mejoró? | Se añadió ayuda contextual en los campos de coordenadas y de factor de CO₂ (verificada por prueba automática) |

> **Aviso de transparencia.** Las respuestas de este informe son **simuladas con fines académicos**: las generó el equipo para validar el procedimiento, la hoja de cálculo y el script de puntuación. No provienen de una sesión con usuarios reales. La acción 3 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) las sustituye por respuestas reales ejecutando el mismo script. Los resultados de este documento deben leerse con esa salvedad.

## Glosario

| Término | Significado |
|---|---|
| **SUS** (*System Usability Scale*) | Cuestionario de 10 preguntas que da una nota de 0 a 100 sobre la facilidad de uso de un sistema |
| **Escala Likert 1–5** | 1 = totalmente en desacuerdo, 5 = totalmente de acuerdo |
| **Umbral de aceptación** | Valor de referencia de la industria: una puntuación SUS de 68 o más se considera por encima del promedio |
| **Cuello de botella** | Punto de la interfaz donde las personas se detienen, dudan o se equivocan |
| **Intervalo de confianza** | Rango donde probablemente se encuentra la nota real de toda la población de usuarios |

## 1. Ficha técnica de la evaluación

| Campo | Detalle |
|---|---|
| **Sistema evaluado** | EcoLogística Lima, versión 3.0.0, imagen Docker de producción con datos de demostración ([Guía de despliegue](05%20Gu%C3%ADa%20de%20despliegue.md)) |
| **Instrumento** | System Usability Scale (SUS), Brooke (1996), en su traducción habitual al español |
| **Escala de valoración** | Likert de 5 puntos: 1 (totalmente en desacuerdo) a 5 (totalmente de acuerdo) |
| **Muestra (n)** | 8 participantes (más de los 5 que Nielsen y Landauer recomiendan como mínimo para detectar la gran mayoría de los problemas de usabilidad) |
| **Tipo de muestra** | Por conveniencia, con representación de los 5 roles del sistema |
| **Naturaleza de los datos** | **Simulados con fines académicos** (ver aviso); archivo de origen: [`respuestas_sus.csv`](datos/respuestas_sus.csv) |
| **Procedimiento** | Cada participante ejecuta las tareas de su rol, sin ayuda del evaluador, y después responde las 10 preguntas |
| **Normas de referencia** | ISO 9241-11 (efectividad, eficiencia y satisfacción), ISO/IEC 25010 (característica "Usabilidad") y [RNF-004](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) del proyecto |

### 1.1 Perfil de los participantes

| Participante | Rol en el sistema | Experiencia con sistemas similares |
|---|---|---|
| U01 | Administrador de flota | Alta |
| U02 | Operador logístico | Media |
| U03 | Auditor | Media |
| U04 | Dueño de bodega | Media |
| U05 | Conductor | Baja |
| U06 | Operador logístico | Alta |
| U07 | Administrador de flota | Alta |
| U08 | Dueño de bodega | Baja |

Resumen: 3 con experiencia alta, 3 media y 2 baja; los cinco roles de [08. Usuarios](../../01%20Inicio/08.%20Usuarios%20V_1_0_0.md) están representados.

### 1.2 Tareas ejecutadas antes de responder

Las tareas son las mismas que cubre la suite E2E de [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md), de modo que cada una tiene también una prueba automática.

| N.º | Tarea | Roles |
|---|---|---|
| T1 | Iniciar sesión con su correo y contraseña | Todos |
| T2 | Revisar el Dashboard e identificar cuántos vehículos hay disponibles | Todos |
| T3 | Registrar un vehículo nuevo (placa, capacidad y combustible) | Administrador de flota |
| T4 | Buscar un vehículo por placa y filtrar por estado | Administrador, operador, auditor |
| T5 | Registrar un pedido con dirección, coordenadas, peso y ventana horaria | Operador, dueño de bodega |
| T6 | Cancelar un pedido propio y comprobar que ya no puede cancelarlo otra vez | Operador, dueño de bodega |
| T7 | Consultar la flota y los pedidos sin modificarlos | Conductor, auditor |
| T8 | Cerrar sesión | Todos |

## 2. Cuestionario SUS aplicado

Las preguntas **impares** son positivas y las **pares** son negativas; por eso se puntúan de forma distinta (sección 3).

| N.º | Pregunta | Tipo |
|---|---|---|
| P1 | Creo que me gustaría utilizar este sistema con frecuencia. | Positiva |
| P2 | Encontré el sistema innecesariamente complejo. | Negativa |
| P3 | Pensé que el sistema era fácil de usar. | Positiva |
| P4 | Creo que necesitaría el apoyo de un técnico para poder utilizar este sistema. | Negativa |
| P5 | Encontré que las diversas funciones del sistema estaban bien integradas. | Positiva |
| P6 | Pensé que había demasiada inconsistencia en este sistema. | Negativa |
| P7 | Imagino que la mayoría de las personas aprenderían a utilizar este sistema muy rápidamente. | Positiva |
| P8 | Encontré el sistema muy incómodo de usar. | Negativa |
| P9 | Me sentí muy seguro(a) utilizando el sistema. | Positiva |
| P10 | Necesité aprender muchas cosas antes de poder empezar a utilizar el sistema. | Negativa |

## 3. Resultados cuantitativos

### 3.1 Respuestas brutas (escala 1 a 5)

| Participante | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 |
|---|---|---|---|---|---|---|---|---|---|---|
| U01 | 5 | 1 | 5 | 2 | 4 | 1 | 5 | 1 | 5 | 2 |
| U02 | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 |
| U03 | 4 | 2 | 5 | 1 | 4 | 2 | 4 | 2 | 4 | 3 |
| U04 | 5 | 2 | 4 | 2 | 5 | 1 | 4 | 1 | 4 | 2 |
| U05 | 3 | 3 | 4 | 3 | 3 | 2 | 4 | 2 | 3 | 3 |
| U06 | 4 | 1 | 4 | 2 | 4 | 2 | 5 | 2 | 4 | 2 |
| U07 | 5 | 2 | 5 | 1 | 5 | 1 | 5 | 2 | 5 | 1 |
| U08 | 4 | 2 | 4 | 3 | 4 | 2 | 4 | 2 | 3 | 2 |

### 3.2 Cómo se calcula el puntaje (regla de Brooke)

1. **Preguntas impares (P1, P3, P5, P7, P9):** aportación = respuesta − 1.
2. **Preguntas pares (P2, P4, P6, P8, P10):** aportación = 5 − respuesta.
3. Cada aportación vale entre 0 y 4. **Se suman las 10 aportaciones** (máximo 40).
4. **SUS individual = suma × 2,5** (así la nota queda entre 0 y 100).
5. **SUS global = promedio de los SUS individuales.**

### 3.3 Ejemplo paso a paso (participante U01)

| Pregunta | Respuesta | Regla | Aportación |
|---|---|---|---|
| P1 (impar) | 5 | 5 − 1 | 4 |
| P2 (par) | 1 | 5 − 1 | 4 |
| P3 (impar) | 5 | 5 − 1 | 4 |
| P4 (par) | 2 | 5 − 2 | 3 |
| P5 (impar) | 4 | 4 − 1 | 3 |
| P6 (par) | 1 | 5 − 1 | 4 |
| P7 (impar) | 5 | 5 − 1 | 4 |
| P8 (par) | 1 | 5 − 1 | 4 |
| P9 (impar) | 5 | 5 − 1 | 4 |
| P10 (par) | 2 | 5 − 2 | 3 |
| **Suma** | | | **37** |

SUS de U01 = 37 × 2,5 = **92,5**.

### 3.4 Aportación de cada pregunta y SUS individual de todos los participantes

| Participante | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | Suma | SUS = suma × 2,5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U01 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 37 | **92,5** |
| U02 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 30 | **75,0** |
| U03 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 2 | 31 | **77,5** |
| U04 | 4 | 3 | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 3 | 34 | **85,0** |
| U05 | 2 | 2 | 3 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 24 | **60,0** |
| U06 | 3 | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 32 | **80,0** |
| U07 | 4 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 38 | **95,0** |
| U08 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 2 | 3 | 28 | **70,0** |

### 3.5 Puntaje SUS promedio global

```
SUS global = (92,5 + 75,0 + 77,5 + 85,0 + 60,0 + 80,0 + 95,0 + 70,0) / 8
           = 635,0 / 8
           = 79,375  →  79,4
```

| Indicador | Valor |
|---|---|
| Participantes (n) | 8 |
| **SUS medio** | **79,4** |
| Desviación estándar (muestral) | 11,6 |
| Mínimo / máximo | 60,0 / 95,0 |
| Intervalo de confianza del 95 % | 69,7 a 89,0 (79,375 ± 2,365 × 11,55 / √8) |
| Umbral de aceptación | 68 |
| ¿Supera el umbral? | Sí (+11,4 puntos) |

> Los datos y cálculos se reproducen con un solo comando: `python scripts/calcular_sus.py "docs/03 Inplementación/Sprint 4/datos/respuestas_sus.csv"` ([`calcular_sus.py`](../../../scripts/calcular_sus.py)). Si se cambia el CSV por respuestas reales, el script entrega las mismas tablas.

## 4. Análisis e interpretación

### 4.1 Ubicación frente al estándar

| Referencia | Valor | Lectura |
|---|---|---|
| Promedio de la industria (Sauro y Lewis) | 68 | **Superado** por 11,4 puntos |
| Escala de letras (Sauro y Lewis, 2016) | A- (78,9 a 80,7) | **Nota A-**: usabilidad superior a la gran mayoría de sistemas evaluados |
| Escala de adjetivos (Bangor, Kortum y Miller, 2009) | entre "Bueno" (71,4) y "Excelente" (85,5) | **"Bueno"**, cerca de "Excelente" |
| Aceptabilidad | por encima de 70 | **Aceptable** |

Cómo leer las notas: A es lo mejor y F lo peor. Una A- significa que el sistema es claramente más fácil de usar que el promedio, pero todavía hay margen para llegar a A.

### 4.2 Resultados por pregunta

| Pregunta | Promedio bruto (1–5) | Aportación media (0–4) |
|---|---|---|
| P1 Usaría el sistema con frecuencia | 4,2 | 3,25 |
| P2 Innecesariamente complejo | 1,9 | 3,13 |
| P3 Fácil de usar | 4,4 | 3,38 |
| P4 Necesitaría apoyo técnico | 2,0 | 3,00 |
| P5 Funciones bien integradas | 4,1 | 3,13 |
| P6 Demasiada inconsistencia | 1,6 | 3,38 |
| P7 Se aprende rápido | 4,4 | 3,38 |
| P8 Incómodo de usar | 1,8 | 3,25 |
| P9 Me sentí seguro(a) | 4,0 | 3,00 |
| P10 Necesité aprender muchas cosas | 2,1 | 2,88 |

- **Lo mejor valorado:** facilidad de uso (P3), coherencia de la interfaz (P6) y rapidez de aprendizaje percibida (P7), todas con 3,38 sobre 4.
- **Lo peor valorado:** P10 (2,88), P4 (3,00) y P9 (3,00): lo que se necesita aprender de antemano, la dependencia de apoyo técnico y la confianza al usar.

### 4.3 Por nivel de experiencia

| Experiencia | Participantes | SUS medio |
|---|---|---|
| Alta | U01, U06, U07 | **89,2** |
| Media | U02, U03, U04 | **79,2** |
| Baja | U05, U08 | **65,0** |

La brecha de 24 puntos entre experiencia alta y baja es la señal más importante: el sistema funciona muy bien para quien ya conoce el dominio y se queda justo por debajo del umbral (65 frente a 68) para quien no.

Según el modelo de Lewis y Sauro, las preguntas P4 y P10 miden la **facilidad de aprendizaje** y las otras ocho la **usabilidad general**:

| Dimensión | Puntaje (0–100) |
|---|---|
| Usabilidad general (8 preguntas) | 80,9 |
| Facilidad de aprendizaje (P4 y P10) | 73,4 |

El aprendizaje es, por tanto, la dimensión más débil.

### 4.4 Cuellos de botella de la interfaz

| N.º | Cuello de botella | Evidencia | Dónde ocurre |
|---|---|---|---|
| C1 | **Vocabulario técnico sin explicación** para quien no conoce el dominio | P10 es la pregunta peor valorada; U05 y U08 puntúan 60 y 70 | Campo "Factor Emisión CO₂ (kg/L)" del formulario de vehículos |
| C2 | **Coordenadas escritas a mano** sin indicar formato ni signo | P4 (necesitar apoyo) y P9 (confianza) por debajo del resto | Campos "Latitud" y "Longitud" del formulario de pedidos |
| C3 | **Sin guía de primer uso**: la persona debe descubrir qué hacer | Brecha de experiencia de 24 puntos | Dashboard y listas vacías |
| C4 | **Confianza ante acciones irreversibles** | P9 en 3,00 | Dar de baja un vehículo y cancelar un pedido |

Lo que **no** es un cuello de botella: las pruebas automáticas confirman que la interfaz informa los errores dentro del formulario (placa duplicada, peso excesivo), conserva los datos para corregirlos y no ofrece acciones a los roles que no pueden usarlas ([Análisis Playwright, sección 3](03%20Analisis%20PlayWrigth%20V_1_0_0.md)).

## 5. Mejoras

### 5.1 Mejoras aplicadas en este sprint (verificables)

| Mejora | Cuello que resuelve | Qué cambió | Cómo se verifica |
|---|---|---|---|
| M1: ayuda de formato en coordenadas | C2 | Texto de ayuda bajo "Latitud" y "Longitud": grados decimales, ejemplo de Lima (-12.0464, -77.0428) y aviso del signo negativo; asociado a ambos campos con `aria-describedby` para lectores de pantalla | Prueba E2E "usabilidad (mejora SUS)" en [`pedidos.spec.ts`](../../../src/frontend/e2e/pedidos.spec.ts) |
| M2: explicación del factor de CO₂ | C1 | Texto de ayuda: "Kilogramos de CO₂ por litro. Si no lo conoce, deje el valor sugerido (2.68 para diésel)" | Código en [`VehiculosPage.tsx`](../../../src/frontend/src/pages/VehiculosPage.tsx); estilo `.form-hint` con el mismo color que las etiquetas, cuyo contraste ya cumple WCAG ([Sprint 3, WCAG](../Sprint%2003/05%20WCAG%20V_1_0_0.md)) |

### 5.2 Mejoras propuestas (priorizadas por impacto y esfuerzo)

| Prioridad | Mejora | Cuello | Esfuerzo | Historia relacionada |
|---|---|---|---|---|
| 1 | Selector de ubicación en un mapa (o búsqueda de dirección) en lugar de escribir coordenadas | C2 | Alto | US-007 (mapa interactivo), [Artefactos Jira](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md) |
| 2 | Recorrido de primer uso (3 pasos) y mensajes de lista vacía con un botón de acción ("Registrar el primer vehículo") | C3 | Medio | EN-004 |
| 3 | Mensaje de confirmación más descriptivo en dar de baja y cancelar, indicando qué se conserva ("el registro se conserva como historial") | C4 | Bajo | US-001, US-003 |

### 5.3 Cómo se comprobará la mejora

Repetir la evaluación con las mismas tareas y el mismo script tras las mejoras propuestas. Meta: SUS medio ≥ 82 y SUS de experiencia baja ≥ 68 (acción 5 de la [Retrospectiva](02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md)).

## 6. Limitaciones

- Los datos son simulados (ver aviso al inicio): demuestran el procedimiento, no la opinión de usuarios reales.
- Con n = 8 el intervalo de confianza es amplio (69,7 a 89,0); una muestra mayor lo estrecharía.
- El SUS mide la percepción de facilidad de uso; no mide tiempos ni errores. Esos aspectos los cubren las pruebas de rendimiento y E2E, y [RNF-004](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) (tarea en ≤ 20 s con conductores reales) requerirá la aplicación móvil del conductor, que aún no está construida.

## Referencias

- Brooke, J. (1996). *SUS: A "quick and dirty" usability scale*.
- Bangor, A., Kortum, P. y Miller, J. (2009). *Determining what individual SUS scores mean*. Journal of Usability Studies, 4(3).
- Sauro, J. y Lewis, J. (2016). *Quantifying the User Experience*, 2.ª ed.
- Nielsen, J. y Landauer, T. (1993). *A mathematical model of the finding of usability problems*.
- ISO 9241-11:2018 (usabilidad: efectividad, eficiencia y satisfacción) e ISO/IEC 25010:2023 (calidad del producto).

## Referencias cruzadas

- Requisito de usabilidad: [07. Requisitos no funcionales (RNF-004)](../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) y roles: [08. Usuarios](../../01%20Inicio/08.%20Usuarios%20V_1_0_0.md).
- Accesibilidad (complemento de la usabilidad): [Sprint 3, WCAG](../Sprint%2003/05%20WCAG%20V_1_0_0.md).
- Pruebas automáticas de las mismas tareas: [Análisis Playwright](03%20Analisis%20PlayWrigth%20V_1_0_0.md).
- Resultados del sprint: [Revisión del Sprint](01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).

## Control de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 16/11/2026 | Primera evaluación SUS (datos simulados con fines académicos), análisis, mejoras aplicadas y propuestas. |
