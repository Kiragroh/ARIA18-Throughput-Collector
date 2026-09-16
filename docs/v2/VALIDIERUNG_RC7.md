# Collector rc.7: Quellen und Leserechte

Arbeitsstand vom 16.09.2026. RDL-Kandidat, keine allgemeine Freigabe fuer unbekannte
Standorte. Analyseverfahren weiterhin rc.6; die Quellenpruefung im RDL wurde
erweitert, nicht die Definition klinischer Kennzahlen.

## Korrekturen

- Pflicht- und optionale Spalten werden auf Sichtbarkeit und effektive Leserechte
  des ausfuehrenden Kontos geprueft, auch bei spaltenbezogenen Berechtigungen.
- Pflichtquellen fehlen: Quellenbericht bleibt ausfuehrbar; keine leere klinische
  Auswertung als vermeintliche Null-Klinik.
- Optionale Quellen fehlen: Nur betroffene Zusatzinformationen bleiben leer.
- Abschlusshistorie fehlt: Historien-/Abschlussdiagnosen melden explizit
  `SOURCE_UNAVAILABLE` statt `AVAILABLE` mit scheinbaren Null-Nachweisen.
- Bildobjektfelder sind jetzt vollstaendig als optionale Quellen inventarisiert.
- Lokales Profilformular erklaert Schema-/Rechteprobleme und uebernimmt den
  Exportzeitraum. Vorhandene Zuordnungen koennen weiterverwendet werden;
  Quellen-/Profilbestaetigungen werden zurueckgesetzt.

## Native Kurztests

Es wurden ausschliesslich temporaere SSRS-Ausfuehrungsdefinitionen verwendet.
Keine Reportkatalogaenderung, keine Rechteaenderung, keine klinischen Schreibzugriffe.
Der ausgewaehlte Beobachtungszeitraum umfasst zwei Behandlungstage, mit bewusst
verkuerztem Vorlauf und Nachbeobachtung fuer den technischen Test.

| Szenario | Ergebnis | Excel-Render |
| --- | --- | ---: |
| Unveraenderte verfuegbare Quellen | Erfolgreich; 60 Inventareintraege inklusive Bildobjekten | 13,7 s |
| Historie und Bildobjekte fehlen | Kerndaten bleiben erhalten, Zusatzquellen explizit nicht verfuegbar | 10,2 s |
| SELECT fuer ein Pflichtfeld fehlt | Diagnosebericht erfolgreich; kein Ereignisexport, Analyse verweigert | 0,3 s |

Fuer die beiden Fehlerszenarien wurden nur Kopien der RDL-Definition angepasst:
nicht existierende Test-Objektnamen beziehungsweise ein simuliertes negatives
Berechtigungspruefergebnis. Damit wurden die generierten T-SQL-Abzweigungen und
der Excel-/Python-Weg am nativen Server ausgefuehrt. Dies ist keine Pruefung
saemtlicher realer SQL-Rollen, View-Abhaengigkeiten oder anderer ARIA-Versionen.

Der regulaere Kurzexport wurde mit dem vorherigen rc.6-Kurzexport bei gleichem
Analysecode verglichen: Patienten-/Fraktions-/Planzahlen und Patientenfluss
unveraendert; Zeitverteilungen und Nenner unveraendert. Bei einem Mittelwert
trat Gleitkomma-Rundungsrauschen von weniger als 1e-12 Minuten auf.
Im Ausfalltest blieben die Kerndatenzahlen gleich, waehrend die nicht vorhandenen
Bildobjekte und Historienanker tatsaechlich ausblieben.

Die lokale Suite bestand mit 243 Tests in 50,79 Sekunden. Sie prueft unter anderem
jedes Pflichtfeld bei fehlendem Schema, verweigertem SELECT und unbekanntem
Berechtigungsstatus. Die Guard-Ausdruecke werden dafuer mit einem synthetischen
Metadatenkatalog ausgewertet; diese Tests allein ersetzen keinen SQL-Server-Test.
Die drei nativen Exporte wurden zusaetzlich im Offline-Profilformular geprueft:
passende Fehlertexte, exportgleiche Datumsfelder, unbestaetigter JSON-Download
und Darstellung auf Desktop/Mobil. Klinische Exporte bleiben ausserhalb des Repos.

## Grenzen

Ein erfolgreicher Kurztest belegt keine vollstaendige Jahreskohorte oder
Nachbeobachtung. Eine Rechtepruefung kann defekte Views, geaenderte Berechtigungen
waehrend des Laufs, Timeouts oder andere DWH-Schemata nicht ausschliessen.
Unbekannte Standorte benoetigen weiterhin einen lokalen Probelauf und fachlichen
Abgleich. Fehlende Daten werden nicht ersetzt, keine klinische Rangliste abgeleitet.
Bestehende Releasepakete bleiben unveraendert; dieser Stand ist ausschliesslich
ein neuer Testkandidat.
