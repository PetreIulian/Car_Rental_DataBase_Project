from app.db import run_execute, run_select, get_connection
from pathlib import Path

def create_procedure():
    project_root = Path(__file__).resolve().parent.parent.parent

    connection =  get_connection()
    cursor = connection.cursor()

    try:
        procedure_path = project_root / "sql" / "procedures.sql"
        procedure_text = procedure_path.read_text(encoding="utf-8")

        procedure_block = [
            b.strip()
            for b in procedure_text.split("--END_PROCEDURE--")
            if b.strip()
        ]
        for block in procedure_block:
            cursor.execute(block)
            connection.commit()
    except Exception as e:
        connection.rollback()
        print("Eroare la crearea procedurilor", e)
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_procedure()