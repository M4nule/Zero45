# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Game rules: state, decisions, shared luck, scoring, learning and backlash.

The state is a plain dict (JSON-serialisable) so it can be saved after every action.
Dispatch is computed by ptz.engine.model.simulate (called by the server / runner, possibly in another process).
"""
from __future__ import annotations

import copy
import json
import secrets
import time
import zlib
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

from ptz.engine.model import CAP_KEYS, FIXED_KEYS, assumptions, fixed_capacities, trade_capacity
from ptz.i18n import TDict, num, tr

PKG = Path(__file__).resolve().parents[1]
GAME_DEFAULT = PKG / "config" / "game_default.yaml"

NEW_TECHS = ["onwind", "offwind", "solar_utility", "solar_rooftop", "battery", "h2_package", "h2_storage", "gas_new",
             "biomass_flex"]
EXISTING = ["coal", "gas", "biomass", "ror"]
LABELS = TDict({
    "onwind": "Onshore-Wind", "offwind": "Offshore-Wind", "solar_utility": "Freiflächen-PV",
    "solar_rooftop": "Dach-PV", "battery": "Batteriespeicher (4-h-Speicher)", "h2_package": "Wasserstoff: Elektrolyse",
    "h2_storage": "Wasserstoff-Speicher (Kaverne)",
    "gas_new": "Neue Gasturbinen (H₂-ready)", "biomass_flex": "Biomasse-Flexibilisierung",
    "coal": "Kohle (Braun- & Steinkohle)", "gas": "Bestehende Gaskraftwerke", "biomass": "Biomasse/Biogas",
    "ror": "Laufwasser", "gas_new_h2": "Gasturbinen auf H₂ umgerüstet", "waste": "Abfallverbrennung",
    "trade": "Import/Export (Kuppelleitungen)",
    "onwind_old": "Onshore-Wind (Bestand)", "offwind_old": "Offshore-Wind (Bestand)",
    "battery_old": "Großbatterien (Bestand, 1-h-Speicher)", "phs": "Pumpspeicher", "other_fossil": "Öl & sonstige Konventionelle",
    "reserve": "Netz- & Kapazitätsreserve",
})
_hi = assumptions()["technologies"]["h2_import"]
_eff = assumptions()["technologies"]["gas_new"]["efficiency"]
INFLUENCE = TDict({   # one sentence each (cards and rules); details in INFLUENCE_DETAIL. Order = display order.
    # policy & society
    "social": ("Akzeptanz & Teilhabe", "Halbiert das Risiko gesellschaftlicher Gegenreaktionen – ab dieser Stufe."),
    "innovation": ("Beschleunigte Innovation", "Doppelte Kostensenkung durch eigene Bauprojekte – ab dieser Stufe."),
    "resilience": ("Klimaresilienz", "Halbiert die Folgen von Katastrophen (auch Dunkelflaute, Hitze) – ab dieser Stufe."),
    # technology & infrastructure
    "h2_demo": ("Demonstrationsprogramm Wasserstoff",
                "Eigener grüner Wasserstoff: Elektrolyse, Speicher und Umrüstung von Gasturbinen – ab der nächsten Stufe."),
    "h2_grid": ("Wasserstoff-Netz & Import", "Importierter Wasserstoff für umgerüstete Gasturbinen, dazu Speicher und "
                "Umrüstung (keine Elektrolyse) – ab der nächsten Stufe."),
    "grid_eu": ("Netzausbau Europa", f"+{assumptions()['trade']['grid_eu_bonus_mw'] / 1e3:.0f} GW Leitungen ins Ausland "
                "für Import und Export – ab der nächsten Stufe."),
    "flex": ("Flexible Verbraucher", "E-Autos, Wärmepumpen und Industrie passen ihren Verbrauch an – ab der nächsten Stufe."),
})
INFLUENCE_GROUPS = [("Politik & Gesellschaft", ["social", "innovation", "resilience"]),
                    ("Technik & Infrastruktur", ["h2_demo", "h2_grid", "grid_eu", "flex"])]
INFLUENCE_DETAIL = TDict({
    "h2_demo": "Elektrolyse gibt es nur mit dieser Karte. Sie läuft nur mit deutschem Ökostrom-Überschuss.",
    "h2_grid": "Teuer, aber CO₂-frei. Import: " + "; ".join(
        f"{y}: {_hi['capacity_mw'][y] / 1e3:.0f} GW H₂ (≈ {_hi['capacity_mw'][y] * _eff / 1e3:.0f} GW Strom) "
        f"zu {_hi['price'][y]:.0f} €/MWh H₂" for y in sorted(_hi["capacity_mw"]) if _hi["capacity_mw"][y] > 0) + ".",
    "flex": "Verbrauch wird innerhalb eines Tages verschoben; die Industrie verzichtet bei Knappheit (ab 300 €/MWh). "
            "Wächst mit jeder Stufe.",
})
PHASES = ["lobby", "build", "resolving", "results", "finished"]
STATE_VERSION = 5   # bump when the saved state format changes (older saved games are not loaded)


@lru_cache(maxsize=1)
def default_config() -> dict:
    return yaml.safe_load(GAME_DEFAULT.read_text(encoding="utf-8"))


def stage_years() -> list[int]:
    return list(assumptions()["stages"])


# ----------------------------------------------------------------------------- economics
def annuity(lifetime: float, r: float | None = None) -> float:
    r = assumptions()["discount_rate"] if r is None else r
    return r / (1 - (1 + r) ** -lifetime)


def invest_eur_kw(tech: str, year: int) -> float:
    return float(assumptions()["technologies"][tech]["invest"][year])


def mw_per_token(team: dict, tech: str, year: int, cfg: dict) -> float:
    """MW bought by one build token for this team (DEA cost of the stage year x team learning)."""
    eur_kw = invest_eur_kw(tech, year) * team["learn"].get(tech, 1.0)
    return cfg["token_value_bn"] * 1e9 / (eur_kw * 1e3)


def start_capacities() -> dict:
    ex = assumptions()["existing"]
    cap = {k: 0.0 for k in CAP_KEYS}
    cap.update(onwind_old=ex["onwind"], offwind_old=ex["offwind"],
               solar_utility=ex["solar_total"] * (1 - ex["solar_rooftop_share"]),
               solar_rooftop=ex["solar_total"] * ex["solar_rooftop_share"],
               biomass=ex["biomass"], gas=ex["gas"], coal=ex["lignite"] + ex["hard_coal"], ror=ex["ror"])
    cap.update(fixed_capacities(stage_years()[0]))
    return cap


# ----------------------------------------------------------------------------- creation
def new_game(cfg: dict | None = None, mode: str = "server") -> dict:
    cfg = copy.deepcopy(cfg or default_config())
    seed = cfg.get("seed")
    return {
        "version": STATE_VERSION,
        "pin": f"{secrets.randbelow(900000) + 100000}",
        "mode": mode,
        "cfg": cfg,
        "created": time.time(),
        "seed": int(seed) if seed not in (None, "") else secrets.randbelow(2**31),
        "stage": 0,                     # index 0..3
        "phase": "lobby",
        "timer_end": None,
        "luck": [None] * cfg["stages"],
        "teams": {},
        "log": [],
    }


def can_join(game: dict) -> str | None:
    if game["phase"] in ("resolving", "finished"):
        return tr("Beitritt gerade nicht möglich (Spiel wird berechnet oder ist beendet).")
    if len(game["teams"]) >= game["cfg"].get("max_teams", 99):
        return tr("Das Spiel ist voll.")
    return None


def remove_team(game: dict, tid: str):
    game["teams"].pop(tid, None)


def clean_name(name: str) -> str:
    """Team names are shown on the projector and in charts: no markup characters, no control characters."""
    name = "".join(" " if ch.isspace() else ch for ch in (name or ""))
    name = "".join(ch for ch in name if ch.isprintable() and ch not in "<>{}`\\")
    return " ".join(name.split())[:30]


def add_team(game: dict, name: str) -> tuple[str, str]:
    name = clean_name(name) or tr("Team {0}", len(game['teams']) + 1)
    if any(t["name"].lower() == name.lower() for t in game["teams"].values()):
        name = f"{name} ({len(game['teams']) + 1})"
    tid = secrets.token_hex(4)
    cap = start_capacities()
    game["teams"][tid] = {
        "id": tid, "name": name, "secret": secrets.token_urlsafe(16), "joined": time.time(),
        "cap": cap,
        "start_cap": copy.deepcopy(cap),
        "learn": {t: 1.0 for t in NEW_TECHS},
        "investments": [],             # {tech, mw, eur_kw, stage, lifetime, fom}
        "blocked": [],                 # techs blocked this stage by backlash
        "influence_tokens": game["cfg"]["influence_tokens_start"],
        "influence_used": {},          # key -> stage index
        "h2_unlocked_from": None,      # H2 storage and conversion (h2_demo or h2_grid)
        "electrolysis_from": None,     # electrolysis (h2_demo only)
        "draft": None,
        "sims_used": 0,
        "submitted": False,
        "status": "bearbeitet",
        "history": [],
        "penalty": 0,
        "ready": False,
        "rev": 0,                      # bumped on every change (refreshes other devices of the team)
    }
    reset_draft(game, tid)
    return tid, game["teams"][tid]["secret"]


def reset_draft(game: dict, tid: str):
    team = game["teams"][tid]
    s = game["stage"]
    year = stage_years()[s]
    coal_max = assumptions()["existing_params"]["coal_max_mw"][year]
    keep = {k: team["cap"][k] for k in EXISTING}
    keep["coal"] = min(keep["coal"], coal_max)
    for k in EXISTING:
        if k in team["blocked"]:
            keep[k] = 0.0
    team["draft"] = {"build": {t: 0 for t in NEW_TECHS}, "keep": keep, "convert_mw": 0.0, "borrow": 0,
                     "influence_bought": 0, "influence_new": []}
    team["sims_used"] = 0
    team["submitted"] = False
    team["ready"] = False
    team["status"] = "bearbeitet"
    team["rev"] = team.get("rev", 0) + 1


# ----------------------------------------------------------------------------- decisions
def tokens_total(game: dict, tid: str) -> int:
    d = game["teams"][tid]["draft"]
    cfg = game["cfg"]
    return cfg["build_tokens"][game["stage"]] + d["borrow"] - d["influence_bought"] * cfg["influence_token_price"]


def tokens_left(game: dict, tid: str) -> int:
    return tokens_total(game, tid) - sum(game["teams"][tid]["draft"]["build"].values())


H2_TECHS = ("h2_package", "h2_storage")


def h2_available(game: dict, tid: str, tech: str | None = None) -> bool:
    """Storage and conversion: after either H2 card. Electrolysis ("h2_package"): only after h2_demo."""
    team = game["teams"][tid]
    if tech == "h2_package":   # fallback for saved games without electrolysis_from
        u = team["electrolysis_from"] if "electrolysis_from" in team else team["h2_unlocked_from"]
    else:
        u = team["h2_unlocked_from"]
    return u is not None and game["stage"] >= u


def can_build(game: dict, tid: str, tech: str) -> tuple[bool, str]:
    team = game["teams"][tid]
    if tech in team["blocked"]:
        return False, tr("Gesellschaftliche Gegenreaktion – in dieser Stufe gesperrt")
    if tech in H2_TECHS and not h2_available(game, tid, tech):
        if tech == "h2_package":
            return False, tr("Erst nach dem Demonstrationsprogramm Wasserstoff (ab der Folgestufe)")
        return False, tr("Erst nach Demonstrationsprogramm Wasserstoff oder Wasserstoff-Netz (ab der Folgestufe)")
    if tech == "biomass_flex":
        year = stage_years()[game["stage"]]
        add = (team["draft"]["build"]["biomass_flex"] + 1) * mw_per_token(team, tech, year, game["cfg"])
        if team["cap"]["biomass_flex"] + add > flex_max(game, tid) + 1:
            return False, tr("Flexibilisierung höchstens bis zur dreifachen Leistung der weiterbetriebenen Biomasse")
    return True, ""


def editable(game: dict, tid: str) -> bool:
    return game["phase"] == "build" and not game["teams"][tid]["submitted"]


def change_build(game: dict, tid: str, tech: str, delta: int) -> str | None:
    if not editable(game, tid):
        return tr("Die Bauphase ist geschlossen.")
    d = game["teams"][tid]["draft"]
    if delta > 0:
        ok, why = can_build(game, tid, tech)
        if not ok:
            return why
        if tokens_left(game, tid) < delta:
            return tr("Keine Bau-Token mehr übrig.")
    d["build"][tech] = max(0, d["build"][tech] + delta)
    return None


def set_keep(game: dict, tid: str, tech: str, mw: float) -> str | None:
    if not editable(game, tid):
        return tr("Die Bauphase ist geschlossen.")
    team = game["teams"][tid]
    year = stage_years()[game["stage"]]
    mx = team["cap"][tech]
    if tech == "coal":
        mx = min(mx, assumptions()["existing_params"]["coal_max_mw"][year])
    if tech in team["blocked"]:
        mx = 0.0
    team["draft"]["keep"][tech] = float(min(max(0.0, mw), mx))
    return None


def max_convert(game: dict, tid: str) -> float:
    team = game["teams"][tid]
    if not h2_available(game, tid):
        return 0.0
    year = stage_years()[game["stage"]]
    new_gas = team["cap"]["gas_new"] + team["draft"]["build"]["gas_new"] * mw_per_token(team, "gas_new", year, game["cfg"])
    return float(new_gas)


def h2_capacity_planned(game: dict, tid: str, tech: str = "h2_package") -> float:
    """Existing capacity plus tokens drafted this stage (tokens > 0 is enough to count as planned)."""
    team = game["teams"][tid]
    return team["cap"].get(tech, 0.0) + team["draft"]["build"].get(tech, 0)


def h2_ready(game: dict, tid: str) -> bool:
    """Conversion needs a hydrogen supply: own electrolysis and storage (existing or drafted), or pipeline import."""
    return all(h2_capacity_planned(game, tid, t) > 0 for t in H2_TECHS) or h2_import_cap(game, tid) > 0


def effective_convert(game: dict, tid: str) -> float:
    """Conversion that actually happens: limited by new gas available, needs electrolysis and storage."""
    team = game["teams"][tid]
    if not h2_ready(game, tid):
        return 0.0
    year = stage_years()[game["stage"]]
    new_gas = team["cap"]["gas_new"] + team["draft"]["build"]["gas_new"] * mw_per_token(team, "gas_new", year, game["cfg"])
    return float(max(0.0, min(team["draft"]["convert_mw"], new_gas)))


def set_convert(game: dict, tid: str, mw: float) -> str | None:
    if not editable(game, tid):
        return tr("Die Bauphase ist geschlossen.")
    team = game["teams"][tid]
    if mw > 0 and not h2_ready(game, tid):
        return (tr("Umrüstung braucht Wasserstoff: Elektrolyse und Speicher (gebaut oder in dieser Stufe geplant) oder Import über das Wasserstoff-Netz."))
    team["draft"]["convert_mw"] = float(min(max(0.0, mw), max_convert(game, tid)))
    return None


def set_borrow(game: dict, tid: str, n: int) -> str | None:
    if not editable(game, tid):
        return tr("Die Bauphase ist geschlossen.")
    d = game["teams"][tid]["draft"]
    n = int(min(max(0, n), game["cfg"]["max_borrow_tokens"]))
    used = sum(d["build"].values())
    if game["cfg"]["build_tokens"][game["stage"]] + n - d["influence_bought"] * game["cfg"]["influence_token_price"] < used:
        return tr("Erst Bau-Token zurücknehmen.")
    d["borrow"] = n
    return None


def buy_influence(game: dict, tid: str, delta: int = 1) -> str | None:
    if not editable(game, tid):
        return tr("Die Bauphase ist geschlossen.")
    team = game["teams"][tid]
    d = team["draft"]
    if delta > 0:
        if tokens_left(game, tid) < game["cfg"]["influence_token_price"]:
            return tr("Nicht genug Bau-Token.")
        d["influence_bought"] += 1
        team["influence_tokens"] += 1
    else:
        if d["influence_bought"] == 0 or team["influence_tokens"] - len(d["influence_new"]) <= 0:
            return tr("Nichts zurückzunehmen.")
        d["influence_bought"] -= 1
        team["influence_tokens"] -= 1
    return None


def toggle_influence(game: dict, tid: str, key: str) -> str | None:
    if not editable(game, tid):
        return tr("Die Bauphase ist geschlossen.")
    team = game["teams"][tid]
    d = team["draft"]
    if key in team["influence_used"]:
        return tr("Bereits eingesetzt.")
    if key in d["influence_new"]:
        d["influence_new"].remove(key)
        return None
    if team["influence_tokens"] - len(d["influence_new"]) <= 0:
        return tr("Kein Einfluss-Token frei.")
    d["influence_new"].append(key)
    return None


def influence_active(game: dict, tid: str, key: str) -> bool:
    team = game["teams"][tid]
    return key in team["influence_used"] or key in team["draft"]["influence_new"]


def apply_ageing(cap: dict, start_cap: dict, year: int) -> dict:
    """Existing wind/PV fleet shrinks over time (fleet_remaining); team caps store the un-aged values."""
    rem = assumptions()["fleet_remaining"]
    out = dict(cap)
    out["onwind_old"] = start_cap.get("onwind_old", 0.0) * rem["onwind_old"][year]
    out["offwind_old"] = start_cap.get("offwind_old", 0.0) * rem["offwind_old"][year]
    for t in ("solar_utility", "solar_rooftop"):
        out[t] = max(0.0, cap[t] - start_cap.get(t, 0.0) * (1 - rem["solar"][year]))
    return out


def old_fleet(team: dict, key: str, year: int) -> float:
    """Remaining MW of the start fleet (key: onwind_old, offwind_old, solar_utility, solar_rooftop)."""
    rem = assumptions()["fleet_remaining"]
    r = rem["solar"][year] if key.startswith("solar") else rem[key][year]
    return team["start_cap"].get(key, 0.0) * r


def trade_cap(game: dict, tid: str, year: int | None = None) -> float:
    team = game["teams"][tid]
    s = game["stage"]
    year = year or stage_years()[s]
    used = team["influence_used"].get("grid_eu")
    bonus = assumptions()["trade"]["grid_eu_bonus_mw"] if used is not None and used < stage_years().index(year) else 0
    return trade_capacity(year) + bonus


def h2_import_cap(game: dict, tid: str, year: int | None = None) -> float:
    """Pipeline hydrogen (influence "h2_grid"): from the stage after the card was played."""
    team = game["teams"][tid]
    year = year or stage_years()[game["stage"]]
    used = team["influence_used"].get("h2_grid")
    if used is None or used >= stage_years().index(year):
        return 0.0
    return float(assumptions()["technologies"]["h2_import"]["capacity_mw"][year])


def flex_caps(game: dict, tid: str, year: int | None = None) -> dict[str, float]:
    """Flexible consumers (influence "flex"): active from the stage after the card was played."""
    team = game["teams"][tid]
    year = year or stage_years()[game["stage"]]
    used = team["influence_used"].get("flex")
    if used is None or used >= stage_years().index(year):
        return {"flex_shift": 0.0, "flex_shed": 0.0}
    fl = assumptions()["flexibility"]
    return {"flex_shift": float(fl["shift_mw"][year]), "flex_shed": float(fl["shed_mw"][year])}


def portfolio(game: dict, tid: str, aged: bool = True) -> dict:
    """Capacities (MW) that would be in operation this stage with the current draft."""
    team = game["teams"][tid]
    d = team["draft"]
    year = stage_years()[game["stage"]]
    cap = dict(team["cap"])
    for t in NEW_TECHS:
        cap[t] = team["cap"][t] + d["build"][t] * mw_per_token(team, t, year, game["cfg"])
    for k in EXISTING:
        cap[k] = d["keep"][k]
    # flexibilisation only works at biomass plants that are kept
    cap["biomass_flex"] = min(cap["biomass_flex"], flex_max(game, tid))
    conv = effective_convert(game, tid)
    cap["gas_new"] -= conv
    cap["gas_new_h2"] = team["cap"]["gas_new_h2"] + conv
    cap.update(fixed_capacities(year))
    cap["trade"] = trade_cap(game, tid, year)
    cap.update(flex_caps(game, tid, year))
    cap["h2_import"] = h2_import_cap(game, tid, year)
    if aged:
        cap = apply_ageing(cap, team["start_cap"], year)
    return cap


def flex_max(game: dict, tid: str) -> float:
    """Max. effective flexibilisation MW: max_per_base x kept biomass base capacity."""
    k = assumptions()["technologies"]["biomass_flex"].get("max_per_base", 1.0)
    return k * game["teams"][tid]["draft"]["keep"]["biomass"]


def flex_built(game: dict, tid: str) -> float:
    """Biomass flexibilisation MW owned after this stage's draft (independent of how much biomass is kept)."""
    team = game["teams"][tid]
    year = stage_years()[game["stage"]]
    return team["cap"]["biomass_flex"] + team["draft"]["build"]["biomass_flex"] * mw_per_token(team, "biomass_flex", year, game["cfg"])


