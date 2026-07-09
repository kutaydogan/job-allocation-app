from app.engine.dummy_engine import calculate_allocation
from app.models import AllocationInput, AllocationResponse
from app.services.database import save_allocation
from app.services.excel_service import export_allocation

def run_allocation(payload: AllocationInput) -> AllocationResponse:
    results = calculate_allocation(payload)
    export_filename = export_allocation(payload, results)
    allocation_id = save_allocation(payload, results, export_filename)
    return AllocationResponse(allocation_id=allocation_id, export_filename=export_filename, results=results)
