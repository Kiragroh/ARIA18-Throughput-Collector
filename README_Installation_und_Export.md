# Installation und Export

## Voraussetzungen

- ARIA 18 mit erreichbarem SSRS-ReportServer und der DWH-Datenquelle `variandw`
- Leserechte auf die Varian-DWH
- Recht zum Anlegen eines Berichts in einem persönlichen oder freigegebenen SSRS-Ordner
- Microsoft Report Builder oder Zugriff auf das ReportServer-Webportal

## Einmalige Einrichtung

1. `dist/ARIA18_Durchsatz_Klinikvergleich_Collector.rdl` im ARIA-Modul **Berichte** importieren oder im Microsoft Report Builder öffnen.
2. Prüfen, ob die gemeinsame Datenquelle `/VarianTemplate/Data Sources/variandw` erreichbar ist. Falls der Standort einen anderen Pfad verwendet, nur die Referenz der Datenquelle anpassen; die SQL-Abfragen bleiben unverändert.
3. Den Bericht in einem Ordner veröffentlichen, in dem der ausführende Benutzer Berichte anlegen darf. Ein persönlicher Ordner wie `/Users Folders/<DOMÄNE Benutzer>/My Reports` ist für einen Test geeignet.
4. Den gewünschten Zeitraum und die tatsächlich zu vergleichenden Therapiegeräte auswählen. Die Geräteliste wird aus den im Zeitraum beobachteten Behandlungen aufgebaut.

## Parameter

- `Standort`: neutrale Bezeichnung für den Export, beispielsweise `Klinik A`.
- `Zeitraum von/bis`: gewünschter Beobachtungszeitraum. Im Export stehen zusätzlich erster und letzter tatsächlich beobachteter Behandlungstag.
- `Geräte`: nur die zu vergleichenden LINACs auswählen. Ausgewählte und tatsächlich aktive Geräte werden getrennt berichtet.
- `Mindestgruppengröße`: Standard 5; schützt kleine klinische Fallmix-Gruppen. Gesamtzahlen und Gerätetage werden dadurch nicht entfernt.
- `Pseudonymisierte Detailblätter`: nur einschalten, wenn die empfangende Stelle diese kontrollierten Forschungsdaten benötigt.

## Export

Im Webportal kann der Bericht normal als Excel exportiert werden. Per HTTP funktioniert derselbe Weg wie bei anderen ARIA-Berichten:

```text
http://REPORTSERVER/ReportServer?/ORDNER/BERICHT&rs:Command=Render&rs:Format=EXCELOPENXML
```

Parameter können an die URL angehängt werden. Mehrfach ausgewählte Geräte werden als wiederholte `Machines=`-Parameter übergeben.

Der mitgelieferte Testhelfer veröffentlicht eine zeitgestempelte Kopie, rendert PDF und Excel und entfernt die Testkopie anschließend:

```powershell
pwsh -File tools\publish_and_test_rdl.ps1 `
  -ReportServer http://REPORTSERVER/ReportServer `
  -ParentPath '/Users Folders/DOMÄNE Benutzer/My Reports' `
  -PeriodStart 2025-01-01 -PeriodEnd 2025-12-31 `
  -Machines LINAC1,LINAC2,LINAC3,LINAC4
```

Alternativ `tools/Test_ARIA18_Collector.bat` starten. Der ReportServer und der persönliche Zielordner werden abgefragt. Für den Test wird die Windows-Anmeldung des ausführenden Benutzers verwendet; es werden keine Passwörter gespeichert. Werden keine Gerätenamen übergeben, verwendet der Report seine automatisch ermittelte Standardauswahl.

## Übergabe

Für den Klinikvergleich reicht die erzeugte `.xlsx`. Die RDL muss nicht dauerhaft öffentlich liegen. Vor der Weitergabe prüfen:

- Standort, Zeitraum und Geräteauswahl sind korrekt.
- `00_Coverage` zeigt den erwarteten ersten und letzten Behandlungstag.
- `07_DataQuality` enthält keine unerklärten großen Ausschlüsse.
- Detailblätter `90_...` und `91_...` sind nur enthalten, wenn sie bewusst aktiviert wurden.
- Die SHA-256-Prüfsumme der RDL stimmt mit `dist/SHA256SUMS.txt` überein.

## Lokale Besonderheiten

Der Collector enthält zwei bekannte ARIA-18-Ressourcenpfade: `InSightiveResourceMachine` sowie `vv_ResourceInfo`/`ctrResourceSer`. Welche Variante verfügbar ist, wird im Blatt `00_Coverage` dokumentiert. Falls beide fehlen, bleibt die Slotauswertung leer und `07_DataQuality` weist darauf hin; die Behandlungsdaten können dennoch exportiert werden.
