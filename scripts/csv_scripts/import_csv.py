import csv
from pathlib import Path
from app.db import get_connection

ALLOWED_TABLES = {
    "Marci", "Model", "Masini", "Cont_Client", "Date_Client", "Factura",
    "Comanda", "Raport_Comanda", "Raport_Predare", "Raport_Primire", "Plata"
}

AUTO_SKIP_COLS = {"id", "isDeleted"}


def get_table_columns(cur, table: str) -> set[str]:
    cur.execute(f"DESCRIBE {table};")
    return {row[0] for row in cur.fetchall()}


def import_table_from_csv(table: str, csv_path: Path, truncate_first: bool = False):
    table = table.strip()
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")

    if not csv_path.exists():
        raise FileNotFoundError(f"Nu exista CSV la: {csv_path}")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        table_cols = get_table_columns(cursor, table)

        with csv_path.open(mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV invalid: lipseste header-ul.")

            cols = [c.strip() for c in reader.fieldnames if c.strip() in table_cols and c.strip() not in AUTO_SKIP_COLS]

            if not cols:
                raise ValueError("Nu am coloane importabile (header-ul nu corespunde tabelului).")

            placeholders = ", ".join(["%s"] * len(cols))
            col_list = ", ".join(cols)
            sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

            skipped = 0
            inserted = 0

            if truncate_first:
                print(f"Curatare tabel {table}...")
                cursor.execute(f"TRUNCATE TABLE {table};")

            for i, row in enumerate(reader, start=2):
                values = []
                is_row_empty = True

                for c in cols:
                    val = row.get(c)
                    if val is not None:
                        val = val.strip()
                        if val != "":
                            is_row_empty = False
                            values.append(val)
                        else:
                            values.append(None)
                    else:
                        values.append(None)

                if is_row_empty:
                    skipped += 1
                    continue

                try:
                    cursor.execute(sql, tuple(values))
                    inserted += 1
                except Exception as row_err:
                    print(f"Eroare la randul {i}: {row_err}")
                    skipped += 1

        connection.commit()
        print(f"--- IMPORT FINALIZAT ---")
        print(f"Tabel:    {table}")
        print(f"Inserate: {inserted}")
        print(f"Sarite:   {skipped}")

    except Exception as e:
        connection.rollback()
        print(f"IMPORT FAIL --> Rollback executat. Eroare: {e}")
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    print("--- Utilitar Import CSV ---")
    tbl = input(f"Tabel ({', '.join(sorted(ALLOWED_TABLES))}): ").strip()
    csv_file = input("Cale fisier CSV: ").strip()
    trnc = input("Doriti TRUNCATE inainte de import? (y/n): ").strip().lower() == "y"

    import_table_from_csv(tbl, Path(csv_file), truncate_first=trnc)