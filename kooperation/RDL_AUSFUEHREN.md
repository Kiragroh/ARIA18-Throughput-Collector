# RDL ausfuehren und den Standorttest zurueckgeben

Der Hauptreport kann bei passender Datenquelle und passendem Schema bereits
beim ersten Versuch laufen. **Preflight und Formular helfen trotzdem**: Sie
erklaeren lokale Geraete, Statuswerte und Besonderheiten, auch wenn kein Fehler
auftritt. Ein technisch erfolgreicher Export bestaetigt noch nicht alle Zahlen.

## Kleines Downloadpaket

**[Standorttest-ZIP herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.1/ARIA-Performance_Standorttest.zip)**

Das Paket enthaelt nur `START_HIER.html` mit Anleitung, ausfuellbarem Formular
und lokalem Linkgenerator, diese README, die beiden benoetigten RDLs und eine
Pruefsummenliste. ZIP entpacken und `START_HIER.html` im Browser oeffnen.
Keine Python-Installation fuer diesen Ersttest, keine alten Versionen und kein
Quellcodepaket. Die HTML-Datei fuehrt selbst kein SQL aus und laedt nichts hoch.

## Weg A: im ARIA-Modul Berichte

1. Im Modul **Berichte** die Importfunktion oeffnen und die gewuenschte `.rdl`
   auswaehlen. Nicht jede ARIA-Benutzerrolle darf Berichte importieren. Fehlt die
   Funktion oder das Recht, bitte die lokale ARIA-/Berichtsadministration ansprechen.
2. Falls erforderlich, die gemeinsame Datenquelle an die lokale **ARIA-DWH**
   binden. Der mitgelieferte Verweis ist `/VarianTemplate/Data Sources/variandw`;
   bei anderen lokalen Bezeichnungen muss er angepasst werden.
3. **Nach einer Importwarnung zuerst nachsehen:** In den bisher beobachteten
   Installationen kann der Bericht trotz Warnung bereits unter **Sonstiges**
   liegen. Dort nach dem Berichtsnamen suchen, bevor erneut importiert wird.
   Das ist installationsabhaengig, keine Garantie fuer jede Warnung. Fehler bei
   Rechten, Datenquelle oder Ausfuehrung muessen weiterhin geklaert werden.
4. Den Bericht unter Sonstiges belassen oder, mit den noetigen Rechten, in eine
   passende Berichtsgruppe verschieben. Von dort **ausfuehren**, Parameter
   kontrollieren und im Ergebnis **Exportieren > Excel (.xlsx)** waehlen.
5. Zuerst den kleinen Preflight fuer Januar/Februar 2025 ausfuehren. Den
   Hauptreport fuer 2025 koennen Sie ebenfalls direkt testen. Fuer die
   Rueckgabe bleibt **Lokale pseudonymisierte Ereignisse exportieren = Nein**.

## Weg B: Microsoft Report Builder, ohne ARIA-Import

1. Wenn installiert und berechtigt, **Microsoft Report Builder** starten und
   ueber **Oeffnen > Dieser PC / Durchsuchen** die lokale `.rdl` oeffnen.
2. Unter **Berichtsdaten > Datenquellen** die passende DWH-Datenquelle zuordnen.
   Die mitgelieferte RDL verwendet eine freigegebene Serverdatenquelle. Deshalb
   muss Report Builder den lokalen Reportserver erreichen und darauf zugreifen
   duerfen. Alternativ kann die Administration eine zulaessige eingebettete
   Verbindung einrichten; Zugangsdaten niemals in die Rueckgabe aufnehmen.
3. **Ausfuehren / Run** waehlen, Parameter setzen und gegebenenfalls
   **Bericht anzeigen / Aktualisieren** ausloesen.
4. Im ausgefuehrten Bericht **Exportieren > Excel** waehlen und lokal speichern.
   Das speichert das Ergebnis, nicht nur die RDL-Definition.

