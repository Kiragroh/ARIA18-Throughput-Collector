# Pruefstatus 2.0.0-rc.4

## Erweiterte Analyse rc.4

- **Noch nicht veroeffentlicht:** Der kombinierte Excel-Export erreichte in zwei
  temporaeren Tests das 900-s-Clientlimit, auch mit festen Detailzeilenhoehen.
  Die Freigabe des Downloadpakets bleibt deshalb offen. SQL-Verarbeitung und
  Excel-Rendering wurden nicht getrennt gemessen; der erfolgreiche Fast-CSV-Lauf
  allein ist kein Nachweis fuer den kombinierten Excel-Weg.
- 90 automatisierte Tests bestanden, einschliesslich Auswertung aus dem
  entpackten Gesamtpaket und Ausschluss klinischer Daten aus beiden ZIPs.
- Beide lokalen Standortanalysen: 17 von 17 Diagrammen befuellt; Desktop/Mobil,
  Hell/Dunkel, Box-/Linienansicht, Monatsauswahl und Popup geprueft.
- Wiederholte lokale Auswertung aus dem SQLite-Cache geprueft.
- Neuer Fast-CSV-RDL gegen ARIA 18 als temporaere Ausfuehrungsdefinition getestet,
  ohne Aenderung am SSRS-Katalog. Januar/Februar 2025: 153,2 s; Jahr 2025:
  226,2 s. Umfang einschliesslich vollstaendiger Vorjahrespopulation und Nachbeobachtung.
- Ruecklesepruefung: neue Quellenflags, Plansoll und erster Behandlungstag sind
  im technischen Export vorhanden; kein Export direkter Patientenkennungen.
- Zusaetzliche Regressionen: sieben vs. mehr als sieben Tage Nachbeobachtung,
  spaetere Planfortsetzung, links abgeschnittene Planbeginne, manuelle Brachy/
  historische Therapie, mehrdeutige Ressourcen, Q1-Pool und Slotdefinitionen.
- Vorhandene Altlieferung bleibt auswertbar; fehlende Plansoll-/Vorjahresdaten
  werden nicht als vollstaendig rekonstruiert. Ein neuer Export ist hier erforderlich.
- Fachliche Gleichwertigkeit der Datenquellen ist weiterhin nicht bestaetigt.
  Insbesondere Terminklassifikation, manuelle Therapien und Testpatientenregeln
  bleiben Bestandteil der standortbezogenen Abnahme.

## Historisch: Formular und Pakete rc.3

- 74 automatisierte Tests bestanden, einschliesslich synthetischer Analyse
  direkt aus einem entpackten Paket ausserhalb des Quellrepositories.
- Beide ZIPs enthalten bytegleiche Durchfuehrungsdateien; Pruefsummen und
  relative Dokumentationslinks getestet. Keine klinischen Daten beigepackt.
- Rueckmeldung ausschliesslich JSON; Offline-Browserpruefung fuer Download,
  Import, kleine Bildschirme und Pflicht zur gemeinsamen Einreichung mit Excel.
- Praesentation: 21 Ansichten, keine horizontalen Ueberlaeufe, sieben Druckseiten.
- Ergebnisbericht: Box-/Linienplots, Modelle, Perioden, Hell/Dunkel und
  Vergroesserung mit synthetischen und geschuetzten lokalen Daten geprueft.
- RDL unveraendert und SHA256-identisch zu rc.2. Rechenmethodik unveraendert.
  Kein erneuter Export wegen des Formular- oder Paketupdates erforderlich.

## Historisch: Kombinierter Report rc.2

- 70 automatisierte Tests: Kernmethodik, Parameter, integrierte Diagnoseabfragen,
  Quellenwaechter, wiederholte Abschlusszeitpunkte und minimales Downloadpaket.
- Kombinierte RDL am Pilotstandort temporaer geladen, ohne Aenderung des
  SSRS-Katalogs: 02.-03.01.2025 mit automatischem Vorlauf/Nachbeobachtung,
  Excel erfolgreich in 19,8 s, 8.089.119 Bytes. Definition und Export gehasht.
- Excel zurueckgelesen: Quellen-/Status-/Geraeteinventare, Abschlussdiagnostik,
  VersionInfo und 45.039 Ereigniszeilen, davon 1.146 im kurzen Auswertungsfenster.
  Kontextjahre sind fuer Episoden/Folgetermine, keine zusaetzlichen Jahresfaelle.
- Derselbe kombinierte Export im lokalen Zuordnungsformular eingelesen.
- Negativtest mit absichtlich nicht vorhandenen Pflichtquellen in einer
  temporaeren Testdefinition: Diagnose-Excel erfolgreich, collection_state
  kennzeichnet fehlende Ereignisdaten; der Python-Import lehnt die Auswertung ab.
- Fast-CSV-Kurzlauf mit korrigierter Abschlussauswahl ebenfalls technisch
  erfolgreich; kein isolierter Performancevergleich verschiedener Perioden.
- Offline-Teilnahmeformular: nur Standortkuerzel ergaenzt, JSON/Text/PDF,
  Import/Wiederaufnahme und Direktlink ohne interne SSRS-Parameter getestet.