# capacity that can be dispatched on demand (storage at full power; wind and sun count zero, run-of-river half)
FIRM_KEYS = ["gas", "gas_new", "coal", "other_fossil", "reserve", "biomass", "biomass_flex"]   # + h2_firm()
H2_FIRM_HOURS = 336   # converted turbines count as secured only as far as hydrogen lasts through a 2-week Dunkelflaute
# storage and flexible demand help for hours, not through a multi-day Dunkelflaute: shown separately
SHORT_KEYS = ["battery", "battery_old", "phs", "flex_shift", "flex_shed"]


def h2_firm(cap: dict) -> float:
    """Converted H2 turbines that count as secured: limited by the hydrogen available for two weeks
    (pipeline import + full store / 336 h, converted to electricity). A convention for the display only -
    scoring uses the hourly model, where electrolysis can also refill the store."""
    e = assumptions()["technologies"]["gas_new"]["efficiency"]
    supply = (cap.get("h2_import", 0.0) + cap.get("h2_storage", 0.0) / H2_FIRM_HOURS) * e
    return min(cap.get("gas_new_h2", 0.0), supply)


def firm_capacity(cap: dict) -> float:
    """Secured capacity: dispatchable plants only (no storage, no flexible demand, no imports)."""
    return (sum(cap.get(k, 0.0) for k in FIRM_KEYS) + h2_firm(cap)
            + 0.5 * cap.get("ror", 0.0) + 0.65 * cap.get("waste", 0.0))


