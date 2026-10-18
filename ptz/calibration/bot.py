# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Adaptive bot for calibration: tries a few portfolio templates per stage in the simulator, keeps the best.

Usage:  uv run python -m ptz.calibration.bot --seeds 1 2 3
"""
from __future__ import annotations

import argparse
import copy
import json

from ptz.game import core, runner

TEMPLATES = {
    "wind":     {"onwind": .40, "offwind": .15, "solar_utility": .20, "battery": .15, "gas_new": .10},
    "storage":  {"onwind": .30, "offwind": .10, "solar_utility": .20, "battery": .25, "gas_new": .15},
    "re_heavy": {"onwind": .45, "offwind": .15, "solar_utility": .25, "battery": .15},
    "solar":    {"onwind": .25, "solar_utility": .35, "solar_rooftop": .10, "battery": .25, "gas_new": .05},
    # hydrogen templates (only once hydrogen is unlocked); tried with/without conversion and old-gas retirement
    "h2imp":    {"onwind": .35, "offwind": .10, "solar_utility": .20, "battery": .15, "h2_storage": .05,
                 "gas_new": .15},
    "h2mix":    {"onwind": .30, "offwind": .05, "solar_utility": .20, "battery": .10, "h2_package": .10,
                 "h2_storage": .10, "gas_new": .15},
}
H2_TEMPLATES = ("h2imp", "h2mix")


def allocate(game, tid, shares: dict):
    n = core.tokens_left(game, tid)
    techs = [t for t in shares if core.can_build(game, tid, t)[0]]
    if not techs:
        return
    tot = sum(shares[t] for t in techs)
    alloc = {t: int(n * shares[t] / tot) for t in techs}
    rest = n - sum(alloc.values())
    for t in sorted(techs, key=lambda x: -shares[x])[:rest]:
        alloc[t] += 1
    for t, k in alloc.items():
        for _ in range(k):
            if core.change_build(game, tid, t, 1):
                break


def value(ev, summary):
    return (sum(ev["points"].values()) + 0.05 * summary["clean_share"] - 0.002 * summary["lole_hours"]
            - 0.005 * summary["co2_mt"])


def play(seed: int, borrow: int = 0, verbose=True, influence=("h2_demo", "resilience"), tokens=None) -> dict:
    cfg = copy.deepcopy(core.default_config())
    cfg["seed"] = seed
    if tokens:
        cfg["build_tokens"] = list(tokens)
    g = core.new_game(cfg, mode="solo")
    tid, _ = core.add_team(g, f"bot{seed}")
    core.start_stage(g)
    log = []
    for s in range(cfg["stages"]):
        if s == 0:
            for key in influence:
                core.toggle_influence(g, tid, key)
        core.set_keep(g, tid, "coal", 0)
        best = None
        h2 = core.h2_available(g, tid)
        imp = core.h2_import_cap(g, tid) > 0
        for name, sh in TEMPLATES.items():
            if name in H2_TEMPLATES and not h2:
                continue
            for conv in ([0.0, 1.0] if name in H2_TEMPLATES else [0.0]):
                for keep_gas in ([1.0, 0.0] if (name in H2_TEMPLATES and conv and imp) else [1.0]):
                    trial = copy.deepcopy(g)
                    d = trial["teams"][tid]["draft"]
                    d["build"] = {t: 0 for t in core.NEW_TECHS}
                    core.set_borrow(trial, tid, borrow)
                    allocate(trial, tid, sh)
                    if conv:
                        core.set_convert(trial, tid, core.max_convert(trial, tid) * conv)
                    if keep_gas < 1:
                        core.set_keep(trial, tid, "gas", trial["teams"][tid]["cap"]["gas"] * keep_gas)
                    summary, _ = runner.run_engine(core.engine_args(trial, tid, None))
                    ev = core.evaluate(trial, tid, summary)
                    v = value(ev, summary)
                    if best is None or v > best[0]:
                        best = (v, f"{name}{'+conv' if conv else ''}{'-gas' if keep_gas < 1 else ''}", conv,
                                copy.deepcopy(trial["teams"][tid]["draft"]), ev["points"])
        g["teams"][tid]["draft"] = best[3]
        runner.resolve_stage_sequential(g)
        h = g["teams"][tid]["history"][-1]
        line = (f"seed {seed} S{s + 1}: {best[1]:8s} conv={best[2]} sim_pts={best[4]} -> real pts={h['points']} "
                f"LOLE={h['summary']['lole_hours']} clean={h['summary']['clean_share']} CO2={h['summary']['co2_mt']:.1f}Mt "
                f"€/MWh={h['cost']['eur_per_mwh']:.0f} "
                f"backlash={h['backlash']} | {core.describe_luck(g['luck'][s])[:90]}")
        if verbose:
            print(line, flush=True)
        log.append(line)
        core.next_stage(g)
    total = core.total_points(g["teams"][tid])
    print(f"seed {seed} TOTAL {total}", flush=True)
    return {"seed": seed, "total": total, "log": log, "history": [
        {k: h[k] for k in ("points", "backlash")} | {"lole": h["summary"]["lole_hours"], "clean": h["summary"]["clean_share"],
                                                     "co2": h["summary"]["co2_mt"], "detail": h.get("clean_detail"),
                                                     "eur": h["cost"]["eur_per_mwh"],
                                                     "build": {k: v for k, v in h["build"].items() if v},
                                                     "convert": h.get("convert_mw", 0)}
        for h in g["teams"][tid]["history"]]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--borrow", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--influence", nargs="+", default=["h2_demo", "resilience"])
    ap.add_argument("--tokens", type=int, nargs="+", default=None, help="build tokens per stage")
    a = ap.parse_args()
    res = [play(s, a.borrow, influence=a.influence, tokens=a.tokens) for s in a.seeds]
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
