# ARIA Performance: Nur Durchfuehrung 2.0.0-rc.9 (Teststand)

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

Enthalten ist Collector rc.8. Fuer Hersteller-/ExacTrac-Erkennung bitte neu
exportieren. Die gemeinsame Quelle VARIAN muss neben variandw zugeordnet sein;
Details stehen in Durchfuehrung/RDL_AUSFUEHREN.md.
[release-v2.json](release-v2.json) nennt die enthaltenen Versionsstaende.

Dieses Paket enthaelt dieselben Durchfuehrungsdateien wie das
[Gesamtpaket derselben Version](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.9/ARIA-Performance_Gesamtpaket.zip),
aber keine Python-Auswertung. Exporte sind pseudonymisiert, nicht anonym:
nur nach lokaler Freigabe im geschuetzten Projektbereich teilen, niemals auf
GitHub. Keine klinische Freigabe der Software.
