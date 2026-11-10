/**
 * Paginador — navegación por bloques de registros (Informe Green IT, optimización 2).
 */

interface PaginadorProps {
  page: number;
  total: number;
  pageSize: number;
  onChange: (page: number) => void;
}

export default function Paginador({ page, total, pageSize, onChange }: PaginadorProps) {
  const totalPaginas = Math.max(1, Math.ceil(total / pageSize));
  if (total <= pageSize) return null;

  return (
    <nav
      aria-label="Paginación"
      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', gap: '0.75rem', flexWrap: 'wrap' }}
    >
      <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
        Página {page} de {totalPaginas} · {total} registros
      </span>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => onChange(page - 1)} disabled={page <= 1}>
          Anterior
        </button>
        <button className="btn btn-ghost btn-sm" onClick={() => onChange(page + 1)} disabled={page >= totalPaginas}>
          Siguiente
        </button>
      </div>
    </nav>
  );
}
