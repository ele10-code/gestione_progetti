FROM python:3.8-slim-buster

# Imposta variabili d'ambiente per ridurre l'output dei log di Python e non creare file .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia solo il file requirements.txt inizialmente
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'applicazione
COPY . .

EXPOSE 5000

# Usa un utente non-root per eseguire l'applicazione
RUN useradd -m myuser
USER myuser

CMD ["python", "app.py"]