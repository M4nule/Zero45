# Data sources and licences

The **code** of Zero45 is licensed under GPL-2.0-or-later (see [LICENSE](LICENSE)).
The **data** used by the game come from third parties and keep **their own licences**. They all allow free use,
redistribution and modification, but require attribution. If you redistribute Zero45 or the data files, keep this
file with them.

## 1. Processed data in this repository (`ptz/data/processed/`)

These files are derived from the raw data listed in section 2 by `ptz/data/build_inputs.py`.

| File | Derived from | Licence of the source | Changes made |
|---|---|---|---|
| `pecd_2030.csv.gz`, `pecd_2040.csv.gz` | ENTSO-E PECD 3.1 (TYNDP 2024), bidding zone DE00, target years 2030/2040, climate years 1995/2008/2009: onshore wind, offshore wind, solar PV capacity factors | CC BY 4.0 | Selected zone, technologies and climate years; clipped to 0–1; rounded |
| `demand_mw.csv.gz` | ENTSO-E/ENTSOG TYNDP 2024 demand profiles (National Trends 2030/2040, Distributed Energy 2050), Germany | CC BY 4.0 | Shape only; intermediate years as means of two profiles; scaled to the annual demand of the game (see `ptz/config/assumptions.yaml`) |
| `ror.csv.gz` | ENTSO-E TYNDP 2024 hydro inflows (PEMMDB DE00, 2030), run-of-river | CC BY 4.0 | Converted to an hourly capacity factor |
| `neighbours_2030.csv.gz`, `neighbours_2040.csv.gz` | TYNDP 2024 demand profiles and PECD 3.1 of the 12 neighbouring bidding zones (AT00, BE00, CH00, CZ00, DKE1, DKW1, FR00, LUG1, NL00, NOS0, PL00, SE04) | CC BY 4.0 | Aggregated into one synthetic neighbouring market (hourly residual "fossil need"); calibrated to TYNDP trade volumes |
| `weather_check.csv` | Computed from the files above | CC BY 4.0 (derived) | Statistics per climate year |
| `meta.json` | TYNDP 2024 commodity prices; BNetzA power plant list (capacities per fuel) | CC BY 4.0; Datenlizenz Deutschland – Namensnennung | Selected values; fuel/CO₂ prices of 2030/2040/2050 |

**Attribution for the TYNDP / PECD data:** “Source: ENTSO-E and ENTSOG, TYNDP 2024 Scenarios (including Pan-European
Climate Database PECD 3.1), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Data were
selected, aggregated, scaled and rounded for Zero45.” Download: https://2024.entsos-tyndp-scenarios.eu/download/

