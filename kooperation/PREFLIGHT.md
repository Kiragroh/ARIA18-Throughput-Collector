# Alternative: nur technische Vorpruefung

`ARIA18_Technischer_Preflight_1.0.rdl` liest ausschliesslich Schema- und
Rechteinformationen. Keine klinischen Tabellenzeilen, keine Patienten-, Fall-,
Plan- oder Ereignisschluessel, keine Einzelzeitpunkte, keine Fallzahlen und
keine lokalen Freitextkataloge werden ausgegeben. Es gibt keine Pflichtparameter.

## Ausfuehren

1. RDL im ARIA-Berichtemodul importieren oder im Microsoft Report Builder oeffnen.
2. Die lokale ARIA-DWH-Datenquelle zuordnen und ausfuehren (rein lesend).
3. Als Excel exportieren. Bei Importwarnungen auch unter Sonstiges nachsehen.
4. Optional die Exceldatei als `STANDORT_TechnischerPreflight_R01.xlsx` ueber
   https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/ bereitstellen.
   Standort und dienstliche Rueckmeldeadresse koennen im Begleittext stehen.
   Fuer diesen Weg ist keine Full-Collector-Datei und kein Formular erforderlich.

## Was das Ergebnis bedeutet

- `SCHEMA_ACCESS_OK`: Die erforderlichen DWH-Spalten sind sichtbar und lesbar.
  Das ist keine Aussage ueber Datenvollstaendigkeit oder korrekte Kennzahlen.
- `CHECK_CAPABILITIES`: In Capabilities fehlende Spalten oder Rechte pruefen.
  Fehlende Sichtbarkeit kann ebenfalls zu diesem Status fuehren.
- `schema_available` und `select_allowed` trennen Sichtbarkeit und Leserechte.
  Optionale Quellen werden einzeln ausgewiesen, nicht pauschal vorausgesetzt.
- Native VARIAN-Bildgebung, Wartebereich, tatsaechliche Zeitfuellung und lokale
  Terminzuordnungen werden hier nicht geprueft. Das Blatt Scope weist dies aus.
- Die SQL-Version ist nicht die ARIA-Version. Bisheriger Pruefstand: ARIA 18.

## Danach am Zentrum auswerten

Auf Grundlage der Vorpruefung und lokaler Angaben koennen wir das vorhandene
Python-Auswerteskript an den Standort anpassen. Detaildaten und Auswertung
bleiben dann am Zentrum; erst gepruefte zusammengefasste Ergebnisse werden
nach Abstimmung geteilt. Die Vorpruefung allein ersetzt diesen Abgleich nicht.

Alternativ ist weiterhin eine gemeinsame Analyse mit dem Full Collector nach
lokaler Freigabe moeglich. Maximilian Grohmann hat keinen Zugriff auf die
Quellsysteme anderer Zentren. Eingereichte Detaildateien und daraus erzeugte
Detailkopien sollen nach Abschluss der vereinbarten Analyse geloescht werden;
der Abschluss und die Umsetzung einschliesslich Ablage-/Backup-Fristen werden
mit dem Zentrum abgestimmt. Diese Projektregel ist keine automatische Loeschfunktion.
GitHub ist nur fuer Software und Anleitung vorgesehen.
