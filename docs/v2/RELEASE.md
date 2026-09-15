# ARIA Throughput 2.0.0-rc.2

Pilotpaket fuer die AG Digitalisierung, Standardjahr 2025.

- Ein Full Collector fuer Auswertung und Quellenpruefung, ohne Preflight-/Final-Schalter.
- Nur Standort und Zeitraum sichtbar; 2025 vorgegeben, Kontext automatisch.
- Integriertes Quellen-, Geraete-, Aktivitaets- und Statusinventar,
  Abschlussdiagnostik und Versionshinweise (bisher ARIA 18 getestet).
- Mehrere Abschluss-Historieneintraege verwerfen den ersten passenden Endanker
  nicht mehr; Kandidatenzahl bleibt zur Pruefung erhalten.
- Vier-Dateien-Testpaket mit optionalem Offline-Formular, Text-/PDF-Alternative.
- Lokales Offline-Formular fuer wiederverwendbare Standortprofile, ohne SQL-/JSON-Bearbeitung.
- Bewachter RDL-Ereignisvertrag, schneller CSV-Detailweg und lokale Python-Auswertung.
- Deduplizierte Aufklaerungen, alle bestaetigten Therapieformen, 30-Tage-Episoden
  und drei Kalendermonate Nachbeobachtung ohne kuenstliches Ende der weiteren Suche.
- Aktivitaet als Standard, getrennte Workflow-/technische Zeitmodelle, gewichtete
  Slotabdeckung, Intervallvereinigung und fehlende Messungen nicht als freie Zeit.
- Offline-Boxplots, Gesamtmedian, Modell-/Periodenwechsel, vergroesserte Diagramme
  und inhalts-/profilgebundener Aggregatcache.
- AG-Projektskizze, Voraussetzungen, Standorteinrichtung und Vergleichskriterien.

Nachweise: 70 Tests, Browserpruefung, kombinierter Excel-Kurzlauf via SSRS
und lokale Python-Auswertung zweier vorhandener Jahreslieferungen. Historischer
CSV-Jahreslauf 2025 vorhanden; fachlicher Quellenabgleich noch offen. Veroeffentlicht
wird ausschliesslich eine synthetische Demo; reale Testdaten bleiben lokal.

Grenzen: keine klinische Freigabe und noch keine bestandene Multistandortabnahme.
Objektbasierte RTPlan-/CBCT-Referenzextraktion ist noch nicht implementiert;
Imaging-Schemapruefung und separat getestete Klassifikationsregeln liegen bei.
Grosse Excel-Detailexporte koennen das Clientlimit erreichen; Fast-CSV ist optional
im Vollpaket. Fuer den Einstieg reicht eine Full-Collector-XLSX.
Der 1.x-Vertrag bleibt im Quellrepository als klar gekennzeichnetes Archiv erhalten.

Start: [STANDORTTEST](STANDORTTEST.md), danach [START](START.md).
