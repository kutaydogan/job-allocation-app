# PROJECT.md

## Aktueller Stand

Der lokale MVP bildet den Zielprozess der Job Allocation als geführten Workflow ab. Die echte Engine ist nicht angebunden.

## Umgesetzte Features

- Copy-&-Paste-Erkennung von Employee IDs mit Duplikat- und Unknown-Auswertung.
- Getrennte SD-/ND-Volumen-Erfassung mit Aisle-Parser.
- Editierbare operative Rates und Parameter.
- Vorvalidierung mit Fehlern, Warnungen und Erfolgsmeldungen.
- Separater Rollenplan-Schritt mit Supervisor-Anpassung und Summenvalidierung.
- Deterministische finale Dummy-Allocation.
- Finalisierung mit SQLite-Historie und Excel-Export.
- REST-Endpunkte und Pydantic-/TypeScript-Modelle für den späteren Engine-Adapter.

## Architekturentscheidungen

- Bestehende FastAPI/Next.js/SQLite/Excel-Architektur bleibt erhalten.
- Dummy-Engine ist isoliert in `backend/app/engine/dummy_engine.py`.
- Rates werden zentral im Backend bereitgestellt, ohne Standardwerte durch UI-Änderungen zu überschreiben.
- Parser-Logik ist bewusst einfach und an einer Stelle austauschbar.

## Offene Punkte

- Echte Stammdatenquelle anbinden.
- Echtes SD-/ND-Rohdatenformat präzise implementieren.
- Historische Vortagsdaten aus finalisierten Runs laden.
- Echte Skill-Matrix und echte Job-Allocation-Engine integrieren.
- UI-Komponenten bei wachsendem Umfang weiter feiner auslagern.

## Nächste Schritte

1. Reales Rohdatenformat sammeln und Parser ersetzen.
2. Mitarbeiterstamm-Adapter definieren.
3. Engine-Adapter kontraktieren und gegen die echten Modelle testen.
4. Fachliche Validierungsregeln mit Operations finalisieren.

## Geplante spätere Engine-Integration

`DailyInput` wird in das Eingabeformat der echten Engine übersetzt. Der validierte `RolePlan` wird als Supervisor-Override übergeben. Das Engine-Ergebnis wird wieder in `AllocationResult` gemappt, sodass Frontend, Historie und Excel-Export stabil bleiben.
