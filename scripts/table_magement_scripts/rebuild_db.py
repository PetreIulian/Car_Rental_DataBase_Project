from app.db import run_execute
from scripts.table_magement_scripts.create_tables import create_tables

def rebuild_db():
    print("Se sterg tabelele existente.")

    run_execute("DROP TABLE IF EXISTS Plata;")
    run_execute("DROP TABLE IF EXISTS Factura;")
    run_execute("DROP TABLE IF EXISTS Raport_Primire;")
    run_execute("DROP TABLE IF EXISTS Raport_Predare;")
    run_execute("DROP TABLE IF EXISTS Raport_Comanda;")
    run_execute("DROP TABLE IF EXISTS Date_Client;")
    run_execute("DROP TABLE IF EXISTS Comanda;")
    run_execute("DROP TABLE IF EXISTS Masini;")
    run_execute("DROP TABLE IF EXISTS Model;")
    run_execute("DROP TABLE IF EXISTS Marci;")
    run_execute("DROP TABLE IF EXISTS Cont_Client;")
    run_execute("DROP TABLE IF EXISTS Client;")
    run_execute("DROP TABLE IF EXISTS Logs;")

    print("Se creeaza tabelele din schema.sql.")
    create_tables()

    print("S-a dat rebuild database.")