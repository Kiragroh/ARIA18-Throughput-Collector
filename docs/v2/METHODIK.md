# Methodik 2.0

## Einheiten und Nenner

| Kennzahl | Zaehler | Nenner / Interpretation |
|---|---|---|
| Technische Plan-Fraktion | Dosis-/MU-Nachweis je Person, Plan, Geraet, Tag, Fraktion | Keine Patienten- oder Kurszahl |
| Besuch | Verbund technischer Plan-Intervalle derselben Person/Geraet/Tag innerhalb der Besuchstoleranz | Toleranz standardmaessig 5 Minuten; Sensitivitaet 0/5/10 |
| Terminmatch | Eindeutig 1:1 zugeordnete Besuche | Relevante nicht stornierte Therapieslots; unzugeordnete Slots bleiben erhalten |
| Messabdeckung | Slots mit plausiblem Intervall im gewaehlten Modell | Alle relevanten Slots; niedrige Abdeckung nicht als gute Effizienz auslegen |
| Slotabdeckung | Summe tatsaechlicher Ueberlappung mit zugeordnetem Kalenderslot | Summe genau dieser gebuchten Dauern; gewichtet, 0 bis 100 Prozent |
| Gebucht | Tatsächlich im Kalender stehende Endzeit minus Beginn | Kein nachtraeglich angenommener Standardtermin |
| Freie Stunden | Summe positiver Luecken der Intervallvereinigung | Beobachtetes Geraetetagesfenster zwischen erstem Beginn und letztem Ende |
| Freier Anteil | Freie Stunden | Stunden dieses beobachteten Fensters, nicht nominelle Verfuegbarkeit |
| Takt | Beginn bis naechster Beginn eines anderen Patienten | Innerhalb desselben Geraetetags, nie ueber Nacht |
| Wechsel | Bisher spaetestes Ende bis naechster Beginn | Negative Differenzen sind Ueberlappung, als Wechsel Null |
| Behandlungsepisode | Ueberlappende Behandlungsintervalle mit maximal 30 Tagen Pause | Alle bestaetigten Modalitaeten derselben Person zusammen |
| Aufklaerungsepisode | Kette abgeschlossener Aufklaerungen vor einem folgenden Beginn bzw. ohne folgenden Beginn | Erster abgeschlossener Termin bestimmt die Kohorte |
| Ungeklaert ohne Beginn | Reife Aufklaerungsepisoden ohne Behandlung und ohne weitere Beobachtung | Alle reifen Episoden, auch die mit Behandlung; kein No-show-Nachweis |
| Stornoquote | Eindeutige stornierte/abgebrochene Aufklaerungstermine | Alle eindeutigen registrierten Aufklaerungstermine im Zeitraum, Status separat |

Die begonnenen Behandlungsepisoden im Kalenderjahr sind **nicht** der Nenner der
Aufklaerungsquote. Einige beginnen nach einer Aufklaerung aus dem Vorjahr oder ohne
in der Quelle auffindbare Aufklaerung. Umgekehrt beginnt die Behandlung einer
Aufklaerungskohorte eventuell erst im Folgejahr.

## Zeitmodelle

- **Aktivitaet (Standard):** dokumentierter Aktivitaetsbeginn bis dokumentiertes Ende.
  Fehlende einzelne Anker koennen durch zugeordnete technische Anker ersetzt
  werden. Anzahl dieser Ersatzintervalle bleibt separat sichtbar.
- **Workflow:** erstes plausibles Imaging vor Beam, sonst erster Beam, bis
  dokumentiertem Abschluss. Fehlender Abschluss wird nicht durch die Slotzeit ersetzt.
- **Imaging/Beam:** derselbe Beginn bis letztes technisches Ende. Ein
  Behandlungsrecord-Zeitstempel ohne technischen Beginn ist nur Behandlungsevidenz,
  keine gemessene technische Dauer.

Nur gleichentags positive Intervalle bis zur konfigurierten Plausibilitaetsgrenze
(standardmaessig 240 Minuten) fliessen in Zeitkennzahlen ein. Ausschluesse werden
gezaehlt. Das ist eine technische Pruefgrenze, keine Aussage ueber medizinisch
zulaessige Behandlungsdauer. Lange dokumentierte Intervalle lokal pruefen.
Zeitstempel werden in der im Standortprofil angegebenen Zeitzone interpretiert.
Mehrdeutige oder nicht existierende Uhrzeiten bei Zeitumstellung werden nicht
als gemessene Anker verwendet.

