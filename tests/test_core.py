# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Rule tests (fast, no solver) and one engine smoke test."""
import copy

import pytest

from ptz.engine import model
from ptz.game import core

FAKE_SUMMARY = {"year": 2030, "demand_twh": 620, "served_twh": 619.0, "unserved_twh": 1.0, "lole_hours": 5,
                "max_unserved_gw": 3.0, "peak_demand_gw": 110, "clean_share": 76.0, "fossil_twh": 148, "co2_mt": 60.0,
                "opex_bn": 15.0, "opex_detail_bn": {}, "generation_twh": {}, "curtailment_twh": 5, "electrolyser_twh": 0,
                "battery_charge_twh": 2, "solve_seconds": 1}


@pytest.fixture
def game():
    cfg = copy.deepcopy(core.default_config())
    cfg["seed"] = 7
    g = core.new_game(cfg)
    tid, _ = core.add_team(g, "Test")
    core.start_stage(g)
    return g, tid


def test_tokens_and_limits(game):
    g, tid = game
    n = g["cfg"]["build_tokens"][0]
    assert core.tokens_left(g, tid) == n
    assert core.change_build(g, tid, "onwind", 3) is None
    assert core.tokens_left(g, tid) == n - 3
    assert core.change_build(g, tid, "onwind", n) is not None  # not enough tokens
    assert core.set_borrow(g, tid, 2) is None and core.tokens_left(g, tid) == n - 1
    assert core.set_borrow(g, tid, 99) is None and g["teams"][tid]["draft"]["borrow"] == g["cfg"]["max_borrow_tokens"]


def test_h2_lock_next_stage(game):
    g, tid = game
    assert core.change_build(g, tid, "h2_package", 1) is not None       # locked in stage 1
    assert core.toggle_influence(g, tid, "h2_demo") is None
    assert core.change_build(g, tid, "h2_package", 1) is not None       # still locked in the same stage
    core.close_stage(g)
    core.apply_stage_result(g, tid, FAKE_SUMMARY)
    core.finish_resolution(g)
    core.next_stage(g)
    assert core.change_build(g, tid, "h2_package", 1) is None           # unlocked from stage 2
    assert core.change_build(g, tid, "h2_storage", 1) is None


def test_coal_phaseout_cap(game):
    g, tid = game
    t = g["teams"][tid]
    assert t["draft"]["keep"]["coal"] <= 17000 + 1e-6
    core.set_keep(g, tid, "coal", 1e9)
    assert t["draft"]["keep"]["coal"] <= 17000 + 1e-6


def test_stage_result_updates_state(game):
    g, tid = game
    core.change_build(g, tid, "onwind", 4)
    core.set_keep(g, tid, "coal", 0)
    before = g["teams"][tid]["cap"]["onwind"]
    core.close_stage(g)
    rec = core.apply_stage_result(g, tid, FAKE_SUMMARY)
    t = g["teams"][tid]
    assert t["cap"]["onwind"] > before and t["cap"]["coal"] == 0
    assert rec["points"]["reliability"] == 4 and rec["points"]["clean"] == 4
    assert t["learn"]["onwind"] < 1.0
    assert len(t["investments"]) == 1


def test_luck_is_reproducible(game):
    g, _ = game
    a = core.draw_luck(g)
    b = core.draw_luck(g)
    assert a == b
    assert a["weather_year"] in (2008, 1995, 2009)
    # three weather levels with the configured frequencies
    from collections import Counter
    c = Counter()
    for seed in range(400):
        g["seed"] = seed
        c[core.draw_luck(g)["weather_level"]] += 1
    assert 0.5 < c["normal"] / 400 < 0.7 and 0.2 < c["hard"] / 400 < 0.4 and 0.04 < c["extreme"] / 400 < 0.17


def test_influence_once(game):
    g, tid = game
    assert core.toggle_influence(g, tid, "resilience") is None
    assert core.toggle_influence(g, tid, "social") is None
    assert core.toggle_influence(g, tid, "innovation") is not None     # only 2 tokens
    assert core.buy_influence(g, tid, 1) is None
    assert core.toggle_influence(g, tid, "innovation") is None
    assert core.tokens_left(g, tid) == g["cfg"]["build_tokens"][0] - g["cfg"]["influence_token_price"]
    inv = [i for i in core.stage_investments(g, tid) if i["tech"] == "influence"]
    assert inv and inv[0]["eur"] == g["cfg"]["influence_token_price"] * g["cfg"]["token_value_bn"] * 1e9
    cost = core.system_cost(g, tid, core.portfolio(g, tid), FAKE_SUMMARY, core.stage_investments(g, tid))
    cost0 = core.system_cost(g, tid, core.portfolio(g, tid), FAKE_SUMMARY, [])
    assert cost["capex_bn"] > cost0["capex_bn"]          # influence programme counts as cost


