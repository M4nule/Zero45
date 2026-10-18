# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Team view (also used in single-player mode)."""
from __future__ import annotations

import math
import time

from nicegui import ui

from ptz.engine.model import assumptions, capacity_factors, demand_total_twh, fixed_capacities, peak_demand_mw
from ptz.game import core, runner
from ptz.server import charts, rules
from ptz.server.runtime import Runtime
from ptz.server.theme import (CAT, CSS, RISK_COLOR, RISK_DE, SEP, de, gw, points_color, tcolor, tdesc,
                              ticon, SCROLL_JS)
from ptz.i18n import TDict, tr

STAGE_LABELS = rules.STAGE_LABELS
PHASE_DE = TDict({"lobby": "Warten auf Start", "build": "Bauphase", "resolving": "Wird berechnet …",
                 "results": "Ergebnisse", "finished": "Spiel beendet"})
COST_LABEL = "Erzeugungs- und Speicherkosten"
COST_NOTE = "ohne Netze, Umlagen, Steuern"
INFLUENCE_ICONS = {"resilience": "shield", "innovation": "rocket_launch", "h2_demo": "science", "social": "groups",
                   "h2_grid": "hub",
                   "grid_eu": "public", "flex": "electric_car"}
EVENT_ICONS = {"storm": "thunderstorm", "dunkelflaute": "dark_mode", "heat": "thermostat"}
SECTIONS = [
    ("Wind & Sonne", "Günstige Energie – aber nur, wenn Wind weht oder die Sonne scheint.",
     ["onwind", "offwind", "solar_utility", "solar_rooftop"]),
    ("Speicher & Flexibilität", "Verschieben Strom von Überschuss- in Knappheitsstunden.", ["battery", "biomass_flex"]),
    ("Steuerbare Kraftwerke", "Liefern auch bei Dunkelflaute – mit Erdgas oder, umgerüstet, mit Wasserstoff.",
     ["gas_new"]),
    ("Wasserstoff", "Drei Bausteine, die zusammenpassen müssen: Elektrolyse macht aus Überschussstrom Wasserstoff, "
                    "der Speicher bewahrt ihn für Wochen auf, umgerüstete Gasturbinen machen wieder Strom daraus.",
     ["h2_package", "h2_storage"]),
]


def amount(tech: str, mw: float, d: int = 1) -> str:
    """Capacity with unit: GW, or TWh hydrogen for the storage (stored in MWh)."""
    return f"{de(mw / 1e6, d)} TWh H₂" if tech == "h2_storage" else gw(mw, d)


def kv(rows: list[tuple[str, str]]):
    """Label–value grid (no user-provided text in here)."""
    inner = "".join(f'<span class="k">{k}</span><span class="v">{v}</span>' for k, v in rows)
    ui.html(f'<div class="ptz-kv">{inner}</div>').classes("w-full")


def section_title(no: int, title: str, intro: str = ""):
    with ui.row().classes("items-center ptz-section w-full gap-0"):
        ui.html(f'<span class="ptz-sec-no">{no}</span>')
        ui.label(title).classes("ptz-h2").style("margin-top:0")
    if intro:
        ui.label(intro).classes("ptz-sub")


def info_button(html: str):
    """Small (i) button; a click opens the details (works with mouse and touch). html: own text only."""
    with ui.button(icon="info_outline").props("flat round dense size=sm color=grey-7").classes("shrink-0"):
        with ui.menu().props("anchor='bottom left' self='top left'"):
            ui.html(f'<div class="text-sm" style="max-width:340px;padding:10px 12px;line-height:1.4">{html}</div>')


def risk_badge(risk: str):
    ui.badge(tr("Risiko {0}", RISK_DE[risk]), color=RISK_COLOR[risk]).props("outline").classes("text-xs")


def points_box(key: str, pts: int, value: str, target: str):
    label, icon, color = CAT[key]
    with ui.card().classes("ptz-card flex-1 min-w-[200px]").style(f"border-top: 5px solid {color}"):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            with ui.row().classes("items-center gap-1 no-wrap"):
                ui.icon(icon).style(f"color:{color}")
                ui.label(label).classes("ptz-h3")
            ui.html(f'<span class="ptz-pts" style="background:{points_color(pts)}">{pts} / 5</span>')
        ui.label(value).classes("ptz-big ptz-num")
        ui.label(target).classes("ptz-muted")


def sim_compare(res: dict):
    """One line: what changed against the previous simulator test of this stage."""
    p, sm, ev = res["prev"], res["summary"], res["eval"]
    now_pts, old_pts = sum(ev["points"].values()), sum(p["points"].values())

    def arrow(old, new, unit, d=0, lower_better=True):
        if abs(new - old) < 0.5 * 10 ** -d:
            return tr("{0} {1} (gleich)", de(new, d), unit)
        good = (new < old) == lower_better
        col = "#15803d" if good else "#b91c1c"
        return f'{de(old, d)} → <b style="color:{col}">{de(new, d)}</b> {unit}'
    parts = [tr("Punkte {0}", arrow(old_pts, now_pts, '', 0, lower_better=False)),
             tr("Lücke {0}", arrow(p['lole'], sm['lole_hours'], 'h')),
             tr("CO₂ {0}", arrow(p['co2'], sm['co2_mt'], 'Mt', 1)),
             tr("CO₂-frei {0}", arrow(p['share'], sm['clean_share'], '%', 1, lower_better=False)),
             tr("Kosten {0}", arrow(p['eur'], ev['cost']['eur_per_mwh'], '€/MWh'))]
    ui.html(tr("<div class=\"ptz-card w-full\" style=\"padding:10px 14px;background:#eff6ff\"><b>Im Vergleich zum Test von {0} Uhr:</b> {1}</div>", time.strftime("%H:%M", time.localtime(p["time"])), SEP.join(parts))).classes("w-full")


