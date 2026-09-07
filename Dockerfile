# Imagen base oficial de Python 3.11
FROM python:3.11-slim

# Variables de entorno para Python y Cloud Run
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Instalar dependencias del sistema para OpenCV y procesamiento
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer puerto de Cloud Run
EXPOSE 8080

# Iniciar Gunicorn escuchando en el puerto definido por Cloud Run
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 0 portafolios.wsgi:application
