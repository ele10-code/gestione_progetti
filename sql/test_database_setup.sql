CREATE DATABASE IF NOT EXISTS TestGestioneProgetti;
USE TestGestioneProgetti;

-- Crea la tabella utenti
CREATE TABLE IF NOT EXISTS utenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Crea la tabella progetti
CREATE TABLE IF NOT EXISTS progetti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_progetto VARCHAR(255) NOT NULL,
    descrizione TEXT,
    id_responsabile INT,
    scadenza DATETIME,
    FOREIGN KEY (id_responsabile) REFERENCES utenti(id)
);

-- Crea la tabella tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descrizione TEXT NOT NULL,
    stato VARCHAR(50),
    priorita VARCHAR(50),
    scadenza DATETIME,
    id_progetto INT,
    FOREIGN KEY (id_progetto) REFERENCES progetti(id)
);

-- Crea la tabella assegnazioni
CREATE TABLE IF NOT EXISTS assegnazioni (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_task INT,
    id_utente INT,
    FOREIGN KEY (id_task) REFERENCES tasks(id),
    FOREIGN KEY (id_utente) REFERENCES utenti(id)
);
