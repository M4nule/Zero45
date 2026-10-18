# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Rules & overview page ("Spielregeln"): all numbers come from the game config and assumptions."""
from __future__ import annotations

from nicegui import ui

from ptz.engine.model import (assumptions, capacity_factors, demand_total_twh, fixed_capacities,
                              peak_demand_mw, trade_capacity)
from ptz.game import core
from ptz.server.theme import CAT, RISK_DE, de, gw, points_color, tcolor, tdesc
from ptz.i18n import TList, tr

STAGE_LABELS = TList(["Jetzt–2030", "2031–2035", "2036–2040", "2041–2045"])


def _table(header: list[str], rows: list[list[str]], align: str = ""):
    """align: one letter per column, l = left/wrapping text, r = right/numbers (default: first l, rest r)."""
    align = align or ("l" + "r" * (len(header) - 1))

    def cell(tag, i, c):
        a = align[i] if i < len(align) else "r"
        style = "text-align:left;white-space:normal" if a == "l" else "text-align:right;white-space:nowrap"
        return f'<{tag} style="{style}">{c}</{tag}>'
    h = "".join(cell("th", i, c) for i, c in enumerate(header))
    body = "".join("<tr>" + "".join(cell("td", i, c) for i, c in enumerate(r)) + "</tr>" for r in rows)
    ui.html(f'<div style="overflow-x:auto"><table class="ptz-table"><thead><tr>{h}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>').classes("w-full")


def _section(no: int, title: str, intro: str = ""):
    with ui.row().classes("items-center ptz-section w-full") as row:
        ui.html(f'<span class="ptz-sec-no">{no}</span>')
        ui.label(title).classes("ptz-h2").style("margin-top:0")
    if intro:
        ui.label(intro).classes("ptz-sub")
    return row


def _bullets(items: list[str]):
    ui.markdown("\n".join(f"- {s}" for s in items)).classes("w-full")


def _stage_notes(cfg: dict) -> list[str]:
    """One 'watch out' line per stage, computed from the data."""
    a = assumptions()
    ys = core.stage_years()
    coal = a["existing_params"]["coal_max_mw"]
    dem, peak = {y: demand_total_twh(y) for y in ys}, {y: peak_demand_mw(y) for y in ys}
    res = {y: fixed_capacities(y)["reserve"] for y in ys}
    return [
        tr("Kohle höchstens {0}. Einfluss-Token früh einsetzen.", gw(coal[ys[0]], 0)),
        tr("Großer Sprung: Verbrauch +{0} %, Spitzenlast +{1} GW – und nur noch {2} Kohle.", de(100 * (dem[ys[1]] / dem[ys[0]] - 1), 0), de((peak[ys[1]] - peak[ys[0]]) / 1e3, 0), gw(coal[ys[1]], 0)),
        tr("Kohle und Öl sind weg, Reserve nur noch {0}. Viele alte Windräder gehen vom Netz.", gw(res[ys[2]], 0)),
        tr("Klimaneutral: 5 Klimaschutz-Punkte nur mit ≥ {0} % CO₂-frei", de(cfg['clean_thresholds'][3][0], 1))
        + (tr(" und ≤ {0} Mt CO₂", de(cfg['co2_mt_thresholds'][3][0], 0)) if cfg.get("co2_mt_thresholds") else "") + ".",
    ]


def stage_banner(cfg: dict, s: int):
    """Projector banner at the start of a stage: what is new, in big letters."""
    a = assumptions()
    ys = core.stage_years()
    y = ys[s]
    coal = a["existing_params"]["coal_max_mw"][y]
    items = [(tr("Verbrauch"), f"{de(demand_total_twh(y), 0)} TWh"
              + (f" ({'+' if demand_total_twh(y) >= demand_total_twh(ys[s - 1]) else ''}"
                 f"{de(100 * (demand_total_twh(y) / demand_total_twh(ys[s - 1]) - 1), 0)} %)" if s else "")),
             (tr("Spitzenlast"), f"{de(peak_demand_mw(y) / 1e3, 0)} GW"),
             (tr("Kohle höchstens"), gw(coal, 0)),
             (tr("CO₂-Preis"), f"{de(a['prices']['co2'][y], 0)} €/t")]
    if cfg.get("co2_mt_thresholds"):
        items.append((tr("CO₂-Ziel (5 Punkte)"), f"≤ {de(cfg['co2_mt_thresholds'][s][0], 0)} Mt"))
    items.append((tr("CO₂-frei (5 Punkte)"), f"≥ {de(cfg['clean_thresholds'][s][0], 0)} %"))
    note = _stage_notes(cfg)[s] if s < len(_stage_notes(cfg)) else ""
    with ui.card().classes("w-full ptz-card").style("background:#fffbeb;border-left:8px solid #d97706"):
        ui.label(tr("Stufe {0} ({1}): Das ist neu", s + 1, STAGE_LABELS[s])).classes("text-2xl font-extrabold")
        ui.html('<div style="display:flex;flex-wrap:wrap;gap:10px 28px;font-size:1.35rem">' + "".join(
            f'<div><span style="color:#6b7280">{k}</span> <b>{v}</b></div>' for k, v in items) + "</div>")
        if note:
            ui.label("⚠️ " + note).classes("text-xl").style("color:#92400e")


