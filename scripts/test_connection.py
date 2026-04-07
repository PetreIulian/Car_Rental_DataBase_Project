from app.db import run_select

try:
    results = run_select(
        "SELECT DATABASE() AS db_name, 'Conexiunea s-a realizat cu succes' AS status;"
    )

    print(results)

except:
    print("A apărut o eroare la conectarea la baza de date.")