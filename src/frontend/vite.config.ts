import { defineConfig } from 'vitest/config'
import type { Plugin } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Optimiza el HTML compilado para el primer pintado (Informe Green IT, FCP y LCP):
 *
 * 1. Incrusta la hoja de estilos en index.html: sin segunda petición ni recurso que bloquee el renderizado.
 * 2. No pide el JavaScript de la aplicación hasta que el navegador informa el primer pintado
 *    (`PerformanceObserver` de tipo `paint`, con respaldo a los 3 s). El HTML ya trae la pantalla de
 *    bienvenida, de modo que el JavaScript nunca compite con el primer pintado; después se precarga
 *    todo el grafo de módulos en paralelo y se importa la entrada.
 *
 * Los módulos que Vite precarga (`modulepreload`) se retiran del HTML y se listan en una etiqueta
 * `meta`, que el script en línea lee. El servidor calcula el hash CSP de ese script al montar el frontend.
 */
function optimizarPrimerPintado(): Plugin {
  const arranque =
    "(function(){var m=document.querySelector('meta[name=precarga]').content.split(','),ok=0;" +
    "function ir(){if(ok++)return;m.forEach(function(h){var l=document.createElement('link');" +
    "l.rel='modulepreload';l.crossOrigin='';l.href=h;document.head.appendChild(l)});import(m[m.length-1])}" +
    "try{new PerformanceObserver(function(l,o){if(l.getEntriesByName('first-contentful-paint').length)" +
    "{o.disconnect();setTimeout(ir)}}).observe({type:'paint',buffered:true});setTimeout(ir,3000)}" +
    "catch(e){addEventListener('load',ir)}})()"
  return {
    name: 'optimizar-primer-pintado',
    apply: 'build',
    transformIndexHtml: {
      order: 'post',
      handler(html, contexto) {
        const paquete = contexto.bundle
        const entrada = contexto.chunk?.fileName
        if (!paquete || !entrada) return html
        let resultado = html.replace(/<link rel="stylesheet"[^>]*href="\/?(assets\/[^"]+\.css)"[^>]*>/g, (enlace, ruta: string) => {
          const recurso = paquete[ruta]
          if (!recurso || recurso.type !== 'asset') return enlace
          delete paquete[ruta] // ya no se publica como archivo aparte
          return `<style>${String(recurso.source)}</style>`
        })
        const precargados = [...resultado.matchAll(/<link rel="modulepreload"[^>]*href="(\/assets\/[^"]+)"[^>]*>\s*/g)].map((m) => m[1])
        resultado = resultado.replace(/<link rel="modulepreload"[^>]*>\s*/g, '')
        const modulos = [...precargados.filter((m) => m !== `/${entrada}`), `/${entrada}`].join(',')
        const etiqueta = new RegExp(`<script type="module"[^>]*src="/${entrada.replace('.', '\\.')}"[^>]*></script>`)
        return resultado.replace(etiqueta, `<meta name="precarga" content="${modulos}">\n    <script>${arranque}</script>`)
      },
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), optimizarPrimerPintado()],
  build: {
    rollupOptions: {
      output: {
        // react y el router cambian poco: un chunk aparte se conserva en caché entre versiones.
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/__tests__/**', 'src/main.tsx', 'src/**/*.d.ts'],
    },
  },
})
