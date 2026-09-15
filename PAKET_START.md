# ARIA Throughput 2.0.0-rc.2

Start mit [Full Collector und Quellenpruefung](docs/v2/STANDORTTEST.md).

1. `dist/ARIA18_Throughput_Collector_2.0.rdl` importieren und die lokale
   gemeinsame ARIA-DWH-Datenquelle zuweisen. Als Excel ausfuehren.
2. Einmal Python-Abhaengigkeiten installieren:
   `python -m pip install -r requirements-analysis.txt`.
3. `tools/Standort_vorbereiten.cmd` starten, Full-Collector-Excel auswaehlen,
   Geraete/Terminarten im lokalen Formular zuordnen und Profil herunterladen.
4. Nach Quellenpruefung dieselben exportierten Daten lokal
   auswerten. [Anleitung](docs/v2/START.md).

Standardjahr: 2025. Ersttest: Januar/Februar 2025. Manuelle Therapie, Brachy
und historische Geraete werden ueber fachlich bestaetigte Terminarten erfasst,
wenn keine technische Behandlungsevidenz vorliegt. Kalenderzeiten werden nicht
zu gemessenen Behandlungszeiten erklaert.

[Methodik](docs/v2/METHODIK.md) | [AG-Projekt](docs/v2/AG_PROJEKT.md) |
[Pruefstatus und Grenzen](docs/v2/VALIDIERUNG.md)

Auswertung und Pruefabfragen gemeinsam. Nur Standort und Zeitraum pruefen;
Vorlauf/Nachbeobachtung sind automatisch, kein Begruendungs-Pflichtfeld.

Pilot-/Releasekandidat, keine klinische Freigabe. Pseudonymisierte Exporte nur
lokal oder nach lokaler Freigabe im geschuetzten Projektbereich verarbeiten.
Oeffentlich nur gepruefte Aggregate teilen.
Das synthetische HTML-Beispiel der Release enthaelt keine klinischen Daten.