def short_term_capacity(cap: dict) -> float:
    """Storage and flexible demand: full power, but only for a few hours."""
    return sum(cap.get(k, 0.0) for k in SHORT_KEYS)


def h2_reach(cap: dict) -> dict:
    """What a full hydrogen store gives back: electricity (TWh) and full-load hours of the H2 turbines."""
    e = assumptions()["technologies"]["gas_new"]["efficiency"]
    twh_el = cap.get("h2_storage", 0.0) * e / 1e6
    turb = cap.get("gas_new_h2", 0.0)
    return {"store_twh": cap.get("h2_storage", 0.0) / 1e6, "twh_el": twh_el,
            "hours": (twh_el * 1e6 / turb) if turb > 0 else 0.0}


def h2_warnings(cap: dict) -> list[str]:
    """Missing building blocks of the hydrogen chain (electrolysis or import -> storage -> converted turbines)."""
    el, st, tu = cap.get("h2_package", 0.0) > 1, cap.get("h2_storage", 0.0) > 1, cap.get("gas_new_h2", 0.0) > 1
    imp = cap.get("h2_import", 0.0) > 1
    if not (el or st or tu):
        return []
    out = []
    e = assumptions()["technologies"]["gas_new"]["efficiency"]
    if tu and not st and not imp:
        out.append(tr("Umgerüstete Gasturbinen ohne Wasserstoff-Speicher liefern keinen Strom."))
    if tu and st and not el and not imp:
        out.append(tr("Ohne Elektrolyse bleibt der Wasserstoff-Speicher leer – die H₂-Turbinen liefern nichts."))
    if tu and imp and not st and cap["gas_new_h2"] > cap["h2_import"] * e * 1.05:
        out.append(tr("Der Import reicht nur für {0:.0f} GW eurer H₂-Turbinen gleichzeitig – für Spitzen braucht ihr zusätzlich einen Speicher.", cap['h2_import'] * e / 1e3))
    if el and not st:
        out.append(tr("Elektrolyse ohne Speicher: Der Wasserstoff kann nicht aufbewahrt werden."))
    if st and not el and not tu and not imp:
        out.append(tr("Ein Speicher allein nützt nichts – es fehlen Elektrolyse und umgerüstete Gasturbinen."))
    if (el or imp) and st and not tu:
        out.append(tr("Wasserstoff wird erzeugt und gespeichert, aber nicht verstromt – es fehlen umgerüstete Gasturbinen."))
    return out


