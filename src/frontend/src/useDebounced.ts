import { useEffect, useState } from 'react';

/** Devuelve `valor` con retraso: evita una petición por cada tecla en los buscadores. */
export function useDebounced<T>(valor: T, retrasoMs = 300): T {
  const [retrasado, setRetrasado] = useState(valor);
  useEffect(() => {
    const temporizador = setTimeout(() => setRetrasado(valor), retrasoMs);
    return () => clearTimeout(temporizador);
  }, [valor, retrasoMs]);
  return retrasado;
}
