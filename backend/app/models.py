from pydantic import BaseModel, Field
from typing import List

class Employee(BaseModel):
    id: str
    name: str
    skills: List[str] = Field(default_factory=list)
    present: bool = True

class AisleVolume(BaseModel):
    aisle: str
    volume: int

class AllocationInput(BaseModel):
    shift_date: str
    build_time_hours: float = 7.5
    rate_per_hour: int = 120
    target_volume: int = 0
    employees: List[Employee]
    aisle_volumes: List[AisleVolume]

class AllocationResult(BaseModel):
    employee_id: str
    employee_name: str
    role: str
    aisle: str
    volume: int
    utilization: float
    warnings: List[str] = Field(default_factory=list)

class AllocationResponse(BaseModel):
    allocation_id: int
    export_filename: str
    results: List[AllocationResult]
