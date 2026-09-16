# ARIA Performance: Nur Durchfuehrung 2.0.0-rc.6 (Teststand)

Start: [Durchfuehrung/START_HIER.html](Durchfuehrung/START_HIER.html).

1. Full Collector aus dem Ordner `Durchfuehrung` in ARIA Berichte importieren
   oder im Microsoft Report Builder oeffnen und als Excel exportieren.
2. Das Offline-Formular ausfuellen und die JSON herunterladen.
3. **Full-Collector-Exceldatei und Standortformular-JSON** eindeutig benennen
   und gemeinsam als ZIP ueber den geschuetzten Upload im Formular einreichen.

Die [Anleitung](Durchfuehrung/README.md) erklaert Datenquelle, Import und Export.
Kein Python und kein separater Preflight erforderlich. Standardjahr 2025,
bislang gegen ARIA 18 getestet. Alte Exceldateien bleiben lesbar; die korrigierte
Ressourcenaufloesung patientenloser Pausenslots erfordert einen neuen Export.

Dieses Paket enthaelt dieselben Durchfuehrungsdateien wie das
[Gesamtpaket derselben Version](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases),
aber keine Python-Auswertung. Exporte sind pseudonymisiert, nicht anonym:
nur nach lokaler Freigabe im geschuetzten Projektbereich teilen, niemals auf
GitHub. Keine klinische Freigabe der Software.
