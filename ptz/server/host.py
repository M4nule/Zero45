# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Host (game leader) pages: settings window, lobby with QR code, stage control, dashboard."""
from __future__ import annotations

import copy
import csv
import html
import io
import re
import time
from pathlib import Path

import qrcode
import qrcode.image.svg
import yaml
from nicegui import ui

from ptz.game import core
from ptz.server import charts, runtime
from ptz.engine.model import assumptions, demand_total_twh
from ptz.server import rules
from ptz.server.player import COST_LABEL, COST_NOTE, PHASE_DE, STAGE_LABELS
from ptz.server.theme import CSS, SEP, de, points_color
from ptz.i18n import tr

HOST_CSS = "<style>.ptz-host { font-size: 18px; } .ptz-host .q-table td, .ptz-host .q-table th { font-size: 1.05rem; }</style>"

PRESETS = Path(__file__).resolve().parents[2] / "presets"


def qr_svg(url: str) -> str:
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=12)
    return img.to_string(encoding="unicode")


def safe_preset_name(name: str) -> str:
    """Only letters, digits, space, - and _ (no path separators or dots)."""
    return re.sub(r"[^\w \-]", "", name or "", flags=re.UNICODE).strip()[:40]


def csv_cell(v):
    """Neutralise spreadsheet formulas in text cells (CSV injection via team names)."""
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def list_presets() -> dict[str, Path]:
    PRESETS.mkdir(exist_ok=True)
    return {p.stem: p for p in sorted(PRESETS.glob("*.yaml"))}


