from __future__ import annotations
from app.models import AllocationAssignment, AllocationResult, DailyInput, Employee, RolePlan, RolePlanItem, RolePlanValidation, ValidationIssue

ROLE_CATALOG = [
    {'engine_cluster':'Stow A','role':'Stower A','type':'volume_based','editable':True,'minimum':0},
    {'engine_cluster':'Stow B/C','role':'Stower B/C','type':'volume_based','editable':True,'minimum':0},
    {'engine_cluster':'Pick A','role':'Picker','type':'mandatory','editable':False,'minimum':0},
    {'engine_cluster':'Induct','role':'Induct','type':'mandatory','editable':'restricted','minimum':2},
    {'engine_cluster':'ASL','role':'ASL','type':'volume_based','editable':True,'minimum':0},
    {'engine_cluster':'ASML','role':'ASML','type':'volume_based','editable':True,'minimum':0},
    {'engine_cluster':'Yard Marshall','role':'Yard Marshall','type':'mandatory','editable':False,'minimum':1},
    {'engine_cluster':'Problem Solver','role':'Problem Solver','type':'optional','editable':True,'minimum':0},
    {'engine_cluster':'Line Lead','role':'Line Lead','type':'fixed','editable':True,'minimum':0},
    {'engine_cluster':'Standby','role':'Standby','type':'surplus','editable':True,'minimum':0},
]
ROLE_BY_CLUSTER = {r['engine_cluster']: r for r in ROLE_CATALOG}
STOW_RATES = {'Stow A':'stow_rate_a','Stow B/C':'stow_rate_bc'}

def get_additional_role_catalog() -> list[dict]:
    return ROLE_CATALOG

def skilled_count(employees: list[Employee], cluster: str) -> int:
    return sum(1 for e in employees if e.present and e.allocatable and (cluster in e.skills or 'Allrounder' in e.skills or (cluster.startswith('Stow') and 'Stow' in e.skills)))

def rate_value(inp: DailyInput, key: str, default: float) -> float:
    for rate in inp.rates:
        if rate.key == key:
            return rate.current_value or default
    return default

def calculate_stow_utilization(cluster: str, count: int, inp: DailyInput) -> float | None:
    """Dummy/MVP-Auslastung: Stow-Volumen je Cluster geteilt durch Rate * Belt-Time * Stower."""
    if cluster not in STOW_RATES:
        return None
    if count <= 0:
        return None
    active_finger = 'A' if cluster == 'Stow A' else None
    volume = sum(v.total_volume for v in inp.volumes if (v.finger == active_finger if active_finger else v.finger != 'A'))
    if volume <= 0:
        volume = sum(v.total_volume for v in inp.volumes)
    capacity = rate_value(inp, STOW_RATES[cluster], 105 if cluster == 'Stow A' else 120) * rate_value(inp, 'stow_belt_time', 7.5) * count
    return round((volume / capacity) * 100, 1) if capacity > 0 else None

def sync_pick_a(items: list[RolePlanItem]) -> None:
    stow = next((i for i in items if i.engine_cluster == 'Stow A'), None)
    pick = next((i for i in items if i.engine_cluster == 'Pick A'), None)
    if stow and pick:
        pick.current_count = stow.current_count
        pick.suggested_count = stow.current_count
        pick.editable = False
        pick.warnings = sorted(set([*pick.warnings, 'Automatisch gekoppelt an Stow A']))

def calculate_role_plan(inp: DailyInput) -> RolePlan:
    alloc = [e for e in inp.employees if e.present and e.allocatable]
    total = sum(v.total_volume for v in inp.volumes)
    target = len(alloc)
    base = {'Induct':2,'Yard Marshall':1}
    remaining = max(target - sum(base.values()), 0)
    weights = {'Stow A':0.25,'Stow B/C':0.35,'ASL':0.18,'ASML':0.22}
    suggested = dict(base)
    for c,w in weights.items(): suggested[c] = int(remaining*w)
    suggested['Pick A'] = suggested['Stow A']
    while sum(suggested.values()) < target: suggested['Stow B/C'] += 1
    while sum(suggested.values()) > target and suggested['Stow B/C'] > 0: suggested['Stow B/C'] -= 1
    items=[]
    for cfg in ROLE_CATALOG[:7]:
        cluster=cfg['engine_cluster']; avail=skilled_count(inp.employees, cluster); count=suggested.get(cluster, 0)
        maxc = avail if cfg['editable'] else count
        warn = []
        if cluster == 'Pick A': warn.append('Automatisch gekoppelt an Stow A')
        if count > avail: warn.append(f'Nur {avail} qualifizierte Dummy-Mitarbeiter verfügbar')
        items.append(RolePlanItem(engine_cluster=cluster,suggested_count=count,current_count=count,minimum_count=cfg['minimum'],maximum_count=maxc,mandatory=cfg['type']=='mandatory',editable=cfg['editable'],type=cfg['type'],available_skilled_employees=avail,warnings=warn,average_utilization_percent=calculate_stow_utilization(cluster,count,inp)))
    sync_pick_a(items)
    return RolePlan(target_positions=target,current_positions=sum(i.current_count for i in items),items=items,warnings=[f'Dummy-Rollenplan aus {total} Units abgeleitet'])

