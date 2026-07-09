import json, sqlite3
from pathlib import Path
from app.models import AllocationHistoryEntry, FinalizationRequest
DB_PATH = Path(__file__).resolve().parents[2] / 'data' / 'allocation.db'; DB_PATH.parent.mkdir(parents=True, exist_ok=True)
def get_connection():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS allocations (id INTEGER PRIMARY KEY AUTOINCREMENT, shift_date TEXT NOT NULL, status TEXT NOT NULL, input_json TEXT NOT NULL, role_plan_json TEXT NOT NULL, result_json TEXT NOT NULL, assigned_count INTEGER NOT NULL, total_volume INTEGER NOT NULL, export_filename TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
def save_finalization(req: FinalizationRequest, export_filename: str) -> int:
    with get_connection() as conn:
        cur=conn.execute('INSERT INTO allocations (shift_date,status,input_json,role_plan_json,result_json,assigned_count,total_volume,export_filename) VALUES (?,?,?,?,?,?,?,?)',(req.daily_input.shift_date,'finalized',req.daily_input.model_dump_json(),req.role_plan.model_dump_json(),req.allocation_result.model_dump_json(),len(req.allocation_result.assignments),sum(v.total_volume for v in req.daily_input.volumes),export_filename))
        return int(cur.lastrowid)
def list_allocations() -> list[AllocationHistoryEntry]:
    with get_connection() as conn:
        rows=conn.execute('SELECT id run_id, shift_date, status, assigned_count, total_volume, export_filename, created_at FROM allocations ORDER BY id DESC').fetchall()
    return [AllocationHistoryEntry(**dict(r)) for r in rows]
