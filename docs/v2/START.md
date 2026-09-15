# Standortanalyse 2.0

Ein rein lesender ARIA-Export und eine lokale Python-Auswertung fuer die
AG Digitalisierung. Kein direkter zentraler Zugriff auf die klinische Datenbank.
Die Auswertung kann lokal oder nach lokaler Freigabe im geschuetzten Projektbereich erfolgen.
Die interaktive Ergebnisdatei funktioniert ohne Webserver und ohne Internet.

## 1. Zeitraum

**Standardjahr: 1. Januar bis 31. Dezember 2025.** Bei einer begruendeten
Ausnahmesituation kann ein moeglichst aktuelles, vollstaendiges anderes Jahr
gewaehlt werden. Grund festhalten, zum Beispiel Geraeteersatz oder monatelanger
Stillstand. Eine stoerungsarme Periode ist nicht automatisch repraesentativer:
Stillstand kann selbst eine wesentliche Untersuchungsgroesse sein.

Primaere Vergleiche verwenden denselben Kalenderzeitraum. Abweichende Jahre
separat oder als Sensitivitaetsanalyse berichten, nicht unkommentiert zusammenwerfen.
Januar/Februar 2025 sind ein schneller Validierungszeitraum, kein Jahresersatz.

## 2. RDL

1. [ARIA18_Throughput_Collector_2.0.rdl](../../dist/ARIA18_Throughput_Collector_2.0.rdl)
   in ARIA Berichte importieren oder lokal im Report Builder oeffnen.
2. Gemeinsame Datenquelle an die lokale ARIA-DWH-Datenquelle binden.
   Vorgabepfad: `/VarianTemplate/Data Sources/variandw`.
3. Standort ersetzen und Auswertungszeitraum pruefen. Auswertungsdaten und
   Prueftabellen sind automatisch enthalten. Keine weitere Pflichtangabe.
4. Vorlauf und Nachbeobachtung werden automatisch bestimmt; der Terminartenkatalog
   wird vollstaendig geladen. Ein technischer Datenstand ist keine fachliche
   Vollstaendigkeitsgarantie.
5. Excel/CSV auf geschuetztem Speicher ablegen. Nicht oeffentlich hochladen.

Der RDL schreibt keine ARIA-Daten. Temporare Tabellen und Indizes existieren nur
in seiner SQL-Sitzung. Er kann nicht durch blosses Oeffnen einer RDL-Datei im
Browser ausgefuehrt werden. Der optionale Testweg nutzt eine temporaere
SSRS-Ausfuehrungsdefinition und veraendert keinen Katalogbericht.

Fuer grosse Ereignismengen gibt es zusaetzlich
[Collector Fast](../../dist/ARIA18_Throughput_Collector_Fast_2.0.rdl).
Dieser verwendet dieselbe geschuetzte Quellabfrage, exportiert aber ein flaches
**CSV** mit ISO-Zeitstempeln und eingebettetem Lauf-/Zeitraumvertrag.
Die Python-Auswertung akzeptiert CSV direkt. Das Aktivitaetsinventar und die
Spaltenabdeckung stehen im gemeinsamen Full-Collector-Excel.
Ein leeres Detail-CSV wird nicht als klinische Nullmenge interpretiert.

## 3. Profil

[site-template.json](../../profiles/site-template.json) als lokale Arbeitskopie
verwenden. `activity_codes` ordnet **exakte ActivityCode-Werte** zu:

```json
{
  "CONS": "counselling",
  "RETURN": "observation",
  "TX": "treatment_external",
  "BRACHY": "treatment_brachy",
  "LEGACY": "treatment_legacy",
  "XRAY": "treatment_xray",
  "BREAK": "block",
  "PLANNING": "ignore"
}
```

Das sind Beispiele, keine empfohlenen lokalen Aktivitaetscodes. Ein
abgeschlossener Planungstermin darf nicht zur Therapie erklaert werden.
Historische Maschinen einschliesslich nicht im R&V dokumentierter Therapie
ausdruecklich pruefen. `machines` ordnet exportierte Geraetecodes neutralen
Bezeichnungen zu. Nur bestaetigte Therapiegeraete aufnehmen.

`confirmed` erst nach Pruefung der Zuordnungen aktivieren;
`sources_complete` erst nach Pruefung aller relevanten Therapie- und
Aufklaerungsquellen. Ohne diese Bestaetigungen gibt es keine belastbare negative
Quote. Zusaetzlich muss `complete_through` mindestens den Datenstand im Export
abdecken. Diese Pruefung ist fuer den Export und andere berechenbare Kennzahlen
nicht erforderlich. Nicht zugeordnete Aktivitaeten werden als Qualitaetsluecke gemeldet.

## 4. Python

```powershell
python -m pip install -r requirements-analysis.txt
python -m analysis.cli "Collector.xlsx" --profile "standort.json" --output "Ergebnis"
```

Ausgabe: `Standortanalyse.html`, `Kennzahlen.csv`, `aggregate.json` und
`aggregate-cache.sqlite`. Keine Patienten-/Ereignisschluessel in diesen Dateien.
Der Cache bindet Dateiinhalt, Profil und Methodenversion. Dieselbe Datei unter
demselben Namen mit neuen Inhalten wird neu berechnet; Modell- und Periodenwechsel
im HTML brauchen weder SQL noch Python.

Vor Weitergabe HTML/CSV/JSON lokal freigeben. Auch Aggregate koennen
identifizierend sein. Kleine Gruppen werden unterdrueckt; diese technische
Massnahme allein garantiert keine Anonymitaet. Pseudonymisierte Detailblaetter
nur nach lokaler Freigabe ueber den geschuetzten Projektweg bereitstellen.

## Synthetischer Probelauf

```powershell
python tools/create_demo_v2.py --output .local/demo.xlsx
python -m analysis.cli .local/demo.xlsx --profile profiles/synthetic.json --output .local/report
```

Alle Personen, Zeitintervalle und Mengen dieser Demo sind frei erzeugt.
Kein Beispielpatient stammt aus einem klinischen System.

## Grenzen

Der Basisexport nutzt die DWH-Bildgebung. Eine direkte Imaging-Objektanalyse ist
nicht stillschweigend eingeschaltet; siehe [IMAGING](IMAGING.md).
Getestete SQL-Spalten bedeuten nicht, dass jeder Standort dieselben fachlichen
Status- und Aktivitaetskonventionen verwendet. Siehe [Validierung](VALIDIERUNG.md).

Fuer den naechsten Standort: [Minimalvoraussetzungen und Testablauf](STANDORTTEST.md).