def stage_timeline(cfg: dict, current: int | None = None, team: dict | None = None, notes: bool = False):
    """Arrow-like stage overview (like the original game board), optionally with the team's points."""
    a = assumptions()
    years = core.stage_years()
    hist = {h["stage"]: h for h in (team or {}).get("history", [])}
    tips = _stage_notes(cfg) if notes else []
    with ui.row().classes("w-full gap-2 flex-nowrap overflow-x-auto"):
        for i, y in enumerate(years[:cfg["stages"]]):
            with ui.column().classes("ptz-stage gap-0 flex-1" + (" now" if i == current else "")):
                ui.label(tr("Stufe {0}", i + 1)).classes("text-xs font-bold ptz-muted")
                ui.label(STAGE_LABELS[i]).classes("ptz-h3")
                ui.html(tr("<div class=\"ptz-kv\" style=\"font-size:.85rem\"><span class=\"k\">Verbrauch</span><span class=\"v\">{0} TWh</span><span class=\"k\">Spitzenlast</span><span class=\"v\">{1} GW</span><span class=\"k\">Bau-Token</span><span class=\"v\">{2}</span><span class=\"k\">CO₂-Preis</span><span class=\"v\">{3} €/t</span>", de(demand_total_twh(y), 0), de(peak_demand_mw(y) / 1e3, 0), cfg["build_tokens"][i], de(a["prices"]["co2"][y], 0))
                        + (tr("<span class=\"k\">CO₂-Ziel</span><span class=\"v\">≤ {0} Mt</span>", de(cfg["co2_mt_thresholds"][i][0], 0)) if cfg.get("co2_mt_thresholds") else "")
                        + '</div>')
                if i < len(tips):
                    ui.label("⚠️ " + tips[i]).classes("text-sm mt-1").style("color:#92400e")
                if team is not None:
                    h = hist.get(i)
                    chips = "".join(
                        f'<span class="ptz-chip" style="background:{points_color(h["points"][k]) if h else "#d1d5db"}"'
                        f' title="{CAT[k][0]}">{h["points"][k] if h else "–"}</span> ' for k in CAT)
                    ui.html(f'<div class="mt-1">{chips}</div>')


