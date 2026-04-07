from app.db import run_select

def check_tables():
    tables = run_select("SHOW TABLES;")

    print("Tabele existente:")
    for t in tables:
        print("-", t[0])