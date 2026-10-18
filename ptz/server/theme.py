# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Shared look & feel: number formatting, technology colours/icons/texts, CSS."""
from __future__ import annotations

from ptz.i18n import TDict, num, tr

SEP = " | "

# --------------------------------------------------------------------------- formatting
def de(x: float, d: int = 1) -> str:
    """Number in the viewer's format (German 1.234,5 / English 1,234.5)."""
    return num(x, d)


def gw(mw: float, d: int = 1) -> str:
    return de(mw / 1e3, d) + " GW"


def pct(x: float, d: int = 0) -> str:
    return de(x, d) + " %"


# --------------------------------------------------------------------------- technologies
# colour, Material icon, one-line description (shown on cards and in the rules)
TECH = {
    "onwind": ("#3b82c4", "air", "Günstiger Strom bei Wind; liefert im Winter mehr als im Sommer."),
    "offwind": ("#1e4f8a", "sailing", "Weht stetiger und stärker als an Land, aber teurer."),
    "solar_utility": ("#e9b10e", "solar_power", "Billigster Strom, aber nur tagsüber und vor allem im Sommer."),
    "solar_rooftop": ("#f08c1a", "roofing", "Wie Freiflächen-PV, ~10 % weniger Ertrag, teurer – dafür kaum Widerstand."),
    "battery": ("#c2549d", "battery_charging_full", "Verschiebt Strom z. B. vom Mittag in den Abend; voll geladen reicht er 4 h bei voller Leistung."),
    "biomass_flex": ("#6aae5a", "tune", "Mehr Leistung an Biogasanlagen: gleiche Energiemenge, aber gezielt bei Knappheit."),
    "gas_new": ("#e07b67", "local_fire_department", "Günstige Gasturbinen als Reserve: jederzeit startbereit, stoßen CO₂ aus – auf H₂ umrüstbar."),
    "h2_package": ("#8e5bd6", "science", "Elektrolyse: macht aus deutschem Ökostrom-Überschuss Wasserstoff – für Speicher und umgerüstete Gasturbinen."),
    "h2_storage": ("#6d28d9", "propane_tank", "Salzkaverne: bewahrt Wasserstoff über Wochen und Monate auf – günstig pro TWh."),
    "coal": ("#6b5b45", "factory", "Hohe CO₂-Emissionen, träge (mind. 15 % Leistung). Gesetzlicher Ausstieg."),
    "gas": ("#d64545", "local_fire_department", "Bestehende Gaskraftwerke: steuerbar, stoßen CO₂ aus."),
    "biomass": ("#3f8f3f", "grass", "Biogas, Holz u. a.: steuerbar, Energiemenge begrenzt (~41 TWh/Jahr)."),
    "ror": ("#3d5a80", "water", "Laufwasser: kleiner, recht gleichmäßiger Beitrag."),
    "phs": ("#17a2b8", "water_drop", "Pumpspeicher: voll geladen reicht er ca. 6 h bei voller Leistung."),
    "battery_old": ("#c2549d", "battery_std", "Bestehende Großbatterien: voll geladen reichen sie ca. 1 h bei voller Leistung."),
    "other_fossil": ("#8c8c8c", "factory", "Öl, Grubengas u. a.: teuer, nur bei Knappheit; ab 2040 stillgelegt."),
    "reserve": ("#4d4d4d", "shield", "Reservekraftwerke außerhalb des Markts: nur in Notlagen."),
    "gas_new_h2": ("#b07aa1", "swap_horiz", "Neue Gasturbinen, die Wasserstoff aus dem eigenen Speicher verbrennen."),
    "waste": ("#7a6f5a", "delete", "Abfallverbrennung: läuft immer, zur Hälfte erneuerbar."),
    "trade": ("#0f766e", "public", "Kuppelleitungen zu den Nachbarländern: Import und Export."),
    "flex": ("#0891b2", "electric_car", "E-Autos und Wärmepumpen verschieben Verbrauch, Industrie verzichtet bei "
                                        "Knappheit."),
}