# ----------------------------------------------------------------------------- settings window
def settings_form(on_create, solo: bool = False):
    cfg = copy.deepcopy(core.default_config())
    holder = {"cfg": cfg}

    @ui.refreshable
    def form():
        c = holder["cfg"]
        ui.label(tr("Spiel-Einstellungen")).classes("text-xl font-bold")
        with ui.row().classes("items-end gap-2"):
            presets = list_presets()
            sel = ui.select({"Standard": tr("Standard"), **{p: p for p in presets}}, value="Standard", label=tr("Vorlage laden")).classes("w-48")

            def load_preset():
                if sel.value == "Standard":
                    holder["cfg"] = copy.deepcopy(core.default_config())
                else:
                    holder["cfg"] = {**core.default_config(), **yaml.safe_load(presets[sel.value].read_text(encoding="utf-8"))}
                form.refresh()
            ui.button(tr("Laden"), on_click=load_preset).props("outline dense")

        with ui.expansion(tr("Ablauf"), icon="schedule", value=True).classes("w-full"):
            with ui.row().classes("gap-2 flex-wrap"):
                for i in range(c["stages"]):
                    ui.number(tr("Timer Stufe {0} (Min., 0 = aus)", i + 1), value=c["timer_minutes"][i], min=0, max=120,
                              on_change=lambda e, i=i: c["timer_minutes"].__setitem__(i, int(e.value or 0))).classes("w-40")
            with ui.row().classes("gap-2 flex-wrap"):
                ui.number(tr("Simulationen pro Stufe"), value=c["simulations_per_stage"], min=0, max=50,
                          on_change=lambda e: e.value is not None and c.update(simulations_per_stage=int(e.value))).classes("w-48")
                ui.number(tr("Max. Teams"), value=c["max_teams"], min=1, max=50,
                          on_change=lambda e: c.update(max_teams=int(e.value or 1))).classes("w-32")
                ui.number(tr("Zufalls-Seed (leer = zufällig)"), value=c.get("seed"),
                          on_change=lambda e: c.update(seed=int(e.value) if e.value not in (None, "") else None)).classes("w-56")
        with ui.expansion(tr("Budget & Token"), icon="savings").classes("w-full"):
            with ui.row().classes("gap-2 flex-wrap"):
                ui.number(tr("Wert eines Bau-Tokens (Mrd. €)"), value=c["token_value_bn"], min=1, max=100, step=1,
                          on_change=lambda e: c.update(token_value_bn=float(e.value or 10))).classes("w-56")
                for i in range(c["stages"]):
                    ui.number(tr("Bau-Token Stufe {0}", i + 1), value=c["build_tokens"][i], min=0, max=100,
                              on_change=lambda e, i=i: c["build_tokens"].__setitem__(i, int(e.value or 0))).classes("w-36")
            with ui.row().classes("gap-2 flex-wrap"):
                ui.number(tr("Max. Kredit-Token pro Stufe"), value=c["max_borrow_tokens"], min=0, max=20,
                          on_change=lambda e: c.update(max_borrow_tokens=int(e.value or 0))).classes("w-56")
                ui.number(tr("Einfluss-Token zu Beginn"), value=c["influence_tokens_start"], min=0, max=4,
                          on_change=lambda e: c.update(influence_tokens_start=int(e.value or 0))).classes("w-48")
        with ui.expansion(tr("Zufall & Ereignisse"), icon="casino").classes("w-full"):
            with ui.row().classes("gap-2 flex-wrap items-center"):
                wp = c.setdefault("weather_probabilities", {"normal": 0.6, "hard": 0.3, "extreme": 0.1})

                def set_wp(key, v):
                    wp[key] = float(v or 0)
                    wp["normal"] = max(0.0, 1.0 - wp["hard"] - wp["extreme"])
                ui.number(tr("Wahrsch. schwieriges Jahr (1995)"), value=wp["hard"], min=0, max=1, step=0.05,
                          on_change=lambda e: set_wp("hard", e.value)).classes("w-60")
                ui.number(tr("Wahrsch. extremer Winter (2009)"), value=wp["extreme"], min=0, max=1, step=0.05,
                          on_change=lambda e: set_wp("extreme", e.value)).classes("w-60")
                ui.number(tr("Nachfrageschock (Std.-Abw.)"), value=c["demand_shock_sd"], min=0, max=0.1, step=0.01,
                          on_change=lambda e: c.update(demand_shock_sd=float(e.value or 0))).classes("w-56")
                ui.switch(tr("Katastrophen"), value=c["disasters_enabled"],
                          on_change=lambda e: c.update(disasters_enabled=e.value))
                ui.switch(tr("Gesellschaftliche Gegenreaktionen"), value=c["backlash_enabled"],
                          on_change=lambda e: c.update(backlash_enabled=e.value))
            with ui.row().classes("gap-2 flex-wrap"):
                for i in range(c["stages"]):
                    ui.number(tr("Katastrophe Stufe {0}", i + 1), value=c["disaster_probability"][i], min=0, max=1, step=0.05,
                              on_change=lambda e, i=i: c["disaster_probability"].__setitem__(i, float(e.value or 0))).classes("w-40")
        with ui.expansion(tr("Punkteschwellen (Fortgeschritten)"), icon="tune").classes("w-full"):
            ui.label(tr("Werte für 5, 4, 3, 2, 1 Punkte, kommagetrennt.")).classes("ptz-muted")
            ui.input(tr("Versorgungslücke (Stunden)"), value=", ".join(map(str, c["lole_thresholds"])),
                     on_change=lambda e: _set_list(c, "lole_thresholds", e.value)).classes("w-96")
            for i in range(c["stages"]):
                with ui.row().classes("gap-2"):
                    ui.input(tr("CO₂-frei % Stufe {0}", i + 1), value=", ".join(map(str, c["clean_thresholds"][i])),
                             on_change=lambda e, i=i: _set_list(c["clean_thresholds"], i, e.value)).classes("w-64")
                    if c.get("co2_mt_thresholds"):
                        ui.input(tr("CO₂ Mt Stufe {0}", i + 1), value=", ".join(map(str, c["co2_mt_thresholds"][i])),
                                 on_change=lambda e, i=i: _set_list(c["co2_mt_thresholds"], i, e.value)).classes("w-64")
                    ui.input(tr("Kosten €/MWh Stufe {0}", i + 1), value=", ".join(map(str, c["cost_thresholds"][i])),
                             on_change=lambda e, i=i: _set_list(c["cost_thresholds"], i, e.value)).classes("w-72")
        with ui.row().classes("items-end gap-2 mt-2"):
            name = ui.input(tr("Als Vorlage speichern unter")).classes("w-56")

            def save_preset():
                nm = safe_preset_name(name.value)
                if not nm:
                    ui.notify(tr("Bitte einen Namen eingeben (Buchstaben, Ziffern, Leerzeichen, - und _)"), type="warning")
                    return
                PRESETS.mkdir(exist_ok=True)
                (PRESETS / f"{nm}.yaml").write_text(yaml.safe_dump(holder["cfg"], allow_unicode=True), encoding="utf-8")
                ui.notify(tr("Vorlage „{0}“ gespeichert", nm), type="positive")
            ui.button(tr("Speichern"), on_click=save_preset).props("outline dense")
        ui.button(tr("Einzelspiel starten") if solo else tr("Spiel erstellen"),
                  on_click=lambda: on_create(holder["cfg"])).props("color=primary size=lg").classes("mt-4")

    form()


