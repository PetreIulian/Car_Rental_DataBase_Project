import time
from app.db import run_execute
def apply_indexes():
    print("Se aplica indexii.")
    index_query = [
        "CREATE INDEX IF NOT EXISTS idx_vin_masini ON Masini(vin);",
        "CREATE INDEX IF NOT EXISTS idx_numar_status ON Masini(status);",
        
        "CREATE INDEX IF NOT EXISTS idx_username ON Cont_Client(username);",
        "CREATE INDEX IF NOT EXISTS idx_data_factura ON Factura(data_emitere);",
        
        "CREATE INDEX IF NOT EXISTS idx_masini_model ON Masini(fk_model);",
        "CREATE INDEX IF NOT EXISTS idx_model_marca ON Model(fk_marca);",
        "CREATE INDEX IF NOT EXISTS idx_raport_comanda ON Raport_Comanda(fk_comanda);",
        "CREATE INDEX IF NOT EXISTS idx_plata_factura ON Plata(fk_factura);",
        "CREATE INDEX IF NOT EXISTS idx_client_nume_complet ON Date_Client(nume, prenume);"
    ]
    for query in index_query:
        print(f"Ruluam : {query}")
        try:
            start = time.time()
            run_execute(query)
            end = time.time()
            duration = (end - start) * 1000
            print(f"-> Succes! (Durata creare: {duration:.2f}ms)\n")
        except Exception as e:
            print(f"-> Eroare la crearea indexului: {e}\n")
    print("Indexuri aplicate cu succes.")
    print("----------------------------")