def tcolor(k: str) -> str:
    return TECH.get(k, ("#999999",))[0]


def ticon(k: str) -> str:
    return TECH.get(k, ("", "bolt"))[1]


def tdesc(k: str) -> str:
    return tr(TECH.get(k, ("", "", ""))[2])


# chart groups: name -> (colour, member series)
GROUPS_POS = {
    "Wasser": ("#3d5a80", ["ror"]),
    "Biomasse & Abfall": ("#3f8f3f", ["biomass", "waste"]),
    "Kohle": ("#6b5b45", ["coal"]),
    "Erdgas": ("#d64545", ["gas", "gas_new"]),
    "Sonstige & Reserve": ("#8c8c8c", ["other_fossil", "reserve"]),
    "Wasserstoff": ("#8e5bd6", ["h2_turbine", "gas_new_h2"]),
    "Wind": ("#3b82c4", ["onwind", "offwind"]),
    "Sonne": ("#e9b10e", ["solar_utility", "solar_rooftop"]),
    "Speicher (Entladen)": ("#c2549d", ["battery_discharge", "phs_discharge"]),
    "Flexible Verbraucher": ("#0891b2", ["flex_shed", "flex_shift_discharge"]),
    "Import": ("#0f766e", ["import"]),
    "Versorgungslücke": ("#111111", ["lost_load"]),
}
GROUPS_NEG = {
    "Speicher (Laden)": ("#e7a6cd", ["battery_charge", "phs_charge"]),
    "Verbrauch verschoben": ("#67e8f9", ["flex_shift_charge"]),
    "Elektrolyse": ("#c9b3ee", ["electrolyser"]),
    "Export": ("#5eead4", ["export"]),
}

RISK_DE = TDict({"none": "kein", "low": "niedrig", "moderate": "mittel", "high": "hoch"})
RISK_COLOR = {"none": "grey-7", "low": "green-8", "moderate": "orange-9", "high": "red-8"}
POINT_COLORS = ["#9ca3af", "#dc2626", "#ea580c", "#ca8a04", "#65a30d", "#15803d"]
CAT = TDict(idx=(0,), **{  # score categories (name translated when read)
    "reliability": ("Versorgungssicherheit", "bolt", "#2563eb"),
    "clean": ("Klimaschutz", "eco", "#16a34a"),
    "cost": ("Bezahlbarkeit", "euro", "#ea580c"),
})

