# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the processed German input data for the game from the raw TYNDP 2024 / PECD / BNetzA files.

Usage (from the project folder):
    uv run python -m ptz.data.build_inputs            # reads raw/, writes ptz/data/processed/

All outputs are hourly (8760 h, calendar year without Feb 29) and per weather (climate) year.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "raw"
OUT = Path(__file__).resolve().parent / "processed"
ASSUMPTIONS = Path(__file__).resolve().parents[1] / "config" / "assumptions.yaml"

CLIMATE_YEARS = [1995, 2008, 2009]
HOURS = 8760


def log(*a):
    print("[build_inputs]", *a, flush=True)


# ----------------------------------------------------------------------------- PECD
def load_pecd() -> dict[int, pd.DataFrame]:
    """Capacity factors for DE00 per PECD target year (2030, 2040) -> columns '<tech>_<cy>'."""
    z = zipfile.ZipFile(RAW / "PECD_3.1+pre-built.0.1.zip")
    techs = {"onwind": "Wind_Onshore", "offwind": "Wind_Offshore", "solar": "LFSolarPV"}
    out = {}
    for ty in (2030, 2040):
        cols = {}
        for key, name in techs.items():
            f = f"{ty}/PECD_{name}_{ty}_DE00_edition 2023.2.csv"
            df = pd.read_csv(io.BytesIO(z.read(f)))
            assert len(df) == HOURS, (f, len(df))
            for cy in CLIMATE_YEARS:
                cols[f"{key}_{cy}"] = df[str(cy)].astype(float).clip(0, 1).values
        out[ty] = pd.DataFrame(cols)
        log("PECD", ty, {k: round(v.mean(), 3) for k, v in out[ty].items()})
    return out


# ----------------------------------------------------------------------------- demand
def _read_sheet(zf: zipfile.ZipFile, member: str, sheet: str) -> list[tuple]:
    wb = openpyxl.load_workbook(io.BytesIO(zf.read(member)), read_only=True, data_only=True)
    rows = list(wb[sheet].iter_rows(values_only=True))
    wb.close()
    return rows


def _demand_from_rows(rows: list[tuple]) -> pd.DataFrame:
    """Find the header row containing the climate years and return hourly MW per climate year."""
    hdr_idx = next(i for i, r in enumerate(rows) if r and r[0] == "Date")
    hdr = rows[hdr_idx]
    data = [r for r in rows[hdr_idx + 1:] if r and r[0] is not None]
    cols = {}
    for cy in CLIMATE_YEARS:
        j = list(hdr).index(cy)
        vals = np.array([r[j] if r[j] is not None else np.nan for r in data], dtype=float)
        cols[cy] = vals[:HOURS]
    df = pd.DataFrame(cols)
    assert len(df) == HOURS and not df.isna().any().any(), "incomplete demand profile"
    return df


def load_demand() -> dict[str, pd.DataFrame]:
    """Hourly German electricity demand shapes (MW) from TYNDP 2024 per scenario/year."""
    z = zipfile.ZipFile(RAW / "Demand-Profiles.zip")
    out = {}
    for y in (2030, 2040):
        member = f"Demand Profiles/NT/Electricity demand profiles/{y}_National Trends.xlsx"
        log("reading", member, "(large file, takes a minute)")
        out[f"NT{y}"] = _demand_from_rows(_read_sheet(z, member, "DE00"))
    # Distributed Energy 2050 = market + prosumer demand
    tot = None
    for part in ("MARKET", "PROSUMER"):
        member = f"Demand Profiles/DE/2050/ELECTRICITY_{part} DE 2050.xlsx"
        log("reading", member)
        d = _demand_from_rows(_read_sheet(z, member, "DE00"))
        tot = d if tot is None else tot + d
    out["DE2050"] = tot
    for k, v in out.items():
        log("demand", k, {cy: f"{v[cy].sum()/1e6:.0f} TWh / peak {v[cy].max()/1e3:.0f} GW" for cy in CLIMATE_YEARS})
    return out


# ----------------------------------------------------------------------------- hydro
def load_ror() -> tuple[pd.DataFrame, float]:
    """Run-of-river availability (p.u.) per climate year from daily PEMMDB inflows; capacity in MW."""
    z = zipfile.ZipFile(RAW / "Hydro-Inflows.zip")
    member = "Hydro Inflows/2030/PEMMDB_DE00_Hydro_Inflows_2030.xlsx"
    wb = openpyxl.load_workbook(io.BytesIO(z.read(member)), read_only=True, data_only=True)
    info = {r[0]: r[1] for r in wb["MarketNodeInfo"].iter_rows(values_only=True) if r and r[0]}
    cap_mw = float(info["Run of River - MW"])
    rows = list(wb["Run of River - Year Dependent"].iter_rows(values_only=True))
    wb.close()
    hdr = rows[1]
    data = [r for r in rows[2:] if r and r[1] == "INFLOW"]
    cols = {}
    for cy in CLIMATE_YEARS:
        j = list(hdr).index(cy)
        daily = np.array([r[j] for r in data[:365]], dtype=float)  # GWh/day
        pu = daily * 1000 / 24 / cap_mw  # constant within the day
        cols[cy] = np.clip(np.repeat(pu, 24), 0, 1)
        log("ROR", cy, f"{daily.sum()/1000:.1f} TWh/yr at {cap_mw:.0f} MW")
    return pd.DataFrame(cols), cap_mw


