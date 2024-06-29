-- Crea il database di test
CREATE DATABASE IF NOT EXISTS TestGestioneProgetti;

-- Usa il database di test
USE TestGestioneProgetti;

-- Crea la tabella utenti
CREATE TABLE IF NOT EXISTS utenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    _is_active BOOLEAN DEFAULT TRUE
);

-- Crea la tabella progetti
CREATE TABLE IF NOT EXISTS progetti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_progetto VARCHAR(255) NOT NULL,
    id_responsabile INT,
    scadenza DATETIME,
    FOREIGN KEY (id_responsabile) REFERENCES utenti(id) ON DELETE SET NULL
);

-- Crea la tabella tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descrizione TEXT,
    id_progetto INT,
    stato VARCHAR(100),
    priorita VARCHAR(100),  
    FOREIGN KEY (id_progetto) REFERENCES progetti(id) ON DELETE CASCADE
);

-- Crea la tabella assegnazioni
CREATE TABLE IF NOT EXISTS assegnazioni (
    id_utente INT,
    id_task INT,
    PRIMARY KEY (id_utente, id_task),
    FOREIGN KEY (id_utente) REFERENCES utenti(id) ON DELETE CASCADE,
    FOREIGN KEY (id_task) REFERENCES tasks(id) ON DELETE CASCADE
);
