# ARIA Performance: Gesamtpaket 2.0.0-rc.8 (Teststand)

## Durchfuehrung

Mit [Durchfuehrung/START_HIER.html](Durchfuehrung/START_HIER.html) beginnen.
Der Ordner enthaelt den gemeinsamen Full Collector, das Offline-Formular
und die Anleitung fuer ARIA oder Microsoft Report Builder.

Fuer die Teilnahme brauchen wir **die Full-Collector-Exceldatei und die
Standortformular-JSON**. Beide eindeutig benennen und gemeinsam als ZIP ueber
den geschuetzten Upload im Formular einreichen. Kein Python erforderlich.

## Analyse (optional)

[Analyse/README.md](Analyse/README.md) erklaert Installation, Standortzuordnung
und lokale Python-Auswertung. Skript, Vorlagen und ein Generator fuer rein
synthetische Beispieldaten sind enthalten. Keine klinischen Beispieldaten.
Das Rueckmeldeformular ist kein fertiges Analyseprofil: Geraete, Terminarten
und Statuswerte muessen fuer die Auswertung fachlich zugeordnet werden.

## Stand und Grenzen

Standardjahr 2025; bislang gegen ARIA 18 getestet. Auswertungsdaten und
Prueftabellen stehen in derselben Exceldatei, kein separater Preflight noetig.
Enthalten sind Collector rc.7 und Analyseverfahren rc.6. Paket rc.8 korrigiert
nur Teilnahmeunterlagen, Versionsangaben und Downloadlinks. Ein vorhandener
rc.7-Export muss nicht erneut erstellt werden. Bei Exporten vor rc.6 dagegen
neu exportieren: verlorene Geraetezuordnungen lassen sich nicht rekonstruieren.
[release-v2.json](release-v2.json) dokumentiert die einzelnen Versionsstaende.

Pilot-/Releasekandidat, keine klinische Freigabe. Exporte sind pseudonymisiert,
nicht anonym. Nur lokal oder nach lokaler Freigabe im geschuetzten
Projektbereich verarbeiten, niemals in GitHub hochladen.
