# ARIA Performance: Gesamtpaket 2.0.0-rc.4

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
rc.4 erweitert Klinikprofil, Planlogik und Vorjahreskohorte. Alte Exceldateien
bleiben lesbar. Fuer vollstaendige Plan-/Vorjahresauswertung und die erweiterten
Quellpruefungen den neuen RDL ausfuehren.

Pilot-/Releasekandidat, keine klinische Freigabe. Exporte sind pseudonymisiert,
nicht anonym. Nur lokal oder nach lokaler Freigabe im geschuetzten
Projektbereich verarbeiten, niemals in GitHub hochladen.
