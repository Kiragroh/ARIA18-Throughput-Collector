# Changelog

## 1.1.0 - 2026-08-18

- Patientenanmeldung sowie Pending-/In-Progress- und Completed-Zeitpunkte aus dem ARIA-Terminworkflow ergänzt
- Ersten Imaging-Zeitpunkt, ersten Beam-Zeitpunkt und einen transparenten klinischen Start-Proxy getrennt exportiert
- Plausibilitätskennzeichen und abgeleitete Warte-/Slotzeiten im pseudonymisierten Termindetailblatt ergänzt
- Maschinenlesbares Excel-Blatt `08_Glossary` hinzugefügt
- Python-Auswertung für einen einzelnen Standort mit Excel- und HTML-Ergebnis ergänzt
- Einzelstandort-Auswertung um Anmeldung bis Laden, Laden bis klinischen Start und klinischen Start bis Terminabschluss ergänzt
- Leipziger ARIA-18-Schema und alle zwölf SQL-Datasets read-only geprüft

## 1.0.0 - 2026-08-17

- Erster portabler ARIA-18-Collector mit eingebetteten SQL-Abfragen
- Aggregierte Standort-, Monats-, Gerätetag-, Slot-, Fallmix-, Bildgebungs- und Qualitätsblätter
- Optionale jahresweise pseudonymisierte Sitzungs- und Termindetails
- Automatische Geräte- und Schemaerkennung für zwei bekannte ARIA-18-Ressourcenmodelle
- Getesteter Import und HTTP-Export über SSRS als PDF und Excel
