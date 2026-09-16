# Standortvergleich aus lokalen Aggregaten

Noch nicht veroeffentlichter Pilot. Keine klinische oder statistische Freigabe.
Fuer die Teilnahme bleiben nur Full-Collector-Excel und Standortformular-JSON
erforderlich. Diese zusaetzliche Auswertung richtet sich an die lokale Analyse
und die spaetere Zusammenstellung mehrerer Standorte.

## Probelauf ohne klinische Daten

Im Ordner `Analyse` des Gesamtpakets, nach Installation der Anforderungen:

```powershell
.venv\Scripts\python.exe tools/create_comparison_demo.py --output Vergleich-Demo
```

`Vergleich-Demo/Vergleich/Standortvergleich.html` zeigt sechs kuenstliche
Standorte mit Monats-, Quartals- und Jahresansichten. Die Zahlen sind frei
erfunden und ausdruecklich als synthetisch gekennzeichnet. Der Bericht und
alle Diagramme funktionieren offline.

## Vorhandene Standorte vergleichen

Jeden echten Export zuerst mit seinem lokal geprueften Standortprofil
auswerten. Danach die entstandenen Aggregate einlesen:

```powershell
.venv\Scripts\python.exe -m analysis.compare --site "A=C:\GESCHUETZT\A\aggregate.json" --site "B=C:\GESCHUETZT\B\aggregate.json" --output "C:\GESCHUETZT\Vergleich"
```

`--site` kann fuer weitere Standorte wiederholt werden (2 bis 12).
Fuer unterschiedliche Lieferungen unterschiedliche neutrale Standortaliase
verwenden. Identische Dateien, Export-Fingerprints oder Exportlaeufe werden
als Dubletten abgelehnt. Revisionen eines Standorts ersetzen dessen vorherige
Datei in der Auswahl; sie zaehlen nicht als weiterer Standort.

Ausgaben:

- `Standortvergleich.html`: getrennte Standortwerte, gruppierte Boxplots,
  Zeitmodelle, Patienten-/Fraktions-/Planverlaeufe und Bildobjektfrequenzen.
- `Vergleich.json`: explizit ausgewaehlte Aggregate und Vergleichspruefungen.
- `Standorte.csv`: Gesamtzahlen je Standort und Bereich.
- `Perioden.csv`: Durchsatzkennzahlen mit exakten Nennern je Zeitraum/Modell.

Originale Geraete- und Ausstattungsnamen werden nicht uebernommen; fuer
Bildobjekte bleiben neutrale Geraete und Ausstattungsepochen getrennt.
Freitexte, Ursprungsdateinamen und Patientenkennungen werden nicht weitergereicht.
Auch Aggregate koennen sensibel sein und bleiben bis zur gesonderten Freigabe
auf geschuetztem Speicher. Die Schwellwertunterdrueckung allein macht sie
nicht automatisch anonym oder fuer eine Veroeffentlichung geeignet.

## Was vor einem fachlichen Vergleich gelten muss

- Gleicher Beobachtungszeitraum, Exportvertrag und Rechenstand.
- Gleiche relevante Recheneinstellungen und Bibliotheksversionen.
- Dokumentierte Datenfelder und Quellenverfuegbarkeit. Das Verfahren prueft
  konservativ: Auch optionale Unterschiede koennen einen Pruefpunkt ausloesen.
- Lokal bestaetigte Terminarten, Therapiegeraete, Statuswerte, Quellenumfang
  und Datenstand. Insbesondere manuelle Therapie ohne technisches R&V ist
  fachlich zu pruefen; Planung oder offene Termine allein belegen sie nicht.
- Fuer Patientenfluss zusaetzlich gleicher dokumentierter Vorlauf und
  Nachbeobachtungsstand; Bildobjekte benoetigen ihre direkte Datenquelle.
- Fuer einzelne Abschnitte: vorhandener Pool, exakte Nenner, kein
  unvollstaendiger Abschnitt und keine durch Unterdrueckung fehlenden Geraete.

Nach dieser lokalen Pruefung kann `--reviewed A --reviewed B` zusaetzlich
angegeben werden. Das bestaetigt nur die manuelle Pruefung: Fehlende Metadaten,
abweichende Zeitraeume oder unbestaetigte Quellen bleiben Pruefpunkte.
Es ist weder eine klinische Freigabe noch ein Schalter zum Verbergen von Warnungen.

Aeltere Aggregate bleiben lesbar, aber ohne nachgewiesenen Rechenstand nur
deskriptiv. Herkunftsangaben nicht manuell erfinden: Mit der aktuellen Analyse
aus dem vorhandenen Export neu berechnen. Ein erneuter RDL-Lauf ist dafuer
nicht notwendig, sofern der Export die benoetigten Daten bereits enthaelt.

## Was die Zahlen nicht bedeuten

Patienten werden weder ueber Zeitabschnitte noch ueber Standorte addiert.
Standortmediane werden nicht gemittelt; es gibt keinen gemeinsamen Median,
keine Rangliste und keine Signifikanztests. Gewichtete Slotabdeckung verwendet
die echte Ueberlappung geteilt durch die zugehoerigen gebuchten Minuten.
Behandlungsdauer geteilt durch Slotdauer ist eine andere Kennzahl.

Fehlende Werte bleiben leer, nicht Null. Freie Zeit setzt vollstaendige
Intervalle des beobachteten Geraetetages voraus. Bildobjekte sind nicht ohne
weitere Pruefung Aufnahmevorgaenge; Exposition ist nicht die gesamte
Bildgebungszeit. Unterschiede koennen durch Fallmix, Fraktionierung,
Organisation, Hardware, Zuordnungen oder Datenluecken entstehen.

Fuer eine Publikation bleiben ein abgestimmtes Analyseprotokoll, lokale
fachliche Abnahme, Datenfreigabe und eine gesonderte statistische Planung
erforderlich. Synthetische und echte Standorte werden nie als methodisch
vergleichbar freigegeben.
