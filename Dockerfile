# USAR UNA IMAGEN BASE LIGERA
FROM python:3.11-slim

# EVITAR QUE PYTHON GENERE ARCHIVOS .pyc Y HABILITAR LOGS EN TIEMPO REAL
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ESTABLECER DIRECTORIO DE TRABAJO
WORKDIR /app

# INSTALAR DEPENDENCIAS DE SISTEMA MÍNIMAS
# libpq-dev es necesario para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# COPIAR SOLO LOS REQUERIMIENTOS PRIMERO (PARA APROVECHAR CACHÉ DE DOCKER)
COPY requirements.txt .

# INSTALAR DEPENDENCIAS DE PYTHON
# --no-cache-dir reduce el tamaño de la imagen significativamente
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# COPIAR EL RESTO DEL PROYECTO
COPY . .

# EXPONER EL PUERTO (Railway inyecta la variable $PORT)
ENV PORT 8000
EXPOSE 8000

# COMANDO PARA INICIAR LA APLICACIÓN
# Usamos uvicorn directamente apuntando al main de logica_negocio
CMD uvicorn logica_negocio.main:app --host 0.0.0.0 --port ${PORT:-8000}
