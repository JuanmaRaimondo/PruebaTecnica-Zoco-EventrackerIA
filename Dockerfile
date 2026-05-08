# Usamos la imagen oficial de Microsoft Playwright para Python
# Esta imagen ya viene con todas las dependencias de sistema para correr navegadores
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# 1. Copiamos e instalamos las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Instalamos el navegador Chromium (versión ligera)
RUN playwright install chromium

# 3. Copiamos todo tu código al contenedor
COPY . .

# 4. Comando para arrancar
# En Docker no podemos usar el menú interactivo, así que lanzamos 
# directamente la función de automatización que ya tenés en main.py
CMD ["python", "-c", "import asyncio; from main import automatizacion_continua; asyncio.run(automatizacion_continua())"]