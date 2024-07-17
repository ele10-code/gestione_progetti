# Usa un'immagine base Python
FROM python:3.10-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i file requirements.txt e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'applicazione nel container
COPY . .

# Espone la porta su cui gira l'applicazione
EXPOSE 5000

# Comando per eseguire l'applicazione
CMD ["python", "src/app.py"]
