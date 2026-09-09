import sqlite3
import json
import os
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_DB_PATH = (
    os.path.join(os.environ.get("TEMP", "/tmp"), "ucs_history.db")
    if os.environ.get("VERCEL")
    else os.path.join(REPO_ROOT, "data", "ucs_history.db")
)


def get_db_path() -> str:
    return os.environ.get("UCS_DB_PATH", DEFAULT_DB_PATH)

def get_connection():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
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
    cursor.execute('SELECT full_output_json FROM runs ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row["full_output_json"])
    return None

# Initialize DB on import
init_db()
