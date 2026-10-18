# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Helpers to run dispatch for teams (sequentially or in a process pool) and to analyse dispatch results."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ptz.engine.model import simulate
from ptz.game import core
from ptz.i18n import TDict, num, tr


def run_engine(args: dict) -> tuple[dict, pd.DataFrame]:
    """Process-pool friendly wrapper: returns (summary, dispatch GW)."""
    r = simulate(**args)
    return r["summary"], r["dispatch"]


def warmup() -> int:
    """Import the model and solve once so the first real simulation in this worker is fast."""
    import os
    simulate({"gas": 1000.0}, 2030, 2008)
    return os.getpid()


def resolve_stage_sequential(game: dict) -> dict[str, tuple[dict, pd.DataFrame]]:
    """Close the stage and resolve all teams in this process (used by single-player mode and calibration)."""
    luck = core.close_stage(game)
    out = {}
    for tid in game["teams"]:
        summary, disp = run_engine(core.engine_args(game, tid, luck))
        core.apply_stage_result(game, tid, summary)
        out[tid] = (summary, disp)
    core.finish_resolution(game)
    return out


# ----------------------------------------------------------------------------- chart shortcuts
SERIES_ORDER = ["ror", "biomass", "coal", "gas", "gas_new", "other_fossil", "reserve", "gas_new_h2", "h2_turbine",
                "offwind", "onwind", "solar_utility", "solar_rooftop", "phs_discharge", "battery_discharge", "lost_load"]
NEG_SERIES = ["battery_charge", "phs_charge", "electrolyser"]
SERIES_LABELS = TDict({
    "ror": "Laufwasser", "biomass": "Biomasse", "coal": "Kohle", "gas": "Gas (Bestand)", "gas_new": "Gas (neu)",
    "gas_new_h2": "H₂ in umgerüsteten Gasturbinen", "h2_turbine": "Wasserstoff-Turbine", "offwind": "Offshore-Wind",
    "onwind": "Onshore-Wind", "solar_utility": "Freiflächen-PV", "solar_rooftop": "Dach-PV",
    "battery_discharge": "Batterie (Entladen)", "lost_load": "Nicht gedeckter Bedarf",
    "battery_charge": "Batterie (Laden)", "electrolyser": "Elektrolyse", "demand": "Verbrauch",
    "other_fossil": "Öl & sonstige Konventionelle", "reserve": "Reservekraftwerke",
    "phs_discharge": "Pumpspeicher (Turbine)", "phs_charge": "Pumpspeicher (Pumpen)",
    "waste": "Abfallverbrennung", "import": "Import", "export": "Export",
    "onwind_old": "davon Onshore-Bestand", "offwind_old": "davon Offshore-Bestand",
    "flex_shed": "Lastverzicht (Industrie)", "flex_shift_discharge": "Lastverschiebung (verlagerter Verbrauch)",
})
SERIES_COLORS = {
    "ror": "#4e79a7", "biomass": "#59a14f", "coal": "#6b5b45", "gas": "#e15759", "gas_new": "#f28e8c",
    "gas_new_h2": "#b07aa1", "h2_turbine": "#9c6ade", "offwind": "#2f6fb0", "onwind": "#76b7e5",
    "solar_utility": "#f1ce63", "solar_rooftop": "#f5a623", "battery_discharge": "#d37295",
    "lost_load": "#111111", "battery_charge": "#e8a6c0", "electrolyser": "#c9b3e8", "demand": "#222222",
    "other_fossil": "#8c8c8c", "reserve": "#4d4d4d", "phs_discharge": "#17becf", "phs_charge": "#9edae5",
}


def week_shortcuts(disp: pd.DataFrame, event: dict | None = None) -> dict[str, int]:
    """Start hour of interesting weeks (168 h windows)."""
    def best(x: np.ndarray, mode="max") -> int:
        s = pd.Series(x).rolling(168).sum().to_numpy()[167:]
        i = int(np.nanargmax(s) if mode == "max" else np.nanargmin(s))
        return i

    wind = (disp["onwind"] + disp["offwind"]).to_numpy()
    solar = (disp["solar_utility"] + disp["solar_rooftop"]).to_numpy()
    resid = disp["demand"].to_numpy() - wind - solar - disp["ror"].to_numpy()
    out = {tr("Spitzenlast"): max(0, min(int(np.argmax(disp["demand"].to_numpy())) - 84, 8760 - 168)),
           tr("Dunkelflaute (höchste Residuallast)"): best(resid),
           tr("Wenigster Wind"): best(wind, "min"),
           tr("Meiste Sonne"): best(solar),
           tr("Meiste Abregelung"): best(disp["curtailment"].to_numpy())}
    if disp["lost_load"].sum() > 0.1:
        out = {tr("Größte Versorgungslücke"): best(disp["lost_load"].to_numpy()), **out}
    if disp["battery_discharge"].sum() > 0.1:
        out[tr("Meiste Batterienutzung")] = best(disp["battery_discharge"].to_numpy())
    if "reserve" in disp and disp["reserve"].sum() > 0.1:
        out[tr("Meiste Reserve-Einsätze")] = best(disp["reserve"].to_numpy())
    h2 = (disp["h2_turbine"] + disp["gas_new_h2"]).to_numpy()
    if h2.sum() > 0.1:
        out[tr("Meiste Wasserstoff-Verstromung")] = best(h2)
    if event:
        out[tr("Katastrophenzeitraum")] = int(event["start"])
    return out


