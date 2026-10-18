# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Plotly figures for dispatch, scores and comparisons."""
from __future__ import annotations

import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ptz.game.runner import daily, grouped
from ptz.server.theme import CAT, GROUPS_NEG, GROUPS_POS
from ptz.i18n import is_en, tr

FONT = dict(family="Inter, Roboto, Arial, sans-serif", size=13, color="#111827")
LAYOUT = dict(margin=dict(l=50, r=10, t=36, b=40), font=FONT,
              legend=dict(orientation="h", y=-0.22, font=dict(size=12)),
              hovermode="x unified", plot_bgcolor="#ffffff", paper_bgcolor="rgba(0,0,0,0)", height=440,
              xaxis=dict(gridcolor="#eef0f3"), yaxis=dict(gridcolor="#eef0f3"),
              separators=",.")


def _layout(**over) -> dict:
    """LAYOUT with the decimal separator of the viewer's language."""
    return {**LAYOUT, "separators": ".," if is_en() else ",.", **over}


# Plotly treats two clicks as a double click only within 300 ms by default - slower than many people click
# (Windows default: 500 ms), so "double click shows only this group" seemed not to work. Allow 600 ms.
PLOT_CONFIG = {"doubleClickDelay": 600, "displaylogo": False}


def as_plot(fig: go.Figure) -> dict:
    """Figure as dict for ui.plotly, with our config."""
    d = fig.to_plotly_json()
    d["config"] = dict(PLOT_CONFIG)
    return d


def _txt(s: str) -> str:
    """Plotly interprets a subset of HTML in labels: escape user-provided text."""
    return html.escape(str(s), quote=False)


