DROP PROCEDURE IF EXISTS plasare_comanda;
--END_PROCEDURE--

CREATE PROCEDURE plasare_comanda(
    IN p_user_id INT,
    IN p_masina_id INT,
    IN p_data_predare DATETIME,
    IN p_data_returnare DATETIME
)
BEGIN
    DECLARE v_comanda_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Eroare: Comanda nu a putut fi plasata.';
    END;

    START TRANSACTION;

    INSERT INTO Comanda (fk_user, status_plata, data_comanda)
    VALUES (p_user_id, 'In curs', NOW());

    SET v_comanda_id = LAST_INSERT_ID();

    INSERT INTO Raport_Comanda (fk_comanda, fk_masina, data_predare, data_returnare)
    VALUES (v_comanda_id, p_masina_id, p_data_predare, p_data_returnare);

    UPDATE Masini
    SET status = 'Rezervat'
    WHERE id_masina = p_masina_id;

    COMMIT;
END
--END_PROCEDURE--

DROP PROCEDURE IF EXISTS finalizare_inchiriere
--END_PROCEDURE--

CREATE PROCEDURE finalizare_inchiriere(
    IN p_raport_comanda_id INT,
    IN p_km_reali DECIMAL(10,2),
    IN p_daune_text TEXT
)
BEGIN
    DECLARE v_masina_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
    END;

    START TRANSACTION;
        INSERT INTO Raport_Primire (fk_raport_comanda, numar_kilometrii, daune)
        VALUES (p_raport_comanda_id, p_km_reali, p_daune_text);

        SELECT fk_masina INTO v_masina_id FROM Raport_Comanda WHERE id_raport = p_raport_comanda_id;

        IF p_daune_text IS NULL OR p_daune_text ='' THEN
            UPDATE Masini SET status = 'Disponibil' WHERE id_masina = v_masina_id;
        ELSE
            UPDATE Masini SET status = 'In Service' WHERE id_masina = v_masina_id;
        END IF;
    COMMIT;
END
--END_PROCEDURE--

DROP PROCEDURE IF EXISTS genereaza_factura
--END_PROCEDURE--

CREATE PROCEDURE genereaza_factura(
    IN p_comanda_id INT,
    IN p_serie_comanda VARCHAR(4),
    IN p_numar_comanda VARCHAR(15)
)
BEGIN
    DECLARE v_zile INT;
    DECLARE v_pret_zi DECIMAL(10,2);
    DECLARE v_client_id INT;
    DECLARE v_total_net DECIMAL(10,2);

    SELECT DATEDIFF(rc.data_returnare, rc.data_predare), m.pret_inchiriere, dc.id_client
    INTO v_zile, v_pret_zi, v_client_id
    FROM Raport_Comanda rc
    JOIN Masini m ON rc.fk_masina = m.id_masina
    JOIN Comanda c ON rc.fk_comanda = c.id_comanda
    JOIN Date_Client dc ON c.fk_user = dc.fk_user
    WHERE rc.fk_comanda = p_comanda_id;

    SET v_total_net = v_zile * v_pret_zi;

    INSERT INTO Factura (fk_comanda, fk_client, serie, numar, valoare_neta, valoare_tva, valoare_totala, status_factura)
    VALUES (p_comanda_id, v_client_id, p_serie_comanda, p_numar_comanda, v_total_net, v_total_net * 0.19, v_total_net * 1.19, 'Neplatit');
END
--END_PROCEDURE--