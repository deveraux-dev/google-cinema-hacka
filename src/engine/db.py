import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "ucs_history.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            scene_id TEXT,
            severity TEXT,
            full_output_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_run(output_dict: dict):
    """Log a complete pipeline run to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    scene_id = output_dict.get("scene", {}).get("id", "UNKNOWN")
    severity = output_dict.get("safety", {}).get("severity", "UNKNOWN")
    
    cursor.execute('''
        INSERT INTO runs (scene_id, severity, full_output_json)
        VALUES (?, ?, ?)
    ''', (scene_id, severity, json.dumps(output_dict)))
    
    conn.commit()
    conn.close()

def get_latest_run():
    """Retrieve the most recent run from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT full_output_json FROM runs ORDER BY timestamp DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row["full_output_json"])
    return None

# Initialize DB on import
init_db()
