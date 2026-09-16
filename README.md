![ARIA18 Throughput Collector: rein lesender Export und lokale Analyse](docs/assets/banner-github.png)

# ARIA Performance-Analyse

Dieses Projekt verbindet einen rein lesenden ARIA-Export mit einer lokalen
Python-Auswertung. Es hilft strahlentherapeutischen Einrichtungen, gebuchte
Gerätezeiten, dokumentierte Behandlungsabläufe und Datenlücken nachvollziehbar
zu untersuchen. Gemeinsame Definitionen sollen anschließend belastbare
Standortvergleiche ermöglichen, keine unbereinigten Ranglisten.

## Aktueller Stand

**Paket 2.0.0-rc.9** ist der aktuelle Pilot-/Releasekandidat zur Vorbereitung
eines Projekts der AG Digitalisierung. Exporte aus zwei ARIA-18-Kliniken wurden
technisch ausgewertet und mit lokalen Kennzahlen abgeglichen. Einzelne
Zähldifferenzen werden noch geklärt; weitere Standorte helfen beim Abgleich.
Das Werkzeug dient der rückblickenden Prozessanalyse, nicht der Patientenbehandlung.

**[Gesamtpaket herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.9/ARIA-Performance_Gesamtpaket.zip)**
| [Prüfstatus](docs/v2/VALIDIERUNG.md)
| [Änderungen](CHANGELOG.md)

Zwei Ordner: **Durchfuehrung** mit RDL, Offline-Formular und Anleitung;
**Analyse** mit Python-Skript, Standortprofilen, Methodik und synthetischem Probelauf.

**[Nur Durchführung herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.9/ARIA-Performance_Durchfuehrung.zip)**:
dieselben Durchführungsdateien ohne Analyse-Skripte. Start in beiden Paketen:
`Durchfuehrung/START_HIER.html`. Für die Einreichung ist Python nicht nötig.

Enthalten: Collector **rc.8**, Analyseverfahren **rc.7**.
Paket rc.9 ergaenzt native Hersteller-/Aufnahmedaten zur ExacTrac-Erkennung,
trennt CT-Schichtobjekte und schaetzt Mindestplaene manueller Therapien.
Das optionale Sheet `93_Wartebereich` trennt Testhinweise und unplausible
Ankunftszeiten; es ist noch keine validierte Wartezeitkennzahl.
Die Analyse trennt Behandlungsdauer/Slotlaenge, positive Slotueberschneidung
und konservative Lueckenmessung von beobachteten Patientenwechseln.
Fuer Herstellerangaben und korrigierte Bildfrequenzen ist ein neuer Export
erforderlich. Bei Exporten vor rc.6 bitte ebenfalls den
neuen Collector verwenden: verlorene Ressourcen-Zuordnungen sind nicht
nachträglich in Python rekonstruierbar.

Gemeinsamer Jahreszeitraum: **1. Januar bis 31. Dezember 2025**.
Ein anderes möglichst aktuelles, vollständiges Jahr ist möglich; lokale
Besonderheiten können kurz erläutert werden. Für einen Probelauf reichen Januar/Februar 2025.

## Sie möchten mitmachen?

**Alternative ohne Detaildaten: [Nur technische Vorprüfung herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.9/ARIA-Performance_Nur_Preflight.zip).**
Diese separate RDL prüft ausschließlich DWH-Schema und Leserechte. Keine
klinischen Datensätze, Pseudonyme, individuellen Zeitpunkte oder Fallzahlen.
Die Exceldatei zeigt technische Voraussetzungen und noch offene Prüfungen,
nicht die tatsächliche Datenfüllung. [Ablauf und Grenzen](kooperation/PREFLIGHT.md).
Für diesen Einstieg ist kein Full Collector und kein Formular erforderlich.

Im **[Ordner kooperation](kooperation/README.md)** stehen die Projektidee,
der Nutzen für Ihren Standort und alle Schritte zur Teilnahme: gemeinsamer
Report, JSON-Standortformular, eindeutige Dateibenennung und Upload-Hinweise.

