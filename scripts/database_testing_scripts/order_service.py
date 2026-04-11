from datetime import datetime, timedelta
from app.db import get_connection, run_select

print("ORDER SERVICE - TESTING PROCEDURES")

user_rows = run_select("SELECT id_user FROM Cont_Client WHERE username = %s;", ("dana.dinu7985",))
if not user_rows:
    print("Error: User not found.")
    exit()

user_id = user_rows[0][0]

masini = [
    {"id_masina": 6},
    {"id_masina": 9},
]

data_predare = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
data_returnare = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

connection = get_connection()
cursor = connection.cursor()

try:
    print(f"Apelam procedura plasare_comanda pentru {len(masini)} masini...")

    for masina in masini:
        m_id = masina["id_masina"]
        # Calling the procedure with the 4 required arguments
        cursor.execute(
            "CALL plasare_comanda(%s, %s, %s, %s);",
            (user_id, m_id, data_predare, data_returnare)
        )
        print(f"Comanda plasata cu succes pentru masina ID: {m_id}")

    connection.commit()
    print("\nToate procedurile au fost rulate cu succes.")

except Exception as e:
    print(f"Eroare la executie: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()

print("\nVerificarea in DB (Ultimele comenzi plasate):")
query_verificare = """
    SELECT 
        c.id_comanda, 
        m.id_masina,
        m.status, 
        rc.data_predare, 
        rc.data_returnare
    FROM Comanda c
    JOIN Raport_Comanda rc ON c.id_comanda = rc.fk_comanda
    JOIN Masini m ON rc.fk_masina = m.id_masina
    WHERE c.fk_user = %s
    ORDER BY c.id_comanda DESC
    LIMIT 5;
"""

rows = run_select(query_verificare, (user_id,))
for row in rows:
    print(f"Comanda: {row[0]} | Masina: {row[1]} | Status: {row[2]} | Perioada: {row[3]} -> {row[4]}")