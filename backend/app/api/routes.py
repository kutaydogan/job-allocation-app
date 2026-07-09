from __future__ import annotations
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.engine.dummy_engine import calculate_role_plan, final_allocation, validate_role_plan
from app.models import *
from app.services.database import list_allocations, save_finalization
from app.services.excel_service import OUTPUT_DIR, export_finalization, parse_employee_workbook

router = APIRouter()
RATES=[OperationalRate(key='stow_a',name='Stow Rate A',default_value=105,current_value=105,unit='uph'),OperationalRate(key='stow_bc',name='Stow Rate B/C',default_value=120,current_value=120,unit='uph'),OperationalRate(key='adta_stow',name='ADTA Stow Rate',default_value=135,current_value=135,unit='uph'),OperationalRate(key='pick',name='Pick Rate',default_value=95,current_value=95,unit='uph'),OperationalRate(key='induct',name='Induct Rate',default_value=1100,current_value=1100,unit='uph'),OperationalRate(key='asl',name='ASL Rate',default_value=850,current_value=850,unit='uph'),OperationalRate(key='asml',name='ASML Rate',default_value=900,current_value=900,unit='uph'),OperationalRate(key='belt_time',name='Belt Time',default_value=7.5,current_value=7.5,unit='h'),OperationalRate(key='new_hire_days',name='New Hire Days',default_value=14,current_value=14,unit='days')]
DUMMY=[]
for i in range(1,37):
    eid=f'{123456000+i}'; skills=['Stow']
    if i%2==0: skills.append('Stow B/C')
    if i%3==0: skills.append('Pick A')
    if i%4==0: skills.append('ASL')
    if i%5==0: skills.append('ASML')
    if i%6==0: skills.append('Induct')
    if i%9==0: skills.append('Yard Marshall')
    if i%7==0: skills.append('Allrounder')
    DUMMY.append(Employee(employee_id=eid,name=f'Dummy Associate {i:02d}',badge_id=f'B{i:05d}',user_id=f'dummy{i:02d}',skills=skills,notes=['Dummy-Stammdaten'],new_hire=i%10==0,l3=i%8==0,present=True,allocatable=i%13!=0))
MASTER={e.employee_id:e for e in DUMMY}

def ids(raw:str)->list[str]: return re.findall(r'\d{5,}', raw or '')
def parse_one(raw:str)->dict[str,int]:
    # MVP adapter point: replace this tokenizer when real SD/ND copy format is known.
    out={}
    for aisle,num in re.findall(r'\b([A-Z][0-9]{2})\b\D{0,40}([0-9][0-9.,]*)', raw.upper()):
        out[aisle]=out.get(aisle,0)+int(float(num.replace('.','').replace(',','.')))
    return out

@router.get('/health')
def health(): return {'status':'ok','mode':'local_dummy_mvp'}

@router.post('/employees/resolve', response_model=EmployeeResolutionResponse)
def resolve(req: EmployeeResolutionRequest):
    raw=ids(req.raw_employee_ids); seen=set(); dup=[]; employees=[]; unknown=[]
    for eid in raw:
        if eid in seen: dup.append(eid); continue
        seen.add(eid)
        if eid in MASTER: employees.append(MASTER[eid])
        else: unknown.append(eid); employees.append(Employee(employee_id=eid,name='Unbekannt',badge_id='',user_id='',status='unknown',present=False,allocatable=False,notes=['Nicht im Dummy-Stamm gefunden']))
    return EmployeeResolutionResponse(total_ids=len(raw),found_count=sum(e.status=='found' for e in employees),unknown_ids=unknown,duplicate_ids=dup,employees=employees)

@router.post('/volumes/parse', response_model=VolumeParseResponse)
def volumes(req: VolumeParseRequest):
    sd=parse_one(req.sd_raw_text); nd=parse_one(req.nd_raw_text); aisles=[]
    for aisle in sorted(set(sd)|set(nd)):
        s=sd.get(aisle,0); n=nd.get(aisle,0); aisles.append(AisleVolume(finger=aisle[0],aisle=aisle,sd_volume=s,nd_volume=n,total_volume=s+n))
    return VolumeParseResponse(aisles=aisles,sd_total=sum(sd.values()),nd_total=sum(nd.values()),total_volume=sum(sd.values())+sum(nd.values()),aisle_count=len(aisles),active_fingers=sorted({a[0] for a in set(sd)|set(nd)}),warnings=[] if aisles else ['Keine Aisle-Volumen-Paare erkannt'])

@router.get('/config/rates', response_model=list[OperationalRate])
def rates(): return RATES

@router.post('/validation/pre-run', response_model=ValidationResult)
def pre(inp: DailyInput):
    issues=[]; present=sum(e.present for e in inp.employees); alloc=sum(e.present and e.allocatable for e in inp.employees)
    for ok,msg in [(present>0,f'{present} Mitarbeiter anwesend'),(alloc>0,f'{alloc} Mitarbeiter allokierbar'),(sum(v.total_volume for v in inp.volumes)>0,f'{sum(v.sd_volume for v in inp.volumes)} SD / {sum(v.nd_volume for v in inp.volumes)} ND Volume erkannt'),(inp.previous_day_found,'Vortagsdaten vorhanden'),(True,'Dummy-Skill-Matrix geladen')]: issues.append(ValidationIssue(severity='success' if ok else 'error',message=msg))
    if any(e.status=='unknown' for e in inp.employees): issues.append(ValidationIssue(severity='warning',message='Unbekannte Employee IDs vorhanden'))
    for r in inp.rates:
        if r.current_value <= 0: issues.append(ValidationIssue(severity='error',message=f'{r.name} muss positiv sein',field=r.key))
    return ValidationResult(is_valid=not any(i.severity=='error' for i in issues),error_count=sum(i.severity=='error' for i in issues),warning_count=sum(i.severity=='warning' for i in issues),issues=issues)

@router.post('/role-plan/calculate', response_model=RolePlan)
def role_calc(inp: DailyInput): return calculate_role_plan(inp)
@router.post('/role-plan/validate', response_model=RolePlanValidation)
def role_val(plan: RolePlan): return validate_role_plan(plan)
@router.post('/allocation/final', response_model=AllocationResult)
def alloc(payload: dict): return final_allocation(DailyInput(**payload['daily_input']), RolePlan(**payload['role_plan']))
@router.post('/allocation/finalize', response_model=FinalizationResult)
def finalize(req: FinalizationRequest):
    filename=export_finalization(req); run_id=save_finalization(req,filename)
    return FinalizationResult(run_id=run_id,status='finalized',export_filename=filename,message='Allocation erfolgreich finalisiert')
@router.get('/allocations', response_model=list[AllocationHistoryEntry])
def history(): return list_allocations()
@router.get('/exports/{filename}')
def download_export(filename: str):
    path=OUTPUT_DIR / filename
    if not path.exists(): raise HTTPException(404,'Export nicht gefunden')
    return FileResponse(path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
@router.post('/employees/upload')
async def upload_employees(file: UploadFile = File(...)):
    suffix = Path(file.filename or 'employees.xlsx').suffix or '.xlsx'
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp: tmp.write(await file.read()); tmp_path=Path(tmp.name)
    try: return {'employees': parse_employee_workbook(tmp_path)}
    finally: tmp_path.unlink(missing_ok=True)
