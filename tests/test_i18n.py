# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Language switch: every German text has an English version with the same placeholders."""
import ast
import re
from pathlib import Path

from ptz import i18n
from ptz.i18n_en import EN

ROOT = Path(__file__).resolve().parents[1] / "ptz"
PH = re.compile(r"\{[^{}]*\}")
GERMAN = re.compile(r"[äöüÄÖÜß]|\b(und|oder|nicht|der|die|das|mit|für|von|ist|eure?|Stufe|Punkte|Strom|Speicher)\b")


def _code_keys() -> set[str]:
    keys = set()
    for f in ROOT.rglob("*.py"):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "tr" and n.args \
                    and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                keys.add(n.args[0].value)
    return keys


def _table_keys() -> set[str]:
    """German texts kept in tables and translated when read (TDict, lists translated at the point of use)."""
    from ptz.game import core, runner
    from ptz.server import charts, player, rules, theme
    keys = set()
    for d in (core.LABELS, core.INFLUENCE, core.INFLUENCE_DETAIL, core.EVENT_TEXT, core.WEATHER_TEXT,
              core.CO2_SOURCES, core.CO2_ADVICE, runner.SERIES_LABELS, theme.RISK_DE, player.PHASE_DE):
        for k in d:
            v = dict.__getitem__(d, k)
            keys.update(v if isinstance(v, tuple) else (v,))
    keys.update(dict.__getitem__(theme.CAT, k)[0] for k in theme.CAT)
    keys.update(v[2] for v in theme.TECH.values())
    keys.update(theme.GROUPS_POS)
    keys.update(theme.GROUPS_NEG)
    keys.update(core.CAP_GROUPS)
    keys.update(g for g, _ in core.INFLUENCE_GROUPS)
    keys.update(list.__iter__(rules.STAGE_LABELS))
    for k, v in rules.GLOSSARY:
        keys.update((k, v))
    for t, i, _ in player.SECTIONS:
        keys.update((t, i))
    keys.update((player.COST_LABEL, player.COST_NOTE))
    keys.update(lab for lab, _, _ in charts.CAP_BAR)
    keys.update(runner.MONTHS)
    keys.update(["bearbeitet", "fertig gemeldet", "wird berechnet", "fertig", "Fehler"])    # team status
    keys.update(["Bauen", "Einfluss", "Simulator", "Ergebnisse", "Verlauf", "Regeln"])       # tabs
    keys.update(["Spielregeln", "Beitreten", "Team", "Einzelspiel", "Spielleitung", "Zero45"])  # page titles
    return keys


def test_every_text_has_an_english_version():
    missing = sorted((_code_keys() | _table_keys()) - set(EN))
    assert not missing, f"{len(missing)} texts without English version, e.g. {missing[:5]}"


def test_placeholders_and_markup_match():
    tag = re.compile(r"</?([a-zA-Z0-9]+)")
    for de, en in EN.items():
        assert sorted(PH.findall(de)) == sorted(PH.findall(en)), de
        assert tag.findall(de) == tag.findall(en), de
        assert de.count("**") == en.count("**"), de


def test_default_is_german_and_numbers():
    assert i18n.lang() == "de"
    assert i18n.tr("Stufe {0}", 2) == "Stufe 2"
    assert i18n.num(1234.5, 1) == "1.234,5"
    tok = i18n.force_lang("en")
    try:
        assert i18n.tr("Stufe {0}", 2) == "Stage 2"
        assert i18n.num(1234.5, 1) == "1,234.5"
        assert i18n.tr("unbekannter Text") == "unbekannter Text"     # falls back to German
    finally:
        i18n.reset_lang(tok)
    assert i18n.tr("Stufe {0}", 2) == "Stufe 2"


def test_generated_texts_in_english():
    """Tips, events and labels produced by the game logic come out in English."""
    from ptz.game import core
    cfg = core.default_config()
    summary = {"lole_hours": 12, "max_unserved_gw": 3.2, "co2_mt": 50.0, "clean_share": 70.0, "import_twh": 40,
               "generation_twh": {"gas": 60.0, "coal": 20.0}}
    luck = {"weather_year": 2009, "weather_level": "extreme", "demand_shock": -0.012,
            "event": {"kind": "storm", "start": 500, "factors": {"onwind": 0.5}}}
    tok = i18n.force_lang("en")
    try:
        texts = [core.describe_luck(luck), core.LABELS["onwind"], core.INFLUENCE["h2_grid"][0]]
        for pts in ({"reliability": 2, "clean": 4, "cost": 4}, {"reliability": 5, "clean": 1, "cost": 5},
                    {"reliability": 5, "clean": 5, "cost": 1}):
            ev = {"points": pts, "clean_detail": {"share": 1, "co2": 3},
                  "cost": {"eur_per_mwh": 90, "capex_bn": 20, "fom_bn": 5, "opex_bn": 10}}
            texts += core.stage_tip(cfg, 0, summary, ev)
    finally:
        i18n.reset_lang(tok)
    for x in texts:
        assert not GERMAN.search(x), x
