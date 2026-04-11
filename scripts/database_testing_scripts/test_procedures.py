from datetime import datetime, timedelta
from app.db import get_connection, run_select
import random
import string

print("--- TESTING RENTAL SYSTEM PROCEDURES ---")

user_rows = run_select("SELECT id_user FROM Cont_Client LIMIT 1",)
masini_rows = run_select("SELECT id_masina FROM Masini WHERE status = 'Disponibil' LIMIT 5",)
if not user_rows:
    print("Eroare: Utilizatorul nu a fost găsit.")
    exit()

user_id = user_rows[0][0]
masini_de_test = [m[0] for m in masini_rows]

data_predare = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
data_returnare = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

connection = get_connection()
cursor = connection.cursor()

try:
    print("\n[1] Plasare comenzi...")
    comenzi_create = []

    for masina_id in masini_de_test:
        cursor.execute(
            "CALL plasare_comanda(%s, %s, %s, %s);",
            (user_id, masina_id, data_predare, data_returnare)
        )
        cursor.execute("SELECT LAST_INSERT_ID();")
        comenzi_create.append(cursor.fetchone()[0])
        print(f"Comanda plasată pentru masina ID: {masina_id}, inchiriata in perioada {data_predare} - {data_returnare}")

    print("\n[2] Generare facturi pentru comenzile noi...")
    for comenzi_id in comenzi_create:
        serie = ''.join(random.choices(string.ascii_uppercase, k=3))
        numar = random.randint(100000, 999999)
        cursor.execute("CALL genereaza_factura(%s, %s, %s);", (comenzi_id, serie, numar))
        print(f"Factura generată pentru comanda ID: {comenzi_id}")

    print("\n[3] Finalizare închiriere returnare mașinia...")
    for comanda_id in comenzi_create:
        cursor.execute("SELECT id_raport FROM Raport_Comanda WHERE fk_comanda = %s;", (comanda_id,))
        raport_id = cursor.fetchone()[0]

        if comanda_id == comenzi_create[0]:
            daune = "Zgârietură bară față"
        else:
            daune = ''

        km_parcursi = random.uniform(50.0, 500.0)

        cursor.execute(
            "CALL finalizare_inchiriere(%s, %s, %s);",
            (raport_id, km_parcursi, daune)
        )
        print(f"OK: Retur procesat pentru raport ID: {raport_id} | Status daune: {daune}")

    connection.commit()
    print("\n--- Toate procedurile au fost executate cu succes! ---")

except Exception as e:
    print(f"\nEroare : Execuția a eșuat: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()

print("\nVerificare Status Final în DB:")
query_final = """
    SELECT 
        comanda.id_comanda, 
        masini.id_masina,
        masini.status as status_masina,
        factura.valoare_totala,
        factura.status_factura
    FROM Comanda comanda
    JOIN Raport_Comanda raport_comanda ON comanda.id_comanda = raport_comanda.fk_comanda
    JOIN Masini masini ON raport_comanda.fk_masina = masini.id_masina
    LEFT JOIN Factura factura ON comanda.id_comanda = factura.fk_comanda
    WHERE comanda.fk_user = %s
    ORDER BY comanda.id_comanda DESC
    LIMIT 5;
"""

rows = run_select(query_final, (user_id,))
for row in rows:
    print(f"Comenzi: {row[0]} | Masina: {row[1]} | Status Masina: {row[2]} | Factura: {row[3]} RON ({row[4]})")