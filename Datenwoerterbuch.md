# Datenwörterbuch

## Gemeinsame Felder

Jedes Datenblatt enthält `MethodVersion`, `RunId`, `SiteLabel` und `RecordType`. Damit bleiben Methode, Ausführung, Standort und Datensatztyp auch nach dem Zusammenführen mehrerer Kliniken nachvollziehbar.

## Blätter

### 00_Coverage

Dokumentiert angefragten und tatsächlich beobachteten Zeitraum, ausgewählte und aktive Geräte sowie die Verfügbarkeit wichtiger ARIA-18-Quellen. `selected_machines` ist die Benutzerauswahl; `active_machines` zählt Geräte mit mindestens einer Behandlung im Zeitraum.

### 01_SiteSummary

Standortweite Summen: Behandlungssitzungen, eindeutige Patienten, aktive Kalendertage, aktive Samstage, aktive Gerätetage und Brutto-Gerätestunden. Ein Gerätetag ist die Kombination aus Datum und Therapiegerät mit mindestens einer gültigen Behandlungssitzung.

### 02_MachineMonth

Monatliche Geräteaktivität mit Sitzungen, Patienten, Gerätetagen sowie erstem und letztem Behandlungstag. Geeignet zur Prüfung von Inbetriebnahmen, Stillständen und ungleichen Beobachtungszeiten.

### 03_DeviceDay

Eine Zeile pro Gerätetag. Enthält Sitzungen, Patienten, Erstfraktionen, Felder, erste/letzte Sitzung, Betriebsfenster, tatsächliche Sitzungsdauer, Start-zu-Start-Taktung und Lückenklassen. `net_proxy_hours` ist das Brutto-Betriebsfenster abzüglich dokumentierter Lücken von mindestens 30 Minuten; es ist eine Näherung und keine gemessene Beam-on-Zeit.

### 04_SlotSummary

Monatliche Termin-/Slotkennzahlen nach Gerät und Aktivität. `match_coverage_pct` ist der Anteil relevanter Slots, die einer Behandlungssitzung desselben Patienten, Tages und Geräts zugeordnet werden konnten. Nutzungswerte unter 50 Prozent werden als nicht belastbar gekennzeichnet.

### 05_CaseMix

Unterdrückte klinische Gruppen nach Monat und Gerät. Gruppen unter der gewählten Mindestpatientenzahl werden nicht als publizierbare Einzelgruppe ausgegeben. Enthält Technik, Fraktionierung, Diagnosegruppe und weitere verfügbare neutrale Dimensionen.

### 06_Imaging

Anzahl dokumentierter Bildaufnahmen nach Monat, Gerät und Bildgebungstyp. `capability_status` unterscheidet reale Zählung von nicht verfügbarer Quellinformation.

### 07_DataQuality

Qualitätsprotokoll mit Rohzeilen, ausgeschlossenen Bildfeldern, Brachytherapie- und Testpatientenzeilen sowie fehlenden Geräte- oder Fraktionsangaben. Dieses Blatt muss bei jedem Standort mit ausgewertet werden.

### 90_Sessions_JAHR

Optionales, jahresweise geteiltes Sitzungsdetailblatt. Enthält nur gesalzene SHA-256-Schlüssel und fachliche Messwerte wie Datum, Gerät, Fraktion, Technik, Start/Ende, Dauer und Feldzahl. Es enthält keine Original-ID und keinen Freitext.

### 91_Appointments_JAHR

Optionales, jahresweise geteiltes Termindetailblatt. Enthält pseudonymisierte Patienten-, Termin- und Matchschlüssel sowie Datum, Gerät, Slotzeiten, Aktivitätsklassifikation und zugeordnete Behandlungsdauer.

## Zentrale Definitionen

- `Behandlungssitzung`: deduplizierte externe Bestrahlung eines Patienten/Plans/Geräts/Datums/Fraktionszählers; Bildfelder, Brachytherapie und Testpatienten werden ausgeschlossen.
- `Brutto-Gerätestunden`: Zeit zwischen erster und letzter dokumentierter Sitzung eines Gerätetags.
- `Netto-Proxy-Stunden`: Brutto-Gerätestunden minus Lücken von mindestens 30 Minuten.
- `Sitzungstakt`: Abstand vom Start einer Sitzung bis zum Start der nächsten Sitzung am selben Gerätetag.
- `Tatsächliche Dauer`: dokumentiertes Ende minus Start der Sitzung.
- `Aktiver Samstag`: Samstag mit mindestens einer eingeschlossenen Behandlungssitzung.
