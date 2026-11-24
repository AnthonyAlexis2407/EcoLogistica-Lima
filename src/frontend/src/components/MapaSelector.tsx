/**
 * MapaSelector — elige una ubicación tocando el mapa (RF-002). Es un complemento: los campos de latitud y longitud
 * del formulario siguen siendo la vía accesible por teclado y se mantienen sincronizados con el marcador.
 */

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Props {
  latitud: number;
  longitud: number;
  onElegir: (latitud: number, longitud: number) => void;
}

export default function MapaSelector({ latitud, longitud, onElegir }: Props) {
  const contenedor = useRef<HTMLDivElement | null>(null);
  const mapa = useRef<L.Map | null>(null);
  const marcador = useRef<L.CircleMarker | null>(null);
  const alElegir = useRef(onElegir);

  useEffect(() => {
    alElegir.current = onElegir;
  }, [onElegir]);

  useEffect(() => {
    if (!contenedor.current || mapa.current) return;
    const m = L.map(contenedor.current, { scrollWheelZoom: false }).setView([latitud, longitud], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(m);
    marcador.current = L.circleMarker([latitud, longitud], { radius: 9, color: '#047857', fillColor: '#10b981', fillOpacity: 0.9 }).addTo(m);
    m.on('click', (e: L.LeafletMouseEvent) => alElegir.current(Number(e.latlng.lat.toFixed(5)), Number(e.latlng.lng.toFixed(5))));
    mapa.current = m;
    return () => {
      m.remove();
      mapa.current = null;
      marcador.current = null;
    };
    // El mapa se crea una sola vez; los cambios de coordenadas se aplican en el efecto siguiente.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!mapa.current || !marcador.current || Number.isNaN(latitud) || Number.isNaN(longitud)) return;
    marcador.current.setLatLng([latitud, longitud]);
    mapa.current.panTo([latitud, longitud]);
  }, [latitud, longitud]);

  return <div ref={contenedor} className="mapa-selector" role="region" aria-label="Mapa para elegir la ubicación de entrega" />;
}