def test_h2_firm_two_weeks():
    e = core.assumptions()["technologies"]["gas_new"]["efficiency"]
    cap = {"gas_new_h2": 20000.0}
    assert core.h2_firm(cap) == 0                                    # no hydrogen: not secured
    cap["h2_import"] = 15000.0
    assert core.h2_firm(cap) == pytest.approx(15000 * e)             # import only
    cap["h2_storage"] = 3.7e6                                        # + one cavern token (MWh H2)
    assert core.h2_firm(cap) == pytest.approx(min(20000, (15000 + 3.7e6 / 336) * e))
    cap["h2_storage"] = 50e6
    assert core.h2_firm(cap) == 20000                                # capped by the turbines


def test_insights_and_firm_capacity(game):
    import numpy as np, pandas as pd
    from ptz.game import runner
    g, tid = game
    cap = core.portfolio(g, tid)
    assert core.firm_capacity(cap) > 50e3
    disp = pd.DataFrame({k: np.zeros(8760) for k in ["onwind", "offwind", "solar_utility", "solar_rooftop",
                                                     "lost_load", "demand"]})
    disp["demand"] = 60.0
    disp.loc[100, "lost_load"] = 5.0
    s = dict(FAKE_SUMMARY, generation_twh={"gas": 100, "coal": 50, "onwind": 200})
    lines = runner.insights(s, disp, {"capex_bn": 1, "fom_bn": 2, "opex_bn": 30, "blackout_bn": 0, "total_bn": 33})
    assert lines and "Versorgungslücke" in lines[0] and "5. Januar" in lines[0]


def test_points():
    assert core.points_lower_better(3, [3, 10, 25, 50, 100]) == 5
    assert core.points_lower_better(101, [3, 10, 25, 50, 100]) == 0
    assert core.points_higher_better(79.9, [80, 75, 70, 65, 60]) == 4


@pytest.mark.slow
def test_engine_smoke():
    from ptz.engine.model import simulate
    cap = {"onwind": 120e3, "offwind": 30e3, "solar_utility": 120e3, "solar_rooftop": 80e3, "battery": 30e3,
           "h2_package": 10e3, "h2_storage": 5e6, "gas": 30e3, "gas_new_h2": 5e3, "coal": 6e3, "biomass": 8e3,
           "biomass_flex": 4e3,
           "ror": 3.9e3, "waste": 1.9e3, "trade": 18e3}
    r = simulate(cap, 2035, 2009, event={"kind": "dunkelflaute", "start": 400, "hours": 336,
                                          "factors": {"onwind": 0.3, "offwind": 0.3, "solar": 0.5}, "demand_factor": 1.05})
    s = r["summary"]
    assert 0 < s["clean_share"] <= 100
    assert s["generation_twh"]["biomass"] <= 41.0 * 1.0001
    assert s["generation_twh"]["coal"] >= 6e3 * 0.3 * 8760 / 1e6 * 0.99   # coal must-run 30 %
    assert len(r["dispatch"]) == 8760
    assert s["electrolyser_twh"] >= 0
    assert s["import_twh"] >= 0 and s["export_twh"] >= 0 and 0 <= s["clean_share"] <= 100
    assert s["generation_twh"]["gas_new_h2"] > 0                      # H2 only via converted turbines


def test_start_fleet_split_and_fixed_blocks(game):
    g, tid = game
    t = g["teams"][tid]
    assert t["cap"]["onwind"] == 0 and t["cap"]["onwind_old"] > 60e3
    assert t["cap"]["battery"] == 0 and t["cap"]["battery_old"] > 3e3
    assert abs(t["cap"]["solar_rooftop"] / (t["cap"]["solar_rooftop"] + t["cap"]["solar_utility"]) - 0.66) < 1e-6
    cap = core.portfolio(g, tid)
    assert cap["phs"] == 9900 and cap["reserve"] > 10e3
    g["stage"] = 2
    assert core.portfolio(g, tid)["reserve"] < 4e3      # coal reserve gone from 2040


def test_ready_reset_and_rev(game):
    g, tid = game
    t = g["teams"][tid]
    t["ready"] = True
    rev = t["rev"]
    core.close_stage(g)
    assert t["ready"] is False and t["rev"] > rev
    t["ready"] = True
    g["phase"] = "results"
    core.next_stage(g)
    assert t["ready"] is False