def results_block(summary: dict, ev: dict, stage: int, cfg: dict, disp=None, sim: bool = False,
                  compare: str | None = None):
    """Three big category boxes, "Warum?" lines and details."""
    pts, c = ev["points"], ev["cost"]
    def target(p: int, parts: list[tuple[list, str]]) -> str:
        """Next better level instead of only the 5-point limit. parts: (thresholds for 5..1 points, format)."""
        if p >= 5:
            return tr("✔ Ziel erreicht")
        nxt = tr(" und ").join(f.format(de(th[4 - p], 0 if float(th[4 - p]).is_integer() else 1)) for th, f in parts)
        if p == 4:
            return tr("Für 5 P.: {0}", nxt)
        top = tr(" und ").join(f.format(de(th[0], 0 if float(th[0]).is_integer() else 1)) for th, f in parts)
        return tr("Für {0} P.: {1} (5 P.: {2})", p + 1, nxt, top)

    with ui.row().classes("w-full gap-3"):
        points_box("reliability", pts["reliability"], tr("{0} h mit Lücke", summary['lole_hours']),
                   tr("{0}{1}nicht gedeckt: {2} TWh", target(pts['reliability'], [(cfg['lole_thresholds'], '≤ {} h')]), SEP, de(summary['unserved_twh'], 2)))
        det = ev.get("clean_detail") or {}
        mt = cfg.get("co2_mt_thresholds")
        share_part = (cfg["clean_thresholds"][stage], "≥ {} %")
        mt_part = (mt[stage], "≤ {} Mt") if mt else None
        if "co2" in det and mt_part:
            limiting = [x for x, k in ((share_part, "share"), (mt_part, "co2")) if det[k] == pts["clean"]]
            cond = target(pts["clean"], limiting or [share_part, mt_part])
            worse = (tr("Anteil") if det["share"] < det["co2"] else tr("Ausstoß")) if det["share"] != det["co2"] else ""
            cond += (tr("{0}Anteil {1} P., Ausstoß {2} P.", SEP, det['share'], det['co2'])
                     + (tr(" → es zählt der {0}", worse) if worse else ""))
        else:
            cond = target(pts["clean"], [share_part])
        points_box("clean", pts["clean"], tr("{0} % | {1} Mt", de(summary['clean_share']), de(summary['co2_mt'])), cond)
        points_box("cost", pts["cost"], tr("{0} €/MWh", de(c['eur_per_mwh'], 0)),
                   f"{target(pts['cost'], [(cfg['cost_thresholds'][stage], '≤ {} €/MWh')])}{SEP}{tr(COST_LABEL)} ({tr(COST_NOTE)})")
    if compare:
        ui.html(compare).classes("w-full")
    lines = runner.insights(summary, disp, c)
    tips = core.stage_tip(cfg, stage, summary, ev, ev.get("cap"), sim=sim)
    if lines or tips:
        ui.label(tr("Warum?")).classes("ptz-h3 mt-2")
        with ui.column().classes("w-full gap-1"):
            for line in tips:
                ui.label("💡 " + line).classes("ptz-insight w-full").style(
                    "border-left-color:#ca8a04;background:#fefce8;font-weight:600")
            for line in lines:
                ui.label(line).classes("ptz-insight w-full")
    with ui.row().classes("w-full gap-2"):
        with ui.expansion(tr("Kennzahlen"), icon="list").classes("flex-1 min-w-[260px] ptz-card"):
            kv([(tr("Größte Lücke"), f"{de(summary['max_unserved_gw'])} GW"),
                (tr("Spitzenlast"), f"{de(summary['peak_demand_gw'])} GW"),
                (tr("Verbrauch"), f"{de(summary['demand_twh'], 0)} TWh"),
                (tr("CO₂ je kWh Strom"), tr("{0} g (heute ~{1} g, UBA {2})", de(core.co2_intensity(summary), 0), core.CO2_INTENSITY_TODAY[1], core.CO2_INTENSITY_TODAY[0])),
                (tr("Abregelung"), f"{de(summary['curtailment_twh'])} TWh"),
                (tr("Elektrolyse"), f"{de(summary['electrolyser_twh'])} TWh"),
                (tr("Wasserstoff-Import"), f"{de(summary.get('h2_import_twh', 0))} TWh H₂"),
                (tr("Import"), f"{de(summary.get('import_twh', 0))} TWh"),
                (tr("Export"), f"{de(summary.get('export_twh', 0))} TWh")])
        with ui.expansion(tr("{0} im Detail", tr(COST_LABEL)), icon="euro").classes("flex-1 min-w-[260px] ptz-card"):
            kv([(tr("Investitionen (Rate)"), f"{de(c['capex_bn'])} Mrd. €"),
                (tr("Fixe Betriebskosten"), f"{de(c['fom_bn'])} Mrd. €"),
                (tr("Brennstoff, CO₂, variabel"), f"{de(c['opex_bn'])} Mrd. €"),
                (tr("Kreditaufschlag"), f"{de(c['borrow_bn'])} Mrd. €"),
                (tr("Summe pro Jahr"), f"{de(c['total_bn'])} Mrd. €")]
               + ([(tr("Dazu: Schaden durch Versorgungslücken"), f"{de(c.get('blackout_bn', 0))} Mrd. €")]
                  if c.get("blackout_bn", 0) > 0.005 else []))
            ui.label(tr("Nicht mit dem Strompreis vergleichbar ({0}). Der Schaden durch Versorgungslücken (10.000 €/MWh) zählt nur bei der Versorgung, nicht bei den Kosten-Punkten.", tr(COST_NOTE))).classes(
                "ptz-muted")
        with ui.expansion(tr("Stromerzeugung (TWh)"), icon="bolt").classes("flex-1 min-w-[260px] ptz-card"):
            g = summary["generation_twh"]
            rows = []
            for k, v in g.items():
                if v <= 0.05 or k.endswith("_old"):
                    continue
                rows.append((runner.SERIES_LABELS.get(k, k), de(v)))
                if g.get(f"{k}_old", 0) > 0.05:      # existing fleet directly below its technology, indented
                    rows.append((tr("&nbsp;&nbsp;&nbsp;↳ davon Bestand"), f'<span class="ptz-muted">{de(g[k + "_old"])}</span>'))
            kv(rows)


def dispatch_panel(disp, event: dict | None, title: str):
    """Dispatch chart with full-year view, week slider and shortcut buttons."""
    shortcuts = runner.week_shortcuts(disp, event)
    state = {"start": None}
    plot = ui.plotly(charts.as_plot(charts.dispatch_figure(disp, None, title))).classes("w-full")
    ui.label(tr("Tipp: Doppelklick auf einen Eintrag in der Legende zeigt nur diese Gruppe; Einfachklick blendet sie aus.")).classes("ptz-muted")

    def show(start):
        state["start"] = start
        plot.update_figure(charts.as_plot(charts.dispatch_figure(disp, start, title)))
        if start is not None:
            slider.value = start // 168 + 1

    with ui.row().classes("items-center gap-2 w-full flex-wrap"):
        ui.button(tr("Ganzes Jahr"), on_click=lambda: show(None)).props("dense outline")
        for name, start in shortcuts.items():
            ui.button(name, on_click=lambda s=start: show(s)).props("dense outline color=primary")
    with ui.row().classes("items-center w-full no-wrap"):
        ui.label(tr("Woche wählen")).classes("ptz-muted")
        slider = ui.slider(min=1, max=52, step=1, value=1).props("label").classes("flex-1 max-w-md")

        def on_week(e):
            try:
                wk = int(min(max(float(e.args), 1), 52))
            except (TypeError, ValueError, OverflowError):
                return
            start = (wk - 1) * 168
            if state["start"] is None or state["start"] // 168 != wk - 1:
                state["start"] = start
                plot.update_figure(charts.as_plot(charts.dispatch_figure(disp, start, title)))
        slider.on("update:model-value", on_week, throttle=0.3)
    return plot


