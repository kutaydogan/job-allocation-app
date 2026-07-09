# Job Allocation App

Lokaler MVP zur fachlichen Vorbereitung des späteren Job-Allocation-Workflows. Die echte `job-allocation-engine` wird **nicht** angebunden; alle Berechnungen laufen über klar gekennzeichnete Dummy-Logik.

## Architektur

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, Pydantic, Python
- Persistenz: SQLite unter `backend/data/allocation.db`
- Export: Excel-Dateien unter `backend/outputs/`
- Kommunikation: REST API unter `/api/*`

## Start unter Windows PowerShell

```powershell
cd job-allocation-app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --reload
```

In einem zweiten Terminal:

```powershell
cd job-allocation-app\frontend
npm install
npm run dev
```

Dann `http://localhost:3000` öffnen. Das Frontend erwartet standardmäßig `http://localhost:8000/api`.

## Neuer User Flow

1. Schichtdatum auswählen und simulierte Vortagsdaten prüfen.
2. Employee IDs gesammelt per Copy & Paste einfügen.
3. Mitarbeiter gegen Dummy-Stammdaten erkennen.
4. SD- und ND-Rohdaten getrennt einfügen und Aisle/Volumen-Paare parsen.
5. Operative Rates und Parameter prüfen oder schichtspezifisch ändern.
6. Eingaben vorvalidieren.
7. Rollenbedarf berechnen.
8. Zulässige Cluster-Anzahlen anpassen und Rollenplan validieren.
9. Finale Dummy-Allocation berechnen.
10. Ergebnis prüfen, finalisieren, SQLite-Historie schreiben und Excel exportieren.

## API-Endpunkte

- `GET /api/health`
- `POST /api/employees/resolve`
- `POST /api/volumes/parse`
- `GET /api/config/rates`
- `POST /api/validation/pre-run`
- `POST /api/role-plan/calculate`
- `POST /api/role-plan/validate`
- `POST /api/allocation/final`
- `POST /api/allocation/finalize`
- `GET /api/allocations`
- `GET /api/exports/{filename}`
- `POST /api/employees/upload` als Admin-/Fallback-Funktion

## Dummy-Daten

Das Backend erzeugt lokale Dummy-Mitarbeiter, Skills, New-Hire-/L3-Marker, operative Rates, Vortagsstatus, Rollenplan-Verfügbarkeiten und finale Zuweisungen. Die Daten sind austauschbar angelegt und ersetzen keine echten Stammdaten.

## Bekannte Einschränkungen

- Keine echte Solver- oder Engine-Optimierung.
- Volume-Parser ist bewusst modular und nutzt eine robuste MVP-Heuristik: Aisle-Code plus nachfolgende Zahl.
- Keine Authentifizierung und kein Deployment.
- Vortagsdaten sind derzeit simuliert.

## Spätere Engine-Integration

Der Integrationspunkt liegt im Backend in `backend/app/engine/dummy_engine.py`. Später kann dort ein Adapter zur echten Engine die Modelle `DailyInput`, `RolePlan` und `AllocationResult` übersetzen, ohne den UI-Workflow grundsätzlich zu ändern.
