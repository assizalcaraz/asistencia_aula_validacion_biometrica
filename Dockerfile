FROM python:3.10-slim

# Instalar dependencias necesarias para dlib y face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-thread-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto de Django
EXPOSE 8000

# Copiar y dar permisos al script de entrada
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Usar el script como entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto (se puede sobrescribir)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
