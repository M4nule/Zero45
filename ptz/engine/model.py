# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""PyPSA dispatch model for one stage year (single German node, 8760 h, chronological, cyclic storage,
import/export with a synthetic neighbour market).

Players decide capacities; this module only optimises the hourly operation (least operating cost)
and reports the metrics the game scores on.
"""
from __future__ import annotations

import ctypes
import gc
import logging
import os
import sys
import time
import warnings

os.environ.setdefault("TQDM_DISABLE", "1")
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa
import yaml

try:
    pypsa.options.api.legacy_string_dtype = True
except Exception:  # older/newer PyPSA without this option
    pass
logging.getLogger("pypsa").setLevel(logging.ERROR)
logging.getLogger("linopy").setLevel(logging.ERROR)

PKG = Path(__file__).resolve().parents[1]
PROCESSED = PKG / "data" / "processed"
ASSUMPTIONS = PKG / "config" / "assumptions.yaml"
HOURS = 8760
NSE_TOLERANCE_MW = 100.0  # an hour counts as "loss of load" above this unserved power
# Unserved energy costs VOLL x (1 - NSE_PEAK_DISCOUNT x demand/peak): a tiny preference for leaving gaps in the
# highest-demand hours. Without it, an LP with storage is indifferent how a shortfall is spread over hours, so
# the number of LOLE hours would not be unique. Costs in the game always use the flat VOLL.
NSE_PEAK_DISCOUNT = 0.01

# capacity keys used throughout the game (MW)
CAP_KEYS = ["onwind_old", "onwind", "offwind_old", "offwind", "solar_utility", "solar_rooftop", "ror",
            "biomass", "biomass_flex", "battery_old", "battery", "phs", "h2_package", "h2_storage", "h2_import",
            "gas", "gas_new", "gas_new_h2", "coal", "other_fossil", "reserve", "waste", "trade",
            "flex_shift", "flex_shed"]
FIXED_KEYS = ["battery_old", "phs", "other_fossil", "reserve", "waste"]
FOSSIL = ["gas", "gas_new", "coal", "other_fossil", "reserve"]          # plus the fossil share of "waste"
# which disaster factor applies to which unit
EVENT_KEY = {"onwind_old": "onwind", "offwind_old": "offwind", "solar_utility": "solar", "solar_rooftop": "solar",
             "battery_old": "battery", "other_fossil": "gas", "reserve": "gas"}


@lru_cache(maxsize=1)
def assumptions() -> dict:
    return yaml.safe_load(ASSUMPTIONS.read_text(encoding="utf-8"))


def fixed_capacities(year: int) -> dict[str, float]:
    """MW of the fixed blocks (not buildable, not retirable) in a stage year."""
    a = assumptions()
    fb = a["fixed_blocks"]
    return {"battery_old": float(fb["battery_old"]["mw"]) * a["fleet_remaining"]["battery_old"][year],
            "phs": float(fb["phs"]["mw"]), "other_fossil": float(fb["other_fossil"]["mw"][year]),
            "reserve": float(fb["reserve"]["mw"][year]), "waste": float(fb["waste"]["mw"])}


def demand_total_twh(year: int) -> float:
    """Load served by the model in the normal weather year: net demand plus grid losses and own consumption."""
    a = assumptions()
    return float(a["demand_twh"][year]) * float(a.get("demand_loss_factor", {}).get(year, 1.0))


def trade_capacity(year: int) -> float:
    return float(assumptions()["trade"]["capacity_mw"][year])


@lru_cache(maxsize=1)
def _data():
    return {
        "demand": pd.read_csv(PROCESSED / "demand_mw.csv.gz"),
        2030: pd.read_csv(PROCESSED / "pecd_2030.csv.gz"),
        2040: pd.read_csv(PROCESSED / "pecd_2040.csv.gz"),
        "ror": pd.read_csv(PROCESSED / "ror.csv.gz"),
        "nb2030": pd.read_csv(PROCESSED / "neighbours_2030.csv.gz"),
        "nb2040": pd.read_csv(PROCESSED / "neighbours_2040.csv.gz"),
    }


def profiles(year: int, weather_year: int) -> dict[str, np.ndarray]:
    a = assumptions()
    d = _data()
    pecd = d[2030] if year < 2040 else d[2040]
    der = a["wind_old_derating"]
    # demand: scale so that the NORMAL weather year matches demand_twh; other climate years keep their ratio
    dem = d["demand"]
    scale = demand_total_twh(year) * 1e6 / float(dem[f"{year}_{a['normal_weather_year']}"].sum())
    return {
        "demand": dem[f"{year}_{weather_year}"].to_numpy(dtype=float) * scale,
        "onwind": pecd[f"onwind_{weather_year}"].to_numpy(dtype=float),
        "offwind": pecd[f"offwind_{weather_year}"].to_numpy(dtype=float) * a.get("offwind_new_derating", 1.0),
        # existing fleet: PECD 2030 profile (also in later stages), derated
        "onwind_old": d[2030][f"onwind_{weather_year}"].to_numpy(dtype=float) * der["onwind"],
        "offwind_old": d[2030][f"offwind_{weather_year}"].to_numpy(dtype=float) * der["offwind"],
        "solar": pecd[f"solar_{weather_year}"].to_numpy(dtype=float),
        "solar_utility": np.clip(pecd[f"solar_{weather_year}"].to_numpy(dtype=float)
                                 * a.get("solar_utility_yield_factor", 1.0), 0.0, 1.0),
        "ror": d["ror"][f"ror_{weather_year}"].to_numpy(dtype=float),
    }


def trade_profiles(year: int, weather_year: int, capacity_mw: float) -> dict[str, np.ndarray]:
    """Hourly import availability (p.u.), import price (EUR/MWh) and CO2 (t/MWh), export availability and price.

    Based on the neighbours' hourly fossil need F(t) (see assumptions.yaml "trade")."""
    a = assumptions()
    t = a["trade"]
    F = _data()["nb2030" if year < 2040 else "nb2040"][f"F_{weather_year}"].to_numpy(dtype=float)
    fmax = max(F.max(), 1.0)
    p, ef = a["prices"], a["emission_factors"]
    fuel = p["natural_gas"][year] + p["co2"][year] * ef["natural_gas"]
    p_ccgt = fuel / t["ccgt_efficiency"] + 4.0
    p_ocgt = fuel / t["ocgt_efficiency"] + 6.0
    c_ccgt = ef["natural_gas"] / t["ccgt_efficiency"]
    c_ocgt = ef["natural_gas"] / t["ocgt_efficiency"]
    u = F / fmax
    price = np.interp(u, [0.0, 0.2, 0.8, 1.0], [t["surplus_price"], p_ccgt, p_ocgt, t["scarcity_price"]])
    co2 = np.interp(u, [0.0, 0.2, 0.8, 1.0], [0.0, c_ccgt, c_ocgt, c_ocgt])
    price[u <= 0] = t["surplus_price"]
    co2[u <= 0] = 0.0
    market = price.copy()
    price = market + t.get("import_fee", 0.0)
    cap = max(capacity_mw, 1.0)
    imp_avail = np.clip((t["margin"] * fmax - F) / cap, 0.0, 1.0)
    # neighbours take German power to replace their fossil plants (F > 0) and, in addition, a flexible amount that
    # they can always absorb (hydro saving in NO/SE/Alps, electrolysis, power-to-heat), paid at a low price
    absorb = float(t.get("absorb_mw", {}).get(year, 0.0)) if isinstance(t.get("absorb_mw"), dict) else 0.0
    exp_avail = np.clip((np.clip(F, 0.0, None) + absorb) / cap, 0.0, 1.0)
    exp_price = np.where(F > 0, np.maximum(market - t["export_discount"], 0.0), t.get("absorb_price", 0.0))
    return {"imp_avail": imp_avail, "imp_price": price, "imp_co2": co2, "exp_avail": exp_avail, "exp_price": exp_price}


