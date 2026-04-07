from scripts.table_magement_scripts.check_tables import check_tables
from scripts.table_magement_scripts.rebuild_db import rebuild_db
from scripts.database_testing_scripts.seed import populate
from scripts.table_magement_scripts.create_triggers import create_triggers
from scripts.table_magement_scripts.add_indexes import apply_indexes

def init_db():

    print("Se initializeaza baza de date prin creearea tabelelor.")
    rebuild_db()
    print("Tabelele au fost create")
    create_triggers()
    populate()
    apply_indexes()



if __name__ == "__main__":
    init_db()
    check_tables()