def points_tables(cfg: dict, current: int | None = None):
    def num(v):
        return de(v, 1 if v % 1 else 0)

    def rows(table):
        return [[("▶ " if i == current else "") + str(i + 1)] + [num(v) for v in row] for i, row in enumerate(table)]
    head = [tr("Stufe"), tr("5 P."), "4", "3", "2", "1"]
    with ui.grid().classes("w-full gap-3 grid-cols-1 lg:grid-cols-3"):
        with ui.card().classes("ptz-card"):
            ui.label(tr("⚡ Versorgungssicherheit")).classes("ptz-h3").style(f"color:{CAT['reliability'][2]}")
            ui.label(tr("Stunden im Jahr, in denen Strom fehlt. Weniger ist besser.")).classes("ptz-muted")
            ui.label(tr("Höchstens … Stunden:")).classes("text-sm font-bold")
            _table(head, [[tr("alle")] + [num(v) for v in cfg["lole_thresholds"]]])
        with ui.card().classes("ptz-card"):
            ui.label(tr("🌿 Klimaschutz")).classes("ptz-h3").style(f"color:{CAT['clean'][2]}")
            mt = cfg.get("co2_mt_thresholds")
            ui.label(tr("Zwei Bedingungen – es zählt der schlechtere Wert. (1) Anteil CO₂-freier Strom: was in Deutschland sauber erzeugt wird; exportierter Ökostrom zählt mit, Importe nicht. ")
                     + (tr("(2) CO₂-Ausstoß in Deutschland (Mt pro Jahr) – die Grenze sinkt jede Stufe bis fast null (Klimaneutralität 2045). ") if mt else "")
                     + tr("5 Punkte = politisches Ziel erreicht.")).classes("ptz-muted")
            ui.label(tr("Anteil CO₂-frei, mindestens … %:")).classes("text-sm font-bold")
            _table(head, rows(cfg["clean_thresholds"]))
            if mt:
                ui.label(tr("CO₂-Ausstoß, höchstens … Mt:")).classes("text-sm font-bold mt-1")
                _table(head, rows(mt))
                ui.label(tr("Orientierung: 2030 Klimaschutzgesetz (Energiewirtschaft 108 Mt, davon Strom grob 70), 2035 G7-Zusage „Stromsektor weitgehend CO₂-frei“, 2040 Kohleausstieg und Ende der CO₂-Zertifikate im EU-Emissionshandel, 2045 Klimaneutralität (Abfallverbrennung allein ~5 Mt).")).classes("ptz-muted")
        with ui.card().classes("ptz-card"):
            ui.label(tr("💶 Bezahlbarkeit")).classes("ptz-h3").style(f"color:{CAT['cost'][2]}")
            ui.label(tr("Kosten für Anlagen, Brennstoff und CO₂ je MWh Strom (ohne Netz, Steuern, Abgaben). Investitionen werden auf ihre Lebensdauer verteilt und zählen auch in allen späteren Stufen. Weniger ist besser.")).classes("ptz-muted")
            ui.label(tr("Höchstens … €/MWh:")).classes("text-sm font-bold")
            _table(head, rows(cfg["cost_thresholds"]))
    ui.label(tr("Pro Stufe bis 15 Punkte, im ganzen Spiel {0}. Bei Gleichstand gewinnt das Team mit weniger CO₂.", 15 * cfg['stages'])).classes("ptz-sub")


def _have(team: dict | None, t: str, y: int) -> float:
    """Capacity of a buildable technology at the start of the stage (incl. the remaining old fleet)."""
    cap = team["cap"] if team else core.start_capacities()
    start = team["start_cap"] if team else cap
    aged = core.apply_ageing(cap, start, y)
    if t in ("onwind", "offwind"):
        return aged[t] + aged.get(t + "_old", 0.0)
    if t == "gas_new":
        return aged[t] + aged.get("gas_new_h2", 0.0)
    return aged.get(t, 0.0)


