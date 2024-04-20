CREATE DATABASE GestioneProgetti;
USE GestioneProgetti;

CREATE TABLE utenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE progetti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_progetto VARCHAR(255) NOT NULL,
    id_responsabile INT,
    scadenza DATETIME,  -- Qui c'era una virgola extra seguita dalla parola "utenti"
    
    FOREIGN KEY (id_responsabile) REFERENCES utenti(id) ON DELETE SET NULL
);


CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descrizione TEXT,
    id_progetto INT,
    stato VARCHAR(100),
    priorità VARCHAR(100),
    FOREIGN KEY (id_progetto) REFERENCES progetti(id) ON DELETE CASCADE
);

CREATE TABLE assegnazioni (
    id_utente INT,
    id_task INT,
    PRIMARY KEY (id_utente, id_task),
    FOREIGN KEY (id_utente) REFERENCES utenti(id) ON DELETE CASCADE,
    FOREIGN KEY (id_task) REFERENCES tasks(id) ON DELETE CASCADE
);


DESCRIBE utenti;
DESCRIBE progetti;
DESCRIBE tasks;
DESCRIBE assegnazioni;

ALTER TABLE utenti ADD COLUMN password_hash VARCHAR(255);
ALTER TABLE utenti ADD COLUMN _is_active BOOLEAN DEFAULT TRUE;