def build_player(rt: Runtime, tid: str, solo: bool = False):
    st = rt.state
    cfg = st["cfg"]
    a = assumptions()
    ui.add_head_html(CSS + SCROLL_JS)
    ui_state = {"tab": "Bauen", "fp": None, "hist_seen": len(st["teams"][tid]["history"]), "overview": st["stage"] == 0}

    def team():
        return st["teams"][tid]

    def year():
        return core.stage_years()[st["stage"]]

    def notify_err(err):
        if err:
            ui.notify(err, type="warning")
        return err

    def bump():
        t = team()
        t["rev"] = t.get("rev", 0) + 1
        rt.touch()
        ui_state["fp"] = fingerprint()   # this device is already up to date

    def keep_scroll():
        """Put the page back where it was when the button was pressed (see SCROLL_JS)."""
        ui.run_javascript("window.ptzKeepScroll && window.ptzKeepScroll()")

    def act(fn, *args):
        err = fn(st, tid, *args)
        if not notify_err(err):
            bump()
            header.refresh()
            if ui_state["tab"] == "Bauen" and st["phase"] == "build":
                build_tab.refresh()      # only the cards, not tabs/overview: keeps the page still
            else:
                body.refresh()
            keep_scroll()

    def act_quiet(fn, *args, after=None):
        """For sliders: apply without rebuilding the tab (a rebuild would interrupt dragging)."""
        err = fn(st, tid, *args)
        if notify_err(err):
            body.refresh()
            return
        bump()
        header.refresh()
        portfolio_panel.refresh()
        if after:
            after()

    def slider_value(e) -> float | None:
        try:
            v = float(e.args)
        except (TypeError, ValueError):
            return None
        return v if math.isfinite(v) else None

    # ---------------------------------------------------------------- sticky header
    @ui.refreshable
    def header():
        t = team()
        s = st["stage"]
        with ui.row().classes("w-full items-center justify-between no-wrap gap-3"):
            with ui.column().classes("gap-0 flex-1 overflow-hidden").style("min-width:6.5rem"):
                ui.label(f"⚡ {t['name']}").classes("text-lg font-extrabold truncate w-full")
                ui.label(tr("Stufe {0}/{1}{2}{3}{4}{5}", s + 1, cfg['stages'], SEP, STAGE_LABELS[s], SEP, PHASE_DE[st['phase']])).classes(
                    "ptz-sub text-sm")
            if st["phase"] == "build":
                total, left = core.tokens_total(st, tid), core.tokens_left(st, tid)
                used = total - left
                base = cfg["build_tokens"][s] - t["draft"]["influence_bought"] * cfg["influence_token_price"]
                squares = []
                for i in range(total):
                    cls = "ptz-tok" + (" used" if i < used else "") + (" credit" if i >= base else "")
                    squares.append(f'<span class="{cls}"></span>')
                with ui.column().classes("items-center gap-0 min-w-0").style("max-width:46vw"):
                    ui.label(tr("Bau-Token: {0} von {1} übrig", left, total)).classes("text-sm font-bold text-center")
                    ui.html(tr("<div style=\"max-width:min(340px,100%);line-height:0\">{0}</div>", "".join(squares)))
            with ui.column().classes("items-end gap-0 shrink-0"):
                ui.label(tr("Punkte")).classes("ptz-muted")
                ui.label(str(core.total_points(t))).classes("ptz-big")

    # ---------------------------------------------------------------- overview strip
    @ui.refreshable
    def overview():
        if ui_state.get("ov_stage") != st["stage"]:     # new stage: open only in stage 1, later collapsed
            ui_state.update(ov_stage=st["stage"], overview=st["stage"] == 0)
        with ui.expansion(tr("Übersicht: Stufen & deine Punkte"), icon="timeline", value=ui_state["overview"],
                          on_value_change=lambda e: ui_state.update(overview=e.value)).classes("w-full ptz-card"):
            rules.stage_timeline(cfg, st["stage"], team())

    # ---------------------------------------------------------------- portfolio panel
    @ui.refreshable
    def portfolio_panel():
        t = team()
        before = core.cap_groups(core.stage_start_cap(st, tid))
        cap = core.portfolio(st, tid)
        after = core.cap_groups(cap)
        mx = max(max(after.values()), max(before.values()), 1)
        with ui.card().classes("ptz-card w-full"):
            ui.label(tr("Dein Kraftwerkspark")).classes("ptz-h3")
            ui.label(tr("Leistung zu Beginn der Stufe → mit deinen Entscheidungen")).classes("ptz-muted")
            colors = {"Wind": "#3b82c4", "Sonne": "#e9b10e", "Speicher": "#c2549d",
                      "Steuerbar CO₂-frei": "#3f8f3f", "Steuerbar fossil": "#d64545",
                      "Wasserstoff-Elektrolyse": "#8e5bd6", "Flexible Verbraucher": "#0891b2"}
            for g, v in after.items():
                b = before[g]
                diff = v - b
                dtxt = "" if abs(diff) < 50 else (f' <span style="color:{"#15803d" if diff > 0 else "#b91c1c"}">'
                                                   f'({"+" if diff > 0 else "−"}{de(abs(diff) / 1e3)})</span>')
                ui.html(f'<div class="w-full"><div class="flex justify-between text-sm"><span>{tr(g)}</span>'
                        f'<span class="ptz-num"><b>{de(v / 1e3)} GW</b>{dtxt}</span></div>'
                        f'<div class="ptz-bar"><div style="width:{100 * v / mx:.1f}%;background:{colors[g]}"></div>'
                        f'</div></div>').classes("w-full")
            if cap.get("h2_storage", 0) > 1 or cap.get("h2_import", 0) > 1 or core.h2_warnings(cap):
                ui.html(tr("<div class=\"text-sm\">Wasserstoff-Speicher: <b>{0}</b><br>{1}</div>", amount("h2_storage", cap.get("h2_storage", 0)), h2_status_html())).classes("w-full")
            firm = core.firm_capacity(cap)
            peak = peak_demand_mw(year())
            short = core.short_term_capacity(cap)
            trade = cap.get("trade", 0.0)
            margin = 100 * (firm / peak - 1)                     # power plants only (long Dunkelflaute): neutral
            margin2 = 100 * ((firm + short) / peak - 1)          # + storage & flexibility (evening peak)
            margin3 = 100 * ((firm + short + trade) / peak - 1)  # + interconnectors (imports, if available)

            def light(m, green, yellow):
                col = "#15803d" if m >= green else ("#ca8a04" if m >= yellow else "#b91c1c")
                return (f'<span style="color:{col};font-weight:700">●&nbsp;{"+" if m >= 0 else ""}{de(m, 0)}&nbsp;%'
                        '</span>')

            ui.separator()
            with ui.row().classes("items-center gap-1"):
                ui.label(tr("Gesicherte Leistung")).classes("font-bold")
                info_button(
                    tr("<b>Kraftwerke</b> ({0}): nur steuerbare Kraftwerke – sie liefern auch in einer tagelangen Dunkelflaute. Wind und Sonne zählen nicht, Laufwasser halb. Auf Wasserstoff umgerüstete Gasturbinen zählen nur so weit, wie Import und voller Speicher sie 2 Wochen lang versorgen (Dauer der kalten Dunkelflaute im Spiel).<br><br><b>Speicher & Flex</b> (bis {1}): Batterien, Pumpspeicher und flexible Verbraucher helfen bei kurzen Spitzen (Abend), sind aber nach einigen Stunden erschöpft. Ampel: grün ab +10 %, gelb ab 0 %.<br><br><b>Leitungen</b> (bis {2}): Importe – aber nur, wenn die Nachbarn Strom übrig haben; bei europaweiter Flaute fehlen sie. Ampel deshalb strenger: grün ab +30 %, gelb ab +15 %. Testläufe: Wer bei beiden Ampeln grün ist, hat auch im extremen Winter kaum Lücken.<br><br>Vergleich mit der Spitzenlast im Normaljahr – in schwierigen Jahren liegt sie höher.", gw(firm, 0), gw(short, 0), gw(trade, 0)))
            turb = cap.get("gas_new_h2", 0.0)
            if turb > 1 and core.h2_firm(cap) < turb - 50:
                ui.html(tr("<div class=\"text-sm\" style=\"color:#b45309\">H₂-Turbinen: {0}, davon gesichert {1} – der Wasserstoff reicht nicht für 2 Wochen Volllast.</div>", gw(turb), gw(core.h2_firm(cap))))
            kv([(tr("Gesichert / Spitzenlast"), f"{de(firm / 1e3, 0)}&nbsp;/&nbsp;{de(peak / 1e3, 0)}&nbsp;GW"),
                (tr("Puffer Kraftwerke"), f'<span style="color:#4b5563">{"+" if margin >= 0 else ""}{de(margin, 0)}&nbsp;%</span>'),
                (tr("+ Speicher & Flex"), light(margin2, 10, 0)),
                (tr("+ Leitungen"), light(margin3, 30, 15))])
            if st["phase"] == "build":
                used = core.tokens_total(st, tid) - core.tokens_left(st, tid)
                ui.separator()
                kv([(tr("Investition diese Stufe"), tr("{0} Mrd. €", de(used * cfg['token_value_bn'], 0))),
                    (tr("Kredit-Token"), str(t["draft"]["borrow"]))])

    # ---------------------------------------------------------------- cards
    def tech_card(tech: str, ed: bool):
        t = team()
        d = t["draft"]
        y = year()
        ok, why = core.can_build(st, tid, tech)
        locked = not ok and d["build"][tech] == 0
        per = core.mw_per_token(t, tech, y, cfg)
        add = d["build"][tech] * per            # this stage's draft
        cf = capacity_factors(y)
        inv = core.invest_eur_kw(tech, y) * t["learn"][tech]
        learn = 1 - t["learn"][tech]

        def built_txt(before: float) -> str:
            """'Bisher gebaut' with the effect of this stage's tokens: 14,4 GW → 28,8 GW."""
            if add <= 0:
                return amount(tech, before)
            return f'{amount(tech, before)} → <b style="color:{tcolor(tech)}">{amount(tech, before + add)}</b>'

        unit = "€/kWh H₂" if tech == "h2_storage" else "€/kW"
        info = [tdesc(tech), tr("Kosten: {0} {1}", de(inv, 2 if tech == 'h2_storage' else 0), unit)
                + (tr(" (−{0} % durch eigenen Lerneffekt)", de(100 * learn, 0)) if learn > 0.001 else "")]
        if tech in ("onwind", "offwind", "solar_utility", "solar_rooftop"):
            old_key = tech + "_old" if tech in ("onwind", "offwind") else tech
            built = t["cap"][tech] if tech in ("onwind", "offwind") else t["cap"][tech] - t["start_cap"].get(tech, 0.0)
            rows = [(tr("Bisher gebaut"), built_txt(built)),
                    (tr("Altanlagen"), f"{gw(core.old_fleet(t, old_key, y))}{fleet_next(t, old_key)}"),
                    (tr("Auslastung"), f"Ø {de(cf[tech], 0)} %")]
            if tech in ("onwind", "offwind"):
                info.append(tr("Auslastung der Altanlagen: Ø {0} % (kleinere, ältere Anlagen).", de(cf[tech + '_old'], 0)))
        elif tech == "battery":
            rows = [(tr("Bisher gebaut"), built_txt(t["cap"][tech])),
                    (tr("Altanlagen (1 h)"), f"{gw(fixed_capacities(y)['battery_old'])}{fleet_next(t, 'battery_old')}")]
        elif tech == "biomass_flex":
            room = max(0.0, core.flex_max(st, tid) - core.flex_built(st, tid))
            rows = [(tr("Bisher gebaut"), built_txt(t["cap"][tech])), (tr("Noch möglich"), gw(room))]
        elif tech == "h2_package":
            eff = a["technologies"]["h2_package"]["electrolyser_efficiency"][y]
            rows = [(tr("Bisher gebaut"), built_txt(t["cap"][tech])), (tr("Läuft nur"), tr("bei Ökostrom-Überschuss")),
                    (tr("Braucht"), tr("Speicher + umgerüstete Gasturbinen"))]
            info.append(tr("Wirkungsgrad {0} % (Strom → Wasserstoff). Läuft nur, wenn Wind, Sonne und Laufwasser in Deutschland mehr liefern als gebraucht wird – kein Import- oder Fossilstrom.", de(eff * 100, 0)))
        elif tech == "h2_storage":
            e_t = a["technologies"]["gas_new"]["efficiency"]
            rows = [(tr("Bisher gebaut"), built_txt(t["cap"][tech])),
                    (tr("Braucht"), tr("Elektrolyse oder Wasserstoff-Netz + umgerüstete Gasturbinen"))]
            info.append(tr("Je TWh Wasserstoff kommen in den Gasturbinen ≈ {0} TWh Strom zurück.", de(e_t, 2)))
        else:
            eff = a["technologies"]["gas_new"]["efficiency"]
            h2 = t["cap"]["gas_new_h2"]
            rows = [(tr("Bisher gebaut"), built_txt(t["cap"][tech] + h2))]
            if h2 > 1:
                rows.append((tr("davon auf H₂"), gw(h2)))
            info.append(tr("Gasturbine mit {0} % Wirkungsgrad; jederzeit startbereit.", de(eff * 100, 0)))
        rows.append((tr("pro Token"), f'<span style="color:{tcolor(tech)};font-size:1.05rem">+{amount(tech, per)}</span>'))
        with ui.card().classes("ptz-card ptz-tech w-full" + (" opacity-60" if locked else "")).style(
                f"--tc:{tcolor(tech)}"):
            with ui.row().classes("w-full items-center justify-between no-wrap"):
                with ui.row().classes("items-center gap-1 no-wrap min-w-0"):
                    ui.icon(ticon(tech), size="sm").style(f"color:{tcolor(tech)}")
                    ui.label(core.LABELS[tech]).classes("ptz-h3 truncate")
                    info_button("<br><br>".join(info))
                risk_badge(cfg["backlash_risk"][tech])
            kv(rows)
            if locked:
                ui.label("🔒 " + why).classes("text-sm text-red-700 font-medium")
            with ui.row().classes("items-center gap-3 ptz-ctl mt-auto"):
                ui.button(icon="remove", on_click=lambda x=tech: act(core.change_build, x, -1)).props(
                    "round unelevated color=grey-4 text-color=black" + ("" if ed and d["build"][tech] > 0 else " disable"))
                ui.label(str(d["build"][tech])).classes("text-2xl font-extrabold w-8 text-center ptz-num")
                ui.button(icon="add", on_click=lambda x=tech: act(core.change_build, x, 1)).props(
                    "round unelevated color=primary" + ("" if ed and ok else " disable"))
                if d["build"][tech]:
                    ui.label(f"= +{amount(tech, add)}").classes("text-lg font-bold").style(f"color:{tcolor(tech)}")

    FIXED_KEYS_UI = ("battery_old", "phs", "waste", "other_fossil", "reserve")

    def fleet_next(t: dict, key: str) -> str:
        """' → nächste Stufe X GW' for the ageing start fleet (empty in the last stage or without change)."""
        years = core.stage_years()
        s = st["stage"]
        if s + 1 >= len(years):
            return ""
        y0, y1 = years[s], years[s + 1]
        if key in FIXED_KEYS_UI:
            now, nxt = fixed_capacities(y0)[key], fixed_capacities(y1)[key]
        else:
            now, nxt = core.old_fleet(t, key, y0), core.old_fleet(t, key, y1)
        if now - nxt < 50:
            return ""
        return tr(" <span style=\"color:#b45309\">→ {0} GW ab {1}</span>", de(nxt / 1e3), y1 - 4)

    def fixed_changes() -> str:
        """Short note for the collapsed 'Feste Anlagen' header: what shrinks in the next stage."""
        years = core.stage_years()
        s = st["stage"]
        if s + 1 >= len(years):
            return ""
        f0, f1 = fixed_capacities(years[s]), fixed_capacities(years[s + 1])
        names = {"battery_old": tr("Großbatterien"), "other_fossil": tr("Öl & Sonstige"), "reserve": tr("Reserve")}
        parts = [tr("{0} {1} → {2} GW", n, de(f0[k] / 1e3), de(f1[k] / 1e3)) for k, n in names.items() if f0[k] - f1[k] >= 50]
        return (tr("Nächste Stufe: ") + ", ".join(parts)) if parts else tr("Keine Änderung in der nächsten Stufe")

    def existing_card(k: str, ed: bool):
        t = team()
        d = t["draft"]
        coal_max = a["existing_params"]["coal_max_mw"][year()]
        mx = t["cap"][k] if k != "coal" else min(t["cap"][k], coal_max)
        if k in t["blocked"]:
            mx = 0
        with ui.card().classes("ptz-card ptz-tech w-full").style(f"--tc:{tcolor(k)}"):
            with ui.row().classes("w-full items-center justify-between no-wrap"):
                with ui.row().classes("items-center gap-1 no-wrap"):
                    ui.icon(ticon(k), size="sm").style(f"color:{tcolor(k)}")
                    ui.label(core.LABELS[k]).classes("ptz-h3")
                    if k == "coal":
                        info_button(tr("Behaltene Kohle läuft immer mit mindestens 15 % Leistung (Fernwärme, Tagebau) und ist träge – auch wenn Wind und Sonne genug liefern. Hohe CO₂-Emissionen."))
                risk_badge(cfg["backlash_risk"][k])

            def status_html() -> str:
                keep, have = team()["draft"]["keep"][k], team()["cap"][k]
                allowed = min(have, coal_max) if k == "coal" else have
                txt = tr("<b>{0}</b> von {1} weiterbetreiben", gw(keep), gw(allowed))
                if have - allowed > 50:
                    txt += tr("<br><span class=\"ptz-sub\">{0} gehen durch den Kohleausstieg vom Netz</span>", gw(have - allowed))
                if allowed - keep > 50:
                    txt += (tr("<br><span style=\"color:#b91c1c;font-weight:700\">{0} werden endgültig stillgelegt</span>", gw(allowed - keep)))
                return f'<div class="text-base">{txt}</div>'
            status = ui.html(status_html())
            if k == "coal":
                ui.label(tr("Kohleausstieg: in dieser Stufe höchstens {0}.", gw(coal_max))).classes("ptz-muted")
            if k == "biomass":
                ui.label(tr("Energie begrenzt (~{0} TWh/Jahr); Flexibilisierung bis zur dreifachen Leistung.", de(a['existing_params']['biomass']['energy_twh'], 0))).classes("ptz-muted")
            if k in t["blocked"]:
                ui.label(tr("⚠️ Gegenreaktion: muss in dieser Stufe stillgelegt werden")).classes("text-sm text-red-700")
            if mx > 0:
                sl = ui.slider(min=0, max=round(mx / 1e3, 1), step=0.1, value=round(d["keep"][k] / 1e3, 1)).props(
                    "" if ed else "disable")

                def on_keep(e, x=k, lab=status):
                    v = slider_value(e)
                    if v is None:
                        return
                    act_quiet(core.set_keep, x, v * 1e3, after=lambda: lab.set_content(status_html()))
                sl.on("update:model-value", on_keep, throttle=0.3)

    # ---------------------------------------------------------------- submit / confirm
    def confirm_dialog(on_yes, title: str, yes_label: str):
        s = core.draft_summary(st, tid)
        with dialog_host, ui.dialog() as dlg, ui.card().classes("ptz-card min-w-[320px] max-w-xl"):
            ui.label(title).classes("ptz-h2").style("margin-top:0")
            if s["builds"]:
                ui.label(tr("Neubau")).classes("ptz-h3")
                kv([(core.LABELS[t_], tr("{0} Token = +{1}", n, amount(t_, mw))) for t_, (n, mw) in s["builds"].items()])
            else:
                ui.label(tr("Kein Neubau in dieser Stufe.")).classes("ptz-sub")
            if s["convert"] > 0:
                kv([(tr("Umrüstung auf H₂"), gw(s["convert"]))])
            if s["retire"]:
                ui.label(tr("Endgültige Stilllegung (eure Entscheidung)")).classes("ptz-h3 text-red-700")
                kv([(core.LABELS[k], gw(v)) for k, v in s["retire"].items()])
            if s["forced"]:
                ui.label(tr("Kohleausstieg (Gesetz): {0} gehen vom Netz.", gw(s['forced']['coal']))).classes("ptz-sub")
            if s["influence"]:
                ui.label(tr("Einfluss-Maßnahmen: ") + ", ".join(core.INFLUENCE[k][0] for k in s["influence"])).classes(
                    "ptz-sub")
            if s["tokens_left"] > 0:
                ui.label(tr("⚠️ Noch {0} Bau-Token übrig – sie verfallen am Ende der Stufe.", s['tokens_left'])).classes(
                    "text-orange-700 font-bold")
            if s["influence_free"] > 0:
                ui.label(tr("ℹ️ {0} Einfluss-Token noch frei (bleiben für spätere Stufen).", s['influence_free'])).classes(
                    "ptz-sub")
            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button(tr("Zurück"), on_click=dlg.close).props("flat")

                async def yes():
                    dlg.close()
                    r = on_yes()
                    if hasattr(r, "__await__"):
                        await r
                ui.button(yes_label, on_click=yes).props("color=positive unelevated")
        dlg.open()

    def set_ready(v: bool):
        t = team()
        t["ready"] = v
        t["status"] = "fertig gemeldet" if v else "bearbeitet"
        bump()
        body.refresh()

    # ---------------------------------------------------------------- hydrogen: conversion + status
    def h2_status_html() -> str:
        cap = core.portfolio(st, tid)
        r = core.h2_reach(cap)
        lines = []
        if cap.get("h2_storage", 0) > 1 and cap.get("gas_new_h2", 0) > 1:
            lines.append(tr("Voller Speicher: {0} TWh H₂ ≈ {1} TWh Strom – reicht für <b>{2} Tage</b> Volllast eurer H₂-Turbinen ({3}).", de(r['store_twh']), de(r['twh_el']), de(r['hours'] / 24), gw(cap['gas_new_h2'])))
        elif cap.get("h2_storage", 0) > 1:
            lines.append(tr("Voller Speicher: {0} TWh H₂ ≈ {1} TWh Strom.", de(r['store_twh']), de(r['twh_el'])))
        if cap.get("h2_import", 0) > 1:
            price = a["technologies"]["h2_import"]["price"][year()]
            lines.append(tr("Wasserstoff-Import über das Netz: bis {0} H₂ zu {1} €/MWh (≈ {2} Strom).", gw(cap['h2_import']), de(price, 0), gw(cap['h2_import'] * a['technologies']['gas_new']['efficiency'])))
        lines += [f'<span style="color:#b45309">⚠️ {w}</span>' for w in core.h2_warnings(cap)]
        return "<br>".join(lines)

    def h2_section(t: dict, d: dict, ed: bool):
        unlocked = core.h2_available(st, tid)
        mxc = core.max_convert(st, tid)
        with ui.card().classes("ptz-card ptz-tech w-full" + ("" if unlocked else " opacity-60")).style(
                f"--tc:{tcolor('gas_new_h2')}"):
            with ui.row().classes("items-center gap-1"):
                ui.icon(ticon("gas_new_h2"), size="sm").style(f"color:{tcolor('gas_new_h2')}")
                ui.label(tr("Gasturbinen auf Wasserstoff umrüsten")).classes("ptz-h3")
                info_button(tr("Umgerüstete Gasturbinen verbrennen nur noch Wasserstoff – aus eurem Speicher oder dem Wasserstoff-Netz (CO₂-frei), kein Erdgas mehr. Umrüstung {0} €/kW, ohne Bau-Token. Möglich, sobald Elektrolyse und Speicher gebaut oder in dieser Stufe eingeplant sind – oder Wasserstoff über das Netz kommt (Einfluss-Karte).", de(a['technologies']['gas_new']['conversion_invest'], 0)))
            conv_label = ui.label(tr("Bereits umgerüstet: {0}{1}in dieser Stufe: {2}", gw(t['cap']['gas_new_h2']), SEP, gw(core.effective_convert(st, tid)))).classes("text-base")
            ui.label(tr("Ohne Bau-Token; danach nur noch Wasserstoff statt Erdgas.")).classes("ptz-muted")
            if not unlocked:
                ui.label(tr("🔒 Möglich nach Demonstrationsprogramm Wasserstoff oder Wasserstoff-Netz (ab der Folgestufe)")
                         ).classes("text-sm text-red-700 font-medium")
            elif not core.h2_ready(st, tid):
                ui.label(tr("Erst Elektrolyse und Speicher einplanen (oder Wasserstoff-Netz) – dann umrüsten.")).classes(
                    "ptz-muted")
            elif mxc > 0:
                sl = ui.slider(min=0, max=round(mxc / 1e3, 1), step=0.1,
                               value=round(d["convert_mw"] / 1e3, 1)).props("" if ed else "disable")

                def on_conv(e):
                    v = slider_value(e)
                    if v is None:
                        return

                    def after():
                        conv_label.set_text(tr("Bereits umgerüstet: {0}{1}in dieser Stufe: {2}", gw(team()['cap']['gas_new_h2']), SEP, gw(core.effective_convert(st, tid))))
                        status.set_content(h2_status_html())
                    act_quiet(core.set_convert, v * 1e3, after=after)
                sl.on("update:model-value", on_conv, throttle=0.3)
            else:
                ui.label(tr("Erst neue Gasturbinen bauen – dann umrüsten.")).classes("ptz-muted")
            status = ui.html(h2_status_html()).classes("text-sm")

    def h2_locked_note(no: int, t: dict, d: dict):
        """Hydrogen section before an H2 card takes effect: one line instead of the locked cards."""
        with ui.row().classes("items-center ptz-section w-full gap-0"):
            ui.html(f'<span class="ptz-sec-no">{no}</span>')
            ui.label(tr("Wasserstoff")).classes("ptz-h2").style("margin-top:0")
        pending = [core.INFLUENCE[k][0] for k in ("h2_demo", "h2_grid")
                   if k in d["influence_new"] or k in t["influence_used"]]
        if pending:
            txt = tr("🔓 Freigeschaltet ab der nächsten Stufe (Einfluss-Karte „{0}“).", pending[0])
        else:
            txt = (tr("🔒 Gesperrt – freischalten über die Einfluss-Karten „Demonstrationsprogramm Wasserstoff“ (eigene Elektrolyse) oder „Wasserstoff-Netz & Import“. Wirkt ab der Folgestufe."))
        ui.label(txt).classes("text-base")

    # ---------------------------------------------------------------- build tab
    @ui.refreshable
    def build_tab():
        t = team()
        y = year()
        ed = core.editable(st, tid)
        d = t["draft"]
        if st["phase"] != "build":
            ui.label(tr("Die Bauphase ist geschlossen. Warte auf die Spielleitung.")).classes("text-orange-700 font-bold")
        pr = a["prices"]
        ui.label(tr("Annahmen {0}: Verbrauch {1} TWh (inkl. Netzverluste, ohne Elektrolyse){2}CO₂-Preis {3} €/t{4}1 Bau-Token = {5} Mrd. €", y, de(demand_total_twh(y), 0), SEP, de(pr['co2'][y], 0), SEP, de(cfg['token_value_bn'], 0))).classes("ptz-sub")
        with ui.row().classes("w-full items-start gap-4 no-wrap max-lg:flex-wrap"):
            with ui.column().classes("flex-1 min-w-0 gap-2"):
                no = 0
                for title, intro, techs in SECTIONS:
                    no += 1
                    if techs[0] == "h2_package" and not core.h2_available(st, tid):
                        h2_locked_note(no, t, d)      # one line instead of three greyed-out cards
                        continue
                    section_title(no, tr(title), tr(intro))
                    if techs[0] == "h2_package" and not core.h2_available(st, tid, "h2_package") \
                            and not d["build"]["h2_package"]:
                        techs = [x for x in techs if x != "h2_package"]
                        ui.label(tr("🔒 Elektrolyse (eigener Wasserstoff) nur mit der Einfluss-Karte „Demonstrationsprogramm Wasserstoff“ – ab der Folgestufe.")).classes("ptz-muted")
                    with ui.grid().classes("w-full gap-3 grid-cols-1 md:grid-cols-2"):
                        for tech in techs:
                            tech_card(tech, ed)
                    if techs[-1] == "h2_storage":
                        h2_section(t, d, ed)
                no += 1
                section_title(no, tr("Bestehende Kraftwerke"), tr("Weiterbetreiben kostet fixe Betriebskosten. Stilllegen ist endgültig."))
                with ui.grid().classes("w-full gap-3 grid-cols-1 md:grid-cols-2"):
                    for k in core.EXISTING:
                        if k != "ror":        # run-of-river: nobody retires it, shown with the fixed plants
                            existing_card(k, ed)
                no += 1
                section_title(no, tr("Feste Anlagen"), tr("Gibt es in jedem Portfolio – nicht ausbaubar, nicht stilllegbar."))
                fixed = fixed_capacities(y)
                fb = a["fixed_blocks"]
                with ui.expansion(tr("Anzeigen"), icon="lock", caption=fixed_changes()).classes("w-full ptz-card"):
                    kv([(tr("Laufwasser"), tr("{0}{1}klein, gleichmäßig, CO₂-frei", gw(t['cap']['ror']), SEP)),
                        (tr("Pumpspeicher"), tr("{0}{1}ca. {2} h", gw(fixed['phs']), SEP, fb['phs']['hours'])),
                        (tr("Großbatterien (Bestand)"), tr("{0}{1}{2}1-h-Speicher, altern bis 2045 weg", gw(fixed['battery_old']), fleet_next(t, 'battery_old'), SEP)),
                        (tr("Abfallverbrennung"), tr("{0}{1}läuft immer, halb erneuerbar", gw(fixed['waste']), SEP)),
                        (tr("Öl & sonstige Konventionelle"), tr("{0}{1}{2}fossil, ab Stufe 3 stillgelegt", gw(fixed['other_fossil']), fleet_next(t, 'other_fossil'), SEP)),
                        (tr("Netz- & Kapazitätsreserve"), tr("{0}{1}{2}nur bei Knappheit, fossil", gw(fixed['reserve']), fleet_next(t, 'reserve'), SEP))])
                with ui.card().classes("ptz-card ptz-tech w-full").style(f"--tc:{tcolor('trade')}"):
                    with ui.row().classes("items-center gap-1"):
                        ui.icon(ticon("trade"), size="sm").style(f"color:{tcolor('trade')}")
                        ui.label(tr("Import & Export")).classes("ptz-h3")
                        info_button(tr("Strom kommt aus den Nachbarländern, wenn er dort übrig und günstig ist – bei europaweiter Dunkelflaute ist er knapp und teuer. Importe zählen nicht als erneuerbar, exportierter Ökostrom zählt mit."))
                    tc = core.trade_cap(st, tid, y)
                    kv([(tr("Kuppelleitungen"), gw(tc)),
                        (tr("Nächste Stufe"), gw(core.trade_cap(st, tid, core.stage_years()[min(st["stage"] + 1, 3)])))])
                    ui.label(tr("Mehr Leitungen: Einfluss-Karte „Netzausbau Europa“.")).classes("ptz-muted")
                no += 1
                section_title(no, tr("Finanzierung"), tr("Kredit: bis zu {0} zusätzliche Bau-Token, +{1} % Kosten.", cfg['max_borrow_tokens'], int(cfg['borrow_premium'] * 100)))
                with ui.card().classes("ptz-card w-full"):
                    with ui.row().classes("items-center gap-3 ptz-ctl"):
                        ui.label(tr("Kredit-Token")).classes("ptz-h3")
                        ui.button(icon="remove", on_click=lambda: act(core.set_borrow, d["borrow"] - 1)).props(
                            "round unelevated color=grey-4 text-color=black" + ("" if ed and d["borrow"] > 0 else " disable"))
                        ui.label(str(d["borrow"])).classes("text-2xl font-extrabold w-8 text-center")
                        ui.button(icon="add", on_click=lambda: act(core.set_borrow, d["borrow"] + 1)).props(
                            "round unelevated color=orange-9" + ("" if ed else " disable"))
                if st["phase"] == "build" and not solo:
                    with ui.row().classes("mt-4 items-center gap-3"):
                        if t.get("ready"):
                            ui.label(tr("✔ Fertig gemeldet")).classes("text-green-700 font-bold text-lg")
                            ui.button(tr("Doch noch ändern"), on_click=lambda: set_ready(False)).props("outline")
                        else:
                            ui.button(tr("Fertig melden"), icon="check", on_click=lambda: confirm_dialog(
                                lambda: set_ready(True), tr("Fertig melden?"), tr("Ja, fertig"))).props(
                                "color=positive size=lg unelevated")
            with ui.column().classes("w-full lg:w-80 shrink-0 lg:sticky").style("top: 110px"):
                portfolio_panel()

    # ---------------------------------------------------------------- influence tab
    def influence_tab():
        t = team()
        d = t["draft"]
        ed = core.editable(st, tid)
        free = t["influence_tokens"] - len(d["influence_new"])
        with ui.row().classes("items-center gap-2"):
            ui.label(tr("Einfluss-Token frei: {0}", free)).classes("ptz-h2").style("margin-top:0")
            ui.html("".join('<span class="ptz-tok infl"></span>' for _ in range(max(free, 0))))
        ui.label(tr("Jede Maßnahme kann einmal im Spiel gewählt werden; bis zum Ende der Bauphase änderbar.")).classes(
            "ptz-sub")
        with ui.row().classes("w-full gap-4 items-start max-md:flex-wrap"):
            for group, keys in core.INFLUENCE_GROUPS:     # policy left, technology right (hydrogen stacked)
                with ui.column().classes("flex-1 min-w-[280px] gap-3"):
                    ui.label(tr(group)).classes("ptz-h3 text-purple-900")
                    for key in keys:
                        name, desc = core.INFLUENCE[key]
                        used = key in t["influence_used"]
                        chosen = key in d["influence_new"]
                        with ui.card().classes("ptz-card ptz-tech w-full" + (" ptz-chosen" if chosen else "")
                                               + (" ptz-used" if used else "")).style("--tc:#7c3aed"):
                            with ui.row().classes("w-full items-center justify-between no-wrap gap-2"):
                                with ui.row().classes("items-center gap-2 no-wrap"):
                                    ui.icon(INFLUENCE_ICONS[key], size="sm").classes("text-purple-700")
                                    ui.label(name).classes("ptz-h3")
                                if chosen:
                                    ui.badge(tr("✔ Gewählt"), color="green-7").classes("text-sm shrink-0")
                                elif used:
                                    ui.badge(tr("✔ Aktiv"), color="grey-6").classes("text-sm shrink-0")
                            ui.label(desc).classes("text-base")
                            if key in core.INFLUENCE_DETAIL:
                                ui.label(core.INFLUENCE_DETAIL[key]).classes("ptz-muted")
                            fy = [y for y in core.stage_years() if y > year()]   # takes effect from the next stage
                            if key == "flex" and fy:
                                fl = a["flexibility"]
                                ui.label(tr("Verschieben + Verzicht: ") + SEP.join(
                                    f"{y}: {de((fl['shift_mw'][y] + fl['shed_mw'][y]) / 1e3, 0)} GW"
                                    for y in fy)).classes("ptz-muted")
                            if used:
                                ui.label(tr("✔ eingesetzt in Stufe {0}", t['influence_used'][key] + 1)).classes("text-green-700 font-bold")
                            else:
                                ui.button(tr("Gewählt – zurücknehmen") if chosen else tr("Einsetzen"),
                                          on_click=lambda k=key: act(core.toggle_influence, k)).props(
                                    ("outline" if chosen else "color=purple-8 unelevated") + ("" if ed else " disable"))
        price = cfg["influence_token_price"]
        with ui.row().classes("items-center gap-2 mt-3"):
            ui.button(tr("Einfluss-Token kaufen ({0} Bau-Token = {1} Mrd. €)", price, de(price * cfg['token_value_bn'], 0)),
                      on_click=lambda: act(core.buy_influence, 1)).props(
                "outline color=purple-8" + ("" if ed else " disable"))
            if d["influence_bought"]:
                ui.button(tr("Kauf zurücknehmen"), on_click=lambda: act(core.buy_influence, -1)).props("flat")
        ui.label(tr("Gekaufte Einfluss-Token zählen als Programmkosten in den Erzeugungs- und Speicherkosten.")).classes(
            "ptz-muted")

    # ---------------------------------------------------------------- simulator tab
    def simulator_tab():
        t = team()
        limit = cfg["simulations_per_stage"] + t.get("sims_extra", 0)
        left = max(0, limit - t["sims_used"])
        ui.label(tr("Der Simulator testet dein aktuelles Portfolio mit einem normalen Wetterjahr – ohne Nachfrageschock und ohne Katastrophe. Die echte Stufe kann schwieriger werden.")).classes("text-base")

        async def do_sim():
            btn.props("loading")
            err = await rt.simulate(tid)
            notify_err(err)
            body.refresh()
        btn = ui.button(tr("Simulieren ({0} von {1} übrig)", left, limit), icon="play_arrow", on_click=do_sim).props(
            "color=primary size=lg unelevated" + ("" if st["phase"] == "build" and left > 0 and tid not in rt.sim_running
                                                  else " disable"))
        if tid in rt.sim_running:
            ui.label(tr("Berechnung läuft … (ca. 5–15 Sekunden)")).classes("text-blue-700 font-bold")
        res = rt.sim.get(tid)
        if res and res["stage"] == st["stage"]:
            ui.label(tr("Ergebnis der Simulation von {0} Uhr", time.strftime('%H:%M', time.localtime(res['time'])))).classes(
                "ptz-h2")
            if res.get("prev"):
                sim_compare(res)
            results_block(res["summary"], {**res["eval"], "cap": res.get("cap")}, st["stage"], cfg, res["dispatch"],
                          sim=True)
            dispatch_panel(res["dispatch"], None, tr("Simulierte Stromversorgung"))

    def stage_compare(stage: int) -> str | None:
        """'All teams in this stage' line: average points per category and own rank (only with several teams)."""
        rows = [(x["id"], h) for x in st["teams"].values() for h in x["history"] if h["stage"] == stage]
        if len(rows) < 2:
            return None
        avg = {k: sum(h["points"][k] for _, h in rows) / len(rows) for k in ("reliability", "clean", "cost")}
        mine = next((h for i, h in rows if i == tid), None)
        if mine is None:
            return None
        rank = 1 + sum(1 for _, h in rows if h["stage_points"] > mine["stage_points"])
        parts = [f'{CAT[k][0]} {de(avg[k], 1)}' for k in avg]
        return (tr("<div class=\"ptz-card\" style=\"padding:8px 14px;background:#f5f3ff\"><b>Alle {0} Teams in dieser Stufe (Durchschnitt):</b> {1}{2}<b>Euer Platz in dieser Stufe: {3} von {4}</b> ({5} Punkte)</div>", len(rows), SEP.join(parts), SEP, rank, len(rows), mine["stage_points"]))

    # ---------------------------------------------------------------- results tab
    def results_tab():
        t = team()
        if not t["history"]:
            ui.label(tr("Noch keine Ergebnisse.")).classes("ptz-sub")
            return
        stages = [h["stage"] for h in t["history"]]
        sel = {"s": stages[-1]}

        @ui.refreshable
        def show():
            h = next(x for x in t["history"] if x["stage"] == sel["s"])
            luck = st["luck"][h["stage"]]
            disp = rt.get_dispatch(tid, h["stage"])
            with ui.card().classes("w-full ptz-card bg-amber-50"):
                ui.label(tr("Stufe {0} ({1}): ", h['stage'] + 1, h['year']) + core.describe_luck(luck)).classes("text-base")
            results_block(h["summary"], {"points": h["points"], "cost": h["cost"], "cap": h.get("cap"),
                                         "clean_detail": h.get("clean_detail", {})}, h["stage"], cfg, disp,
                          compare=stage_compare(h["stage"]))
            if h["penalty"]:
                ui.label(tr("Abzug für Gegenreaktionen in der letzten Stufe: −{0} Punkte", h['penalty'])).classes(
                    "text-red-700 font-bold")
            if h["backlash"]:
                ui.label(tr("⚠️ Gesellschaftliche Gegenreaktion bei: ") + ", ".join(core.LABELS[b] for b in h["backlash"])
                         + tr(" – in der nächsten Stufe gesperrt bzw. Stilllegung.")).classes("text-red-700")
            if h["learning"]:
                ui.label(tr("📉 Lerneffekte: ") + ", ".join(
                    f"{core.LABELS[k]} −{de(v * 100)} %" for k, v in h["learning"].items())).classes("text-green-800")
            if disp is not None:
                ev = luck.get("event") if luck else None
                dispatch_panel(disp, ev, tr("Stromversorgung {0}", h['year']))
                ui.label(tr("Füllstand der Speicher")).classes("ptz-h3")
                ui.plotly(charts.as_plot(charts.storage_figure(disp))).classes("w-full")

        if len(stages) > 1:
            ui.toggle({s: tr("Stufe {0}", s + 1) for s in stages}, value=sel["s"],
                      on_change=lambda e: (sel.update(s=e.value), show.refresh()))
        show()

    def history_tab():
        t = team()
        ui.plotly(charts.as_plot(charts.score_chart(t["history"], cfg["stages"]))).classes("w-full")
        rows = []
        for h in t["history"]:
            rows.append({"stufe": f"{h['stage'] + 1} ({h['year']})", "rel": h["points"]["reliability"],
                         "clean": h["points"]["clean"], "cost": h["points"]["cost"],
                         "lole": h["summary"]["lole_hours"], "share": de(h["summary"]["clean_share"]),
                         "eur": de(h["cost"]["eur_per_mwh"], 0), "co2": de(h["summary"]["co2_mt"]),
                         "gkwh": de(core.co2_intensity(h["summary"]), 0),
                         "cum": de(sum(x["co2_cum_gt"] for x in t["history"] if x["stage"] <= h["stage"]), 2)})
        cols = [{"name": "stufe", "label": tr("Stufe"), "field": "stufe", "align": "left"},
                {"name": "rel", "label": tr("Pkt Versorgung"), "field": "rel"},
                {"name": "clean", "label": tr("Pkt Klimaschutz"), "field": "clean"},
                {"name": "cost", "label": tr("Pkt Kosten"), "field": "cost"},
                {"name": "lole", "label": tr("Lücken-h"), "field": "lole"},
                {"name": "share", "label": tr("CO₂-frei %"), "field": "share"},
                {"name": "eur", "label": tr("€/MWh"), "field": "eur"},
                {"name": "co2", "label": tr("CO₂ Mt/Jahr"), "field": "co2"},
                {"name": "gkwh", "label": tr("g CO₂/kWh"), "field": "gkwh"},
                {"name": "cum", "label": tr("CO₂ kumuliert Gt"), "field": "cum"}]
        ui.table(rows=rows, columns=cols, row_key="stufe").props(f'no-data-label="{tr("Keine Daten vorhanden.")}"').classes("w-full")
        if t["penalty"]:
            ui.label(tr("Abzug Gegenreaktionen: −{0}", t['penalty'])).classes("text-red-700")
        ui.label(tr("Gesamtpunkte: {0}{1}CO₂ gesamt: {2} Gt", core.total_points(t), SEP, de(core.cumulative_co2_gt(t), 2))).classes(
            "ptz-h3")

    def rules_tab():
        rules.build_rules(cfg, st["stage"], team())

    # ---------------------------------------------------------------- event pop-up
    def event_dialog(h: dict):
        luck = st["luck"][h["stage"]] or {}
        with dialog_host, ui.dialog() as dlg, ui.card().classes("ptz-card min-w-[320px] max-w-xl"):
            ui.label(tr("Stufe {0} ({1}): Das Jahr ist gelaufen", h['stage'] + 1, h['year'])).classes("ptz-h2").style(
                "margin-top:0")

            def line(icon, text, cls=""):
                with ui.row().classes("items-start no-wrap gap-2"):
                    ui.icon(icon, size="sm").classes("text-blue-800")
                    ui.label(text).classes("text-base " + cls)
            if luck:
                lvl = core.weather_level(luck)
                line({"normal": "wb_sunny", "hard": "cloud", "extreme": "ac_unit"}[lvl],
                     tr("Wetterjahr {0}: {1}", luck['weather_year'], core.WEATHER_TEXT[lvl]),
                     "font-bold text-red-700" if lvl == "extreme" else "")
                line("trending_up" if luck["demand_shock"] >= 0 else "trending_down",
                     tr("Stromverbrauch {0}{1} % gegenüber der Prognose", '+' if luck['demand_shock'] >= 0 else '−', de(abs(luck['demand_shock']) * 100, 1)))
                ev = luck.get("event")
                if ev:
                    line(EVENT_ICONS.get(ev["kind"], "warning"), core.EVENT_TEXT[ev["kind"]], "font-bold text-red-700")
                else:
                    line("check_circle", tr("Keine Katastrophe"))
            if h["backlash"]:
                line("campaign", tr("Gesellschaftliche Gegenreaktion: ") + ", ".join(core.LABELS[b] for b in h["backlash"]),
                     "font-bold text-red-700")
            if h["learning"]:
                line("trending_down", tr("Lerneffekte: ") + ", ".join(
                    f"{core.LABELS[k]} −{de(v * 100)} %" for k, v in h["learning"].items()), "text-green-800")
            with ui.row().classes("w-full gap-2 mt-2"):
                for k in CAT:
                    ui.html(f'<div class="text-center"><div class="ptz-muted">{CAT[k][0]}</div>'
                            f'<span class="ptz-pts" style="background:{points_color(h["points"][k])}">'
                            f'{h["points"][k]} / 5</span></div>')
            ui.label(tr("Diese Stufe: {0} Punkte", h['stage_points']) + (tr(" (−{0} Abzug)", h['penalty']) if h["penalty"] else "")
                     ).classes("ptz-h3")
            with ui.row().classes("w-full justify-end"):
                ui.button(tr("Details ansehen"), on_click=dlg.close).props("color=primary unelevated")
        dlg.open()

    def check_new_results():
        hist = team()["history"]
        if len(hist) > ui_state["hist_seen"]:
            ui_state["hist_seen"] = len(hist)
            event_dialog(hist[-1])

    # ---------------------------------------------------------------- solo controls
    def solo_controls():
        with ui.row().classes("gap-2 my-2 items-center"):
            if st["phase"] == "lobby":
                ui.button(tr("Spiel starten"), on_click=lambda: (core.start_stage(st), rt.touch(), refresh_all())).props(
                    "color=primary unelevated")
            elif st["phase"] == "build":
                async def close():
                    await rt.close_and_resolve()
                    ui_state["tab"] = "Ergebnisse"
                    refresh_all()
                    check_new_results()
                ui.button(tr("Stufe abschließen & berechnen"), icon="play_arrow", on_click=lambda: confirm_dialog(
                    close, tr("Stufe abschließen?"), tr("Ja, berechnen"))).props("color=positive size=lg unelevated")
            elif st["phase"] == "resolving":
                ui.spinner(size="lg")
                ui.label(tr("Das Jahr wird simuliert …")).classes("text-lg")
            elif st["phase"] == "results":
                def nxt():
                    core.next_stage(st)
                    rt.touch()
                    ui_state["tab"] = "Bauen" if st["phase"] == "build" else "Verlauf"
                    refresh_all()
                ui.button(tr("Weiter zur nächsten Stufe") if st["stage"] < cfg["stages"] - 1 else tr("Spiel beenden"),
                          icon="arrow_forward", on_click=nxt).props("color=primary size=lg unelevated")
            elif st["phase"] == "finished":
                ui.label(tr("Spiel beendet – {0} Punkte", core.total_points(team()))).classes("ptz-h2")
                ui.button(tr("Neues Einzelspiel"), on_click=lambda: ui.navigate.to("/solo?neu=1")).props("outline")

    # ---------------------------------------------------------------- body
    @ui.refreshable
    def body():
        if solo:
            solo_controls()
        if st["phase"] == "lobby":
            ui.label(tr("Du bist im Spiel. Die Spielleitung startet gleich Stufe 1. Schau dir solange die Regeln an:")).classes(
                "text-lg mt-2")
            rules_tab()
            return
        if st["phase"] == "resolving":
            done, tot = rt.resolve_progress
            with ui.row().classes("items-center gap-3 mt-4"):
                ui.spinner(size="lg")
                ui.label(tr("Das Jahr wird simuliert … ({0}/{1} Teams)", done, tot)).classes("text-lg")
            return
        overview()
        tabs_names = ["Bauen", "Einfluss", "Simulator", "Ergebnisse", "Verlauf", "Regeln"]
        icons = {"Bauen": "construction", "Einfluss": "how_to_vote", "Simulator": "insights",
                 "Ergebnisse": "emoji_events", "Verlauf": "timeline", "Regeln": "menu_book"}
        if ui_state["tab"] not in tabs_names:
            ui_state["tab"] = "Bauen"
        with ui.tabs().classes("w-full").props("dense inline-label outside-arrows mobile-arrows") as tabs:
            for n in tabs_names:
                ui.tab(n, label=tr(n), icon=icons[n])

        def switch(e):
            if e.value != ui_state["tab"]:
                ui_state["tab"] = e.value
                body.refresh()
        tabs.on_value_change(switch)
        builders = {"Bauen": build_tab, "Einfluss": influence_tab, "Simulator": simulator_tab,
                    "Ergebnisse": results_tab, "Verlauf": history_tab, "Regeln": rules_tab}
        with ui.tab_panels(tabs, value=ui_state["tab"], animated=False).classes("w-full bg-transparent"):
            for n in tabs_names:
                with ui.tab_panel(n).classes("px-0"):
                    if n == ui_state["tab"]:  # render only the visible tab (fast on phones, no hidden plots)
                        builders[n]()

    def fingerprint():
        t = team()
        return (st["phase"], st["stage"], len(t["history"]), t.get("sims_extra", 0), t["sims_used"],
                tid in rt.sim_running, rt.resolve_progress if st["phase"] == "resolving" else None,
                rt.sim.get(tid, {}).get("time"), t.get("rev", 0), st["cfg"]["simulations_per_stage"])

    def refresh_all():
        ui_state["fp"] = fingerprint()
        header.refresh()
        body.refresh()

    def tick():
        if tid not in st["teams"]:   # removed by the host
            timer.cancel()
            ui.navigate.to(f"/join?pin={st['pin']}" if not solo else "/")
            return
        if st["phase"] == "build" and st.get("timer_end"):
            rest = int(st["timer_end"] - time.time())
            timer_label.text = f"⏱ {rest // 60}:{rest % 60:02d}" if rest > 0 else tr("⏱ Zeit um")
            key = (st["stage"], round(st["timer_end"]))   # again after the host adds time
            if 0 < rest <= 120 and ui_state.get("warned") != key:
                ui_state["warned"] = key
                if not team().get("ready"):
                    ui.notify(tr("Noch 2 Minuten – jetzt testen und „Fertig melden“!"), type="warning",
                              position="top", timeout=10000, progress=True)
            timer_label.classes(add="ptz-blink" if 0 < rest <= 120 else "", remove="" if 0 < rest <= 120 else "ptz-blink")
        else:
            timer_label.text = ""
        fp = fingerprint()
        if fp != ui_state["fp"]:
            old = ui_state["fp"] or (None, None)
            if fp[:2] != old[:2] and st["phase"] in ("results", "finished"):
                ui_state["tab"] = "Ergebnisse"
            if fp[:2] != old[:2] and st["phase"] == "build":
                ui_state["tab"] = "Bauen"
            refresh_all()
            check_new_results()

    with ui.header().classes("bg-white text-gray-900 shadow-sm px-3 py-2"):
        with ui.row().classes("w-full max-w-7xl mx-auto items-center no-wrap gap-3"):
            with ui.element("div").classes("flex-1 min-w-0"):
                header()
            timer_label = ui.label("").classes("text-xl font-extrabold text-red-700")
    with ui.column().classes("w-full max-w-7xl mx-auto p-2 gap-2"):
        body()
    dialog_host = ui.element("div")   # stable parent for dialogs (body/tab content gets rebuilt)
    ui_state["fp"] = fingerprint()
    timer = ui.timer(1.0, tick)
