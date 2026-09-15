# Vor dem Upload

- [ ] Es handelt sich um den **Standort-Preflight**, nicht um einen Collector mit Ereignisdetails.
- [ ] Alle Tabellenblaetter wurden kontrolliert, auch ausgeblendete oder zusaetzliche Blaetter.
- [ ] Keine Patienten-, Fall- oder Planidentifikatoren, auch keine Hash-Schluessel.
- [ ] Keine Patienten-/Personalnamen in Aktivitaetsbezeichnungen oder Metadaten; falls doch, vor Weitergabe lokal bereinigen.
- [ ] Keine Befund-/Aufklaerungsnotizen, Geburtsdaten, Original-DICOM-UIDs oder Screenshots mit Patientendaten.
- [ ] Keine Zugangsdaten, Verbindungspasswoerter oder unbereinigten Logs.
- [ ] Ein vollstaendiges ZIP mit ID `STANDORT_Phase_VON-BIS_R01`; alle enthaltenen Dateinamen beginnen mit derselben ID, ohne Patientenangaben.
- [ ] Standortkuerzel, voller Klinikname, Zeitraum, Revision, Exportdatum und RDL-/Analyseversion sind im Begleitbogen angegeben.
- [ ] Eine dienstliche Rueckmeldeadresse und die vollstaendige Dateiliste stehen im Begleitbogen.
- [ ] Bei Korrekturen: neue Revision, ersetzte Einreichungs-ID und Aenderungsgrund angegeben; unveraenderte Wiederholung behaelt ihre ID.
- [ ] Begleitbogen enthaelt nur notwendige dienstliche Kontaktangaben und organisatorische Informationen.
- [ ] Die lokale Freigabe zur Weitergabe liegt vor; kleine Aggregate wurden geprueft.

## Fuer spaetere Ergebnisse

- [ ] Nur freigegebene `Standortanalyse.html`, `aggregate.json` und `Kennzahlen.csv`, jeweils mit der Einreichungs-ID im Dateinamen, plus Begleitbogen.
- [ ] Methode, Zeitraum, Datenstand und Nachweisluecken sind angegeben.
- [ ] Klinische Quellen einschliesslich manueller Therapie/Brachy wurden abgeglichen.
- [ ] Keine Detail-CSVs, Ereignis-Exceldateien, Cache-Datenbanken oder lokalen Zuordnungsformulare.

Bei Unsicherheit **nicht hochladen**. Zuerst mit der lokalen Freigabestelle und
der fachlichen Projektansprechperson klaeren. GitHub ist kein Ablageort fuer
klinische Dateien. Dieser technische Hinweis ersetzt keine lokale Freigabe.

[Zum Upload](https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/)
| [Zurueck zur Teilnahme](README.md)
