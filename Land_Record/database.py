import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "land_records.db"

def init_db():
    """Initializes the SQLite database and creates the records table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landowner_name TEXT,
            survey_khasra_no TEXT,
            khata_no TEXT,
            area_hectares REAL,
            village TEXT,
            tehsil TEXT,
            district TEXT,
            state TEXT,
            confidence_score REAL,
            validation_status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_record(data: dict) -> bool:
    """Inserts a verified land record into SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO records (
                landowner_name, survey_khasra_no, khata_no, area_hectares,
                village, tehsil, district, state, confidence_score,
                validation_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(data.get("landowner_name", "Unknown")),
            str(data.get("survey_khasra_no", "N/A")),
            str(data.get("khata_no", "N/A")),
            float(data.get("area_hectares", 0.0)),
            str(data.get("village", "N/A")),
            str(data.get("tehsil", "N/A")),
            str(data.get("district", "N/A")),
            str(data.get("state", "N/A")),
            float(data.get("confidence_score", 0.0)),
            str(data.get("validation_status", "Verified & Committed")),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database insert error: {e}")
        return False

def update_record(record_id: int, data: dict) -> bool:
    """Updates an existing land record in SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE records 
            SET landowner_name = ?, survey_khasra_no = ?, khata_no = ?, 
                area_hectares = ?, village = ?, tehsil = ?, district = ?, 
                state = ?, validation_status = ?
            WHERE id = ?
        """, (
            str(data.get("landowner_name", "")),
            str(data.get("survey_khasra_no", "")),
            str(data.get("khata_no", "")),
            float(data.get("area_hectares", 0.0)),
            str(data.get("village", "")),
            str(data.get("tehsil", "")),
            str(data.get("district", "")),
            str(data.get("state", "")),
            str(data.get("validation_status", "Updated by Officer")),
            record_id
        ))
        conn.commit()
        updated_count = cursor.rowcount
        conn.close()
        return updated_count > 0
    except Exception as e:
        print(f"❌ Database update error: {e}")
        return False

def delete_record(record_id: int) -> bool:
    """Deletes a land record by ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        return deleted_count > 0
    except Exception as e:
        print(f"❌ Database delete error: {e}")
        return False

def get_all_records() -> pd.DataFrame:
    """Fetches all stored land records as a DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM records ORDER BY id DESC", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df