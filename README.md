# ARIA 18+ Throughput Collector

Portabler SSRS-Bericht mit eingebetteten SQL-Abfragen für standortübergreifende Durchsatz- und Klinikvergleiche in der Strahlentherapie. Ein Standort führt ihn einmal gegen seine lokale ARIA-DWH aus und exportiert die Ergebnisblätter als Excel. Die Ausgabe erfasst Zeitraum, aktive Geräte, Sitzungen, Patienten, Gerätetage, Betriebsfenster, Taktung, lange Lücken, Slotnutzung, Fallmix, Bildgebung, Patientenanmeldung, Workflowstatus und Datenqualität in einer methodisch einheitlichen Form.

## In drei Schritten

1. `ARIA18_Durchsatz_Klinikvergleich_Collector.rdl` aus der neuesten GitHub-Release herunterladen.
2. Die RDL im ARIA-Modul **Berichte** beziehungsweise im Microsoft Report Builder importieren und mit der lokalen gemeinsamen Datenquelle `variandw` verbinden.
3. Bericht ausführen, Zeitraum und Therapiegeräte auswählen und als Excel exportieren.

Für eine erste lokale Auswertung genügt anschließend:

```powershell
py -3 -m pip install -r requirements-analysis.txt
py -3 tools/analyze_single_site.py "Collector-Export.xlsx" --output-dir analysis_output
```

Unter Windows kann alternativ `tools/Analyse_Einzelstandort.bat` mit der Exceldatei als Argument gestartet werden. Das Skript erzeugt eine kompakte Auswertungs-Exceldatei und einen HTML-Bericht. Es exportiert keine Detailzeilen oder Hashschlüssel in den Ergebnisbericht.

Der Bericht wurde produktiv mit ARIA 18 und dem zugehörigen DWH/SSRS getestet. Er ist für ARIA 18 und neuere Versionen mit kompatiblem DWH-Schema vorgesehen. Bei lokalen Schemaabweichungen dokumentiert das Blatt `00_Coverage`, welche optionale Quelle nicht verfügbar war.

Der Einstieg im Quellpaket ist `dist/ARIA18_Durchsatz_Klinikvergleich_Collector.rdl`. Die ausführliche Installation und der Export sind in `README_Installation_und_Export.md` beschrieben. Felddefinitionen stehen in `Datenwoerterbuch.md`; die Gegenprüfung in `validation/validation_report.md`.

## Was der Export beantwortet

- Von wann bis wann und an wie vielen Geräten wurde tatsächlich behandelt?
- Wie viele Sitzungen und Patienten wurden pro Gerät, Monat und Gerätetag versorgt?
- Wie lang waren Betriebsfenster, Sitzungen, Start-zu-Start-Takte und Lücken?
- Wie gut deckten geplante Slots die tatsächlichen Behandlungen ab?
- Wie lange lagen Patientenanmeldung, Laden des Patienten, erste Bildgebung, erster Beam und Terminabschluss auseinander?
- Wie unterscheiden sich Technik, Fraktionierung, Diagnosegruppen und Bildgebung?
- Welche Datenquellen waren am Standort verfügbar und wo bestehen Qualitätslücken?

## Verzeichnisstruktur

- `dist`: weiterzugebende RDL und Prüfsummen
- `sql`: SQL-Quellen der einzelnen Datasets
- `templates`: RDL-Vorlage
- `tools`: Build, Prüfung, SQL-Smoke-Test und HTTP/SSRS-Test
- `tools/analyze_single_site.py`: lokale Einzelstandort-Auswertung aus einem Collector-Excel-Export
- `tests`: statische Vertrags- und Datenschutztests
- `validation`: eingefrorener Methodenvergleich ohne Patientendaten

## Datenschutz

Aggregierte Blätter sind für standortübergreifende Analysen vorgesehen. Die optionalen Detailblätter sind pseudonymisiert, aber weiterhin als kontrollierte Forschungsdaten zu behandeln. Der pro Ausführung erzeugte Salt wird nicht exportiert; Hash-Schlüssel lassen sich deshalb nicht zwischen unabhängigen Läufen verknüpfen.

Namen, Geburtsdaten, ursprüngliche Patienten- oder Plan-IDs, Freitexte und DICOM-UIDs werden nicht exportiert. Vor einer externen Weitergabe bleibt eine lokale Datenschutz- und Freigabeprüfung erforderlich.

Ankunfts-, Pending-/In-Progress- und Abschlusszeiten sind Workflowzeitpunkte und keine Strahlenapplikationszeiten. Der klinische Start-Proxy verwendet die erste dokumentierte Bildgebung, sofern sie vor dem ersten Beam liegt, sonst den ersten Beam. Beide Rohzeitpunkte werden getrennt ausgegeben.

## Abgrenzung

Der Collector ist ein Analyse- und Forschungswerkzeug. Er verändert keine ARIA-Daten und ist nicht für klinische Entscheidungen, Terminsteuerung oder die Behandlung einzelner Patienten bestimmt. Die SQL-Abfragen sind read-only. Installation, Datenfreigabe und Interpretation bleiben in der Verantwortung des jeweiligen Standorts.