# ----------------------------------------------------------------------------- prices
def load_prices() -> dict:
    z = zipfile.ZipFile(RAW / "Prices.zip")
    wb = openpyxl.load_workbook(io.BytesIO(z.read("Prices/2023 06 22 TYNDP 2024 Commodity prices Final.xlsx")),
                                read_only=True, data_only=True)
    rows = list(wb["Matrix 2024"].iter_rows(values_only=True))
    wb.close()
    want = {"Hard coal": "hard_coal", "Natural Gas": "natural_gas", "CO2 price": "co2",
            "Lignite G2 (SK - DE - RS - PL - ME - UKNI - BA - IE)": "lignite"}
    res = {}
    for r in rows:
        if r and r[1] in want:
            res[want[r[1]]] = {2030: float(r[3]), 2040: float(r[4]), 2050: float(r[5])}
    log("prices (2021 EUR, fuels EUR/GJ, CO2 EUR/t)", res)
    return res


# ----------------------------------------------------------------------------- capacities
def load_kraftwerksliste() -> dict:
    wb = openpyxl.load_workbook(RAW / "Kraftwerksliste.xlsx", read_only=True, data_only=True)
    rows = list(wb["Auswertung Kraftwerksstatus"].iter_rows(min_row=7, max_row=40, max_col=3, values_only=True))
    wb.close()
    cap = {r[1]: float(r[2]) for r in rows if r[1] and isinstance(r[2], (int, float))}
    log("Kraftwerksliste in operation (MW):", {k: round(v) for k, v in cap.items()})
    return cap


# ----------------------------------------------------------------------------- weather check
def weather_check(pecd40: pd.DataFrame, demand40: pd.DataFrame, ror: pd.DataFrame, scale_twh: float) -> pd.DataFrame:
    """Compare climate years: residual load stats for a reference 2040 renewable fleet."""
    ref = {"onwind": 140e3, "offwind": 40e3, "solar": 250e3}  # MW reference fleet
    rows = []
    for cy in CLIMATE_YEARS:
        d = demand40[cy] / demand40[cy].sum() * scale_twh * 1e6
        vre = sum(pecd40[f"{k}_{cy}"] * v for k, v in ref.items()) + ror[cy] * 4000
        resid = d - vre
        win = np.r_[0:59 * 24, 304 * 24:HOURS]  # Nov-Feb
        deficit = resid.clip(lower=0)
        two_weeks = deficit.rolling(336).sum().max() / 1e6
        wind_cf = (pecd40[f"onwind_{cy}"] * 140 + pecd40[f"offwind_{cy}"] * 40) / 180
        rows.append({
            "climate_year": cy,
            "winter_mean_residual_GW": resid.iloc[win].mean() / 1e3,
            "annual_deficit_TWh": deficit.sum() / 1e6,
            "max_2week_deficit_TWh": two_weeks,
            "peak_residual_GW": resid.max() / 1e3,
            "min_7day_wind_cf": wind_cf.rolling(168).mean().min(),
            "onwind_cf": pecd40[f"onwind_{cy}"].mean(), "offwind_cf": pecd40[f"offwind_{cy}"].mean(),
            "solar_cf": pecd40[f"solar_{cy}"].mean(), "demand_peak_GW": d.max() / 1e3,
        })
    return pd.DataFrame(rows).set_index("climate_year").round(3)


# ----------------------------------------------------------------------------- neighbours (imports/exports)
NEIGHBOURS = ["AT00", "BE00", "CH00", "CZ00", "DKE1", "DKW1", "FR00", "LUG1", "NL00", "NOS0", "PL00", "SE04"]
# TYNDP 2024 Scenario Report data, fig. 26 (EU27 power generation, National Trends+, TWh): shares of total generation
EU_MIX = {2030: {"onwind": 874.4, "offwind": 411.5, "solar": 772.0, "flat": 568 + 314.9 + 185.1 + 29},
          2040: {"onwind": 1347.1, "offwind": 1113.4, "solar": 1344.5, "flat": 522 + 314.7 + 147 + 15}}
EU_TOTAL = {2030: 3584.0, 2040: 5183.0}