CSS = """
<style>
:root { --ptz-ink:#111827; --ptz-sub:#374151; --ptz-muted:#4b5563; --ptz-line:#e5e7eb; --ptz-bg:#f3f5f9; }
html, body { overflow-anchor: none; }
body { background: var(--ptz-bg); color: var(--ptz-ink); font-size: 16px; }
.ptz-card { border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,.08); border: 1px solid var(--ptz-line); background:#fff; }
@keyframes ptzblink { 50% { opacity: .35; } }
.ptz-blink { animation: ptzblink 1s step-start infinite; }
.ptz-tech { border-left: 6px solid var(--tc, #999); height: 100%; }
.ptz-card.ptz-chosen { background:#ecfdf5; border: 2px solid #16a34a; border-left: 6px solid #16a34a;
  box-shadow: 0 0 0 3px rgba(22,163,74,.18); }
.ptz-card.ptz-used { background:#f3f4f6; opacity:.85; }
.ptz-big { font-size: 1.7rem; font-weight: 800; line-height: 1.1; }
.ptz-h1 { font-size: 1.5rem; font-weight: 800; }
.ptz-h2 { font-size: 1.2rem; font-weight: 800; margin-top: .6rem; }
.ptz-h3 { font-size: 1.05rem; font-weight: 700; }
.ptz-sub { color: var(--ptz-sub); }
.ptz-muted { color: var(--ptz-muted); font-size: .9rem; }
.ptz-kv { display:grid; grid-template-columns: auto 1fr; column-gap: 14px; row-gap: 2px; font-size: .95rem; }
.ptz-kv .k { color: var(--ptz-muted); }
.ptz-kv .v { font-weight: 600; font-variant-numeric: tabular-nums; text-align: right; }
.ptz-num { font-variant-numeric: tabular-nums; }
.ptz-pts { font-size: 1.15rem; font-weight: 800; padding: 2px 12px; border-radius: 10px; color: #fff; display:inline-block; }
.ptz-chip { font-size: .8rem; font-weight: 700; padding: 1px 7px; border-radius: 7px; color: #fff; display:inline-block; min-width: 1.6rem; text-align:center; }
.ptz-tok { width: 15px; height: 15px; border-radius: 4px; display:inline-block; margin: 1px; border: 2px solid #1d4ed8; }
.ptz-tok.used { background:#1d4ed8; }
.ptz-tok.credit { border-color:#ea580c; }
.ptz-tok.credit.used { background:#ea580c; }
.ptz-tok.infl { border-color:#7c3aed; background:#7c3aed; }
.ptz-stage { border-radius: 12px; padding: 6px 10px; border: 2px solid var(--ptz-line); background: #fff; min-width: 150px; }
.ptz-stage .ptz-kv .v { white-space: nowrap; }
.ptz-stage.now { border-color: #1d4ed8; background: #eff6ff; }
.ptz-section { border-top: 2px solid var(--ptz-line); padding-top: .4rem; margin-top: .8rem; scroll-margin-top: 90px; }
.ptz-sec-no { background:#1d4ed8; color:#fff; border-radius: 50%; width: 1.7rem; height: 1.7rem; display:inline-flex;
              align-items:center; justify-content:center; font-weight:800; margin-right:.5rem; }
.ptz-bar { height: 12px; border-radius: 6px; background: #e5e7eb; overflow: hidden; display:flex; }
.ptz-bar > div { height: 100%; }
.ptz-table td, .ptz-table th { padding: 4px 8px; text-align: right; font-variant-numeric: tabular-nums; }
.ptz-table td:first-child, .ptz-table th:first-child { text-align: left; }
.ptz-table th { background: #f3f4f6; font-weight: 700; }
.ptz-table tr { border-bottom: 1px solid var(--ptz-line); }
.ptz-table { border-collapse: collapse; width: 100%; font-size: .95rem; }
.ptz-insight { border-left: 4px solid #2563eb; background: #eff6ff; padding: 6px 10px; border-radius: 6px; }
.q-tab__label { font-size: .9rem; font-weight: 700; }
.ptz-ctl .q-btn { min-width: 44px; min-height: 44px; }
@media (max-width: 600px) { .ptz-big { font-size: 1.35rem; } .ptz-hide-sm { display:none; } }
</style>
"""

# Remember the scroll position when a control is pressed; after the server re-renders the cards it is restored, so
# the page does not jump (browsers may otherwise "anchor" the scroll position to re-created elements).
SCROLL_JS = """
<script>
(function () {
  let y = null, tDown = 0, tUser = 0;
  document.addEventListener("pointerdown", () => { y = window.scrollY; tDown = Date.now(); }, true);
  // the user scrolled after the click: do not pull the page back
  for (const ev of ["wheel", "touchmove", "keydown"]) document.addEventListener(ev, () => { tUser = Date.now(); }, true);
  window.ptzKeepScroll = function () {
    if (y === null || tUser > tDown) return;
    const target = y;
    const fix = () => { if (Math.abs(window.scrollY - target) > 1) window.scrollTo(0, target); };
    requestAnimationFrame(fix); setTimeout(fix, 80);
  };
})();
</script>
"""


def points_color(p: int) -> str:
    return POINT_COLORS[max(0, min(5, int(p)))]
