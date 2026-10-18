# ⚡ Zero45 – Energy transition planning game (Germany 2030–2045)

*Deutsche Version: [README.de.md](README.de.md)*

A planning game for groups: in four stages, teams build an electricity system for Germany that is
**reliable**, **climate-neutral** and **affordable**. Each stage is simulated with a real
electricity market model (PyPSA + HiGHS) for all 8,760 hours of a year. The game runs in German or English –
chosen per browser (see "Language" below). It runs on one laptop in the room, without internet.

The game idea is based on **“Path to Zero”** by Jesse D. Jenkins and the Princeton ZERO Lab. Zero45 is an
independent, unofficial adaptation with its own model and German data; it is not affiliated with or endorsed by
Princeton University (see [Credits](#credits)).

> **Please read:** Zero45 is a learning game, not a forecast – see [What the game is and isn't](#what-the-game-is-and-isnt)
> and the [Disclaimer](#disclaimer). Free software under the [GPL-2.0-or-later](#license).

**Documents** (in [`docs/`](docs/), German and English): rules, quick reference, background for the game master,
cheat sheet for the game master.

---

## Quick start

### 1. Once: installation
Only needed on the game master's computer – the teams only need a browser.

Get the game: on GitHub click **Code → Download ZIP** and unpack it, or `git clone` the repository.

**Windows** (PowerShell in the game folder):
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```
**Mac/Linux**:
```bash
bash setup.sh
```
This installs [uv](https://docs.astral.sh/uv/) (Python package manager), its own Python and all
packages into the folder `.venv`. Takes 1–3 minutes, internet required. **After every update** of the
game folder, run the setup once more (with internet) – it then only installs what has changed.
Supported: Windows 10/11 (also on ARM laptops), macOS 14 or newer on Apple Silicon (not yet tested on a real Mac), Linux x86_64. On Intel Macs and
macOS 13, a few packages are not available pre-built: delete the line `no-build = true` in `pyproject.toml` (the setup
then builds them, which needs the Xcode Command Line Tools).
If uv is missing, the setup runs the official uv installer of Astral (fixed version 0.11.32, from astral.sh); it installs
uv into your user profile (`%USERPROFILE%\.local\bin` or `~/.local/bin`).

### 2. Play
| What | Windows | Mac/Linux |
|---|---|---|
| **Network mode**: group game (teams in the Wi-Fi) | `.\start_spiel.ps1` | `bash start_spiel.sh` |
| **Local mode**: this computer only, with single-player game | `.\start_spiel.ps1 -Local` | `bash start_spiel.sh --local` |
| Local mode, opens the single-player game directly | `.\start_spiel.ps1 -Solo` | `bash start_spiel.sh --solo` |

The single-player game is only available in local mode – so in network mode teams cannot start their own
games and use up computing power.

Options: `-Port 8000` / `--port 8000`, `-Password secret` / `--password secret`, `-Workers 3` / `--workers 3`.

If Windows refuses to run the script ("running scripts is disabled on this system" or a security warning for downloaded
files), start it like the setup: `powershell -ExecutionPolicy Bypass -File .\start_spiel.ps1` (applies to this call
only), or allow the scripts in the game folder once with `Unblock-File .\*.ps1`.

**Computing processes:** the number of simultaneous calculations is determined at start-up from the cores and the free
memory (up to ~1.2 GB per process; the window shows e.g. "Simulation processes: 2 (3.4 of 16 GB free …)"). With 12 GB of
memory and 3 cores or more there are at least 2. To force more: `.\start_spiel.ps1 -Workers 3` – if memory then runs
short, Windows swaps to disk and it gets slower, but nothing is lost. The game server itself runs in addition to these
processes. If the port is taken, the game automatically uses the next free one and shows it.

**Game master:** in network mode, the page `/host` only opens on the game master's computer
itself (projector laptop). It is blocked for phones in the Wi-Fi. To run the game master page from
another device: `-HostRemote` / `--host-remote` – then be sure to set your own password
(`-Password <your own>`), because the default password `energiewende` is written in this guide.

At start-up the window shows the addresses, e.g.:
```
This computer:    http://localhost:8000
Mode:             network (teams in the Wi-Fi)
In the network:   http://192.168.1.23:8000/join   [WLAN]
In the network:   http://172.20.80.1:8000/join   [vEthernet (WSL)]   (virtual adapter/VPN – usually not for teams)
Game master:      http://localhost:8000/host   password: energiewende   (this computer only)
Other devices cannot connect?  See "Network tips" in the README (firewall, private network).
```
Give the teams the `/join` address of the Wi-Fi adapter (or show the QR code in the lobby).

### Language: German or English
At the bottom left of every page, the **EN / DE** button switches the language – per browser, without internet. The
choice is remembered (also after reloading or in the next stage). German and English teams can play in the same
game; numbers and scoring are identical. The game master (host page) has its own choice.

---

## How a game round works

1. The **game master** opens `/host` on the projector computer, logs in and sets timer, simulations
   per stage, budget, chance etc. in the **settings window** (can be saved as a preset) → "Create game".
2. The lobby shows a **QR code and PIN**. Teams scan with their phone or open `/join`, enter
   the PIN and a team name.
3. **Start stage** → build phase with timer. Teams spend build tokens, decide on existing
   power plants, use influence tokens and test with the **dispatch simulator**
   (normal weather year, limited number of attempts). On the right, "Your power plant fleet" shows the firm
   capacity: buffer with power plants only (grey), plus two traffic lights: with storage & flex (green from +10 %)
   and with storage, flex & interconnectors (green from +30 %). Details behind the info button. Gas turbines
   converted to hydrogen only count as firm as far as imports and a full storage can supply them for two
   weeks (length of the cold dark doldrums in the game). From the second test, the simulator shows
   what has changed since the last test. With 2 minutes left a notice appears and the timer flashes.
   At the start of each stage the game master shows in large print on the projector what is new (demand, coal, targets).
4. The game master ends the build phase (nothing happens automatically). Then the **same**
   random events are drawn for **all teams** (weather year, demand, disaster) and every
   portfolio is simulated.
5. **Results**: ranking, points per category, electricity mix and fleet comparison on the projector; every
   team sees its details with a chart and jump marks (dark doldrums, supply gap …) and a
   💡 tip: what cost the most points (e.g. the largest CO₂ source) and what changes in the next stage.
6. Next stage – 4 stages in total: NOW–2030, 2031–2035, 2036–2040, 2041–2045.

If a phone reloads the page, the team comes back automatically. Game states are saved continuously
in the folder `games/` and continued after a restart.

### Points (0–5 per category and stage, max. 60)
- **Security of supply:** hours with a supply gap (5 points at ≤ 3 h/year – the usual
  reliability standard in Germany and neighbouring countries).
- **Climate protection:** two conditions, the **worse** value counts:
  1. **CO₂-free share** as in the official statistics (EEG target): CO₂-free generation in Germany
     incl. exported green power, measured against demand; imports do not count, waste counts half
     (= (demand + exports − imports − fossil generation) ÷ demand, at most 100 %).
  2. **CO₂ emissions in Germany** (Mt/year, territorial as in the Climate Protection Act; exports offset
     nothing). The thresholds fall every stage to almost zero: 5 points at ≤ 70 / 45 / 25 / 8 Mt
     (2030: Climate Protection Act energy sector 108 Mt, of which electricity roughly 70; 2035: G7 pledge "power
     sector predominantly decarbonised"; 2040: coal exit 2038 and end of allowances in the EU emissions trading
     system around 2039/40; 2045: net greenhouse-gas neutrality – waste incineration alone emits ~5 Mt).
  5 points only when the political targets are reached (share 2030: 80 %, 2045 close to 100 %).
- **Affordability:** generation and storage costs in €/MWh – **excluding grids, levies, taxes**,
  so not comparable with the electricity price (investments as annuity, fixed and variable
  operating costs, fuel, CO₂ price, import costs minus export revenues, credit surcharge,
  costs of purchased influence tokens). Existing plants only enter with their fixed operating costs.
  The damage from unserved demand (10,000 €/MWh) is shown, but it no longer counts
  for the cost points – a supply gap only costs the supply points, not twice.
- **Deduction:** −2 points per new technology with public backlash in the last stage.
- Shown (not scored): cumulative CO₂ emissions in Gt, CO₂ per kWh (g/kWh, as published by the German
  Environment Agency UBA; additionally including the CO₂ of imports).

### Game mechanics
- **Build tokens**: 1 token = €10 bn investment (adjustable), 18 / 18 / 17 / 17 per stage – more
  at the beginning, like the real investment need (own estimate for the EEG expansion path of wind and PV: ≈ €204 / 157 / 120 / 74 bn).
  How many GW a token buys follows from the real costs (e.g. ~7 GW onshore wind, ~21 GW
  ground-mounted PV). Credit tokens possible (+20 % costs).
- **Existing power plants** (coal, gas, biomass; run-of-river always runs): keep running with a slider
  or retire permanently. Coal follows the legal phase-out path (Coal Phase-out Act, KVBG) and, as long as it is
  kept, runs in every hour at at least 15 % output (district heating, open-pit mining logistics); it can
  change its output by only 40 % per hour. Whoever keeps e.g. 10 GW generates at least ~13 TWh
  of coal power per year.
- **Fixed plants** (neither expandable nor retirable, with a fixed schedule): pumped hydro 9.9 GW
  (energy for about 6 h at full power), existing large batteries 3.7 GW (about 1 h, age out by
  2045; home batteries not included),
  waste incineration 1.9 GW (always running, half renewable), oil & other conventional 4.8 GW
  (oil, mine gas etc.; until 2035, retired from 2040) and grid and capacity reserve (11.1 GW until 2035, then
  3.6 GW; only in scarcity, 500 €/MWh).
- **Old plants**: today's wind and solar plants go offline step by step (onshore wind
  ~25 years: ~30 % left in 2045; solar ~30 years: ~65 % left in 2045; offshore ~30 years). The tiles
  show the decline to the next stage. Old wind turbines have a weaker profile (Ø ~20 %
  onshore, ~34 % offshore); new ones ~26–29 % and ~45 % (offshore incl. wake losses in the wind farm cluster).
- **New gas turbines** (H₂-ready, ~41 % efficiency, ~640 €/kW): cheap reserve, emit CO₂.
- **Battery storage**: energy for 4 hours at full power (4 GWh per GW), ~92 % efficiency for charging and discharging combined.
- **Biomass flexibilisation**: more capacity for the same annual energy, at most up to
  three times the capacity of the biomass kept.
- **Hydrogen** – three building blocks, expandable separately: **electrolysis** (~1,900 €/kW, 62–68 %,
  25 years, ~5 GW per token; runs only on the German green-power surplus of the respective hour – green
  hydrogen, no imported or fossil power), **hydrogen storage** in salt caverns (~2.7 €/kWh H₂, 100 years,
  ~3.7 TWh H₂ per token) and **gas turbines converted to H₂** (conversion of the newly built
  gas turbines, 120 €/kW without a token, ~41 %; afterwards hydrogen only, no natural gas). Round trip ≈ 25 %.
  Conversion is only possible when electrolysis and storage are built or planned in the stage (or imports
  come via the hydrogen grid). Each is unlocked from the following stage: "Hydrogen demonstration
  programme" → electrolysis, storage, conversion; "Hydrogen grid & imports" → storage, conversion,
  imports (no electrolysis). The game shows
  how many days the full storage supplies the H₂ turbines and warns when a building block is missing.
- **Imports & exports**: interconnectors to the neighbouring countries (25 / 28 / 32 / 35 GW, based on the
  TYNDP; +10 GW with "European grid expansion"). Availability, price and CO₂ of imports follow the
  scarcity in the neighbouring countries hour by hour (from their weather and demand, TYNDP): in a Europe-wide
  dark doldrums imports are scarce and expensive. The neighbours buy German power when they need it, and take
  up to 8 GW of surplus at any time (hydro storage, electrolysis, heat). A storage abroad
  (hydropower in Norway and the Alps) takes surplus and returns it later at a higher price.
  Import costs and export revenues enter the costs; the CO₂ of imports is shown separately
  (not in the German balance, as in the official statistics).
- **Flexible demand** (only with an influence token, from the following stage): electric cars and heat pumps
  shift demand within a day (5 / 10 / 15 / 20 GW, energy for 4 h at full load), industry cuts back in
  scarcity (4 / 6 / 8 / 10 GW, 300 €/MWh, at most 200 full-load hours per year). Without the token there is
  no demand flexibility.
- **Influence tokens**: climate resilience, accelerated innovation, hydrogen demonstration programme,
  hydrogen grid & imports (pipeline H₂ for converted gas turbines from 2035: 15 / 30 / 45 GW H₂
  ≈ 6 / 12 / 18 GW electricity, at 140 / 125 / 110 €/MWh H₂ ≈ 4.2 / 3.8 / 3.3 €/kg – assumption within the ranges of EWI 2025 and Fraunhofer HYPAT 2024, see DATA_SOURCES.md), acceptance & participation,
  European grid expansion, flexible demand – each once per game. 2 at the start; more cost 2 build tokens each, the money
  counts as programme costs in the generation and storage costs.
- **Rules & overview**: page `/regeln` (link on the start page, "Rules" tab for the teams,
  "Show rules" button for the game master for the projector). All numbers come from the current
  game settings.
- **Chance**: weather year (normal 2008: 60 %, difficult 1995: 30 %, extreme winter 2009: 10 % –
  adjustable), demand shock, disasters
  (storm/flood, cold dark doldrums, heat/drought) – the same for all teams. Backlash
  and learning effects are team-specific.

---

## Data and assumptions

All numbers with sources are in `ptz/config/assumptions.yaml`; game parameters in
`ptz/config/game_default.yaml`.

| Area | Source |
|---|---|
| Wind and PV profiles (hourly) | ENTSO-E PECD 3.1 (TYNDP 2024), bidding zone DE00, weather years 1995/2008/2009 |
| Electricity demand (hourly) | TYNDP 2024 demand profiles (National Trends 2030/2040, Distributed Energy 2050), scaled to 560 / 760 / 875 / 925 TWh net electricity consumption excluding electrolysis (2030 according to the energy transition monitoring report 2025, afterwards middle path of the Grid Development Plan NEP 2037/2045), plus 6–7 % for grid losses and power plant own consumption (≈ 600 / 810 / 930 / 980 TWh); the CO₂-free share refers to this, as the official statistics refer to gross electricity consumption |
| Imports/exports | Synthetic neighbouring market from TYNDP demand and PECD weather of the 12 neighbouring bidding zones and the EU electricity mix (TYNDP 2024 NT+); interconnector capacity according to the TYNDP NT+ results, storage and offtake of the neighbours calibrated to the TYNDP trade volumes (see section 8 of the background document in `docs/`) |
| Gas turbines, electrolysis, cavern | PyPSA technology-data (OCGT, electrolysis, hydrogen storage underground), EUR 2025 |
| Run-of-river | TYNDP 2024 hydro inflows (PEMMDB DE00) |
| Fuel and CO₂ prices | TYNDP 2024 commodity prices (IEA WEO 2022 APS), from EUR 2021 to EUR 2025 with factor 1.18 (Destatis CPI). CO₂ price 134 / 154 / 173 / 186 €/t – well above the level of autumn 2026 (EU ETS ~80–90 €/t) |
| Emission factors | TYNDP 2024 CO₂ emission factors |
| Technology costs | PyPSA technology-data (mainly Danish Energy Agency technology data), EUR 2025 |
| Starting capacities | Federal Network Agency (BNetzA) power plant list (as of 26 June 2026); PV split 66 % rooftop / 34 % ground-mounted (Solarserver, Feb. 2026) |
| PV yields | One PECD profile; ground-mounted PV ×1.10 (~975 full-load hours), rooftop PV as PECD (~885 h) – assumption based on Fraunhofer ISE "Recent facts about photovoltaics in Germany" |
| Pumped hydro | Power plant list (9.9 GW incl. plants in AT/LU connected to the German grid); storage duration of 6 h is an assumption |

**Weather years:** the analysis `ptz/data/processed/weather_check.csv` shows: 2008 is the
mildest of the three years, 1995 more difficult (less wind, largest deficit over two weeks), 2009 extreme (very cold
winter, weakest wind week, highest peak and residual load – occurs roughly every 10–20 years). Hence: normal 2008 (60 %), difficult 1995 (30 %), extreme 2009 (10 %). The simulator in the
build phase always calculates with the normal year.

**Simplifications** (belong in the debriefing): Germany as one node without
grid bottlenecks; neighbouring countries only as a simplified market (no full European model);
perfect foresight of the model over the year; no unit commitment with
on/off states (coal as one block: min. 15 % output, ramp 40 % per hour); flexible demand only via the influence token and smaller than in the official studies; biomass can shift its
annual energy freely; existing gas power plants do not age; one PV profile for rooftop and
ground-mounted plants; reservoir hydropower (0.8 GW) not modelled; hydrogen only for electricity
(hydrogen imports only via the influence card with fixed capacity and price, no demand from industry or transport); home batteries not modelled;
coal as one block (lignite and hard coal together). Values marked "ASSUMPTION"
in `assumptions.yaml` are our own settings without a direct source.

**Supply gaps:** a linear model with storage can distribute a gap arbitrarily across hours.
So that the number of gap hours is unambiguous, unserved demand in
hours with higher demand is valued minimally (up to 1 %) cheaper – the gap then ends up in
the peak hours. The cost display always uses the full 10,000 €/MWh.

### Regenerating the data
Put the raw data (TYNDP/PECD/BNetzA, approx. 1.4 GB) in the folder `raw/`, then:
```bash
uv run --frozen python -m ptz.data.build_inputs               # everything (neighbouring market takes a few minutes)
uv run --frozen python -m ptz.data.build_inputs --neighbours  # only the import/export data
```
The processed data (`ptz/data/processed/`, approx. 1 MB) are already included – the raw data are not
needed for the game.

---

## Network tips for the game day
- **Other devices cannot connect?** Most common causes:
  1. Windows firewall prompt cancelled at the first start → Windows blocks Python. Fix: Control Panel → Windows
     Defender Firewall → "Allow an app or feature through Windows Defender Firewall" → "Change settings" → tick
     **Private** for the "python" entries (the ones in the uv folder of your user profile).
  2. The Wi-Fi is classified as "Public" in Windows. Fix (only for your own Wi-Fi/hotspot): Settings → Network &
     Internet → properties of the network → "Private network". The start script warns when a network is "Public".
  3. Wrong address: VPN active or virtual adapters (WSL, Hyper-V, VirtualBox). The
     start-up output shows the adapter name for every address – take the Wi-Fi address.
  4. The Wi-Fi itself isolates devices from each other (guest Wi-Fi, eduroam, corporate Wi-Fi) → own
     router or phone hotspot.
- Most reliable: **own router or phone hotspot**, game master computer and all teams
  in the same Wi-Fi. University/guest Wi-Fi networks (e.g. eduroam) often block connections between devices.
- At the first start Windows asks about the firewall → "Allow access" **only for private
  networks** (not "public"). If necessary, in PowerShell as administrator:
  `New-NetFirewallRule -DisplayName "Zero45 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Profile Private -Action Allow`
  and remove it again after the game day: `Remove-NetFirewallRule -DisplayName "Zero45 8000"`.
  Classify your own hotspot/router network as "Private" in Windows.
- Computing power: one year takes approx. 10–20 s per team; several teams run in parallel on all
  processor cores (up to ~1.2 GB of memory per calculation; the game limits the number of parallel
  calculations automatically by cores and free memory). A laptop with 8 cores and 16 GB handles
  ~10 teams in a few minutes.

## Security (short version)
- **Installation:** all of the roughly 100 packages come from PyPI and are installed with `uv sync --frozen` exactly in the
  versions from `uv.lock`, each with a SHA-256 checksum. Only pre-built
  packages (wheels) are installed – enforced by `no-build = true` in `pyproject.toml` –, so nothing is compiled or
  executed during installation. If a wheel were ever missing, the setup stops with an error instead. New
  versions are only taken after one week (`exclude-newer` in `pyproject.toml`), because
  tampered releases are usually discovered within a few days. Everything ends up in the
  project folder (`.venv`) or with uv in the user folder – no administrator rights needed. uv
  uses its own Python (not the one from the Microsoft Store or an existing system Python).
- **Participants** only need a browser. The pages load nothing from the internet (all
  scripts come from the game master's computer); nothing is downloaded or installed and
  no account is created. Only a session cookie is stored (team membership and language).
  Team names are cleaned and shown as text everywhere.
- **Game master computer:** the server only provides the game pages (no file sharing,
  no uploads, no commands). In network mode it can be reached by everyone in the same Wi-Fi –
  therefore use your own hotspot/router network and stop the server after the game (Ctrl+C).
- The connection is unencrypted (HTTP in the local network). So do not use real names or
  passwords as team names.

## For developers
```
ptz/config/      Assumptions with sources (assumptions.yaml), game parameters (game_default.yaml)
ptz/data/        Data pipeline (build_inputs.py) and processed data
ptz/engine/      PyPSA model (model.py): dispatch, imports/exports, key figures
ptz/game/        Game rules, chance, ageing, points (core.py); runner.py (simulation, hints)
ptz/server/      Web interface (NiceGUI): app.py (start, pages), runtime.py (game states,
                 parallel simulation), host.py, player.py, rules.py (/regeln), charts.py, theme.py
ptz/i18n.py      Language switch: tr("German text {0}", value) translates at display time; English in i18n_en.py
                 (key = original German text). New text → add it to i18n_en.py; tests/test_i18n.py
                 reports missing translations.
ptz/calibration/ Bots for calibration
tests/           uv run --frozen pytest
```
Code comments, console output, setup and network scripts are in English; the web interface switches between German and English. The German texts in `tr("…")` and in the label tables are the translation keys and must not be translated.
The Python package is called `ptz` for historical reasons (working title of the project).

### Updating dependencies (security fixes)
`uv.lock` pins every package version, so a later installation gets exactly the same versions – also when newer
versions with security fixes exist. Updates therefore happen only when the repository is updated:

- **Get notified:** in the GitHub repository, enable *Dependabot alerts* (Settings → Advanced Security). GitHub reads
  `uv.lock` and sends an e-mail when a used version has a known vulnerability.
- **Update** (when there is an alert, or e.g. before a new workshop season):
  1. In `pyproject.toml`, set `exclude-newer` to a date about one week ago (cooldown against freshly published,
     possibly tampered releases) and remove or update the exception in `exclude-newer-package`.
  2. Run `uv lock --upgrade`, then `uv sync --frozen` and `uv run --frozen pytest`.
  3. Play one stage as a test, then commit `pyproject.toml` and `uv.lock`.

  If a new version is only available as source code (no pre-built wheel), `uv sync` stops with an error because of
  `no-build = true`; keep the previous version in that case (e.g. `uv lock --upgrade-package <other packages>`).

---

## What the game is and isn't

Zero45 is a **learning game**. It makes the trade-offs of the energy transition tangible – security of supply,
climate protection and costs, under uncertainty – and is meant to start discussions. It is **not a forecast and not a
policy recommendation**. Please keep the following in mind when you discuss results:

- **Costs** cover only generation and storage. Grids, taxes, levies, grid fees and retail margins are missing, so the
  game's €/MWh cannot be compared with electricity prices, and total costs are far below whole-system studies.
- **Model:** Germany as one node ("copper plate", no grid bottlenecks), perfect foresight over the year, one weather
  year per stage, no power plant outages. Power plants (except coal) can start instantly and have no minimum output.
  Supply gaps are therefore rather a lower bound.
- **Simplified:** neighbouring countries as one synthetic market, hydrogen only for electricity, flexible demand only via
  an influence card, no nuclear power and no CCS (see "Simplifications" above).
- **Data and assumptions** reflect official sources as of 2026 (TYNDP 2024, BNetzA, NEP, PyPSA technology-data) and will
  age. Every value and its source is in `ptz/config/assumptions.yaml`; own settings are marked `ASSUMPTION`.
- **Chance** (weather year, demand, disasters, backlash) decides a lot in a single game – as in reality.

A longer discussion (calibration, comparison with official scenarios, questions and answers) is in the background
document in `docs/`.

## Disclaimer

Zero45 is provided **"as is", without warranty of any kind**, express or implied (see sections 11 and 12 of the
[GPL](LICENSE)). **Use it at your own risk.** To the extent permitted by law, the authors are not liable for any
damage arising from its use, including damage to computers or other devices, loss of data, network or security
problems, or decisions based on the game's results.

Please note in particular:
- The setup installs software (uv, a Python version and about 100 packages from PyPI) into the game folder and into
  your user profile. It needs no administrator rights.
- If you create a firewall rule by hand (see "Network tips"), remove it again after the game day.
- While the game runs, every device in the same network can reach the game pages, and the connection is unencrypted.
  Use your own router or hotspot and stop the server after the game.
- A simulation needs up to ~1.2 GB of memory per process; on weak laptops reduce the number of processes (`-Workers`).
- The game's results are no legal, financial, investment or policy advice.

## Credits

- **Original game:** “Path to Zero – The Electricity Decarbonization Game”, created and designed by
  [Jesse D. Jenkins](https://mae.princeton.edu/people/faculty/jenkins), developed by the
  [Princeton ZERO Lab](https://zero.lab.princeton.edu/) and the Princeton Research Software Engineering Group,
  <https://github.com/PrincetonZEROLab/Path-to-Zero>, licensed under GPL-2.0.
  Zero45 adopts the game concept (stages, build tokens, influence ("shaping") tokens, social backlash, shared chance,
  scoring on reliability, clean energy and cost, the stage board) and some mechanics and parameters (backlash risk
  levels, effects of the resilience and acceptance cards). The code (Python instead of Julia), the electricity market
  model, the German and European data, the neighbouring market, hydrogen, the web interface and the bilingual version
  are new. No code from the original was copied.
- **Data:** ENTSO-E and ENTSOG (TYNDP 2024, PECD 3.1, CC BY 4.0), Bundesnetzagentur (Kraftwerksliste, Datenlizenz
  Deutschland), PyPSA technology-data, Danish Energy Agency and others – details and attribution in
  [DATA_SOURCES.md](DATA_SOURCES.md).
- **Software:** [PyPSA](https://pypsa.org), [linopy](https://github.com/PyPSA/linopy), [HiGHS](https://highs.dev),
  [NiceGUI](https://nicegui.io), [Plotly](https://plotly.com/python/), pandas, NumPy, [uv](https://docs.astral.sh/uv/)
  and many more open-source packages (MIT, BSD, Apache and MPL licences).
- **Development:** Manuel Lerschmacher. The code and documents were written with substantial help from the AI
  assistant Claude (Anthropic); design decisions, testing in workshops and responsibility lie with the author.

## How to cite

If you use Zero45 in teaching or research, please cite it – GitHub shows a "Cite this repository" button based on
[CITATION.cff](CITATION.cff). Please also cite the original game “Path to Zero” and the data sources.

## License

Copyright (C) 2026 Manuel Lerschmacher

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU General Public License](LICENSE)
for more details.

In short: you may use, copy, change and pass on Zero45 freely, also commercially. If you pass on a changed version,
it must again be under the GPL with its source code, and the copyright and credit notices must be kept.

The data in `ptz/data/processed/` keep their own licences (CC BY 4.0 and Datenlizenz Deutschland – Namensnennung);
see [DATA_SOURCES.md](DATA_SOURCES.md).
