# RDL ausfuehren und Ergebnisse bereitstellen

**[Standorttest-ZIP herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.2/ARIA-Performance_Standorttest.zip)**

Entpacken und `START_HIER.html` oeffnen. Das kleine Paket enthaelt nur eine
RDL, die Offline-Anleitung mit optionalem Formular, diese README und Pruefsummen.
Fuer den Export sind weder Python noch ein ausgefuelltes Formular erforderlich.

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
Bei Unstimmigkeiten helfen die Zusatzabfragen gemeinsam mit dem optionalen
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

Soweit vorhanden: **Full Collector XLSX mit integrierten Prueftabellen** und optional eine
kurze Rueckmeldung. Das Formular braucht kein Internet. Nur Standortkuerzel und
Auswertungszeitraum werden fuer die eindeutige Benennung benoetigt.
Exportdatum und Datenstand stehen schon in der Exceldatei
und muessen nicht nochmals eingegeben werden. Keine Datenschutz-Pflichtcheckbox.

Download als JSON oder Text; alternativ Drucken/PDF. Falls das Klinikgeraet
Downloads blockiert, genuegt eine normale Textdatei mit:
Standortkuerzel, Zeitraum, Rueckkontakt und gegebenenfalls Besonderheiten.
Das Formular ist niemals Voraussetzung fuer einen Reportlauf.

Nuetzliche optionale Angaben:
- ARIA-Version, soweit bekannt; aktuell gegen ARIA 18 geprueft.
- Geraeteanzahl, Kalender-/Ressourcenname, Betrieb von/bis (Monat/Jahr reicht),
  laengere Stillstaende, Ersatzgeraet.
- Bei Therapie ohne technisches R&V, etwa Tomotherapy oder Brachy:
  exakter Ressourcenname, Aktivitaetsname oder ActivityCode und Status nach
  Durchfuehrung, etwa `Manually Completed`. Planung, Vermessung und QA abgrenzen.

Die Dateien sind pseudonymisiert, **nicht anonym**. Lokal auswerten oder nach
lokaler Freigabe ausschliesslich ueber den geschuetzten Projektweg bereitstellen.
Die Ereignis-Hashschluessel sind zur Episodenbildung notwendig. Keine Namen,
Original-Patientenkennungen, Freitextnotizen oder Zugangsdaten hinzufuegen.
Auf GitHub gehoeren weder klinische Detaildateien noch reale Standortergebnisse.

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
[Lokale Auswertung](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/START.md)
