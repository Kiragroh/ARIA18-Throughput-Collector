# Methodik 2.0

## Einheiten und Nenner

| Kennzahl | Zaehler | Nenner / Interpretation |
|---|---|---|
| Technische Plan-Fraktion | Dosis-/MU-Nachweis je Person, Plan, Geraet, Tag, Fraktion | Keine Patienten- oder Kurszahl |
| Besuch | Verbund technischer Plan-Intervalle derselben Person/Geraet/Tag innerhalb der Besuchstoleranz | Toleranz standardmaessig 5 Minuten; Sensitivitaet 0/5/10 |
| Terminmatch | Eindeutig 1:1 zugeordnete Besuche | Relevante nicht stornierte Therapieslots; unzugeordnete Slots bleiben erhalten |
| Messabdeckung | Slots mit plausiblem Intervall im gewaehlten Modell | Alle relevanten Slots; niedrige Abdeckung nicht als gute Effizienz auslegen |
| Slotabdeckung | Summe tatsaechlicher Ueberlappung mit zugeordnetem Kalenderslot | Summe genau dieser gebuchten Dauern; gewichtet, 0 bis 100 Prozent |
| Dauer / Slot | Summe gemessener Dauern mit gueltigem Slot | Summe derselben Slotdauern; ignoriert Zeitverschiebung, kann >100 Prozent sein |
| Patienten | Eindeutige Personen mit technischer oder bestaetigter manueller Behandlung | Nicht ueber Geraete oder Zeitabschnitte addieren |
| Bestrahlte Plaene | Eindeutige technische Plaene mit Bestrahlung im Zeitraum | Brachy-/historische Termine ohne Planreferenz sind keine erfundenen Plaene |
| Neueinstellungen (Plaene) | Erste tatsaechliche Bestrahlung des Plans | Fraktion 1 oder erster Behandlungstag aus Planquelle; unabhaengig von Terminbezeichnungen |
| Gebucht | Tatsächlich im Kalender stehende Endzeit minus Beginn | Kein nachtraeglich angenommener Standardtermin |
| Freie Stunden | Summe positiver Luecken der Intervallvereinigung | Beobachtetes Geraetetagesfenster zwischen erstem Beginn und letztem Ende |
| Freier Anteil | Freie Stunden | Stunden dieses beobachteten Fensters, nicht nominelle Verfuegbarkeit |
| Takt | Beginn bis naechster beobachteter Beginn eines anderen Patienten | Positive Differenz am selben Geraetetag, nie ueber Nacht |
| Wechsel | Ende des vorherigen beobachteten Besuchs bis naechster Beginn | Ueberlappungen ausgeschlossen, nicht auf Null gesetzt |
| Behandlungsepisode | Ueberlappende Behandlungsintervalle mit maximal 30 Tagen Pause | Alle bestaetigten Modalitaeten derselben Person zusammen |
| Aufklaerungsepisode | Kette abgeschlossener Aufklaerungen vor einem folgenden Beginn bzw. ohne folgenden Beginn | Erster abgeschlossener Termin bestimmt die Kohorte |
| Ungeklaert ohne Beginn | Reife Aufklaerungsepisoden ohne Behandlung und ohne weitere Beobachtung | Alle reifen Episoden, auch die mit Behandlung; kein No-show-Nachweis |
| Stornoquote | Eindeutige stornierte/abgebrochene Aufklaerungstermine | Alle eindeutigen registrierten Aufklaerungstermine im Zeitraum, Status separat |

Die begonnenen Behandlungsepisoden im Kalenderjahr sind **nicht** der Nenner der
Aufklaerungsquote. Einige beginnen nach einer Aufklaerung aus dem Vorjahr oder ohne
in der Quelle auffindbare Aufklaerung. Umgekehrt beginnt die Behandlung einer
Aufklaerungskohorte eventuell erst im Folgejahr.

## Getrennter Definitionsabgleich