CAP_GROUPS = {
    "Wind": ["onwind_old", "onwind", "offwind_old", "offwind"],
    "Sonne": ["solar_utility", "solar_rooftop"],
    "Speicher": ["battery_old", "battery", "phs"],
    "Steuerbar CO₂-frei": ["biomass", "biomass_flex", "ror", "gas_new_h2"],
    "Steuerbar fossil": ["coal", "gas", "gas_new", "other_fossil", "reserve", "waste"],
    "Wasserstoff-Elektrolyse": ["h2_package"],
    "Flexible Verbraucher": ["flex_shift", "flex_shed"],
}


def cap_groups(cap: dict) -> dict[str, float]:
    return {g: sum(cap.get(k, 0.0) for k in ks) for g, ks in CAP_GROUPS.items()}


def stage_start_cap(game: dict, tid: str) -> dict:
    """Capacities at the start of the current stage (before this stage's decisions)."""
    team = game["teams"][tid]
    year = stage_years()[game["stage"]]
    cap = dict(team["cap"])
    cap.update(fixed_capacities(year))
    cap["trade"] = trade_cap(game, tid, year)
    cap.update(flex_caps(game, tid, year))
    cap["h2_import"] = h2_import_cap(game, tid, year)
    return apply_ageing(cap, team["start_cap"], year)


