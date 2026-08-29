import sqlite3
import pandas as pd

DB_FILE = "land_records.db"

def init_db():
    """Initialize the SQLite database schema if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS land_records (
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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_record(record: dict) -> bool:
    """Insert an approved land record into the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO land_records (
                landowner_name, survey_khasra_no, khata_no,
                area_hectares, village, tehsil, district,
                state, confidence_score, validation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.get("landowner_name", ""),
            record.get("survey_khasra_no", ""),
            record.get("khata_no", ""),
            float(record.get("area_hectares", 0.0)),
            record.get("village", ""),
            record.get("tehsil", ""),
            record.get("district", ""),
            record.get("state", ""),
            float(record.get("confidence_score", 0.0)),
            record.get("validation_status", "Verified & Committed")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database insertion error: {e}")
        return False

def get_all_records() -> pd.DataFrame:
    """Fetch all stored land records as a pandas DataFrame."""
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM land_records ORDER BY id DESC", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df