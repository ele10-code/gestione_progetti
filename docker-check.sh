#!/bin/bash

echo "Verifica e configurazione di Docker"

# Verifica se Docker è installato
if ! command -v docker &> /dev/null
then
    echo "Docker non è installato. Vuoi installarlo? (y/n)"
    read install_docker
    if [ "$install_docker" = "y" ]; then
        sudo apt-get update
        sudo apt-get install -y docker.io
    else
        echo "Docker è necessario per continuare. Uscita."
        exit 1
    fi
fi

# Verifica lo stato del servizio Docker
if ! sudo systemctl is-active --quiet docker; then
    echo "Il servizio Docker non è attivo. Avvio in corso..."
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Verifica che l'utente sia nel gruppo docker
if ! groups $USER | grep -q '\bdocker\b'; then
    echo "Aggiunta dell'utente al gruppo docker..."
    sudo usermod -aG docker $USER
    echo "Per rendere effettive le modifiche, effettua il logout e il login."
fi

# Verifica il socket Docker
if [ ! -S /var/run/docker.sock ]; then
    echo "Il socket Docker non esiste. Potrebbe esserci un problema con l'installazione di Docker."
else
    echo "Socket Docker trovato."
fi

echo "Configurazione completata. Prova ad eseguire 'docker pull hello-world' per verificare."
echo "Se continui ad avere problemi, riavvia il sistema e riprova."