def test_conversion_needs_h2_and_is_clamped(game):
    g, tid = game
    t = g["teams"][tid]
    t["h2_unlocked_from"] = t["electrolysis_from"] = 0
    core.change_build(g, tid, "gas_new", 2)
    core.change_build(g, tid, "h2_package", 1)
    assert core.set_convert(g, tid, 1e9) is not None                    # storage still missing
    core.change_build(g, tid, "h2_storage", 1)
    assert core.set_convert(g, tid, 1e9) is None
    full = core.max_convert(g, tid)
    assert core.effective_convert(g, tid) == pytest.approx(full)
    core.change_build(g, tid, "gas_new", -1)          # fewer new gas plants -> conversion clamped
    assert core.effective_convert(g, tid) < full
    inv = [i for i in core.stage_investments(g, tid) if i["tech"] == "gas_new_h2"][0]
    assert inv["mw"] == pytest.approx(core.effective_convert(g, tid))
    core.change_build(g, tid, "h2_package", -1)       # no electrolysis -> no conversion
    assert core.effective_convert(g, tid) == 0
    core.change_build(g, tid, "h2_package", 1)
    core.change_build(g, tid, "h2_storage", -1)       # no storage -> no conversion
    assert core.effective_convert(g, tid) == 0
    assert not [i for i in core.stage_investments(g, tid) if i["tech"] == "gas_new_h2"]


def test_biomass_flex_limited_to_kept_biomass(game):
    g, tid = game
    core.change_build(g, tid, "biomass_flex", 1)
    flex = core.portfolio(g, tid)["biomass_flex"]
    assert flex > 0
    assert core.can_build(g, tid, "biomass_flex")[0]          # a 2nd token fits (cap 2x kept base)
    core.change_build(g, tid, "biomass_flex", 1)
    assert not core.can_build(g, tid, "biomass_flex")[0]      # a 3rd does not
    flex = core.portfolio(g, tid)["biomass_flex"]
    core.set_keep(g, tid, "biomass", 2000)
    assert core.portfolio(g, tid)["biomass_flex"] == pytest.approx(min(flex, 4000))
    core.apply_stage_result(g, tid, FAKE_SUMMARY)
    assert g["teams"][tid]["cap"]["biomass_flex"] == pytest.approx(flex)   # owned MW are kept


def test_join_rules(game):
    g, tid = game
    assert core.can_join(g) is None
    g["phase"] = "resolving"
    assert core.can_join(g)
    g["phase"] = "finished"
    assert core.can_join(g)
    core.remove_team(g, tid)
    assert tid not in g["teams"]


def test_server_helpers():
    from ptz.server.host import csv_cell, safe_preset_name
    assert "/" not in safe_preset_name("../../evil") and "." not in safe_preset_name("../../evil")
    assert csv_cell("=HYPERLINK(1)").startswith("'") and csv_cell(3) == 3


def test_host_only_on_this_computer():
    from types import SimpleNamespace as NS
    from ptz.server import app as srv
    req = lambda ip: NS(client=NS(host=ip))
    srv.ARGS.update(local=False, host_remote=False)
    assert srv.host_allowed(req("127.0.0.1")) and not srv.host_allowed(req("192.168.1.50"))
    srv.ARGS["host_remote"] = True
    assert srv.host_allowed(req("192.168.1.50"))
    srv.ARGS["host_remote"] = False


def test_team_names_cleaned():
    assert core.clean_name("<img src=x onerror=alert(1)>") == "img src=x onerror=alert(1)"
    assert core.clean_name("  Team\n\tSonne  ") == "Team Sonne"
    assert len(core.clean_name("x" * 100)) == 30


def test_ageing_trade_and_h2_split(game):
    g, tid = game
    t = g["teams"][tid]
    cap = core.portfolio(g, tid)
    assert cap["onwind_old"] < t["start_cap"]["onwind_old"]          # old onshore fleet already shrinking in 2030
    assert cap["trade"] == 25000 and cap["waste"] > 1800
    assert cap["flex_shift"] == 0 and cap["flex_shed"] == 0
    g["stage"] = 3
    core.reset_draft(g, tid)
    cap45 = core.portfolio(g, tid)
    assert cap45["onwind_old"] < 0.35 * t["start_cap"]["onwind_old"] and cap45["other_fossil"] == 0
    assert cap45["solar_utility"] < t["start_cap"]["solar_utility"]
    # Netzausbau Europa: +10 GW and flexible consumers: both from the following stage
    t["influence_used"]["grid_eu"] = 2
    t["influence_used"]["flex"] = 3
    cap45 = core.portfolio(g, tid)
    assert cap45["trade"] == 35000 + 10000 and cap45["flex_shift"] == 0
    t["influence_used"]["flex"] = 2
    cap45 = core.portfolio(g, tid)
    assert cap45["flex_shift"] == 20000 and cap45["flex_shed"] == 10000
    # stored team capacities stay un-aged
    core.apply_stage_result(g, tid, FAKE_SUMMARY)
    assert t["cap"]["onwind_old"] == t["start_cap"]["onwind_old"]


