# Bildgebung: Rueckmeldung und belastbare Grenzen

## Herstellerquelle ab Collector rc.8

Der Full Collector nutzt zusaetzlich die native gemeinsame Datenquelle
`/VarianTemplate/Data Sources/VARIAN`. Sie muss im Reportserver vorhanden und
lesbar sein. Die DWH-Quelle allein enthaelt nicht alle Herstellerangaben.
Fehlende native Tabellen/Spalten oder SELECT-Rechte ergeben `UNAVAILABLE`;
eine fehlende Reportserver-Datenquelle muss lokal zugeordnet werden.

`Image -> ImageSlice -> Slice -> Equipment.Manufacturer` liefert die
Aufnahmehersteller. Brainlab-RTIMAGE vom Typ ImagePI wird als ExacTrac erkannt,
aber ImageDRR und ReferenceImage bleiben ausgeschlossen. Varian allein beweist
kein CBCT: CT-Objekte benoetigen zusaetzlich ein bekanntes Verification-Modell.
ImageCT-Schichtobjekte sind keine zusaetzlichen Aufnahmen und werden aus der
Frequenzzaehlung entfernt. kV/MV bleibt ohne passenden Nachweis unbestimmt.

Die Zusatzdaten werden nur ueber denselben gesalzenen Bildschluessel desselben
Exports verbunden. Fehlende Aufnahmegeraete werden nicht aus dem Plangeraet
oder einer Patient-/Tag-Heuristik erfunden. Nicht zugeordnete ExacTrac-Objekte
bleiben in der Herkunftspruefung sichtbar, aber nicht im LINAC-Nenner.
Alte Exceldateien ohne diese Quelle koennen nicht nachtraeglich anhand eines
Herstellers klassifiziert werden; dafuer ist ein neuer Export erforderlich.

Kurztest UKL, 02.-03.01.2025: Die native Quelle enthaelt 94 Brainlab-ImagePI
und 188 Brainlab-ImageDRR. Diese Zahlen sind Quellinventar, kein Nachweis einer
vollstaendigen standortuebergreifenden Zuordnung. UKE benoetigt einen neuen Export.

Ein technischer Hardware-Erfahrungsbericht vom 15.09.2026 beschreibt relevante
Unterschiede zwischen regulaeren Linacs, Halcyon, regulaeren/adaptiven Ethos-
Workflows und externem ExacTrac. Diese Hinweise sind Ausgangspunkte fuer lokale
Regressionen, keine standortuebergreifende Validierungsbescheinigung.

## Uebernommene Regeln

- Aufnahmeobjekt vor zeitlicher Heuristik: Image, ImageSlice, Slice, SliceRT.
- Aufnahmezeit bevorzugt aus Slice.AcquisitionDateTime, nicht Image.CreationDate.
- Aufnahmegeraet vor Plangeraet; externe Bildgebung getrennt kennzeichnen.
- New ist ein Objektstatus, kein alleiniger Nachweis klinisch offenen Imagings.
- CT-artige Objekte brauchen semantischen Treatment-/RTPlan-Bezug, sonst
  bleiben sie unbestaetigte CT-Kandidaten.
- ExacTrac hat Vorrang vor kV/MV-Einordnung. Bei RTIMAGE wird MINUTE als kV,
  MU als MV unterschieden; Referenzbilder werden getrennt behandelt.
- Kein ARIA-CBCT bei adaptiven Workflows bedeutet nicht keine Bildgebung.

Die Klassifikationsregeln sind separat in `analysis/imaging.py` getestet.
Sie werden **nicht** auf unpassende DWH-Felder angewendet. Der Basisbericht
deklariert seine Bildgebung weiterhin als DWH-Fallback.

## Preflight

[ARIA18_Imaging_Preflight_2.0.rdl](../../dist/ARIA18_Imaging_Preflight_2.0.rdl)
fragt nur Tabellen-/Spaltenmetadaten und Fremdschluesselbeziehungen der operativen
ARIA-Datenquelle ab. Gemeinsame Datenquelle:
`/VarianTemplate/Data Sources/VARIAN`.
Es werden keine Bilder, Patientenstammdaten oder DICOM-UIDs exportiert.

Die aktuelle lokale Schemapruefung bestaetigt den Objektpfad und
AcquisitionDateTime/SliceRT-Felder. Sie zeigt aber auch, dass optionale Felder
nicht an jedem erwarteten Ort existieren (beispielsweise Series.ResourceSer).
Darum werden Beispiel-SQL-Fragmente nicht ungeprueft uebernommen.

## Noch offene Adapterabnahme

`DICOMPlanReference` aus dem Erfahrungsbericht ist ausdruecklich ein logischer
Adaptername, keine behauptete ARIA-Tabelle. Fuer eine belastbare CBCT-Selektion
muss die Referenced RT Plan Sequence auf einen existierenden RTPlan abgebildet
werden. Ein beliebiger DICOMCodeValue oder eine Study-Zugehoerigkeit ist kein
Ersatz dafuer. Diese Abbildung ist in 2.0-rc.1 **noch nicht implementiert/freigegeben**.

Bis zur Abnahme wird keine neue objektbasierte CBCT-Gesamtzahl und kein daraus
abgeleiteter klinischer Start vorgetaeuscht. Zur Abnahme benoetigt werden ein
positiver Treatment-CBCT-Fall, ein technisches CT-Negativobjekt, kV, MV,
ExacTrac sowie regulaere/adaptive Beispiele. Alle Original-IDs bleiben lokal.
