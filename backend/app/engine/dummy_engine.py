from app.models import AllocationInput, AllocationResult

ROLE_BY_SKILL = {
    "pick": "Picker",
    "pack": "Packer",
    "rebin": "Rebin",
    "stow": "Stower",
}

def _role_for(skills: list[str]) -> str:
    normalized = [skill.lower() for skill in skills]
    for key, role in ROLE_BY_SKILL.items():
        if key in normalized:
            return role
    return "General Associate"

def calculate_allocation(payload: AllocationInput) -> list[AllocationResult]:
    present = [employee for employee in payload.employees if employee.present]
    if not present:
        return []

    capacity = max(payload.build_time_hours * payload.rate_per_hour, 1)
    results: list[AllocationResult] = []
    for index, item in enumerate(payload.aisle_volumes):
        employee = present[index % len(present)]
        utilization = round(min(item.volume / capacity, 1.5), 2)
        warnings: list[str] = []
        if utilization > 1:
            warnings.append("Über Kapazität")
        if item.volume == 0:
            warnings.append("Kein Volumen")
        results.append(
            AllocationResult(
                employee_id=employee.id,
                employee_name=employee.name,
                role=_role_for(employee.skills),
                aisle=item.aisle,
                volume=item.volume,
                utilization=utilization,
                warnings=warnings,
            )
        )
    return results