Die vorab festgelegte Aufklaerungskohorte bleibt dem **ersten abgeschlossenen
Termin** zugeordnet. Eine zusaetzliche operative Sensitivitaetsauswertung ordnet
den Pfad dem **letzten abgeschlossenen Termin** zu. Ausschliesslich offene
Aufklaerungen werden darin nur bei nachfolgendem Behandlungsbeginn als abgeleitete
Anwesenheit gezaehlt und separat von dokumentierten Abschluessen ausgewiesen.
Das aendert weder den Status noch die Zahl abgeschlossener Termine. Auch der
Kalendertag des Behandlungsbeginns gilt hier als passende Terminzuordnung.

Der Abgleich stellt zwei Behandlungsdefinitionen nebeneinander:

- Einzelne belegte Behandlungstage mit maximal 30 Tagen Abstand.
- ARIA-Kursintervalle vom ersten bis letzten belegten Behandlungstag, danach
  Zusammenfuehrung bei Ueberlappung oder maximal 30 Tagen Abstand. Ohne Kursreferenz
  wird die Planreferenz verwendet. Ein solches Kursintervall kann eine laengere
  interne Pause ueberbruecken; deshalb ist es nicht die automatische Hauptdefinition.

Bestaetigte manuelle Therapien bleiben in beiden Varianten enthalten. Die Zahlen
sind alternative Definitionen, keine addierbaren Patientengruppen. Kleine
Teilgruppen und kleine Differenzen zwischen Varianten werden unterdrueckt.
Ein identisches Ergebnis belegt noch keine identische oder vollstaendige Quelle.

Der Quellfilter-Abgleich zaehlt **Ereigniszeilen**, nicht Patienten oder Fraktionen,
und trennt Auswahlzeitraum und gesamten Kontext. Direkte Bildobjekte sind davon
ausgenommen. Testnamenskennzeichen, lokales Kennungsformat und Ressourcenstatus
werden mit dieser Vorrangfolge disjunkt gezaehlt. Nichtnumerische Kennungen sind
nicht automatisch Testpatienten; der Filter muss zum Standort passen. Fehlende
Flagspalten werden als nicht pruefbar gekennzeichnet. Bereits upstream ausgeschlossene
Datensaetze koennen anhand dieses Exports nicht nachtraeglich inventarisiert werden.

## Zeitmodelle

### Terminzuordnung ohne standortspezifischen Namen

Fachlich klassifizierte Therapietermine bleiben die primaere Terminquelle.
Zusaetzlich kann ein noch nicht klassifizierter Geraetetermin einen Zeitanker
liefern, wenn dieselbe Person am selben konfigurierten R&V-Geraet einen
technischen Besuch hat und dessen gesamtes Intervall im dokumentierten
Aktivitaetsintervall liegt. Kalender- und Aktivitaetszeiten muessen gleichentags,
positiv und innerhalb der bestehenden Plausibilitaetsgrenzen liegen. Es gelten
derselbe Terminabgleich von -120 bis +240 Minuten und die vorhandene
Besuchsdefinition. Status muss abgeschlossen oder offen sein.

Die Zuordnung muss in **beide Richtungen eindeutig** sein. Bereits ein
klassifizierter Therapietermin als zeitlicher Kandidat sperrt die automatische
Ergaenzung, auch wenn dessen Zuordnung mehrdeutig bleibt. Kein naechstgelegener
Ersatz bei konkurrierenden unbekannten Terminen, keine Zuordnung eines Termins
zu mehreren Besuchen. Explizites Ignore, Block, Aufklaerung oder Beobachtung
wird niemals automatisch ueberstimmt.

Diese Regel betrifft ausschliesslich Zeitmessungen und den zugehoerigen
Slotnenner. Die klinische Terminart und der Status werden nicht umklassifiziert.
Patienten, Fraktionen, Planbeginne und Behandlungsepisoden erhalten dadurch
keine zusaetzlichen manuellen Nachweise. Brachy und historische Therapie ohne
R&V benoetigen weiterhin eine lokale Zuordnung. Aus Zahl oder Namen der
Termine wird kein technischer Bestrahlungsnachweis abgeleitet.

