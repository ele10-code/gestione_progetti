#!/bin/bash

# Installa pipreqs se non è già installato
pip install pipreqs

# Genera un nuovo requirements.txt
pipreqs --force .

# Opzionale: aggiungi versioni specifiche per alcune librerie
echo "Flask==2.0.1" >> requirements.txt
echo "pytest==6.2.5" >> requirements.txt

# Rimuovi eventuali duplicati
sort -u requirements.txt -o requirements.txt