GLOSSARY = [
    ("Leistung (GW)", "Wie viel Strom in einem Moment fließen kann – wie weit ein Wasserhahn aufgedreht ist. "
                      "1 Gigawatt (GW) entspricht etwa einem großen Kraftwerk."),
    ("Energie (TWh)", "Wie viel Strom insgesamt über eine Zeit fließt – wie viel Wasser im Eimer landet. "
                      "Leistung mal Stunden. Deutschland verbraucht heute rund 500 Terawattstunden (TWh) im Jahr."),
    ("Spitzenlast", "Die Stunde mit dem höchsten Verbrauch im Jahr, meist an einem kalten Winterabend. So viel "
                    "Leistung muss dann bereitstehen."),
    ("Auslastung", "Wie viel eine Anlage im Jahresschnitt liefert, verglichen mit Volllast rund um die Uhr. "
                   "Ein Windrad an Land schafft etwa ein Viertel, eine Solaranlage etwa ein Zehntel."),
    ("Steuerbar", "Liefert Strom, wann man ihn braucht – z. B. Gas, Biomasse, Wasserstoff oder ein voller Speicher. "
                  "Wind und Sonne sind nicht steuerbar: Sie liefern nur, wenn das Wetter mitspielt."),
    ("Gesicherte Leistung", "Alle steuerbaren Kraftwerke zusammen (Gas, Wasserstoff, Kohle, Biomasse, Reserve). Darauf "
                            "könnt ihr auch zählen, wenn tagelang weder Wind weht noch Sonne scheint. Sie sollte über "
                            "der Spitzenlast liegen. Speicher und flexible Verbraucher helfen zusätzlich – aber nur für "
                            "einige Stunden. Wasserstoff-Turbinen zählen nur so weit, wie der Wasserstoff 2 Wochen "
                            "reicht."),
    ("Residuallast", "Verbrauch minus Wind- und Sonnenstrom – also der Rest, den steuerbare Anlagen, Speicher und "
                     "Importe liefern müssen."),
    ("Dunkelflaute", "Mehrere Tage mit wenig Wind und kaum Sonne, meist im Winter. Die härteste Probe für das "
                     "Stromsystem."),
    ("Versorgungslücke", "Eine Stunde, in der nicht genug Strom da ist. In Wirklichkeit müssten dann Verbraucher "
                         "abgeschaltet werden."),
    ("Speicher", "Nimmt Strom auf, wenn zu viel da ist, und gibt ihn ab, wenn er fehlt. Die Angabe „4 h“ heißt: Der "
                 "volle Speicher reicht 4 Stunden bei voller Leistung (bei halber Leistung 8 Stunden). Batterien und "
                 "Pumpspeicher reichen so für Stunden, Wasserstoff für Wochen."),
    ("Wasserstoff & Elektrolyse", "Elektrolyse macht aus Strom Wasserstoff. Der lässt sich in unterirdischen "
                                  "Salzhöhlen (Kavernen) über Wochen und Monate lagern und in umgerüsteten "
                                  "Gasturbinen ohne CO₂ wieder verbrennen. Dabei geht viel verloren: Nur etwa ein "
                                  "Viertel des Stroms kommt zurück. Die Elektrolyse ist teuer, der Speicher pro TWh "
                                  "vergleichsweise billig. Wasserstoff kann auch über Pipelines importiert werden "
                                  "(Wasserstoff-Kernnetz)."),
    ("Abregelung", "Wind- und Sonnenstrom, der gerade weder gebraucht, gespeichert noch exportiert werden kann. "
                   "Die Anlagen werden dann gedrosselt – der Strom ist verloren."),
    ("Import & Export", "Über Stromleitungen ins Ausland (Kuppelleitungen) kann Deutschland Strom kaufen (Import) "
                        "oder verkaufen (Export)."),
    ("Flexible Verbraucher", "Verbraucher, die mitdenken: Ein E-Auto lädt mittags statt abends, eine Wärmepumpe "
                             "heizt vor, eine Fabrik pausiert in teuren Stunden. Das senkt die Spitzenlast."),
    ("CO₂-Preis", "Was Kraftwerke für jede ausgestoßene Tonne CO₂ zahlen müssen. Macht Kohle und Gas teurer – und "
                  "steigt bis 2045."),
    ("CO₂-Ausstoß (Mt)", "Wie viel CO₂ die Kraftwerke in Deutschland in einem Jahr ausstoßen, in Millionen Tonnen "
                         "(Mt). Zum Vergleich: Die ganze Energiewirtschaft darf 2030 laut Klimaschutzgesetz noch 108 Mt "
                         "ausstoßen."),
    ("Klimaneutralität (Netto-Null)", "Ziel des Klimaschutzgesetzes für 2045: Deutschland stößt nicht mehr "
                                      "Treibhausgase aus, als Wälder, Moore und Technik wieder aufnehmen. Für den "
                                      "Stromsektor heißt das: Ausstoß fast null. Gezählt werden Tonnen – Ökostrom-"
                                      "Exporte gleichen nichts aus."),
    ("Anteil CO₂-frei", "Wie viel des Verbrauchs in Deutschland sauber erzeugt wird (Wind, Sonne, Wasser, Biomasse, "
                        "Wasserstoff). Exportierter Ökostrom zählt mit, Importe nicht. Gesetzliches Ziel 2030: 80 %."),
]


