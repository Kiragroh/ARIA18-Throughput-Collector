# rc.6: Ressourcen und Fraktionsnachweise

Arbeitsstand vom 16.09.2026, noch keine klinische Freigabe oder neue
veroeffentlichte Paketversion.

## Gepruefte Korrekturen

- Patientenkontakte mit mehreren Ressourcen bleiben ein Termin.
- Patientenlose Reservierungen verschiedener Geraete zur selben Uhrzeit werden
  vor der Geraeteaufloesung nicht zusammengefasst.
- Geloeschte/stornierte Ressourcen erzeugen keine kuenstliche Mehrdeutigkeit;
  zwei tatsaechlich zugeordnete Geraete bleiben ausdruecklich mehrdeutig.
- Hauptabfrage und Terminarteninventar verwenden dieselben SQL-CTEs. Das
  Inventar enthaelt nun auch patientenlose Reservierungen.
- Ein externer Termin ohne Geraetezuordnung ist bei vorhandenem technischem
  externem Tagesnachweis kein Beleg fuer eine weitere Fraktion. Er bleibt
  als Prueffall erhalten. Andere Modalitaeten werden nicht dadurch entfernt.
- Kleine Werte des neuen Qualitaetszaehlers bleiben unterdrueckt.

## Testumfang

Die Ressourcen-CTEs werden mit synthetischen Tabellen ausgefuehrt, nicht nur
als Text durchsucht. Dabei werden lediglich T-SQL-Temp-Tabellennamen und
Unicode-Literalpraefixe fuer die lokale SQLite-Testumgebung angepasst.
Diese Fixtures ersetzen keinen SQL-Server-Test.

Zusaetzlich wurde der vollstaendige RDL an einem ARIA-18-Standort als temporaere
SSRS-Definition mit zwei ausgewaehlten Behandlungstagen ausgefuehrt. Excel-Render:
13,4 Sekunden im abschliessenden Lauf, erfolgreich. Der Reportkatalog und klinische Daten wurden nicht
veraendert; nur lesende Abfragen mit temporaeren SQL-Arbeitstabellen.
Einlesen und lokale Analyse des Kurzexports: rund 10 Sekunden.

Der Kurzexport enthielt patientenlose, eindeutig zugeordnete Geraetetermine,
aber keinen parallelen Termin gleicher Art/Uhrzeit auf mehreren Geraeten.
Der spezifische Parallelfall ist deshalb bislang synthetisch geprueft, nicht
an diesem Live-Zeitfenster nachgewiesen.

Eine bereits vorliegende zweite Standortdatei wurde lokal neu ausgewertet.
Die gezielte Populationspruefung lief in 23,5 Sekunden; die anschliessende
vollstaendige Neuberechnung aus dem lokalen Ereigniscache dauerte rund 270
Sekunden. Sie benoetigte keine neue SQL-Abfrage. Die lokale Quellenpruefung
ist nicht mit einer bestaetigten Vollstaendigkeit der Klinikdaten gleichzusetzen.

Der native Test verwendete einen ausdruecklich verkuerzten Kontext, damit kein
Jahreslauf noetig ist. Er belegt Syntax, Export und Verarbeitung, nicht eine
vollstaendige Jahreskohorte oder ausreichende Nachbeobachtung.

Abschliessende lokale Testsuite: 135 Tests bestanden in 48,26 Sekunden;
entpacktes Paket einschliesslich Analyse- und Vergleichs-CLI geprueft.

## Grenzen und erneuter Export

Die Fraktionskorrektur kann auf vorhandenen Exporten angewandt werden.
Bereits verlorene Ressourceninformationen alter RDLs lassen sich hingegen
nicht nachtraeglich erfinden; dafuer wird ein neuer Export benoetigt.
Nicht zugeordnete Aktivitaeten, manuelle Modalitaeten und Pausentypen bleiben
Bestandteil der lokalen fachlichen Profilpruefung.
