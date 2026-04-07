CREATE TABLE IF NOT EXISTS Marci (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nume_marca VARCHAR(100) NOT NULL UNIQUE,
    isDeleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Model (
    id_model INT AUTO_INCREMENT PRIMARY KEY,
    fk_marca INT NOT NULL,
    nume_model VARCHAR(100) NOT NULL,
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_model_marca
        FOREIGN KEY (fk_marca) REFERENCES Marci(id_marca)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Masini (
    id_masina INT AUTO_INCREMENT PRIMARY KEY,
    fk_model INT NOT NULL,
    numar_inmatriculare VARCHAR(15) UNIQUE,
    vin VARCHAR(30) UNIQUE,
    status VARCHAR(25) NOT NULL,
    pret_inchiriere DECIMAL(10,2) NOT NULL,
    categorie_permis VARCHAR(5),
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_masini_model
        FOREIGN KEY (fk_model) REFERENCES Model(id_model)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Cont_Client (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    isDeleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Date_Client (
    id_client INT AUTO_INCREMENT PRIMARY KEY,
    fk_user INT NOT NULL,
    nume VARCHAR(50) NOT NULL,
    prenume VARCHAR(50) NOT NULL,
    numar_telefon VARCHAR(15),
    adresa VARCHAR(100),
    email VARCHAR(100),
    permis_conducere VARCHAR(20),
    cui VARCHAR(20),
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_date_client_user
        FOREIGN KEY (fk_user) REFERENCES Cont_Client(id_user)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Comanda (
    id_comanda INT AUTO_INCREMENT PRIMARY KEY,
    fk_user INT NOT NULL,
    status_plata VARCHAR(100),
    data_comanda DATETIME DEFAULT CURRENT_TIMESTAMP,
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_comanda_user
        FOREIGN KEY (fk_user) REFERENCES Cont_Client(id_user)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Raport_Comanda (
    id_raport INT AUTO_INCREMENT PRIMARY KEY,
    fk_comanda INT NOT NULL,
    fk_masina INT NOT NULL,
    data_predare DATETIME,
    data_returnare DATETIME,
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_raport_comanda
        FOREIGN KEY (fk_comanda) REFERENCES Comanda(id_comanda)
        ON DELETE CASCADE,
    CONSTRAINT fk_raport_masina
        FOREIGN KEY (fk_masina) REFERENCES Masini(id_masina)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    fk_comanda INT NOT NULL,
    fk_client INT NOT NULL,
    serie VARCHAR(10) NOT NULL,
    numar INT NOT NULL,
    data_emitere DATETIME DEFAULT CURRENT_TIMESTAMP,
    valoare_neta DECIMAL(10,2) NOT NULL,
    valoare_tva DECIMAL(10,2) NOT NULL,
    valoare_totala DECIMAL(10,2) NOT NULL,
    status_factura VARCHAR(25),
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_factura_comanda
        FOREIGN KEY (fk_comanda) REFERENCES Comanda(id_comanda)
        ON DELETE CASCADE,
    CONSTRAINT fk_factura_client
        FOREIGN KEY (fk_client) REFERENCES Date_Client(id_client)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Plata (
    id_plata INT AUTO_INCREMENT PRIMARY KEY,
    fk_factura INT NOT NULL,
    data_plata DATETIME,
    suma_plata DECIMAL(10,2) NOT NULL,
    metoda_plata VARCHAR(50),
    id_tranzactie_bancara VARCHAR(100),
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_plata_factura
        FOREIGN KEY (fk_factura) REFERENCES Factura(id_factura)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Raport_Predare (
    id_raport_predare INT AUTO_INCREMENT PRIMARY KEY,
    fk_raport_comanda INT NOT NULL,
    numar_kilometrii DECIMAL(10,2) NOT NULL,
    daune TEXT,
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_predare_raport
        FOREIGN KEY (fk_raport_comanda) REFERENCES Raport_Comanda(id_raport)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Raport_Primire (
    id_raport_primire INT AUTO_INCREMENT PRIMARY KEY,
    fk_raport_comanda INT NOT NULL,
    numar_kilometrii DECIMAL(10,2) NOT NULL,
    daune TEXT,
    isDeleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_primire_raport
        FOREIGN KEY (fk_raport_comanda) REFERENCES Raport_Comanda(id_raport)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Logs(
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    tabel_vizat VARCHAR(100) NOT NULL,
    camp_vizat VARCHAR(100) NOT NULL,
    modificare VARCHAR(100) NOT NULL,
    data_log DATETIME DEFAULT CURRENT_TIMESTAMP,
    isDeleted BOOLEAN DEFAULT FALSE
);