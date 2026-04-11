import os
import mariadb
from dotenv import load_dotenv

load_dotenv()

pool_size = int(os.getenv("DB_POOL_SIZE", "40"))

pool = mariadb.ConnectionPool(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3307")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "rootpassword"),
    database=os.getenv("DB_NAME", "CarRental_System"),
    pool_name="car_rental_pool",
    pool_size=pool_size
)

def get_connection():
    return pool.get_connection()

def run_select(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()

def run_execute(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
        affected = cur.rowcount
        return affected
    finally:
        cur.close()
        conn.close()