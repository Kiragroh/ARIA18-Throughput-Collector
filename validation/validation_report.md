# Validierungsbericht

## Umfang

Der Collector wurde am 17.08.2026 read-only gegen eine produktive ARIA-18-DWH getestet. Für den Vergleich mit der eingefrorenen Leipziger Auswertung wurde derselbe Zeitraum vom 01.08.2025 bis 31.07.2026 und dieselbe Auswahl von vier Bestrahlungsgeräten verwendet.

## Technische Validierung

- Alle elf SQL-Datasets wurden ohne Schreiboperation gegen ARIA 18 ausgeführt.
- Der Report wurde auf dem SSRS-ReportServer in einem persönlichen Testordner veröffentlicht.
- PDF und Excel wurden über die HTTP-Render-API erfolgreich erzeugt; SSRS meldete keine Warnungen.
- Ein zweiter Excel-Test mit aktivierten pseudonymisierten Details erzeugte die Jahresblätter `90_Sessions_2026` und `91_Appointments_2026`.
- Der temporäre Testreport wurde nach jedem Lauf wieder vom ReportServer entfernt.
- Die Detailblätter enthalten Hash-Schlüssel, aber keine Namen, Geburtsdaten, ursprünglichen IDs, Freitexte oder DICOM-UIDs.

## Vergleich zur bisherigen Leipziger Auswertung

| Kennzahl | Bisherige Auswertung | Neuer Collector |
|---|---:|---:|
| Sitzungen | 39.414 | 39.422 |
| Eindeutige Patienten | 2.152 | 2.154 |
| Aktive Kalendertage | 259 | 261 |
| Aktive Samstage | 11 | 12 |
| Aktive Gerätetage | 1.032 | 1.035 |
| Brutto-Gerätestunden | 9.930,78 | 9.936,78 |
| Netto-Proxy-Stunden | 8.573,83 | 8.574,87 |

Die Differenz von acht Sitzungen ist kein Abfragefehler. Die Altanalyse entfernte komplette Gerätetage mit weniger als fünf eindeutigen Patienten. Dadurch fehlten drei reale Gerätetage: HAL2 am 01.12.2025 mit zwei Sitzungen, HAL1 am 28.12.2025 mit einer Sitzung und HAL2 am 10.01.2026 mit fünf Sitzungen. Der neue Collector zählt alle Behandlungstage in den standortweiten Summen. Die Mindestgruppengröße wird nur dort angewandt, wo veröffentlichte klinische Untergruppen geschützt werden müssen.

## Übertragbarkeit

Die Leipziger Ausführung ist vollständig verifiziert. Die alternative ARIA-18-Ressourcenauflösung für Hamburg wurde gegen die dort bereits erfolgreich ausgelesene Schema- und Aggregatstruktur geprüft. Ein echter ReportServer-Lauf in Hamburg bleibt Teil der lokalen Inbetriebnahme, weil dieser Server aus Leipzig nicht erreichbar ist.