def daily(disp: pd.DataFrame) -> pd.DataFrame:
    return disp.groupby(np.arange(len(disp)) // 24).mean()


MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
          "November", "Dezember"]


def hour_label(h: int) -> str:
    import datetime as dt
    t = dt.datetime(2001, 1, 1) + dt.timedelta(hours=int(h))
    return tr("{0}. {1}, {2}:00 Uhr", t.day, tr(MONTHS[t.month - 1]), t.hour)


def _de(x: float, d: int = 1) -> str:
    return num(x, d)


def insights(summary: dict, disp: pd.DataFrame | None, cost: dict | None = None) -> list[str]:
    """Up to four plain-language explanations of a simulated year ("Warum?")."""
    out = []
    g = summary.get("generation_twh", {})
    if disp is not None:
        ll = disp["lost_load"].to_numpy()
        vre = (disp["onwind"] + disp["offwind"] + disp["solar_utility"] + disp["solar_rooftop"]).to_numpy()
        if summary["lole_hours"] > 0 and ll.max() > 0.05:
            h = int(np.argmax(ll))
            out.append(tr("Größte Versorgungslücke: {0} GW am {1} – Wind und Sonne lieferten da nur {2} GW bei {3} GW Verbrauch.", _de(ll[h]), hour_label(h), _de(vre[h]), _de(disp['demand'].iloc[h])))
        else:
            resid = disp["demand"].to_numpy() - vre
            h = int(np.argmax(resid))
            out.append(tr("Keine Versorgungslücke. Knappste Stunde: {0} – {1} GW mussten steuerbare Kraftwerke, Speicher und Importe liefern.", hour_label(h), _de(resid[h])))
    served = max(summary.get("served_twh", 0), 1e-6)
    gas = g.get("gas", 0) + g.get("gas_new", 0)
    coal = g.get("coal", 0)
    other = g.get("other_fossil", 0) + g.get("reserve", 0) + 0.5 * g.get("waste", 0)   # half of waste is fossil
    fossil = gas + coal + other
    if fossil / served > 0.005:
        parts = [tr("Erdgas {0} %", _de(100 * gas / served, 0)), tr("Kohle {0} %", _de(100 * coal / served, 0))]
        if other / served > 0.005:
            parts.append(tr("Sonstige/Reserve/Abfall {0} %", _de(100 * other / served, 0)))
        out.append(tr("Fossile Kraftwerke lieferten {0} % des Stroms ({1}) – {2} Mt CO₂.", _de(100 * fossil / served, 0), ', '.join(parts), _de(summary.get('co2_mt', 0))))
    else:
        out.append(tr("Praktisch kein fossiler Strom in diesem Jahr."))
    imp, exp = summary.get("import_twh", 0), summary.get("export_twh", 0)
    if imp > 1 or exp > 1:
        out.append(tr("Import {0} TWh ({1} % des Verbrauchs, zählt nicht als erneuerbar), Export {2} TWh (exportierter Ökostrom zählt mit).", _de(imp, 0), _de(100 * imp / served, 0), _de(exp, 0)))
    vre_gen = sum(g.get(k, 0) for k in ["onwind", "offwind", "solar_utility", "solar_rooftop"])
    curt = summary.get("curtailment_twh", 0)
    if curt > 0.05 * (vre_gen + curt) and curt > 1:
        out.append(tr("{0} TWh Wind- und Sonnenstrom wurden abgeregelt ({1} % des möglichen) – Speicher oder Elektrolyse könnten ihn nutzen.", _de(curt), _de(100 * curt / (vre_gen + curt), 0)))
    if cost:
        blocks = {tr("Investitionen"): cost.get("capex_bn", 0), tr("Fixe Betriebskosten"): cost.get("fom_bn", 0),
                  tr("Brennstoff, CO₂ & variable Kosten"): cost.get("opex_bn", 0)}
        k = max(blocks, key=blocks.get)
        out.append(tr("Größter Kostenblock: {0} mit {1} Mrd. €/Jahr (von {2} Mrd. € gesamt).", k, _de(blocks[k]), _de(cost.get('total_bn', 0))))
    return out[:5]


def grouped(d: pd.DataFrame, groups: dict) -> dict[str, np.ndarray]:
    out = {}
    for name, (_, members) in groups.items():
        cols = [c for c in members if c in d]
        if cols:
            out[name] = d[cols].sum(axis=1).to_numpy()
    return out
