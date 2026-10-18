# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""English texts, keyed by the German original (see ptz/i18n.py). Placeholders {0}, {1:.1f} must match."""
# flake8: noqa
EN = {
    "Beitritt gerade nicht möglich (Spiel wird berechnet oder ist beendet).":
        "Joining is not possible right now (the game is being calculated or has ended).",
    "Das Spiel ist voll.":
        "The game is full.",
    "Team {0}":
        "Team {0}",
    "Die Bauphase ist geschlossen.":
        "The build phase is closed.",
    "Umrüstung braucht Wasserstoff: Elektrolyse und Speicher (gebaut oder in dieser Stufe geplant) oder Import über das Wasserstoff-Netz.":
        "Conversion needs hydrogen: electrolysis and storage (built or planned in this stage) or imports via the hydrogen grid.",
    "Erst Bau-Token zurücknehmen.":
        "Remove build tokens first.",
    "Bereits eingesetzt.":
        "Already used.",
    "Kein Einfluss-Token frei.":
        "No influence token left.",
    "Wetterjahr {0} ({1})":
        "Weather year {0} ({1})",
    "Nachfrage {0} %":
        "Demand {0} %",
    "Gesellschaftliche Gegenreaktion – in dieser Stufe gesperrt":
        "Public backlash – blocked in this stage",
    "Erst nach Demonstrationsprogramm Wasserstoff oder Wasserstoff-Netz (ab der Folgestufe)":
        "Only after the Hydrogen demonstration programme or Hydrogen grid (from the following stage)",
    "Keine Bau-Token mehr übrig.":
        "No build tokens left.",
    "Nicht genug Bau-Token.":
        "Not enough build tokens.",
    "Nichts zurückzunehmen.":
        "Nothing to take back.",
    "Umgerüstete Gasturbinen ohne Wasserstoff-Speicher liefern keinen Strom.":
        "Converted gas turbines without hydrogen storage produce no electricity.",
    "Ohne Elektrolyse bleibt der Wasserstoff-Speicher leer – die H₂-Turbinen liefern nichts.":
        "Without electrolysis the hydrogen storage stays empty – the H₂ turbines produce nothing.",
    "Der Import reicht nur für {0:.0f} GW eurer H₂-Turbinen gleichzeitig – für Spitzen braucht ihr zusätzlich einen Speicher.":
        "The imports cover only {0:.0f} GW of your H₂ turbines at the same time – for peaks you also need storage.",
    "Elektrolyse ohne Speicher: Der Wasserstoff kann nicht aufbewahrt werden.":
        "Electrolysis without storage: the hydrogen cannot be kept.",
    "Ein Speicher allein nützt nichts – es fehlen Elektrolyse und umgerüstete Gasturbinen.":
        "Storage alone is useless – electrolysis and converted gas turbines are missing.",
    "Wasserstoff wird erzeugt und gespeichert, aber nicht verstromt – es fehlen umgerüstete Gasturbinen.":
        "Hydrogen is produced and stored but not turned into electricity – converted gas turbines are missing.",
    "{0} (ab Woche {1})":
        "{0} (from week {1})",
    "Keine Katastrophe":
        "No disaster",
    "Alle drei Ziele erreicht – stark!":
        "All three goals reached – great!",
    "Am meisten Punkte kostete die Versorgung: {0} Stunden mit Lücke, größte {1} GW. ":
        "Security of supply cost the most points: {0} hours with a supply gap, largest {1} GW. ",
    ", CO₂-Ziel ≤ {0} Mt":
        ", CO₂ target ≤ {0} Mt",
    ", Ziel ≥ {0} % CO₂-frei":
        ", target ≥ {0} % CO₂-free",
    "Nächste Stufe ({0}–{1}): Verbrauch {2}{3} %{4}, Kohle höchstens {5} GW.":
        "Next stage ({0}–{1}): demand {2}{3} %{4}, coal at most {5} GW.",
    "Erst nach dem Demonstrationsprogramm Wasserstoff (ab der Folgestufe)":
        "Only after the Hydrogen demonstration programme (from the following stage)",
    "Flexibilisierung höchstens bis zur dreifachen Leistung der weiterbetriebenen Biomasse":
        "Flexibilisation at most up to three times the capacity of the biomass you keep",
    "Eure H₂-Turbinen ({0} GW) hatten nur für etwa {1} GW genug Wasserstoff – mehr Speicher oder Import, oder weniger umrüsten.":
        "Your H₂ turbines ({0} GW) only had enough hydrogen for about {1} GW – more storage or imports, or convert less.",
    "Mehr gesicherte Leistung einplanen – Gasturbinen, Biomasse-Flexibilisierung oder Speicher.":
        "Plan more firm capacity – gas turbines, biomass flexibilisation or storage.",
    " Der Simulator rechnet nur ein normales Jahr – plant Puffer für schwierige Jahre (Ampeln grün).":
        " The simulator only calculates a normal year – plan a buffer for difficult years (green traffic lights).",
    "Betroffen: ":
        "Affected: ",
    "Investitionen":
        "Investment",
    "fixe Betriebskosten":
        "fixed operating costs",
    "Brennstoff, CO₂ & Importe":
        "fuel, CO₂ & imports",
    "Am meisten Punkte kostete die Bezahlbarkeit: {0} €/MWh, für 5 Punkte höchstens {1} €. Größter Block: {2}. {3}":
        "Affordability cost the most points: {0} €/MWh, for 5 points at most {1} €. Largest block: {2}. {3}",
    "Am meisten Punkte kostete der Klimaschutz – es zählte der Ausstoß: {0} Mt, für 5 Punkte höchstens {1} Mt. Größte Quelle: {2} ({3} Mt). {4}":
        "Climate protection cost the most points – emissions counted: {0} Mt, for 5 points at most {1} Mt. Largest source: {2} ({3} Mt). {4}",
    "Am meisten Punkte kostete der Klimaschutz – es zählte der Anteil: {0} % CO₂-frei, für 5 Punkte mindestens {1} %. Importe ({2} TWh) und fossiler Strom zählen nicht – mehr eigener Ökostrom hilft, Exporte zählen mit.":
        "Climate protection cost the most points – the share counted: {0} % CO₂-free, for 5 points at least {1} %. Imports ({2} TWh) and fossil power do not count – more domestic green power helps, exports count.",
    "Günstige Technologien (Wind an Land, Freiflächen-PV) liefern am meisten Strom je Token – teure Anlagen nur, wo sie gebraucht werden.":
        "Cheap technologies (onshore wind, ground-mounted PV) deliver the most electricity per token – use expensive plants only where they are needed.",
    "Nicht mehr gebrauchte Altanlagen kosten Betriebskosten – stilllegen prüfen.":
        "Old plants you no longer need cost operating costs – consider retiring them.",
    "Erdgas, Kohle, CO₂-Preis und Importe sind teuer – mehr Wind und Sonne senken sie.":
        "Natural gas, coal, the CO₂ price and imports are expensive – more wind and sun reduce them.",
    "PV":
        "PV",
    "{0}. {1}, {2}:00 Uhr":
        "{1} {0}, {2}:00",
    "Spitzenlast":
        "Peak load",
    "Dunkelflaute (höchste Residuallast)":
        "Dark doldrums (highest residual load)",
    "Wenigster Wind":
        "Least wind",
    "Meiste Sonne":
        "Most sun",
    "Meiste Abregelung":
        "Most curtailment",
    "Größte Versorgungslücke":
        "Largest supply gap",
    "Meiste Batterienutzung":
        "Most battery use",
    "Meiste Reserve-Einsätze":
        "Most reserve dispatch",
    "Meiste Wasserstoff-Verstromung":
        "Most hydrogen power",
    "Katastrophenzeitraum":
        "Disaster period",
    "Erdgas {0} %":
        "Natural gas {0} %",
    "Kohle {0} %":
        "Coal {0} %",
    "Fossile Kraftwerke lieferten {0} % des Stroms ({1}) – {2} Mt CO₂.":
        "Fossil power plants supplied {0} % of the electricity ({1}) – {2} Mt CO₂.",
    "Praktisch kein fossiler Strom in diesem Jahr.":
        "Practically no fossil power this year.",
    "Import {0} TWh ({1} % des Verbrauchs, zählt nicht als erneuerbar), Export {2} TWh (exportierter Ökostrom zählt mit).":
        "Imports {0} TWh ({1} % of demand, not counted as renewable), exports {2} TWh (exported green power counts).",
    "{0} TWh Wind- und Sonnenstrom wurden abgeregelt ({1} % des möglichen) – Speicher oder Elektrolyse könnten ihn nutzen.":
        "{0} TWh of wind and solar power were curtailed ({1} % of what was possible) – storage or electrolysis could use it.",
    "Fixe Betriebskosten":
        "Fixed operating costs",
    "Brennstoff, CO₂ & variable Kosten":
        "Fuel, CO₂ & variable costs",
    "Größter Kostenblock: {0} mit {1} Mrd. €/Jahr (von {2} Mrd. € gesamt).":
        "Largest cost block: {0} with €{1} bn/year (of €{2} bn in total).",
    "Größte Versorgungslücke: {0} GW am {1} – Wind und Sonne lieferten da nur {2} GW bei {3} GW Verbrauch.":
        "Largest supply gap: {0} GW on {1} – wind and sun only supplied {2} GW with {3} GW demand.",
    "Keine Versorgungslücke. Knappste Stunde: {0} – {1} GW mussten steuerbare Kraftwerke, Speicher und Importe liefern.":
        "No supply gap. Tightest hour: {0} – {1} GW had to come from dispatchable plants, storage and imports.",
    "Sonstige/Reserve/Abfall {0} %":
        "Other/reserve/waste {0} %",
    "Spiel-PIN":
        "Game PIN",
    "Erneut versuchen":
        "Try again",
    "Du bist bereits als Team „{0}“ angemeldet.":
        "You have already joined as team “{0}”.",
    "Passwort":
        "Password",
    "⚡ Zero45 – Energiewende-Spiel":
        "⚡ Zero45 – energy transition game",
    "Baue ein Stromsystem für Deutschland bis 2045: zuverlässig, klimaneutral und bezahlbar.":
        "Build an electricity system for Germany up to 2045: reliable, climate-neutral and affordable.",
    "Spielregeln & Überblick":
        "Rules & overview",
    "⚡ Zero45 – Beitreten":
        "⚡ Zero45 – Join",
    "Spiel {0} | {1} Teams angemeldet":
        "Game {0} | {1} teams joined",
    "Teamname":
        "Team name",
    "Beitreten":
        "Join",
    "Neues Spiel":
        "New game",
    "Abmelden":
        "Log out",
    "Einem Spiel beitreten":
        "Join a game",
    "Weiter":
        "Continue",
    "Kein laufendes Spiel mit dieser PIN gefunden.":
        "No running game with this PIN found.",
    "Weiter zum Spiel":
        "Continue to the game",
    "Als anderes Team beitreten":
        "Join as a different team",
    "Hinweis: Das Spiel läuft schon – neue Teams starten in der aktuellen Stufe.":
        "Note: the game is already running – new teams start in the current stage.",
    "Das Einzelspiel ist im Netzwerk-Modus ausgeschaltet.":
        "Single-player mode is switched off in network mode.",
    "Zum alleine Spielen den Server im lokalen Modus starten (start_spiel -Local bzw. --local).":
        "To play alone, start the server in local mode (start_spiel -Local or --local).",
    "Zur Startseite":
        "Back to the start page",
    "Dein Teamname":
        "Your team name",
    "Die Spielleitung ist nur am Spielleitungs-Rechner erreichbar.":
        "The game master page is only available on the game master's computer.",
    "Spielleitung – Anmeldung":
        "Game master – login",
    "Falsches Passwort":
        "Wrong password",
    "Anmelden":
        "Log in",
    "Mein Team":
        "My team",
    "Laufende Spiele fortsetzen":
        "Continue running games",
    "Spiel leiten":
        "Run a game",
    "Für die Spielleitung am Hauptrechner/Beamer.":
        "For the game master on the main computer/projector.",
    "Zur Spielleitung":
        "To the game master page",
    "Einzelspiel":
        "Single player",
    "Alleine spielen, ohne Spielleitung.":
        "Play alone, without a game master.",
    "Einzelspiel starten":
        "Start single player",
    "PIN {0} | Stufe {1} | {2} Teams":
        "PIN {0} | Stage {1} | {2} teams",
    "Tag im Jahr (Tagesmittel)":
        "Day of the year (daily mean)",
    "Tag der Woche (Woche {0})":
        "Day of the week (week {0})",
    "Stufe {0}":
        "Stage {0}",
    "Punkte":
        "Points",
    "Verbrauch":
        "Demand",
    "Wasserstoffspeicher (TWh H₂, links)":
        "Hydrogen storage (TWh H₂, left)",
    "Pumpspeicher (GWh, rechts)":
        "Pumped hydro (GWh, right)",
    "Batterien (GWh, rechts)":
        "Batteries (GWh, right)",
    "Bitte nur Zahlen, durch Kommas getrennt":
        "Numbers only, separated by commas",
    "Team":
        "Team",
    "Status":
        "Status",
    "Token übrig":
        "Tokens left",
    "Simulationen":
        "Simulations",
    "+1 Simulation":
        "+1 simulation",
    "Team entfernen":
        "Remove team",
    "<th>Stufe {0}</th>":
        "<th>Stage {0}</th>",
    "Stufe":
        "Stage",
    "Jahr":
        "Year",
    "Punkte Versorgung":
        "Points supply",
    "Punkte Klimaschutz":
        "Points climate",
    "davon Anteil":
        "of which share",
    "davon Ausstoß":
        "of which emissions",
    "Punkte Kosten":
        "Points costs",
    "Lücken-Stunden":
        "Gap hours",
    "CO2-frei %":
        "CO2-free %",
    "Erzeugungs- und Speicherkosten €/MWh":
        "Generation and storage costs €/MWh",
    "CO2 Mt":
        "CO2 Mt",
    "g CO2/kWh":
        "g CO2/kWh",
    "g CO2/kWh mit Import-CO2":
        "g CO2/kWh incl. import CO2",
    "Gegenreaktion":
        "Backlash",
    "⏱ Zeit um":
        "⏱ Time is up",
    "Spiel-Einstellungen":
        "Game settings",
    "Katastrophen":
        "Disasters",
    "Gesellschaftliche Gegenreaktionen":
        "Public backlash",
    "Vorlage „{0}“ gespeichert":
        "Preset “{0}” saved",
    "Teams ({0})":
        "Teams ({0})",
    "Während der Berechnung nicht möglich.":
        "Not possible during the calculation.",
    "Team „{0}“ endgültig entfernen?":
        "Remove team “{0}” permanently?",
    "Rangliste (alle bisherigen Stufen)":
        "Ranking (all stages so far)",
    "<table class=\"ptz-table\" style=\"font-size:1.1rem\"><thead><tr><th>Team</th>{0}<th>Gesamt</th><th>CO₂ Gt</th></tr></thead><tbody>{1}</tbody></table>":
        "<table class=\"ptz-table\" style=\"font-size:1.1rem\"><thead><tr><th>Team</th>{0}<th>Total</th><th>CO₂ Gt</th></tr></thead><tbody>{1}</tbody></table>",
    "Punkte je Kategorie":
        "Points by category",
    "Stufe {0} im Detail":
        "Stage {0} in detail",
    "€/MWh = {0} ({1}).{2}g CO₂/kWh: heute ~{3} (UBA {4}, wie dort ohne Importe).":
        "€/MWh = {0} ({1}).{2}g CO₂/kWh: today ~{3} (UBA {4}, like there without imports).",
    "Strommix der Teams (TWh)":
        "Electricity mix of the teams (TWh)",
    "Kraftwerkspark der Teams (GW)":
        "Power plant fleet of the teams (GW)",
    "Installierte Leistung in dieser Stufe, inkl. Bestand. Fahrt mit der Maus über die Balken für die Werte; ein Klick auf die Legende blendet eine Technologie aus.":
        "Installed capacity in this stage, incl. existing plants. Hover over the bars for the values; a click on the legend hides a technology.",
    "Laden":
        "Load",
    "Ablauf":
        "Schedule",
    "Budget & Token":
        "Budget & tokens",
    "Zufall & Ereignisse":
        "Chance & events",
    "Punkteschwellen (Fortgeschritten)":
        "Point thresholds (advanced)",
    "Werte für 5, 4, 3, 2, 1 Punkte, kommagetrennt.":
        "Values for 5, 4, 3, 2, 1 points, comma-separated.",
    "Versorgungslücke (Stunden)":
        "Supply gap (hours)",
    "Als Vorlage speichern unter":
        "Save as preset under",
    "Bitte einen Namen eingeben (Buchstaben, Ziffern, Leerzeichen, - und _)":
        "Please enter a name (letters, digits, spaces, - and _)",
    "Speichern":
        "Save",
    "Regeln zeigen":
        "Show rules",
    "Ergebnisse als CSV":
        "Results as CSV",
    "Gesamt":
        "Total",
    "Versorgung":
        "Supply",
    "Klimaschutz":
        "Climate",
    "Kosten":
        "Costs",
    "Abzug":
        "Deduction",
    "CO₂ Gt":
        "CO₂ Gt",
    "Lücken-h":
        "Gap h",
    "CO₂-frei %":
        "CO₂-free %",
    "€/MWh":
        "€/MWh",
    "CO₂ Mt":
        "CO₂ Mt",
    "g CO₂/kWh":
        "g CO₂/kWh",
    "… mit Import-CO₂":
        "… incl. import CO₂",
    "Standard":
        "Default",
    "Vorlage laden":
        "Load preset",
    "Simulationen pro Stufe":
        "Simulations per stage",
    "Max. Teams":
        "Max. teams",
    "Zufalls-Seed (leer = zufällig)":
        "Random seed (empty = random)",
    "Wert eines Bau-Tokens (Mrd. €)":
        "Value of a build token (bn €)",
    "Max. Kredit-Token pro Stufe":
        "Max. credit tokens per stage",
    "Einfluss-Token zu Beginn":
        "Influence tokens at the start",
    "Wahrsch. schwieriges Jahr (1995)":
        "Prob. difficult year (1995)",
    "Wahrsch. extremer Winter (2009)":
        "Prob. extreme winter (2009)",
    "Nachfrageschock (Std.-Abw.)":
        "Demand shock (std. dev.)",
    "Stufe 1 starten":
        "Start stage 1",
    "Ereignisse Stufe {0}: ":
        "Events stage {0}: ",
    "Timer Stufe {0} (Min., 0 = aus)":
        "Timer stage {0} (min, 0 = off)",
    "Bau-Token Stufe {0}":
        "Build tokens stage {0}",
    "Katastrophe Stufe {0}":
        "Disaster stage {0}",
    "CO₂-frei % Stufe {0}":
        "CO₂-free % stage {0}",
    "Kosten €/MWh Stufe {0}":
        "Costs €/MWh stage {0}",
    "Spiel erstellen":
        "Create game",
    "⚡ Zero45 – Energiewende":
        "⚡ Zero45 – energy transition",
    "Stufe {0}/{1}{2}{3}{4}{5}":
        "Stage {0}/{1}{2}{3}{4}{5}",
    "Annahmen {0}: Verbrauch {1} TWh{2}CO₂-Preis {3} €/t{4}Erdgas {5} €/MWh":
        "Assumptions {0}: demand {1} TWh{2}CO₂ price {3} €/t{4}natural gas {5} €/MWh",
    "Warte auf Teams …":
        "Waiting for teams …",
    "Bauphase beenden & Jahr simulieren":
        "End build phase & simulate the year",
    "+2 Min.":
        "+2 min",
    "+5 Min.":
        "+5 min",
    "Beitreten: QR-Code scannen oder Adresse öffnen":
        "Join: scan the QR code or open the address",
    "Entfernen":
        "Remove",
    "Abbrechen":
        "Cancel",
    "CO₂ Mt Stufe {0}":
        "CO₂ Mt stage {0}",
    "Berechne Stufe … {0}/{1} Teams":
        "Calculating stage … {0}/{1} teams",
    "{0} Punkte":
        "{0} points",
    "Spiel beenden & Siegerehrung":
        "End game & award ceremony",
    "Stufe {0} starten":
        "Start stage {0}",
    "🏆 Spiel beendet":
        "🏆 Game over",
    "Punkte {0}":
        "Points {0}",
    "Lücke {0}":
        "Gap {0}",
    "CO₂ {0}":
        "CO₂ {0}",
    "CO₂-frei {0}":
        "CO₂-free {0}",
    "Kosten {0}":
        "Costs {0}",
    "Für {0} P.: {1} (5 P.: {2})":
        "For {0} pts: {1} (5 pts: {2})",
    " <span style=\"color:#b45309\">→ {0} GW ab {1}</span>":
        " <span style=\"color:#b45309\">→ {0} GW from {1}</span>",
    "<div class=\"ptz-card\" style=\"padding:8px 14px;background:#f5f3ff\"><b>Alle {0} Teams in dieser Stufe (Durchschnitt):</b> {1}{2}<b>Euer Platz in dieser Stufe: {3} von {4}</b> ({5} Punkte)</div>":
        "<div class=\"ptz-card\" style=\"padding:8px 14px;background:#f5f3ff\"><b>All {0} teams in this stage (average):</b> {1}{2}<b>Your rank in this stage: {3} of {4}</b> ({5} points)</div>",
    "{0} {1} (gleich)":
        "{0} {1} (same)",
    "✔ Ziel erreicht":
        "✔ Goal reached",
    "Für 5 P.: {0}":
        "For 5 pts: {0}",
    "{0} h mit Lücke":
        "{0} h with a gap",
    "{0}{1}nicht gedeckt: {2} TWh":
        "{0}{1}unserved: {2} TWh",
    "{0} % | {1} Mt":
        "{0} % | {1} Mt",
    "{0} €/MWh":
        "{0} €/MWh",
    "Großbatterien":
        "Large batteries",
    "Öl & Sonstige":
        "Oil & other",
    "Reserve":
        "Reserve",
    "{0} {1} → {2} GW":
        "{0} {1} → {2} GW",
    "Keine Änderung in der nächsten Stufe":
        "No change in the next stage",
    "🔓 Freigeschaltet ab der nächsten Stufe (Einfluss-Karte „{0}“).":
        "🔓 Unlocked from the next stage (influence card “{0}”).",
    "🔒 Gesperrt – freischalten über die Einfluss-Karten „Demonstrationsprogramm Wasserstoff“ (eigene Elektrolyse) oder „Wasserstoff-Netz & Import“. Wirkt ab der Folgestufe.":
        "🔒 Locked – unlock with the influence cards “Hydrogen demonstration programme” (own electrolysis) or “Hydrogen grid & imports”. Takes effect from the following stage.",
    "<div class=\"ptz-card w-full\" style=\"padding:10px 14px;background:#eff6ff\"><b>Im Vergleich zum Test von {0} Uhr:</b> {1}</div>":
        "<div class=\"ptz-card w-full\" style=\"padding:10px 14px;background:#eff6ff\"><b>Compared with the test at {0}:</b> {1}</div>",
    "{0}Anteil {1} P., Ausstoß {2} P.":
        "{0}share {1} pts, emissions {2} pts",
    "Tipp: Doppelklick auf einen Eintrag in der Legende zeigt nur diese Gruppe; Einfachklick blendet sie aus.":
        "Tip: double-click an entry in the legend to show only this group; a single click hides it.",
    "Kosten: {0} {1}":
        "Costs: {0} {1}",
    "pro Token":
        "per token",
    "Nächste Stufe: ":
        "Next stage: ",
    "<b>{0}</b> von {1} weiterbetreiben":
        "Keep <b>{0}</b> of {1} running",
    "Voller Speicher: {0} TWh H₂ ≈ {1} TWh Strom – reicht für <b>{2} Tage</b> Volllast eurer H₂-Turbinen ({3}).":
        "Full storage: {0} TWh H₂ ≈ {1} TWh electricity – enough for <b>{2} days</b> of your H₂ turbines at full load ({3}).",
    "Wasserstoff-Import über das Netz: bis {0} H₂ zu {1} €/MWh (≈ {2} Strom).":
        "Hydrogen imports via the grid: up to {0} H₂ at {1} €/MWh (≈ {2} electricity).",
    "Simulierte Stromversorgung":
        "Simulated power supply",
    "Pkt Versorgung":
        "Pts supply",
    "Pkt Klimaschutz":
        "Pts climate",
    "Pkt Kosten":
        "Pts costs",
    "CO₂ Mt/Jahr":
        "CO₂ Mt/year",
    "CO₂ kumuliert Gt":
        "CO₂ cumulative Gt",
    "Anteil":
        "share",
    "Ausstoß":
        "emissions",
    " → es zählt der {0}":
        " → the {0} counts",
    "Warum?":
        "Why?",
    "Ganzes Jahr":
        "Whole year",
    "Woche wählen":
        "Choose week",
    "<b>Kraftwerke</b> ({0}): nur steuerbare Kraftwerke – sie liefern auch in einer tagelangen Dunkelflaute. Wind und Sonne zählen nicht, Laufwasser halb. Auf Wasserstoff umgerüstete Gasturbinen zählen nur so weit, wie Import und voller Speicher sie 2 Wochen lang versorgen (Dauer der kalten Dunkelflaute im Spiel).<br><br><b>Speicher & Flex</b> (bis {1}): Batterien, Pumpspeicher und flexible Verbraucher helfen bei kurzen Spitzen (Abend), sind aber nach einigen Stunden erschöpft. Ampel: grün ab +10 %, gelb ab 0 %.<br><br><b>Leitungen</b> (bis {2}): Importe – aber nur, wenn die Nachbarn Strom übrig haben; bei europaweiter Flaute fehlen sie. Ampel deshalb strenger: grün ab +30 %, gelb ab +15 %. Testläufe: Wer bei beiden Ampeln grün ist, hat auch im extremen Winter kaum Lücken.<br><br>Vergleich mit der Spitzenlast im Normaljahr – in schwierigen Jahren liegt sie höher.":
        "<b>Power plants</b> ({0}): dispatchable plants only – they deliver even in dark doldrums lasting several days. Wind and sun do not count, run-of-river counts half. Gas turbines converted to hydrogen only count as far as imports and a full storage can supply them for 2 weeks (the length of the cold dark doldrums in the game).<br><br><b>Storage & flex</b> (up to {1}): batteries, pumped hydro and flexible demand help with short peaks (evening) but run out after a few hours. Traffic light: green from +10 %, yellow from 0 %.<br><br><b>Interconnectors</b> (up to {2}): imports – but only if the neighbours have power to spare; in a Europe-wide lull they are missing. That is why this light is stricter: green from +30 %, yellow from +15 %. Test runs: whoever is green on both lights has hardly any gaps even in the extreme winter.<br><br>Compared with the peak load in a normal year – in difficult years it is higher.",
    "<div class=\"text-sm\" style=\"color:#b45309\">H₂-Turbinen: {0}, davon gesichert {1} – der Wasserstoff reicht nicht für 2 Wochen Volllast.</div>":
        "<div class=\"text-sm\" style=\"color:#b45309\">H₂ turbines: {0}, of which firm {1} – the hydrogen does not last for 2 weeks at full load.</div>",
    " (−{0} % durch eigenen Lerneffekt)":
        " (−{0} % from your own learning effect)",
    "Bisher gebaut":
        "Built so far",
    "Altanlagen":
        "Existing plants",
    "Auslastung":
        "Capacity factor",
    "Auslastung der Altanlagen: Ø {0} % (kleinere, ältere Anlagen).":
        "Capacity factor of the existing plants: Ø {0} % (smaller, older turbines).",
    "<br><span class=\"ptz-sub\">{0} gehen durch den Kohleausstieg vom Netz</span>":
        "<br><span class=\"ptz-sub\">{0} go offline because of the coal phase-out</span>",
    "<br><span style=\"color:#b91c1c;font-weight:700\">{0} werden endgültig stillgelegt</span>":
        "<br><span style=\"color:#b91c1c;font-weight:700\">{0} will be retired permanently</span>",
    "Voller Speicher: {0} TWh H₂ ≈ {1} TWh Strom.":
        "Full storage: {0} TWh H₂ ≈ {1} TWh electricity.",
    "Umgerüstete Gasturbinen verbrennen nur noch Wasserstoff – aus eurem Speicher oder dem Wasserstoff-Netz (CO₂-frei), kein Erdgas mehr. Umrüstung {0} €/kW, ohne Bau-Token. Möglich, sobald Elektrolyse und Speicher gebaut oder in dieser Stufe eingeplant sind – oder Wasserstoff über das Netz kommt (Einfluss-Karte).":
        "Converted gas turbines burn only hydrogen – from your storage or the hydrogen grid (CO₂-free), no more natural gas. Conversion {0} €/kW, no build tokens needed. Possible as soon as electrolysis and storage are built or planned in this stage – or hydrogen comes via the grid (influence card).",
    "Annahmen {0}: Verbrauch {1} TWh (inkl. Netzverluste, ohne Elektrolyse){2}CO₂-Preis {3} €/t{4}1 Bau-Token = {5} Mrd. €":
        "Assumptions {0}: demand {1} TWh (incl. grid losses, excl. electrolysis){2}CO₂ price {3} €/t{4}1 build token = €{5} bn",
    "Bestehende Kraftwerke":
        "Existing power plants",
    "Weiterbetreiben kostet fixe Betriebskosten. Stilllegen ist endgültig.":
        "Keeping them costs fixed operating costs. Retiring is final.",
    "Feste Anlagen":
        "Fixed plants",
    "Gibt es in jedem Portfolio – nicht ausbaubar, nicht stilllegbar.":
        "Part of every portfolio – cannot be expanded or retired.",
    "Finanzierung":
        "Financing",
    "Kredit: bis zu {0} zusätzliche Bau-Token, +{1} % Kosten.":
        "Credit: up to {0} extra build tokens, +{1} % costs.",
    "Jede Maßnahme kann einmal im Spiel gewählt werden; bis zum Ende der Bauphase änderbar.":
        "Each measure can be chosen once per game; you can change it until the end of the build phase.",
    "Gekaufte Einfluss-Token zählen als Programmkosten in den Erzeugungs- und Speicherkosten.":
        "Bought influence tokens count as programme costs in the generation and storage costs.",
    "Der Simulator testet dein aktuelles Portfolio mit einem normalen Wetterjahr – ohne Nachfrageschock und ohne Katastrophe. Die echte Stufe kann schwieriger werden.":
        "The simulator tests your current portfolio with a normal weather year – without a demand shock and without a disaster. The real stage can be harder.",
    "Simulieren ({0} von {1} übrig)":
        "Simulate ({0} of {1} left)",
    "Stromversorgung {0}":
        "Power supply {0}",
    "Gesamtpunkte: {0}{1}CO₂ gesamt: {2} Gt":
        "Total points: {0}{1}CO₂ in total: {2} Gt",
    "Wetterjahr {0}: {1}":
        "Weather year {0}: {1}",
    "Stromverbrauch {0}{1} % gegenüber der Prognose":
        "Electricity demand {0}{1} % compared with the forecast",
    "Risiko {0}":
        "Risk {0}",
    "Kennzahlen":
        "Key figures",
    "Größte Lücke":
        "Largest gap",
    "CO₂ je kWh Strom":
        "CO₂ per kWh of electricity",
    "{0} g (heute ~{1} g, UBA {2})":
        "{0} g (today ~{1} g, UBA {2})",
    "Abregelung":
        "Curtailment",
    "Elektrolyse":
        "Electrolysis",
    "Wasserstoff-Import":
        "Hydrogen imports",
    "Import":
        "Imports",
    "Export":
        "Exports",
    "{0} im Detail":
        "{0} in detail",
    "Nicht mit dem Strompreis vergleichbar ({0}). Der Schaden durch Versorgungslücken (10.000 €/MWh) zählt nur bei der Versorgung, nicht bei den Kosten-Punkten.":
        "Not comparable with the electricity price ({0}). The damage from supply gaps (10,000 €/MWh) only counts for security of supply, not for the cost points.",
    "Stromerzeugung (TWh)":
        "Electricity generation (TWh)",
    "<div style=\"max-width:min(340px,100%);line-height:0\">{0}</div>":
        "<div style=\"max-width:min(340px,100%);line-height:0\">{0}</div>",
    "Übersicht: Stufen & deine Punkte":
        "Overview: stages & your points",
    "Dein Kraftwerkspark":
        "Your power plant fleet",
    "Leistung zu Beginn der Stufe → mit deinen Entscheidungen":
        "Capacity at the start of the stage → with your decisions",
    "Gesichert / Spitzenlast":
        "Firm / peak load",
    "Puffer Kraftwerke":
        "Buffer power plants",
    "+ Speicher & Flex":
        "+ storage & flex",
    "+ Leitungen":
        "+ interconnectors",
    "Altanlagen (1 h)":
        "Existing plants (1 h)",
    "Bereits umgerüstet: {0}{1}in dieser Stufe: {2}":
        "Already converted: {0}{1}in this stage: {2}",
    "Ohne Bau-Token; danach nur noch Wasserstoff statt Erdgas.":
        "No build tokens needed; afterwards hydrogen only instead of natural gas.",
    "Die Bauphase ist geschlossen. Warte auf die Spielleitung.":
        "The build phase is closed. Wait for the game master.",
    "Einfluss-Token kaufen ({0} Bau-Token = {1} Mrd. €)":
        "Buy influence token ({0} build tokens = €{1} bn)",
    "Berechnung läuft … (ca. 5–15 Sekunden)":
        "Calculating … (about 5–15 seconds)",
    "Ergebnis der Simulation von {0} Uhr":
        "Simulation result from {0}",
    "Noch keine Ergebnisse.":
        "No results yet.",
    "Abzug Gegenreaktionen: −{0}":
        "Deduction for backlash: −{0}",
    "Gesellschaftliche Gegenreaktion: ":
        "Public backlash: ",
    "Lerneffekte: ":
        "Learning effects: ",
    "Du bist im Spiel. Die Spielleitung startet gleich Stufe 1. Schau dir solange die Regeln an:":
        "You are in the game. The game master will start stage 1 soon. Meanwhile, have a look at the rules:",
    "Noch 2 Minuten – jetzt testen und „Fertig melden“!":
        "2 minutes left – test now and “Mark as ready”!",
    "Investitionen (Rate)":
        "Investment (annual rate)",
    "Brennstoff, CO₂, variabel":
        "Fuel, CO₂, variable",
    "Kreditaufschlag":
        "Credit surcharge",
    "Summe pro Jahr":
        "Total per year",
    "&nbsp;&nbsp;&nbsp;↳ davon Bestand":
        "&nbsp;&nbsp;&nbsp;↳ of which existing",
    "<div class=\"text-sm\">Wasserstoff-Speicher: <b>{0}</b><br>{1}</div>":
        "<div class=\"text-sm\">Hydrogen storage: <b>{0}</b><br>{1}</div>",
    "Gesicherte Leistung":
        "Firm capacity",
    "Investition diese Stufe":
        "Investment this stage",
    "{0} Mrd. €":
        "€{0} bn",
    "Kredit-Token":
        "Credit tokens",
    "Noch möglich":
        "Still possible",
    "Wirkungsgrad {0} % (Strom → Wasserstoff). Läuft nur, wenn Wind, Sonne und Laufwasser in Deutschland mehr liefern als gebraucht wird – kein Import- oder Fossilstrom.":
        "Efficiency {0} % (electricity → hydrogen). Runs only when wind, sun and run-of-river in Germany supply more than is needed – no imported or fossil power.",
    "Behaltene Kohle läuft immer mit mindestens 15 % Leistung (Fernwärme, Tagebau) und ist träge – auch wenn Wind und Sonne genug liefern. Hohe CO₂-Emissionen.":
        "Coal you keep always runs at least at 15 % (district heating, mines) and is slow – even when wind and sun supply enough. High CO₂ emissions.",
    "Kohleausstieg: in dieser Stufe höchstens {0}.":
        "Coal phase-out: at most {0} in this stage.",
    "Energie begrenzt (~{0} TWh/Jahr); Flexibilisierung bis zur dreifachen Leistung.":
        "Energy limited (~{0} TWh/year); flexibilisation up to three times the capacity.",
    "⚠️ Gegenreaktion: muss in dieser Stufe stillgelegt werden":
        "⚠️ Backlash: must be retired in this stage",
    "Neubau":
        "New build",
    "{0} Token = +{1}":
        "{0} tokens = +{1}",
    "Kein Neubau in dieser Stufe.":
        "No new build in this stage.",
    "Umrüstung auf H₂":
        "Conversion to H₂",
    "Endgültige Stilllegung (eure Entscheidung)":
        "Permanent retirement (your decision)",
    "Kohleausstieg (Gesetz): {0} gehen vom Netz.":
        "Coal phase-out (law): {0} go offline.",
    "⚠️ Noch {0} Bau-Token übrig – sie verfallen am Ende der Stufe.":
        "⚠️ {0} build tokens left – they expire at the end of the stage.",
    "ℹ️ {0} Einfluss-Token noch frei (bleiben für spätere Stufen).":
        "ℹ️ {0} influence tokens still free (kept for later stages).",
    "Zurück":
        "Back",
    "Gasturbinen auf Wasserstoff umrüsten":
        "Convert gas turbines to hydrogen",
    "🔒 Möglich nach Demonstrationsprogramm Wasserstoff oder Wasserstoff-Netz (ab der Folgestufe)":
        "🔒 Possible after the Hydrogen demonstration programme or Hydrogen grid (from the following stage)",
    "Strom kommt aus den Nachbarländern, wenn er dort übrig und günstig ist – bei europaweiter Dunkelflaute ist er knapp und teuer. Importe zählen nicht als erneuerbar, exportierter Ökostrom zählt mit.":
        "Power comes from the neighbouring countries when they have spare cheap power – in Europe-wide dark doldrums it is scarce and expensive. Imports do not count as renewable, exported green power counts.",
    "Kauf zurücknehmen":
        "Undo purchase",
    "Abzug für Gegenreaktionen in der letzten Stufe: −{0} Punkte":
        "Deduction for backlash in the last stage: −{0} points",
    "Füllstand der Speicher":
        "Storage levels",
    "Diese Stufe: {0} Punkte":
        "This stage: {0} points",
    "Details ansehen":
        "See details",
    "Spiel starten":
        "Start game",
    "Das Jahr wird simuliert … ({0}/{1} Teams)":
        "Simulating the year … ({0}/{1} teams)",
    "Dazu: Schaden durch Versorgungslücken":
        "Plus: damage from supply gaps",
    "Bau-Token: {0} von {1} übrig":
        "Build tokens: {0} of {1} left",
    "Läuft nur":
        "Runs only",
    "bei Ökostrom-Überschuss":
        "with surplus green power",
    "Braucht":
        "Needs",
    "Speicher + umgerüstete Gasturbinen":
        "Storage + converted gas turbines",
    "Je TWh Wasserstoff kommen in den Gasturbinen ≈ {0} TWh Strom zurück.":
        "Each TWh of hydrogen gives back ≈ {0} TWh of electricity in the gas turbines.",
    "Gasturbine mit {0} % Wirkungsgrad; jederzeit startbereit.":
        "Gas turbine with {0} % efficiency; ready to start at any time.",
    "Einfluss-Maßnahmen: ":
        "Influence measures: ",
    "Erst Elektrolyse und Speicher einplanen (oder Wasserstoff-Netz) – dann umrüsten.":
        "First plan electrolysis and storage (or the hydrogen grid) – then convert.",
    "Wasserstoff":
        "Hydrogen",
    "Anzeigen":
        "Show",
    "Laufwasser":
        "Run-of-river hydro",
    "{0}{1}klein, gleichmäßig, CO₂-frei":
        "{0}{1}small, steady, CO₂-free",
    "Pumpspeicher":
        "Pumped hydro",
    "{0}{1}ca. {2} h":
        "{0}{1}approx. {2} h",
    "Großbatterien (Bestand)":
        "Large batteries (existing)",
    "{0}{1}{2}1-h-Speicher, altern bis 2045 weg":
        "{0}{1}{2}1-hour storage, retired by 2045",
    "Abfallverbrennung":
        "Waste incineration",
    "{0}{1}läuft immer, halb erneuerbar":
        "{0}{1}always running, half renewable",
    "Öl & sonstige Konventionelle":
        "Oil & other conventional",
    "{0}{1}{2}fossil, ab Stufe 3 stillgelegt":
        "{0}{1}{2}fossil, retired from stage 3",
    "Netz- & Kapazitätsreserve":
        "Grid & capacity reserve",
    "{0}{1}{2}nur bei Knappheit, fossil":
        "{0}{1}{2}only when scarce, fossil",
    "Kuppelleitungen":
        "Interconnectors",
    "Nächste Stufe":
        "Next stage",
    "Mehr Leitungen: Einfluss-Karte „Netzausbau Europa“.":
        "More interconnectors: influence card “European grid expansion”.",
    "Einfluss-Token frei: {0}":
        "Influence tokens free: {0}",
    "Stufe {0} ({1}): ":
        "Stage {0} ({1}): ",
    " – in der nächsten Stufe gesperrt bzw. Stilllegung.":
        " – blocked or retired in the next stage.",
    "📉 Lerneffekte: ":
        "📉 Learning effects: ",
    "Stufe {0} ({1}): Das Jahr ist gelaufen":
        "Stage {0} ({1}): the year is over",
    " (−{0} Abzug)":
        " (−{0} deduction)",
    "Stufe abschließen & berechnen":
        "Close stage & calculate",
    "Elektrolyse oder Wasserstoff-Netz + umgerüstete Gasturbinen":
        "Electrolysis or hydrogen grid + converted gas turbines",
    "Erst neue Gasturbinen bauen – dann umrüsten.":
        "Build new gas turbines first – then convert.",
    "🔒 Elektrolyse (eigener Wasserstoff) nur mit der Einfluss-Karte „Demonstrationsprogramm Wasserstoff“ – ab der Folgestufe.":
        "🔒 Electrolysis (own hydrogen) only with the influence card “Hydrogen demonstration programme” – from the following stage.",
    "Import & Export":
        "Imports & exports",
    "⚠️ Gesellschaftliche Gegenreaktion bei: ":
        "⚠️ Public backlash against: ",
    "Das Jahr wird simuliert …":
        "Simulating the year …",
    "davon auf H₂":
        "of which on H₂",
    "✔ Fertig gemeldet":
        "✔ Marked as ready",
    "Doch noch ändern":
        "Make changes after all",
    "Fertig melden":
        "Mark as ready",
    "✔ eingesetzt in Stufe {0}":
        "✔ used in stage {0}",
    "Stufe abschließen?":
        "Close the stage?",
    "Ja, berechnen":
        "Yes, calculate",
    "Weiter zur nächsten Stufe":
        "On to the next stage",
    "Spiel beenden":
        "End game",
    "Spiel beendet – {0} Punkte":
        "Game over – {0} points",
    "Neues Einzelspiel":
        "New single-player game",
    "✔ Gewählt":
        "✔ Chosen",
    "Verschieben + Verzicht: ":
        "Shifting + curtailing: ",
    "Gewählt – zurücknehmen":
        "Chosen – undo",
    "Einsetzen":
        "Use",
    "Fertig melden?":
        "Mark as ready?",
    "Ja, fertig":
        "Yes, ready",
    "✔ Aktiv":
        "✔ Active",
    "Kohle höchstens {0}. Einfluss-Token früh einsetzen.":
        "Coal at most {0}. Use influence tokens early.",
    "Großer Sprung: Verbrauch +{0} %, Spitzenlast +{1} GW – und nur noch {2} Kohle.":
        "Big jump: demand +{0} %, peak load +{1} GW – and only {2} of coal left.",
    "Kohle und Öl sind weg, Reserve nur noch {0}. Viele alte Windräder gehen vom Netz.":
        "Coal and oil are gone, reserve only {0}. Many old wind turbines go offline.",
    "5 P.":
        "5 pts",
    "So läuft eine Stufe":
        "How a stage works",
    "Euer Bildschirm":
        "Your screen",
    "Ziele & Punkte":
        "Goals & points",
    "Jede Stufe gibt bis zu 5 Punkte pro Ziel. Die Ziele werden von Stufe zu Stufe strenger.":
        "Each stage gives up to 5 points per goal. The goals get stricter from stage to stage.",
    "Die vier Stufen":
        "The four stages",
    "Der Verbrauch wächst durch Wärmepumpen, E-Autos und Industrie.":
        "Demand grows because of heat pumps, electric cars and industry.",
    "Token":
        "Tokens",
    "Neue Anlagen":
        "New plants",
    "Werte für {0}. 1 Bau-Token = {1} Mrd. €.":
        "Values for {0}. 1 build token = €{1} bn.",
    "Alte Kraftwerke & feste Anlagen":
        "Old power plants & fixed plants",
    "Alte Kraftwerke könnt ihr behalten oder stilllegen – Stilllegen ist endgültig, Behalten kostet Betriebskosten.":
        "You can keep or retire old power plants – retiring is final, keeping them costs operating costs.",
    "Zufall & Risiken":
        "Chance & risks",
    "Wetter, Verbrauch und Katastrophen sind für alle Teams gleich. Lerneffekte und Proteste treffen jedes Team einzeln.":
        "Weather, demand and disasters are the same for all teams. Learning effects and protests hit each team individually.",
    "Tipps für den Start":
        "Tips for the start",
    "Wie rechnet das Modell?":
        "How does the model calculate?",
    "Glossar – Begriffe einfach erklärt":
        "Glossary – terms explained simply",
    "Kohle höchstens":
        "Coal at most",
    "CO₂-Preis":
        "CO₂ price",
    "CO₂-frei (5 Punkte)":
        "CO₂-free (5 points)",
    "Ihr plant als Team den Strom für Deutschland bis 2045 – in **vier Stufen**. In jeder Stufe baut ihr neue Anlagen und entscheidet über alte Kraftwerke. Dann rechnet der Computer ein ganzes Jahr Stunde für Stunde durch. Punkte gibt es für drei Ziele: **⚡ immer genug Strom**, **🌿 Klimaschutz** (sauberer Strom und wenig CO₂) und **💶 möglichst günstig** – je bis zu 5 Punkte pro Stufe, insgesamt höchstens {0}.\n\n**Kurz gesagt:** Deckt den Bedarf zu jeder Stunde, macht den Strom sauber, achtet auf die Kosten – und plant Puffer für das ein, was ihr nicht vorhersehen könnt.":
        "As a team you plan Germany's electricity up to 2045 – in **four stages**. In each stage you build new plants and decide about old power plants. Then the computer calculates a whole year, hour by hour. You get points for three goals: **⚡ always enough power**, **🌿 climate protection** (clean power and little CO₂) and **💶 as cheap as possible** – up to 5 points each per stage, at most {0} in total.\n\n**In short:** cover demand in every hour, make the power clean, watch the costs – and plan a buffer for what you cannot foresee.",
    "Bauen":
        "Build",
    "Bau-Token auf neue Anlagen verteilen, alte Kraftwerke behalten oder stilllegen.":
        "Spend build tokens on new plants, keep or retire old power plants.",
    "Testen":
        "Test",
    "Mit dem Simulator ausprobieren ({0}× pro Stufe). Er rechnet ohne Zufall.":
        "Try it out with the simulator ({0}× per stage). It calculates without chance.",
    "Ändern geht noch, bis die Spielleitung die Bauphase schließt. Danach gilt es.":
        "You can still make changes until the game master closes the build phase. After that it counts.",
    "Jahr simulieren":
        "Simulate the year",
    "Für alle gleich: Wetter, Verbrauch, vielleicht eine Katastrophe.":
        "The same for everyone: weather, demand, maybe a disaster.",
    "Ergebnisse ansehen – dann geht es in die nächste Stufe.":
        "Look at the results – then on to the next stage.",
    "Anlagen bauen und alte Kraftwerke behalten. Rechts „Dein Kraftwerkspark“: Liegt die gesicherte Leistung über der Spitzenlast?":
        "Build plants and keep old power plants. On the right, “Your power plant fleet”: is the firm capacity above the peak load?",
    "Einfluss":
        "Influence",
    "Einfluss-Token für Maßnahmen wie Wasserstoff oder Akzeptanz einsetzen.":
        "Use influence tokens for measures such as hydrogen or acceptance.",
    "Simulator":
        "Simulator",
    "Probelauf eures Plans mit Diagramm.":
        "Test run of your plan with a chart.",
    "Ergebnisse":
        "Results",
    "Was im Jahr wirklich passiert ist – mit Punkten und Diagrammen.":
        "What really happened in the year – with points and charts.",
    "Verlauf":
        "History",
    "Eure Punkte und Entscheidungen aller Stufen.":
        "Your points and decisions in all stages.",
    "Kopfzeile":
        "Header",
    "Bau-Token als Kästchen (gefüllt = verplant, orange = Kredit) und eure Punkte.":
        "Build tokens as boxes (filled = planned, orange = credit) and your points.",
    "Was es ist":
        "What it is",
    "Maßnahme":
        "Measure",
    "Wirkung":
        "Effect",
    "Anlage":
        "Plant",
    "Protest-Risiko":
        "Protest risk",
    "Wofür?":
        "What for?",
    "**Wasserstoff braucht drei Bausteine:** **Elektrolyse** macht Wasserstoff aus deutschem Ökostrom-Überschuss (nicht aus Import- oder Kohle-/Gasstrom), der **Speicher** (Salzkaverne) bewahrt ihn über Wochen auf, **umgerüstete Gasturbinen** machen daraus wieder Strom (nur etwa ein Viertel kommt zurück). Zwei Einfluss-Karten, jeweils ab der Stufe danach: „Demonstrationsprogramm Wasserstoff“ = eigener grüner Wasserstoff (Elektrolyse, Speicher, Umrüstung); „Wasserstoff-Netz & Import“ = teurer Wasserstoff von außen (Speicher, Umrüstung, Import, aber keine Elektrolyse). Beide zusammen kosten zwei Token. Die Import-Leistung ist in GW Wasserstoff angegeben – daraus wird nur etwa 40 % Strom. Das Spiel zeigt an, für wie viele Tage euer Speicher reicht.":
        "**Hydrogen needs three building blocks:** **electrolysis** makes hydrogen from German surplus green power (not from imported, coal or gas power), the **storage** (salt cavern) keeps it for weeks, **converted gas turbines** turn it back into electricity (only about a quarter comes back). Two influence cards, each from the following stage: “Hydrogen demonstration programme” = your own green hydrogen (electrolysis, storage, conversion); “Hydrogen grid & imports” = expensive hydrogen from abroad (storage, conversion, imports, but no electrolysis). Both together cost two tokens. Import capacity is given in GW of hydrogen – only about 40 % of it becomes electricity. The game shows how many days your storage lasts.",
    "**Biomasse-Flexibilisierung:** gleiche Menge Biogas, aber mehr Leistung genau dann, wenn Strom knapp ist (höchstens das Dreifache der weiterbetriebenen Biomasse).":
        "**Biomass flexibilisation:** the same amount of biogas, but more capacity exactly when power is scarce (at most three times the biomass you keep).",
    "**Alte Wind- und Solaranlagen** gehen nach und nach vom Netz. Die Kacheln im Bauen-Tab zeigen, wie viel in der nächsten Stufe noch läuft.":
        "**Old wind and solar plants** go offline step by step. The cards in the Build tab show how much is still running in the next stage.",
    "**Lerneffekt:** Was ihr baut, wird für euch in den nächsten Stufen etwas billiger.":
        "**Learning effect:** what you build gets a little cheaper for you in the following stages.",
    "Kraftwerk":
        "Power plant",
    "heute":
        "today",
    "Hinweis":
        "Note",
    "**Wetter:** meist ein normales Jahr ({0}), manchmal ein schwieriges ({1}: weniger Wind), selten ein extremer Winter ({2}: lange Kälte, kaum Wind).":
        "**Weather:** usually a normal year ({0}), sometimes a difficult one ({1}: less wind), rarely an extreme winter ({2}: long cold spell, hardly any wind).",
    "**Verbrauch:** kann einige Prozent höher oder niedriger sein als erwartet.":
        "**Demand:** can be a few percent higher or lower than expected.",
    "**Katastrophen** werden von Stufe zu Stufe wahrscheinlicher: *Sturm/Hochwasser* – für jede Technologie wird einzeln gewürfelt, getroffene liefern 4 Wochen nur halb so viel. *Kalte Dunkelflaute* – 2 Wochen kaum Wind und Sonne. *Hitze & Dürre* – Kraftwerke mit Kühlwasser (Gas, Kohle, Biomasse) liefern weniger, Laufwasser auch. Wind, Sonne und Speicher trifft es nicht.":
        "**Disasters** become more likely from stage to stage: *storm/flood* – dice are rolled for each technology separately, those hit deliver only half for 4 weeks. *Cold dark doldrums* – 2 weeks with hardly any wind and sun. *Heat & drought* – power plants with cooling water (gas, coal, biomass) deliver less, run-of-river too. Wind, sun and storage are not affected.",
    "**Nachbarländer** helfen mit Strom aus – aber nicht, wenn in ganz Europa gleichzeitig Flaute ist. Überschuss nehmen sie zum Teil ab (z. B. für ihre Wasserkraft-Speicher) und geben ihn später teurer zurück. Exportierter Ökostrom zählt für den CO₂-frei-Anteil, importierter Strom nicht. Beim CO₂-Ausstoß zählt nur, was in Deutschland ausgestoßen wird – Exporte helfen dort nicht.":
        "**Neighbouring countries** help out with power – but not when there is a lull across all of Europe at the same time. They partly take surplus power (e.g. for their hydro storage) and give it back later at a higher price. Exported green power counts for the CO₂-free share, imported power does not. For CO₂ emissions only what is emitted in Germany counts – exports do not help there.",
    "**Protest (Gegenreaktion):** Jeder Bau-Token kann Protest auslösen. *Neue Anlage:* Das Gebaute läuft weiter, aber in der nächsten Stufe dürft ihr davon nichts dazubauen. *Altes Kraftwerk:* muss in der nächsten Stufe ganz stillgelegt werden.":
        "**Protest (backlash):** every build token can trigger protest. *New plant:* what was built keeps running, but in the next stage you may not build more of it. *Old power plant:* must be retired completely in the next stage.",
    "**Letzte Stufe:** Jeder Protest gegen eine neue Anlage kostet {0} Punkte – damit am Ende niemand bedenkenlos alles vollbaut.":
        "**Last stage:** every protest against a new plant costs {0} points – so that nobody builds everything without a second thought at the end.",
    "Begriff":
        "Term",
    "Bedeutung":
        "Meaning",
    "Klimaneutral: 5 Klimaschutz-Punkte nur mit ≥ {0} % CO₂-frei":
        "Climate-neutral: 5 climate points only with ≥ {0} % CO₂-free",
    "CO₂-Ziel (5 Punkte)":
        "CO₂ target (5 points)",
    "Pro Stufe bis 15 Punkte, im ganzen Spiel {0}. Bei Gleichstand gewinnt das Team mit weniger CO₂.":
        "Up to 15 points per stage, {0} in the whole game. In a tie, the team with less CO₂ wins.",
    "📖 Spielregeln":
        "📖 Rules",
    "Verbrauch inklusive Netzverluste, ohne Elektrolyse. Spitzenlast im normalen Wetterjahr – in kalten Wintern liegt sie höher.":
        "Demand incl. grid losses, excl. electrolysis. Peak load in a normal weather year – in cold winters it is higher.",
    "Feste Anlagen – hat jedes Team, nicht veränderbar. Sie folgen einem festen Fahrplan: alte Anlagen gehen vom Netz, die Leitungen ins Ausland werden automatisch ausgebaut.":
        "Fixed plants – every team has them, they cannot be changed. They follow a fixed schedule: old plants go offline, the interconnectors to other countries are expanded automatically.",
    "1. **Erst testen, dann fertig melden.** Der Simulator kennt keinen Zufall – plant Reserve ein.\n2. **Bau-Token aufbrauchen** – übrige verfallen.\n3. **Wind und Sonne allein reichen nicht.** An windstillen Winterabenden muss trotzdem Strom da sein. Haltet die gesicherte Leistung über der Spitzenlast.\n4. **Batterien helfen für Stunden, nicht für Wochen.** Für lange Flauten braucht ihr Gas, Biomasse oder Wasserstoff.\n5. **Früh an Wasserstoff denken:** Er wirkt erst eine Stufe nach dem Einfluss-Token. Eigener Wasserstoff braucht drei Bausteine (Elektrolyse, Speicher, umgerüstete Gasturbinen), Import das Wasserstoff-Netz. Ohne Wasserstoff wird 2045 kaum klimaneutral.\n6. **Stufe 2 ist der große Sprung:** viel mehr Verbrauch, viel weniger Kohle – schon in Stufe 1 vorsorgen.\n7. **CO₂ Stufe für Stufe senken:** Die Grenze für den Ausstoß sinkt jede Stufe (oben in der Übersicht: „CO₂-Ziel“). Gaskraftwerke laufen, wann immer sie gebraucht werden – weniger CO₂ gibt es nur mit mehr Ökostrom, Speichern, Wasserstoff-Umrüstung oder durch Stilllegen alter Kraftwerke.":
        "1. **Test first, then mark as ready.** The simulator knows no chance – plan a reserve.\n2. **Use up your build tokens** – leftovers expire.\n3. **Wind and sun alone are not enough.** On windless winter evenings there must still be power. Keep the firm capacity above the peak load.\n4. **Batteries help for hours, not for weeks.** For long lulls you need gas, biomass or hydrogen.\n5. **Think about hydrogen early:** it only takes effect one stage after the influence token. Your own hydrogen needs three building blocks (electrolysis, storage, converted gas turbines), imports need the hydrogen grid. Without hydrogen, 2045 will hardly be climate-neutral.\n6. **Stage 2 is the big jump:** much more demand, much less coal – prepare already in stage 1.\n7. **Cut CO₂ stage by stage:** the emission limit falls every stage (at the top of the overview: “CO₂ target”). Gas power plants run whenever they are needed – less CO₂ only comes with more green power, storage, hydrogen conversion or by retiring old power plants.",
    "Deutschland als ein Netz ohne Engpässe, alle **8.760 Stunden** eines Jahres. Die Nachbarländer sind vereinfacht als ein Markt abgebildet, mit ihrem eigenen Wetter und Verbrauch, einem Speicher (Wasserkraft in Norwegen und den Alpen) und einer festen Abnahme für deutschen Überschuss.":
        "Germany as one grid without bottlenecks, all **8,760 hours** of a year. The neighbouring countries are simplified as one market, with their own weather and demand, a storage (hydropower in Norway and the Alps) and a fixed uptake for German surplus power.",
    "In jeder Stunde laufen die **günstigsten** Anlagen zuerst. Speicher laden bei Überschuss und liefern bei Knappheit. Das Modell kennt das ganze Jahr im Voraus.":
        "In every hour the **cheapest** plants run first. Storage charges when there is a surplus and delivers when power is scarce. The model knows the whole year in advance.",
    "**Kosten** = Investitionen (verteilt über die Lebensdauer, 5 % Zins) + Betriebskosten + Brennstoff und CO₂ + Importe − Exporterlöse + Kredit- und Einfluss-Kosten, geteilt durch den Verbrauch. Alte Anlagen zählen nur mit ihren Betriebskosten. Fehlender Strom wird als Schaden angezeigt (10.000 €/MWh), kostet aber nur Versorgungs-Punkte, keine Kosten-Punkte.":
        "**Costs** = investment (spread over the lifetime, 5 % interest) + operating costs + fuel and CO₂ + imports − export revenue + credit and influence costs, divided by demand. Old plants only count with their operating costs. Missing power is shown as damage (10,000 €/MWh) but only costs supply points, not cost points.",
    "**CO₂-frei** = (Verbrauch + Export − Import − fossiler Strom) ÷ Verbrauch, höchstens 100 %. CO₂-frei sind Wind, Sonne, Wasser, Biomasse, Wasserstoff und die Hälfte der Abfallverbrennung.":
        "**CO₂-free** = (demand + exports − imports − fossil power) ÷ demand, at most 100 %. CO₂-free are wind, sun, hydro, biomass, hydrogen and half of waste incineration.",
    "**CO₂-Ausstoß** zählt nur in Deutschland, wie im Klimaschutzgesetz. Das CO₂ der Importe wird getrennt angezeigt.":
        "**CO₂ emissions** only count in Germany, as in the Climate Protection Act. The CO₂ of imports is shown separately.",
    "**Klimaschutz-Punkte** = der schlechtere Wert aus den Punkten für den Anteil und für den Ausstoß. So helfen Exporte nicht gegen zu viel CO₂ und Importe nicht gegen einen zu kleinen Anteil.":
        "**Climate points** = the worse of the points for the share and for the emissions. So exports do not help against too much CO₂, and imports do not help against too small a share.",
    "Daten: ENTSO-E TYNDP 2024 (Wetter, Verbrauch, Preise), Bundesnetzagentur (Kraftwerke), PyPSA technology-data (Kosten).":
        "Data: ENTSO-E TYNDP 2024 (weather, demand, prices), Federal Network Agency (power plants), PyPSA technology-data (costs).",
    " und ≤ {0} Mt CO₂":
        " and ≤ {0} Mt CO₂",
    "Stufe {0} ({1}): Das ist neu":
        "Stage {0} ({1}): what's new",
    "<b>Bau-Token</b>":
        "<b>Build tokens</b>",
    "{0} Mrd. € für neue Anlagen. Je Stufe: {1} – vorne mehr, weil dort am meisten gebaut werden muss. <b>Verfallen am Ende der Stufe</b> – also aufbrauchen.":
        "€{0} bn for new plants. Per stage: {1} – more at the beginning, because that is where most has to be built. <b>They expire at the end of the stage</b> – so use them up.",
    "<b>Kredit-Token</b>":
        "<b>Credit tokens</b>",
    "Bis zu {0} zusätzliche Bau-Token pro Stufe, kosten {1} % mehr.":
        "Up to {0} extra build tokens per stage, they cost {1} % more.",
    "<b>Einfluss-Token</b>":
        "<b>Influence tokens</b>",
    "{0} zu Beginn, weitere für je {1} Bau-Token. Schalten eine Maßnahme frei – jede nur einmal im Spiel. Je früher, desto länger wirkt sie.":
        "{0} at the start, more for {1} build tokens each. They unlock a measure – each only once per game. The earlier, the longer it works.",
    "Kohle (Braun- & Steinkohle)":
        "Coal (lignite & hard coal)",
    "Gaskraftwerke":
        "Gas power plants",
    "steuerbar, stoßen CO₂ aus":
        "dispatchable, emit CO₂",
    "Biomasse/Biogas":
        "Biomass/biogas",
    "steuerbar, aber nur ~{0} TWh im Jahr":
        "dispatchable, but only ~{0} TWh per year",
    "Für Interessierte anzeigen":
        "Show for those interested",
    "Springe zu:":
        "Jump to:",
    "Stunden im Jahr, in denen Strom fehlt. Weniger ist besser.":
        "Hours per year in which power is missing. Fewer is better.",
    "Höchstens … Stunden:":
        "At most … hours:",
    "Anteil CO₂-frei, mindestens … %:":
        "Share CO₂-free, at least … %:",
    "Kosten für Anlagen, Brennstoff und CO₂ je MWh Strom (ohne Netz, Steuern, Abgaben). Investitionen werden auf ihre Lebensdauer verteilt und zählen auch in allen späteren Stufen. Weniger ist besser.":
        "Costs of plants, fuel and CO₂ per MWh of electricity (excl. grid, taxes, levies). Investments are spread over their lifetime and also count in all later stages. Lower is better.",
    "Höchstens … €/MWh:":
        "At most … €/MWh:",
    "Speicher (4 h Volllast)":
        "Storage (4 h full load)",
    "nach Überschuss":
        "when there is a surplus",
    "Wochen–Monate":
        "weeks–months",
    "steuerbar":
        "dispatchable",
    "läuft immer mit mindestens 15 % Leistung (Fernwärme, Tagebau) und ändert die Leistung höchstens um 40 % pro Stunde. Kohleausstieg per Gesetz: höchstens ":
        "always runs at least at 15 % (district heating, mines) and changes its output by at most 40 % per hour. Coal phase-out by law: at most ",
    "Energieinhalt reicht für ca. {0} Stunden bei voller Leistung":
        "Energy content lasts about {0} hours at full power",
    "Energieinhalt für ca. 1 Stunde bei voller Leistung; altern bis 2045 weg":
        "Energy content for about 1 hour at full power; retired by 2045",
    "klein, recht gleichmäßig, CO₂-frei":
        "small, fairly steady, CO₂-free",
    "läuft immer, zur Hälfte erneuerbar":
        "always running, half renewable",
    "teuer, nur bei Knappheit":
        "expensive, only when scarce",
    "nur im Notfall, fossil":
        "only in emergencies, fossil",
    "höchstens so viel Import oder Export; +{0} mit „Netzausbau Europa“ (ab der Folgestufe)":
        "at most this much import or export; +{0} with “European grid expansion” (from the following stage)",
    "<div class=\"ptz-kv\" style=\"font-size:.85rem\"><span class=\"k\">Verbrauch</span><span class=\"v\">{0} TWh</span><span class=\"k\">Spitzenlast</span><span class=\"v\">{1} GW</span><span class=\"k\">Bau-Token</span><span class=\"v\">{2}</span><span class=\"k\">CO₂-Preis</span><span class=\"v\">{3} €/t</span>":
        "<div class=\"ptz-kv\" style=\"font-size:.85rem\"><span class=\"k\">Demand</span><span class=\"v\">{0} TWh</span><span class=\"k\">Peak load</span><span class=\"v\">{1} GW</span><span class=\"k\">Build tokens</span><span class=\"v\">{2}</span><span class=\"k\">CO₂ price</span><span class=\"v\">{3} €/t</span>",
    "alle":
        "all",
    "5 Punkte = politisches Ziel erreicht.":
        "5 points = political target reached.",
    "CO₂-Ausstoß, höchstens … Mt:":
        "CO₂ emissions, at most … Mt:",
    "Orientierung: 2030 Klimaschutzgesetz (Energiewirtschaft 108 Mt, davon Strom grob 70), 2035 G7-Zusage „Stromsektor weitgehend CO₂-frei“, 2040 Kohleausstieg und Ende der CO₂-Zertifikate im EU-Emissionshandel, 2045 Klimaneutralität (Abfallverbrennung allein ~5 Mt).":
        "Orientation: 2030 Climate Protection Act (energy sector 108 Mt, of which electricity roughly 70), 2035 G7 pledge “power sector largely CO₂-free”, 2040 coal exit and end of new CO₂ allowances in the EU emissions trading system, 2045 climate neutrality (waste incineration alone ~5 Mt).",
    "Alte Großbatterien":
        "Old large batteries",
    "Öl & sonstige":
        "Oil & other",
    "Reservekraftwerke":
        "Reserve power plants",
    "Leitungen ins Ausland":
        "Interconnectors to other countries",
    "<span class=\"k\">CO₂-Ziel</span><span class=\"v\">≤ {0} Mt</span>":
        "<span class=\"k\">CO₂ target</span><span class=\"v\">≤ {0} Mt</span>",
    "⚡ Versorgungssicherheit":
        "⚡ Security of supply",
    "🌿 Klimaschutz":
        "🌿 Climate protection",
    "Zwei Bedingungen – es zählt der schlechtere Wert. (1) Anteil CO₂-freier Strom: was in Deutschland sauber erzeugt wird; exportierter Ökostrom zählt mit, Importe nicht. ":
        "Two conditions – the worse value counts. (1) Share of CO₂-free power: what is generated cleanly in Germany; exported green power counts, imports do not. ",
    "💶 Bezahlbarkeit":
        "💶 Affordability",
    "(2) CO₂-Ausstoß in Deutschland (Mt pro Jahr) – die Grenze sinkt jede Stufe bis fast null (Klimaneutralität 2045). ":
        "(2) CO₂ emissions in Germany (Mt per year) – the limit falls every stage to almost zero (climate neutrality 2045). ",
    "Der Simulator ist nur in der Bauphase verfügbar.":
        "The simulator is only available during the build phase.",
    "Keine Simulationen mehr in dieser Stufe.":
        "No simulations left in this stage.",
    "Simulation läuft bereits.":
        "Simulation already running.",
    "Simulation fehlgeschlagen: {0}":
        "Simulation failed: {0}",
    "Onshore-Wind":
        "Onshore wind",
    "Offshore-Wind":
        "Offshore wind",
    "Freiflächen-PV":
        "Ground-mounted PV",
    "Dach-PV":
        "Rooftop PV",
    "Batteriespeicher (4-h-Speicher)":
        "Battery storage (4-hour)",
    "Wasserstoff: Elektrolyse":
        "Hydrogen: electrolysis",
    "Wasserstoff-Speicher (Kaverne)":
        "Hydrogen storage (cavern)",
    "Neue Gasturbinen (H₂-ready)":
        "New gas turbines (H₂-ready)",
    "Biomasse-Flexibilisierung":
        "Biomass flexibilisation",
    "Bestehende Gaskraftwerke":
        "Existing gas power plants",
    "Gasturbinen auf H₂ umgerüstet":
        "Gas turbines converted to H₂",
    "Import/Export (Kuppelleitungen)":
        "Imports/exports (interconnectors)",
    "Onshore-Wind (Bestand)":
        "Onshore wind (existing)",
    "Offshore-Wind (Bestand)":
        "Offshore wind (existing)",
    "Großbatterien (Bestand, 1-h-Speicher)":
        "Large batteries (existing, 1-hour)",
    "Akzeptanz & Teilhabe":
        "Acceptance & participation",
    "Halbiert das Risiko gesellschaftlicher Gegenreaktionen – ab dieser Stufe.":
        "Halves the risk of public backlash – from this stage.",
    "Beschleunigte Innovation":
        "Accelerated innovation",
    "Doppelte Kostensenkung durch eigene Bauprojekte – ab dieser Stufe.":
        "Double cost reduction from your own construction projects – from this stage.",
    "Klimaresilienz":
        "Climate resilience",
    "Halbiert die Folgen von Katastrophen (auch Dunkelflaute, Hitze) – ab dieser Stufe.":
        "Halves the impact of disasters (including dark doldrums, heat) – from this stage.",
    "Demonstrationsprogramm Wasserstoff":
        "Hydrogen demonstration programme",
    "Eigener grüner Wasserstoff: Elektrolyse, Speicher und Umrüstung von Gasturbinen – ab der nächsten Stufe.":
        "Your own green hydrogen: electrolysis, storage and conversion of gas turbines – from the next stage.",
    "Wasserstoff-Netz & Import":
        "Hydrogen grid & imports",
    "Importierter Wasserstoff für umgerüstete Gasturbinen, dazu Speicher und Umrüstung (keine Elektrolyse) – ab der nächsten Stufe.":
        "Imported hydrogen for converted gas turbines, plus storage and conversion (no electrolysis) – from the next stage.",
    "Netzausbau Europa":
        "European grid expansion",
    "+10 GW Leitungen ins Ausland für Import und Export – ab der nächsten Stufe.":
        "+10 GW of interconnectors to other countries for imports and exports – from the next stage.",
    "Flexible Verbraucher":
        "Flexible demand",
    "E-Autos, Wärmepumpen und Industrie passen ihren Verbrauch an – ab der nächsten Stufe.":
        "Electric cars, heat pumps and industry adapt their consumption – from the next stage.",
    "Elektrolyse gibt es nur mit dieser Karte. Sie läuft nur mit deutschem Ökostrom-Überschuss.":
        "Electrolysis is only available with this card. It runs only on German surplus green power.",
    "Teuer, aber CO₂-frei. Import: 2035: 15 GW H₂ (≈ 6 GW Strom) zu 140 €/MWh H₂; 2040: 30 GW H₂ (≈ 12 GW Strom) zu 125 €/MWh H₂; 2045: 45 GW H₂ (≈ 18 GW Strom) zu 110 €/MWh H₂.":
        "Expensive, but CO₂-free. Imports: 2035: 15 GW H₂ (≈ 6 GW electricity) at 140 €/MWh H₂; 2040: 30 GW H₂ (≈ 12 GW electricity) at 125 €/MWh H₂; 2045: 45 GW H₂ (≈ 18 GW electricity) at 110 €/MWh H₂.",
    "Verbrauch wird innerhalb eines Tages verschoben; die Industrie verzichtet bei Knappheit (ab 300 €/MWh). Wächst mit jeder Stufe.":
        "Consumption is shifted within a day; industry cuts back when power is scarce (from 300 €/MWh). Grows with every stage.",
    "Sturm/Hochwasser: Anlagen beschädigt – betroffene Technologien liefern 4 Wochen nur halbe Leistung.":
        "Storm/flood: plants damaged – affected technologies deliver only half for 4 weeks.",
    "Kalte Dunkelflaute: 2 Wochen kaum Wind und wenig Sonne, dazu höherer Verbrauch.":
        "Cold dark doldrums: 2 weeks with hardly any wind and little sun, plus higher demand.",
    "Hitze & Dürre: 4 Wochen Kühlwassermangel und niedrige Flusspegel – Kraftwerke gedrosselt.":
        "Heat & drought: 4 weeks of cooling-water shortage and low river levels – power plants throttled.",
    "normales Jahr":
        "normal year",
    "schwieriges Jahr: kälter, weniger Wind":
        "difficult year: colder, less wind",
    "extremer Winter: lange Kälte, kaum Wind":
        "extreme winter: long cold spell, hardly any wind",
    "Kohle":
        "Coal",
    "alte Gaskraftwerke":
        "old gas power plants",
    "neue Gasturbinen (Erdgas)":
        "new gas turbines (natural gas)",
    "Kohle früher stilllegen.":
        "Retire coal earlier.",
    "Alte Gaskraftwerke reduzieren und durch Wasserstoff-Turbinen, Speicher oder mehr Ökostrom ersetzen – solange die Ampeln der gesicherten Leistung grün bleiben.":
        "Reduce old gas power plants and replace them with hydrogen turbines, storage or more green power – as long as the firm-capacity traffic lights stay green.",
    "Neue Gasturbinen auf Wasserstoff umrüsten (Einfluss-Karte nötig) – mit genug Wasserstoff, sonst fehlen sie in der Dunkelflaute.":
        "Convert new gas turbines to hydrogen (influence card needed) – with enough hydrogen, otherwise they are missing in the dark doldrums.",
    "Mehr Ökostrom und Speicher, damit die teuren Altanlagen seltener laufen.":
        "More green power and storage, so that the expensive old plants run less often.",
    "Mehr gesicherte Leistung, damit die Reserve seltener einspringen muss.":
        "More firm capacity, so that the reserve has to step in less often.",
    "Abfallverbrennung ist fest – an anderer Stelle CO₂ sparen.":
        "Waste incineration is fixed – save CO₂ elsewhere.",
    "Biomasse":
        "Biomass",
    "Gas (Bestand)":
        "Gas (existing)",
    "Gas (neu)":
        "Gas (new)",
    "H₂ in umgerüsteten Gasturbinen":
        "H₂ in converted gas turbines",
    "Wasserstoff-Turbine":
        "Hydrogen turbine",
    "Batterie (Entladen)":
        "Battery (discharging)",
    "Nicht gedeckter Bedarf":
        "Unserved demand",
    "Batterie (Laden)":
        "Battery (charging)",
    "Pumpspeicher (Turbine)":
        "Pumped hydro (turbine)",
    "Pumpspeicher (Pumpen)":
        "Pumped hydro (pumping)",
    "davon Onshore-Bestand":
        "of which existing onshore",
    "davon Offshore-Bestand":
        "of which existing offshore",
    "Lastverzicht (Industrie)":
        "Demand reduction (industry)",
    "Lastverschiebung (verlagerter Verbrauch)":
        "Load shifting (shifted consumption)",
    "kein":
        "none",
    "niedrig":
        "low",
    "mittel":
        "medium",
    "hoch":
        "high",
    "Warten auf Start":
        "Waiting for start",
    "Bauphase":
        "Build phase",
    "Wird berechnet …":
        "Calculating …",
    "Spiel beendet":
        "Game over",
    "Versorgungssicherheit":
        "Security of supply",
    "Bezahlbarkeit":
        "Affordability",
    "Günstiger Strom bei Wind; liefert im Winter mehr als im Sommer.":
        "Cheap power when the wind blows; delivers more in winter than in summer.",
    "Weht stetiger und stärker als an Land, aber teurer.":
        "Blows more steadily and strongly than on land, but more expensive.",
    "Billigster Strom, aber nur tagsüber und vor allem im Sommer.":
        "Cheapest power, but only during the day and mainly in summer.",
    "Wie Freiflächen-PV, ~10 % weniger Ertrag, teurer – dafür kaum Widerstand.":
        "Like ground-mounted PV, ~10 % less yield, more expensive – but hardly any opposition.",
    "Verschiebt Strom z. B. vom Mittag in den Abend; voll geladen reicht er 4 h bei voller Leistung.":
        "Shifts power, e.g. from noon to the evening; when full it lasts 4 h at full power.",
    "Mehr Leistung an Biogasanlagen: gleiche Energiemenge, aber gezielt bei Knappheit.":
        "More capacity at biogas plants: same amount of energy, but targeted at scarce hours.",
    "Günstige Gasturbinen als Reserve: jederzeit startbereit, stoßen CO₂ aus – auf H₂ umrüstbar.":
        "Cheap gas turbines as a reserve: ready to start at any time, emit CO₂ – can be converted to H₂.",
    "Elektrolyse: macht aus deutschem Ökostrom-Überschuss Wasserstoff – für Speicher und umgerüstete Gasturbinen.":
        "Electrolysis: turns German surplus green power into hydrogen – for storage and converted gas turbines.",
    "Salzkaverne: bewahrt Wasserstoff über Wochen und Monate auf – günstig pro TWh.":
        "Salt cavern: keeps hydrogen for weeks and months – cheap per TWh.",
    "Hohe CO₂-Emissionen, träge (mind. 15 % Leistung). Gesetzlicher Ausstieg.":
        "High CO₂ emissions, slow (at least 15 % output). Legal phase-out.",
    "Bestehende Gaskraftwerke: steuerbar, stoßen CO₂ aus.":
        "Existing gas power plants: dispatchable, emit CO₂.",
    "Biogas, Holz u. a.: steuerbar, Energiemenge begrenzt (~41 TWh/Jahr).":
        "Biogas, wood etc.: dispatchable, energy limited (~41 TWh/year).",
    "Laufwasser: kleiner, recht gleichmäßiger Beitrag.":
        "Run-of-river: small, fairly steady contribution.",
    "Pumpspeicher: voll geladen reicht er ca. 6 h bei voller Leistung.":
        "Pumped hydro: when full it lasts about 6 h at full power.",
    "Bestehende Großbatterien: voll geladen reichen sie ca. 1 h bei voller Leistung.":
        "Existing large batteries: when full they last about 1 h at full power.",
    "Öl, Grubengas u. a.: teuer, nur bei Knappheit; ab 2040 stillgelegt.":
        "Oil, mine gas etc.: expensive, only when scarce; retired from 2040.",
    "Reservekraftwerke außerhalb des Markts: nur in Notlagen.":
        "Reserve power plants outside the market: only in emergencies.",
    "Neue Gasturbinen, die Wasserstoff aus dem eigenen Speicher verbrennen.":
        "New gas turbines that burn hydrogen from your own storage.",
    "Abfallverbrennung: läuft immer, zur Hälfte erneuerbar.":
        "Waste incineration: always running, half renewable.",
    "Kuppelleitungen zu den Nachbarländern: Import und Export.":
        "Interconnectors to the neighbouring countries: imports and exports.",
    "E-Autos und Wärmepumpen verschieben Verbrauch, Industrie verzichtet bei Knappheit.":
        "Electric cars and heat pumps shift consumption, industry cuts back when power is scarce.",
    "Wasser":
        "Hydro",
    "Biomasse & Abfall":
        "Biomass & waste",
    "Erdgas":
        "Natural gas",
    "Sonstige & Reserve":
        "Other & reserve",
    "Wind":
        "Wind",
    "Sonne":
        "Sun",
    "Speicher (Entladen)":
        "Storage (discharging)",
    "Versorgungslücke":
        "Supply gap",
    "Speicher (Laden)":
        "Storage (charging)",
    "Verbrauch verschoben":
        "Shifted consumption",
    "Speicher":
        "Storage",
    "Steuerbar CO₂-frei":
        "Dispatchable CO₂-free",
    "Steuerbar fossil":
        "Dispatchable fossil",
    "Wasserstoff-Elektrolyse":
        "Hydrogen electrolysis",
    "Politik & Gesellschaft":
        "Policy & society",
    "Technik & Infrastruktur":
        "Technology & infrastructure",
    "Jetzt–2030":
        "Now–2030",
    "2031–2035":
        "2031–2035",
    "2036–2040":
        "2036–2040",
    "2041–2045":
        "2041–2045",
    "Leistung (GW)":
        "Capacity (GW)",
    "Wie viel Strom in einem Moment fließen kann – wie weit ein Wasserhahn aufgedreht ist. 1 Gigawatt (GW) entspricht etwa einem großen Kraftwerk.":
        "How much power can flow at one moment – how far a tap is turned on. 1 gigawatt (GW) is roughly one large power plant.",
    "Energie (TWh)":
        "Energy (TWh)",
    "Wie viel Strom insgesamt über eine Zeit fließt – wie viel Wasser im Eimer landet. Leistung mal Stunden. Deutschland verbraucht heute rund 500 Terawattstunden (TWh) im Jahr.":
        "How much power flows in total over a period – how much water ends up in the bucket. Capacity times hours. Germany uses about 500 terawatt hours (TWh) per year today.",
    "Die Stunde mit dem höchsten Verbrauch im Jahr, meist an einem kalten Winterabend. So viel Leistung muss dann bereitstehen.":
        "The hour with the highest demand of the year, usually on a cold winter evening. That much capacity must be available then.",
    "Wie viel eine Anlage im Jahresschnitt liefert, verglichen mit Volllast rund um die Uhr. Ein Windrad an Land schafft etwa ein Viertel, eine Solaranlage etwa ein Zehntel.":
        "How much a plant delivers on average over the year, compared with full output around the clock. An onshore wind turbine manages about a quarter, a solar plant about a tenth.",
    "Steuerbar":
        "Dispatchable",
    "Liefert Strom, wann man ihn braucht – z. B. Gas, Biomasse, Wasserstoff oder ein voller Speicher. Wind und Sonne sind nicht steuerbar: Sie liefern nur, wenn das Wetter mitspielt.":
        "Delivers power when it is needed – e.g. gas, biomass, hydrogen or a full storage. Wind and sun are not dispatchable: they only deliver when the weather plays along.",
    "Alle steuerbaren Kraftwerke zusammen (Gas, Wasserstoff, Kohle, Biomasse, Reserve). Darauf könnt ihr auch zählen, wenn tagelang weder Wind weht noch Sonne scheint. Sie sollte über der Spitzenlast liegen. Speicher und flexible Verbraucher helfen zusätzlich – aber nur für einige Stunden. Wasserstoff-Turbinen zählen nur so weit, wie der Wasserstoff 2 Wochen reicht.":
        "All dispatchable power plants together (gas, hydrogen, coal, biomass, reserve). You can count on them even when the wind does not blow and the sun does not shine for days. It should be above the peak load. Storage and flexible demand also help – but only for a few hours. Hydrogen turbines only count as far as the hydrogen lasts for 2 weeks.",
    "Residuallast":
        "Residual load",
    "Verbrauch minus Wind- und Sonnenstrom – also der Rest, den steuerbare Anlagen, Speicher und Importe liefern müssen.":
        "Demand minus wind and solar power – the rest that dispatchable plants, storage and imports have to supply.",
    "Dunkelflaute":
        "Dark doldrums (Dunkelflaute)",
    "Mehrere Tage mit wenig Wind und kaum Sonne, meist im Winter. Die härteste Probe für das Stromsystem.":
        "Several days with little wind and hardly any sun, usually in winter. The toughest test for the power system.",
    "Eine Stunde, in der nicht genug Strom da ist. In Wirklichkeit müssten dann Verbraucher abgeschaltet werden.":
        "An hour in which there is not enough power. In reality, consumers would then have to be disconnected.",
    "Nimmt Strom auf, wenn zu viel da ist, und gibt ihn ab, wenn er fehlt. Die Angabe „4 h“ heißt: Der volle Speicher reicht 4 Stunden bei voller Leistung (bei halber Leistung 8 Stunden). Batterien und Pumpspeicher reichen so für Stunden, Wasserstoff für Wochen.":
        "Takes in power when there is too much and releases it when it is missing. “4 h” means: the full storage lasts 4 hours at full power (8 hours at half power). Batteries and pumped hydro therefore last for hours, hydrogen for weeks.",
    "Wasserstoff & Elektrolyse":
        "Hydrogen & electrolysis",
    "Elektrolyse macht aus Strom Wasserstoff. Der lässt sich in unterirdischen Salzhöhlen (Kavernen) über Wochen und Monate lagern und in umgerüsteten Gasturbinen ohne CO₂ wieder verbrennen. Dabei geht viel verloren: Nur etwa ein Viertel des Stroms kommt zurück. Die Elektrolyse ist teuer, der Speicher pro TWh vergleichsweise billig. Wasserstoff kann auch über Pipelines importiert werden (Wasserstoff-Kernnetz).":
        "Electrolysis turns electricity into hydrogen. It can be stored in underground salt caverns for weeks and months and burned again without CO₂ in converted gas turbines. A lot is lost on the way: only about a quarter of the electricity comes back. Electrolysis is expensive, the storage is comparatively cheap per TWh. Hydrogen can also be imported via pipelines (hydrogen core grid).",
    "Wind- und Sonnenstrom, der gerade weder gebraucht, gespeichert noch exportiert werden kann. Die Anlagen werden dann gedrosselt – der Strom ist verloren.":
        "Wind and solar power that can currently neither be used, stored nor exported. The plants are then throttled – the power is lost.",
    "Über Stromleitungen ins Ausland (Kuppelleitungen) kann Deutschland Strom kaufen (Import) oder verkaufen (Export).":
        "Via power lines to other countries (interconnectors) Germany can buy (import) or sell (export) electricity.",
    "Verbraucher, die mitdenken: Ein E-Auto lädt mittags statt abends, eine Wärmepumpe heizt vor, eine Fabrik pausiert in teuren Stunden. Das senkt die Spitzenlast.":
        "Consumers that think along: an electric car charges at noon instead of in the evening, a heat pump preheats, a factory pauses in expensive hours. This lowers the peak load.",
    "Was Kraftwerke für jede ausgestoßene Tonne CO₂ zahlen müssen. Macht Kohle und Gas teurer – und steigt bis 2045.":
        "What power plants have to pay for every tonne of CO₂ they emit. Makes coal and gas more expensive – and rises until 2045.",
    "CO₂-Ausstoß (Mt)":
        "CO₂ emissions (Mt)",
    "Wie viel CO₂ die Kraftwerke in Deutschland in einem Jahr ausstoßen, in Millionen Tonnen (Mt). Zum Vergleich: Die ganze Energiewirtschaft darf 2030 laut Klimaschutzgesetz noch 108 Mt ausstoßen.":
        "How much CO₂ the power plants in Germany emit in one year, in million tonnes (Mt). For comparison: under the Climate Protection Act the whole energy sector may still emit 108 Mt in 2030.",
    "Klimaneutralität (Netto-Null)":
        "Climate neutrality (net zero)",
    "Ziel des Klimaschutzgesetzes für 2045: Deutschland stößt nicht mehr Treibhausgase aus, als Wälder, Moore und Technik wieder aufnehmen. Für den Stromsektor heißt das: Ausstoß fast null. Gezählt werden Tonnen – Ökostrom-Exporte gleichen nichts aus.":
        "Target of the Climate Protection Act for 2045: Germany emits no more greenhouse gases than forests, moors and technology absorb again. For the power sector this means: emissions close to zero. Tonnes are counted – green power exports do not offset anything.",
    "Anteil CO₂-frei":
        "CO₂-free share",
    "Wie viel des Verbrauchs in Deutschland sauber erzeugt wird (Wind, Sonne, Wasser, Biomasse, Wasserstoff). Exportierter Ökostrom zählt mit, Importe nicht. Gesetzliches Ziel 2030: 80 %.":
        "How much of the demand in Germany is generated cleanly (wind, sun, hydro, biomass, hydrogen). Exported green power counts, imports do not. Legal target for 2030: 80 %.",
    "Wind & Sonne":
        "Wind & sun",
    "Günstige Energie – aber nur, wenn Wind weht oder die Sonne scheint.":
        "Cheap energy – but only when the wind blows or the sun shines.",
    "Speicher & Flexibilität":
        "Storage & flexibility",
    "Verschieben Strom von Überschuss- in Knappheitsstunden.":
        "Shift power from surplus hours to scarce hours.",
    "Steuerbare Kraftwerke":
        "Dispatchable power plants",
    "Liefern auch bei Dunkelflaute – mit Erdgas oder, umgerüstet, mit Wasserstoff.":
        "Deliver even in dark doldrums – with natural gas or, once converted, with hydrogen.",
    "Drei Bausteine, die zusammenpassen müssen: Elektrolyse macht aus Überschussstrom Wasserstoff, der Speicher bewahrt ihn für Wochen auf, umgerüstete Gasturbinen machen wieder Strom daraus.":
        "Three building blocks that must fit together: electrolysis makes hydrogen from surplus power, the storage keeps it for weeks, converted gas turbines turn it back into electricity.",
    "Erzeugungs- und Speicherkosten":
        "Generation and storage costs",
    "ohne Netze, Umlagen, Steuern":
        "excl. grids, levies, taxes",
    "Photovoltaik":
        "Photovoltaics",
    "Batterien":
        "Batteries",
    "Biomasse, Wasser, Abfall":
        "Biomass, hydro, waste",
    "Wasserstoff-Turbinen":
        "Hydrogen turbines",
    "Gasturbinen neu":
        "Gas turbines new",
    "Gas Bestand":
        "Gas existing",
    "Öl & Reserve":
        "Oil & reserve",
    "Januar":
        "January",
    "Februar":
        "February",
    "März":
        "March",
    "April":
        "April",
    "Mai":
        "May",
    "Juni":
        "June",
    "Juli":
        "July",
    "August":
        "August",
    "September":
        "September",
    "Oktober":
        "October",
    "November":
        "November",
    "Dezember":
        "December",
    "bearbeitet":
        "editing",
    "fertig gemeldet":
        "marked as ready",
    "wird berechnet":
        "calculating",
    "fertig":
        "done",
    "Fehler":
        "Error",
    "Spielregeln":
        "Rules",
    "Spielleitung":
        "Game master",
    "Zero45":
        "Zero45",
    "Regeln":
        "Rules",
    " und ":
        " and ",
    "Keine Daten vorhanden.":
        "No data.",
    "vorhanden":
        "existing",
    "−1 Simulation":
        "−1 simulation",
    "Bereits genutzte Simulationen lassen sich nicht abziehen.":
        "Simulations already used cannot be removed.",
    "Simulationen pro Stufe für alle Teams:":
        "Simulations per stage for all teams:",
    "Gilt sofort und für die weiteren Stufen. +/− in der Tabelle: nur dieses Team, nur diese Stufe.":
        "Applies immediately and for the following stages. +/− in the table: this team only, this stage only.",
    "−5 Min.":
        "−5 min",
    "−2 Min.":
        "−2 min",
    "Spielidee nach „Path to Zero“ von Jesse D. Jenkins und dem Princeton ZERO Lab · Freie Software (GPL-2.0-or-later) · Lernspiel, keine Prognose":
        "Game idea based on “Path to Zero” by Jesse D. Jenkins and the Princeton ZERO Lab · Free software (GPL-2.0-or-later) · Learning game, not a forecast",
}
