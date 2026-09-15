# Lokale Analyse (optional)

Fuer die Teilnahme genuegen Excel und JSON aus `Durchfuehrung`.
Hier koennen Sie dieselbe Excel selbst auswerten. Die folgenden Befehle
im **Ordner Analyse** ausfuehren (getestet mit Python 3.13).

## 1. Installation

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-analysis.txt
```

Fuer diese Installation wird ein Paketindex oder ein lokal bereitgestellter
Python-Paketbestand benoetigt. Danach benoetigt die Auswertung weder Internet
noch Datenbankzugriff; auch der erzeugte HTML-Bericht funktioniert offline.

## 2. Synthetischer Probelauf

```powershell
.venv\Scripts\python.exe tools/create_demo_v2.py --output Demo.xlsx
.venv\Scripts\python.exe -m analysis.cli Demo.xlsx --profile profiles/synthetic.json --output Demo-Ergebnis
```

`Demo-Ergebnis/Standortanalyse.html` im Browser oeffnen. Alle Beispieldaten
sind kuenstlich erzeugt; keine echten Patienten oder Standortdaten.

## 3. Lokales Profil und echte Excel

```powershell
.venv\Scripts\python.exe tools/prepare_site.py "C:\GESCHUETZT\FullCollector.xlsx" --output "C:\GESCHUETZT\Standort-Setup" --open
```

Das erzeugte lokale Formular zeigt die exportierten Geraete, Terminarten
und Statuswerte. Fachlich zuordnen und das Profil als `standort.json`
herunterladen. Brachy und manuell abgeschlossene Therapien ohne technisches
R&V gesondert pruefen. Planung allein ist kein Behandlungsnachweis.
Ungeklaerte Quellen nicht als vollstaendig bestaetigen.

Die **Standortformular-JSON fuer die Rueckmeldung ist kein Analyseprofil**.
Sie beschreibt den Standort; das erzeugte Profil legt die Rechenzuordnungen
fest. [profiles/site-template.json](profiles/site-template.json) dient als Vorlage.

```powershell
.venv\Scripts\python.exe -m analysis.cli "C:\GESCHUETZT\FullCollector.xlsx" --profile "C:\GESCHUETZT\standort.json" --output "C:\GESCHUETZT\Ergebnis"
```

Ausgabe: `Standortanalyse.html`, `Kennzahlen.csv`, `aggregate.json` und
`aggregate-cache.sqlite`. Alle Modelle und Zeitaufteilungen sind vorbereitet;
Umschalten im HTML braucht keine neue Abfrage. Ein geaenderter Dateiinhalt
oder ein geaendertes Profil wird neu berechnet.

## Interpretation

[Methodik und Nenner](docs/METHODIK.md) | [AG-Projektidee](docs/AG_PROJEKT.md)

Aktivitaet ist das Standardmodell. Workflow und Imaging/Beam haben andere
Zeitanker und duerfen nicht als identische Auslastungsmasse gelesen werden.
Fehlende Intervalle sind keine nachgewiesenen Pausen. Nicht bestaetigte
Quellen, kleine Gruppen und unvollstaendige Geraetetage werden gekennzeichnet
oder unterdrueckt, nicht als Null interpretiert.

Echte Exporte nur auf geschuetztem Speicher verarbeiten. Auch die aggregierten
Ausgaben vor Weitergabe lokal pruefen. Keine klinischen Daten auf GitHub.
Pilotversion ohne klinische Freigabe; Paket rc.3, Rechenmethodik/RDL rc.2.