def marginal_costs(year: int) -> dict[str, float]:
    """EUR/MWh_el operating cost (fuel + CO2 + VOM) per technology for a stage year."""
    a = assumptions()
    p, ef, ex, tech = a["prices"], a["emission_factors"], a["existing_params"], a["technologies"]
    fb = a["fixed_blocks"]
    co2 = p["co2"][year]
    ls = ex["coal"]["lignite_share"]
    coal_fuel = ls * p["lignite"][year] + (1 - ls) * p["hard_coal"][year]
    coal_ef = ls * ef["lignite"] + (1 - ls) * ef["hard_coal"]
    gas = p["natural_gas"][year]
    of = fb["other_fossil"]
    return {
        "coal": (coal_fuel + co2 * coal_ef) / ex["coal"]["efficiency"] + ex["coal"]["vom"],
        "gas": (gas + co2 * ef["natural_gas"]) / ex["gas"]["efficiency"] + ex["gas"]["vom"],
        "gas_new": (gas + co2 * ef["natural_gas"]) / tech["gas_new"]["efficiency"] + tech["gas_new"]["vom"],
        "other_fossil": (p["light_oil"][year] + co2 * ef["light_oil"]) / of["efficiency"] + of["vom"],
        "reserve": float(fb["reserve"]["marginal_cost"]),
        "biomass": ex["biomass"]["marginal_cost"],
        "ror": ex["ror"]["marginal_cost"],
        "onwind": tech["onwind"]["vom"], "offwind": tech["offwind"]["vom"],
        "solar_utility": 0.0, "solar_rooftop": 0.0,
        "gas_new_h2": tech["gas_new"]["vom"], "waste": 0.0,
    }


