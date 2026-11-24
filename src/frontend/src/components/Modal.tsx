/**
 * Modal accesible (RNF-007, WCAG 2.1.2 y 2.4.3): atrapa el foco dentro del diálogo, lo devuelve al elemento que lo abrió
 * al cerrarse y se cierra con Escape. Usa `role="dialog"` y `aria-modal` con un título que lo nombra.
 */

import { useEffect, useRef, type ReactNode } from 'react';
import { X } from 'lucide-react';

const FOCALIZABLES =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

interface ModalProps {
  titulo: string;
  onCerrar: () => void;
  children: ReactNode;
  pie?: ReactNode;
  ancho?: number;
}

export default function Modal({ titulo, onCerrar, children, pie, ancho }: ModalProps) {
  const dialogo = useRef<HTMLDivElement | null>(null);
  const idTitulo = `modal-${titulo.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;

  useEffect(() => {
    const previo = document.activeElement as HTMLElement | null;
    const nodo = dialogo.current;
    const enfocables = () => Array.from(nodo?.querySelectorAll<HTMLElement>(FOCALIZABLES) ?? []);
    // El foco pasa al primer campo (no al botón de cerrar) para que se pueda escribir enseguida.
    const lista = enfocables();
    (lista.find((e) => e.tagName !== 'BUTTON') ?? lista[0])?.focus();

    const alPresionar = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onCerrar();
        return;
      }
      if (e.key !== 'Tab') return;
      const items = enfocables();
      if (items.length === 0) return;
      const primero = items[0];
      const ultimo = items[items.length - 1];
      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault();
        primero.focus();
      }
    };
    document.addEventListener('keydown', alPresionar);
    return () => {
      document.removeEventListener('keydown', alPresionar);
      previo?.focus();
    };
    // Solo al montar: onCerrar puede cambiar de identidad en cada render sin reiniciar el foco.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="modal-overlay" role="presentation" onClick={onCerrar}>
      <div
        className="modal" role="dialog" aria-modal="true" aria-labelledby={idTitulo} ref={dialogo}
        style={ancho ? { maxWidth: ancho } : undefined} onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3 id={idTitulo}>{titulo}</h3>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onCerrar} aria-label="Cerrar ventana" title="Cerrar">
            <X size={18} />
          </button>
        </div>
        {children}
        {pie && <div className="modal-footer">{pie}</div>}
      </div>
    </div>
  );
}