def test_h2_split_investments_and_units(game):
    g, tid = game
    t = g["teams"][tid]
    t["h2_unlocked_from"] = t["electrolysis_from"] = 0
    core.change_build(g, tid, "h2_package", 1)
    core.change_build(g, tid, "h2_storage", 1)
    inv = {i["tech"]: i for i in core.stage_investments(g, tid)}
    assert inv["h2_package"]["lifetime"] == 25 and inv["h2_storage"]["lifetime"] == 100
    for k in ("h2_package", "h2_storage"):                          # one token = 10 bn EUR each
        assert inv[k]["mw"] * 1e3 * inv[k]["eur_kw"] == pytest.approx(10e9)
    cap = core.portfolio(g, tid)
    assert 3e6 < cap["h2_storage"] < 5e6                          # MWh: ~3.7 TWh H2 per token in 2030
    assert 4e3 < cap["h2_package"] < 7e3                          # MW: ~5.3 GW electrolysis per token


def test_h2_reach_and_warnings():
    assert core.h2_warnings({}) == []
    assert any("Speicher" in w for w in core.h2_warnings({"gas_new_h2": 5000}))
    assert any("Elektrolyse" in w for w in core.h2_warnings({"gas_new_h2": 5000, "h2_storage": 1e6}))
    assert any("verstromt" in w for w in core.h2_warnings({"h2_package": 5000, "h2_storage": 1e6}))
    assert core.h2_warnings({"h2_package": 5000, "h2_storage": 1e6, "gas_new_h2": 5000}) == []
    r = core.h2_reach({"h2_storage": 2e6, "gas_new_h2": 10000})
    assert r["store_twh"] == pytest.approx(2.0) and r["twh_el"] == pytest.approx(0.82, abs=0.01)
    assert r["hours"] == pytest.approx(82, abs=1)


def test_net_zero_scoring_takes_worse_of_share_and_mt(game):
    g, tid = game
    cfg = g["cfg"]
    good_share_high_co2 = dict(FAKE_SUMMARY, clean_share=100.0, co2_mt=95.0)
    d = core.clean_points_detail(cfg, 0, good_share_high_co2)
    assert d == {"share": 5, "co2": 2}
    assert core.score(g, good_share_high_co2, {"eur_per_mwh": 60})["clean"] == 2
    low_share_low_co2 = dict(FAKE_SUMMARY, clean_share=70.0, co2_mt=20.0)
    assert core.score(g, low_share_low_co2, {"eur_per_mwh": 60})["clean"] == 3
    old_cfg = {k: v for k, v in cfg.items() if k != "co2_mt_thresholds"}   # presets without the new rule
    assert core.clean_points_detail(old_cfg, 0, good_share_high_co2) == {"share": 5}


@pytest.mark.slow
def test_h2_storage_limits_hydrogen_power():
    """Without storage the converted turbines produce nothing; with storage they do."""
    cap = core.start_capacities()
    cap.update(trade=25000, onwind=150e3, solar_utility=150e3, h2_package=10e3, gas_new_h2=10e3)
    none = model.simulate(cap, 2040, 2008)["summary"]["generation_twh"].get("gas_new_h2", 0)
    cap["h2_storage"] = 3e6
    some = model.simulate(cap, 2040, 2008)["summary"]["generation_twh"].get("gas_new_h2", 0)
    assert none < 0.05 and some > 0.5
    assert some <= 3e6 * 0.41 / 1e6 * 20                          # bounded by refills of the 3 TWh store


