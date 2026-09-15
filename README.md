# ARIA Performance-Analyse

Dieses Projekt verbindet einen rein lesenden ARIA-Export mit einer lokalen
Python-Auswertung. Es hilft strahlentherapeutischen Einrichtungen, gebuchte
Gerätezeiten, dokumentierte Behandlungsabläufe und Datenlücken nachvollziehbar
zu untersuchen. Gemeinsame Definitionen sollen anschließend belastbare
Standortvergleiche ermöglichen, keine unbereinigten Ranglisten.

## Aktueller Stand

**Version 2.0.0-rc.1** ist der aktuelle Pilot-/Releasekandidat zur Vorbereitung
eines Projekts der AG Digitalisierung. Technische Tests an einem Pilotstandort
sind erfolgt; eine gemeinsame fachliche Multistandortabnahme steht noch aus.
Die Software ist nicht klinisch freigegeben.

**[Aktuelles Paket herunterladen](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/tag/v2.0.0-rc.1)**
| [Prüfstatus](docs/v2/VALIDIERUNG.md)
| [Änderungen](CHANGELOG.md)

**Für den ersten Standorttest: [kleines ZIP mit nur fünf Dateien](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.1/ARIA-Performance_Standorttest.zip).**
Zwei RDLs, `START_HIER.html` mit Anleitung und Formular, README und Prüfsummen.

Gemeinsamer Jahreszeitraum: **1. Januar bis 31. Dezember 2025**.
Ein anderes möglichst aktuelles, vollständiges Jahr ist mit dokumentierter
Begründung möglich. Für den ersten technischen Test reichen Januar/Februar 2025.

## Sie möchten mitmachen?

Im **[Ordner kooperation](kooperation/README.md)** stehen die Projektidee,
der Nutzen für Ihren Standort und alle Schritte zur Teilnahme: kleiner
Preflight, Begleitbogen, eindeutige Dateibenennung und Upload-Checkliste.

Die **[kurze Präsentation](https://kiragroh.github.io/ARIA18-Throughput-Collector/)**
erklärt den Einstieg und enthält QR-Codes zur Projektseite und zum Upload.
Für die erste Einreichung benötigen Sie noch keine Python-Installation.
Der Report kann bereits direkt funktionieren; Preflight und Formular helfen
trotzdem bei der Einordnung. Gerne alle drei Unterlagen zurückgeben: Hauptreport
als Excel **ohne Ereignisdetails**, Preflight und ausgefülltes Standortformular.
[ARIA-Import, Report Builder und anonymisiertes Excel-URL-Beispiel für 2025](kooperation/RDL_AUSFUEHREN.md).

Die über den dort verlinkten Upload eingereichten Dateien sind ausschließlich
für **Maximilian Grohmann** freigegeben. Er erhält Upload-Benachrichtigungen,
prüft die Einreichungen und kann sich über die dienstliche Kontaktadresse im
Begleitbogen bei Rückfragen melden. Andere Teilnehmende haben keinen Zugriff
auf Ihre Einreichung. Nur lokal geprüfte und freigegebene Unterlagen hochladen,
keine Patientendetails.

## Einstieg am Standort

1. **Preflight:** Den
   [Standort-Preflight](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.1/ARIA18_Standort_Preflight_2.0.rdl)
   importieren, mit der lokalen ARIA-DWH-Datenquelle verbinden und als Excel
   exportieren. Damit werden Schema, Geräte, Terminarten und Statuswerte geprüft.
2. **Zuordnung bestätigen:** Das
   [Standortformular und den Testablauf](docs/v2/STANDORTTEST.md) verwenden.
   Auch Brachy und historische Geräte ohne technischen R&V-Nachweis berücksichtigen.
3. **Lokal auswerten:** Nach der fachlichen Prüfung mit dem
   [CSV-Collector für Jahresdaten](dist/ARIA18_Throughput_Collector_Fast_2.0.rdl)
   exportieren und die [Python-Auswertung](docs/v2/START.md) ausführen.
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

Benötigt werden ARIA-DWH, lesender SSRS-Zugriff und eine fachlich bestätigte
Zuordnung der lokalen Geräte und Aktivitäten. Therapie ohne technisches R&V
kann über eindeutig zugeordnete abgeschlossene Therapietermine belegt werden;
technische Beam-Zeiten werden daraus nicht abgeleitet. Fehlende Quellen brauchen
eine gekennzeichnete Einschränkung oder einen eigenen Adapter.

Die Abfragen verändern keine ARIA-Daten. Detaildateien und lokale Profile bleiben
am Standort. Nur freigegebene Aggregate und der geprüfte Preflight werden über
den vorgesehenen Weg geteilt; auch Aggregate sind nicht automatisch anonym.
Keine klinischen Dateien in GitHub-Issues oder Pull Requests einstellen.
Das Projekt dient Analyse und Forschung, nicht der Behandlung einzelner Patienten.

## Dokumentation

- [Projektidee und Analyseplan](docs/v2/AG_PROJEKT.md)
- [Standorttest und minimale Anpassungen](docs/v2/STANDORTTEST.md)
- [Methodik, Zähler und Nenner](docs/v2/METHODIK.md)
- [Lokale Installation und Auswertung](docs/v2/START.md)
- [Bildgebung: Quellen und noch offene Adapter](docs/v2/IMAGING.md)

Frühere Stände bleiben in der
[Versionshistorie](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases)
nachvollziehbar. Für neue Teilnahmen gilt ausschließlich der oben verlinkte Stand.
