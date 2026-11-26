/* Service worker de EcoLogística Lima (RNF-010): la aplicación abre y se usa sin conexión.
 *
 * - Navegaciones: red primero y, si falla, la versión guardada del shell de la aplicación.
 * - Archivos estáticos (/assets, /img, manifiesto): caché primero.
 * - Teselas del mapa de OpenStreetMap: caché primero, con un tope de entradas.
 * - API (/api/*): nunca se guarda aquí; la aplicación mantiene su propia cola de acciones y la última ruta.
 */
const VERSION = 'ecologistica-v4';
const TESELAS = 'ecologistica-teselas-v1';
const MAX_TESELAS = 300;
// El servidor añade «Vary» (CORS, compresión): se ignora para que una petición de módulo coincida con lo ya guardado.
const COINCIDIR = { ignoreVary: true };

self.addEventListener('install', (evento) => {
  evento.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    await cache.addAll(['/', '/manifest.webmanifest', '/img/icono-192.png']);
    // precache.json lo genera la compilación con los módulos de la app del conductor; si falta, se sigue con lo básico.
    try {
      const lista = await (await fetch('/precache.json', { cache: 'no-store' })).json();
      await Promise.all(lista.map((u) => cache.add(u).catch(() => undefined)));
    } catch {
      /* sin lista: el shell y lo que cargue la página se guardan por el mensaje o al usarse */
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((claves) => Promise.all(claves.filter((k) => k !== VERSION && k !== TESELAS).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

// La página envía la lista de recursos que ya cargó para guardarlos y poder reabrir la aplicación sin red.
self.addEventListener('message', (evento) => {
  if (!evento.data || evento.data.tipo !== 'cachear') return;
  const urls = (evento.data.urls || []).filter((u) => typeof u === 'string' && u.startsWith('/') && !u.startsWith('/api/'));
  evento.waitUntil(caches.open(VERSION).then((c) => Promise.all(urls.map((u) => c.add(u).catch(() => undefined)))));
});

async function limitar(nombre, maximo) {
  const cache = await caches.open(nombre);
  const claves = await cache.keys();
  if (claves.length > maximo) await Promise.all(claves.slice(0, claves.length - maximo).map((k) => cache.delete(k)));
}

self.addEventListener('fetch', (evento) => {
  const peticion = evento.request;
  if (peticion.method !== 'GET') return;
  const url = new URL(peticion.url);

  if (url.hostname.endsWith('.tile.openstreetmap.org')) {
    evento.respondWith(
      caches.open(TESELAS).then(async (cache) => {
        const guardada = await cache.match(peticion);
        if (guardada) return guardada;
        try {
          const respuesta = await fetch(peticion);
          cache.put(peticion, respuesta.clone());
          limitar(TESELAS, MAX_TESELAS);
          return respuesta;
        } catch {
          return Response.error();
        }
      }),
    );
    return;
  }

  if (url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;

  if (peticion.mode === 'navigate') {
    evento.respondWith(
      fetch(peticion).catch(() => caches.match('/', COINCIDIR).then((r) => r || Response.error())),
    );
    return;
  }

  if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/img/') || url.pathname === '/manifest.webmanifest') {
    evento.respondWith(
      caches.match(peticion, COINCIDIR).then((guardada) => guardada || fetch(peticion).then((respuesta) => {
        const copia = respuesta.clone();
        if (respuesta.ok) caches.open(VERSION).then((c) => c.put(peticion, copia));
        return respuesta;
      })),
    );
  }
});
