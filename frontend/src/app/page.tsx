'use client';
import { useMemo, useState } from 'react';
import { Button, Card, Input, Textarea } from '@/components/ui';

type Employee = { id: string; name: string; skills: string[]; present: boolean };
type AisleVolume = { aisle: string; volume: number };
type Result = { employee_name: string; role: string; aisle: string; volume: number; utilization: number; warnings: string[] };
const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
const starterEmployees: Employee[] = [
  { id: 'emp-1', name: 'Alex Morgan', skills: ['Pick'], present: true },
  { id: 'emp-2', name: 'Sam Rivera', skills: ['Pack', 'Rebin'], present: true },
  { id: 'emp-3', name: 'Taylor Chen', skills: ['Stow'], present: false },
];

export default function Home() {
  const [shiftDate, setShiftDate] = useState(new Date().toISOString().slice(0, 10));
  const [employees, setEmployees] = useState<Employee[]>(starterEmployees);
  const [buildTimeHours, setBuildTimeHours] = useState(7.5);
  const [ratePerHour, setRatePerHour] = useState(120);
  const [targetVolume, setTargetVolume] = useState(2400);
  const [rawText, setRawText] = useState('Aisle A01 1200\nB02: 850\nFinger F3 - 640');
  const [preview, setPreview] = useState<AisleVolume[]>([]);
  const [results, setResults] = useState<Result[]>([]);
  const [exportFile, setExportFile] = useState('');
  const presentCount = useMemo(() => employees.filter((employee) => employee.present).length, [employees]);

  async function parseRows() {
    const items = await parseRawRows();
    setPreview(items);
  }

  async function parseRawRows(): Promise<AisleVolume[]> {
    const response = await fetch(`${API}/parse-aisles`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ raw_text: rawText }) });
    const data = await response.json();
    return data.items ?? [];
  }

  async function uploadEmployees(file?: File) {
    if (!file) return;
    const body = new FormData();
    body.append('file', file);
    const response = await fetch(`${API}/employees/upload`, { method: 'POST', body });
    const data = await response.json();
    setEmployees(data.employees);
  }

  async function calculate() {
    const aisle_volumes = preview.length ? preview : await parseRawRows();
    if (!preview.length) setPreview(aisle_volumes);
    const response = await fetch(`${API}/allocations`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shift_date: shiftDate, build_time_hours: buildTimeHours, rate_per_hour: ratePerHour, target_volume: targetVolume, employees, aisle_volumes }),
    });
    const data = await response.json();
    setResults(data.results ?? []);
    setExportFile(data.export_filename ?? '');
  }

  return <main className="mx-auto max-w-7xl space-y-6 p-6">
    <section className="rounded-3xl bg-gradient-to-r from-blue-700 to-indigo-600 p-8 text-white shadow-lg">
      <p className="text-sm uppercase tracking-widest opacity-80">Lokaler MVP</p>
      <h1 className="mt-2 text-4xl font-bold">Job Allocation Dashboard</h1>
      <p className="mt-3 max-w-3xl text-blue-100">Tagesdaten erfassen, Aisle-Volumen parsen, Allocation berechnen, lokal speichern und als Excel exportieren.</p>
    </section>
    <section className="grid gap-4 md:grid-cols-4">
      <Card><p className="text-sm text-slate-500">Schichtdatum</p><Input type="date" value={shiftDate} onChange={(event) => setShiftDate(event.target.value)} /></Card>
      <Card><p className="text-sm text-slate-500">Anwesend</p><p className="text-3xl font-bold">{presentCount}/{employees.length}</p></Card>
      <Card><p className="text-sm text-slate-500">Zielvolumen</p><Input type="number" value={targetVolume} onChange={(event) => setTargetVolume(Number(event.target.value))} /></Card>
      <Card><p className="text-sm text-slate-500">Kapazität</p><p className="text-3xl font-bold">{Math.round(buildTimeHours * ratePerHour * Math.max(presentCount, 1))}</p></Card>
    </section>
    <section className="grid gap-6 lg:grid-cols-2">
      <Card><h2 className="text-xl font-semibold">Mitarbeiter & Skills</h2><Input className="mt-4" type="file" accept=".xlsx" onChange={(event) => uploadEmployees(event.target.files?.[0])} />
        <div className="mt-4 space-y-2">{employees.map((employee, index) => <label key={employee.id} className="flex items-center gap-3 rounded-xl border p-3"><input type="checkbox" checked={employee.present} onChange={(event) => setEmployees((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, present: event.target.checked } : item))} /><span className="font-medium">{employee.name}</span><span className="text-sm text-slate-500">{employee.skills.join(', ') || 'keine Skills'}</span></label>)}</div></Card>
      <Card><h2 className="text-xl font-semibold">Build Time & Rates</h2><div className="mt-4 grid gap-3"><label>Build Time (h)<Input type="number" step="0.25" value={buildTimeHours} onChange={(e) => setBuildTimeHours(Number(e.target.value))} /></label><label>Rate pro Stunde<Input type="number" value={ratePerHour} onChange={(e) => setRatePerHour(Number(e.target.value))} /></label></div></Card>
    </section>
    <Card><h2 className="text-xl font-semibold">Aisle-/Volumendaten einfügen</h2><Textarea rows={8} value={rawText} onChange={(event) => setRawText(event.target.value)} /><Button className="mt-3" onClick={parseRows}>Parser-Vorschau erzeugen</Button></Card>
    <Card><h2 className="text-xl font-semibold">Vorschau & Berechnung</h2><div className="mt-3 grid gap-2 md:grid-cols-3">{preview.map((item) => <div key={item.aisle} className="rounded-xl bg-slate-100 p-3"><b>{item.aisle}</b><p>{item.volume} Units</p></div>)}</div><Button className="mt-4" onClick={calculate}>Allocation berechnen</Button></Card>
    {results.length > 0 && <Card><div className="flex items-center justify-between"><h2 className="text-xl font-semibold">Ergebnis</h2>{exportFile && <a className="font-semibold text-blue-700" href={`${API}/exports/${exportFile}`}>Excel herunterladen</a>}</div><div className="mt-4 overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th>Mitarbeiter</th><th>Rolle</th><th>Aisle/Finger</th><th>Volumen</th><th>Auslastung</th><th>Warnungen</th></tr></thead><tbody>{results.map((result, index) => <tr key={`${result.aisle}-${index}`} className="border-b"><td>{result.employee_name}</td><td>{result.role}</td><td>{result.aisle}</td><td>{result.volume}</td><td>{Math.round(result.utilization * 100)}%</td><td>{result.warnings.join(', ') || 'OK'}</td></tr>)}</tbody></table></div></Card>}
  </main>;
}
