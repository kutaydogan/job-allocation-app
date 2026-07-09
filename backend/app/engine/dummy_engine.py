from __future__ import annotations
from app.models import AllocationAssignment, AllocationResult, DailyInput, Employee, RolePlan, RolePlanItem, RolePlanValidation, ValidationIssue

CLUSTERS = [
    ('Stow A','Stower A','volume-dependent',True,0),('Stow B/C','Stower B/C','volume-dependent',True,0),
    ('Pick A','Picker','mandatory',False,2),('Induct','Induct','mandatory','restricted',2),
    ('ASL','ASL','volume-dependent',True,0),('ASML','ASML','volume-dependent',True,0),('Yard Marshall','Yard Marshall','mandatory',False,1),
]

def skilled_count(employees: list[Employee], cluster: str) -> int:
    return sum(1 for e in employees if e.present and e.allocatable and (cluster in e.skills or 'Allrounder' in e.skills or (cluster.startswith('Stow') and 'Stow' in e.skills)))

def calculate_role_plan(inp: DailyInput) -> RolePlan:
    alloc = [e for e in inp.employees if e.present and e.allocatable]
    total = sum(v.total_volume for v in inp.volumes)
    target = len(alloc)
    base = {'Pick A':2,'Induct':2,'Yard Marshall':1}
    remaining = max(target - sum(base.values()), 0)
    weights = {'Stow A':0.25,'Stow B/C':0.35,'ASL':0.18,'ASML':0.22}
    suggested = dict(base)
    for c,w in weights.items(): suggested[c] = int(remaining*w)
    while sum(suggested.values()) < target: suggested['Stow B/C'] += 1
    while sum(suggested.values()) > target and suggested['Stow B/C'] > 0: suggested['Stow B/C'] -= 1
    items=[]
    for cluster, _role, typ, editable, minimum in CLUSTERS:
        avail = skilled_count(inp.employees, cluster)
        count = suggested.get(cluster, 0)
        maxc = avail if editable else count
        warn = []
        if count > avail: warn.append(f'Nur {avail} qualifizierte Dummy-Mitarbeiter verfügbar')
        items.append(RolePlanItem(engine_cluster=cluster,suggested_count=count,current_count=count,minimum_count=minimum,maximum_count=maxc,mandatory=typ=='mandatory',editable=editable,type=typ,available_skilled_employees=avail,warnings=warn))
    return RolePlan(target_positions=target,current_positions=sum(i.current_count for i in items),items=items,warnings=[f'Dummy-Rollenplan aus {total} Units abgeleitet'])

def validate_role_plan(plan: RolePlan) -> RolePlanValidation:
    issues=[]
    current=sum(i.current_count for i in plan.items)
    if current != plan.target_positions:
        diff=plan.target_positions-current
        issues.append(ValidationIssue(severity='error',message=(f'Es fehlen {diff} Positionen.' if diff>0 else f'Es sind {-diff} Positionen zu viel.'),field='role_plan'))
    seen=set()
    for i in plan.items:
        if i.engine_cluster in seen: issues.append(ValidationIssue(severity='error',message=f'Doppelter Cluster {i.engine_cluster}'))
        seen.add(i.engine_cluster)
        if i.current_count < 0: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster}: negative Anzahl'))
        if i.current_count < i.minimum_count: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster}: Mindestwert {i.minimum_count} unterschritten'))
        if i.maximum_count is not None and i.current_count > i.maximum_count: issues.append(ValidationIssue(severity='error',message=f'{i.engine_cluster}: maximal mögliche Anzahl {i.maximum_count}',field=i.engine_cluster))
    return RolePlanValidation(is_valid=not any(x.severity=='error' for x in issues),target_positions=plan.target_positions,current_positions=current,issues=issues)

def final_allocation(inp: DailyInput, plan: RolePlan) -> AllocationResult:
    employees=[e for e in inp.employees if e.present and e.allocatable]
    idx=0; assignments=[]; aisles=inp.volumes or []
    for item in plan.items:
        role = next(r for c,r,_,_,_ in CLUSTERS if c==item.engine_cluster)
        for n in range(item.current_count):
            if idx >= len(employees): break
            e=employees[idx]; v=aisles[idx % len(aisles)] if aisles else None; idx+=1
            assignments.append(AllocationAssignment(employee_id=e.employee_id,badge_id=e.badge_id,name=e.name,user_id=e.user_id,role=role,engine_cluster=item.engine_cluster,fclm_cluster=item.engine_cluster.replace('/',' '),finger=v.finger if v else None,primary_aisles=[v.aisle] if v else [],primary_volume=v.total_volume if v else 0,load_percent=round(min(((v.total_volume if v else 0)/900)*100,160),1),internal_note='Deterministische Dummy-Zuteilung'))
    standby=employees[idx:]
    total=sum(v.total_volume for v in inp.volumes); sd=sum(v.sd_volume for v in inp.volumes); nd=sum(v.nd_volume for v in inp.volumes)
    kpis={'present_employees':sum(e.present for e in inp.employees),'allocatable_employees':len(employees),'assigned_employees':len(assignments),'open_mandatory_roles':0,'standby_count':len(standby),'sd_volume':sd,'nd_volume':nd,'total_volume':total,'issue_count':0}
    return AllocationResult(run_status='dummy_success',kpis=kpis,assignments=assignments,standby_employees=standby,aisle_utilization=[v.model_dump() for v in inp.volumes],warnings=['Dummy-Engine: keine Solver-Optimierung aktiv'])
