# Gestione Progetti

## Descrizione
Questo progetto è un sistema di gestione progetti, progettato per aiutare gli utenti a creare, gestire e monitorare progetti e task. È stato sviluppato utilizzando Python con il framework Flask e include funzionalità di autenticazione, gestione delle scadenze e assegnazione dei task.

## Struttura delle Cartelle
La struttura delle cartelle del progetto è organizzata come segue:

```
/
|-- src/
    |-- projects/       # Modulo per la gestione dei progetti
    |-- tasks/          # Modulo per la gestione dei task
    |-- users/          # Modulo per la gestione degli utenti
    |-- notifications/  # Modulo per la gestione delle notifiche (non utilizzato qui)
|-- tests/               # Test unitari e di integrazione
|-- scripts/             # Script per la gestione e configurazione del progetto
|-- docker/              # Configurazione per la containerizzazione con Docker
|-- README.md            # File di descrizione del progetto
|-- .github/workflows/   # Configurazione della pipeline CI/CD
    |-- ci.yml           # File di configurazione per GitHub Actions
```

## Requisiti
- Python 3.10
- MySQL 5.7 o superiore
- Docker (opzionale per containerizzazione)
- Git

## Installazione
1. **Clonare il repository:**
   ```bash
   git clone https://github.com/ele10-code/gestione_progetti.git
   cd gestione_progetti
   ```

2. **Creare un ambiente virtuale e attivarlo:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installare le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurare il database:**
   Creare un database MySQL e aggiornare le credenziali nel file `config.py`.

5. **Eseguire le migrazioni del database:**
   ```bash
   flask db upgrade
   ```

## Esecuzione
Per eseguire l'applicazione in ambiente di sviluppo:
```bash
flask run
```

## Docker
Per eseguire l'applicazione in un container Docker:
1. **Costruire l'immagine Docker:**
   ```bash
   docker build -t gestione_progetti .
   ```

2. **Eseguire il container:**
   ```bash
   docker run -p 5000:5000 gestione_progetti
   ```

## Testing
Per eseguire i test:
```bash
pytest
```

## CI/CD
Questo progetto utilizza GitHub Actions per Continuous Integration e Continuous Delivery. La configurazione si trova nella cartella `.github/workflows/ci.yml`.



