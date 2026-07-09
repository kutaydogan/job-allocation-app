from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class Employee(BaseModel):
    employee_id: str
    name: str
    badge_id: str
    user_id: str
    skills: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    new_hire: bool = False
    l3: bool = False
    present: bool = True
    allocatable: bool = True
    status: Literal['found','unknown'] = 'found'

class EmployeeResolutionRequest(BaseModel):
    raw_employee_ids: str

class EmployeeResolutionResponse(BaseModel):
    total_ids: int
    found_count: int
    unknown_ids: list[str]
    duplicate_ids: list[str]
    employees: list[Employee]

class AisleVolume(BaseModel):
    finger: str
    aisle: str
    sd_volume: int = 0
    nd_volume: int = 0
    total_volume: int = 0

class VolumeParseRequest(BaseModel):
    sd_raw_text: str = ''
    nd_raw_text: str = ''

class VolumeParseResponse(BaseModel):
    aisles: list[AisleVolume]
    sd_total: int
    nd_total: int
    total_volume: int
    aisle_count: int
    active_fingers: list[str]
    warnings: list[str] = Field(default_factory=list)

class OperationalRate(BaseModel):
    key: str
    name: str
    default_value: float
    current_value: float
    unit: str = ''

class ValidationIssue(BaseModel):
    severity: Literal['error','warning','info','success']
    message: str
    field: str | None = None

class DailyInput(BaseModel):
    shift_date: str
    employees: list[Employee] = Field(default_factory=list)
    volumes: list[AisleVolume] = Field(default_factory=list)
    rates: list[OperationalRate] = Field(default_factory=list)
    previous_day_found: bool = True

class ValidationResult(BaseModel):
    is_valid: bool
    error_count: int
    warning_count: int
    issues: list[ValidationIssue]

class RolePlanItem(BaseModel):
    engine_cluster: str
    suggested_count: int
    current_count: int
    minimum_count: int = 0
    maximum_count: int | None = None
    mandatory: bool = False
    editable: bool | Literal['restricted'] = True
    type: str
    available_skilled_employees: int
    warnings: list[str] = Field(default_factory=list)

class RolePlan(BaseModel):
    target_positions: int
    current_positions: int
    items: list[RolePlanItem]
    warnings: list[str] = Field(default_factory=list)

class RolePlanValidation(BaseModel):
    is_valid: bool
    target_positions: int
    current_positions: int
    issues: list[ValidationIssue]

class AllocationAssignment(BaseModel):
    employee_id: str
    badge_id: str
    name: str
    user_id: str
    role: str
    engine_cluster: str
    fclm_cluster: str
    finger: str | None = None
    primary_aisles: list[str] = Field(default_factory=list)
    primary_volume: int = 0
    load_percent: float = 0
    support_target: str | None = None
    support_aisles: list[str] = Field(default_factory=list)
    internal_note: str = ''
    status: str = 'assigned'

class AllocationResult(BaseModel):
    run_status: str
    kpis: dict[str, Any]
    assignments: list[AllocationAssignment]
    warnings: list[str] = Field(default_factory=list)
    open_mandatory_roles: list[str] = Field(default_factory=list)
    open_optional_roles: list[str] = Field(default_factory=list)
    standby_employees: list[Employee] = Field(default_factory=list)
    aisle_utilization: list[dict[str, Any]] = Field(default_factory=list)
    support_assignments: list[dict[str, Any]] = Field(default_factory=list)

class FinalizationRequest(BaseModel):
    daily_input: DailyInput
    role_plan: RolePlan
    allocation_result: AllocationResult

class FinalizationResult(BaseModel):
    run_id: int
    status: str
    export_filename: str
    message: str

class AllocationHistoryEntry(BaseModel):
    run_id: int
    shift_date: str
    status: str
    assigned_count: int
    total_volume: int
    export_filename: str
    created_at: str
