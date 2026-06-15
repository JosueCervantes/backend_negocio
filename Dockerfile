FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

# Set work directory
WORKDIR /usr/src/app

# Copy requirements.txt
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Puerto para el servicio
EXPOSE 8000
# Comando para ejecutar el servicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]