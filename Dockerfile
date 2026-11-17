# Imagen de producción de EcoLogística Lima: la API (FastAPI) sirve también el frontend compilado.
# Construcción en dos etapas: la primera compila el frontend; la segunda deja solo lo necesario para ejecutar.

# ── Etapa 1: compilar el frontend (React + Vite) ──────────────────────────────
FROM node:22-slim AS frontend
WORKDIR /app/src/frontend
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm ci
COPY src/frontend ./
# Mismo origen que la API: el frontend llama a rutas relativas (/api/...).
ENV VITE_API_URL=""
RUN npm run build

# ── Etapa 2: imagen final de ejecución (Python) ───────────────────────────────
FROM python:3.12-slim
WORKDIR /app

COPY src/backend/requirements.txt src/backend/requirements.txt
RUN pip install --no-cache-dir -r src/backend/requirements.txt

COPY src/backend src/backend
COPY --from=frontend /app/src/frontend/dist src/frontend/dist

# Usuario sin privilegios: el proceso no corre como root.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

ENV PYTHONPATH=/app/src/backend \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,os;urllib.request.urlopen('http://localhost:'+os.environ.get('PORT','8000')+'/api/health',timeout=3)"

# SECRET_KEY, SEED_DEMO_DATA y DATABASE_URL se definen como variables de entorno del servicio.
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
