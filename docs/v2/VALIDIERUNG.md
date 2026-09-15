# Pruefstatus 2.0-rc.1

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
