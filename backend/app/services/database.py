import json
import sqlite3
from pathlib import Path
from app.models import AllocationInput, AllocationResult

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "allocation.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_date TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                export_filename TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

def save_allocation(payload: AllocationInput, results: list[AllocationResult], export_filename: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO allocations (shift_date, input_json, result_json, export_filename) VALUES (?, ?, ?, ?)",
            (
                payload.shift_date,
                payload.model_dump_json(),
                json.dumps([result.model_dump() for result in results]),
                export_filename,
            ),
        )
        return int(cursor.lastrowid)

def list_allocations() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT id, shift_date, export_filename, created_at FROM allocations ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]
