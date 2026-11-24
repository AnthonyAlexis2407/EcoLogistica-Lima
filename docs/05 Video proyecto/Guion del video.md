[← Volver al README principal](../../README.md)

# Guion del video del proyecto (MP4 de 5 minutos)

**Proyecto:** EcoLogística Lima - Optimizador de Rutas Sostenibles para DistriRápido S.A.C.
**Archivo a entregar en esta carpeta:** `Video proyecto EcoLogistica Lima.mp4` (formato MP4, 5 minutos con una tolerancia de ±15 segundos).
**Versión del documento:** 1.0.0 · **Fecha:** 24/11/2026

> **Para qué sirve esta guía.** La consigna final pide un video de unos 5 minutos con dos partes continuas: **1 minuto** de presentación de la idea (*elevator pitch*) y **4 minutos** de demostración técnica en vivo. Esta guía dice qué decir, qué mostrar y en qué segundo, y trae una lista para revisar el archivo antes de subirlo. El video lo graba el equipo; esta carpeta debe contener el `.mp4` final.

## 1. Resumen del video

| Parte | Minuto | Contenido |
|---|---|---|
| **Presentación de la idea** | 0:00 a 1:00 | Problema, solución, propuesta de valor y público objetivo |
| **Demostración funcional** | 1:00 a 5:00 | Recorrido por el sistema desplegado: acceso, flota, pedidos, rutas con mapa, indicadores y reportes, calidad y despliegue |

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
| **1:00 a 1:25** Acceso y roles | Pantalla de inicio de sesión; entrar como **administrador de flota**; mostrar el Dashboard | "Entramos con un usuario de **administrador de flota**. Cada rol ve solo lo que le corresponde: el menú lo muestra." |
| **1:25 a 2:05** Flota (RF-001) | Vehículos → **Registrar Vehículo**: placa, capacidad, combustible y factor de CO₂; guardar y ver la fila | "Registramos un vehículo con su capacidad y su factor de emisión. Si repito la placa, el sistema la rechaza. Sin factor de emisión, el planificador no lo usa." |
| **2:05 a 2:40** Pedidos (RF-002) | Cerrar sesión y entrar como **operador**; Pedidos → **Registrar Pedido**: dirección, coordenadas (con su ayuda de formato), peso y ventana; ver estado PENDIENTE | "El operador registra pedidos con su ubicación, peso y ventana horaria. Si el peso excede la flota, el sistema lo rechaza con un mensaje claro." |
| **2:40 a 3:35** Rutas y mapa (RF-003, RF-004) | Rutas → **Optimizar rutas**: resultados (rutas, kilómetros, **CO₂ evitado**, árboles equivalentes, tiempo de cálculo en milisegundos); recorrer el mapa y una tabla de paradas con "En ventana" | "Un clic planifica todos los pedidos pendientes. Calculó las rutas en milisegundos, frente al límite de 45 segundos. Cada color es una ruta; el mapa y la tabla muestran el orden de las paradas y si llegan dentro de su ventana. Los vehículos con Pico y Placa quedan fuera y el sistema lo informa." |
| **3:35 a 4:10** Indicadores y reportes (RF-005, RF-006, RF-010) | Dashboard con "Rutas y compensación de carbono"; en Rutas, pulsar **Pedidos (CSV)** y abrir el archivo | "El dashboard resume kilómetros, CO₂ evitado acumulado y su equivalente en árboles. Los reportes se descargan en CSV y se abren en Excel." |
| **4:10 a 4:40** Calidad y despliegue | Pestaña **Actions** de GitHub con los cuatro flujos en verde; informe de Playwright (152 ejecuciones); README con los índices | "Cada cambio pasa por tres flujos automáticos: calidad, pruebas y despliegue. Tenemos 96 pruebas de backend con 94 % de cobertura, 81 de frontend y 152 ejecuciones de extremo a extremo en tres navegadores, todas en verde. Al fusionar a `main`, la aplicación se publica sola." |
| **4:40 a 5:00** Cierre | Pantalla final con la URL y el repositorio | "Entregamos un producto operativo, probado y desplegado. Lo pendiente está documentado en los reportes de cierre. Gracias." |

## 3. Preparación antes de grabar

- [ ] Abrir la aplicación en producción 1 minuto antes (para que Render esté despierto).
- [ ] Tener **pedidos pendientes** y **vehículos disponibles con factor de emisión** para que "Optimizar rutas" muestre resultados (registrar 5 a 8 pedidos con coordenadas distintas de Lima).
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
- Qué se muestra y cómo se verificó cada requisito: [Matriz de cumplimiento](../03%20Inplementaci%C3%B3n/Sprint%205/01%20Matriz%20de%20cumplimiento%20V_1_0_0.md).