**Attribution for the BNetzA data:** “Datenquelle: Bundesnetzagentur, Kraftwerksliste (Stand 26.06.2026),
Datenlizenz Deutschland – Namensnennung.” Download:
https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Versorgungssicherheit/Erzeugungskapazitaeten/start.html
(According to the BNetzA imprint, data in .xls/.xlsx/.csv format are licensed under “Datenlizenz Deutschland –
Namensnennung” unless stated otherwise: https://www.bundesnetzagentur.de/DE/Service/Impressum/start.html; licence texts:
https://www.govdata.de/lizenzen)

## 2. Raw data (not in this repository, ~1.4 GB)

Only needed to regenerate the processed data (`raw/` folder, see README).

| File in `raw/` | Source |
|---|---|
| `PECD_3.1+pre-built.0.1.zip` | ENTSO-E/ENTSOG TYNDP 2024 Scenarios – Pan-European Climate Database 3.1 |
| `Demand-Profiles.zip` | TYNDP 2024 Scenarios – demand profiles |
| `Hydro-Inflows.zip` | TYNDP 2024 Scenarios – hydro inflows (PEMMDB) |
| `Prices.zip` | TYNDP 2024 Scenarios – commodity prices (“2023 06 22 TYNDP 2024 Commodity prices Final.xlsx”) |
| `Kraftwerksliste.xlsx` | Bundesnetzagentur, Kraftwerksliste (as of 26 June 2026) |

## 3. Numbers in `ptz/config/assumptions.yaml`

Individual numbers (costs, efficiencies, lifetimes, targets) are taken from published sources and cited next to each
value in the file. Values marked `ASSUMPTION` are our own settings without a direct source.

| Source | Used for | Licence / terms |
|---|---|---|
| PyPSA technology-data (mainly based on the Danish Energy Agency technology catalogues), EUR 2025 | Investment and operating costs, efficiencies, lifetimes | Project code GPL-3.0; only individual numbers are used, no code. Please cite: https://github.com/PyPSA/technology-data |
| Danish Energy Agency, Technology Data catalogues | (via PyPSA technology-data) | Published by the Danish Energy Agency and Energinet |
| ENTSO-E/ENTSOG TYNDP 2024: commodity prices (file `Prices.zip`, based on the IEA WEO 2022 APS price path), CO₂ emission factors v2, interconnector capacities | Fuel and CO₂ prices (converted from EUR 2021/GJ to EUR 2025/MWh: ×3.6 and ×1.18; 2035/2045 interpolated), emission factors, interconnectors, neighbouring countries | CC BY 4.0 |
| Bundesnetzagentur, Kraftwerksliste | Existing power plant fleet | Datenlizenz Deutschland – Namensnennung |
| Solarserver (Feb. 2026, based on Marktstammdatenregister data); Marktstammdatenregister (MaStR) | Split of rooftop/ground-mounted PV; size of large batteries | Individual numbers cited; MaStR data: Datenlizenz Deutschland – Namensnennung 2.0 |
| Destatis, consumer price index | Conversion EUR 2021 → EUR 2025 (factor 1.18) | Datenlizenz Deutschland – Namensnennung 2.0 |
| Netzentwicklungsplan Strom 2037/2045 (2025), Monitoringbericht Energiewende 2025 | Annual demand, flexibility comparison | Publications; individual numbers cited |
| Kohleverstromungsbeendigungsgesetz (KVBG), Klimaschutzgesetz (KSG, Anlage 2a: energy sector 108 Mt CO₂-eq. in 2030), EEG (80 % renewables in 2030) | Coal phase-out path (2030: 8 GW hard coal + 9 GW lignite; 2035: linear interpolation towards the 2038 end date, own assumption), CO₂ and renewable targets | Laws (official works, § 5 UrhG) |
| G7 Leaders' Communiqué, Elmau 2022 | 2035 target: “fully or predominantly decarbonised power sectors” | Publication |
| ACER, reliability standards of the member states (status 2022) | Germany: 2.77 h loss of load expectation per year – basis of the 3-hour threshold | Publication |
| Umweltbundesamt (2026): CO₂ emissions per kWh of electricity | Comparison value 344 g/kWh (2025, estimate) | Publication |
| Fraunhofer ISE (“Aktuelle Fakten zur Photovoltaik”; Stromgestehungskosten 2024: 4.1–9.2 ct/kWh for onshore wind and ground-mounted PV), Fraunhofer IWES, Solarserver | Single comparison values (PV yields, wake losses, costs of new plants) | Publications; individual numbers cited |
| IMK / Hans-Böckler-Stiftung (2024), investment needs of the power grids | Comparison only: ~651 bn € grid expansion until 2045 (not part of the game's costs) | Publication |
| EWI (2025): “Global production and delivery costs of green hydrogen”; Fraunhofer ISI/ISE/IEG, HYPAT “Global Hydrogen Atlas” (2024); Schmitz et al. (2024), Int. J. Hydrogen Energy 63, 566–579 | Hydrogen import price of the card “Hydrogen grid & imports”: 140 / 125 / 110 €/MWh H₂ (2035 / 2040 / 2045) – own assumption within the ranges of these studies (pipeline imports 2030 ~150 €/MWh; 3.5–6.5 €/kg in 2030, 2–4.5 €/kg in 2050) | Publications; individual numbers cited |
| EU ETS price (ICE, October 2026) | Comparison only: CO₂ price ~80–90 €/t | Market data |

Individual facts and numbers are not protected by copyright; the sources are cited for transparency and so that
the assumptions can be checked and updated.

## 4. Original game

The game concept is based on “Path to Zero – The Electricity Decarbonization Game” (Princeton ZERO Lab,
GPL-2.0). See the Credits section of the [README](README.md#credits). No input data (time series, costs, capacities)
from the original game are used; some game parameters were adopted (backlash risk levels, influence card effects).
