# Mitmachen: ARIA Performance-Analyse

**Wie werden Behandlungszeiten, Terminplanung und Behandlungspfade dokumentiert,
und was laesst sich daraus verlaesslich vergleichen?** Wir suchen interessierte
strahlentherapeutische Standorte fuer einen Pilot zur Vorbereitung eines Projekts
der AG Digitalisierung. Zuerst pruefen wir Datenqualitaet und Definitionen,
danach gemeinsam die Ergebnisse. Es geht nicht um eine unbereinigte Rangliste.

**[Kurze Praesentation im Browser](https://kiragroh.github.io/ARIA18-Throughput-Collector/)**
| [Projekt und Analyseplan](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/AG_PROJEKT.md)
| [Downloadpaket](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/tag/v2.0.0-rc.1)

Zum Weitergeben oder offline Oeffnen:
[Praesentation als einzelne HTML-Datei](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.1/Kooperation_ARIA_Performance.html)
| [Teilnahmeunterlagen als ZIP](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.1/ARIA-Performance_Kooperation.zip).

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

**Noch keinen grossen Jahresbericht erzeugen.** Fuer den Einstieg reicht ein
kleiner Preflight: eine Vorabpruefung des Datenbankschemas und lokaler Konventionen.

1. **Zustaendigkeit klaeren:** Eine fachliche und eine ARIA-/Daten-Ansprechperson
   benennen; erforderliche lokale Freigaben vor dem Datenzugriff klaeren.
2. **Preflight ausfuehren:**
   [Standort-Preflight 2.0 herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.1/ARIA18_Standort_Preflight_2.0.rdl),
   in ARIA Berichte / Report Builder importieren und die lokale gemeinsame
   ARIA-DWH-Datenquelle zuweisen. Vorgabe: **Januar/Februar 2025**.
3. **Als Excel exportieren und lokal pruefen:** Der Preflight liefert Spalten,
   Geraete, Aktivitaetscodes, Statuswerte und aggregierte Ankerverfuegbarkeit.
   Er liefert keine Patientenliste. Die Inhalte trotzdem vor Weitergabe pruefen.
4. **Rueckmeldung hochladen:** Freigegebenen Preflight und den ausgefuellten
   [Begleitbogen](Begleitbogen.md) mit derselben Einreichungs-ID benennen,
   zusammen als ZIP ueber den unten verlinkten Upload abgeben.
   Bei einem Fehler genuegen Fehlercode und kurze Beschreibung ohne Patientendaten.

Fuer diesen ersten Schritt ist **keine Python-Installation am Standort noetig**.
SQL oder JSON muessen nicht bearbeitet werden. Die Zuordnung wird anschliessend
anhand des Preflights vorbereitet und mit der fachlichen Ansprechperson abgestimmt.

## Danach: lokale Auswertung

Das [Standortformular](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/STANDORTTEST.md) hilft bei der Zuordnung der
Geraete und Terminarten. Einmal Python einrichten, das Profil speichern und bei
spaeteren Laeufen wiederverwenden. Vor der Jahresauswertung werden lokale
Positiv-/Negativfaelle geprueft. Erst danach folgen der Detail-Collector und
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
| Basis | ARIA-DWH und lesender SSRS-Zugriff; ohne diesen Datenweg ist ein eigener Adapter erforderlich |
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
- **Phase:** `Preflight` oder spaeter `Auswertung`.
- **VON-BIS:** tatsaechlicher Auswertungszeitraum als `JJJJMMTT-JJJJMMTT`,
  nicht das Uploaddatum. Exportdatum und vollstaendiger Datenstand stehen im Begleitbogen.
- **R01:** erste Einreichung dieses Standorts, dieser Phase und dieses Zeitraums.
  Eine korrigierte oder ergaenzte Fassung bekommt `R02`, dann `R03` usw.

Beispiel, bitte `MUSTER-STR` durch das eigene Kuerzel ersetzen:

```text
MUSTER-STR_Preflight_20250101-20250228_R01.zip
  MUSTER-STR_Preflight_20250101-20250228_R01_Preflight.xlsx
  MUSTER-STR_Preflight_20250101-20250228_R01_Begleitbogen.md
```

Den Begleitbogen koennen Sie auch als Textdatei oder PDF beilegen. Er muss
**Einreichungs-ID, Klinik, dienstliche Rueckmeldeadresse, Exportdatum, Version und
Dateiliste** enthalten. Stimmen mehrere Personen am Standort mit, bitte dasselbe
Kuerzel verwenden und die Revisionsnummer gemeinsam abstimmen.

**Korrekturen:** Immer ein vollstaendiges neues Paket senden, im Begleitbogen
`ersetzt Einreichung: ..._R01` und den Aenderungsgrund nennen. Nicht nur einzelne
Dateien nachreichen. Bei einem unveraenderten Wiederholungsupload dieselbe ID und
denselben Dateinamen behalten, keine neue Revision vergeben. Ein anderes Jahr
oder eine andere Phase ist eine eigene Einreichung, kein Ersatz.

Dieses Schema ermoeglicht die Zuordnung und Dublettenpruefung; das Uploadportal
selbst prueft die Benennung und Doppeleinreichungen nicht automatisch.

**Zum Einstieg:** lokal gepruefter Preflight und Begleitbogen.
**Spaeter:** lokal freigegebene aggregierte HTML-, CSV- und JSON-Ergebnisse.

**Nicht hochladen:** Collector-Detaildateien, Patienten-/Fall-/Plan-IDs, Hash-
Schluessel, Patientenlisten, Namen, Geburtsdaten, Freitextnotizen, unbereinigte Logs,
Screenshots mit Patientendaten oder Zugangsdaten. Die Detail-CSVs und die
pseudonymisierten Excel-Ereignisblaetter bleiben am Standort. Das lokale Profil
und das Zuordnungsformular sind ebenfalls keine regulaeren Upload-Dateien.

Auch Aggregate sind nicht automatisch anonym. Lokale Freigabe und Pruefung
kleiner Gruppen bleiben erforderlich. Keine klinischen Dateien in GitHub-Issues
oder Pull Requests ablegen. Der Upload-Link ersetzt keine lokale Freigabe.

## Status

Pilot-/Releasekandidat **2.0.0-rc.1**. Technischer Preflight, Jahresexport und
lokale Python-Auswertung wurden an einem Pilotstandort erprobt. Eine gemeinsame
fachliche Multistandortabnahme steht noch aus. Die direkte objektbasierte
RTPlan-/CBCT-Referenzextraktion ist noch nicht implementiert; das wird nicht als
vollstaendige Imaging-Erfassung dargestellt.

[Methodik und Grenzen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/METHODIK.md) |
[Pruefstatus](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/VALIDIERUNG.md) |
[Zur Projektstartseite](https://github.com/Kiragroh/ARIA18-Throughput-Collector)
