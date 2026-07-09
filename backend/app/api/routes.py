from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from app.models import AllocationInput
from app.parsers.aisle_parser import parse_aisle_volumes
from app.services.allocation_service import run_allocation
from app.services.database import list_allocations
from app.services.excel_service import OUTPUT_DIR, parse_employee_workbook

router = APIRouter()

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@router.post("/parse-aisles")
def parse_aisles(payload: dict[str, str]):
    return {"items": parse_aisle_volumes(payload.get("raw_text", ""))}

@router.post("/employees/upload")
async def upload_employees(file: UploadFile = File(...)):
    suffix = Path(file.filename or "employees.xlsx").suffix or ".xlsx"
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        return {"employees": parse_employee_workbook(tmp_path)}
    finally:
        tmp_path.unlink(missing_ok=True)

@router.post("/allocations")
def create_allocation(payload: AllocationInput):
    return run_allocation(payload)

@router.get("/allocations")
def allocations():
    return {"items": list_allocations()}

@router.get("/exports/{filename}")
def download_export(filename: str):
    path = OUTPUT_DIR / filename
    return FileResponse(path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
