import random
from faker import Faker
from app.db import run_execute, run_select
from pathlib import Path
import csv
from datetime import timedelta
import string

fake = Faker('ro_RO')

NUM_MASINI = 5000
NUM_CONTURI = 2000
NUM_COMENZI = 1750


def populate():
    base_path = Path(__file__).resolve().parent.parent.parent / "data_csv"

    marci_path = base_path / "marci.csv"
    with open(marci_path, 'r', encoding='utf-8') as csvfile:
        marci_reader = csv.reader(csvfile)
        for marca in marci_reader:
            run_execute("INSERT INTO Marci (nume_marca) VALUES (%s);", (marca[0],))

    modele_path = base_path / "modele.csv"
    with open(modele_path, 'r', encoding='utf-8') as csvfile:
        modele_reader = csv.reader(csvfile)
        for modele in modele_reader:
            run_execute("INSERT INTO Model (fk_marca, nume_model) VALUES (%s, %s);", (modele[0], modele[1],))

    modele_db = run_select("SELECT id_model FROM Model;")
    lista_id_modele = [m[0] for m in modele_db]
    statusuri_posibile = ['Disponibil', 'Inchiriat', 'In Service', 'Rezervat']
    categorii_permis = ['B', 'B1', 'BE']

    vins_folosite = set()
    nr_inmatr_folosite = set()

    for _ in range(NUM_MASINI):
        fk_model = random.choice(lista_id_modele)

        while True:
            nr_inmatriculare = fake.license_plate()
            if nr_inmatriculare not in nr_inmatr_folosite:
                nr_inmatr_folosite.add(nr_inmatriculare)
                break

        while True:
            vin = fake.unique.vin()
            if vin not in vins_folosite:
                vins_folosite.add(vin)
                break

        status = random.choice(statusuri_posibile)
        categorie = random.choice(categorii_permis)
        pret_inchiriere = round(random.uniform(100.0, 500.0), 2)

        run_execute(
            """
            INSERT INTO Masini (fk_model, numar_inmatriculare, vin, status, 
                                pret_inchiriere, categorie_permis, isDeleted) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (fk_model, nr_inmatriculare, vin, status, pret_inchiriere, categorie, False)
        )

    usernames_folosite = set()
    for _ in range(NUM_CONTURI):
        prenume = fake.first_name()
        nume = fake.last_name()

        while True:
            username = f"{prenume.lower()}.{nume.lower()}{random.randint(100, 9999)}"
            if username not in usernames_folosite:
                usernames_folosite.add(username)
                break

        is_deleted = random.choices([False, True], weights=[0.9, 0.1])[0]
        parola_random = fake.password(length=15)

        run_execute(
            "INSERT INTO Cont_Client (username, password, isDeleted) VALUES (%s, %s, %s);",
            (username, parola_random, is_deleted)
        )

        res = run_select("SELECT id_user FROM Cont_Client WHERE username = %s;", (username,))
        id_user_nou = res[0][0]

        nr_telefon = fake.phone_number()[:15]
        adresa = fake.address().replace('\n', ', ')
        email = f"{username}@gmail.com"
        permis = random.choice(categorii_permis)
        cui = str(random.randint(10000000, 99999999)) if random.random() > 0.8 else None

        run_execute(
            """
            INSERT INTO Date_Client (fk_user, nume, prenume, numar_telefon, adresa, 
                                     email, permis_conducere, cui, isDeleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (id_user_nou, nume, prenume, nr_telefon, adresa, email, permis, cui, is_deleted)
        )

    users = run_select("SELECT id_user from Cont_Client")
    lista_id_user = [i[0] for i in users]

    for _ in range(NUM_COMENZI):
        user_id = random.choice(lista_id_user)
        data = fake.date_this_century()
        status_plata = random.choices(['Platita', 'In curs', 'Neplatita'], weights=[0.75, 0.10, 0.15])[0]

        run_execute(
            "INSERT INTO Comanda (fk_user, data_comanda, status_plata, isDeleted) VALUES (%s, %s, %s, %s);",
            (user_id, data, status_plata, False)
        )

    comenzi_db = run_select("SELECT id_comanda FROM Comanda")
    lista_comenzi = [i[0] for i in comenzi_db]
    masini_db = run_select("SELECT id_masina FROM Masini")
    lista_masini = [i[0] for i in masini_db]

    for id_comanda in lista_comenzi:
        id_masina = random.choice(lista_masini)
        data_predare = fake.date_between(start_date='-5y', end_date='today')
        data_returnare = data_predare + timedelta(days=random.randint(3, 20))

        run_execute(
            "INSERT INTO Raport_Comanda (fk_comanda, fk_masina, data_predare, data_returnare) VALUES (%s, %s, %s, %s);",
            (id_comanda, id_masina, data_predare, data_returnare)
        )

    date_facturare = run_select("""
        SELECT DISTINCT c.id_comanda, dc.id_client, rc.data_predare, rc.data_returnare, m.pret_inchiriere
        FROM Comanda c
        JOIN Date_Client dc ON c.fk_user = dc.fk_user
        JOIN Raport_Comanda rc ON c.id_comanda = rc.fk_comanda
        JOIN Masini m ON rc.fk_masina = m.id_masina
    """)

    facturi_folosite = set()
    for i in date_facturare:
        id_comanda, id_client, d_predare, d_returnare, pret_zi = i
        nr_zile = max((d_returnare - d_predare).days, 1)
        valoare_neta = round(nr_zile * float(pret_zi), 2)
        tva = round(valoare_neta * 0.19, 2)
        valoare_totala = round(valoare_neta + tva, 2)
        serie = ''.join(random.choices(string.ascii_uppercase, k=3))

        while True:
            numar_factura = random.randint(100000, 999999)
            if numar_factura not in facturi_folosite:
                facturi_folosite.add(numar_factura)
                break

        status_factura = random.choices(['Emisa', 'Platit', 'Neplatit', 'Anulat'], weights=[0.1, 0.75, 0.1, 0.05])[0]

        run_execute(
            """
            INSERT INTO Factura (fk_comanda, fk_client, serie, numar, data_emitere, 
                                 valoare_neta, valoare_tva, valoare_totala, status_factura)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (id_comanda, id_client, serie, numar_factura, d_predare, valoare_neta, tva, valoare_totala, status_factura)
        )

    facturi_db = run_select("SELECT id_factura, valoare_totala, data_emitere FROM Factura")
    for f in facturi_db:
        metoda = random.choices(['cash', 'tranzactie bancara'], weights=[0.2, 0.8])[0]
        id_tranz = random.randint(1000000, 9999999) if metoda == 'tranzactie bancara' else None
        run_execute(
            "INSERT INTO Plata (fk_factura, data_plata, suma_plata, metoda_plata, id_tranzactie_bancara) VALUES (%s, %s, %s, %s, %s);",
            (f[0], f[2], f[1], metoda, id_tranz)
        )

    rapoarte_comanda = run_select("SELECT id_raport FROM Raport_Comanda")
    for r in rapoarte_comanda:
        id_raport = r[0]
        km_start = round(random.uniform(10000, 200000), 2)
        daune_predare = "Zgarietura bara" if random.random() < 0.1 else "Fara daune"

        run_execute("INSERT INTO Raport_Predare (fk_raport_comanda, numar_kilometrii, daune) VALUES (%s, %s, %s);",
                    (id_raport, km_start, daune_predare))

        run_execute("INSERT INTO Raport_Primire (fk_raport_comanda, numar_kilometrii, daune) VALUES (%s, %s, %s);",
                    (id_raport, km_start + random.uniform(50, 1000), "Fara daune noi"))

    print("Populare finalizată cu succes!")