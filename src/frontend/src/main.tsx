import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// PWA (RNF-010): el service worker guarda la aplicación para abrirla sin conexión. Solo en producción: en desarrollo
// interferiría con la recarga en caliente de Vite.
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      /* sin service worker la aplicación sigue funcionando con conexión */
    });
    // Se guardan los recursos ya cargados (JS, CSS, imágenes) para poder reabrir la aplicación sin red.
    navigator.serviceWorker.ready.then((registro) => {
      const urls = performance.getEntriesByType('resource')
        .map((e) => new URL(e.name))
        .filter((u) => u.origin === location.origin)
        .map((u) => u.pathname);
      registro.active?.postMessage({ tipo: 'cachear', urls: ['/', ...urls] });
    }).catch(() => {});
  });
}