def dispatch_figure(disp: pd.DataFrame, start: int | None = None, title: str = "") -> go.Figure:
    """start=None: whole year as daily means; else one week (168 h) from start hour. Series grouped."""
    if start is None:
        d = daily(disp)
        x = np.arange(len(d)) + 1
        xtitle = tr("Tag im Jahr (Tagesmittel)")
    else:
        start = int(max(0, min(start, len(disp) - 168)))
        d = disp.iloc[start:start + 168]
        x = (np.arange(len(d)) / 24) + 1
        xtitle = tr("Tag der Woche (Woche {0})", start // 168 + 1)
    fig = go.Figure()
    for stack, groups in (("pos", GROUPS_POS), ("neg", GROUPS_NEG)):
        for name, y in grouped(d, groups).items():
            if np.abs(y).max() < 0.05:
                continue
            color = groups[name][0]
            fig.add_trace(go.Scatter(x=x, y=y, name=tr(name), stackgroup=stack, mode="lines",
                                     line=dict(width=0.5, color=color), fillcolor=color,
                                     hovertemplate="%{y:.1f} GW"))
    fig.add_trace(go.Scatter(x=x, y=d["demand"].to_numpy(), name=tr("Verbrauch"), mode="lines",
                             line=dict(color="#111", width=2, dash="dot"), hovertemplate="%{y:.1f} GW"))
    fig.update_layout(**_layout(), title=dict(text=_txt(title), font=dict(size=15)), xaxis_title=xtitle,
                      yaxis_title="GW")
    return fig


def storage_figure(disp: pd.DataFrame) -> go.Figure:
    """Daily mean state of charge: hydrogen (TWh, left axis), pumped hydro and batteries (GWh, right axis)."""
    d = daily(disp)
    x = np.arange(len(d)) + 1
    fig = go.Figure()
    if d["h2_soc"].max() > 0:
        fig.add_trace(go.Scatter(x=x, y=d["h2_soc"] / 1e3, name=tr("Wasserstoffspeicher (TWh H₂, links)"),
                                 line=dict(color=GROUPS_POS["Wasserstoff"][0], width=2)))
    if "phs_soc" in d and d["phs_soc"].max() > 0:
        fig.add_trace(go.Scatter(x=x, y=d["phs_soc"], name=tr("Pumpspeicher (GWh, rechts)"), yaxis="y2",
                                 line=dict(color="#17a2b8")))
    if d["battery_soc"].max() > 0:
        fig.add_trace(go.Scatter(x=x, y=d["battery_soc"], name=tr("Batterien (GWh, rechts)"), yaxis="y2",
                                 line=dict(color="#c2549d")))
    fig.update_layout(**_layout(height=300), xaxis_title=tr("Tag im Jahr (Tagesmittel)"))
    fig.update_layout(yaxis=dict(title="TWh H₂", rangemode="tozero", gridcolor="#eef0f3"),
                      yaxis2=dict(title="GWh", overlaying="y", side="right", rangemode="tozero", showgrid=False))
    return fig


def points_bar(rows: list[dict]) -> go.Figure:
    names = [_txt(r["name"]) for r in rows]
    fig = go.Figure()
    for key, (label, _, color) in CAT.items():
        fig.add_trace(go.Bar(y=names, x=[r[key] for r in rows], name=label, orientation="h", marker_color=color,
                             text=[r[key] for r in rows], textposition="inside"))
    fig.update_layout(**_layout(height=max(260, 52 * len(rows) + 120), hovermode="closest"),
                      barmode="stack", xaxis_title=tr("Punkte"))
    fig.update_layout(yaxis=dict(autorange="reversed", tickfont=dict(size=15)))
    return fig


def mix_bar(teams: list[tuple[str, dict]]) -> go.Figure:
    """Electricity generation mix (TWh) per team for one stage, grouped like the dispatch chart."""
    fig = go.Figure()
    names = [_txt(n) for n, _ in teams]
    for name, (color, members) in GROUPS_POS.items():
        members = [m for m in members if m not in ("battery_discharge", "phs_discharge", "lost_load", "flex_shed",
                                                  "flex_shift_discharge")]
        if not members:
            continue
        vals = [sum(g.get(m, 0) for m in members) for _, g in teams]
        if max(vals or [0]) < 0.1:
            continue
        fig.add_trace(go.Bar(x=names, y=vals, name=tr(name), marker_color=color))
    fig.update_layout(**_layout(hovermode="closest"), barmode="stack", yaxis_title="TWh")
    return fig


CAP_BAR = [  # (label, capacity keys, colour) for the fleet comparison on the host page
    ("Onshore-Wind", ["onwind", "onwind_old"], "#3b82c4"),
    ("Offshore-Wind", ["offwind", "offwind_old"], "#1e4f8a"),
    ("Photovoltaik", ["solar_utility", "solar_rooftop"], "#e9b10e"),
    ("Batterien", ["battery", "battery_old"], "#c2549d"),
    ("Pumpspeicher", ["phs"], "#17a2b8"),
    ("Flexible Verbraucher", ["flex_shift", "flex_shed"], "#0891b2"),
    ("Biomasse, Wasser, Abfall", ["biomass", "biomass_flex", "ror", "waste"], "#3f8f3f"),
    ("Wasserstoff-Turbinen", ["gas_new_h2"], "#b07aa1"),
    ("Gasturbinen neu", ["gas_new"], "#e07b67"),
    ("Gas Bestand", ["gas"], "#d64545"),
    ("Kohle", ["coal"], "#6b5b45"),
    ("Öl & Reserve", ["other_fossil", "reserve"], "#8c8c8c"),
    ("Elektrolyse", ["h2_package"], "#8e5bd6"),
]


def fleet_bar(teams: list[tuple[str, dict]]) -> go.Figure:
    """Installed capacity (GW) per team for one stage."""
    fig = go.Figure()
    names = [_txt(n) for n, _ in teams]
    for label, keys, color in CAP_BAR:
        vals = [round(sum(c.get(k, 0.0) for k in keys) / 1e3, 1) for _, c in teams]
        if max(vals or [0]) < 0.1:
            continue
        fig.add_trace(go.Bar(x=names, y=vals, name=tr(label), marker_color=color,
                             hovertemplate="%{x}: %{y:.1f} GW<extra>" + tr(label) + "</extra>"))
    fig.update_layout(**_layout(hovermode="closest", height=460), barmode="stack", yaxis_title="GW")
    return fig


def score_chart(history: list[dict], stages: int) -> go.Figure:
    """Points per stage and category (stacked)."""
    labels = [tr("Stufe {0}", i + 1) for i in range(stages)]
    fig = go.Figure()
    for key, (label, _, color) in CAT.items():
        vals = [None] * stages
        for h in history:
            vals[h["stage"]] = h["points"][key]
        fig.add_trace(go.Bar(x=labels, y=vals, name=label, marker_color=color, text=vals, textposition="inside"))
    fig.update_layout(**_layout(height=300, hovermode="closest"), barmode="stack")
    fig.update_layout(yaxis=dict(title=tr("Punkte"), range=[0, 15], dtick=5, gridcolor="#eef0f3"))
    return fig
