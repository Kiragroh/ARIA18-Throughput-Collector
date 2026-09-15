# ARIA Throughput 2.0.0-rc.1

Start mit [Standort-Preflight und Formular](docs/v2/STANDORTTEST.md).

1. `dist/ARIA18_Standort_Preflight_2.0.rdl` importieren und die lokale
   gemeinsame ARIA-DWH-Datenquelle zuweisen. Als Excel ausfuehren.
2. Einmal Python-Abhaengigkeiten installieren:
   `python -m pip install -r requirements-analysis.txt`.
3. `tools/Standort_vorbereiten.cmd` starten, Preflight-Excel auswaehlen,
   Geraete/Terminarten im lokalen Formular zuordnen und Profil herunterladen.
4. Erst nach Quellenpruefung den CSV-Detailcollector ausfuehren und lokal
   auswerten. [Anleitung](docs/v2/START.md).

Standardjahr: 2025. Ersttest: Januar/Februar 2025. Manuelle Therapie, Brachy
und historische Geraete werden ueber fachlich bestaetigte Terminarten erfasst,
wenn keine technische Behandlungsevidenz vorliegt. Kalenderzeiten werden nicht
zu gemessenen Behandlungszeiten erklaert.

[Methodik](docs/v2/METHODIK.md) | [AG-Projekt](docs/v2/AG_PROJEKT.md) |
[Pruefstatus und Grenzen](docs/v2/VALIDIERUNG.md)

Pilot-/Releasekandidat, keine klinische Freigabe. Pseudonymisierte Exporte und
lokale Zuordnungsformulare bleiben am Standort. Nur gepruefte Aggregate teilen.
Das synthetische HTML-Beispiel der Release enthaelt keine klinischen Daten.