def draft_summary(game: dict, tid: str) -> dict:
    """What the team is about to do this stage (for the confirmation dialog)."""
    team = game["teams"][tid]
    d = team["draft"]
    year = stage_years()[game["stage"]]
    builds = {t: (n, n * mw_per_token(team, t, year, game["cfg"])) for t, n in d["build"].items() if n > 0}
    coal_max = assumptions()["existing_params"]["coal_max_mw"][year]
    allowed = {k: (min(team["cap"][k], coal_max) if k == "coal" else team["cap"][k]) for k in EXISTING}
    retire = {k: allowed[k] - d["keep"][k] for k in EXISTING if allowed[k] - d["keep"][k] > 1}
    forced = {"coal": team["cap"]["coal"] - allowed["coal"]} if team["cap"]["coal"] - allowed["coal"] > 1 else {}
    return {"builds": builds, "retire": retire, "forced": forced, "convert": effective_convert(game, tid),
            "influence": list(d["influence_new"]), "tokens_left": tokens_left(game, tid),
            "influence_free": team["influence_tokens"] - len(d["influence_new"]), "borrow": d["borrow"]}


def biomass_share(game: dict, tid: str) -> float:
    team = game["teams"][tid]
    base = team["start_cap"]["biomass"]
    return (team["draft"]["keep"]["biomass"] / base) if base > 0 else 0.0


# ----------------------------------------------------------------------------- shared luck
def _rng(game: dict, *salt) -> np.random.Generator:
    return np.random.default_rng([game["seed"], *[zlib.crc32(str(x).encode()) for x in salt]])


def draw_luck(game: dict) -> dict:
    """Shared luck of the current stage: weather year, demand shock and (maybe) a disaster."""
    cfg, a = game["cfg"], assumptions()
    s = game["stage"]
    rng = np.random.default_rng([game["seed"], 1000 + s])
    probs = cfg.get("weather_probabilities") or {"normal": 1 - cfg.get("harder_year_probability", 0.3),
                                                 "hard": cfg.get("harder_year_probability", 0.3), "extreme": 0.0}
    x = rng.random()
    level = "extreme" if x < probs.get("extreme", 0) else ("hard" if x < probs.get("extreme", 0) + probs.get("hard", 0)
                                                           else "normal")
    wy = {"normal": a["normal_weather_year"], "hard": a["harder_weather_year"], "extreme": a["extreme_weather_year"]}
    luck = {"weather_year": wy[level], "weather_level": level, "harder_year": level != "normal",
            "demand_shock": float(np.clip(rng.normal(0, cfg["demand_shock_sd"]), -0.1, 0.1)),
            "event": None}
    if cfg["disasters_enabled"] and rng.random() < cfg["disaster_probability"][s]:
        kinds = list(cfg["disaster_type_weights"])
        w = np.array([cfg["disaster_type_weights"][k] for k in kinds], dtype=float)
        kind = kinds[rng.choice(len(kinds), p=w / w.sum())]
        if kind == "storm":
            start = int(rng.integers(0, 49)) * 168
            hit = [t for t in ["onwind", "offwind", "solar", "gas", "gas_new", "coal", "biomass", "battery",
                               "h2_package", "ror"] if rng.random() < cfg["storm_hit_probability"]]
            ev = {"kind": "storm", "start": start, "hours": 4 * 168, "factors": {t: 0.5 for t in hit},
                  "demand_factor": 1.0}
        elif kind == "dunkelflaute":
            # two weeks between November and February
            windows = list(range(0, 59 * 24 - 336, 24)) + list(range(305 * 24, 8760 - 336, 24))
            start = int(rng.choice(windows))
            ev = {"kind": "dunkelflaute", "start": start, "hours": 336,
                  "factors": {"onwind": 0.3, "offwind": 0.3, "solar": 0.5}, "demand_factor": 1.05}
        else:
            start = int(rng.integers(152, 244 - 28)) * 24  # June - September
            ev = {"kind": "heat", "start": start, "hours": 4 * 168,
                  "factors": {"gas": 0.8, "gas_new": 0.8, "coal": 0.8, "biomass": 0.8, "ror": 0.6},
                  "demand_factor": 1.03}
        luck["event"] = ev
    return luck


def team_event(game: dict, tid: str, event: dict | None) -> dict | None:
    if not event:
        return None
    ev = copy.deepcopy(event)
    if influence_active(game, tid, "resilience"):
        k = game["cfg"]["resilience_factor"]
        ev["factors"] = {t: 1 - (1 - f) * k for t, f in ev["factors"].items()}
        ev["demand_factor"] = 1 + (ev["demand_factor"] - 1) * k
    return ev


EVENT_TEXT = TDict({
    "storm": "Sturm/Hochwasser: Anlagen beschädigt – betroffene Technologien liefern 4 Wochen nur halbe Leistung.",
    "dunkelflaute": "Kalte Dunkelflaute: 2 Wochen kaum Wind und wenig Sonne, dazu höherer Verbrauch.",
    "heat": "Hitze & Dürre: 4 Wochen Kühlwassermangel und niedrige Flusspegel – Kraftwerke gedrosselt.",
})


WEATHER_TEXT = TDict({"normal": "normales Jahr", "hard": "schwieriges Jahr: kälter, weniger Wind",
                     "extreme": "extremer Winter: lange Kälte, kaum Wind"})


def weather_level(luck: dict) -> str:
    return luck.get("weather_level") or ("hard" if luck.get("harder_year") else "normal")