def _set_list(target, key, text):
    try:
        target[key] = [float(x) for x in str(text).replace(";", ",").split(",") if x.strip()]
    except ValueError:
        ui.notify(tr("Bitte nur Zahlen, durch Kommas getrennt"), type="warning")


# ----------------------------------------------------------------------------- dashboard
def build_host(rt: runtime.Runtime, join_urls: list[str]):
    st = rt.state
    cfg = st["cfg"]
    ui.add_head_html(CSS)
    ui.add_head_html(HOST_CSS)
    seen = {"v": None}

    @ui.refreshable
    def top():
        s = st["stage"]
        with ui.card().classes("w-full ptz-card bg-blue-50"):
            with ui.row().classes("w-full items-center justify-between flex-wrap"):
                with ui.column().classes("gap-0"):
                    ui.label(tr("⚡ Zero45 – Energiewende")).classes("text-2xl font-extrabold")
                    ui.label(tr("Stufe {0}/{1}{2}{3}{4}{5}", s + 1, cfg['stages'], SEP, STAGE_LABELS[s], SEP, PHASE_DE[st['phase']])).classes(
                        "text-xl")
                    year = core.stage_years()[s]
                    a = assumptions()
                    ui.label(tr("Annahmen {0}: Verbrauch {1} TWh{2}CO₂-Preis {3} €/t{4}Erdgas {5} €/MWh", year, de(demand_total_twh(year), 0), SEP, de(a['prices']['co2'][year], 0), SEP, de(a['prices']['natural_gas'][year]))
                             ).classes("ptz-sub")
                with ui.column().classes("items-center gap-0"):
                    ui.label(tr("Spiel-PIN")).classes("ptz-muted")
                    ui.label(st["pin"]).classes("text-5xl font-extrabold tracking-widest")
            rules.stage_timeline(cfg, s)
        if st["phase"] in ("lobby", "build"):
            rules.stage_banner(cfg, s)


    @ui.refreshable
    def controls():
        ph = st["phase"]
        with ui.row().classes("gap-2 items-center flex-wrap"):
            if ph == "lobby":
                ui.button(tr("Stufe 1 starten"), on_click=lambda: (core.start_stage(st), rt.touch(), refresh())).props(
                    "color=primary size=lg" + ("" if st["teams"] else " disable"))
                if not st["teams"]:
                    ui.label(tr("Warte auf Teams …")).classes("ptz-muted")
            elif ph == "build":
                async def close():
                    btn.props("loading")
                    await rt.close_and_resolve()
                    refresh()
                btn = ui.button(tr("Bauphase beenden & Jahr simulieren"), on_click=close).props("color=positive size=lg")

                def add_time(m):
                    if m < 0 and not st.get("timer_end"):
                        return
                    # never below "now": shortening ends at 0:00 ("time is up"), the host still ends the phase
                    st["timer_end"] = max(max(st.get("timer_end") or time.time(), time.time()) + m * 60, time.time())
                    rt.touch()
                no_timer = "" if st.get("timer_end") else " disable"
                ui.button(tr("−5 Min."), on_click=lambda: add_time(-5)).props("outline" + no_timer)
                ui.button(tr("−2 Min."), on_click=lambda: add_time(-2)).props("outline" + no_timer)
                ui.button(tr("+2 Min."), on_click=lambda: add_time(2)).props("outline")
                ui.button(tr("+5 Min."), on_click=lambda: add_time(5)).props("outline")
            elif ph == "resolving":
                done, tot = rt.resolve_progress
                ui.spinner(size="lg")
                ui.label(tr("Berechne Stufe … {0}/{1} Teams", done, tot)).classes("text-lg")
            elif ph == "results":
                last = st["stage"] >= cfg["stages"] - 1

                def nxt():
                    core.next_stage(st)
                    rt.touch()
                    refresh()
                ui.button(tr("Spiel beenden & Siegerehrung") if last else tr("Stufe {0} starten", st['stage'] + 2),
                          on_click=nxt).props("color=primary size=lg")
            elif ph == "finished":
                ui.label(tr("🏆 Spiel beendet")).classes("text-xl font-bold")
            ui.button(tr("Regeln zeigen"), icon="menu_book",
                      on_click=lambda: ui.navigate.to(f"/regeln?pin={st['pin']}", new_tab=True)).props("outline")
            ui.button(tr("Ergebnisse als CSV"), icon="download", on_click=export_csv).props("flat")

    @ui.refreshable
    def lobby_box():
        if st["phase"] != "lobby" and st["stage"] > 0:
            return
        with ui.card().classes("w-full ptz-card"):
            with ui.row().classes("items-center gap-6 flex-wrap"):
                url = f"{join_urls[0]}/join?pin={st['pin']}" if join_urls else f"/join?pin={st['pin']}"
                ui.html(qr_svg(url)).classes("w-56 h-56")
                with ui.column():
                    ui.label(tr("Beitreten: QR-Code scannen oder Adresse öffnen")).classes("text-lg font-bold")
                    for u in join_urls:
                        ui.label(f"{u}/join{SEP}PIN {st['pin']}").classes("text-2xl font-mono")

    @ui.refreshable
    def teams_box():
        rows = []
        for t in st["teams"].values():
            limit = cfg["simulations_per_stage"] + t.get("sims_extra", 0)
            rows.append({"id": t["id"], "name": t["name"], "status": tr(t["status"]) + (" ✔" if t.get("ready") else ""),
                         "sims": f"{t['sims_used']}/{limit}",
                         "token": core.tokens_left(st, t["id"]) if st["phase"] == "build" else "",
                         "punkte": core.total_points(t)})
        ui.label(tr("Teams ({0})", len(rows))).classes("text-lg font-bold")
        cols = [{"name": "name", "label": tr("Team"), "field": "name", "align": "left"},
                {"name": "status", "label": tr("Status"), "field": "status"},
                {"name": "token", "label": tr("Token übrig"), "field": "token"},
                {"name": "sims", "label": tr("Simulationen"), "field": "sims"},
                {"name": "punkte", "label": tr("Punkte"), "field": "punkte"}]
        tbl = ui.table(rows=rows, columns=cols, row_key="id").props(f'no-data-label="{tr("Keine Daten vorhanden.")}"').classes("w-full")
        tbl.add_slot("body-cell-sims", """
            <q-td :props="props">
              <q-btn dense flat size="sm" icon="remove" @click="$parent.$emit('fewer', props.row.id)" title="MINUS"/>
              {{ props.value }}
              <q-btn dense flat size="sm" icon="add" @click="$parent.$emit('extra', props.row.id)" title="TITLE"/>
            </q-td>""".replace("TITLE", tr("+1 Simulation")).replace("MINUS", tr("−1 Simulation")))
        tbl.add_slot("body-cell-name", """
            <q-td :props="props">{{ props.value }}
              <q-btn dense flat size="sm" icon="delete" color="grey" @click="$parent.$emit('remove', props.row.id)"
                     title="TITLE"/>
            </q-td>""".replace("TITLE", tr("Team entfernen")))

        def remove(e):
            t = st["teams"].get(e.args)
            if not t:
                return
            if st["phase"] == "resolving":
                ui.notify(tr("Während der Berechnung nicht möglich."), type="warning")
                return
            with ui.dialog() as dlg, ui.card():
                ui.label(tr("Team „{0}“ endgültig entfernen?", t['name']))
                with ui.row():
                    def yes():
                        core.remove_team(st, t["id"])
                        rt.touch()
                        dlg.close()
                        refresh()
                    ui.button(tr("Entfernen"), on_click=yes).props("color=negative")
                    ui.button(tr("Abbrechen"), on_click=dlg.close).props("flat")
            dlg.open()
        tbl.on("remove", remove)

        def extra(e):
            t = st["teams"].get(e.args)
            if t:
                t["sims_extra"] = t.get("sims_extra", 0) + 1
                rt.touch()
                teams_box.refresh()
        tbl.on("extra", extra)

        def fewer(e):
            t = st["teams"].get(e.args)
            if not t:
                return
            if cfg["simulations_per_stage"] + t.get("sims_extra", 0) <= t["sims_used"]:
                ui.notify(tr("Bereits genutzte Simulationen lassen sich nicht abziehen."), type="warning")
                return
            t["sims_extra"] = t.get("sims_extra", 0) - 1
            rt.touch()
            teams_box.refresh()
        tbl.on("fewer", fewer)

    def sims_all():
        """Limit for all teams; kept outside teams_box so typing is not interrupted by table refreshes."""
        def apply(e):
            if e.value is None:
                return
            cfg["simulations_per_stage"] = max(0, int(e.value))
            rt.touch()
            teams_box.refresh()
        with ui.row().classes("items-center gap-1"):
            ui.label(tr("Simulationen pro Stufe für alle Teams:")).classes("font-bold")
            ui.button(icon="remove", on_click=lambda: num.set_value(max(0, int(num.value or 0) - 1))).props(
                "dense flat round")
            num = ui.number(value=cfg["simulations_per_stage"], min=0, max=50, step=1, on_change=apply).props(
                "dense outlined").classes("w-20")
            ui.button(icon="add", on_click=lambda: num.set_value(min(50, int(num.value or 0) + 1))).props(
                "dense flat round")
            ui.label(tr("Gilt sofort und für die weiteren Stufen. +/− in der Tabelle: nur dieses Team, nur diese Stufe."
                        )).classes("ptz-muted")

    @ui.refreshable
    def results_box():
        if not any(t["history"] for t in st["teams"].values()):
            return
        s_res = max(h["stage"] for t in st["teams"].values() for h in t["history"])
        luck = st["luck"][s_res]
        with ui.card().classes("w-full ptz-card bg-amber-50"):
            ui.label(tr("Ereignisse Stufe {0}: ", s_res + 1) + core.describe_luck(luck)).classes("text-base")
        lb = core.leaderboard(st)
        if st["phase"] == "finished":
            with ui.row().classes("w-full justify-center items-end gap-6 my-4"):
                for place, idx, h in [(2, 1, "h-24"), (1, 0, "h-36"), (3, 2, "h-16")]:
                    if idx < len(lb):
                        with ui.column().classes("items-center"):
                            ui.label(lb[idx]["name"]).classes("text-xl font-bold")
                            ui.label(tr("{0} Punkte", lb[idx]['total'])).classes("ptz-muted")
                            ui.element("div").classes(f"w-28 {h} bg-amber-400 rounded-t-lg flex items-center "
                                                      "justify-center text-3xl font-bold").props(f'innerHTML="{place}."')
        ui.label(tr("Rangliste (alle bisherigen Stufen)")).classes("ptz-h2")
        # team x stage matrix (points per stage)
        head = "".join(tr("<th>Stufe {0}</th>", i + 1) for i in range(cfg["stages"]))
        body_rows = []
        for place, r in enumerate(lb, 1):
            t = st["teams"][r["id"]]
            hist = {h["stage"]: h for h in t["history"]}
            cells = "".join(
                f'<td><span class="ptz-chip" style="background:{points_color(round(hist[i]["stage_points"] / 3)) if i in hist else "#d1d5db"};font-size:1rem">'
                f'{hist[i]["stage_points"] if i in hist else "–"}</span></td>' for i in range(cfg["stages"]))
            body_rows.append(f"<tr><td><b>{place}.</b> {html.escape(r['name'])}</td>{cells}"
                             f"<td><b style='font-size:1.2rem'>{r['total']}</b></td><td>{de(r['co2_gt'], 2)}</td></tr>")
        ui.html(tr("<table class=\"ptz-table\" style=\"font-size:1.1rem\"><thead><tr><th>Team</th>{0}<th>Gesamt</th><th>CO₂ Gt</th></tr></thead><tbody>{1}</tbody></table>", head, "".join(body_rows))).classes("w-full")
        ui.label(tr("Punkte je Kategorie")).classes("ptz-h3 mt-2")
        cols = [{"name": k, "label": l, "field": k, "align": "left" if k == "name" else "right"} for k, l in
                [("name", tr("Team")), ("total", tr("Gesamt")), ("reliability", tr("Versorgung")), ("clean", tr("Klimaschutz")),
                 ("cost", tr("Kosten")), ("penalty", tr("Abzug")), ("co2_gt", tr("CO₂ Gt"))]]
        ui.table(rows=[{**r, "co2_gt": de(r["co2_gt"], 2)} for r in lb], columns=cols, row_key="id").props(f'no-data-label="{tr("Keine Daten vorhanden.")}"').classes("w-full")
        ui.plotly(charts.as_plot(charts.points_bar(lb))).classes("w-full")
        teams = []
        fleets = []
        stage_rows = []
        for t in st["teams"].values():
            h = next((x for x in t["history"] if x["stage"] == s_res), None)
            if h:
                teams.append((t["name"], h["summary"]["generation_twh"]))
                fleets.append((t["name"], h.get("cap", {})))
                stage_rows.append({"name": t["name"], "pts": h["stage_points"], "lole": h["summary"]["lole_hours"],
                                   "clean": de(h["summary"]["clean_share"]), "eur": de(h["cost"]["eur_per_mwh"], 0),
                                   "co2": de(h["summary"]["co2_mt"]), "gkwh": de(core.co2_intensity(h["summary"]), 0),
                                   "gkwh_imp": de(core.co2_intensity_with_imports(h["summary"]), 0),
                                   "bl": ", ".join(core.LABELS[b] for b in h["backlash"])})
        ui.label(tr("Stufe {0} im Detail", s_res + 1)).classes("text-lg font-bold mt-2")
        cols2 = [{"name": k, "label": l, "field": k} for k, l in
                 [("name", tr("Team")), ("pts", tr("Punkte")), ("lole", tr("Lücken-h")), ("clean", tr("CO₂-frei %")),
                  ("eur", tr("€/MWh")), ("co2", tr("CO₂ Mt")), ("gkwh", tr("g CO₂/kWh")), ("gkwh_imp", tr("… mit Import-CO₂")),
                  ("bl", tr("Gegenreaktion"))]]
        ui.table(rows=stage_rows, columns=cols2, row_key="name").props(f'no-data-label="{tr("Keine Daten vorhanden.")}"').classes("w-full")
        ui.label(tr("€/MWh = {0} ({1}).{2}g CO₂/kWh: heute ~{3} (UBA {4}, wie dort ohne Importe).", tr(COST_LABEL), tr(COST_NOTE), SEP, core.CO2_INTENSITY_TODAY[1], core.CO2_INTENSITY_TODAY[0])).classes("ptz-sub")
        ui.label(tr("Strommix der Teams (TWh)")).classes("text-lg font-bold mt-2")
        ui.plotly(charts.as_plot(charts.mix_bar(teams))).classes("w-full")
        ui.label(tr("Kraftwerkspark der Teams (GW)")).classes("text-lg font-bold mt-2")
        ui.plotly(charts.as_plot(charts.fleet_bar(fleets))).classes("w-full")
        ui.label(tr("Installierte Leistung in dieser Stufe, inkl. Bestand. Fahrt mit der Maus über die Balken für die Werte; ein Klick auf die Legende blendet eine Technologie aus.")).classes("ptz-sub")

    def export_csv():
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";")
        w.writerow([tr("Team"), tr("Stufe"), tr("Jahr"), tr("Punkte Versorgung"), tr("Punkte Klimaschutz"), tr("davon Anteil"), tr("davon Ausstoß"),
                    tr("Punkte Kosten"), tr("Lücken-Stunden"),
                    tr("CO2-frei %"), tr("Erzeugungs- und Speicherkosten €/MWh"), tr("CO2 Mt"), tr("g CO2/kWh"), tr("g CO2/kWh mit Import-CO2"), tr("Gegenreaktion")])
        for t in st["teams"].values():
            for h in t["history"]:
                w.writerow([csv_cell(x) for x in
                            [t["name"], h["stage"] + 1, h["year"], h["points"]["reliability"], h["points"]["clean"],
                             h.get("clean_detail", {}).get("share", ""), h.get("clean_detail", {}).get("co2", ""),
                             h["points"]["cost"], h["summary"]["lole_hours"], h["summary"]["clean_share"],
                             h["cost"]["eur_per_mwh"], h["summary"]["co2_mt"], round(core.co2_intensity(h["summary"])), round(core.co2_intensity_with_imports(h["summary"])),
                             " ".join(h["backlash"])]])
        ui.download.content(buf.getvalue().encode("utf-8-sig"), f"zero45_{st['pin']}.csv")

    def refresh():
        seen["v"] = rt.version
        top.refresh()
        controls.refresh()
        lobby_box.refresh()
        teams_box.refresh()
        results_box.refresh()

    def tick():
        if st["phase"] == "build" and st.get("timer_end"):
            rest = int(st["timer_end"] - time.time())
            timer.text = f"⏱ {rest // 60}:{rest % 60:02d}" if rest > 0 else tr("⏱ Zeit um")
            timer.classes(add="ptz-blink" if 0 < rest <= 120 else "", remove="" if 0 < rest <= 120 else "ptz-blink")
        else:
            timer.text = ""
        if seen["v"] != rt.version:
            seen["v"] = rt.version
            controls.refresh()
            teams_box.refresh()
            if st["phase"] in ("results", "finished", "lobby"):
                top.refresh()
                lobby_box.refresh()
                results_box.refresh()

    with ui.column().classes("w-full max-w-7xl mx-auto p-3 gap-3 ptz-host"):
        top()
        timer = ui.label("").classes("text-4xl font-bold text-red-700")
        controls()
        lobby_box()
        sims_all()
        teams_box()
        results_box()
    seen["v"] = rt.version
    ui.timer(1.0, tick)
