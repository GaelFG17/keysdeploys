# Imagen base de Python
FROM python:3.11-slim

# Instalar dependencias de sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libgthread-2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para Flask
EXPOSE 8080

# Comando para iniciar la aplicación
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
