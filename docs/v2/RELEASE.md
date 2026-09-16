# ARIA Throughput: Paket 2.0.0-rc.8

Pilotpaket fuer die AG Digitalisierung, Standardjahr 2025.

Collector rc.7 und Analyseverfahren rc.6 bleiben bytegleich gegenueber dem
rc.7-Paket. rc.8 vereinheitlicht die oeffentlichen Einstiegsseiten, Downloadlinks
und Formularbeschriftung. `release-v2.json` nennt Paket-, Collector- und
Analyseversion sowie den LF-normalisierten SHA-256 des nativ geprueften RDLs; automatische Tests
pruefen diesen Zusammenhang. Alte Pakete bleiben unveraendert nachvollziehbar.

Vorhandene rc.7-Exporte weiterverwenden; fuer dieses Paketupdate ist kein neuer
RDL-Lauf erforderlich. **Bei Exporten vor rc.6 neu exportieren**, da korrigierte
Ressourcen-Zuordnungen nicht nachtraeglich aus verlorenen Daten entstehen.
Nur der Kalenderzeitraum und das Standortkuerzel bleiben sichtbare Parameter.

Seit rc.6/rc.7: Ressourcen-Deduplizierung, getrennte klinische und technische
Behandlungsevidenz, zusaetzliche eindeutige R&V-gestuetzte Zeitanker,
quellengepruefter Standortvergleich, Schema-/SELECT-Diagnostik einschliesslich
optionaler Bildobjekte und explizite Kennzeichnung fehlender Abschlusshistorie.
Quellenabgleich, lokale Fallpruefung und vergleichbare Nachbeobachtung bleiben
Voraussetzung belastbarer klinischer Vergleiche.

Enthalten seit rc.4: Klinikprofil und Verlaeufe fuer Patienten, Fraktionen, bestrahlte
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

Excel-Ereignisblaetter werden monatsweise aufgeteilt, ohne Daten wegzulassen.
Optional vorhandene DWH-Bildobjekte werden zusaetzlich aufgenommen: CBCT,
kV/MV-2D, explizit als ExacTrac bezeichnete Objekte und unklare Typen getrennt.
Die lokale Analyse zeigt Objektfrequenzen und zugeordnete Behandlungsdauern.
Klassifikation anhand von Bildnamen ist vorlaeufig; fehlende ExacTrac-Objekte
beweisen keine fehlende Bildgebung. Ausstattung/HyperSight wird nicht aus
kurzen Aufnahmezeiten geraten. Eine fachliche Quellenpruefung bleibt erforderlich.

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
Verifizierte RTPlan-/CBCT-Akquisitionsreferenzextraktion ist noch nicht implementiert;
Imaging-Schemapruefung und separat getestete Klassifikationsregeln liegen bei.
Grosse Excel-Detailexporte koennen das Clientlimit erreichen; optionale
Spezialwerkzeuge wie Fast-CSV bleiben im Quellrepository. Fuer den Einstieg
enthalten beide Pakete denselben Full Collector.
Der 1.x-Vertrag bleibt im Quellrepository als klar gekennzeichnetes Archiv erhalten.

Start: [STANDORTTEST](STANDORTTEST.md), danach [START](START.md).
