from pathlib import Path
from uuid import uuid4
from openpyxl import Workbook, load_workbook
from app.models import AllocationInput, AllocationResult, Employee

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def export_allocation(payload: AllocationInput, results: list[AllocationResult]) -> str:
    filename = f"allocation_{payload.shift_date}_{uuid4().hex[:8]}.xlsx"
    path = OUTPUT_DIR / filename
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Allocation"
    sheet.append(["Schichtdatum", payload.shift_date])
    sheet.append([])
    sheet.append(["Mitarbeiter", "Rolle", "Aisle/Finger", "Volumen", "Auslastung", "Warnungen"])
    for result in results:
        sheet.append([
            result.employee_name,
            result.role,
            result.aisle,
            result.volume,
            result.utilization,
            ", ".join(result.warnings),
        ])
    workbook.save(path)
    return filename

def parse_employee_workbook(file_path: Path) -> list[Employee]:
    workbook = load_workbook(file_path)
    sheet = workbook.active
    headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
    employees: list[Employee] = []
    for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=1):
        values = dict(zip(headers, row))
        name = values.get("name") or values.get("mitarbeiter") or values.get("employee")
        if not name:
            continue
        raw_skills = values.get("skills") or values.get("skill") or ""
        skills = [skill.strip() for skill in str(raw_skills).split(",") if skill.strip()]
        raw_present = str(values.get("present", "true")).lower()
        present = raw_present not in {"false", "0", "no", "nein"}
        employees.append(Employee(id=f"emp-{row_index}", name=str(name), skills=skills, present=present))
    return employees