def co2_intensity(year: int) -> dict[str, float]:
    """t CO2 per MWh_el."""
    a = assumptions()
    ef, ex, fb = a["emission_factors"], a["existing_params"], a["fixed_blocks"]
    ls = ex["coal"]["lignite_share"]
    coal = (ls * ef["lignite"] + (1 - ls) * ef["hard_coal"]) / ex["coal"]["efficiency"]
    r = fb["reserve"]
    coal_frac = r["coal_mw"][year] / r["mw"][year] if r["mw"][year] else 0.0
    reserve = (coal_frac * ef["hard_coal"] / r["coal_efficiency"]
               + (1 - coal_frac) * ef["natural_gas"] / r["gas_efficiency"])
    return {
        "coal": coal,
        "gas": ef["natural_gas"] / ex["gas"]["efficiency"],
        "gas_new": ef["natural_gas"] / a["technologies"]["gas_new"]["efficiency"],
        "other_fossil": ef["light_oil"] / fb["other_fossil"]["efficiency"],
        "reserve": reserve,
        "waste": fb["waste"]["co2_t_per_mwh_el"],
    }


@lru_cache(maxsize=8)
def capacity_factors(year: int) -> dict[str, float]:
    """Average capacity factor (%) in the normal weather year: existing vs. new wind, PV."""
    pr = profiles(year, assumptions()["normal_weather_year"])
    out = {k: round(100 * float(pr[k].mean()), 1) for k in ["onwind_old", "onwind", "offwind_old", "offwind", "solar",
                                                              "solar_utility", "ror"]}
    out["solar_rooftop"] = out["solar"]
    return out


@lru_cache(maxsize=8)
def peak_demand_mw(year: int) -> float:
    """Peak demand (MW) in the normal weather year without shocks."""
    return float(profiles(year, assumptions()["normal_weather_year"])["demand"].max())


@dataclass
class Event:
    """A disaster / weather event: multiply availability of techs and demand within [start, start+hours)."""
    kind: str = "none"
    start: int = 0
    hours: int = 0
    factors: dict = field(default_factory=dict)   # tech -> availability multiplier
    demand_factor: float = 1.0