Die **[kurze Präsentation](https://kiragroh.github.io/ARIA18-Throughput-Collector/)**
erklärt den Einstieg und enthält QR-Codes zur Projektseite und zum Upload.
Für die erste Einreichung benötigen Sie noch keine Python-Installation.
Report-Erstellung und Excel-Export dauern derzeit jeweils etwa **drei Minuten**,
bei großen Datenbeständen oder hoher Serverlast auch länger. Bitte nicht allein
wegen dieser Wartezeit abbrechen. Bei Problemen stimmen wir die nächsten
Tests gemeinsam ab; Rückmeldungen helfen, den Report für weitere Kliniken zu verbessern.
Der **Full Collector XLSX enthält Auswertungsdaten und integrierte
Preflight-/Diagnoseabfragen**. Kein separater Preflight und kein Umschalten.
Er kann direkt funktionieren; bei Unstimmigkeiten helfen die Prüftabellen
zusammen mit dem kurzen Formular, lokale Konventionen zu klären und den
Report zu verbessern. Nur Standort und Auswertungszeitraum werden angezeigt.
**Für die Einreichung brauchen wir die Full-Collector-Exceldatei und die JSON.**
Das Formular funktioniert offline und bietet nur „JSON herunterladen“;
optionale Angaben dürfen leer bleiben. Beide Dateien gemeinsam als ZIP einreichen.
Falls bekannt, kann die Patientenzahl 2025 mit Zählweise und Quelle ergänzt werden.
Sie dient als unabhängiger Plausibilitätsabgleich, nicht als Ersatz für den Export.
**Ein lokaler Probelauf ist auch ohne Upload möglich.** Für eine gemeinsame
Auswertung wird anschließend die Weitergabe am Standort abgestimmt.
[ARIA-Import, Report Builder und anonymisiertes Excel-URL-Beispiel für 2025](kooperation/RDL_AUSFUEHREN.md).

Die über den dort verlinkten Upload eingereichten Dateien sind ausschließlich
für **Maximilian Grohmann** freigegeben. Er erhält Upload-Benachrichtigungen,
prüft die Einreichungen und kann sich über die dienstliche Kontaktadresse im
Begleitbogen bei Rückfragen melden. Andere Teilnehmende haben keinen Zugriff
auf Ihre Einreichung. Nur lokal geprüfte und freigegebene Unterlagen hochladen,
keine Namen, Original-IDs oder Freitextnotizen ergänzen.

## Einstieg am Standort

1. **Gemeinsamer Report:** Den Full Collector aus dem Ordner `Durchfuehrung`
   importieren, mit der lokalen ARIA-DWH-Datenquelle verbinden und als Excel
   exportieren. Auswertungsdaten, Schema, Geräte, Terminarten, Statuswerte,
   Abschlussdiagnostik und Versionshinweise stehen in derselben Exceldatei.
2. **Zuordnung bestätigen:** Das
   [Standortformular und den Testablauf](docs/v2/STANDORTTEST.md) verwenden.
   Auch Brachy und historische Geräte ohne technischen R&V-Nachweis berücksichtigen.
3. **Lokal auswerten:** Die Exceldatei mit der
   [Python-Auswertung](docs/v2/START.md) verarbeiten.
   Für große Datenmengen steht zusätzlich ein
   [Fast-CSV-Collector](dist/ARIA18_Throughput_Collector_Fast_2.0.rdl) bereit.
   Der interaktive HTML-Bericht funktioniert anschließend ohne Internet.

## Was die Auswertung zeigt

- Kalenderslots, dokumentierte Behandlungsintervalle und deren tatsächliche Überlappung.
- Zeitverteilungen, Patientenwechsel und freie Gerätezeit mit Messabdeckung.
- Aufklärungsepisoden, mehrfache Termine, folgende Therapie und weitere Beobachtung.
- Quellenlücken und unklare Zuordnungen, damit fehlende Daten nicht als Nullwerte erscheinen.

Aktivität ist das Standard-Zeitmodell. Workflow und Imaging/Beam werden getrennt
ausgewiesen. Kalenderdauer ersetzt keine gemessene Dauer; eine Datenlücke ist
keine nachgewiesene Pause. Für eine negative Einstufung einer Aufklärungsepisode
sind mindestens drei Kalendermonate Nachbeobachtung erforderlich. Die Suche nach
späterer Behandlung oder Wiedervorstellung endet dadurch nicht nach drei Monaten.

## Voraussetzungen und Grenzen

**Bisher gegen ARIA 18 geprüft.** Andere ARIA-Versionen sind nicht bestätigt.
`VersionInfo` nennt diesen Prüfstand und die SQL-Server-Version getrennt.
Eine nicht verlässlich auslesbare installierte ARIA-Version wird als unbekannt
gekennzeichnet und kann optional im Formular ergänzt werden.

Benötigt werden ARIA-DWH, lesender SSRS-Zugriff und eine fachlich bestätigte
Zuordnung der lokalen Geräte und Aktivitäten. Therapie ohne technisches R&V
kann über eindeutig zugeordnete abgeschlossene Therapietermine belegt werden;
technische Beam-Zeiten werden daraus nicht abgeleitet. Fehlende Quellen brauchen
eine gekennzeichnete Einschränkung oder einen eigenen Adapter.

## Welche Daten werden verwendet?

- **Rein lesend:** Der Report verändert keine ARIA-Daten. Export und Auswertung
  können zunächst vollständig am Standort erfolgen; es gibt keinen automatischen Upload.
- **Für die Detailanalyse:** Technische Zuordnungsschlüssel verbinden zusammengehörige Ereignisse, damit
  Behandlungsfolgen und Mehrfachzählungen korrekt ausgewertet werden können.
- **Transparente Einordnung:** Die Exceldatei enthält Ereigniszeitpunkte und
  verknüpfbare Behandlungsverläufe. Sie ist deshalb als pseudonymisierter
  Detaildatensatz vorgesehen, nicht als anonymes Ergebnis.
- **Gezielte Weitergabe:** Nach lokaler Freigabe erhalten nur Maximilian Grohmann
  und nicht die anderen Teilnehmenden die eingereichten Dateien. Alternativ
  können zunächst nur technische Fragen ohne klinische Dateien besprochen werden.
  Eine pauschale Datenschutzfreigabe für teilnehmende Standorte liegt nicht vor.

Für gemeinsame Ergebnisdarstellungen sind geprüfte aggregierte Kennzahlen
vorgesehen; kleine Gruppen und mögliche Rückschlüsse werden vor einer Weitergabe
geprüft. Lokale Katalogtexte ebenfalls auf versehentliche Personenangaben prüfen.
GitHub enthält Software und Anleitung, keine klinischen Einreichungen.

**Auswertung am Zentrum:** Maximilian Grohmann hat keinen Zugriff auf die
Quellsysteme anderer Zentren. Nach Klärung der Quellen und Definitionen kann das
vorhandene Auswerteskript standortspezifisch angepasst und vollständig dort
ausgeführt werden. Detaildaten bleiben dann am Zentrum; geteilt werden nur
abgestimmte, geprüfte Aggregate.

Bei einer vereinbarten zentralen Analyse werden eingereichte Detaildateien und
erzeugte Detailkopien nach Abschluss der Analyse gelöscht. Abschluss und
Umsetzung einschließlich Ablage-/Backup-Fristen werden mit dem Zentrum
abgestimmt. Das ist eine Projektregel, keine automatische Löschfunktion.

## Dokumentation

- [Projektidee und Analyseplan](docs/v2/AG_PROJEKT.md)
- [Standorttest und minimale Anpassungen](docs/v2/STANDORTTEST.md)
- [Methodik, Zähler und Nenner](docs/v2/METHODIK.md)
- [Lokale Installation und Auswertung](docs/v2/START.md)
- [Bildgebung: Quellen und noch offene Adapter](docs/v2/IMAGING.md)

Frühere Stände bleiben in der
[Versionshistorie](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases)
nachvollziehbar. Für neue Teilnahmen gilt ausschließlich der oben verlinkte Stand.