def build_rules(cfg: dict, current: int | None = None, team: dict | None = None):
    a = assumptions()
    years = core.stage_years()
    y_now = years[current or 0]
    tech = a["technologies"]
    tok = de(cfg["token_value_bn"], 0)

    # ------------------------------------------------------------------ summary + contents
    ui.label(tr("📖 Spielregeln")).classes("ptz-h1")
    with ui.element("div").classes("ptz-insight w-full"):
        ui.markdown(
            tr("Ihr plant als Team den Strom für Deutschland bis 2045 – in **vier Stufen**. In jeder Stufe baut ihr neue Anlagen und entscheidet über alte Kraftwerke. Dann rechnet der Computer ein ganzes Jahr Stunde für Stunde durch. Punkte gibt es für drei Ziele: **⚡ immer genug Strom**, **🌿 Klimaschutz** (sauberer Strom und wenig CO₂) und **💶 möglichst günstig** – je bis zu 5 Punkte pro Stufe, insgesamt höchstens {0}.\n\n**Kurz gesagt:** Deckt den Bedarf zu jeder Stunde, macht den Strom sauber, achtet auf die Kosten – und plant Puffer für das ein, was ihr nicht vorhersehen könnt.", 15 * cfg['stages']))
    toc = ui.row().classes("w-full gap-1 items-center")
    secs = []

    def section(title: str, intro: str = ""):
        secs.append((title, _section(len(secs) + 1, title, intro)))

    # ------------------------------------------------------------------ 1 flow
    section(tr("So läuft eine Stufe"))
    steps = [("construction", tr("Bauen"), tr("Bau-Token auf neue Anlagen verteilen, alte Kraftwerke behalten oder stilllegen.")),
             ("insights", tr("Testen"), tr("Mit dem Simulator ausprobieren ({0}× pro Stufe). Er rechnet ohne Zufall.", cfg['simulations_per_stage'])),
             ("check_circle", tr("Fertig melden"), tr("Ändern geht noch, bis die Spielleitung die Bauphase schließt. Danach gilt es.")),
             ("casino", tr("Jahr simulieren"), tr("Für alle gleich: Wetter, Verbrauch, vielleicht eine Katastrophe.")),
             ("emoji_events", tr("Punkte"), tr("Ergebnisse ansehen – dann geht es in die nächste Stufe."))]
    with ui.row().classes("w-full gap-2"):
        for i, (icon, title, txt) in enumerate(steps):
            with ui.card().classes("ptz-card flex-1 min-w-[160px]"):
                with ui.row().classes("items-center gap-2 no-wrap"):
                    ui.icon(icon, size="sm").classes("text-blue-700")
                    ui.label(f"{i + 1}. {title}").classes("ptz-h3")
                ui.label(txt).classes("ptz-muted")

    # ------------------------------------------------------------------ 2 screen
    section(tr("Euer Bildschirm"))
    screen = [("construction", tr("Bauen"), tr("Anlagen bauen und alte Kraftwerke behalten. Rechts „Dein Kraftwerkspark“: Liegt die gesicherte Leistung über der Spitzenlast?")),
              ("how_to_vote", tr("Einfluss"), tr("Einfluss-Token für Maßnahmen wie Wasserstoff oder Akzeptanz einsetzen.")),
              ("insights", tr("Simulator"), tr("Probelauf eures Plans mit Diagramm.")),
              ("emoji_events", tr("Ergebnisse"), tr("Was im Jahr wirklich passiert ist – mit Punkten und Diagrammen.")),
              ("timeline", tr("Verlauf"), tr("Eure Punkte und Entscheidungen aller Stufen.")),
              ("toll", tr("Kopfzeile"), tr("Bau-Token als Kästchen (gefüllt = verplant, orange = Kredit) und eure Punkte."))]
    with ui.grid().classes("w-full gap-2 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"):
        for icon, title, txt in screen:
            with ui.row().classes("ptz-card p-2 gap-2 no-wrap items-start"):
                ui.icon(icon, size="sm").classes("text-blue-700 mt-1")
                with ui.column().classes("gap-0"):
                    ui.label(title).classes("font-bold")
                    ui.label(txt).classes("ptz-muted")

    # ------------------------------------------------------------------ 3 points
    section(tr("Ziele & Punkte"), tr("Jede Stufe gibt bis zu 5 Punkte pro Ziel. Die Ziele werden von Stufe zu Stufe strenger."))
    points_tables(cfg, current)

    # ------------------------------------------------------------------ 4 stages
    section(tr("Die vier Stufen"), tr("Der Verbrauch wächst durch Wärmepumpen, E-Autos und Industrie."))
    stage_timeline(cfg, current, team, notes=True)
    ui.label(tr("Verbrauch inklusive Netzverluste, ohne Elektrolyse. Spitzenlast im normalen Wetterjahr – in kalten Wintern liegt sie höher.")).classes("ptz-muted")

    # ------------------------------------------------------------------ 5 tokens
    section(tr("Token"))
    _table([tr("Token"), tr("Was es ist")], align="ll", rows=[
        [tr("<b>Bau-Token</b>"), tr("{0} Mrd. € für neue Anlagen. Je Stufe: {1} – vorne mehr, weil dort am meisten gebaut werden muss. <b>Verfallen am Ende der Stufe</b> – also aufbrauchen.", tok, ' / '.join(str(n) for n in cfg['build_tokens']))],
        [tr("<b>Kredit-Token</b>"), tr("Bis zu {0} zusätzliche Bau-Token pro Stufe, kosten {1} % mehr.", cfg['max_borrow_tokens'], de(cfg['borrow_premium'] * 100, 0))],
        [tr("<b>Einfluss-Token</b>"), tr("{0} zu Beginn, weitere für je {1} Bau-Token. Schalten eine Maßnahme frei – jede nur einmal im Spiel. Je früher, desto länger wirkt sie.", cfg['influence_tokens_start'], cfg['influence_token_price'])],
    ])
    infl_rows = []
    for group, keys in core.INFLUENCE_GROUPS:
        infl_rows.append([f'<span style="color:#581c87;font-weight:700">{tr(group)}</span>', ""])
        for k in keys:
            n, d = core.INFLUENCE[k]
            infl_rows.append([f"<b>{n}</b>", d + (f'<br><span class="ptz-muted">{core.INFLUENCE_DETAIL[k]}</span>'
                                                  if k in core.INFLUENCE_DETAIL else "")])
    _table([tr("Maßnahme"), tr("Wirkung")], infl_rows, "ll")

    # ------------------------------------------------------------------ 6 new technologies
    section(tr("Neue Anlagen"), tr("Werte für {0}. 1 Bau-Token = {1} Mrd. €.", STAGE_LABELS[current or 0], tok))
    cf = capacity_factors(y_now)
    rows = []
    for t in core.NEW_TECHS:
        mw = (core.mw_per_token(team, t, y_now, cfg) if team is not None
              else cfg["token_value_bn"] * 1e9 / (tech[t]["invest"][y_now] * 1e3))
        use = {"battery": tr("Speicher (4 h Volllast)"), "h2_package": tr("nach Überschuss"), "h2_storage": tr("Wochen–Monate"),
               "gas_new": tr("steuerbar"), "biomass_flex": tr("steuerbar")}.get(t) or f"{de(cf[t], 0)} %"
        fmt = (lambda v: f"{de(v / 1e6, 1)} TWh H₂") if t == "h2_storage" else gw
        rows.append([f'<span style="color:{tcolor(t)}">■</span> <b>{core.LABELS[t]}</b>', f"+{fmt(mw)}",
                     fmt(_have(team, t, y_now)), use, RISK_DE[cfg["backlash_risk"][t]], tdesc(t)])
    _table([tr("Anlage"), tr("pro Token"), tr("vorhanden"), tr("Auslastung"), tr("Protest-Risiko"), tr("Wofür?")], rows, "lrrrrl")
    _bullets([
        tr("**Wasserstoff braucht drei Bausteine:** **Elektrolyse** macht Wasserstoff aus deutschem Ökostrom-Überschuss (nicht aus Import- oder Kohle-/Gasstrom), der **Speicher** (Salzkaverne) bewahrt ihn über Wochen auf, **umgerüstete Gasturbinen** machen daraus wieder Strom (nur etwa ein Viertel kommt zurück). Zwei Einfluss-Karten, jeweils ab der Stufe danach: „Demonstrationsprogramm Wasserstoff“ = eigener grüner Wasserstoff (Elektrolyse, Speicher, Umrüstung); „Wasserstoff-Netz & Import“ = teurer Wasserstoff von außen (Speicher, Umrüstung, Import, aber keine Elektrolyse). Beide zusammen kosten zwei Token. Die Import-Leistung ist in GW Wasserstoff angegeben – daraus wird nur etwa 40 % Strom. Das Spiel zeigt an, für wie viele Tage euer Speicher reicht."),
        tr("**Biomasse-Flexibilisierung:** gleiche Menge Biogas, aber mehr Leistung genau dann, wenn Strom knapp ist (höchstens das Dreifache der weiterbetriebenen Biomasse)."),
        tr("**Alte Wind- und Solaranlagen** gehen nach und nach vom Netz. Die Kacheln im Bauen-Tab zeigen, wie viel in der nächsten Stufe noch läuft."),
        tr("**Lerneffekt:** Was ihr baut, wird für euch in den nächsten Stufen etwas billiger."),
    ])

    # ------------------------------------------------------------------ 7 existing & fixed
    section(tr("Alte Kraftwerke & feste Anlagen"), tr("Alte Kraftwerke könnt ihr behalten oder stilllegen – Stilllegen ist endgültig, Behalten kostet Betriebskosten."))
    ex = a["existing"]
    coal_max = a["existing_params"]["coal_max_mw"]
    _table([tr("Kraftwerk"), tr("heute"), tr("Protest-Risiko"), tr("Hinweis")], align="lrrl", rows=[
        [tr("Kohle (Braun- & Steinkohle)"), gw(ex["lignite"] + ex["hard_coal"]), RISK_DE[cfg["backlash_risk"]["coal"]],
         tr("läuft immer mit mindestens 15 % Leistung (Fernwärme, Tagebau) und ändert die Leistung höchstens um 40 % pro Stunde. Kohleausstieg per Gesetz: höchstens ") + ", ".join(f"{gw(coal_max[y], 0)} ({y})" for y in years)],
        [tr("Gaskraftwerke"), gw(ex["gas"]), RISK_DE[cfg["backlash_risk"]["gas"]], tr("steuerbar, stoßen CO₂ aus")],
        [tr("Biomasse/Biogas"), gw(ex["biomass"]), RISK_DE[cfg["backlash_risk"]["biomass"]],
         tr("steuerbar, aber nur ~{0} TWh im Jahr", de(a['existing_params']['biomass']['energy_twh'], 0))],
    ])
    fx = {y: fixed_capacities(y) for y in years}
    ui.label(tr("Feste Anlagen – hat jedes Team, nicht veränderbar. Sie folgen einem festen Fahrplan: alte Anlagen gehen vom Netz, die Leitungen ins Ausland werden automatisch ausgebaut.")).classes("ptz-h3 mt-2")

    def plan(vals):
        return [gw(v, 1) for v in vals]
    _table([tr("Anlage")] + [str(y) for y in years] + [tr("Hinweis")], align="lrrrrl", rows=[
        [tr("Pumpspeicher")] + plan(fx[y]["phs"] for y in years)
        + [tr("Energieinhalt reicht für ca. {0} Stunden bei voller Leistung", a['fixed_blocks']['phs']['hours'])],
        [tr("Alte Großbatterien")] + plan(fx[y]["battery_old"] for y in years)
        + [tr("Energieinhalt für ca. 1 Stunde bei voller Leistung; altern bis 2045 weg")],
        [tr("Laufwasser")] + plan(ex["ror"] for y in years) + [tr("klein, recht gleichmäßig, CO₂-frei")],
        [tr("Abfallverbrennung")] + plan(fx[y]["waste"] for y in years) + [tr("läuft immer, zur Hälfte erneuerbar")],
        [tr("Öl & sonstige")] + plan(fx[y]["other_fossil"] for y in years) + [tr("teuer, nur bei Knappheit")],
        [tr("Reservekraftwerke")] + plan(fx[y]["reserve"] for y in years) + [tr("nur im Notfall, fossil")],
        [tr("Leitungen ins Ausland")] + plan(trade_capacity(y) for y in years)
        + [tr("höchstens so viel Import oder Export; +{0} mit „Netzausbau Europa“ (ab der Folgestufe)", gw(a['trade']['grid_eu_bonus_mw'], 0))],
    ])

    # ------------------------------------------------------------------ 8 chance
    section(tr("Zufall & Risiken"), tr("Wetter, Verbrauch und Katastrophen sind für alle Teams gleich. Lerneffekte und Proteste treffen jedes Team einzeln."))
    _bullets([
        tr("**Wetter:** meist ein normales Jahr ({0}), manchmal ein schwieriges ({1}: weniger Wind), selten ein extremer Winter ({2}: lange Kälte, kaum Wind).", a['normal_weather_year'], a['harder_weather_year'], a['extreme_weather_year']),
        tr("**Verbrauch:** kann einige Prozent höher oder niedriger sein als erwartet."),
        tr("**Katastrophen** werden von Stufe zu Stufe wahrscheinlicher: *Sturm/Hochwasser* – für jede Technologie wird einzeln gewürfelt, getroffene liefern 4 Wochen nur halb so viel. *Kalte Dunkelflaute* – 2 Wochen kaum Wind und Sonne. *Hitze & Dürre* – Kraftwerke mit Kühlwasser (Gas, Kohle, Biomasse) liefern weniger, Laufwasser auch. Wind, Sonne und Speicher trifft es nicht."),
        tr("**Nachbarländer** helfen mit Strom aus – aber nicht, wenn in ganz Europa gleichzeitig Flaute ist. Überschuss nehmen sie zum Teil ab (z. B. für ihre Wasserkraft-Speicher) und geben ihn später teurer zurück. Exportierter Ökostrom zählt für den CO₂-frei-Anteil, importierter Strom nicht. Beim CO₂-Ausstoß zählt nur, was in Deutschland ausgestoßen wird – Exporte helfen dort nicht."),
        tr("**Protest (Gegenreaktion):** Jeder Bau-Token kann Protest auslösen. *Neue Anlage:* Das Gebaute läuft weiter, aber in der nächsten Stufe dürft ihr davon nichts dazubauen. *Altes Kraftwerk:* muss in der nächsten Stufe ganz stillgelegt werden."),
        tr("**Letzte Stufe:** Jeder Protest gegen eine neue Anlage kostet {0} Punkte – damit am Ende niemand bedenkenlos alles vollbaut.", cfg['final_backlash_penalty']),
    ])

    # ------------------------------------------------------------------ 9 tips
    section(tr("Tipps für den Start"))
    ui.markdown(
        tr("1. **Erst testen, dann fertig melden.** Der Simulator kennt keinen Zufall – plant Reserve ein.\n2. **Bau-Token aufbrauchen** – übrige verfallen.\n3. **Wind und Sonne allein reichen nicht.** An windstillen Winterabenden muss trotzdem Strom da sein. Haltet die gesicherte Leistung über der Spitzenlast.\n4. **Batterien helfen für Stunden, nicht für Wochen.** Für lange Flauten braucht ihr Gas, Biomasse oder Wasserstoff.\n5. **Früh an Wasserstoff denken:** Er wirkt erst eine Stufe nach dem Einfluss-Token. Eigener Wasserstoff braucht drei Bausteine (Elektrolyse, Speicher, umgerüstete Gasturbinen), Import das Wasserstoff-Netz. Ohne Wasserstoff wird 2045 kaum klimaneutral.\n6. **Stufe 2 ist der große Sprung:** viel mehr Verbrauch, viel weniger Kohle – schon in Stufe 1 vorsorgen.\n7. **CO₂ Stufe für Stufe senken:** Die Grenze für den Ausstoß sinkt jede Stufe (oben in der Übersicht: „CO₂-Ziel“). Gaskraftwerke laufen, wann immer sie gebraucht werden – weniger CO₂ gibt es nur mit mehr Ökostrom, Speichern, Wasserstoff-Umrüstung oder durch Stilllegen alter Kraftwerke.")
    ).classes("w-full")

    # ------------------------------------------------------------------ 10 model
    section(tr("Wie rechnet das Modell?"))
    with ui.expansion(tr("Für Interessierte anzeigen"), icon="calculate").classes("w-full ptz-card"):
        _bullets([
            tr("Deutschland als ein Netz ohne Engpässe, alle **8.760 Stunden** eines Jahres. Die Nachbarländer sind vereinfacht als ein Markt abgebildet, mit ihrem eigenen Wetter und Verbrauch, einem Speicher (Wasserkraft in Norwegen und den Alpen) und einer festen Abnahme für deutschen Überschuss."),
            tr("In jeder Stunde laufen die **günstigsten** Anlagen zuerst. Speicher laden bei Überschuss und liefern bei Knappheit. Das Modell kennt das ganze Jahr im Voraus."),
            tr("**Kosten** = Investitionen (verteilt über die Lebensdauer, 5 % Zins) + Betriebskosten + Brennstoff und CO₂ + Importe − Exporterlöse + Kredit- und Einfluss-Kosten, geteilt durch den Verbrauch. Alte Anlagen zählen nur mit ihren Betriebskosten. Fehlender Strom wird als Schaden angezeigt (10.000 €/MWh), kostet aber nur Versorgungs-Punkte, keine Kosten-Punkte."),
            tr("**CO₂-frei** = (Verbrauch + Export − Import − fossiler Strom) ÷ Verbrauch, höchstens 100 %. CO₂-frei sind Wind, Sonne, Wasser, Biomasse, Wasserstoff und die Hälfte der Abfallverbrennung."),
            tr("**CO₂-Ausstoß** zählt nur in Deutschland, wie im Klimaschutzgesetz. Das CO₂ der Importe wird getrennt angezeigt."),
            tr("**Klimaschutz-Punkte** = der schlechtere Wert aus den Punkten für den Anteil und für den Ausstoß. So helfen Exporte nicht gegen zu viel CO₂ und Importe nicht gegen einen zu kleinen Anteil."),
            tr("Daten: ENTSO-E TYNDP 2024 (Wetter, Verbrauch, Preise), Bundesnetzagentur (Kraftwerke), PyPSA technology-data (Kosten)."),
        ])

    # ------------------------------------------------------------------ 11 glossary
    section(tr("Glossar – Begriffe einfach erklärt"))
    _table([tr("Begriff"), tr("Bedeutung")], [[f"<b>{tr(k)}</b>", tr(v)] for k, v in GLOSSARY], "ll")

    # ------------------------------------------------------------------ contents (filled now that sections exist)
    with toc:
        ui.label(tr("Springe zu:")).classes("ptz-muted mr-1")
        for title, el in secs:
            ui.button(title.split(" – ")[0], on_click=lambda e=el: ui.run_javascript(
                f'document.getElementById("{e.html_id}").scrollIntoView({{behavior: "smooth"}})')).props(
                "flat dense no-caps color=primary")
