DROP TRIGGER IF EXISTS trg_factura_before_insert;
--TRIGGER_END--

CREATE OR REPLACE TRIGGER trg_factura_before_insert
BEFORE INSERT ON Factura
FOR EACH ROW
BEGIN
    SET NEW.valoare_tva = NEW.valoare_neta * 0.19;
    SET NEW.valoare_totala = NEW.valoare_neta + (NEW.valoare_neta * 0.19);
    SET NEW.serie = UPPER(NEW.serie);
END;
--TRIGGER_END--

DROP TRIGGER IF EXISTS trg_raport_comanda_before_insert;
--TRIGGER_END--

CREATE OR REPLACE TRIGGER trg_raport_comanda_before_insert
BEFORE INSERT ON Raport_Comanda
FOR EACH ROW
BEGIN
    IF NEW.data_returnare <= NEW.data_predare THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Eroare: Data returnarii trebuie sa fie strict dupa data predarii.';
    END IF;
END;
--TRIGGER_END--

DROP TRIGGER IF EXISTS trg_masini_before_insert;
--TRIGGER_END--

CREATE OR REPLACE TRIGGER trg_masini_before_insert
BEFORE INSERT ON Masini
FOR EACH ROW
BEGIN
    SET NEW.numar_inmatriculare = UPPER(NEW.numar_inmatriculare);
    SET NEW.vin = UPPER(NEW.vin);
    IF NEW.status IS NULL OR NEW.status = '' THEN
        SET NEW.status = 'Disponibil';
    END IF;
END;
--TRIGGER_END--

DROP TRIGGER IF EXISTS trg_status_masina_after_update;
--TRIGGER_END--

CREATE OR REPLACE TRIGGER trg_status_masina_after_update
AFTER UPDATE ON Masini
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO Logs (tabel_vizat, camp_vizat, modificare)
        VALUES ('Masini', 'status', CONCAT('Masina ID ', NEW.id_masina, ': ', OLD.status, ' -> ', NEW.status));
    END IF;
END;
--TRIGGER_END--

DROP TRIGGER IF EXISTS trg_status_plata_after_update;
--TRIGGER_END--

CREATE OR REPLACE TRIGGER trg_status_plata_after_update
AFTER UPDATE ON Comanda
FOR EACH ROW
BEGIN
    IF OLD.status_plata <> NEW.status_plata THEN
        INSERT INTO Logs (tabel_vizat, camp_vizat, modificare)
        VALUES ('Comanda', 'status_plata', CONCAT('Comanda ID ', NEW.id_comanda, ': ', OLD.status_plata, ' -> ', NEW.status_plata));
    END IF;
END;
--TRIGGER_END--

DROP TRIGGER IF EXISTS trg_actualizeaza_status_la_inchiriere;
--TRIGGER_END--

CREATE OR REPLACE TRIGGER trg_actualizeaza_status_la_inchiriere
AFTER INSERT ON Raport_Comanda
FOR EACH ROW
BEGIN
    UPDATE Masini
    SET status = 'Inchiriat'
    WHERE id_masina = NEW.fk_masina;
END;
--TRIGGER_END--