R&V-gestuetzte Zeitzuordnungen werden im Kontext und pro Abschnitt/Geraet
separat gezaehlt; kleine Teilgruppen bleiben unterdrueckt. Die lokale fachliche
Pruefung bleibt erforderlich, auch wenn die technische Zuordnung eindeutig ist.

### Zeitanker

- **Aktivitaet (Standard):** dokumentierter Aktivitaetsbeginn bis dokumentiertes Ende.
  Fehlende einzelne Anker koennen durch zugeordnete technische Anker ersetzt
  werden. Anzahl dieser Ersatzintervalle bleibt separat sichtbar.
- **Workflow:** erstes plausibles Imaging vor Beam, sonst erster Beam, bis
  dokumentiertem Aktivitaetsende, ersatzweise eindeutigem Abschlussanker aus der
  Historie. Fehlender Abschluss wird nicht durch die Slotzeit ersetzt.
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

Luecken setzen einen vollstaendig messbaren Geraetetag voraus:
alle relevanten Termine plus nicht zugeordnete technische Besuche benoetigen ein
plausibles Intervall des gewaehlten Modells. Sonst bleibt die Tagesbelegung
unbekannt; die fehlende Behandlung wird nicht als Pause gezaehlt. Vollstaendige
und ausgeschlossene Geraetetage sowie Messabdeckung bleiben sichtbar. Die
auswertbare Teilmenge kann selektiv sein und wird nicht auf ein Jahr hochgerechnet.
Auch vollstaendige exportierte Intervalle beweisen nicht die Vollstaendigkeit
aller klinischen Quellen. Diese muss der Standort gesondert bestaetigen.

Takt und Wechsel verwenden alle aufeinanderfolgenden beobachteten Besuche.
Ein unvollstaendiger Tag schliesst diese Stichprobe nicht pauschal aus.
Fehlende Zwischenbesuche koennen Abstaende vergroessern: Diese Verteilungen
belegen deshalb keine freie Zeit und keine lueckenlose Patientenfolge.
Der JSON-Export kennzeichnet dies als `consecutive_observed_visits` und liefert
mit `cycle_complete_days` und `change_complete_days` die strengere Teilmenge
als Sensitivitaetsanalyse. Takt und Wechsel haben jeweils eigene Stichproben
und Kleingruppenpruefungen; ueberlappende Besuche erzeugen keinen Null-Wechsel.

Optionale Oeffnungsstunden gelten nur bei lokaler Bestaetigung, je **beobachtetem
aktiven Geraetetag**. Tage ohne Behandlung fehlen in diesem Nenner. Daraus darf
keine Jahresverfuegbarkeit oder ungeplante technische Ausfallzeit abgeleitet werden.

## Deduplizierung und Grenzen

### Slotlaenge und zeitliche Passung

Primaer ist die Summe der tatsaechlichen Behandlungsdauern geteilt durch die
Summe der zugehoerigen gebuchten Slotlaengen. Ein zeitlicher Versatz aendert
diese Kennzahl nicht; Werte ueber 100 Prozent sind moeglich.
Die zeitliche Ueberlappung mit dem Kalenderslot bleibt eine separate Kennzahl.
`slot_overlap_visits_pct` zaehlt jede positive zeitliche Ueberschneidung,
auch bei Beginn vor oder Ende nach dem Slot. Reine Randberuehrung zaehlt nicht.
`fully_in_slot_pct` verlangt Beginn und Ende innerhalb des Slots.
Nenner ist `slot_position_n`: Besuche mit
messbarem Ist-Intervall und gueltigem gebuchten Slot. Fehlende Zeiten werden
nicht als Fehlpassung oder Null gewertet. Alle Werte folgen dem Zeitmodell.

### Optionale Erweiterung: Ankunft und Wartezeit