def test_flex_and_neighbour_storage_in_engine():
    """Flexible consumers and the neighbour storage are used and booked consistently."""
    cap = core.start_capacities()
    cap["trade"] = 25000
    cap.update(flex_shift=5000, flex_shed=4000)
    s = model.simulate(cap, 2030, 2008)["summary"]
    g = s["generation_twh"]
    assert g["flex_shift_discharge"] > 1                       # load shifting is used
    assert g["flex_shed"] <= 4000 * 200 / 1e6 + 1e-6          # shedding limited to 200 full-load hours
    assert 0 < s["nb_storage_out_twh"] < s["nb_storage_in_twh"]   # storage abroad returns less than it took
    d = model.simulate(cap, 2030, 2008)["dispatch"]
    shift = (d["flex_shift_discharge"] + d["flex_shift_charge"]).to_numpy().reshape(365, 24).sum(axis=1)
    assert abs(shift).max() < 1e-3                             # load shifting balances within each day
    assert s["import_twh"] >= s["nb_storage_out_twh"] and s["export_twh"] >= s["nb_storage_in_twh"]


def test_h2_grid_card_timing_and_conversion(game):
    g, tid = game
    assert core.h2_import_cap(g, tid) == 0
    assert core.toggle_influence(g, tid, "h2_grid") is None
    core.close_stage(g)
    core.apply_stage_result(g, tid, FAKE_SUMMARY)
    core.finish_resolution(g)
    core.next_stage(g)                                              # stage 2 (2035): import active, H2 unlocked
    assert core.h2_import_cap(g, tid) == 15000 and core.h2_available(g, tid)
    assert core.can_build(g, tid, "h2_storage")[0]                  # grid unlocks storage ...
    assert not core.can_build(g, tid, "h2_package")[0]               # ... but not electrolysis (h2_demo only)
    core.change_build(g, tid, "gas_new", 1)
    assert core.set_convert(g, tid, 5000) is None                  # import alone is enough to convert
    assert core.portfolio(g, tid)["h2_import"] == 15000


@pytest.mark.slow
def test_h2_import_feeds_turbines_and_is_paid():
    cap = core.start_capacities()
    cap.update(trade=25000, onwind=100e3, solar_utility=100e3, gas_new_h2=20000, h2_import=30000, gas=0)
    s = model.simulate(cap, 2040, 2008)["summary"]
    assert s["generation_twh"]["gas_new_h2"] > 1 and s["h2_import_twh"] > 2
    assert s["opex_detail_bn"]["h2_import"] > 0
    assert s["generation_twh"]["gas_new_h2"] <= s["h2_import_twh"] * 0.41 + 0.05     # no storage: all from import


@pytest.mark.slow
def test_electrolysis_only_from_domestic_surplus():
    """Green hydrogen rule: without renewable surplus the electrolyser stays off, even with cheap imports."""
    cap = core.start_capacities()
    cap.update(trade=25000, h2_package=20000, h2_storage=2e6, gas_new_h2=5000, gas_new=10000)
    lean = model.simulate(cap, 2035, 2008)["summary"]["electrolyser_twh"]
    cap.update(onwind=200e3, solar_utility=200e3)
    rich = model.simulate(cap, 2035, 2008)["summary"]["electrolyser_twh"]
    assert lean < 0.5 and rich > 5


def test_blackout_not_in_cost_score(game):
    """A supply gap costs reliability points only: the damage is reported but not in EUR/MWh."""
    g, tid = game
    cap = core.portfolio(g, tid)
    gap = dict(FAKE_SUMMARY)
    none = dict(FAKE_SUMMARY, unserved_twh=0.0)
    c1, c0 = core.system_cost(g, tid, cap, gap, []), core.system_cost(g, tid, cap, none, [])
    assert c1["blackout_bn"] == pytest.approx(10.0)            # 1 TWh x 10,000 EUR/MWh
    assert c1["eur_per_mwh"] == pytest.approx(c0["eur_per_mwh"])
    ev = {"points": {"reliability": 0, "clean": 3, "cost": 3}, "clean_detail": {"share": 3, "co2": 3},
          "cost": c1}
    cap.update(gas_new_h2=20000.0, h2_storage=0.0, h2_import=0.0)
    tip = core.stage_tip(g["cfg"], 0, gap, ev, cap)[0]
    assert "H₂-Turbinen" in tip and "normales Jahr" in tip
    assert "normales Jahr" not in core.stage_tip(g["cfg"], 0, gap, ev, cap, sim=True)[0]

def test_extra_simulations_only_for_one_stage():
    g = core.new_game()
    tid, _ = core.add_team(g, "A")
    core.start_stage(g)
    g["teams"][tid]["sims_extra"] = 2          # host gave +2 in stage 1
    g["stage"] = 1
    core.start_stage(g)
    assert g["teams"][tid]["sims_extra"] == 0 and g["teams"][tid]["sims_used"] == 0
