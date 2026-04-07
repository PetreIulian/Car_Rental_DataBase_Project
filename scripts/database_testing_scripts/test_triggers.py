from app.db import run_execute, run_select

print("--- TEST TRIGGER BEFORE INSERT (Raport_Comanda) ---")
id_masina = run_select("SELECT id_masina FROM Masini LIMIT 1;")[0][0]
id_user = run_select("SELECT id_user FROM Cont_Client LIMIT 1;")[0][0]

run_execute("INSERT INTO Comanda (fk_user, status_plata) VALUES (%s, %s);", (id_user, 'In curs'))
comanda_id = run_select("SELECT id_comanda FROM Comanda ORDER BY id_comanda DESC LIMIT 1;")[0][0]

print(f"Inserare VALIDĂ (Data returnare > Data predare)")
try:
    run_execute(
        "INSERT INTO Raport_Comanda (fk_comanda, fk_masina, data_predare, data_returnare) VALUES (%s, %s, %s, %s);",
        (comanda_id, id_masina, '2026-05-01 10:00:00', '2026-05-05 10:00:00')
    )
    print("OK: Inserarea valida a reusit.")
except Exception as e:
    print("EROARE (nu trebuia):", e)

print(f"\nInserare INVALIDĂ (Data returnare < Data predare)")
try:
    run_execute(
        "INSERT INTO Raport_Comanda (fk_comanda, fk_masina, data_predare, data_returnare) VALUES (%s, %s, %s, %s);",
        (comanda_id, id_masina, '2026-05-10 10:00:00', '2026-05-01 10:00:00')
    )
    print("EROARE: Inserarea invalida a trecut (triggerul NU functioneaza!)")
except Exception as e:
    print("OK: Inserarea invalida a fost respinsa de trigger.")
    print("Mesaj DB:", e)


print("\n--- TEST TRIGGER AFTER UPDATE (Masini) ---")
print("Schimbăm statusul mașinii pentru a verifica logurile...")

run_execute("UPDATE Masini SET status=%s WHERE id_masina=%s;", ("In Service", id_masina))

print("Verificăm tabelul de Logs:")
logs = run_select("SELECT modificare FROM Logs WHERE tabel_vizat='Masini' ORDER BY id_log DESC LIMIT 1;")

if logs:
    for l in logs:
        print("- Log gasit:", l[0])
else:
    print("- EROARE: Nu s-a generat niciun log in baza de date.")

print("\n--- TEST TRIGGERE FINALIZAT ---")