Das optionale Excel-Sheet `93_Wartebereich` prueft native ARIA-Daten aus
`PatientLocation` und `PatientLocationMH`, verknuepft ueber den Termin.
Es verwendet den fruehesten expliziten Check-in (`CheckedInFlag=1`) und den
dokumentierten Ist-Beginn (`ActualStartDate`), niemals das geplante Ende.
Die aktuelle InSightive-Wartebereichsansicht ist keine historische Quelle:
sie kann intern auf den heutigen Tag eingeschraenkt sein.

Ausgegeben werden nur monatliche Diagnosegruppen: fehlender Check-in,
fehlender Ist-Beginn, negative Zeit, tageuebergreifend, mehr als 240 Minuten
und gleicher Tag mit 0 bis 240 Minuten. Die 240 Minuten sind eine technische
Pruefschwelle, keine klinische Normalitaetsgrenze. Auch die letzte Gruppe ist
ohne lokale Validierung keine belastbare Wartezeitkennzahl. Alle Terminarten
werden hier zunaechst gemeinsam geprueft, nicht nur Bestrahlungstermine.
Namenshinweise TEST/DUMMY werden intern als `TEST_HINT` getrennt; `NOT_FLAGGED`
beweist nicht, dass keine Testpatienten enthalten sind. Keine Namen, IDs,
Notizen oder Einzelfallzeiten werden in diesem Sheet ausgegeben.
Gruppen unter fuenf Personen bleiben zahlenmaessig leer. Fehlende Quelle
oder Leserechte werden als `UNAVAILABLE` statt als Null markiert.

Als weitere Erweiterung vorgemerkt: externe Barcode-/OPAS-Ankunftsereignisse.
Erforderlich sind eine eindeutige Besuchszuordnung, Zeitbasis/Zeitzone und die
lokale Bedeutung des Ereignisses (Ankunft, Anmeldung, Raumzutritt).
Erst dann kann Ankunft bis tatsaechlichem Behandlungsbeginn ausgewertet werden.
Ein verspaeteter Beginn gegenueber dem Kalenderslot ist keine Patientenwartezeit.
Ohne solche Nachweise bleibt die Kennzahl nicht verfuegbar; keine Pflichtangabe.

Identische Quellzeilen und gleiche Termine mit mehrfachen Ressourcen werden
zusammengefuehrt. Natuerlicher Terminschluessel: Person + exakter Aktivitaetscode +
Kalenderbeginn; bei patientenlosen Blocks zusaetzlich Geraet. Unterschiedliche
Status-/Zeitversionen ohne eindeutige Reihenfolge bleiben Konfliktfaelle und
werden nicht durch eine willkuerlich bevorzugte Zeile geloest.
Die reine Anzahl zugeordneter Quell-/Ressourcenzeilen ist kein klinischer Konflikt.
Eine leere oder mehrdeutige Ressourcenabbildung darf fuer externe Therapietermine
aus genau einem technisch belegten Tagesgeraet derselben Person aufgeloest werden.
Die Zahl dieser Zuordnungen bleibt sichtbar. Bei mehreren tatsaechlichen Geraeten
bleibt die Zuordnung ungeklaert. Brachy und historische Therapien werden dadurch
nicht einem LINAC zugeschlagen.
Ein externer Therapietermin ohne aufloesbares Geraet beweist am selben Tag wie
eine technisch belegte externe Bestrahlung keine **zusaetzliche** Fraktion.
Er bleibt als Behandlungsnachweis und Prueffall erhalten, wird aber nicht noch
einmal als manuelle Fraktion addiert. Der Kontextzaehler weist dies gesondert
aus. Andere bestaetigte Modalitaeten, insbesondere Brachy und historische
Therapie ohne R&V, bleiben getrennt zaehlbar. Eine wirklich zusaetzliche
Anwendung benoetigt einen eigenen belastbaren Nachweis.

