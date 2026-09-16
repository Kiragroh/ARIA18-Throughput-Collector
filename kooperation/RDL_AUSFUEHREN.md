# RDL ausfuehren und Ergebnisse bereitstellen

**[Gesamtpaket](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.10/ARIA-Performance_Gesamtpaket.zip)** |
**[Nur Durchfuehrung](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.10/ARIA-Performance_Durchfuehrung.zip)**

Entpacken und `Durchfuehrung/START_HIER.html` oeffnen. Beide Pakete enthalten
dieselben Durchfuehrungsdateien: RDL, Offline-Anleitung mit JSON-Formular und
Upload-Hinweise. Das Gesamtpaket ergaenzt den Ordner `Analyse` fuer Python.
Fuer den Export sind weder Python noch ein ausgefuelltes Formular erforderlich.

**Bitte Wartezeit einplanen:** Erstellung des Reports und Excel-Export dauern
derzeit jeweils etwa **drei Minuten**, je nach Datenmenge und Serverlast auch
laenger. Das ist kein fester Timeout und keine Laufzeitgarantie. Nicht allein
wegen dieser Wartezeit mehrfach starten. Fuer Fehler und Rueckfragen genuegen
der Fehlercode ohne Patientendaten, vorhandene Excel-Prueftabellen und das JSON.

Paket rc.9 enthaelt Collector rc.8 mit einer nativen Bildhersteller-Zusatzquelle.
Fuer Hersteller-/ExacTrac-Erkennung bitte neu exportieren. Zusaetzlich zur
gemeinsamen DWH-Datenquelle wird `/VarianTemplate/Data Sources/VARIAN` benoetigt.
Falls diese lokal anders heisst, muss sie beim Import passend zugeordnet werden.
Fehlende Tabellen-/Spaltenrechte werden als nicht verfuegbare Zusatzquelle
ausgewiesen. Alte Exporte bleiben analysierbar, enthalten aber keine nachtraeglich
rekonstruierbaren Herstellerangaben.

## Die Einstellungen

- **Standort / Klinik:** `Ändere mich` beispielsweise durch `UKE-STR` ersetzen.
  Der Export wird bei einem leeren Standort nicht blockiert.
- **Auswertung von / bis:** standardmaessig 01.01.2025 bis 31.12.2025.

Auswertungsdaten und technische Prueftabellen sind immer enthalten.
Kein Preflight-/Final-Schalter und keine weitere sichtbare Checkbox.

Keine zusaetzliche Begruendung und keine Vollstaendigkeitsbestaetigung im RDL.
Vorlauf (ein Jahr vor Beginn), Nachbeobachtung (bis gestern) und vorgemerkte
Folgetermine (bis zwoelf Monate danach) werden automatisch bestimmt.
Der Terminartenkatalog wird vollstaendig gelesen, unabhaengig vom Zeitraum.
Vorlauf und Nachbeobachtung werden nicht als zusaetzliche Jahresfaelle gezaehlt.

Der **Full Collector** ist Auswertung und Preflight in einem Report.
Bei Unstimmigkeiten helfen die Zusatzabfragen gemeinsam mit dem kurzen
Formular bei der Ergebnisanalyse und gezielten Korrektur.
Ein Probelauf fuer Januar/Februar ist moeglich, danach fuer den Vergleich
das vollstaendige Jahr exportieren.
Bei bereits importierten alten RDLs die Definition auf dem Server ersetzen.

**Gegen ARIA 18 geprueft**, andere Versionen sind nicht bestaetigt.
`VersionInfo` trennt den ARIA-Pruefstand von der tatsaechlichen SQL-Version.
Die installierte ARIA-Version wird nicht geraten, wenn das DWH sie nicht
zuverlaessig bereitstellt; dann kann sie optional im Formular ergaenzt werden.
Capabilities, ActivityCatalog, AppointmentInventory, MachineInventory,
HistoryStatusInventory und CompletionDiagnostics helfen beim Quellenabgleich.
Fehlende Pflichtquellen fuehren zu leeren Ereignisdaten mit Diagnosehinweis,
nicht zu auswertbaren Nullzahlen. Rechte- oder Verbindungsfehler koennen einen
Export trotzdem verhindern.

## A. Im ARIA-Modul Berichte

1. Unter **Berichte > Importieren** die RDL auswaehlen. Fehlen Rechte, die lokale
   ARIA-/Berichtsadministration ansprechen.
2. Die gemeinsame Datenquelle an die lokale **ARIA-DWH** binden.
   Mitgelieferter Verweis: `/VarianTemplate/Data Sources/variandw`.
3. Nach einer Importwarnung zuerst unter **Sonstiges** suchen. Je nach Installation
   kann der Report trotz Warnung bereits angelegt sein. Nicht blind mehrfach
   importieren. Rechte-/Datenquellenfehler muessen weiterhin geklaert werden.
4. Dort belassen oder in eine passende Gruppe verschieben. Ausfuehren und
   **Exportieren > Excel** waehlen.

## B. Microsoft Report Builder, ohne Import