def describe_luck(luck: dict | None) -> str:
    if not luck:
        return ""
    parts = [tr("Wetterjahr {0} ({1})", luck['weather_year'], WEATHER_TEXT[weather_level(luck)]),
             tr("Nachfrage {0} %", ("+" if luck['demand_shock'] >= 0 else "−") + num(abs(luck['demand_shock']) * 100, 1))]
    ev = luck.get("event")
    if ev:
        week = ev["start"] // 168 + 1
        parts.append(tr("{0} (ab Woche {1})", EVENT_TEXT[ev['kind']], week))
        if ev["kind"] == "storm" and ev["factors"]:
            parts.append(tr("Betroffen: ") + ", ".join(LABELS.get(t, tr("PV") if t == "solar" else t) for t in ev["factors"]))
    else:
        parts.append(tr("Keine Katastrophe"))
    return " | ".join(parts)


# ----------------------------------------------------------------------------- costs & scoring
def system_cost(game: dict, tid: str, cap: dict, summary: dict, pending_investments: list) -> dict:
    """Annual system cost (EUR bn/yr) and EUR/MWh for the stage."""
    a = assumptions()
    team = game["teams"][tid]
    year = stage_years()[game["stage"]]
    tech = a["technologies"]
    capex = fom_new = 0.0
    for inv in team["investments"] + pending_investments:
        base = inv["eur"] if "eur" in inv else inv["mw"] * 1e3 * inv["eur_kw"]
        capex += base * annuity(inv["lifetime"])
        fom_new += base * inv["fom"] / 100
    exp = a["existing_params"]
    fb = a["fixed_blocks"]
    fom_exist = (cap["coal"] * exp["coal"]["fom_eur_kw"] + cap["gas"] * exp["gas"]["fom_eur_kw"]
                 + cap["biomass"] * exp["biomass"]["fom_eur_kw"] + cap["ror"] * exp["ror"]["fom_eur_kw"]) * 1e3
    for k in FIXED_KEYS:
        fom_exist += cap.get(k, 0.0) * 1e3 * fb[k]["fom_eur_kw"]
    # existing wind and PV that is still in operation: fixed O&M at today's cost level
    for key, t in [("onwind_old", "onwind"), ("offwind_old", "offwind"), ("solar_utility", "solar_utility"),
                   ("solar_rooftop", "solar_rooftop")]:
        fom_exist += old_fleet(team, key, year) * 1e3 * tech[t]["invest"][year] * tech[t]["fom"] / 100
    d = team["draft"]
    premium = d["borrow"] * game["cfg"]["token_value_bn"] * 1e9 * game["cfg"]["borrow_premium"] / 5
    # Damage from unserved energy (value of lost load) is reported, but it is NOT part of the
    # cost score: a supply gap already costs the reliability points, it should not cost the cost points as well.
    nse = summary["unserved_twh"] * 1e6 * a["voll_eur_per_mwh"]
    total = capex + fom_new + fom_exist + premium + summary["opex_bn"] * 1e9
    served = max(summary["served_twh"], 1e-6) * 1e6
    return {"capex_bn": capex / 1e9, "fom_bn": (fom_new + fom_exist) / 1e9, "opex_bn": summary["opex_bn"],
            "borrow_bn": premium / 1e9, "blackout_bn": nse / 1e9, "total_bn": total / 1e9,
            "eur_per_mwh": total / served}


def points_higher_better(value: float, thresholds: list) -> int:
    for i, th in enumerate(thresholds):
        if value >= th:
            return 5 - i
    return 0


def points_lower_better(value: float, thresholds: list) -> int:
    for i, th in enumerate(thresholds):
        if value <= th:
            return 5 - i
    return 0


def clean_points_detail(cfg: dict, s: int, summary: dict) -> dict:
    """CO2 category: share of CO2-free electricity (EEG logic) AND emissions in Mt (net-zero path, territorial).
    The worse of the two counts. Old configs without co2_mt_thresholds score the share only."""
    out = {"share": points_higher_better(summary["clean_share"], cfg["clean_thresholds"][s])}
    if cfg.get("co2_mt_thresholds"):
        out["co2"] = points_lower_better(summary["co2_mt"], cfg["co2_mt_thresholds"][s])
    return out


def score(game: dict, summary: dict, cost: dict) -> dict:
    cfg, s = game["cfg"], game["stage"]
    return {
        "reliability": points_lower_better(summary["lole_hours"], cfg["lole_thresholds"]),
        "clean": min(clean_points_detail(cfg, s, summary).values()),
        "cost": points_lower_better(cost["eur_per_mwh"], cfg["cost_thresholds"][s]),
    }


def stage_investments(game: dict, tid: str) -> list:
    team = game["teams"][tid]
    d = team["draft"]
    year = stage_years()[game["stage"]]
    tech = assumptions()["technologies"]
    out = []
    for t in NEW_TECHS:
        if d["build"][t] > 0:
            mw = d["build"][t] * mw_per_token(team, t, year, game["cfg"])
            out.append({"tech": t, "mw": mw, "eur_kw": invest_eur_kw(t, year) * team["learn"][t],
                        "stage": game["stage"], "lifetime": tech[t]["lifetime"], "fom": tech[t]["fom"]})
    if d.get("influence_bought"):
        cfg = game["cfg"]
        eur = d["influence_bought"] * cfg["influence_token_price"] * cfg["token_value_bn"] * 1e9
        out.append({"tech": "influence", "mw": 0.0, "eur_kw": 0.0, "eur": eur, "stage": game["stage"],
                    "lifetime": cfg.get("influence_lifetime", 20), "fom": 0.0})
    conv = effective_convert(game, tid)
    if conv > 0:
        out.append({"tech": "gas_new_h2", "mw": conv, "eur_kw": tech["gas_new"]["conversion_invest"],
                    "stage": game["stage"], "lifetime": tech["gas_new"]["lifetime"], "fom": 0.0})
    return out


def engine_args(game: dict, tid: str, luck: dict | None = None) -> dict:
    """Arguments for ptz.engine.model.simulate. luck=None -> Dispatch-Simulator (normal year, no shocks)."""
    a = assumptions()
    year = stage_years()[game["stage"]]
    args = {"cap": portfolio(game, tid), "year": year, "biomass_energy_share": biomass_share(game, tid)}
    if luck is None:
        args.update(weather_year=a["normal_weather_year"], demand_shock=0.0, event=None)
    else:
        args.update(weather_year=luck["weather_year"], demand_shock=luck["demand_shock"],
                    event=team_event(game, tid, luck["event"]))
    return args


def evaluate(game: dict, tid: str, summary: dict) -> dict:
    """Cost + points for a dispatch summary of the current draft (used by simulator and resolution)."""
    cap = portfolio(game, tid)
    cost = system_cost(game, tid, cap, summary, stage_investments(game, tid))
    pts = score(game, summary, cost)
    return {"cost": {k: round(v, 2) for k, v in cost.items()}, "points": pts,
            "clean_detail": clean_points_detail(game["cfg"], game["stage"], summary)}


