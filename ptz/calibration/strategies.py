# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Scripted strategies for testing and calibration. Each returns per-stage decisions."""
STRATEGIES = {
    "ausgewogen": [
        dict(build=dict(onwind=5, solar_utility=3, solar_rooftop=1, offwind=1, battery=2, gas_new=4),
             influence=["h2_demo", "resilience"], keep=dict(coal=0)),
        dict(build=dict(onwind=5, solar_utility=2, offwind=2, battery=2, h2_package=2, h2_storage=1, gas_new=2)),
        dict(build=dict(onwind=5, solar_utility=2, offwind=2, battery=2, h2_package=2, h2_storage=1, gas_new=2), convert=1.0),
        dict(build=dict(onwind=4, solar_utility=2, offwind=2, battery=3, h2_package=2, h2_storage=1, gas_new=2), convert=1.0),
    ],
    "fossil_halten": [
        dict(build=dict(onwind=4, solar_utility=4, solar_rooftop=2, battery=2, gas_new=4)),
        dict(build=dict(onwind=4, solar_utility=4, solar_rooftop=2, battery=2, gas_new=4)),
        dict(build=dict(onwind=4, solar_utility=4, solar_rooftop=2, battery=2, gas_new=4)),
        dict(build=dict(onwind=4, solar_utility=4, solar_rooftop=2, battery=2, gas_new=4)),
    ],
    "nur_erneuerbar": [
        dict(build=dict(onwind=7, solar_utility=5, offwind=2, battery=2), keep=dict(coal=0)),
        dict(build=dict(onwind=7, solar_utility=5, offwind=2, battery=2), keep=dict(gas=15000)),
        dict(build=dict(onwind=7, solar_utility=5, offwind=2, battery=2)),
        dict(build=dict(onwind=7, solar_utility=5, offwind=2, battery=2)),
    ],
}


def apply(game, tid, dec, core):
    for t, n in dec.get("build", {}).items():
        core.change_build(game, tid, t, n)
    for k, mw in dec.get("keep", {}).items():
        core.set_keep(game, tid, k, mw)
    for key in dec.get("influence", []):
        core.toggle_influence(game, tid, key)
    if dec.get("convert"):
        core.set_convert(game, tid, core.max_convert(game, tid) * dec["convert"])

STRATEGIES["klug"] = [
    dict(build=dict(onwind=5, solar_utility=3, offwind=1, battery=2, gas_new=5), influence=["h2_demo", "resilience"],
         keep=dict(coal=0)),
    dict(build=dict(onwind=5, solar_utility=3, offwind=2, battery=2, h2_package=2, h2_storage=1, gas_new=1)),
    dict(build=dict(onwind=5, solar_utility=3, offwind=2, battery=2, h2_package=2, h2_storage=1, gas_new=1), convert=0.5),
    dict(build=dict(onwind=4, solar_utility=3, offwind=2, battery=3, h2_package=2, h2_storage=1, gas_new=1), convert=1.0),
]
