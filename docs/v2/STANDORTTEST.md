# Standorttest und Voraussetzungen

## Ersttest ohne Python

Das [Paket Nur Durchfuehrung](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.5/ARIA-Performance_Durchfuehrung.zip)
enthaelt im Ordner `Durchfuehrung` eine RDL und START_HIER.html mit Anleitung,
Rueckmeldeformular und Direktlink-Generator. Das
[Gesamtpaket](https://github.com/Kiragroh/ARIA18-Throughput-Collector/releases/download/v2.0.0-rc.5/ARIA-Performance_Gesamtpaket.zip)
ergaenzt die optionale Python-Auswertung im Ordner `Analyse`.
Der Full Collector kann direkt laufen. Er enthaelt
Auswertungsdaten und Prueftabellen. Fuer die Einreichung werden diese Exceldatei
und die JSON aus dem kurzen Offline-Formular benoetigt. Detaildaten nur nach lokaler Freigabe im geschuetzten Projektbereich. [Ausfuehrungswege und Datenschutzgrenzen](../../kooperation/RDL_AUSFUEHREN.md).
Das kleine Standortformular ist nicht das nachfolgende technische Zuordnungsprofil.

## So wenig Anpassung wie moeglich

Es gibt nur zwei notwendige Konfigurationsorte: die gemeinsame Datenquelle des
RDL und ein lokales JSON-Standortprofil. Keine neuen lokalen SQL-Tabellen,
keine Aenderung an ARIA und keine eingetragenen Passwoerter im Quellpaket.
Das JSON wird im lokalen Formular erzeugt; es muss nicht von Hand bearbeitet werden.

## Ein Report fuer Export und Quellenpruefung

1. [ARIA18_Throughput_Collector_2.0.rdl](../../dist/ARIA18_Throughput_Collector_2.0.rdl)
   importieren, einmal die lokale DWH-Datenquelle zuweisen und als Excel ausfuehren.
   Vorgabe: 2025. Nur Standort und Zeitraum; kein Preflight-/Final-Schalter.
   Auswertungsdaten, Schema, Codes, Statuskonventionen, Geraete, Ankerverfuegbarkeit
   und mehrfache Abschlusszeitpunkte werden gemeinsam exportiert.
2. `tools/Standort_vorbereiten.cmd` starten und diese Exceldatei auswaehlen.
   Python mit den Paketen aus `requirements-analysis.txt` muss einmal installiert
   sein. Alternativ: `python tools/prepare_site.py FullCollector.xlsx --open`.
3. Im offline geoeffneten Formular Geraete, Aktivitaeten und gegebenenfalls
   abweichende Terminstatus zuordnen. Ein vorhandenes `standort.json` kann direkt
   geladen werden; bekannte Zuordnungen bleiben erhalten, neue Eintraege offen.
4. Profil herunterladen. Bei der ersten Einrichtung kann die Zuordnung anhand
   der Preflight-Datei vorbereitet werden; der Standort bestaetigt dann nur noch
   die fachliche Interpretation. Kein automatisches Raten einer Therapie aus
   einem Planungscode. Nach der ersten Fallpruefung dieselben Ereignisdaten auswerten.
   Die fachliche Bestaetigung ist spaeter ebenfalls per Checkbox im Formular
   moeglich. Der fachlich gepruefte Datenstand wird ebenfalls dort hinterlegt;
er ist kein Pflichtfeld im RDL. Er betrifft die negative Quote, nicht den Export.

Spaeter den gemeinsamen Report bei Schema-, Geraete- oder Aktivitaetsaenderungen erneut
ausfuehren; sonst dasselbe Profil verwenden. Ein Preflight prueft technische
Voraussetzungen, kann aber unzuverlaessige klinische Dokumentation nicht garantieren.
Das Formular und Preflight-Ergebnis enthalten lokale Konventionen und bleiben
geschuetzt. Zur Quellenpruefung nur den vereinbarten geschuetzten Datenweg verwenden.

| Voraussetzung | Wofuer | Wenn sie fehlt |
|---|---|---|
| ARIA 18 | Bisheriger Pruefstand | Andere Versionen brauchen einen technischen Test; VersionInfo trennt SQL- und ARIA-Version |
| ARIA-DWH mit Lesezugriff ueber SSRS | Basisexport | Ohne diesen Datenweg braucht es einen separaten Adapter; kein vorgetaeuschter leerer Bericht |
| DimPatient, DimActivityTransaction, DimActivity, DimMachine, FactTreatmentHistory | Gemeinsamer Ereignisvertrag | Fehlende Pflichtspalten werden im Metadatenlauf benannt; Detailausgabe stoppt |
| Testpatientenkennzeichen, Patienten-/Aktivitaetsschluessel, Terminzeit und Status | Ausschluss von Testdaten, Deduplizierung, Verlauf | Keine stille Ersatzheuristik nach ID oder Name |
| Mindestens eine MU-/Dosisnachweisspalte sowie Image-/Brachykennzeichen | Technische Behandlungsevidenz | Detailausgabe stoppt bei unklarem technischen Nachweis |
| Exakte Zuordnung lokaler ActivityCode-Werte | Aufklaerung, Wiedervorstellung, Therapie, Block, ignorierte Aktivitaet | Unbekannte Codes werden gemeldet; Profil bleibt unbestaetigt |
| Erkennbare Maschinenressource und neutrale Geraetelabels | Geraetebezogene Zeiten/Slots | Patientenfluss bleibt moeglich, unzugeordnete Geraetezeiten nicht |
| Bestaetigter vollstaendiger DWH-Datenstand | Reife Kohorten und negative Quote | Keine belastbare Quote ohne gefundenen Beginn |

Die Pruefblaetter listen die Pflicht-/Optionalspalten auf. Bekannte fehlende
Pflichtquellen ergeben einen diagnostischen Export ohne Ereignisdaten, kein
auswertbares Null-Ergebnis. Verbindungs- und Rechtefehler koennen den Report
trotzdem stoppen. Fehlende optionale Historien-/Zeitspalten
werden zu leeren Ankern, nicht zu einem Abbruch aller Auswertungen.

## Nicht-Varian, historische Geraete und Brachy

Die klinische Zaehllogik haengt **nicht vom Hersteller** ab:

- Technischer MU-/Dosisnachweis ist Behandlungsevidenz.
- Ohne technischen Nachweis kann ein **lokal eindeutig als Therapie zugeordneter,
  abgeschlossener oder manuell abgeschlossener Termin** Behandlungsevidenz sein.
  So koennen historische Tomotherapy, Brachy und andere Systeme erfasst werden.
- Planung, Vermessung, Vorbereitung und Imaging allein sind kein Therapiebeginn.
- Offene/stornierte Therapietermine sind kein Durchfuehrungsnachweis.
- Technischer Nachweis und Termin werden nicht als zwei Behandlungsepisoden
  addiert. Ueberlappungen und Therapiepausen bis 30 Tage werden zusammengefuehrt.
- Ohne verlaessliche Planidentitaet darf eine terminbasierte Therapie nicht als
  technische Plan-Fraktion ausgegeben werden. Episoden und Termine bleiben
  unterschiedliche Einheiten.
- Ein Termin mit Kalenderbeginn/-ende liefert **keine gemessene Behandlungsdauer**.
  Aktivitaetszeiten koennen ausgewertet werden, wenn sie dokumentiert/plausibel
  sind. Imaging/Beam und Workflow bleiben ohne technische Anker leer.
- Geraetewechsel nicht rueckwirkend umbenennen: altes und neues Geraet getrennt
  zuordnen; im Verlauf erscheinen die im Zeitraum erkannten Geraete.

Die einzige zusaetzliche Arbeit vor Ort ist damit die fachliche Bestaetigung der
relevanten Therapiecodes. Ein allgemeines Muster wie "Brachy" im Namen reicht
nicht, wenn darunter auch Planungstermine liegen.

## Test in zwei Stufen

1. Gemeinsamen Report exportieren: Datenquelle, Capabilities und ActivityCatalog pruefen.
2. Lokales Profil: reale Maschinen und exakte Aktivitaetscodes zuordnen; unklare
   Codes nicht vorschnell als `ignore` markieren. Bestaetigungsfelder vorerst false.
3. Collector mit dem voreingestellten Datenexport ausfuehren. Fuer einen kurzen
   Funktionstest Januar/Februar 2025 waehlen, fuer den Jahresvergleich ganz 2025.
   Vorlauf und Nachbeobachtung werden automatisch gesetzt. Fuer grosse Datenmengen
   Fast-RDL als CSV verwenden.
4. Python nach START.md ausfuehren. Modellwechsel und Messabdeckung pruefen.
5. Lokale Positiv-/Negativfaelle aus der AG-Prueffallmatrix abgleichen: insbesondere
   manuelle Therapie, Brachy, Mehrfachaufklaerung, Wiederkehr nach Storno und
   laufende Behandlung am Periodenende. Keine Original-IDs oder Freitexte weitergeben.
6. Danach 2025 vollstaendig, mit gleicher Profil-/Methodenversion und ausreichend
   Kontext/Nachbeobachtung. Erst nach Abgleich `confirmed`, `sources_complete`
   sowie `complete_through` im lokalen Profil bestaetigen.

Workflow darf deutlich weniger Messungen liefern als Aktivitaet. Das ist eine
Quellen-/Dokumentationsfrage, kein Grund, ein Kalenderende als echten Abschluss
zu erfinden. Freie Zeit wird nur auf vollstaendig messbaren Geraetetagen gezeigt.

## Rueckgabe und Multistandortvergleich

Fuer den ersten Abgleich: lokal freigegebene `Standortanalyse.html`,
`aggregate.json`, `Kennzahlen.csv`, Metadaten-/Capability-Ausgabe und eine kurze
Liste nicht erklaerter Abweichungen. Keine Namen, Einzelfall-IDs, Notizen oder
pseudonymisierten Detail-CSVs per Mail oder nach GitHub. Falls eine lokale
Fehleranalyse Details braucht: ausschliesslich freigegebener geschuetzter Speicher.

Mehrere Standorte koennen dieselben Aggregatfelder vergleichen. Noch nicht
behauptet ist eine bestandene Hamburg/Leipzig-Vergleichsabnahme. Vor einer
gemeinsamen Darstellung muessen gelten:

- gleiche 2.0-Methodenversion und primaer dasselbe Kalenderjahr 2025;
- gleiche Zeitmodelle, Besuchstoleranz, Plausibilitaetsgrenzen, Zeitzonenbehandlung
  und Lueckendefinition; Ausnahmen als Sensitivitaetsanalyse kennzeichnen;
- Quellenumfang inkl. manueller Therapie und Brachy vollstaendig bestaetigt;
- drei Kalendermonate Nachbeobachtung und vergleichbarer Folgehorizont. Ein
  laengerer Folgehorizont kann spaete Starts finden und die Quote aendern;
- Messabdeckung und Zahl vollstaendig messbarer Geraetetage neben Zeitmetriken;
- Zaehler/Nenner vergleichen, nicht Standortsummen mit unterschiedlich vielen
  Geraeten, Betriebstagen oder Kalendertagen gleichsetzen;
- keine gepoolten Mediane aus Standortmedianen/Quartilen rekonstruieren;
  Standortverteilungen nebeneinander, gewichtete Quoten nur aus freigegebenen
  Zaehlern und Nennern gleicher Definition;
- keine Rangleiste aus verschieden dokumentierten Quellen; erste Ergebnisse
  bleiben eine Machbarkeits-/Datenqualitaetsanalyse.