Ab Collector rc.6 werden patientenlose Reservierungen bei der Ressourcenauflosung
zunaechst nach Quelltransaktion getrennt. Erst nach eindeutiger Geraetezuordnung
werden gleiche Slots desselben Geraets zusammengefuehrt. Parallele Pausen
mehrerer Geraete verlieren dadurch nicht ihre Zuordnung. Geloeschte/stornierte
Ressourcenzuordnungen erzeugen kein zusaetzliches aktuelles Geraet. Das ist
getrennt vom Stornostatus eines klinischen Termins. Das Terminarteninventar
enthaelt jetzt auch patientenlose Reservierungen. Bereits in alten Exporten
verlorene Ressourceninformation kann lokal nicht rekonstruiert werden.

Exakte Aktivitaetsnamen koennen im Profil mehrdeutige Aktivitaetscodes uebersteuern.
Testnamen und nichtklinische Kennungen werden nur anhand nicht-identifizierender
Quellflags geprueft. Die numerische Kennungsregel ist standortabhaengig, nicht
universell. Namen/Kennungen verlassen die quellseitige Klassifikation nicht.

Technische Feldzeilen werden fuer den Export nach Plan/Geraet/Tag/Fraktion
verdichtet; `source_rows` bleibt erhalten. Viele Feldzeilen sind nicht automatisch
Dubletten. Fehlende Fraktionsnummern und zwei getrennte Anwendungen desselben
Plans am selben Tag sind lokale Prueffaelle. Die Methode darf hier keine
scheinbar exakten Besuchszahlen behaupten.

Kontext wird vor und nach dem Auswertungsjahr eingelesen. Der Exporttag wird
niemals kuenstlich als Behandlungsende gesetzt. Eine Episode wird erst nach
beobachteten 30 behandlungsfreien Tagen als abgeschlossen gewertet.

Ab rc.4 umfasst die Exportkohorte auch ausschliesslich im Vorjahr behandelte
Personen. Alte Exporte ohne diesen Nachweis duerfen keinen vollstaendigen
Vorjahresvergleich anzeigen. Die optionalen Planfelder stammen aus
DimPlan.NoFractionsPlanned/FirstDayOfTreatment/LastDayOfTreatment, ersatzweise
FactTreatmentHistory.FractionsPlanned. Aktuelle Planattribute sind keine
historische Version der damaligen Verordnung.

Planebene und Episode sind getrennt: Erreichte Sollfraktionen bedeuten
vollstaendig bestrahlt. Ein unvollstaendiger Plan ohne Fortsetzung fuer **mehr
als sieben beobachtete Tage** gilt analytisch als beendet, nicht als klinisch
abgeschlossen. Ohne Soll bleibt der Zustand "Soll unbekannt". Bei zu kurzer
Nachbeobachtung bleibt das Ende offen. Eine spaetere Fortsetzung desselben Plans
wird als Pause/Fortsetzung ausgewiesen, nicht als neue Neueinstellung.
Der letzte belegte Behandlungstag bleibt das Enddatum. Die 30-Tage-Regel fuer
modalitaetsuebergreifende Episoden aendert sich dadurch nicht.

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
unterdrueckt und aus dem gepoolten Wert entfernt, damit sie nicht als Differenz
rekonstruiert werden koennen. Der verbleibende Pool wird als Teilmenge markiert. Kleine
Teilgruppen im Patientenfluss unterdruecken die betroffenen Werte sowie direkt
abhaengige Summen und Quoten. Unabhaengige Kennzahlen bleiben erhalten.
Mehrere sich ueberlappende Auswertungen erfordern weiterhin eine lokale
Datenschutzpruefung. Fehlend ist nicht Null.

## Bildobjektfrequenz und Ausstattung

Fuer Geraete mit technischem R&V-Nachweis im Export werden Therapie-Termine
nicht als zusaetzlicher klinischer Behandlungsnachweis verwendet, auch nicht
an Tagen ohne passenden Delivery-Datensatz. Das gilt fuer Patienten, Fraktionen,
Aufklaerungszuordnung und Behandlungsepisoden. Ihre Kalenderslots und Zeitanker
bleiben im Durchsatz erhalten. Neueinstellungen folgen technischen Planstarts.
Fehlende technische Daten sind eine Quellluecke, kein Anlass, Termine als
tatsaechlich bestrahlte Fraktionen umzudeuten.

