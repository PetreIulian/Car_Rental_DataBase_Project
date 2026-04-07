from pathlib import Path
from app.db import get_connection

def create_tables():
    project_root = Path(__file__).resolve().parent.parent.parent
    schema_path = project_root / "sql" / "schema.sql"
    sql_string = schema_path.read_text(encoding="utf-8")

    statements = [s.strip() for s in sql_string.split(";") if s.strip()]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for i in statements:
            cursor.execute(i)
        conn.commit()
        print("Comanda executata cu success. S-au creat tabelele din script.")
    except Exception as e:
        conn.rollback()
        print("A aparut o eroare la creearea tabelelor.")
        raise
    finally:
        cursor.close()
        conn.close()