from pathlib import Path
from app.db import get_connection

def create_triggers():
    project_root = Path(__file__).parent.parent.parent
    connection = get_connection()
    cursor = connection.cursor()
    try:
        triggers_path = project_root / 'sql' / 'triggers.sql'
        triggers_text = triggers_path.read_text(encoding='utf-8')
        trigger_blocks = [
            b.strip()
            for b in triggers_text.split('--TRIGGER_END--')
            if b.strip()
        ]
        for block in trigger_blocks:
            cursor.execute(block)
        print("Triggerele au fost create cu succes.")
        connection.commit()
    except Exception as e:
        connection.rollback()
        print("Eroare la crearea triggerului: ", e)
        raise
    finally:
        cursor.close()
        connection.close()