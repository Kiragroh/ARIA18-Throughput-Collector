# Mitmachen: ARIA Performance-Analyse

**Wie werden Behandlungszeiten, Terminplanung und Behandlungspfade dokumentiert,
und was laesst sich daraus verlaesslich vergleichen?** Wir suchen interessierte
strahlentherapeutische Standorte fuer einen Pilot zur Vorbereitung eines Projekts
der AG Digitalisierung. Zuerst pruefen wir Datenqualitaet und Definitionen,
danach gemeinsam die Ergebnisse. Es geht nicht um eine unbereinigte Rangliste.

**[Kurze Praesentation im Browser](https://kiragroh.github.io/ARIA18-Throughput-Collector/)**
| [Projekt und Analyseplan](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/AG_PROJEKT.md)
| [Gesamtpaket](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.3/ARIA-Performance_Gesamtpaket.zip)

Zum Weitergeben oder offline Oeffnen:
[Praesentation als einzelne HTML-Datei](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.3/Kooperation_ARIA_Performance.html)
| [Nur Durchfuehrung als ZIP](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.3/ARIA-Performance_Durchfuehrung.zip).

## Was Ihr Standort davon hat

- Eine lokale, interaktive Auswertung mit nachvollziehbaren Zaehlern, Nennern und
  Qualitaetshinweisen, statt nur einer schwer einzuordnenden Auslastungszahl.
- Eine gemeinsame Sicht auf gebuchte und gemessene Zeiten, dokumentierte Pausen,
  wiederholte Aufklaerungen und anschliessende Behandlung oder Beobachtung.
- Ein wiederverwendbares Standortprofil. Beim ersten Durchlauf wird die Zuordnung
  gemeinsam vorbereitet; spaeter muessen vor allem neue Eintraege geprueft werden.
- Die Moeglichkeit, die Definitionen und Fragestellungen im Pilot mitzugestalten.
  Standortvergleiche folgen erst nach Quellenabgleich und lokaler Freigabe.

Eine bestimmte Einsparung, Effizienzsteigerung oder Publikation wird nicht
versprochen. Ergebnisse sind eine Grundlage fuer die lokale Prozessdiskussion,
keine klinische Entscheidungsunterstuetzung und keine Personalbewertung.

## Der kleinste erste Schritt

**[Gesamtpaket herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.3/ARIA-Performance_Gesamtpaket.zip)**:
Ordner `Durchfuehrung` mit Report, Offline-Formular und Anleitung;
Ordner `Analyse` mit optionaler Python-Auswertung und synthetischem Probelauf.
Wer nur exportieren und einreichen moechte, nimmt
**[Nur Durchfuehrung](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.3/ARIA-Performance_Durchfuehrung.zip)**.
Entpacken und `Durchfuehrung/START_HIER.html` oeffnen. Die Durchfuehrungsdateien
sind in beiden Paketen identisch.

Der Hauptreport kann bereits beim ersten Versuch laufen. **Integrierte Prueftabellen und
Formular helfen trotzdem**, lokale Besonderheiten und Datenluecken richtig
einzuordnen. Bitte die Exceldatei mit Auswertungsdaten und Prueftabellen hochladen:
**Full Collector XLSX und Standortformular-JSON werden beide benoetigt.**
Das Formular funktioniert offline: ausfuellen, JSON herunterladen und zusammen mit der Exceldatei einreichen.

1. **Zustaendigkeit klaeren:** Eine fachliche und eine ARIA-/Daten-Ansprechperson
   benennen; erforderliche lokale Freigaben vor dem Datenzugriff klaeren.
2. **RDL ausfuehren:** In ARIA im Modul **Berichte importieren** (gegebenenfalls
   durch die Administration), nach Importwarnungen auch unter **Sonstiges**
   nachsehen. Alternativ die lokale RDL in **Microsoft Report Builder oeffnen**,
   dort ohne ARIA-Import ausfuehren. Die lokale DWH-Datenquelle und Zugriffsrechte
   sind in beiden Faellen noetig. [Anleitung und Excel-URL fuer 2025](RDL_AUSFUEHREN.md).
3. **Exceldatei erzeugen:** Full Collector mit integrierten Prueftabellen fuer 2025;
   fuer den Probelauf reichen Januar/Februar. Kein Preflight-/Final-Schalter.
   Standort ersetzen; Vorlauf und Nachbeobachtung werden automatisch gesetzt.
   Full Collector XLSX enthaelt pseudonymisierte Daten fuer die Analyse.
4. **Formular und Rueckgabe:** In [START_HIER.html](START_HIER.html) das
   Standortformular einschliesslich Begleitangaben ausfuellen und als JSON
   herunterladen. Zusammen mit den lokal geprueften Exceldateien unter derselben
   Einreichungs-ID als ein ZIP hochladen. Falls ein Report scheitert, vorhandene
   Unterlagen senden und den Fehlercode ohne Patientendaten im Formular beschreiben.

Fuer diesen ersten Schritt ist **keine Python-Installation am Standort noetig**.
SQL oder JSON muessen nicht bearbeitet werden. Die Zuordnung wird anschliessend
anhand der Prueftabellen vorbereitet und mit der fachlichen Ansprechperson abgestimmt.

## Danach: lokale Auswertung

Das [Standortformular](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/STANDORTTEST.md) hilft bei der Zuordnung der
Geraete und Terminarten. Einmal Python einrichten, das Profil speichern und bei
spaeteren Laeufen wiederverwenden. Vor der Jahresauswertung werden lokale
Positiv-/Negativfaelle geprueft. Dieselben exportierten Daten nutzt danach
die lokale Python-Auswertung.

**Gemeinsames Standardjahr ist 2025.** Ein anderes moeglichst aktuelles,
vollstaendiges Jahr ist bei begruendeten Besonderheiten moeglich, beispielsweise
einem Geraetewechsel. Abweichende Jahre werden gekennzeichnet und nicht
unkommentiert mit 2025 zusammengefasst. Nicht einfach das beste Leistungsjahr waehlen.

Aufklaerungskohorten benoetigen mindestens drei Kalendermonate Nachbeobachtung
fuer eine negative Einstufung. Die Suche nach spaeterer Behandlung oder
Wiedervorstellungen endet dadurch nicht nach drei Monaten.

## Voraussetzungen und Besonderheiten

| Thema | Was gelten muss |
|---|---|
| Basis | Gegen ARIA 18 geprueft; ARIA-DWH und lesender SSRS-Zugriff. Andere Versionen sind noch nicht bestaetigt |
| Geraete | Historische Geraete und Wechsel kenntlich machen; neutrale Bezeichnungen verwenden |
| Therapie ohne technisches R&V | Eindeutig als Therapie zugeordnete, abgeschlossene/manuell abgeschlossene Termine koennen Behandlung belegen |
| Brachy | Tatsaechliche Anwendungen mitnehmen; Planung oder Vermessung allein ist keine Behandlung |
| Zeitmessung | Kalenderdauer ist keine gemessene Behandlungsdauer; fehlende Anker bleiben fehlend |
| Freie Zeit | Fehlende Behandlungsintervalle nicht als Pausen werten; Messabdeckung und vollstaendige Geraetetage mitberichten |
| Vergleich | Gleiche Definitionen, Zeitraum, Quellenumfang und vergleichbare Nachbeobachtung; lokale Freigabe vor Weitergabe |

Es ist nicht die Linac-Marke entscheidend, sondern der verfuegbare Nachweis.
Auch Nicht-Varian-Systeme koennen ueber geeignete ARIA-Termine in die klinischen
Episoden eingehen. Technische Plan-Fraktionen oder Beam-Zeiten werden daraus
nicht erfunden. [Detaillierte Voraussetzungen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/STANDORTTEST.md).

## Upload

### Wer die Einreichung erhaelt

Die ueber diesen Link eingereichten Dateien sind ausschliesslich fuer
**Maximilian Grohmann** freigegeben. Er erhaelt Upload-Benachrichtigungen und
kann die Einreichung pruefen, die naechsten Schritte vorbereiten und sich bei
Rueckfragen ueber die dienstliche Kontaktadresse im Begleitbogen melden.
Andere Teilnehmende haben keinen Zugriff auf Ihre Einreichung. Deshalb bitte
die Einreichungs-ID und eine erreichbare dienstliche Kontaktadresse angeben.

**[Freigegebene Unterlagen hochladen](https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/)**

[![QR-Code zum Upload](assets/qr-code.png)](https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/)

Bitte zuerst die [Upload-Checkliste](Upload_Checkliste.md) durchgehen.

### Eindeutig benennen, damit nichts doppelt zaehlt

Bitte **ein ZIP je Einreichung** hochladen. Dessen Name und alle enthaltenen
Dateinamen beginnen mit derselben Einreichungs-ID:

`STANDORT_Phase_VON-BIS_R01`

- **STANDORT:** dauerhaftes, unterscheidbares Kuerzel fuer Klinik und Abteilung,
  beispielsweise `MUSTER-STR`. Im Begleitbogen auch den vollen Kliniknamen angeben.
  Nur Buchstaben, Ziffern und Bindestriche verwenden; keine Patientendaten.
- **Phase:** `Standorttest` fuer den gemeinsamen Export; spaeter `Auswertung` fuer eine
  bereits gepruefte Auswertung.
- **VON-BIS:** tatsaechlicher Auswertungszeitraum als `JJJJMMTT-JJJJMMTT`,
  nicht das Uploaddatum. Exportdatum und Datenstand stehen bereits im Export.
- **R01:** erste Einreichung dieses Standorts, dieser Phase und dieses Zeitraums.
  Eine korrigierte oder ergaenzte Fassung bekommt `R02`, dann `R03` usw.

Beispiel, bitte `MUSTER-STR` durch das eigene Kuerzel ersetzen:

```text
MUSTER-STR_Standorttest_20250101-20251231_R01.zip
  MUSTER-STR_Standorttest_20250101-20251231_R01_FullCollector.xlsx
  MUSTER-STR_Standorttest_20250101-20251231_R01_Standortformular.json
```

Der Begleitbogen wird ausschliesslich im Offline-HTML als JSON erstellt.
**Einreichungs-ID, Klinik und dienstliche Rueckmeldeadresse** helfen bei Fragen.
Exportdatum und Datenstand nicht erneut eingeben. Bei mehreren Personen dasselbe
Kuerzel verwenden und die Revisionsnummer gemeinsam abstimmen.

**Korrekturen:** Immer ein vollstaendiges neues Paket senden, im Begleitbogen
`ersetzt Einreichung: ..._R01` und den Aenderungsgrund nennen. Nicht nur einzelne
Dateien nachreichen. Bei einem unveraenderten Wiederholungsupload dieselbe ID und
denselben Dateinamen behalten, keine neue Revision vergeben. Ein anderes Jahr
oder eine andere Phase ist eine eigene Einreichung, kein Ersatz.

Dieses Schema ermoeglicht die Zuordnung und Dublettenpruefung; das Uploadportal
selbst prueft die Benennung und Doppeleinreichungen nicht automatisch.

**Zum Einstieg:** Full Collector XLSX mit integrierten Prueftabellen und
Standortformular-JSON. Beide Dateien werden fuer die Auswertung benoetigt.
[Begleitbogen.md](Begleitbogen.md) erklaert die Angaben im JSON-Formular.
**Spaeter:** lokal freigegebene aggregierte HTML-, CSV- und JSON-Ergebnisse.

**Pseudonymisierte Full-Collector-Dateien:** nur lokal oder nach lokaler Freigabe
im geschuetzten Projektbereich verarbeiten. Die Hash-Schluessel sind fuer die
Episodenbildung noetig und keine Klartext-Patientenkennungen. Nicht anonym.
**Nicht beifuegen:** Original-Patienten-/Fall-/Plan-IDs, Namen, Geburtsdaten,
Freitextnotizen, unbereinigte Logs, Screenshots mit Patientendaten oder Zugangsdaten. Das technische
Zuordnungsprofil `standort.json` und das lokale `Standortprofil.html` sind nicht
mit dem zur Rueckgabe vorgesehenen Standortformular zu verwechseln und bleiben
regulaer am Standort.

Auch Aggregate sind nicht automatisch anonym. Lokale Freigabe und Pruefung
kleiner Gruppen bleiben erforderlich. Keine klinischen Dateien in GitHub-Issues
oder Pull Requests ablegen. Der Upload-Link ersetzt keine lokale Freigabe.

## Status

Pilot-/Releasekandidat **2.0.0-rc.3**. Technischer Preflight, Jahresexport und
lokale Python-Auswertung wurden an einem Pilotstandort erprobt. Eine gemeinsame
fachliche Multistandortabnahme steht noch aus. Die direkte objektbasierte
RTPlan-/CBCT-Referenzextraktion ist noch nicht implementiert; das wird nicht als
vollstaendige Imaging-Erfassung dargestellt.

[Methodik und Grenzen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/METHODIK.md) |
[Pruefstatus](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/VALIDIERUNG.md) |
[Zur Projektstartseite](https://github.com/Kiragroh/ARIA18-Throughput-Collector)
