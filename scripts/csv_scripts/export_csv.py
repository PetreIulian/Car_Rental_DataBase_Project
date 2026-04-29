import csv
from pathlib import Path
from app.db import get_connection

ALLOWED_TABLES = {"Marci", "Model", "Masini", "Cont_Client", "Date_Client", "Factura",
                  "Comanda", "Raport_Comanda", "Raport_Predare", "Raport_Primire", "Plata"}

def export_csv(table: str, out_dir: Path = Path("exports")):
    table =  table.strip()
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path =  out_dir / f"{table}.csv"
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]

        with out_path.open(mode="w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        print(f"EXPORT REALIZAT CU SUCCES --> {out_path} (rows={len(rows)})")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    table =  input(f"Tabel ({', '.join(sorted(ALLOWED_TABLES))}): ").strip()
    export_csv(table)