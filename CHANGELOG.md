# Changelog

## Noch nicht veroeffentlicht

- Getrennter Definitionsabgleich fuer operative Behandlungspfade: dokumentierte
  und nur aus Behandlungsbeginn abgeleitete Anwesenheit, letzter statt erster
  Aufklaerungstermin sowie Kursintervalle gegen belegte Behandlungstage.
  Die vorab definierte Studienkohorte bleibt unveraendert.
- Ausschlussgruende des lokalen Profils als Ereigniszeilen fuer Auswahl und
  Gesamtkontext sichtbar; fehlende Quellflags werden nicht als geprueft behandelt.
- Bildgebungsquellenhinweis folgt dem tatsaechlichen Export statt eines alten
  festen Texts ohne direkte Bildobjekte. Keine Aenderung der RDL-Datei erforderlich.

## 2.0.0-rc.5 - 2026-09-16

- Optionaler Plausibilitaetsabgleich im Offline-Formular: bekannte Patientenzahl
  2025, Zaehleinheit, Quelle und Umfang. Unbekannt bleibt leer, nicht Null.
- Beim Laden aelterer JSON-Dateien werden fehlende Formularfelder zurueckgesetzt;
  keine uebernommenen Angaben eines zuvor geoeffneten Standorts.
- Projektbanner im GitHub-README; beide Downloadpakete enthalten dasselbe Formular.
- Nur Teilnahmeunterlagen/Paket aktualisiert. RDL und Rechenlogik bleiben rc.4;
  bereits erzeugte rc.4-Exceldateien weiterverwenden, kein erneuter RDL-Import noetig.

## 2.0.0-rc.4 - 2026-09-16

- Getrennte Slotueberlappung und Behandlungsdauer/Slotdauer, Workflow-Endanker korrigiert.
- Q1-/Periodenpool bleibt fuer auswertbare Geraete sichtbar; kleine Gruppen sind nicht im Pool.
- Fehlende/mehrdeutige Therapietermingeräte werden nur anhand eindeutiger tatsaechlicher R&V-Behandlung zugeordnet.
- Klinikprofil mit Patienten, technischen Fraktionen, manuellen Therapien, bestrahlten Plaenen und Plan-Neueinstellungen.
- Plansoll und erster/letzter Behandlungstag im Export; mehr als sieben beobachtete Tage Pause beenden unvollstaendige Plaene analytisch.
- Getrennte Plan-/30-Tage-Episodenlogik; keine erfundenen Planreferenzen fuer manuelle Therapien.
- Vollstaendige Vorjahreskohorte, Quellenflags und Aktivitaetsbezeichnungen im neuen RDL.
- Populations-/Episodenverlaeufe, Vorjahreslegenden, belegtes Tagesfenster und vergroesserbare Diagramme.
- Bisherige Exporte bleiben lesbar, fehlende Vorjahres-/Planinformationen werden kenntlich gemacht.
- Monatliche Excel-Ereignisblaetter statt sehr grosser Jahresblaetter; vollstaendiger Datenumfang erhalten.
- Optionale DWH-Bildobjekte, getrennte Typen und Zuordnung zu eindeutigen Tagesbesuchen.
- Bildobjektfrequenzen und Behandlungszeiten deskriptiv; datierte Geraeteausstattung statt Geschwindigkeitsvermutung.

## 2.0.0-rc.3 - 2026-09-15

- Rueckmeldung im Offline-HTML ausschliesslich als JSON; Text-/PDF-Export entfernt.
- Einreichung klar auf zwei Dateien begrenzt: Full-Collector-XLSX und Standortformular-JSON.
- Keine zusaetzliche Dateibestaetigung; optionale Kontextfelder bleiben optional.
- Zwei klare Downloads: Gesamtpaket mit Durchfuehrung/Analyse und kleineres Paket nur Durchfuehrung. Identische Durchfuehrungsdateien, keine klinischen Beispieldaten.
- Report und Rechenmethodik unveraendert zu rc.2. Vorhandene rc.2-Exporte bleiben verwendbar; kein erneuter Reportlauf nur fuer dieses Formularupdate erforderlich.

## 2.0.0-rc.2 - 2026-09-15

- Ein Full Collector fuer Auswertung und Preflight: neun Datensaetze einschliesslich Quellen-, Status-, Geraete-, Abschluss- und Versionsdiagnostik; Ereignisblaetter jahresweise.
- RDL zeigt nur Standort und Auswertung von/bis. Standortvorgabe: Aendere mich. Kein Preflight-/Final-Schalter.
- Auswertungsdaten automatisch aktiv; Standalone-Preflight und Fast-CSV bleiben optionale Werkzeuge im Vollpaket.
- Mehrere Abschluss-Historieneintraege verwerfen nicht mehr pauschal den Endanker: erster passender Abschluss im begrenzten Terminfenster, Kandidatenzahl bleibt sichtbar.
- Bekannte fehlende Pflichtquellen liefern einen diagnostischen Export ohne Ereignisdaten; Python wertet dies nicht als Nullmenge.
- ARIA-18-Pruefstand getrennt von SQL-Version und nicht erkannter installierter ARIA-Version ausgewiesen.
- Vorlauf, Nachbeobachtung und Begruendungsmetadaten automatisch; Terminartenkatalog bleibt vollstaendig.
- Vollstaendigkeitspruefung fuer negative Aufklaerungsquoten im lokalen Profil mit Datum statt im RDL-Dialog.
- Full Collector pseudonymisiert, nicht anonym: lokal oder mit lokaler Freigabe im geschuetzten Projektbereich, niemals auf GitHub.
- Vier-Dateien-Testpaket und vereinfachtes Offline-Formular: keine Pflicht-Datenschutzcheckbox, keine doppelte Eingabe von Exportdaten; JSON, Text oder PDF.
- Direkte SSRS-Links setzen nur bearbeitbare Standort-/Zeitraumparameter; interne Parameter werden nicht mehr uebergeben.

## Kooperation - 2026-09-15

- Minimales Standorttest-ZIP mit zwei RDLs, Offline-Formular, Anleitung und Pruefsummen.
- ARIA-Import/Sonstiges, Report-Builder-Vorschau ohne Import und anonymisierter Excel-Direktlink fuer 2025 dokumentiert.
- Drei Rueckgabedateien unterschieden: Hauptreport ohne Ereignisdetails, Preflight und ausgefuelltes Standortformular.
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