def simulate(cap: dict, year: int, weather_year: int, demand_shock: float = 0.0,
             event: Event | dict | None = None, biomass_energy_share: float = 1.0) -> dict:
    """Optimise hourly dispatch. cap: MW per CAP_KEYS. Returns summary metrics and hourly dispatch (GW)."""
    t0 = time.time()
    a = assumptions()
    tech = a["technologies"]
    fb = a["fixed_blocks"]
    if isinstance(event, dict):
        event = Event(**event)
    pr = profiles(year, weather_year)
    mc = marginal_costs(year)
    cap = {k: float(cap.get(k, 0.0)) for k in CAP_KEYS}

    window = np.zeros(HOURS, dtype=bool)
    if event and event.hours > 0:
        window[event.start:event.start + event.hours] = True

    def avail(key: str, base: np.ndarray | float = 1.0) -> np.ndarray:
        arr = np.broadcast_to(np.asarray(base, dtype=float), (HOURS,)).copy()
        fk = EVENT_KEY.get(key, key)
        if event and fk in event.factors:
            arr[window] *= event.factors[fk]
        return np.clip(arr, 0.0, 1.0)

    demand = pr["demand"] * (1.0 + demand_shock)
    if event and event.demand_factor != 1.0:
        demand = demand.copy()
        demand[window] *= event.demand_factor

    n = pypsa.Network()
    snaps = pd.RangeIndex(HOURS, name="snapshot")
    n.set_snapshots(snaps)
    n.add("Bus", "DE")
    n.add("Load", "demand", bus="DE", p_set=pd.Series(demand, index=snaps))
    voll = a["voll_eur_per_mwh"] * (1.0 - NSE_PEAK_DISCOUNT * demand / demand.max())
    n.add("Generator", "lost_load", bus="DE", p_nom=float(demand.max()) * 1.05,
          marginal_cost=pd.Series(voll, index=snaps))

    def gen(name, p_nom, pmax, marginal, **kw):
        if p_nom <= 0:
            return
        n.add("Generator", name, bus="DE", p_nom=p_nom, marginal_cost=marginal,
              p_max_pu=pd.Series(pmax, index=snaps), **kw)

    gen("onwind_old", cap["onwind_old"], avail("onwind_old", pr["onwind_old"]), mc["onwind"])
    gen("onwind", cap["onwind"], avail("onwind", pr["onwind"]), mc["onwind"])
    gen("offwind_old", cap["offwind_old"], avail("offwind_old", pr["offwind_old"]), mc["offwind"])
    gen("offwind", cap["offwind"], avail("offwind", pr["offwind"]), mc["offwind"])
    gen("solar_utility", cap["solar_utility"], avail("solar_utility", pr["solar_utility"]), mc["solar_utility"])
    gen("solar_rooftop", cap["solar_rooftop"], avail("solar_rooftop", pr["solar"]), mc["solar_rooftop"])
    gen("ror", cap["ror"], avail("ror", pr["ror"]), mc["ror"])
    gen("gas", cap["gas"], avail("gas"), mc["gas"])
    gen("gas_new", cap["gas_new"], avail("gas_new"), mc["gas_new"])
    gen("other_fossil", cap["other_fossil"], avail("other_fossil"), mc["other_fossil"])
    gen("reserve", cap["reserve"], avail("reserve"), mc["reserve"])
    if cap["waste"] > 0:   # waste must be burned: constant output
        wa = fb["waste"]["availability"]
        n.add("Generator", "waste", bus="DE", p_nom=cap["waste"], marginal_cost=mc["waste"], p_min_pu=wa, p_max_pu=wa)
    tp = None
    if cap["trade"] > 0:
        tp = trade_profiles(year, weather_year, cap["trade"])
        n.add("Generator", "import", bus="DE", p_nom=cap["trade"], p_max_pu=pd.Series(tp["imp_avail"], index=snaps),
              marginal_cost=pd.Series(tp["imp_price"], index=snaps))
        # export = negative generation; marginal cost x negative output = revenue
        n.add("Generator", "export", bus="DE", p_nom=cap["trade"], p_max_pu=0.0,
              p_min_pu=pd.Series(-tp["exp_avail"], index=snaps), marginal_cost=pd.Series(tp["exp_price"], index=snaps))
        # neighbour storage (hydro reservoirs abroad): takes German surplus (paid at the export price) and returns it
        # later (at the import price); shares the interconnector with normal imports/exports (extra_functionality)
        ns = a["trade"].get("neighbour_storage")
        if ns and ns["energy_mwh"] > 0:
            ne = ns["efficiency_one_way"]
            n.add("Bus", "NBS")
            n.add("Store", "nb_store", bus="NBS", e_nom=ns["energy_mwh"], e_cyclic=True)
            n.add("Link", "nb_charge", bus0="DE", bus1="NBS", p_nom=cap["trade"], efficiency=ne,
                  marginal_cost=pd.Series(-tp["exp_price"], index=snaps))
            n.add("Link", "nb_discharge", bus0="NBS", bus1="DE", p_nom=cap["trade"] / ne, efficiency=ne,
                  marginal_cost=pd.Series(tp["imp_price"] * ne, index=snaps))
    if cap["coal"] > 0:
        pmax = avail("coal")
        pmin = np.minimum(a["existing_params"]["coal"]["min_power"], pmax)
        ramp = a["existing_params"]["coal"]["ramp"]
        gen("coal", cap["coal"], pmax, mc["coal"], p_min_pu=pd.Series(pmin, index=snaps),
            ramp_limit_up=ramp, ramp_limit_down=ramp)
    bio_p = cap["biomass"] + cap["biomass_flex"]
    if bio_p > 0:
        energy = a["existing_params"]["biomass"]["energy_twh"] * 1e6 * biomass_energy_share
        gen("biomass", bio_p, avail("biomass"), mc["biomass"], e_sum_max=energy)

    # flexible consumers (influence card): load shifting = lossless short storage, load shedding = limited energy
    fl = a.get("flexibility", {})
    if cap["flex_shed"] > 0:
        n.add("Generator", "flex_shed", bus="DE", p_nom=cap["flex_shed"], marginal_cost=fl["shed_price"],
              e_sum_max=cap["flex_shed"] * fl["shed_max_hours"])

    def storage(name, p_nom, hours, eff, fkey, cost):
        if p_nom <= 0:
            return
        n.add("StorageUnit", name, bus="DE", p_nom=p_nom, max_hours=hours,
              efficiency_store=eff, efficiency_dispatch=eff, cyclic_state_of_charge=True,
              p_max_pu=pd.Series(avail(fkey), index=snaps), marginal_cost=cost)

    beff = tech["battery"]["efficiency_one_way"]
    storage("battery_old", cap["battery_old"], fb["battery_old"]["hours"], beff, "battery_old", 0.1)
    storage("battery", cap["battery"], tech["battery"]["hours"], beff, "battery", 0.1)
    storage("phs", cap["phs"], fb["phs"]["hours"], fb["phs"]["efficiency_one_way"], "phs", 0.2)
    storage("flex_shift", cap["flex_shift"], fl.get("shift_hours", 4), 1.0, "flex_shift", 0.05)

    h2 = tech["h2_package"]
    # hydrogen, three separate building blocks: electrolysis (h2_package, MW_el) -> salt cavern (h2_storage,
    # MWh_H2) -> converted new gas turbines (gas_new_h2, MW_el). Without a store, H2 would have to be burned in the
    # same hour it is produced (pointless losses, the optimiser will not do it).
    if cap["h2_package"] > 0 or cap.get("h2_storage", 0) > 0 or cap["gas_new_h2"] > 0:
        n.add("Bus", "H2")
        n.add("Store", "h2_store", bus="H2", e_nom=float(cap.get("h2_storage", 0.0)), e_cyclic=True)
        if cap.get("h2_import", 0) > 0:      # pipeline hydrogen (influence card), priced per MWh_H2
            n.add("Generator", "h2_import", bus="H2", p_nom=float(cap["h2_import"]),
                  marginal_cost=float(tech["h2_import"]["price"][year]))
        if cap["h2_package"] > 0:
            el_eff = h2["electrolyser_efficiency"][year]
            # Green hydrogen only: electrolysis may only use the German renewable surplus of the hour (wind, solar
            # and run-of-river available beyond demand) - not imports or fossil power (cf. the EU rules for
            # renewable hydrogen: renewable electricity in the same hour). Batteries cannot feed it either.
            vre_avail = sum(cap[k] * avail(k, pr[prof]) for k, prof in
                            [("onwind_old", "onwind_old"), ("onwind", "onwind"), ("offwind_old", "offwind_old"),
                             ("offwind", "offwind"), ("solar_utility", "solar_utility"), ("solar_rooftop", "solar"),
                             ("ror", "ror")])
            surplus = np.clip(vre_avail - demand, 0.0, None)
            el_max = np.minimum(avail("h2_package"), surplus / cap["h2_package"])
            n.add("Link", "electrolyser", bus0="DE", bus1="H2", p_nom=cap["h2_package"], efficiency=el_eff,
                  p_max_pu=pd.Series(el_max, index=snaps))
        if cap["gas_new_h2"] > 0:
            e = tech["gas_new"]["efficiency"]
            n.add("Link", "gas_new_h2", bus0="H2", bus1="DE", p_nom=cap["gas_new_h2"] / e, efficiency=e,
                  marginal_cost=mc["gas_new_h2"] * e, p_max_pu=pd.Series(avail("gas_new"), index=snaps))

    def extra_constraints(n, sns):
        """(1) Normal trade and neighbour storage share the interconnector capacity.
        (2) Load shifting (EVs, heat pumps) balances within each day: the shifted energy is back to zero at the
            end of every day, so consumption moves by hours (e.g. evening -> midday), never across days."""
        m = n.model
        if "nb_charge" in n.links.index:
            gp, lp = m["Generator-p"], m["Link-p"]
            ne = n.links.at["nb_discharge", "efficiency"]
            m.add_constraints(gp.sel(name="import") + ne * lp.sel(name="nb_discharge") <= cap["trade"],
                              name="trade_in")
            m.add_constraints(-gp.sel(name="export") + lp.sel(name="nb_charge") <= cap["trade"], name="trade_out")
        if "flex_shift" in n.storage_units.index:
            soc = m["StorageUnit-state_of_charge"].sel(name="flex_shift")
            day_end = [h for h in range(23, HOURS, 24)]
            m.add_constraints(soc.sel(snapshot=day_end) == 0, name="flex_shift_daily")

    # io_api="direct": hand the model to HiGHS in memory instead of writing an LP file - same results,
    # about a quarter less peak memory and faster (measured 1.47 -> 1.12 GB, 13.7 -> 10.2 s for a 2045 case)
    with _quiet_stdout():
        status, cond = n.optimize(solver_name="highs", include_objective_constant=False, io_api="direct",
                                  extra_functionality=extra_constraints,
                                  solver_options={"log_to_console": False, "output_flag": False})
    if status != "ok":
        raise RuntimeError(f"Optimisation failed: {status} / {cond}")
    t_solve = time.time() - t0
    res = _results(n, cap, year, demand, pr, mc, t_solve, tp)
    del n
    release_memory()
    return res