# ----------------------------------------------------------------------------- stage resolution
def apply_stage_result(game: dict, tid: str, summary: dict) -> dict:
    """Book the resolved stage for a team: score, capacity update, learning, backlash."""
    cfg = game["cfg"]
    team = game["teams"][tid]
    d = team["draft"]
    s = game["stage"]
    ev = evaluate(game, tid, summary)
    cap = portfolio(game, tid)
    cap_store = portfolio(game, tid, aged=False)   # teams keep un-aged values; ageing is applied per stage year
    invs = stage_investments(game, tid)
    flex = flex_built(game, tid)          # before learning changes MW per token
    rng = _rng(game, "team", tid, s)

    # learning (team-specific)
    innov = influence_active(game, tid, "innovation")
    rate = cfg["learning_rate_per_token"] * (cfg["innovation_multiplier"] if innov else 1.0)
    learn_change = {}
    for t in NEW_TECHS:
        n = d["build"][t]
        if n > 0:
            r = max(0.0, rng.normal(rate, rate * cfg["learning_sd_factor"]))
            team["learn"][t] *= (1 - r) ** n
            learn_change[t] = round(1 - (1 - r) ** n, 4)

    # backlash (team-specific)
    backlash = []
    if cfg["backlash_enabled"]:
        social = influence_active(game, tid, "social")
        for t in NEW_TECHS:
            n = d["build"][t]
            if n > 0:
                p = cfg["backlash_rates_new"][cfg["backlash_risk"][t]] * (0.5 if social else 1.0)
                if rng.random() < 1 - (1 - p) ** n:
                    backlash.append(t)
        for k in EXISTING:
            if d["keep"][k] > 0:
                p = cfg["backlash_rates_existing"][cfg["backlash_risk"][k]] * (0.5 if social else 1.0)
                if rng.random() < p:
                    backlash.append(k)

    # influence bookkeeping
    for key in d["influence_new"]:
        team["influence_used"][key] = s        # grid_eu takes effect from the next stage (see trade_cap)
        team["influence_tokens"] -= 1
        if key in ("h2_demo", "h2_grid") and team["h2_unlocked_from"] is None:
            team["h2_unlocked_from"] = s + 1
        if key == "h2_demo" and team.get("electrolysis_from") is None:
            team["electrolysis_from"] = s + 1

    final = s == cfg["stages"] - 1
    penalty = cfg["final_backlash_penalty"] * len([t for t in backlash if t in NEW_TECHS]) if final else 0
    team["penalty"] += penalty
    co2 = summary["co2_mt"]
    rec = {
        "stage": s, "year": stage_years()[s], "summary": summary, "cost": ev["cost"], "points": ev["points"],
        "clean_detail": ev.get("clean_detail", {}),
        "stage_points": sum(ev["points"].values()), "penalty": penalty,
        "cap": {k: round(v, 1) for k, v in cap.items()}, "build": dict(d["build"]), "keep": dict(d["keep"]),
        "convert_mw": effective_convert(game, tid), "borrow": d["borrow"], "backlash": backlash, "learning": learn_change,
        "influence_new": list(d["influence_new"]), "co2_mt": co2, "co2_cum_gt": co2 * 5 / 1000,
    }
    team["history"].append(rec)
    team["investments"].extend(invs)
    cap["biomass_flex"] = flex   # keep owned flex MW even if biomass was reduced this stage
    cap_store["biomass_flex"] = cap["biomass_flex"]
    team["cap"] = cap_store
    team["blocked"] = backlash
    return rec


def total_points(team: dict) -> int:
    return sum(h["stage_points"] for h in team["history"]) - team["penalty"]


# Reference: Umweltbundesamt, CO2 per kWh of electricity consumed in Germany (domestic generation emissions /
# domestic consumption, imports without emissions - same definition as co2_intensity below). 2025: estimate.
CO2_INTENSITY_TODAY = (2025, 344)


def co2_intensity(summary: dict) -> float:
    """g CO2 per kWh consumed (= kg/MWh): emissions in Germany / served demand."""
    served = summary.get("served_twh") or 0.0
    return 1000.0 * summary.get("co2_mt", 0.0) / served if served > 0 else 0.0


def co2_intensity_with_imports(summary: dict) -> float:
    """Like co2_intensity, but including the CO2 emitted abroad for the imported electricity."""
    served = summary.get("served_twh") or 0.0
    co2 = summary.get("co2_mt", 0.0) + summary.get("import_co2_mt", 0.0)
    return 1000.0 * co2 / served if served > 0 else 0.0


def cumulative_co2_gt(team: dict) -> float:
    return sum(h["co2_cum_gt"] for h in team["history"])


def leaderboard(game: dict) -> list[dict]:
    rows = []
    for t in game["teams"].values():
        pts = {"reliability": 0, "clean": 0, "cost": 0}
        for h in t["history"]:
            for k in pts:
                pts[k] += h["points"][k]
        rows.append({"id": t["id"], "name": t["name"], "total": total_points(t), **pts, "penalty": t["penalty"],
                     "co2_gt": round(cumulative_co2_gt(t), 2)})
    return sorted(rows, key=lambda r: (-r["total"], r["co2_gt"]))


# ----------------------------------------------------------------------------- phase control
def start_stage(game: dict):
    game["phase"] = "build"
    mins = game["cfg"]["timer_minutes"][game["stage"]]
    game["timer_end"] = time.time() + mins * 60 if mins and mins > 0 else None
    for tid in game["teams"]:
        game["teams"][tid]["sims_extra"] = 0      # extra simulations from the host only count for one stage
        reset_draft(game, tid)


def close_stage(game: dict) -> dict:
    """Host closes the build phase: drafts count as submitted, shared luck is drawn."""
    game["phase"] = "resolving"
    game["timer_end"] = None
    for tid, t in game["teams"].items():
        t["submitted"] = True
        t["ready"] = False
        t["status"] = "wird berechnet"
        t["draft"]["convert_mw"] = effective_convert(game, tid)   # validate edge cases at close
        t["rev"] = t.get("rev", 0) + 1
    luck = draw_luck(game)
    game["luck"][game["stage"]] = luck
    return luck


def finish_resolution(game: dict):
    game["phase"] = "results"


def next_stage(game: dict):
    if game["stage"] >= game["cfg"]["stages"] - 1:
        game["phase"] = "finished"
        return
    game["stage"] += 1
    start_stage(game)


