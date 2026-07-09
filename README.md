# Job Allocation App (lokaler MVP)

Lokaler End-to-End-MVP für Supervisoren mit Next.js Frontend, FastAPI Backend, SQLite-Speicherung und Excel-Export. Die App nutzt eine Dummy-Allocation-Engine, die später durch eine echte Python Allocation Engine ersetzt werden kann.

## Projektstruktur

```text
frontend/                 Next.js, TypeScript, Tailwind CSS, shadcn/ui-inspirierte Komponenten
backend/                  FastAPI Backend
backend/app/api/          REST-Endpunkte
backend/app/services/     SQLite-, Excel- und Allocation-Services
backend/app/parsers/      Parser für Copy-&-Paste-Aisle-/Volumendaten
backend/app/engine/       Austauschbare Allocation Engine
backend/data/             Lokale SQLite-Datenbank
backend/outputs/          Lokal gespeicherte Excel-Exports
```

## Voraussetzungen

- Node.js 18 oder neuer
- Python 3.11 oder neuer

## Backend starten

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Das Backend läuft dann unter <http://localhost:8000>.

## Frontend starten

In einem zweiten Terminal:

```bash
cd frontend
npm install
npm run dev
```

Das Frontend läuft dann unter <http://localhost:3000>.

## MVP-Flow

1. Schichtdatum auswählen.
2. Optional Mitarbeiter-/Skill-Matrix als Excel-Datei hochladen.
3. Anwesenheit, Build Time, Rates und Volumen bearbeiten.
4. Rohe Aisle-/Volumendaten in das große Textfeld einfügen.
5. Vorschau prüfen.
6. **Allocation berechnen** klicken.
7. Ergebnis prüfen, lokal in SQLite speichern und Excel-Datei herunterladen.
8. Jede Excel-Datei wird zusätzlich in `backend/outputs/` gespeichert.

## Erwartetes Excel-Format für Uploads

Der Upload ist bewusst tolerant. Empfohlene Spalten:

| name | skills | present |
| --- | --- | --- |
| Alex Morgan | Pick, Pack | true |
| Sam Rivera | Rebin | true |

- `name` ist erforderlich.
- `skills` kann kommasepariert sein.
- `present` akzeptiert z. B. `true`, `false`, `1`, `0`, `yes`, `no`.

## Copy-&-Paste Parser

Der Parser erkennt einfache Zeilen wie:

```text
Aisle A01 1200
B02: 850
Finger F3 - 640
```

Er extrahiert die Aisle-/Finger-Bezeichnung und das letzte Zahlenvolumen der Zeile.

## Dummy Allocation Engine ersetzen

Die austauschbare Engine liegt in `backend/app/engine/dummy_engine.py`. Eine echte Engine kann später über `backend/app/services/allocation_service.py` angebunden werden, solange sie dieselbe Ergebnisstruktur liefert.