class _quiet_stdout:
    """HiGHS prints its banner directly to file descriptor 1 (before options apply): silence it during the solve."""
    def __enter__(self):
        try:
            sys.stdout.flush()
            self.saved = os.dup(1)
            self.null = os.open(os.devnull, os.O_WRONLY)
            os.dup2(self.null, 1)
        except Exception:  # no real stdout (e.g. some Windows services): just run
            self.saved = None
        return self

    def __exit__(self, *exc):
        if self.saved is not None:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            os.dup2(self.saved, 1)
            os.close(self.saved)
            os.close(self.null)
        return False


def release_memory():
    """PyPSA/linopy networks contain reference cycles: without an explicit collection, several ~1 GB models can pile
    up in a long-running worker before Python's GC runs. On Linux also hand freed memory back to the OS."""
    gc.collect()
    if sys.platform.startswith("linux"):
        try:
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        except OSError:
            pass


VRE = ["onwind_old", "onwind", "offwind_old", "offwind", "solar_utility", "solar_rooftop", "ror"]


def _results(n: pypsa.Network, cap: dict, year: int, demand: np.ndarray, pr: dict, mc: dict, t_solve: float,
             tp: dict | None = None) -> dict:
    g = n.generators_t.p
    col = lambda df, k: df[k].to_numpy() if k in df.columns else np.zeros(HOURS)
    raw = {k: col(g, k) for k in VRE + ["biomass", "gas", "gas_new", "coal", "other_fossil", "reserve", "waste",
                                        "import", "export", "lost_load", "flex_shed"]}
    lt = n.links_t.p1 if len(n.links) else pd.DataFrame(index=n.snapshots)
    l0 = n.links_t.p0 if len(n.links) else pd.DataFrame(index=n.snapshots)
    nb_in = -col(lt, "nb_discharge")          # MW arriving in DE from the neighbour storage
    nb_out = col(l0, "nb_charge")             # MW leaving DE into the neighbour storage
    disp = pd.DataFrame(index=range(HOURS))
    disp["onwind"] = raw["onwind_old"] + raw["onwind"]
    disp["offwind"] = raw["offwind_old"] + raw["offwind"]
    for k in ["solar_utility", "solar_rooftop", "ror", "biomass", "gas", "gas_new", "coal", "other_fossil", "reserve",
              "waste"]:
        disp[k] = raw[k]
    disp["import"] = np.clip(raw["import"], 0, None) + np.clip(nb_in, 0, None)
    disp["export"] = np.clip(raw["export"], None, 0) - np.clip(nb_out, 0, None)     # negative
    disp["h2_turbine"] = np.zeros(HOURS)   # kept for compatibility (H2 power now only via gas_new_h2)
    disp["gas_new_h2"] = -col(lt, "gas_new_h2")
    su = n.storage_units_t.p
    bat = col(su, "battery") + col(su, "battery_old")
    phs = col(su, "phs")
    disp["phs_discharge"] = np.clip(phs, 0, None)
    disp["battery_discharge"] = np.clip(bat, 0, None)
    disp["battery_charge"] = np.clip(bat, None, 0)
    disp["phs_charge"] = np.clip(phs, None, 0)
    fs = col(su, "flex_shift")
    disp["flex_shed"] = np.clip(raw["flex_shed"], 0, None)
    disp["flex_shift_discharge"] = np.clip(fs, 0, None)
    disp["flex_shift_charge"] = np.clip(fs, None, 0)
    disp["electrolyser"] = -col(l0, "electrolyser")
    disp["lost_load"] = np.clip(raw["lost_load"], 0, None)   # solver noise can be slightly negative
    disp["demand"] = demand
    gi = n.generators.index
    vre_avail = np.zeros(HOURS)
    for k in VRE:
        if k in gi:
            vre_avail += n.generators_t.p_max_pu[k].to_numpy() * n.generators.p_nom[k]
    vre_gen = sum(raw[k] for k in VRE)
    disp["curtailment"] = np.clip(vre_avail - vre_gen, 0, None)
    soc = n.storage_units_t.state_of_charge
    disp["battery_soc"] = col(soc, "battery") + col(soc, "battery_old")
    disp["phs_soc"] = col(soc, "phs")
    disp["h2_soc"] = col(n.stores_t.e, "h2_store") if len(n.stores) else 0.0

    twh = lambda x: float(np.sum(x)) / 1e6
    nse = disp["lost_load"].to_numpy()
    served = twh(demand) - twh(nse) - twh(disp["flex_shed"])     # load shedding lowers consumption
    a = assumptions()
    waste_ren = a["fixed_blocks"]["waste"]["renewable_share"]
    fossil = sum(twh(disp[k]) for k in FOSSIL) + (1 - waste_ren) * twh(disp["waste"])
    ci = co2_intensity(year)
    co2_mt = sum(twh(disp[k]) * ci[k] for k in FOSSIL) + twh(disp["waste"]) * ci["waste"]
    opex = {k: twh(disp[k]) * 1e6 * mc[k] / 1e9 for k in ["coal", "gas", "gas_new", "other_fossil", "reserve",
                                                         "biomass", "ror", "onwind", "offwind", "gas_new_h2"]}
    opex["flex_shed"] = twh(disp["flex_shed"]) * a.get("flexibility", {}).get("shed_price", 0.0) / 1e3
    h2_imp_twh = twh(col(n.generators_t.p, "h2_import"))
    opex["h2_import"] = h2_imp_twh * a["technologies"]["h2_import"]["price"][year] / 1e3
    imp_twh, exp_twh, imp_co2 = twh(disp["import"]), -twh(disp["export"]), 0.0
    if tp is not None:
        imp = disp["import"].to_numpy()
        opex["import"] = float(np.sum(imp * tp["imp_price"])) / 1e9
        opex["export"] = -float(np.sum(-disp["export"].to_numpy() * tp["exp_price"])) / 1e9
        # CO2 of imports: only from the neighbours' plants, not from German power returned by their storage
        imp_co2 = float(np.sum(np.clip(raw["import"], 0, None) * tp["imp_co2"])) / 1e6
    gen_twh = {k: round(twh(disp[k]), 2) for k in ["onwind", "offwind", "solar_utility", "solar_rooftop", "ror",
                                                    "biomass", "waste", "gas", "gas_new", "coal", "other_fossil",
                                                    "reserve", "gas_new_h2", "battery_discharge", "phs_discharge",
                                                    "import", "flex_shed", "flex_shift_discharge"]}
    gen_twh["export"] = round(-exp_twh, 2)
    gen_twh["onwind_old"] = round(twh(raw["onwind_old"]), 2)
    gen_twh["offwind_old"] = round(twh(raw["offwind_old"]), 2)
    summary = {
        "year": year,
        "demand_twh": round(twh(demand), 2),
        "served_twh": round(served, 2),
        "unserved_twh": round(twh(nse), 3),
        "lole_hours": int(np.sum(nse > NSE_TOLERANCE_MW)),
        "max_unserved_gw": round(float(nse.max()) / 1e3, 2),
        "peak_demand_gw": round(float(demand.max()) / 1e3, 1),
        # official logic (EEG statistic): CO2-free generation incl. exports relative to consumption; imports are not
        # counted as renewable. = (consumption + exports - imports - fossil) / consumption, at most 100 %.
        "clean_share": round(min(100.0, max(0.0, 100.0 * (served + exp_twh - imp_twh - fossil) / served)), 2)
        if served > 0 else 0.0,
        "import_twh": round(imp_twh, 2),
        "export_twh": round(exp_twh, 2),
        "import_co2_mt": round(imp_co2, 2),
        "fossil_twh": round(fossil, 2),
        "co2_mt": round(co2_mt, 2),
        "opex_bn": round(sum(opex.values()), 3),
        "opex_detail_bn": {k: round(v, 3) for k, v in opex.items()},
        "generation_twh": gen_twh,
        "curtailment_twh": round(twh(disp["curtailment"]), 2),
        "electrolyser_twh": round(-twh(disp["electrolyser"]), 2),   # dispatch column is negative (consumption)
        "h2_import_twh": round(h2_imp_twh, 2),                      # MWh_H2 bought through the pipeline
        "battery_charge_twh": round(-twh(disp["battery_charge"]), 2),
        "phs_charge_twh": round(-twh(disp["phs_charge"]), 2),
        "nb_storage_in_twh": round(twh(np.clip(nb_out, 0, None)), 2),
        "nb_storage_out_twh": round(twh(np.clip(nb_in, 0, None)), 2),
        "solve_seconds": round(t_solve, 1),
    }
    return {"summary": summary, "dispatch": (disp / 1e3).astype("float32")}  # GW


if __name__ == "__main__":
    import json
    from ptz.game.core import start_capacities
    cap = start_capacities()
    cap.update(fixed_capacities(2030))
    r = simulate(cap, 2030, 2008)
    print(json.dumps(r["summary"], indent=1))
