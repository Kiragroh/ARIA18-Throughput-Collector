# Changelog

## Kooperation - 2026-09-15

- Oeffentlicher Teilnahmeleitfaden mit Preflight-Einstieg, Upload-Checkliste und Begleitbogen.
- Offline-HTML-Praesentation mit synthetischem Beispiel, Upload-Link und geprueftem QR-Code.
- Eindeutige Einreichungs-IDs, Standort-/Kontaktangaben und Revisions-/Ersatzkennzeichnung.
- Startseite auf die aktuelle Version konzentriert; Upload-Zugriff und Benachrichtigungen erklaert.
- Getrennte QR-Codes fuer Projektseite und Einreichung in der Praesentation.
- Eigenes Kooperationspaket und Browseransicht; keine Aenderung der Rechenmethodik 2.0.0-rc.1.

## 2.0.0-rc.1 - 2026-09-15

- Standalone AG-Pilot mit Standardjahr 2025 und begruendeter Periodenabweichung.
- Neuer Ereignisvertrag, optionalen schemaabhaengigen Zeitankern und expliziter
  Datenstands-/Quellenbestaetigung; keine numerische Patienten-ID-Konvention.
- Aktivitaet als Standard, Workflow/Imaging-Beam getrennt, Ersatzintervalle sichtbar.
- Patientenbesuche statt Planwechsel; vereinigte Zeitintervalle, echte Slotueberlappung,
  freie Stunden und relativer Anteil am beobachteten Tagesfenster.
- Lokale bestaetigte Aktivitaetszuordnung fuer Brachy und historische Therapiegeraete.
- Aufklaerungsketten, drei Kalendermonate Reife, weitere Beobachtung und separate Stornos.
- Offline-HTML mit gruppierten Boxplots, Gesamtmedian, Modell-/Periodenwechsel und
  vergroesserbaren Diagrammen; aggregierte CSV/JSON und inhaltsbasierter SQLite-Cache.
- Bildgebungsfeedback in Quellenpruefung und getrennte semantische Klassifikation
  aufgenommen. Direkte DICOM-RTPlan-Referenzen bleiben ein gesonderter Validierungspunkt.
- Rein lesende temporaere SSRS-Ausfuehrung, synthetische Regressionen und Browserpruefung.
- 1.x bleibt reproduzierbar; dessen alte Methodendatei gilt nur fuer den Legacy-Builder.

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