def validate_role_plan(plan: RolePlan) -> RolePlanValidation:
    issues=[]; current=sum(i.current_count for i in plan.items); seen=set(); stow_a=None; pick_a=None
    for i in plan.items:
        if i.engine_cluster in seen: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster}: Rolle ist doppelt im Rollenplan enthalten.',field=i.engine_cluster))
        seen.add(i.engine_cluster)
        if i.engine_cluster not in ROLE_BY_CLUSTER: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster}: unbekannte Rolle.',field=i.engine_cluster))
        if i.current_count < 0: issues.append(ValidationIssue(severity='error',message='Rollenanzahl darf nicht kleiner als 0 sein.',field=i.engine_cluster))
        if i.current_count < i.minimum_count: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster}: Pflichtrolle darf nicht unter Minimum {i.minimum_count} liegen.',field=i.engine_cluster))
        if i.maximum_count is not None and i.current_count > i.maximum_count: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster} wurde auf {i.current_count} gesetzt. Es sind nur {i.maximum_count} qualifizierte anwesende Mitarbeiter verfügbar. Maximal mögliche Anzahl: {i.maximum_count}',field=i.engine_cluster))
        if i.engine_cluster == 'Stow A': stow_a=i.current_count
        if i.engine_cluster == 'Pick A': pick_a=i.current_count
    if stow_a is not None and pick_a is not None and pick_a != stow_a:
        issues.append(ValidationIssue(severity='error',message='Pick A muss automatisch Stow A entsprechen.',field='Pick A'))
    if current != plan.target_positions:
        diff=plan.target_positions-current
        msg=f'Es fehlt {diff} Position.' if diff==1 else (f'Es fehlen {diff} Positionen.' if diff>0 else (f'Es ist {-diff} Position zu viel.' if diff==-1 else f'Es sind {-diff} Positionen zu viel.'))
        issues.append(ValidationIssue(severity='error',message=msg,field='role_plan'))
    return RolePlanValidation(is_valid=not any(x.severity=='error' for x in issues),target_positions=plan.target_positions,current_positions=current,issues=issues)

def final_allocation(inp: DailyInput, plan: RolePlan) -> AllocationResult:
    val=validate_role_plan(plan)
    if not val.is_valid:
        return AllocationResult(run_status='invalid_role_plan',kpis={'issue_count':len(val.issues)},assignments=[],warnings=[i.message for i in val.issues])
    employees=[e for e in inp.employees if e.present and e.allocatable]
    idx=0; assignments=[]; aisles=inp.volumes or []
    for item in plan.items:
        role = ROLE_BY_CLUSTER.get(item.engine_cluster, {'role': item.engine_cluster})['role']
        for _ in range(item.current_count):
            if idx >= len(employees): break
            e=employees[idx]; v=aisles[idx % len(aisles)] if aisles else None; idx+=1
            assignments.append(AllocationAssignment(employee_id=e.employee_id,badge_id=e.badge_id,name=e.name,user_id=e.user_id,role=role,engine_cluster=item.engine_cluster,fclm_cluster=item.engine_cluster.replace('/',' '),finger=v.finger if v else None,primary_aisles=[v.aisle] if v else [],primary_volume=v.total_volume if v else 0,load_percent=round(min(((v.total_volume if v else 0)/900)*100,160),1),internal_note='Deterministische Dummy-Zuteilung'))
    standby=employees[idx:]
    total=sum(v.total_volume for v in inp.volumes); sd=sum(v.sd_volume for v in inp.volumes); nd=sum(v.nd_volume for v in inp.volumes)
    kpis={'present_employees':sum(e.present for e in inp.employees),'allocatable_employees':len(employees),'assigned_employees':len(assignments),'open_mandatory_roles':0,'standby_count':len(standby),'sd_volume':sd,'nd_volume':nd,'total_volume':total,'issue_count':0}
    return AllocationResult(run_status='dummy_success',kpis=kpis,assignments=assignments,standby_employees=standby,aisle_utilization=[v.model_dump() for v in inp.volumes],warnings=['Dummy-Engine: keine Solver-Optimierung aktiv'])
