# ARIA Throughput 2.0.0-rc.4

Pilotpaket fuer die AG Digitalisierung, Standardjahr 2025.

Neu in rc.4: Klinikprofil und Verlaeufe fuer Patienten, Fraktionen, bestrahlte
Plaene, Neueinstellungen und Behandlungsepisoden, einschliesslich bestaetigter
manueller Therapien. Neueinstellung wird aus der ersten Planbestrahlung abgeleitet.
Unvollstaendige Plaene mit mehr als sieben Tagen beobachteter Pause werden
getrennt von vollstaendig bestrahlten Plaenen ausgewiesen.

Slotabdeckung (zeitliche Ueberlappung) und Dauer/Slot-Verhaeltnis sind getrennte
Kennzahlen. Kleine Geraetegruppen unterdruecken nicht mehr die gesamte
Periodensumme; der Pool enthaelt nur auswertbare Geraete.

**Neuer Export erforderlich** fuer vollstaendige Vorjahrespopulation, Plansoll,
Quellflags und exakte Aktivitaetsbezeichnungen. Alte rc.2-Exporte bleiben lesbar,
fehlende Angaben werden jedoch nicht rekonstruiert oder als Null ausgegeben.
Die sichtbaren Reportparameter bleiben Standort und Zeitraum. Rueckmeldung:
Full-Collector-Exceldatei und JSON aus dem Offline-HTML.

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

Nachweise und noch offene Validierung: [Pruefstatus](VALIDIERUNG.md).
Veroeffentlicht wird ausschliesslich eine synthetische Demo; reale Testdaten bleiben lokal.

Grenzen: keine klinische Freigabe und noch keine bestandene Multistandortabnahme.
Objektbasierte RTPlan-/CBCT-Referenzextraktion ist noch nicht implementiert;
Imaging-Schemapruefung und separat getestete Klassifikationsregeln liegen bei.
Grosse Excel-Detailexporte koennen das Clientlimit erreichen; optionale
Spezialwerkzeuge wie Fast-CSV bleiben im Quellrepository. Fuer den Einstieg
enthalten beide Pakete denselben Full Collector.
Der 1.x-Vertrag bleibt im Quellrepository als klar gekennzeichnetes Archiv erhalten.

Start: [STANDORTTEST](STANDORTTEST.md), danach [START](START.md).
