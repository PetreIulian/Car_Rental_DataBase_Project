import mariadb
from dotenv import load_dotenv
import os
from pathlib import Path
import bcrypt

root_dir = Path(__file__).parent.parent

load_dotenv(root_dir/".env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
ROOT_USER = os.getenv("DB_USER")
ROOT_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_root_connection():
    return mariadb.connect(
        host = DB_HOST,
        port = int(DB_PORT),
        user = ROOT_USER,
        password = ROOT_PASSWORD,
        database = DB_NAME
    )

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode(),
        bcrypt.gensalt()
    ).decode()

def create_db_users():
    connection = get_root_connection()
    cursor = connection.cursor()

    db_users = [
        ("admin_user", "admin_root", "ALL PRIVILEGES"),
        ("data_aquisition_user", "psi442down", "SELECT, INSERT"),
        ("data_monitor_user", "stoka123!@", "SELECT, INSERT, UPDATE"),
        ("data_cleaner_user", "recycle296^&", "SELECT, DELETE")
    ]

    for username, passwoerd, privileges in db_users:
        try:
            cursor.execute(f"DROP USER IF EXISTS '{username}'@'%'")
            cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{passwoerd}'")
            cursor.execute(f"GRANT {privileges} ON {DB_NAME}.* TO '{username}'@'%'")
            print(f"[OK] {username} a fost creat")
        except Exception as e:
            print(f"A aparut eraorea {e}")
    cursor.execute("FLUSH PRIVILEGES")
    connection.commit()
    cursor.close()

def encrypt_app_users():
    connection = get_root_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id_user, password FROM Cont_Client WHERE password IS NOT NULL AND isDeleted = 0")
    rows = cursor.fetchall()

    for user_id, password in rows:
        if not str(password).startswith("$2b$"):
            hashed = hash_password(password)
            cursor.execute(
                "UPDATE Cont_Client SET password=? WHERE id_user=?",
                (hashed, user_id,)
            )
            print(f"[UPDATED] User ID {user_id} password encrypted")

    connection.commit()
    cursor.close()

def main():
    print("\n=== CREATE DB USERS + GRANTS ===\n")
    create_db_users()

    print("\n=== ENCRYPT APP USERS PASSWORDS ===\n")
    encrypt_app_users()

    print("\n SECURITY SETUP COMPLETED")

if __name__ == "__main__":
    main()