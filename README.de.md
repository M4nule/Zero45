# ⚡ Zero45 – Energiewende-Planspiel (Deutschland 2030–2045)

*English version: [README.md](README.md)*

Ein Planspiel für Gruppen: Teams bauen in vier Stufen ein Stromsystem für Deutschland, das
**zuverlässig**, **klimaneutral** und **bezahlbar** ist. Jede Stufe wird mit einem echten
Strommarktmodell (PyPSA + HiGHS) für alle 8.760 Stunden eines Jahres simuliert. Das Spiel läuft auf Deutsch oder
Englisch – wählbar pro Browser (siehe „Sprache“ unten) – auf einem Laptop im Raum, ohne Internet.

Die Spielidee stammt von **„Path to Zero“** von Jesse D. Jenkins und dem Princeton ZERO Lab. Zero45 ist eine
unabhängige, inoffizielle Adaption mit eigenem Modell und deutschen Daten; sie ist nicht mit der Princeton
University verbunden oder von ihr unterstützt (siehe [Credits](#credits)).

> **Bitte lesen:** Zero45 ist ein Lernspiel, keine Prognose – siehe [Einordnung](#einordnung-was-das-spiel-ist-und-was-nicht)
> und [Haftungsausschluss](#haftungsausschluss). Freie Software unter der [GPL-2.0-or-later](#lizenz).

**Dokumente** (im Ordner [`docs/`](docs/), deutsch und englisch): Spielregeln, Kurzanleitung, Hintergrund für die
Spielleitung, Spickzettel für die Spielleitung.

---

## Schnellstart

### 1. Einmalig: Installation
Nur auf dem Rechner der Spielleitung nötig – die Teams brauchen nur einen Browser.

Spiel herunterladen: auf GitHub **Code → Download ZIP** und entpacken, oder das Repository mit `git clone` holen.

**Windows** (PowerShell im Spielordner):
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```
**Mac/Linux**:
```bash
bash setup.sh
```
Das installiert [uv](https://docs.astral.sh/uv/) (Python-Paketmanager), ein eigenes Python und alle
Pakete in den Ordner `.venv`. Dauer: 1–3 Minuten, Internet nötig. **Nach jedem Update** des
Spielordners das Setup einmal erneut ausführen (mit Internet) – es installiert dann nur, was sich
geändert hat. Unterstützt: Windows 10/11 (auch ARM-Laptops), macOS ab 14 mit Apple-Chip (noch nicht auf einem echten Mac getestet), Linux x86_64. Auf
Intel-Macs und macOS 13 gibt es einige Pakete nicht fertig gebaut: dann in `pyproject.toml` die Zeile
`no-build = true` löschen (das Setup baut sie dann selbst und braucht dafür die Xcode Command Line Tools).
Fehlt uv, startet das Setup den offiziellen uv-Installer von Astral (feste Version 0.11.32, von
astral.sh); er installiert uv ins Benutzerprofil (`%USERPROFILE%\.local\bin` bzw. `~/.local/bin`).

### 2. Spielen
| Was | Windows | Mac/Linux |
|---|---|---|
| **Netzwerk-Modus**: Gruppenspiel (Teams im WLAN) | `.\start_spiel.ps1` | `bash start_spiel.sh` |
| **Lokaler Modus**: nur dieser Rechner, mit Einzelspiel | `.\start_spiel.ps1 -Local` | `bash start_spiel.sh --local` |
| Lokaler Modus, öffnet direkt das Einzelspiel | `.\start_spiel.ps1 -Solo` | `bash start_spiel.sh --solo` |

Das Einzelspiel gibt es nur im lokalen Modus – im Netzwerk-Modus können Teams so keine eigenen
Spiele starten und Rechenleistung belegen.

Optionen: `-Port 8000` / `--port 8000`, `-Password geheim` / `--password geheim`, `-Workers 3` / `--workers 3`.

Verweigert Windows das Skript („Die Ausführung von Skripts ist auf diesem System deaktiviert“ oder Sicherheitswarnung
für heruntergeladene Dateien), wie beim Setup starten: `powershell -ExecutionPolicy Bypass -File .\start_spiel.ps1`
(gilt nur für diesen Aufruf), oder die Skripte im Spielordner einmal freigeben: `Unblock-File .\*.ps1`.

**Rechenprozesse:** Die Zahl gleichzeitiger Berechnungen wird beim Start aus Kernen und freiem Arbeitsspeicher
bestimmt (je Prozess bis ~1,2 GB; das Fenster zeigt z. B. „Simulation processes: 2 (3.4 of 16 GB free …)“). Ab 12 GB
Arbeitsspeicher und 3 Kernen sind es mindestens 2. Mehr erzwingen: `.\start_spiel.ps1 -Workers 3` – reicht der
Speicher dann nicht, lagert Windows aus und es wird langsamer, aber nichts geht verloren.
Ist der Port belegt, nimmt das Spiel automatisch den nächsten freien und zeigt ihn an.

**Spielleitung:** Die Seite `/host` öffnet sich im Netzwerk-Modus nur am Spielleitungs-Rechner
selbst (Beamer-Laptop). Von Handys im WLAN ist sie gesperrt. Soll die Spielleitung von einem
anderen Gerät aus laufen: `-HostRemote` / `--host-remote` – dann unbedingt ein eigenes Passwort
setzen (`-Password <eigenes>`), denn das Standard-Passwort `energiewende` steht in dieser Anleitung.

Beim Start zeigt das Fenster die Adressen an (Startfenster und Setup sind auf Englisch), z. B.:
```
This computer:    http://localhost:8000
Mode:             network (teams in the Wi-Fi)
In the network:   http://192.168.1.23:8000/join   [WLAN]
In the network:   http://172.20.80.1:8000/join   [vEthernet (WSL)]   (virtual adapter/VPN – usually not for teams)
Game master:      http://localhost:8000/host   password: energiewende   (this computer only)
Other devices cannot connect?  See "Network tips" in the README (firewall, private network).
```
Den Teams die `/join`-Adresse des WLAN-Adapters geben (oder den QR-Code in der Lobby zeigen).

### Sprache: Deutsch oder Englisch
Unten links auf jeder Seite schaltet der Knopf **EN / DE** die Sprache um – pro Browser, ohne Internet. Die Wahl
bleibt gespeichert (auch nach Neuladen oder in der nächsten Stufe). Deutsche und englische Teams können im selben
Spiel spielen; Zahlen und Wertung sind identisch. Die Spielleitung (Host-Seite) hat ihre eigene Wahl.

---

## Ablauf einer Spielrunde

1. **Spielleitung** öffnet `/host` auf dem Beamer-Rechner, meldet sich an und stellt im
   **Einstellungsfenster** Timer, Simulationen pro Stufe, Budget, Zufall usw. ein
   (als Vorlage speicherbar) → „Spiel erstellen“.
2. Die Lobby zeigt **QR-Code und PIN**. Teams scannen mit dem Handy oder öffnen `/join`, geben
   die PIN und einen Teamnamen ein.
3. **Stufe starten** → Bauphase mit Timer. Teams setzen Bau-Token, entscheiden über bestehende
   Kraftwerke, setzen Einfluss-Token ein und testen mit dem **Dispatch-Simulator**
   (normales Wetterjahr, begrenzte Anzahl Versuche). Rechts zeigt „Dein Kraftwerkspark“ die gesicherte
   Leistung: Puffer nur mit Kraftwerken (grau), dazu zwei Ampeln: mit Speicher & Flex (grün ab +10 %)
   und mit Speicher, Flex & Leitungen (grün ab +30 %). Details hinter dem Info-Knopf. Auf Wasserstoff
   umgerüstete Gasturbinen zählen nur so weit als gesichert, wie Import und voller Speicher sie zwei
   Wochen lang versorgen (Dauer der kalten Dunkelflaute im Spiel). Der Simulator zeigt beim zweiten Test,
   was sich gegenüber dem letzten Test geändert hat. Bei 2 Minuten Restzeit erscheint ein Hinweis, der Timer blinkt.
   Auf dem Beamer zeigt die Spielleitung zu Beginn jeder Stufe groß, was neu ist (Verbrauch, Kohle, Ziele).
4. Die Spielleitung beendet die Bauphase (nichts passiert automatisch). Dann werden für **alle
   Teams dieselben** Zufallsereignisse gezogen (Wetterjahr, Nachfrage, Katastrophe) und jedes
   Portfolio simuliert.
5. **Ergebnisse**: Rangliste, Punkte je Kategorie, Strommix- und Kraftwerkspark-Vergleich auf dem Beamer; jedes
   Team sieht seine Details mit Diagramm und Sprungmarken (Dunkelflaute, Versorgungslücke …) und einen
   💡 Tipp: was am meisten Punkte gekostet hat (z. B. größte CO₂-Quelle) und was sich in der nächsten Stufe ändert.
6. Nächste Stufe – insgesamt 4 Stufen: JETZT–2030, 2031–2035, 2036–2040, 2041–2045.

Wenn ein Handy die Seite neu lädt, kommt das Team automatisch zurück. Spielstände werden laufend
im Ordner `games/` gespeichert und nach einem Neustart fortgesetzt.

### Punkte (je Stufe 0–5 pro Kategorie, max. 60)
- **Versorgungssicherheit:** Stunden mit Versorgungslücke (5 Punkte bei ≤ 3 h/Jahr – üblicher
  Zuverlässigkeitsstandard in Nachbarländern).
- **Klimaschutz:** zwei Bedingungen, es zählt der **schlechtere** Wert:
  1. **Anteil CO₂-frei** wie in der amtlichen Statistik (EEG-Ziel): CO₂-freie Erzeugung in Deutschland
     inkl. exportiertem Ökostrom, gemessen am Verbrauch; Importe zählen nicht, Abfall zur Hälfte
     (= (Verbrauch + Export − Import − fossile Erzeugung) ÷ Verbrauch, höchstens 100 %).
  2. **CO₂-Ausstoß in Deutschland** (Mt/Jahr, territorial wie im Klimaschutzgesetz; Exporte gleichen
     nichts aus). Die Grenzen sinken jede Stufe bis fast null: 5 Punkte bei ≤ 70 / 45 / 25 / 8 Mt
     (2030: KSG-Energiewirtschaft 108 Mt, davon Strom grob 70; 2035: G7-Zusage „Stromsektor weitgehend
     dekarbonisiert“; 2040: Kohleausstieg 2038 und Ende der Zertifikate im EU-Emissionshandel um
     2039/40; 2045: Netto-Treibhausgasneutralität – die Abfallverbrennung allein stößt ~5 Mt aus).
  5 Punkte nur bei Erreichen der politischen Ziele (Anteil 2030: 80 %, 2045 nahe 100 %).
- **Bezahlbarkeit:** Erzeugungs- und Speicherkosten in €/MWh – **ohne Netze, Umlagen, Steuern**,
  daher nicht mit dem Strompreis vergleichbar (Investitionen als Annuität, fixe und variable
  Betriebskosten, Brennstoff, CO₂-Preis, Importkosten abzüglich Exporterlösen, Kreditaufschlag,
  Kosten gekaufter Einfluss-Token). Bestehende Anlagen gehen nur mit ihren fixen Betriebskosten ein.
  Der Schaden durch nicht gedeckten Bedarf (10.000 €/MWh) wird angezeigt, zählt aber
  nicht mehr für die Kosten-Punkte – eine Versorgungslücke kostet nur die Versorgungs-Punkte, nicht doppelt.
- **Abzug:** −2 Punkte je neuer Technologie mit gesellschaftlicher Gegenreaktion in der letzten Stufe.
- Angezeigt (nicht bepunktet): CO₂-Emissionen kumuliert in Gt, CO₂ je kWh (g/kWh, wie beim UBA; zusätzlich
  mit dem CO₂ der Importe).

### Spielmechanik
- **Bau-Token**: 1 Token = 10 Mrd. € Investition (einstellbar), 18 / 18 / 17 / 17 je Stufe – vorne
  mehr, wie der reale Investitionsbedarf (eigene Schätzung für den EEG-Ausbaupfad bei Wind und PV: ≈ 204 / 157 / 120 / 74 Mrd. €).
  Wie viele GW ein Token bringt, folgt aus den realen Kosten (z. B. ~7 GW Onshore-Wind, ~21 GW
  Freiflächen-PV). Kredit-Token möglich (+20 % Kosten).
- **Bestehende Kraftwerke** (Kohle, Gas, Biomasse; Laufwasser läuft fest mit): per Schieberegler weiterbetreiben
  oder endgültig stilllegen. Kohle folgt dem gesetzlichen Ausstiegspfad (KVBG) und läuft, solange sie
  behalten wird, in jeder Stunde mit mindestens 15 % Leistung (Fernwärme, Tagebau-Logistik); sie kann
  ihre Leistung nur um 40 % pro Stunde ändern. Wer z. B. 10 GW behält, erzeugt mindestens ~13 TWh
  Kohlestrom im Jahr.
- **Feste Anlagen** (weder ausbaubar noch stilllegbar, mit festem Fahrplan): Pumpspeicher 9,9 GW
  (Energieinhalt für ca. 6 h bei voller Leistung), bestehende Großbatterien 3,7 GW (ca. 1 h, altern bis
  2045 weg; Heimspeicher nicht berücksichtigt),
  Abfallverbrennung 1,9 GW (läuft immer, halb erneuerbar), Öl & sonstige Konventionelle 4,8 GW
  (Öl, Grubengas u. a.; bis 2035, ab 2040 stillgelegt) sowie Netz- und Kapazitätsreserve (11,1 GW bis 2035, danach
  3,6 GW; nur bei Knappheit, 500 €/MWh).
- **Altanlagen**: Die heutigen Wind- und Solaranlagen gehen nach und nach vom Netz (Wind an Land
  ~25 Jahre: 2045 noch ~30 %; Sonne ~30 Jahre: 2045 noch ~65 %; Offshore ~30 Jahre). Die Kacheln
  zeigen den Rückgang zur nächsten Stufe. Alte Windanlagen haben ein schwächeres Profil (Ø ~20 %
  onshore, ~34 % offshore); neue ~26–29 % bzw. ~45 % (Offshore inkl. Abschattung im Windpark-Cluster).
- **Neue Gasturbinen** (H₂-ready, ~41 % Wirkungsgrad, ~640 €/kW): günstige Reserve, stoßen CO₂ aus.
- **Batteriespeicher**: Energieinhalt für 4 Stunden bei voller Leistung (4 GWh je GW), ~92 % Wirkungsgrad für Laden und Entladen zusammen.
- **Biomasse-Flexibilisierung**: mehr Leistung bei gleicher Jahresenergie, höchstens bis zur
  dreifachen Leistung der weiterbetriebenen Biomasse.
- **Wasserstoff** – drei Bausteine, getrennt ausbaubar: **Elektrolyse** (~1.900 €/kW, 62–68 %,
  25 Jahre, ~5 GW je Token; läuft nur mit dem deutschen Ökostrom-Überschuss der jeweiligen Stunde – grüner
  Wasserstoff, kein Import- oder Fossilstrom), **Wasserstoff-Speicher** in Salzkavernen (~2,7 €/kWh H₂, 100 Jahre,
  ~3,7 TWh H₂ je Token) und **auf H₂ umgerüstete Gasturbinen** (Umrüstung der neu gebauten
  Gasturbinen, 120 €/kW ohne Token, ~41 %; danach nur noch Wasserstoff, kein Erdgas). Rundweg ≈ 25 %.
  Umrüsten geht erst, wenn Elektrolyse und Speicher gebaut oder in der Stufe eingeplant sind (oder Import
  über das Wasserstoff-Netz kommt). Freischaltung jeweils ab der Folgestufe: „Demonstrationsprogramm
  Wasserstoff“ → Elektrolyse, Speicher, Umrüstung; „Wasserstoff-Netz & Import“ → Speicher, Umrüstung,
  Import (keine Elektrolyse). Das Spiel zeigt an,
  wie viele Tage der volle Speicher die H₂-Turbinen versorgt, und warnt, wenn ein Baustein fehlt.
- **Import & Export**: Kuppelleitungen zu den Nachbarländern (25 / 28 / 32 / 35 GW, angelehnt an den
  TYNDP; mit „Netzausbau Europa“ +10 GW). Verfügbarkeit, Preis und CO₂ der Importe folgen stündlich der
  Knappheit bei den Nachbarn (aus deren Wetter und Verbrauch, TYNDP): bei europaweiter Dunkelflaute ist
  Import knapp und teuer. Die Nachbarn kaufen deutschen Strom, wenn sie ihn brauchen, und nehmen
  jederzeit bis zu 8 GW Überschuss ab (Wasserkraft-Speicher, Elektrolyse, Wärme). Ein Speicher im Ausland
  (Wasserkraft in Norwegen und den Alpen) nimmt Überschuss auf und gibt ihn später teurer zurück.
  Importkosten und Exporterlöse gehen in die Kosten ein; das CO₂ der Importe wird getrennt
  angezeigt (nicht in der deutschen Bilanz, wie in der amtlichen Statistik).
- **Flexible Verbraucher** (nur mit Einfluss-Token, ab der Folgestufe): E-Autos und Wärmepumpen
  verschieben Verbrauch innerhalb eines Tages (5 / 10 / 15 / 20 GW, Energie für 4 h Volllast), die Industrie verzichtet bei
  Knappheit (4 / 6 / 8 / 10 GW, 300 €/MWh, höchstens 200 Volllaststunden im Jahr). Ohne Token gibt es
  keine Lastflexibilität.
- **Einfluss-Token**: Klimaresilienz, Beschleunigte Innovation, Demonstrationsprogramm Wasserstoff,
  Wasserstoff-Netz & Import (Pipeline-H₂ für umgerüstete Gasturbinen ab 2035: 15 / 30 / 45 GW H₂
  ≈ 6 / 12 / 18 GW Strom, zu 140 / 125 / 110 €/MWh H₂ ≈ 4,2 / 3,8 / 3,3 €/kg – Annahme im Rahmen der Studien EWI 2025 und Fraunhofer HYPAT 2024, siehe DATA_SOURCES.md), Akzeptanz & Teilhabe,
  Netzausbau Europa, Flexible Verbraucher – je einmal pro Spiel. 2 zu Beginn; weitere kosten je 2 Bau-Token, das Geld
  zählt als Programmkosten in den Erzeugungs- und Speicherkosten.
- **Spielregeln & Überblick**: Seite `/regeln` (Link auf der Startseite, Tab „Regeln“ bei den Teams,
  Knopf „Regeln zeigen“ bei der Spielleitung für den Beamer). Alle Zahlen kommen aus den aktuellen
  Spiel-Einstellungen.
- **Zufall**: Wetterjahr (normal 2008: 60 %, schwierig 1995: 30 %, extremer Winter 2009: 10 % –
  einstellbar), Nachfrageschock, Katastrophen
  (Sturm/Hochwasser, kalte Dunkelflaute, Hitze/Dürre) – für alle Teams gleich. Gegenreaktionen
  und Lerneffekte sind teamspezifisch.

---

## Daten und Annahmen

Alle Zahlen stehen mit Quelle in `ptz/config/assumptions.yaml`; Spielparameter in
`ptz/config/game_default.yaml`.

| Bereich | Quelle |
|---|---|
| Wind- und PV-Profile (stündlich) | ENTSO-E PECD 3.1 (TYNDP 2024), Marktgebiet DE00, Wetterjahre 1995/2008/2009 |
| Stromnachfrage (stündlich) | TYNDP 2024 Demand Profiles (National Trends 2030/2040, Distributed Energy 2050), skaliert auf 560 / 760 / 875 / 925 TWh Nettostromverbrauch ohne Elektrolyse (2030 nach Monitoringbericht 2025, danach mittlerer Pfad NEP 2037/2045), zuzüglich 6–7 % für Netzverluste und Kraftwerkseigenverbrauch (≈ 600 / 810 / 930 / 980 TWh); der CO₂-freie Anteil bezieht sich darauf, wie die amtliche Statistik auf den Bruttostromverbrauch |
| Import/Export | Synthetischer Nachbarmarkt aus TYNDP-Nachfrage und PECD-Wetter der 12 Nachbar-Marktgebiete und dem EU-Strommix (TYNDP 2024 NT+); Leitungskapazität nach den TYNDP-NT+-Ergebnissen, Speicher und Abnahme der Nachbarn auf die TYNDP-Handelsmengen kalibriert (siehe Abschnitt 8 des Hintergrund-Dokuments in `docs/`) |
| Gasturbinen, Elektrolyse, Kaverne | PyPSA technology-data (OCGT, electrolysis, hydrogen storage underground), EUR 2025 |
| Laufwasser | TYNDP 2024 Hydro Inflows (PEMMDB DE00) |
| Brennstoff- und CO₂-Preise | TYNDP 2024 Commodity Prices (IEA WEO 2022 APS), von EUR 2021 auf EUR 2025 mit Faktor 1,18 (Destatis VPI). CO₂-Preis 134 / 154 / 173 / 186 €/t – deutlich über dem Niveau im Herbst 2026 (EU-Emissionshandel ~80–90 €/t) |
| Emissionsfaktoren | TYNDP 2024 CO₂ emission factors |
| Technologiekosten | PyPSA technology-data (überwiegend Danish Energy Agency Technology Data), EUR 2025 |
| Startkapazitäten | Bundesnetzagentur Kraftwerksliste (Stand 26.06.2026); PV-Aufteilung 66 % Dach / 34 % Freifläche (Solarserver, Feb. 2026) |
| PV-Erträge | Ein PECD-Profil; Freiflächen-PV ×1,10 (~975 Volllaststunden), Dach-PV wie PECD (~885 h) – Annahme nach Fraunhofer ISE „Aktuelle Fakten zur PV“ |
| Pumpspeicher | Kraftwerksliste (9,9 GW inkl. ans deutsche Netz angeschlossener Anlagen in AT/LU); Speicherdauer 6 h ist eine Annahme |

**Wetterjahre:** Die Auswertung `ptz/data/processed/weather_check.csv` zeigt: 2008 ist das
mildeste der drei Jahre, 1995 schwieriger (weniger Wind, größtes Defizit über zwei Wochen), 2009 extrem (sehr kalter
Winter, schwächste Windwoche, höchste Spitzen- und Residuallast – kommt etwa alle 10–20 Jahre vor). Daher: normal 2008 (60 %), schwierig 1995 (30 %), extrem 2009 (10 %). Der Simulator in der
Bauphase rechnet immer mit dem Normaljahr.

**Vereinfachungen** (gehören in die Nachbesprechung): Deutschland als ein Knoten ohne
Netzengpässe; Nachbarländer nur als vereinfachter Markt (kein vollständiges Europamodell);
perfekte Voraussicht des Modells über das Jahr; keine Kraftwerkseinsatzplanung mit
An/Aus-Zuständen (Kohle als ein Block: mind. 15 % Leistung, Rampe 40 % pro Stunde); flexible Verbraucher nur über den Einfluss-Token und kleiner als in den offiziellen Studien; Biomasse kann ihre
Jahresenergie frei verschieben; bestehende Gaskraftwerke altern nicht; ein PV-Profil für Dach- und
Freiflächenanlagen; Speicherwasserkraft (0,8 GW) nicht modelliert; Wasserstoff nur für Strom
(Wasserstoff-Import nur über die Einflusskarte mit fester Leistung und festem Preis, kein Bedarf von Industrie oder Verkehr); Heimspeicher nicht modelliert;
Kohle als ein Block (Braun- und Steinkohle zusammen). Mit „ASSUMPTION“ markierte Werte
in `assumptions.yaml` sind eigene Setzungen ohne direkte Quelle.

**Versorgungslücken:** Ein lineares Modell mit Speichern kann eine Lücke beliebig auf Stunden
verteilen. Damit die Zahl der Lücken-Stunden eindeutig ist, wird nicht gedeckter Bedarf in
Stunden mit höherem Verbrauch minimal (bis 1 %) billiger bewertet – die Lücke landet dann in
den Spitzenstunden. Die Kosten rechnen immer mit den vollen 10.000 €/MWh.

### Daten neu erzeugen
Rohdaten (TYNDP/PECD/BNetzA, ca. 1,4 GB) in den Ordner `raw/` legen, dann:
```bash
uv run --frozen python -m ptz.data.build_inputs               # alles (Nachbarmarkt dauert einige Minuten)
uv run --frozen python -m ptz.data.build_inputs --neighbours  # nur die Import/Export-Daten
```
Die verarbeiteten Daten (`ptz/data/processed/`, ca. 1 MB) liegen bereits bei – für das Spiel sind
die Rohdaten nicht nötig.

---

## Netzwerk-Tipps für den Spieltag
- **Andere Geräte kommen nicht rein?** Häufigste Ursachen:
  1. Windows-Firewall-Abfrage beim ersten Start abgebrochen → Windows blockiert Python. Abhilfe: Systemsteuerung →
     Windows Defender Firewall → „Eine App oder ein Feature durch die Windows Defender Firewall zulassen“ →
     „Einstellungen ändern“ → bei den Einträgen „python“ (aus dem uv-Ordner im Benutzerprofil) **Privat** ankreuzen.
  2. WLAN ist in Windows als „Öffentlich“ eingestuft. Abhilfe (nur im eigenen WLAN/Hotspot): Einstellungen →
     Netzwerk und Internet → Eigenschaften des Netzwerks → „Privates Netzwerk“. Das Startskript warnt, wenn ein
     Netzwerk „Öffentlich“ ist.
  3. Falsche Adresse: VPN aktiv oder virtuelle Adapter (WSL, Hyper-V, VirtualBox). Die
     Startausgabe zeigt jetzt zu jeder Adresse den Adapternamen – die WLAN-Adresse nehmen.
  4. Das WLAN selbst trennt Geräte voneinander (Gäste-WLAN, eduroam, Firmen-WLAN) → eigener
     Router oder Handy-Hotspot.
- Am zuverlässigsten: **eigener Router oder Handy-Hotspot**, Spielleitungs-Rechner und alle Teams
  im selben WLAN. Uni-/Gäste-WLANs (z. B. eduroam) blockieren oft Verbindungen zwischen Geräten.
- Windows fragt beim ersten Start nach der Firewall → „Zugriff zulassen“ **nur für private
  Netzwerke** (nicht „öffentlich“). Notfalls in PowerShell als Administrator:
  `New-NetFirewallRule -DisplayName "Zero45 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Profile Private -Action Allow`
  und nach dem Spieltag wieder entfernen: `Remove-NetFirewallRule -DisplayName "Zero45 8000"`.
  Das eigene Hotspot-/Router-Netz in Windows als „Privat“ einstufen.
- Rechenleistung: Ein Jahr rechnet je Team ca. 10–20 s; mehrere Teams laufen parallel auf allen
  Prozessorkernen (je Rechnung bis ~1,2 GB Arbeitsspeicher; das Spiel begrenzt die Zahl paralleler
  Rechnungen automatisch nach Kernen und freiem Speicher). Ein Laptop mit 8 Kernen und 16 GB schafft
  ~10 Teams in wenigen Minuten.

## Sicherheit (Kurzfassung)
- **Installation:** Alle rund 100 Pakete kommen von PyPI und werden mit `uv sync --frozen` exakt in den
  Versionen aus `uv.lock` installiert, jeweils mit SHA-256-Prüfsumme. Es werden nur fertige
  Pakete (Wheels) installiert – erzwungen durch `no-build = true` in `pyproject.toml` –, nichts wird beim Installieren
  kompiliert oder ausgeführt. Fehlte einmal ein fertiges Paket, bricht das Setup mit einer Fehlermeldung ab. Neue
  Versionen werden erst nach einer Woche übernommen (`exclude-newer` in `pyproject.toml`), weil
  manipulierte Veröffentlichungen meist innerhalb weniger Tage entdeckt werden. Alles landet im
  Projektordner (`.venv`) bzw. bei uv im Benutzerordner – keine Administratorrechte nötig. uv
  nutzt ein eigenes Python (nicht das aus dem Microsoft Store oder ein vorhandenes System-Python).
- **Teilnehmende** brauchen nur einen Browser. Die Seiten laden nichts aus dem Internet (alle
  Skripte kommen vom Spielleitungs-Rechner), es wird nichts heruntergeladen oder installiert und
  kein Konto angelegt. Es wird nur ein Sitzungs-Cookie gespeichert (Teamzugehörigkeit und Sprache).
  Teamnamen werden bereinigt und überall als Text angezeigt.
- **Spielleitungs-Rechner:** Der Server stellt nur die Spielseiten bereit (keine Dateifreigabe,
  keine Uploads, keine Befehle). Im Netzwerk-Modus ist er für alle im selben WLAN erreichbar –
  deshalb ein eigenes Hotspot-/Router-Netz nutzen und den Server nach dem Spiel beenden (Strg+C).
- Die Verbindung ist unverschlüsselt (HTTP im lokalen Netz). Daher keine echten Namen oder
  Passwörter als Teamnamen verwenden.

## Für Entwickler
```
ptz/config/      Annahmen mit Quellen (assumptions.yaml), Spielparameter (game_default.yaml)
ptz/data/        Datenpipeline (build_inputs.py) und verarbeitete Daten
ptz/engine/      PyPSA-Modell (model.py): Dispatch, Import/Export, Kennzahlen
ptz/game/        Spielregeln, Zufall, Alterung, Punkte (core.py); runner.py (Simulation, Hinweise)
ptz/server/      Web-Oberfläche (NiceGUI): app.py (Start, Seiten), runtime.py (Spielstände,
                 parallele Simulation), host.py, player.py, rules.py (/regeln), charts.py, theme.py
ptz/i18n.py      Sprachumschaltung: tr("deutscher Text {0}", wert) übersetzt beim Anzeigen; Englisch in i18n_en.py
                 (Schlüssel = deutscher Originaltext). Neuer Text → in i18n_en.py ergänzen; tests/test_i18n.py
                 meldet fehlende Übersetzungen.
ptz/calibration/ Bots zur Kalibrierung
tests/           uv run --frozen pytest
```
Code-Kommentare, Konsolenausgaben, Setup- und Netzwerk-Skripte sind englisch; die Web-Oberfläche schaltet zwischen Deutsch und Englisch um. Die deutschen Texte in `tr("…")` und in den Beschriftungstabellen sind die Schlüssel der Übersetzung und dürfen nicht übersetzt werden.
Das Python-Paket heißt aus historischen Gründen `ptz` (Arbeitstitel des Projekts).

### Pakete aktualisieren (Sicherheitsupdates)
`uv.lock` legt jede Paketversion fest. Eine spätere Installation bekommt daher genau dieselben Versionen – auch wenn es
inzwischen neuere mit Sicherheitsfixes gibt. Aktualisiert wird nur, wenn das Repository aktualisiert wird:

- **Benachrichtigen lassen:** Im GitHub-Repository *Dependabot alerts* einschalten (Settings → Advanced Security).
  GitHub liest `uv.lock` und schickt eine E-Mail, wenn eine genutzte Version eine bekannte Lücke hat.
- **Aktualisieren** (bei einer Warnung oder z. B. vor einer neuen Workshop-Saison):
  1. In `pyproject.toml` das Datum bei `exclude-newer` auf etwa eine Woche vor heute setzen (Wartezeit gegen frisch
     veröffentlichte, möglicherweise manipulierte Versionen) und die Ausnahme bei `exclude-newer-package` entfernen
     oder anpassen.
  2. `uv lock --upgrade`, danach `uv sync --frozen` und `uv run --frozen pytest` ausführen.
  3. Eine Stufe probespielen, dann `pyproject.toml` und `uv.lock` committen.

  Gibt es eine neue Version nur als Quellcode (kein fertiges Paket), bricht `uv sync` wegen `no-build = true` mit einem
  Fehler ab; dann die bisherige Version behalten (z. B. nur die übrigen Pakete mit `uv lock --upgrade-package <Paket>`
  aktualisieren).

---

## Einordnung: was das Spiel ist und was nicht

Zero45 ist ein **Lernspiel**. Es macht die Zielkonflikte der Energiewende greifbar – Versorgungssicherheit,
Klimaschutz und Kosten, unter Unsicherheit – und soll Gespräche anstoßen. Es ist **keine Prognose und keine
politische Empfehlung**. Bei der Besprechung der Ergebnisse bitte beachten:

- **Kosten** umfassen nur Erzeugung und Speicher. Netze, Steuern, Umlagen, Netzentgelte und Vertriebsmargen fehlen –
  die €/MWh des Spiels sind daher nicht mit Strompreisen vergleichbar, und die Gesamtkosten liegen weit unter
  Gesamtsystem-Studien.
- **Modell:** Deutschland als ein Knoten („Kupferplatte“, keine Netzengpässe), perfekte Voraussicht über das Jahr, ein
  Wetterjahr je Stufe, keine Kraftwerksausfälle. Kraftwerke (außer Kohle) starten sofort und haben keine
  Mindestleistung. Versorgungslücken sind daher eher eine Untergrenze.
- **Vereinfacht:** Nachbarländer als ein synthetischer Markt, Wasserstoff nur für Strom, flexible Verbraucher nur per
  Einflusskarte, keine Kernkraft und kein CCS (siehe „Vereinfachungen“ oben).
- **Daten und Annahmen** spiegeln amtliche Quellen mit Stand 2026 (TYNDP 2024, BNetzA, NEP, PyPSA technology-data) und
  werden altern. Alle Werte mit Quelle stehen in `ptz/config/assumptions.yaml`; eigene Setzungen sind mit
  `ASSUMPTION` markiert.
- **Zufall** (Wetterjahr, Nachfrage, Katastrophen, Gegenreaktionen) entscheidet in einem einzelnen Spiel viel – wie in
  der Wirklichkeit.

Ausführlicher (Kalibrierung, Vergleich mit offiziellen Szenarien, Fragen und Antworten): Hintergrund-Dokument in `docs/`.

## Haftungsausschluss

Zero45 wird **„wie besehen“ und ohne jede Gewährleistung** bereitgestellt (siehe Abschnitte 11 und 12 der
[GPL](LICENSE)). **Die Nutzung erfolgt auf eigene Gefahr.** Soweit gesetzlich zulässig, haften die Autoren nicht für
Schäden aus der Nutzung, insbesondere nicht für Schäden an Computern oder anderen Geräten, Datenverlust, Netzwerk- oder
Sicherheitsprobleme oder Entscheidungen auf Grundlage der Spielergebnisse. Die Haftung für Vorsatz und grobe
Fahrlässigkeit sowie für Schäden an Leben, Körper und Gesundheit bleibt unberührt.

Insbesondere:
- Das Setup installiert Software (uv, eine Python-Version und rund 100 Pakete von PyPI) in den Spielordner und in Ihr
  Benutzerprofil. Administratorrechte sind nicht nötig.
- Wer von Hand eine Firewall-Regel anlegt (siehe „Netzwerk-Tipps“), entfernt sie nach dem Spieltag wieder.
- Während das Spiel läuft, erreichen alle Geräte im selben Netzwerk die Spielseiten, und die Verbindung ist
  unverschlüsselt. Eigenen Router oder Hotspot nutzen und den Server nach dem Spiel beenden.
- Eine Simulation braucht je Prozess bis ~1,2 GB Arbeitsspeicher; auf schwachen Laptops die Zahl der Prozesse
  verringern (`-Workers`).
- Die Ergebnisse des Spiels sind keine Rechts-, Finanz-, Anlage- oder Politikberatung.

## Credits

- **Originalspiel:** „Path to Zero – The Electricity Decarbonization Game“, entworfen von
  [Jesse D. Jenkins](https://mae.princeton.edu/people/faculty/jenkins), entwickelt vom
  [Princeton ZERO Lab](https://zero.lab.princeton.edu/) und der Princeton Research Software Engineering Group,
  <https://github.com/PrincetonZEROLab/Path-to-Zero>, Lizenz GPL-2.0.
  Zero45 übernimmt das Spielkonzept (Stufen, Bau-Token, Einfluss-Token („shaping tokens“), gesellschaftliche
  Gegenreaktion, gemeinsamer Zufall, Wertung nach Zuverlässigkeit, sauberem Strom und Kosten, die Stufen-Übersicht)
  sowie einige Mechaniken und Parameter (Risikostufen der Gegenreaktion, Wirkung der Karten Resilienz und Akzeptanz).
  Neu sind der Code (Python statt Julia), das Strommarktmodell, die deutschen und europäischen Daten, der
  Nachbarmarkt, Wasserstoff, die Web-Oberfläche und die Zweisprachigkeit. Code des Originals wurde nicht kopiert.
- **Daten:** ENTSO-E und ENTSOG (TYNDP 2024, PECD 3.1, CC BY 4.0), Bundesnetzagentur (Kraftwerksliste, Datenlizenz
  Deutschland), PyPSA technology-data, Danish Energy Agency u. a. – Details und Quellenangaben in
  [DATA_SOURCES.md](DATA_SOURCES.md).
- **Software:** [PyPSA](https://pypsa.org), [linopy](https://github.com/PyPSA/linopy), [HiGHS](https://highs.dev),
  [NiceGUI](https://nicegui.io), [Plotly](https://plotly.com/python/), pandas, NumPy, [uv](https://docs.astral.sh/uv/)
  und viele weitere Open-Source-Pakete (Lizenzen MIT, BSD, Apache, MPL).
- **Entwicklung:** Manuel Lerschmacher. Code und Dokumente entstanden mit umfangreicher Unterstützung des
  KI-Assistenten Claude (Anthropic); Konzeptentscheidungen, Tests in Workshops und Verantwortung liegen beim Autor.

## Zitieren

Wer Zero45 in Lehre oder Forschung nutzt, zitiert es bitte – GitHub zeigt dafür den Knopf „Cite this repository“
(aus [CITATION.cff](CITATION.cff)). Bitte auch das Originalspiel „Path to Zero“ und die Datenquellen nennen.

## Lizenz

Copyright (C) 2026 Manuel Lerschmacher

Dieses Programm ist freie Software. Sie können es unter den Bedingungen der GNU General Public License, wie von der
Free Software Foundation veröffentlicht, weitergeben und/oder verändern, entweder gemäß Version 2 der Lizenz oder
(nach Ihrer Wahl) jeder späteren Version. Die Veröffentlichung erfolgt in der Hoffnung, dass es nützlich ist, aber
OHNE IRGENDEINE GARANTIE, sogar ohne die implizite Garantie der MARKTREIFE oder der VERWENDBARKEIT FÜR EINEN
BESTIMMTEN ZWECK. Details in der [GNU General Public License](LICENSE) (verbindlich ist der englische Lizenztext).

Kurz: Zero45 darf frei genutzt, kopiert, verändert und weitergegeben werden, auch kommerziell. Wer eine veränderte
Fassung weitergibt, muss sie wieder unter der GPL mit Quellcode weitergeben und Urheber- und Credit-Hinweise erhalten.

Die Daten in `ptz/data/processed/` behalten ihre eigenen Lizenzen (CC BY 4.0 und Datenlizenz Deutschland –
Namensnennung); siehe [DATA_SOURCES.md](DATA_SOURCES.md).