Hierfuer ist weder ein Import in ARIA noch eine dauerhafte Veroeffentlichung des
Berichts erforderlich. Datenbank-/Datenquellenrechte werden dadurch nicht umgangen.
Siehe Microsoft zu [Report-Builder-Vorschau](https://learn.microsoft.com/en-us/sql/reporting-services/report-builder/previewing-reports-in-report-builder)
und [Speichern bzw. Exportieren](https://learn.microsoft.com/en-us/sql/reporting-services/report-builder/saving-reports-report-builder).

## Weg C: nach Import direkt als Excel per URL

Das folgende Beispiel startet den **Hauptreport fuer 2025 ohne Ereignisdetails**.
Servername und Ordner sind absichtlich Platzhalter:

```text
https://REPORTSERVER.example.invalid/ReportServer?/ORDNER/ARIA18_Throughput_Collector_2.0&rs:Command=Render&rs:Format=EXCELOPENXML&PeriodStart=2025-01-01&PeriodEnd=2025-12-31&IncludePseudonymizedDetails=0&DataThroughConfirmed=0
```

Fuer den kleinen Preflight als Excel:

```text
https://REPORTSERVER.example.invalid/ReportServer?/ORDNER/ARIA18_Standort_Preflight_2.0&rs:Command=Render&rs:Format=EXCELOPENXML&PeriodStart=2025-01-01&PeriodEnd=2025-02-28&IncludePseudonymizedDetails=0&DataThroughConfirmed=0
```

- `REPORTSERVER.example.invalid` durch den lokalen Host einschliesslich des
  passenden Protokolls und gegebenenfalls Ports ersetzen. Der Beispielhost ist
  absichtlich nicht erreichbar. Keine realen Klinikhostnamen im oeffentlichen Beispiel.
- `/ReportServer` kann am Standort anders heissen. Gemeint ist der SSRS-Endpunkt,
  nicht die Verwaltungsseite `/Reports`.
- `/ORDNER/...` ist der **tatsaechliche SSRS-Katalogpfad nach dem Import**, ohne
  `.rdl` in einer normalen Native-Mode-Installation. Die ARIA-Gruppe Sonstiges ist
  nicht zwingend ein gleichnamiger SSRS-Ordner. Pfad aus dem funktionierenden
  Berichtsaufruf uebernehmen oder bei der Administration erfragen.
- `rsItemNotFound` bedeutet: Katalogpfad oder Berichtsname stimmt nicht oder der
  Bericht ist dort nicht vorhanden. Ein Import allein beweist nicht den Beispielpfad.
- Parameternamen sind exakt und gross-/kleinschreibungssensitiv. Der Hauptreport
  verwendet `PeriodStart` und `PeriodEnd`. `EXCELOPENXML` bedeutet `.xlsx`.
- Fuer die gemeinsame Rueckgabe muss `IncludePseudonymizedDetails=0` bleiben.
  `DataThroughConfirmed=0` bestaetigt keine Datenvollstaendigkeit. Den Datenstand
  im Ergebnis pruefen; der Standardwert von gestern ist keine fachliche Freigabe.

Der Linkgenerator in `START_HIER.html` kodiert Pfad und Parameter und startet
erst nach einem ausdruecklichen Klick auf den erzeugten Link. Er speichert den
Servernamen nicht im Standortformular und uebertraegt ihn nicht an das Projekt.
Die URL benoetigt einen bereits veroeffentlichten Bericht und die normalen
Zugriffsrechte. Eine lokale RDL-Datei laesst sich damit nicht ohne Import ausfuehren.
Microsoft beschreibt [URL-Export](https://learn.microsoft.com/en-us/sql/reporting-services/export-a-report-using-url-access)
und [URL-Parameter](https://learn.microsoft.com/en-us/sql/reporting-services/pass-a-report-parameter-within-a-url).

## Bitte alle drei Unterlagen hochladen, soweit verfuegbar

1. **Hauptreport als Excel ohne Ereignisdetails**, fuer 2025. Er enthaelt
   Exportmetadaten, Quellenabdeckung und Aktivitaetsinventar. Das Blatt `90_Events`
   darf hoechstens Ueberschriften, aber keine Ereigniszeilen enthalten;
   `details_included` in `00_Metadata` muss `0` bzw. `False` sein.
   Das ist ein technischer Pruefbericht, noch keine vollstaendige Durchsatzanalyse.
2. **Preflight als Excel**, normalerweise Januar/Februar 2025, auch wenn der
   Hauptreport bereits lief. Er ergaenzt Geraete-/Termin-/Statusinventare und
   die Verfuegbarkeit der Zeitanker. Inventarwerte sind keine klinischen Kennzahlen.
3. **Ausgefuelltes Standortformular als JSON**, erzeugt mit `START_HIER.html`.
   Es enthaelt zugleich den Begleitbogen: Einreichungs-ID, Kontakt, Zeitraeume,
   Exportstatus, Besonderheiten und die erwarteten Dateinamen. Die Datei muss
   nicht von Hand bearbeitet werden. Das ist nicht das spaetere technische
   `standort.json`-Zuordnungsprofil.

Falls ein Report nicht laeuft, trotzdem Formular und vorhandene Datei schicken;
Fehlercode und kurze Beschreibung ohne Einzelfalldaten angeben. Kein mehrfaches
Blind-Neustarten und keine unbereinigten Logs senden.

Alle Dateien vor Weitergabe pruefen, auch ausgeblendete Tabellenblaetter.
Keine Patienten-/Fall-/Plan-IDs oder zugehoerigen Hash-Schluessel, Notizen,
Geburtsdaten, Original-DICOM-UIDs oder Zugangsdaten hochladen. Technische
Katalogbezeichnungen auf enthaltene Personen-/Patientennamen kontrollieren.
Nur notwendige dienstliche Kontaktdaten im Formular belassen. Kleine Aggregate
brauchen eine lokale Freigabe. Der Detail-CSV-Collector und das lokale
Zuordnungsprofil bleiben fuer die spaetere Analyse am Standort.

## Eindeutige Einreichung und Rueckfragen

Ein ZIP mit derselben Einreichungs-ID in allen Dateinamen, beispielsweise:

```text
MUSTER-STR_Standorttest_20250101-20251231_R01.zip
  MUSTER-STR_Standorttest_20250101-20251231_R01_Bericht_20250101-20251231.xlsx
  MUSTER-STR_Standorttest_20250101-20251231_R01_Preflight_20250101-20250228.xlsx
  MUSTER-STR_Standorttest_20250101-20251231_R01_Standortformular.json
```

Das Formular erzeugt die Namen. Fuer Korrekturen die Revision erhoehen und
angeben, welche Einreichung ersetzt wird. Immer das vollstaendige Paket senden.
Unveraenderte Wiederholungen behalten ihre ID; der Upload dedupliziert nicht selbst.

**[Gepruefte Einreichung hochladen](https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/)**

Die Dateien sind ausschliesslich fuer **Maximilian Grohmann** freigegeben.
Er erhaelt Upload-Benachrichtigungen und kann ueber die dienstliche Kontaktadresse
Rueckfragen stellen. Andere Teilnehmende haben keinen Zugriff auf Ihre Einreichung.
Eine lokale Freigabe bleibt erforderlich. Keine klinischen Dateien auf GitHub.

Zur vollstaendigen lokalen Analyse spaeter:
[Standortprofil und Testablauf](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/STANDORTTEST.md)
und [Python-Auswertung](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/START.md).
