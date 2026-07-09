from app.engine.dummy_engine import final_allocation
from app.models import AllocationResult, DailyInput, RolePlan

def run_allocation(daily_input: DailyInput, role_plan: RolePlan) -> AllocationResult:
    """Compatibility wrapper for callers that want a service layer."""
    return final_allocation(daily_input, role_plan)