- Praesentation in 21 Desktop-/Mobilansichten, Offline-Bilder, Navigation und Druck getestet.
- Zwei vorhandene Standortlieferungen fuer 2025 lokal mit derselben Methodik
  ausgewertet. Ergebnisse und Arbeitsprofile bleiben geschuetzt, nicht in Git.
  Alte Exporte mit verworfenen Abschlussankern brauchen einen neuen Reportlauf.

Die installierte ARIA-Version konnte nicht verlaesslich aus dem DWH abgeleitet
werden. VersionInfo weist dies aus und verwechselt die auslesbare SQL-Version
nicht mit ARIA. Gegen ARIA 18 getestet, keine Zusage fuer andere Versionen.
Keine fachliche Multistandortabnahme und kein neuer vollstaendiger Jahreslauf
mit genau dieser kombinierten Exceldefinition behauptet.

## Historische Nachweise rc.1

## Lokal nachgewiesen

- Bestehende 1.x-Vertragstests plus neue Regressionen fuer den 2.0-Vertrag.
- Synthetischer RDL-kompatibler Excel-Export und Python-Ende-zu-Ende-Bericht.
- Inhalts-/Profil-basierter Cache: zweiter identischer Lauf ist ein Cache-Treffer.
- Browser: Desktop und Mobil, Hell/Dunkel, gruppierte Boxen, Medianlinien,
  Modellwechsel, Monats-/Quartalsauswahl und vergroesserter Dialog.
- UKL-Reportserver: temporaeres Laden und Rendern des 2.0-RDL ohne
  Katalogpublikation. Metadatenlauf erfolgreich, erster Detail-/Kontextlauf
  Januar/Februar 2025 erfolgreich (490,8 s, rund 73 MB).
- Operatives ARIA-Imaging-Schema per rein lesendem Metadaten-RDL geprueft.
- Flacher CSV-Export Januar/Februar 2025: 35,6 s; Wiederholung der finalen
  Definition 36,3 s, rund 30 MB. Kurzer technischer Test ohne klinische Randabnahme.
- CSV-Jahreslauf 2025 mit Kontext ab 2024 und Datenstand 14.09.2026:
  203,3 s, rund 153 MB. Lokale Python-Auswertung auf diesen Daten erfolgreich.
- Kleiner Standort-Preflight Januar/Februar 2025: 10,9 s, rund 66 KB;
  Excel-Inventar anschliessend im lokalen Formular eingelesen.
- CSV-Millisekundenabweichungen durch gemischte ISO-Praezision als Parserfehler
  erkannt und mit Regression korrigiert. Zeitanker nicht pauschal als fehlend gewertet.
- Fehlende Besuchsintervalle werden nicht als freie Zeit interpretiert:
  Luecken/Takt nur auf vollstaendig messbaren Geraetetagen, mit Nennerausweisung.
- 54 automatisierte Tests erfolgreich. Formular im Browser auf Desktop/Mobil
  geprueft: Filter, Geraete-/Aktivitaetszuordnung und unbestaetigter Profildownload.

Weitere grosse Excel-Renderlaeufe erreichten das 900-s-Clientlimit. Darum ist
CSV der empfohlene Detailweg; Excel bleibt fuer den kleinen Preflight geeignet.
Die Zeiten stammen aus unterschiedlichen Export-/Kontextvarianten und begruenden
keinen isoliert gemessenen Beschleunigungsfaktor. SQL-Laufzeit und Excel-Rendering
wurden nicht getrennt profiliert. Messungen sind standort-/lastabhaengig.

`tools/test_collector_v2.ps1` legt ab dem finalen CSV-Test Definition, SHA-256,
Export-SHA, Parameter und Laufzeit im geschuetzten Testordner ab. Reale Exporte
und Standorteinzelfaelle sind nicht Bestandteil dieses Repositorys. Das lokale
Jahresprofil bleibt absichtlich unbestaetigt; dies ist keine klinische Abnahme.

## Nicht behauptet

- Keine formale klinische Freigabe; keine vollstaendige Multistandortvalidierung.
- Keine verifizierte DICOM-RTPlan-Referenz-Extraktion fuer direkte CBCT-Klassifikation.
- Keine Aussage, dass fehlende Behandlungs-/Bildgebungsnachweise echte Ausfaelle sind.
- Keine bestaetigten offiziellen Standort-Jahreszahlen aus einer anderen Stelle.
- Keine automatische Anonymitaetsgarantie durch den Kleingruppenschwellenwert.

## Vor Standortfreigabe

1. Pflichtquellen und optionale Anker im Capability-Blatt pruefen.
2. Alle lokalen Therapie-, Aufklaerungs-, Wiedervorstellungs- und Blockcodes zuordnen.
3. Brachy, manuell beendete historische Therapie und Geraetetausch explizit abgleichen.
4. Prueffallmatrix aus [AG_PROJEKT](AG_PROJEKT.md) bearbeiten.
5. Datumsspanne, Beobachtungsstand und erforderlichen Kontext bestaetigen.
6. Zaehler/Nenner und Abweichungen zu lokalen Referenzzahlen nachvollziehen.
7. Freigegebene Aggregate getrennt von lokalen pseudonymisierten Exporten ablegen.
