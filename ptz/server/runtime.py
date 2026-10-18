# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""In-memory game registry with persistence and asynchronous (process-pool) stage resolution."""
from __future__ import annotations

import asyncio
import logging
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from ptz.game import core, runner
from ptz.i18n import tr

log = logging.getLogger("ptz")
GAMES_DIR = Path(__file__).resolve().parents[2] / "games"


_POOL: ProcessPoolExecutor | None = None
WORKERS = {"n": None}


GB_PER_WORKER = 1.25   # peak RAM of one solver process (2045 with storage abroad, flexibility, hydrogen: ~1.1 GB)


def default_workers() -> int:
    """Parallel solver processes: limited by cores and by the memory that is free when the server starts.
    Override: environment variable PTZ_WORKERS or --workers (start_spiel.ps1 -Workers 3)."""
    if os.environ.get("PTZ_WORKERS"):
        return max(1, int(os.environ["PTZ_WORKERS"]))
    cores = os.cpu_count() or 2
    n = max(1, min(cores - 1, 6))
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_gb, total_gb = vm.available / 1e9, vm.total / 1e9
        by_mem = int((free_gb - 0.5) / GB_PER_WORKER)
        floor = 2 if (total_gb >= 12 and cores >= 3) else 1   # 2 processes rarely peak at the same moment
        n = max(1, min(n, max(by_mem, floor)))
        if not getattr(default_workers, "logged", False):
            default_workers.logged = True
            log.info("Simulation processes: %d (%.1f of %.1f GB free, up to ~%.1f GB per process, %d cores) – more with "
                     "start_spiel.ps1 -Workers N", n, free_gb, total_gb, GB_PER_WORKER, cores)
    except Exception:  # psutil missing: trust the core count
        pass
    return n


def pool() -> ProcessPoolExecutor:
    global _POOL
    if _POOL is None:
        n = WORKERS["n"] or default_workers()
        WORKERS["n"] = n
        _POOL = ProcessPoolExecutor(max_workers=n, mp_context=multiprocessing.get_context("spawn"))
    return _POOL


async def run_job(fn, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(pool(), fn, *args)


class Runtime:
    """One running game plus caches that are not part of the saved state."""

    def __init__(self, state: dict):
        self.state = state
        self.version = 0
        self.lock = asyncio.Lock()
        self.dispatch: dict[tuple[str, int], pd.DataFrame] = {}   # resolved stage dispatch per team
        self.sim: dict[str, dict] = {}                             # last simulator result per team
        self.sim_running: set[str] = set()
        self.resolve_progress = (0, 0)

    @property
    def pin(self) -> str:
        return self.state["pin"]

    @property
    def folder(self) -> Path:
        return GAMES_DIR / self.pin

    def touch(self):
        self.version += 1
        try:
            core.save(self.state, GAMES_DIR)
        except Exception:  # never let a disk problem stop the game
            log.exception("could not save game %s", self.pin)

    # ------------------------------------------------------------------ dispatch storage
    def store_dispatch(self, tid: str, stage: int, disp: pd.DataFrame):
        self.dispatch[(tid, stage)] = disp
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(self.folder / f"{tid}_{stage}.npz", **{c: disp[c].to_numpy() for c in disp.columns})
        except Exception:
            log.exception("could not save dispatch")

    def get_dispatch(self, tid: str, stage: int) -> pd.DataFrame | None:
        key = (tid, stage)
        if key not in self.dispatch:
            f = self.folder / f"{tid}_{stage}.npz"
            if f.exists():
                z = np.load(f)
                self.dispatch[key] = pd.DataFrame({k: z[k] for k in z.files})
        return self.dispatch.get(key)

    # ------------------------------------------------------------------ actions
    async def simulate(self, tid: str) -> str | None:
        st = self.state
        team = st["teams"][tid]
        limit = st["cfg"]["simulations_per_stage"] + team.get("sims_extra", 0)
        if st["phase"] != "build":
            return tr("Der Simulator ist nur in der Bauphase verfügbar.")
        if team["sims_used"] >= limit:
            return tr("Keine Simulationen mehr in dieser Stufe.")
        if tid in self.sim_running:
            return tr("Simulation läuft bereits.")
        args = core.engine_args(st, tid, None)
        self.sim_running.add(tid)
        team["sims_used"] += 1
        self.touch()
        try:
            summary, disp = await run_job(runner.run_engine, args)
        except Exception as e:  # noqa: BLE001
            log.exception("simulation failed")
            team["sims_used"] -= 1
            return tr("Simulation fehlgeschlagen: {0}", e)
        finally:
            self.sim_running.discard(tid)
        if tid not in st["teams"] or st["phase"] != "build":   # team removed or build phase closed meanwhile
            return None
        ev = core.evaluate(st, tid, summary)
        old = self.sim.get(tid)
        prev = None
        if old and old["stage"] == st["stage"]:   # keep the key figures of the previous test for a comparison
            prev = {"points": old["eval"]["points"], "eur": old["eval"]["cost"]["eur_per_mwh"],
                    "co2": old["summary"]["co2_mt"], "share": old["summary"]["clean_share"],
                    "lole": old["summary"]["lole_hours"], "time": old["time"]}
        self.sim[tid] = {"summary": summary, "dispatch": disp, "eval": ev, "stage": st["stage"],
                         "cap": core.portfolio(st, tid), "time": time.time(), "prev": prev}
        self.touch()
        return None

    async def close_and_resolve(self):
        async with self.lock:
            st = self.state
            if st["phase"] != "build":
                return
            luck = core.close_stage(st)
            self.touch()
            tids = list(st["teams"])
            self.resolve_progress = (0, len(tids))
            jobs = [asyncio.create_task(run_job(runner.run_engine, core.engine_args(st, tid, luck))) for tid in tids]
            done = 0
            results = {}
            for tid, job in zip(tids, jobs):
                try:
                    results[tid] = await job
                except Exception:
                    log.exception("resolution failed for %s", tid)
                    results[tid] = None
                done += 1
                self.resolve_progress = (done, len(tids))
                self.version += 1
            for tid in tids:
                if results[tid] is None:
                    st["teams"][tid]["status"] = "Fehler"
                    continue
                summary, disp = results[tid]
                core.apply_stage_result(st, tid, summary)
                self.store_dispatch(tid, st["stage"], disp)
                st["teams"][tid]["status"] = "fertig"
            core.finish_resolution(st)
            self.sim.clear()
            self.touch()


REGISTRY: dict[str, Runtime] = {}


def create(cfg: dict, mode: str = "server") -> Runtime:
    st = core.new_game(cfg, mode=mode)
    while st["pin"] in REGISTRY:
        st = core.new_game(cfg, mode=mode)
    rt = Runtime(st)
    REGISTRY[rt.pin] = rt
    rt.touch()
    return rt


def get(pin: str) -> Runtime | None:
    return REGISTRY.get(str(pin))


def load_all():
    """Restore saved games after a restart (e.g. laptop crashed)."""
    if not GAMES_DIR.exists():
        return
    for f in GAMES_DIR.glob("*.json"):
        try:
            st = core.load(f)
            if st.get("version", 1) != core.STATE_VERSION:   # saved by an older game version: incompatible
                log.info("skipping %s (old game version)", f.name)
                continue
            if st.get("phase") == "resolving":  # interrupted resolution: reopen build phase
                st["phase"] = "build"
                for t in st["teams"].values():
                    t["submitted"] = False
                    t["status"] = "bearbeitet"
            REGISTRY[st["pin"]] = Runtime(st)
        except Exception:
            log.exception("could not load %s", f)