# ----------------------------------------------------------------------------- persistence
def save(game: dict, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    tmp = folder / f"{game['pin']}.json.tmp"
    tmp.write_text(json.dumps(game, ensure_ascii=False), encoding="utf-8")
    tmp.replace(folder / f"{game['pin']}.json")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------------- learning tip after a stage
CO2_SOURCES = TDict({"coal": "Kohle", "gas": "alte Gaskraftwerke", "gas_new": "neue Gasturbinen (Erdgas)",
               "other_fossil": "Öl & Sonstige", "reserve": "Reservekraftwerke", "waste": "Abfallverbrennung"})
CO2_ADVICE = TDict({"coal": "Kohle früher stilllegen.",
              "gas": "Alte Gaskraftwerke reduzieren und durch Wasserstoff-Turbinen, Speicher oder mehr Ökostrom "
                     "ersetzen – solange die Ampeln der gesicherten Leistung grün bleiben.",
              "gas_new": "Neue Gasturbinen auf Wasserstoff umrüsten (Einfluss-Karte nötig) – mit genug Wasserstoff, "
                         "sonst fehlen sie in der Dunkelflaute.",
              "other_fossil": "Mehr Ökostrom und Speicher, damit die teuren Altanlagen seltener laufen.",
              "reserve": "Mehr gesicherte Leistung, damit die Reserve seltener einspringen muss.",
              "waste": "Abfallverbrennung ist fest – an anderer Stelle CO₂ sparen."})


def _de(x: float, d: int = 0) -> str:
    return num(x, d)


def stage_tip(cfg: dict, s: int, summary: dict, ev: dict, cap: dict | None = None, sim: bool = False) -> list[str]:
    """One or two plain-language hints: what cost the most points this stage, and what changes next stage.
    cap: capacities of the stage (for the hydrogen check); sim: simulator forecast (present tense, no outlook)."""
    from ptz.engine.model import co2_intensity as tech_co2, demand_total_twh
    pts, det, cost = ev["points"], ev.get("clean_detail") or {}, ev["cost"]
    year = stage_years()[s]
    out = []
    worst = min(("reliability", "clean", "cost"), key=lambda k: pts[k])   # ties: reliability first
    if pts[worst] >= 5:
        out.append(tr("Alle drei Ziele erreicht – stark!"))
    elif worst == "reliability":
        txt = (tr("Am meisten Punkte kostete die Versorgung: {0} Stunden mit Lücke, größte {1} GW. ", summary['lole_hours'], _de(summary['max_unserved_gw'], 1)))
        turb = (cap or {}).get("gas_new_h2", 0.0)
        if turb > 1000 and h2_firm(cap) < turb - 1000:
            txt += (tr("Eure H₂-Turbinen ({0} GW) hatten nur für etwa {1} GW genug Wasserstoff – mehr Speicher oder Import, oder weniger umrüsten.", _de(turb / 1e3), _de(h2_firm(cap) / 1e3)))
        else:
            txt += tr("Mehr gesicherte Leistung einplanen – Gasturbinen, Biomasse-Flexibilisierung oder Speicher.")
        if not sim:
            txt += tr(" Der Simulator rechnet nur ein normales Jahr – plant Puffer für schwierige Jahre (Ampeln grün).")
        out.append(txt)
    elif worst == "clean":
        if "co2" in det and det["co2"] <= det["share"]:
            ci, g = tech_co2(year), summary.get("generation_twh", {})
            src = {k: g.get(k, 0.0) * ci[k] for k in CO2_SOURCES if k in ci}
            top = max(src, key=src.get)
            out.append(tr("Am meisten Punkte kostete der Klimaschutz – es zählte der Ausstoß: {0} Mt, für 5 Punkte höchstens {1} Mt. Größte Quelle: {2} ({3} Mt). {4}", _de(summary['co2_mt'], 1), _de(cfg['co2_mt_thresholds'][s][0]), CO2_SOURCES[top], _de(src[top], 1), CO2_ADVICE[top]))
        else:
            out.append(tr("Am meisten Punkte kostete der Klimaschutz – es zählte der Anteil: {0} % CO₂-frei, für 5 Punkte mindestens {1} %. Importe ({2} TWh) und fossiler Strom zählen nicht – mehr eigener Ökostrom hilft, Exporte zählen mit.", _de(summary['clean_share'], 1), _de(cfg['clean_thresholds'][s][0]), _de(summary.get('import_twh', 0))))
    else:
        blocks = {tr("Investitionen"): cost.get("capex_bn", 0), tr("fixe Betriebskosten"): cost.get("fom_bn", 0),
                  tr("Brennstoff, CO₂ & Importe"): cost.get("opex_bn", 0)}
        top = max(blocks, key=blocks.get)
        advice = {tr("Investitionen"): tr("Günstige Technologien (Wind an Land, Freiflächen-PV) liefern am meisten Strom je Token – teure Anlagen nur, wo sie gebraucht werden."),
                  tr("fixe Betriebskosten"): tr("Nicht mehr gebrauchte Altanlagen kosten Betriebskosten – stilllegen prüfen."),
                  tr("Brennstoff, CO₂ & Importe"): tr("Erdgas, Kohle, CO₂-Preis und Importe sind teuer – mehr Wind und Sonne senken sie.")}[top]
        out.append(tr("Am meisten Punkte kostete die Bezahlbarkeit: {0} €/MWh, für 5 Punkte höchstens {1} €. Größter Block: {2}. {3}", _de(cost['eur_per_mwh']), _de(cfg['cost_thresholds'][s][0]), top, advice))
    if sim:
        return [x.replace("kostete", "kostet").replace("es zählte", "es zählt") for x in out]
    if s + 1 < cfg["stages"]:
        y1 = stage_years()[s + 1]
        grow = 100 * (demand_total_twh(y1) / demand_total_twh(year) - 1)
        target = (tr(", CO₂-Ziel ≤ {0} Mt", _de(cfg['co2_mt_thresholds'][s + 1][0])) if cfg.get("co2_mt_thresholds")
                  else tr(", Ziel ≥ {0} % CO₂-frei", _de(cfg['clean_thresholds'][s + 1][0])))
        out.append(tr("Nächste Stufe ({0}–{1}): Verbrauch {2}{3} %{4}, Kohle höchstens {5} GW.", y1 - 4, y1, '+' if grow >= 0 else '', _de(grow), target, _de(assumptions()['existing_params']['coal_max_mw'][y1] / 1e3)))
    return out