Alle positiven Luecken sind Standard. Die Alternative **strikt >30 Minuten**
zaehlt die gesamte Laenge solcher Luecken. Genau 30 Minuten werden separat
ausgewiesen. Dokumentierte Blockslots werden mit freien Intervallen geschnitten:
freie Zeit innerhalb und ausserhalb dokumentierter Blocks ist in der CSV enthalten.
Eine solche Luecke ist nicht automatisch organisatorisch vermeidbar.

Luecken, Takt und Wechsel setzen einen vollstaendig messbaren Geraetetag voraus:
alle relevanten Termine plus nicht zugeordnete technische Besuche benoetigen ein
plausibles Intervall des gewaehlten Modells. Sonst bleibt die Tagesbelegung
unbekannt; die fehlende Behandlung wird nicht als Pause gezaehlt. Vollstaendige
und ausgeschlossene Geraetetage sowie Messabdeckung bleiben sichtbar. Die
auswertbare Teilmenge kann selektiv sein und wird nicht auf ein Jahr hochgerechnet.
Auch vollstaendige exportierte Intervalle beweisen nicht die Vollstaendigkeit
aller klinischen Quellen. Diese muss der Standort gesondert bestaetigen.

Optionale Oeffnungsstunden gelten nur bei lokaler Bestaetigung, je **beobachtetem
aktiven Geraetetag**. Tage ohne Behandlung fehlen in diesem Nenner. Daraus darf
keine Jahresverfuegbarkeit oder ungeplante technische Ausfallzeit abgeleitet werden.

## Deduplizierung und Grenzen

Identische Quellzeilen und gleiche Termine mit mehrfachen Ressourcen werden
zusammengefuehrt. Natuerlicher Terminschluessel: Person + exakter Aktivitaetscode +
Kalenderbeginn; bei patientenlosen Blocks zusaetzlich Geraet. Unterschiedliche
Status-/Zeitversionen ohne eindeutige Reihenfolge bleiben Konfliktfaelle und
werden nicht durch eine willkuerlich bevorzugte Zeile geloest.

Technische Feldzeilen werden fuer den Export nach Plan/Geraet/Tag/Fraktion
verdichtet; `source_rows` bleibt erhalten. Viele Feldzeilen sind nicht automatisch
Dubletten. Fehlende Fraktionsnummern und zwei getrennte Anwendungen desselben
Plans am selben Tag sind lokale Prueffaelle. Die Methode darf hier keine
scheinbar exakten Besuchszahlen behaupten.

Kontext wird vor und nach dem Auswertungsjahr eingelesen. Der Exporttag wird
niemals kuenstlich als Behandlungsende gesetzt. Eine Episode wird erst nach
beobachteten 30 behandlungsfreien Tagen als abgeschlossen gewertet.

Reife einer Aufklaerungskette: letzte abgeschlossene Aufklaerung plus drei
Kalendermonate bis zum bestaetigten Datenstand. Wiederholte Wiedervorstellungen
zaehlen weiter als Beobachtung; eine Stornierung beendet diese Suche nicht.
Zukuenftige gebuchte Termine werden bis zwoelf Monate nach dem Datenstand erfasst,
aber niemals als bereits durchgefuehrte Behandlung gewertet.

## Statistik und Darstellung

Boxen werden aus individuellen lokalen Messungen berechnet, weitergegeben werden
nur Quartile/Whisker. Gesamtmedian ist der Median aller gepoolten Beobachtungen,
nicht der Mittelwert von vier Geraetemedianen. Die Linie liegt hinter den Boxen
und ist schwarz im hellen, weiss im dunklen Modus.

Keine patientenbezogenen Einzelpunkte in HTML/JSON. Kleine Geraetegruppen werden
unterdrueckt, gegebenenfalls auch der gepoolte Wert als Differenzschutz. Kleine
Teilgruppen im Patientenfluss unterdruecken die betroffenen Werte sowie direkt
abhaengige Summen und Quoten. Unabhaengige Kennzahlen bleiben erhalten.
Mehrere sich ueberlappende Auswertungen erfordern weiterhin eine lokale
Datenschutzpruefung. Fehlend ist nicht Null.

## Technische Grundlagen

SSRS-Abfragezeit und Berichtslaufzeit sind getrennte Grenzen; der Ereignisexport
hat einen begrenzten Abfrage-Timeout. Siehe
[Microsoft: Berichtstimeouts](https://learn.microsoft.com/en-us/sql/reporting-services/report-server/setting-time-out-values-for-report-and-shared-dataset-processing-ssrs?view=sql-server-ver17).
Der lokale Cache ersetzt keine DWH-Aktualitaetspruefung.
Boxplots verwenden vorab berechnete Quartile, siehe
[Plotly: Boxplots](https://plotly.com/python/box-plots/).
