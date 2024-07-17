-- Creazione del database
CREATE DATABASE GestioneProgetti;
USE GestioneProgetti;

-- Creazione della tabella utenti
CREATE TABLE utenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    _is_active BOOLEAN DEFAULT TRUE
);

-- Creazione della tabella progetti
CREATE TABLE progetti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_progetto VARCHAR(255) NOT NULL,
    id_responsabile INT,
    scadenza DATETIME,
    FOREIGN KEY (id_responsabile) REFERENCES utenti(id) ON DELETE SET NULL
);

-- Creazione della tabella tasks
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descrizione TEXT,
    id_progetto INT,
    stato VARCHAR(100),
    priorita VARCHAR(100),  
    FOREIGN KEY (id_progetto) REFERENCES progetti(id) ON DELETE CASCADE
);

-- Creazione della tabella assegnazioni
CREATE TABLE assegnazioni (
    id_utente INT,
    id_task INT,
    PRIMARY KEY (id_utente, id_task),
    FOREIGN KEY (id_utente) REFERENCES utenti(id) ON DELETE CASCADE,
    FOREIGN KEY (id_task) REFERENCES tasks(id) ON DELETE CASCADE
);