def load_neighbours() -> dict[int, pd.DataFrame]:
    """Hourly 'fossil need' of the neighbouring countries (MW) per PECD target year and climate year.

    APPROXIMATION (no per-country capacities in the raw data): the neighbours' demand (TYNDP NT profiles, sum of
    the 12 market nodes around DE) is covered by wind/solar with the EU27 NT+ energy shares (weather from the
    neighbours' own PECD profiles), a flat block for nuclear + hydro + other RES + biofuels, and fossil plants for the
    rest. F(t) = max(0, demand - wind/solar - flat block); F < 0 means surplus (exports to DE are cheap and clean).
    """
    zp = zipfile.ZipFile(RAW / "PECD_3.1+pre-built.0.1.zip")
    zd = zipfile.ZipFile(RAW / "Demand-Profiles.zip")
    names = {"onwind": "Wind_Onshore", "offwind": "Wind_Offshore", "solar": "LFSolarPV"}
    out = {}
    for ty in (2030, 2040):
        member = f"Demand Profiles/NT/Electricity demand profiles/{ty}_National Trends.xlsx"
        log("neighbours: reading", member, "(takes a few minutes)")
        wb = openpyxl.load_workbook(io.BytesIO(zd.read(member)), read_only=True, data_only=True)
        dem = {}
        for node in NEIGHBOURS:
            if node not in wb.sheetnames:
                log("  no demand sheet for", node); continue
            dem[node] = _demand_from_rows(list(wb[node].iter_rows(values_only=True)))
        wb.close()
        cf = {k: {} for k in names}
        for k, nm in names.items():
            for node in dem:
                f = f"{ty}/PECD_{nm}_{ty}_{node}_edition 2023.2.csv"
                if f in zp.namelist():
                    cf[k][node] = pd.read_csv(io.BytesIO(zp.read(f)))
        mix = EU_MIX[ty]
        cols = {}
        for cy in CLIMATE_YEARS:
            d = sum(dem[n][cy].to_numpy() for n in dem)
            e = d.sum()
            res = d.copy()
            for k in names:
                nodes = [n for n in dem if n in cf[k]]
                w = np.array([dem[n][cy].sum() for n in nodes]); w = w / w.sum()
                prof = sum(wi * cf[k][n][str(cy)].astype(float).clip(0, 1).to_numpy()[:HOURS] for wi, n in zip(w, nodes))
                res -= e * mix[k] / EU_TOTAL[ty] * prof / prof.sum()
            res -= e * mix["flat"] / EU_TOTAL[ty] / HOURS
            cols[f"F_{cy}"] = res          # MW; negative = surplus
            cols[f"D_{cy}"] = d
            log("neighbours", ty, cy, f"demand {e / 1e6:.0f} TWh, fossil need {np.clip(res, 0, None).sum() / 1e6:.0f} TWh, "
                f"surplus hours {(res < 0).sum()}, max need {res.max() / 1e3:.0f} GW")
        out[ty] = pd.DataFrame(cols)
    return out


# ----------------------------------------------------------------------------- main
def main():
    a = yaml.safe_load(ASSUMPTIONS.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    if "--neighbours" in sys.argv:          # only the import/export data (slow step)
        OUT.mkdir(parents=True, exist_ok=True)
        for ty, df in load_neighbours().items():
            df.round(0).to_csv(OUT / f"neighbours_{ty}.csv.gz", index=False)
        log("done ->", OUT)
        return 0
    pecd = load_pecd()
    ror, ror_cap = load_ror()
    dem = load_demand()
    prices = load_prices()
    kwl = load_kraftwerksliste()

    # demand per stage year: shapes blended, scaled so that the NORMAL weather year matches the middle-path
    # total; the other climate years keep their weather-driven ratio to it (cold years slightly higher)
    ny = a["normal_weather_year"]
    norm = {k: v / v[ny].sum() for k, v in dem.items()}
    shapes = {2030: norm["NT2030"], 2035: 0.5 * (norm["NT2030"] + norm["NT2040"]),
              2040: norm["NT2040"], 2045: 0.5 * (norm["NT2040"] + norm["DE2050"])}
    demand = {}
    for y, twh in a["demand_twh"].items():
        y = int(y)
        for cy in CLIMATE_YEARS:
            demand[f"{y}_{cy}"] = shapes[y][cy] * twh * 1e6  # MW
    pd.DataFrame(demand).round(1).to_csv(OUT / "demand_mw.csv.gz", index=False)

    for ty, df in pecd.items():
        df.round(4).to_csv(OUT / f"pecd_{ty}.csv.gz", index=False)
    ror.columns = [f"ror_{c}" for c in ror.columns]
    ror.round(4).to_csv(OUT / "ror.csv.gz", index=False)

    for ty, df in load_neighbours().items():
        df.round(0).to_csv(OUT / f"neighbours_{ty}.csv.gz", index=False)
    wc = weather_check(pecd[2040], dem["NT2040"], ror.rename(columns=lambda c: int(c[4:])), a["demand_twh"][2040])
    log("weather year comparison (2040 reference fleet):\n" + wc.to_string())
    wc.to_csv(OUT / "weather_check.csv")

    meta = {"ror_capacity_mw": ror_cap, "prices_2021eur": prices, "kraftwerksliste_mw": kwl,
            "demand_twh_raw": {k: {str(cy): round(v[cy].sum() / 1e6, 1) for cy in CLIMATE_YEARS} for k, v in dem.items()},
            "demand_peak_gw": {k: round(v.max() / 1e3, 1) for k, v in demand.items()}}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    log("done ->", OUT)


if __name__ == "__main__":
    sys.exit(main())
