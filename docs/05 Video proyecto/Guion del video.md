[← Volver al README principal](../../README.md)

# Guion del video del proyecto (MP4 de 5 minutos)

**Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.
**Archivo a entregar en esta carpeta:** `Video proyecto EcoLogistica Lima.mp4` (formato MP4, 5 minutos con una tolerancia de ±15 segundos).
**Versión del documento:** 1.1.0 · **Fecha:** 28/11/2026

> **Para qué sirve esta guía.** La consigna final pide un video de unos 5 minutos con dos partes continuas: **1 minuto** de presentación de la idea (*elevator pitch*) y **4 minutos** de demostración técnica en vivo. Esta guía dice qué decir, qué mostrar y en qué segundo, y trae una lista para revisar el archivo antes de subirlo. El video lo graba el equipo; esta carpeta debe contener el `.mp4` final.

## 1. Resumen del video

| Parte | Minuto | Contenido |
|---|---|---|
| **Presentación de la idea** | 0:00 a 1:00 | Problema, solución, propuesta de valor y público objetivo |
| **Demostración funcional** | 1:00 a 5:00 | Recorrido por el sistema desplegado: acceso, pedidos, rutas con mapa, app del conductor sin conexión, re-optimización, avisos a la bodega, indicadores y reportes, calidad y despliegue |

**Entorno de grabación.** Usar la aplicación en producción, <https://ecologistica-lima.onrender.com>, con las cuentas de demostración que crea el archivo [`seed.py`](../../src/backend/app/seed.py). Abrir la página **1 minuto antes de grabar**: el plan gratuito de Render se duerme tras 15 minutos sin uso y la primera visita puede tardar hasta 1 minuto.

## 2. Guion minuto a minuto

### Parte 1: presentación de la idea (0:00 a 1:00)

| Tiempo | Qué se ve | Qué se dice (texto sugerido) |
|---|---|---|
| 0:00 a 0:15 | Portada con el nombre del proyecto y el equipo | "Somos Fernandez, Perez y Tovar, y presentamos **EcoLogística Lima**, un optimizador de rutas sostenibles para DistriRápido." |
| 0:15 a 0:30 | Mapa de Lima con muchas entregas | "DistriRápido reparte pedidos de última milla con rutas hechas a mano: recorren más kilómetros de los necesarios, emiten más CO₂ y no siempre llegan en la ventana horaria de cada bodega." |
| 0:30 a 0:45 | Pantalla de rutas optimizadas | "Nuestra solución es una aplicación web que **planifica las rutas** con un algoritmo de optimización, las muestra en un mapa y **mide el CO₂ que se evita**." |
| 0:45 a 1:00 | Indicador de CO₂ evitado y árboles equivalentes | "La propuesta de valor es menos kilómetros, menos emisiones y entregas a tiempo. Está pensada para operadores logísticos, administradores de flota y bodegas. Veamos cómo funciona." |

### Parte 2: demostración funcional (1:00 a 5:00)