Die lokale RDL in **Report Builder > Oeffnen / Durchsuchen** oeffnen.
Unter **Berichtsdaten > Datenquellen** die lokale DWH-Datenquelle zuordnen,
dann **Ausfuehren / Run > Exportieren > Excel**.
Eine dauerhafte Veroeffentlichung oder ein ARIA-Import ist dafuer nicht noetig;
die normalen Datenquellenrechte bleiben erforderlich.
[Microsoft: Report-Builder-Vorschau](https://learn.microsoft.com/en-us/sql/reporting-services/report-builder/previewing-reports-in-report-builder).

Fuer grosse Jahresdaten ist der Fast-CSV-Collector im vollstaendigen Analysepaket
meist geeigneter als der aufwendigere Excel-Renderer. Gleiche Ereignisabfrage;
die Python-Auswertung akzeptiert beide Formate.

## C. Excel-Direktlink nach Import

Full Collector fuer die Auswertung 2025, mit Auswertungsdaten:

```text
https://REPORTSERVER.example.invalid/ReportServer?/ORDNER/ARIA18_Throughput_Collector_2.0&rs:Command=Render&rs:Format=EXCELOPENXML&PeriodStart=2025-01-01&PeriodEnd=2025-12-31&SiteLabel=AENDERE-MICH
```

Host, Port, Standort und Katalogpfad ersetzen. Gemeint ist der SSRS-Endpunkt
`/ReportServer`, nicht die Verwaltungsseite `/Reports`.
Der ARIA-Ordner Sonstiges entspricht nicht zwingend dem SSRS-Katalogpfad.
Bei `rsItemNotFound` den Pfad aus einem funktionierenden Aufruf uebernehmen.
Eine lokale RDL-Datei allein reicht fuer den URL-Aufruf nicht.
[Microsoft: URL-Export](https://learn.microsoft.com/en-us/sql/reporting-services/export-a-report-using-url-access).

Der Offline-Linkgenerator in `START_HIER.html` hilft beim Kodieren. Nur der
Klick auf den erzeugten Link ruft Ihren Server auf. Serveradresse und Pfad
werden nicht im Rueckmeldeformular gespeichert.

## Rueckgabe und Offline-Formular

Fuer die Auswertung werden **Full Collector XLSX mit integrierten Prueftabellen**
und **Standortformular-JSON** benoetigt. Das Formular braucht kein Internet. Standortkuerzel und
Auswertungszeitraum werden fuer die eindeutige Benennung benoetigt.
Exportdatum und Datenstand stehen schon in der Exceldatei
und muessen nicht nochmals eingegeben werden. Keine Datenschutz-Pflichtcheckbox.

In `START_HIER.html` ausfuellen und **JSON herunterladen** waehlen.
JSON und Excel gemeinsam als ZIP einreichen, nicht das HTML selbst.
Der Report laeuft unabhaengig vom Formular; fuer die Einreichung werden beide
Dateien gebraucht. Keine PDF-/Text-Alternative und keine erneute Pflichtbestaetigung.

Nuetzliche optionale Angaben:
- ARIA-Version, soweit bekannt; aktuell gegen ARIA 18 geprueft.
- Geraeteanzahl, Kalender-/Ressourcenname, Betrieb von/bis (Monat/Jahr reicht),
  laengere Stillstaende, Ersatzgeraet.
- Bei Therapie ohne technisches R&V, etwa Tomotherapy oder Brachy:
  exakter Ressourcenname, Aktivitaetsname oder ActivityCode und Status nach
  Durchfuehrung, etwa `Manually Completed`. Planung, Vermessung und QA abgrenzen.

Ein lokaler Probelauf ist ohne Upload moeglich. Der Report liest ARIA-Daten,
veraendert sie nicht und uebertraegt keine Dateien automatisch. Technische
Hash-Schluessel verbinden zusammengehoerige Ereignisse statt direkter
Patientenkennungen. Zeitpunkte und Verlaeufe bleiben enthalten: Die Exceldatei
ist pseudonymisiert, **nicht anonym**. Fuer die gemeinsame Auswertung die
Weitergabe am Standort abstimmen und den geschuetzten Projektupload verwenden.
Keine Namen, Original-Patientenkennungen, Freitextnotizen oder Zugangsdaten
hinzufuegen; Katalogtexte auf solche Inhalte pruefen. GitHub enthaelt Software
und Anleitung, keine klinischen Einreichungen.

## Eindeutige Benennung

```text
MUSTER-STR_Standorttest_20250101-20251231_R01.zip
  MUSTER-STR_Standorttest_20250101-20251231_R01_FullCollector.xlsx
  MUSTER-STR_Standorttest_20250101-20251231_R01_Standortformular.json
```

Fehlende Dateien einfach weglassen. Bei Korrekturen Revision erhoehen und
moeglichst die ersetzte ID nennen; unveraenderte Wiederholungen behalten ihre ID.

**[Geschuetzte Einreichung hochladen](https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/)**

Die Einreichung ist ausschliesslich fuer **Maximilian Grohmann** freigegeben.
Er erhaelt Upload-Benachrichtigungen und kann bei Rueckfragen reagieren.
Andere Teilnehmende haben keinen Zugriff. Lokale Freigaben bleiben erforderlich.

Die fachliche Quellenpruefung erfolgt bei der Auswertung: Ein vollstaendiger
Datenstand ist nur fuer die belastbare Quote ohne spaeteren Behandlungsbeginn
erforderlich, nicht fuer den Export oder alle anderen berechenbaren Kennzahlen.

Falls der Bericht `EVENTS_UNAVAILABLE_CHECK_CAPABILITIES` meldet, ist das keine
Null-Patienten-Auswertung. Bitte die erzeugte Excel mit dem Begleit-JSON
einreichen. Im Blatt `01_Capabilities` steht, welche Pflichtquelle fehlt; neuere
Collector-Versionen unterscheiden dabei sichtbare Spalten und SELECT-Leserechte.
Fehlende optionale Historien- oder Bildquellen sind separat markiert und muessen
nicht den gesamten Export verhindern. Keine Datenbankrechte selbst aendern;
bei Bedarf mit der lokalen ARIA-Administration klaeren.

[Lokale Auswertung](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/START.md)