Ab Collector rc.8 ergaenzt die native VARIAN-Quelle Hersteller, Modalitaet,
Referenzkennzeichen und Aufnahmegeraet. Brainlab-ImagePI/RTIMAGE wird als
ExacTrac klassifiziert, niemals ImageDRR/ReferenceImage. ImageCT-Schichtobjekte
werden nicht zusaetzlich als Aufnahmen gezaehlt. Die Verknuepfung zur DWH erfolgt
ueber dieselbe gesalzene Bildidentitaet, nicht ueber Patient und Tag. Details und
Quellvoraussetzungen stehen in der [Bildgebungsdokumentation](https://github.com/Kiragroh/ARIA18-Throughput-Collector/blob/main/docs/v2/IMAGING.md).

Reine Termingeraete ohne technische Nachweise werden nicht fuer Auslastung,
Slotnutzung, Behandlungsdauer oder Pausen verwendet. Fuer die klinische
Beschreibung wird je Patient und Geraet ein Behandlungscluster mit maximal 30
Tagen Abstand als ein Mindestplan geschaetzt. Die Clusterbildung erfolgt vor
der Periodenauswahl ueber den gesamten verfuegbaren Kontext. Diese Zahl ist
getrennt von technisch belegten Plaenen; sie belegt weder Planidentitaet,
Sollfraktionen noch Planabschluss. Unterschiedliche echte Plaene im Cluster
bleiben unerkannt, getrennte Cluster koennen denselben technischen Plan nutzen.
Es handelt sich deshalb um eine Modellannahme, keine bewiesene Untergrenze
eindeutiger Planidentitaeten. Ungeklaerte Termine an technisch belegten Geraeten
werden nicht als zusaetzliche Mindestplaene geschaetzt.

Der optionale Adapter liest `DWH.FactPatientImage` fuer den ausgewaehlten
Zeitraum. Er dedupliziert nach Bildobjektidentitaet, ersatzweise nach belegbarer
Quellidentitaet. Originalkennungen und Bildnamen werden nicht exportiert.
Referenzbilder werden separat erkannt und nicht als Aufnahmefrequenz gezaehlt.
CBCT, kV/MV-2D, explizit bezeichnete ExacTrac-Objekte und unbekannte Typen bleiben
getrennt. Diese Bildnamenklassifikation ist vorlaeufig, keine DICOM-Verifikation.

Ein ExacTrac-Stereopaar kann zwei Bildobjekte sein. Objektzahl ist daher nicht
gleich Zahl der Aufnahmevorgaenge. Die Verknuepfung mit der Behandlungsdauer
erfolgt nur bei genau einem messbaren Besuch pro Person/Geraet/Tag. Mehrere
Besuche werden nicht willkuerlich zugeordnet. Nenner sind messbare Besuche im
gleichen Zeitmodell und derselben Ausstattungsepoche. Ein Besuch kann mehrere
Bildarten aufweisen; diese Gruppen sind nicht addierbar. `ExposureTime` ist
keine vollstaendige Prozesszeit, `ImageCreationDate` nicht sicher Akquisitionszeit.

Im lokalen Profil kann `equipment_periods` datierte Angaben aufnehmen:

```json
{"machine":"LOKALER_GERAETECODE","start":"2025-01-01","end":"2025-12-31",
 "model":"Halcyon","cbct_system":"HyperSight","cbct_modality":"kv","confirmed":true}
```

Dies ist ein Beispiel, keine automatische Standortannahme. Bei Umbauten werden
nicht ueberlappende Epochen verwendet. Fehlende Angaben bleiben unbekannt;
aus einer kurzen Bildzeit wird weder HyperSight noch eine andere Hardware
abgeleitet. Vergleiche sind deskriptiv, nicht fallmixadjustiert oder kausal.

## Technische Grenzen

Ab Collector rc.7 bedeutet `Capabilities.available`: Die Spalte ist in den
Metadaten sichtbar und fuer das ausfuehrende Datenbankkonto lesbar. Zusaetzlich
werden `schema_available` und `select_allowed` getrennt ausgegeben. Metadaten
koennen selbst durch Berechtigungen unsichtbar sein; `schema_available=0` ist
deshalb nicht automatisch der Nachweis, dass die Spalte nicht existiert.
Die effektiven SELECT-Rechte werden pro Spalte geprueft, nicht pauschal anhand
einer Benutzerrolle. Siehe [Microsoft: HAS_PERMS_BY_NAME](https://learn.microsoft.com/en-us/sql/t-sql/functions/has-perms-by-name-transact-sql).

Pflichtfelder und mindestens ein lesbarer MU-/Dosisnachweis sind Voraussetzung
fuer Ereignisse. Fehlen sie, bleibt der kombinierte Report als Quellenpruefung
ausfuehrbar; Metadaten melden `EVENTS_UNAVAILABLE_CHECK_CAPABILITIES`. Daraus
entsteht keine Analyse mit Null Patienten. Optionale Spalten werden typisiert
leer geliefert, nicht als Nullmessung. Fehlende Historien-Schluessel deaktivieren
die davon abhaengigen Diagnosen mit `SOURCE_UNAVAILABLE`. Fehlende Bildobjekte
deaktivieren nur die Zusatzquelle, nicht vorhandene technische Therapieereignisse.

`DWH.FactPatientImage` ist als optionale Quelle mit allen abgefragten Spalten im
Inventar enthalten. Nicht vorhandene Plan-/Zeit-/Bildfelder begrenzen die jeweils
betroffenen Kennzahlen. Vorhandene Leserechte belegen weder vollstaendige
Dokumentation noch einen aktuellen DWH-Datenstand. Die Rechtepruefung ersetzt
keine lokale Funktionspruefung; Sonderfaelle wie fehlerhafte Views bleiben moeglich.

Das lokale Profilformular uebernimmt den Auswertungszeitraum aus den
Exportmetadaten, auch beim Wiederverwenden einer vorhandenen Codezuordnung.
Eine bisherige Quellenfreigabe wird nicht automatisch auf einen neuen Export
uebertragen. Einreichende benoetigen unveraendert nur Excel und Begleit-JSON;
das technische Profil dient der lokalen Auswertung.

SSRS-Abfragezeit und Berichtslaufzeit sind getrennte Grenzen; der Ereignisexport
hat einen begrenzten Abfrage-Timeout. Siehe
[Microsoft: Berichtstimeouts](https://learn.microsoft.com/en-us/sql/reporting-services/report-server/setting-time-out-values-for-report-and-shared-dataset-processing-ssrs?view=sql-server-ver17).
Der lokale Cache ersetzt keine DWH-Aktualitaetspruefung.
Boxplots verwenden vorab berechnete Quartile, siehe
[Plotly: Boxplots](https://plotly.com/python/box-plots/).
## Historische Aktivitaetsnamen (Collector rc.9)

Der Join auf die historische Aktivitaet bleibt ueber DimActivityID eindeutig.
Nur NULL, leere oder NA-Namen werden aus der neuesten Revision ergaenzt, ueber
ctrActivitySer des Termins (nicht der unvollstaendigen Dimensionszeile).
Die Reihenfolge ActivityRevCount DESC, DimActivityID DESC ist deterministisch.
Fehlende Revisionsspalten sind optional: ohne Nachweis bleibt der Name erhalten.
ActivityCode, Kategorie und Ereignisschluessel werden nicht umgeschrieben.
activity_name_original, activity_name_source und activity_name_revision dienen
dem Audit. Fuer technische Behandlungsereignisse lautet die Herkunft
not_applicable. Ergaenzte Namen brauchen eine explizite lokale Profilzuordnung.
Termin-Nachweise auf R&V-Geraeten werden weiterhin nicht als zusaetzliche
klinische Fraktionen gezaehlt.