| Tiempo | Qué se muestra | Qué se dice y se hace |
|---|---|---|
| **1:00 a 1:20** Acceso y roles | Inicio de sesión como **administrador de flota**; el Dashboard con sus filtros por distrito y fechas | "Entramos como administrador. Cada rol ve solo lo que le corresponde: el menú lo muestra, y el servidor lo exige." |
| **1:20 a 1:50** Pedidos (RF-002) | Cerrar sesión y entrar como **operador**; Pedidos → **Registrar Pedido**: elegir la ubicación tocando el mapa, peso, volumen y ventana horaria | "El operador registra pedidos y elige la ubicación en un mapa. Si el peso o el volumen exceden la flota, el sistema lo rechaza." |
| **1:50 a 2:25** Rutas y mapa (RF-003, RF-004) | Rutas → **Optimizar rutas**: rutas, kilómetros, **CO₂ evitado**, árboles equivalentes y tiempo de cálculo; el mapa; asignar un conductor y **Iniciar** | "Un clic planifica todos los pedidos respetando capacidad, ventanas horarias y Pico y Placa. Calcula en milisegundos frente al límite de 45 segundos. Asignamos un conductor y la ruta sale." |
| **2:25 a 3:10** App del conductor (RF-008, RNF-004, RNF-010) | Abrir `/conductor` en una ventana angosta o en el móvil; **Entregar** → un trazo de firma → **Confirmar**; apagar la red en las herramientas del navegador, entregar otra parada y mostrar «pendiente de sincronizar»; volver a encender la red | "El conductor entrega en tres toques con firma. Sin señal, la entrega queda guardada en el dispositivo y se envía sola al volver la red, sin duplicarse." |
| **3:10 a 3:35** Re-optimización (RF-007) | Rutas → **Incidencia** → vía cerrada junto a una parada: mostrar el aviso con el tiempo de recálculo y el pedido devuelto a pendiente | "Si se cierra una vía, el sistema recalcula lo que falta de la ruta, evitando el área, en una fracción de segundo." |
| **3:35 a 4:05** Avisos, indicadores y reportes (RF-009, RF-005, RF-006, RF-010) | Entrar como **bodega** y ver los avisos con la hora estimada; terminar la ruta como conductor; Dashboard con la compensación confirmada; descargar el reporte en **Excel** y en **PDF** | "La bodega recibe sus avisos. Al terminar la ruta se registra el CO₂ evitado y su equivalente en árboles. Los reportes salen en CSV, Excel y PDF; el auditor los recibe sin direcciones." |
| **4:05 a 4:40** Calidad, seguridad y despliegue | Pestaña **Actions** de GitHub con los flujos en verde (incluidos PostgreSQL y conmutación por falla); informe de Playwright; README | "Cada cambio pasa por flujos automáticos de calidad, pruebas y despliegue. Tenemos 175 pruebas de backend con 93 % de cobertura, más pruebas contra PostgreSQL real, 108 de frontend y {E2E} ejecuciones de extremo a extremo en tres navegadores, con accesibilidad y seguridad verificadas. Los datos personales están cifrados." |
| **4:40 a 5:00** Cierre | Pantalla final con la URL y el repositorio | "Entregamos un producto completo, probado y desplegado. Lo que falta depende de una plataforma de pago y de usuarios reales, y está documentado. Gracias." |

## 3. Preparación antes de grabar

- [ ] Abrir la aplicación en producción 1 minuto antes (para que Render esté despierto).
- [ ] Tener **pedidos pendientes** y **vehículos disponibles con factor de emisión** para que "Optimizar rutas" muestre resultados (registrar 5 a 8 pedidos con coordenadas distintas de Lima).
- [ ] Tener a mano las cuentas de **operador**, **conductor** y **bodega** del seed y dos ventanas del navegador (una de ellas angosta, para el móvil); ensayar apagar y encender la red en las herramientas del navegador.
- [ ] Cerrar notificaciones, otras pestañas y ventanas; usar el navegador a pantalla completa con zoom del 100 %.
- [ ] Probar el micrófono: sin ruido y volumen constante.
- [ ] Ensayar con el cronómetro: la presentación no debe pasar de 1 minuto ni la demostración de 4.

## 4. Lista de verificación del archivo final

| Requisito de la consigna | Cómo comprobarlo |
|---|---|
| Formato `.mp4` | La extensión del archivo es `.mp4` y se reproduce en el navegador |
| Duración de 5 minutos (±15 s para el nivel más alto) | Propiedades del archivo: entre 4:45 y 5:15 |
| Dos segmentos continuos (1 min + 4 min) | La presentación termina cerca del minuto 1:00 y la demostración empieza sin cortes |
| Audio claro e imagen HD | Resolución de 1080p (1920×1080) y voz audible sin ruido |
| Demostración con flujos reales e integración frontend-backend | Se ven el registro de datos, la optimización y el resultado, con la aplicación en producción |
| Ubicación y nombre | `docs/05 Video proyecto/Video proyecto EcoLogistica Lima.mp4` |
| Peso razonable | Menos de 100 MB (GitHub admite archivos de hasta 100 MB); si pesa más, exportar a 1080p con una tasa de bits de 4 a 6 Mbps o usar Git LFS |

## 5. Cómo subir el video

```bash
git add "docs/05 Video proyecto/Video proyecto EcoLogistica Lima.mp4"
git commit -m "docs(cierre): video del proyecto (presentacion y demostracion)"
git push
```

Después, agregar al README un enlace al archivo en la sección "Fase 04: Cierre del proyecto".

## Referencias cruzadas

- Consigna del cierre y entregables: [Reporte Final del Proyecto](../04%20Cierre/06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md).
- Riesgo asociado: RSK-15 en el [Registro de riesgos](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).
- Qué se muestra y cómo se verificó cada requisito: [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Etapa%20final/06%20Matriz%20de%20cumplimiento%20V_1_0_0.md).
