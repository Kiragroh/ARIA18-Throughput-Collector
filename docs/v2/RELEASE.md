# ARIA Throughput 2.0.0-rc.3

Pilotpaket fuer die AG Digitalisierung, Standardjahr 2025.

Neu in rc.3: Rueckmeldung nur als JSON aus dem Offline-HTML. Fuer die Einreichung
werden die Full-Collector-Exceldatei und diese JSON benoetigt.
RDL und Rechenmethodik bleiben auf dem geprueften rc.2-Stand: Bereits erzeugte
rc.2-Exceldateien weiterverwenden, kein erneuter Export fuer das Formularupdate.

- Ein Full Collector fuer Auswertung und Quellenpruefung, ohne Preflight-/Final-Schalter.
- Nur Standort und Zeitraum sichtbar; 2025 vorgegeben, Kontext automatisch.
- Integriertes Quellen-, Geraete-, Aktivitaets- und Statusinventar,
  Abschlussdiagnostik und Versionshinweise (bisher ARIA 18 getestet).
- Mehrere Abschluss-Historieneintraege verwerfen den ersten passenden Endanker
  nicht mehr; Kandidatenzahl bleibt zur Pruefung erhalten.
- Gesamtpaket mit Ordnern Durchfuehrung und Analyse; zweites ZIP nur fuer Durchfuehrung.
- In beiden Paketen identischer RDL und Offline-Formular mit ausschliesslichem JSON-Export.
- Lokales Offline-Formular fuer wiederverwendbare Standortprofile, ohne SQL-/JSON-Bearbeitung.
- Bewachter RDL-Ereignisvertrag, schneller CSV-Detailweg und lokale Python-Auswertung.
- Deduplizierte Aufklaerungen, alle bestaetigten Therapieformen, 30-Tage-Episoden
  und drei Kalendermonate Nachbeobachtung ohne kuenstliches Ende der weiteren Suche.
- Aktivitaet als Standard, getrennte Workflow-/technische Zeitmodelle, gewichtete
  Slotabdeckung, Intervallvereinigung und fehlende Messungen nicht als freie Zeit.
- Offline-Boxplots, Gesamtmedian, Modell-/Periodenwechsel, vergroesserte Diagramme
  und inhalts-/profilgebundener Aggregatcache.
- AG-Projektskizze, Voraussetzungen, Standorteinrichtung und Vergleichskriterien.

Nachweise: 74 Tests inklusive Auswertung aus dem entpackten Paket, Browserpruefung, kombinierter Excel-Kurzlauf via SSRS
und lokale Python-Auswertung zweier vorhandener Jahreslieferungen. Historischer
CSV-Jahreslauf 2025 vorhanden; fachlicher Quellenabgleich noch offen. Veroeffentlicht
wird ausschliesslich eine synthetische Demo; reale Testdaten bleiben lokal.

Grenzen: keine klinische Freigabe und noch keine bestandene Multistandortabnahme.
Objektbasierte RTPlan-/CBCT-Referenzextraktion ist noch nicht implementiert;
Imaging-Schemapruefung und separat getestete Klassifikationsregeln liegen bei.
Grosse Excel-Detailexporte koennen das Clientlimit erreichen; optionale
Spezialwerkzeuge wie Fast-CSV bleiben im Quellrepository. Fuer den Einstieg
enthalten beide Pakete denselben Full Collector.
Der 1.x-Vertrag bleibt im Quellrepository als klar gekennzeichnetes Archiv erhalten.

Start: [STANDORTTEST](STANDORTTEST.md), danach [START](START.md).
