# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Zero45 – energy transition game. Web server (NiceGUI).

Start:
    uv run python -m ptz.server.app                 # network mode (game master + teams in the Wi-Fi)
    uv run python -m ptz.server.app --local         # local mode: this computer only, with single-player game
    uv run python -m ptz.server.app --solo          # like --local, opens the single-player game directly
Options: --port 8000  --password <host password>  --host-remote (game master page from other devices too)
The single-player game (/solo) only exists in local mode, so teams in the network cannot start their own games.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import secrets
import socket
import sys

from fastapi import Request
from nicegui import app, context, run, ui
from starlette.middleware.base import BaseHTTPMiddleware

from ptz import i18n
from ptz.game import core
from ptz.server import host, player, rules, runtime
from ptz.i18n import tr

ARGS = {"password": os.environ.get("PTZ_PASSWORD", "energiewende"), "join_urls": [], "local": False,
        "host_remote": False, "own_ips": {"127.0.0.1", "::1"}}


def is_this_computer(request: Request) -> bool:
    ip = request.client.host if request.client else ""
    return ip in ARGS["own_ips"] or ip.startswith("127.")


def host_allowed(request: Request) -> bool:
    """In network mode the host pages only open on the game laptop itself (unless --host-remote)."""
    return ARGS["local"] or ARGS["host_remote"] or is_this_computer(request)


class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        resp = await call_next(request)
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        return resp


app.add_middleware(SecurityHeaders)


VIRTUAL_HINTS = ("vethernet", "virtualbox", "vmware", "wsl", "hyper-v", "docker", "veth", "br-", "tailscale",
                 "zerotier", "vpn", "tap", "tun", "utun", "loopback", "bluetooth", "npcap", "anyconnect", "wireguard")


def _default_route_ip() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))   # no packet is sent; only picks the outgoing interface
            return s.getsockname()[0]
    except OSError:
        return None


def lan_addresses() -> list[tuple[str, str, bool]]:
    """(interface name, IPv4, looks virtual/VPN) for all active interfaces; best candidate for teams first."""
    out = []
    try:
        import psutil
        stats = psutil.net_if_stats()
        for name, addrs in psutil.net_if_addrs().items():
            if name in stats and not stats[name].isup:
                continue
            for ad in addrs:
                ip = ad.address
                if ad.family == socket.AF_INET and not ip.startswith(("127.", "169.254.")):
                    out.append((name, ip, any(h in name.lower() for h in VIRTUAL_HINTS)))
    except Exception:
        pass
    default = _default_route_ip()
    if default and default not in [ip for _, ip, _ in out] and not default.startswith("127."):
        out.append(("Standardverbindung", default, False))
    # real adapters first; among them the one carrying the default route first
    out.sort(key=lambda x: (x[2], x[1] != default))
    return out


def lan_ips() -> list[str]:
    """Addresses teams can use (virtual/VPN adapters only if nothing else exists)."""
    addrs = lan_addresses()
    real = [ip for _, ip, virt in addrs if not virt]
    return real or [ip for _, ip, _ in addrs]


def page_frame(title: str = "Zero45"):
    """Common page setup; also fixes this browser's language for the page (stored per browser)."""
    lang = app.storage.user.get("lang", i18n.DEFAULT)
    if lang not in i18n.LANGS:
        lang = i18n.DEFAULT
    context.client.ptz_lang = lang
    ui.page_title(tr(title))
    ui.colors(primary="#1d4ed8")
    ui.query("body").style("background:#f5f7fb")

    def switch():
        app.storage.user["lang"] = "en" if lang == "de" else "de"
        ui.navigate.reload()
    ui.button("EN" if lang == "de" else "DE", icon="translate", on_click=switch).props(
        "dense no-caps unelevated size=sm color=white text-color=grey-9").classes("ptz-lang").style(
        "position:fixed;left:4px;bottom:4px;z-index:3000;border:1px solid #d1d5db;border-radius:8px;opacity:.9").tooltip(
        "Switch to English" if lang == "de" else "Auf Deutsch umschalten")


# ----------------------------------------------------------------------------- pages
@ui.page("/")
def index(request: Request):
    page_frame()
    ui.add_head_html(player.CSS)
    with ui.column().classes("w-full max-w-3xl mx-auto p-4 gap-4"):
        ui.label(tr("⚡ Zero45 – Energiewende-Spiel")).classes("text-2xl font-bold")
        ui.label(tr("Baue ein Stromsystem für Deutschland bis 2045: zuverlässig, klimaneutral und bezahlbar.")).classes("text-base")
        ui.button(tr("Spielregeln & Überblick"), icon="menu_book", on_click=lambda: ui.navigate.to("/regeln")).props(
            "outline")
        with ui.card().classes("w-full ptz-card"):
            ui.label(tr("Einem Spiel beitreten")).classes("text-lg font-bold")
            pin = ui.input(tr("Spiel-PIN")).props("inputmode=numeric").classes("w-48")
            ui.button(tr("Weiter"), on_click=lambda: ui.navigate.to(f"/join?pin={pin.value.strip()}")).props("color=primary")
        with ui.row().classes("gap-4 w-full"):
            if host_allowed(request):
                with ui.card().classes("ptz-card flex-1"):
                    ui.label(tr("Spiel leiten")).classes("text-lg font-bold")
                    ui.label(tr("Für die Spielleitung am Hauptrechner/Beamer.")).classes("ptz-muted")
                    ui.button(tr("Zur Spielleitung"), on_click=lambda: ui.navigate.to("/host")).props("outline")
            if ARGS["local"]:
                with ui.card().classes("ptz-card flex-1"):
                    ui.label(tr("Einzelspiel")).classes("text-lg font-bold")
                    ui.label(tr("Alleine spielen, ohne Spielleitung.")).classes("ptz-muted")
                    ui.button(tr("Einzelspiel starten"), on_click=lambda: ui.navigate.to("/solo")).props("outline")
        credits_line()


def credits_line():
    """Attribution of the original game and the licence (start page and rules page)."""
    ui.label(tr("Spielidee nach „Path to Zero“ von Jesse D. Jenkins und dem Princeton ZERO Lab · Freie Software (GPL-2.0-or-later) · Lernspiel, keine Prognose")).classes("ptz-muted text-xs mt-4")


@ui.page("/regeln")
def rules_page(pin: str = ""):
    page_frame("Spielregeln")
    ui.add_head_html(player.CSS)
    rt = runtime.get(pin) if pin else None
    cfg = rt.state["cfg"] if rt else core.default_config()
    stage = rt.state["stage"] if rt else 0
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-2"):
        rules.build_rules(cfg, stage)
        credits_line()


@ui.page("/join")
def join(pin: str = ""):
    page_frame("Beitreten")
    ui.add_head_html(player.CSS)
    rt = runtime.get(pin)
    with ui.column().classes("w-full max-w-md mx-auto p-4 gap-3"):
        ui.label(tr("⚡ Zero45 – Beitreten")).classes("text-xl font-bold")
        if not rt or rt.state["mode"] != "server":
            ui.label(tr("Kein laufendes Spiel mit dieser PIN gefunden.")).classes("text-red-700")
            p = ui.input(tr("Spiel-PIN"), value=pin)
            ui.button(tr("Erneut versuchen"), on_click=lambda: ui.navigate.to(f"/join?pin={p.value.strip()}"))
            return
        stored = app.storage.user.get(f"team_{pin}")
        if stored and stored.get("tid") in rt.state["teams"]:
            t = rt.state["teams"][stored["tid"]]
            ui.label(tr("Du bist bereits als Team „{0}“ angemeldet.", t['name']))
            ui.button(tr("Weiter zum Spiel"), on_click=lambda: ui.navigate.to(f"/play/{pin}")).props("color=primary")
            ui.button(tr("Als anderes Team beitreten"), on_click=lambda: (app.storage.user.pop(f"team_{pin}", None),
                                                                      ui.navigate.to(f"/join?pin={pin}"))).props("flat")
            return
        ui.label(tr("Spiel {0} | {1} Teams angemeldet", pin, len(rt.state['teams']))).classes("ptz-muted")
        why = core.can_join(rt.state)
        if why and rt.state["phase"] == "finished":
            ui.label(why).classes("text-orange-700")
            return
        name = ui.input(tr("Teamname")).props("maxlength=30 autofocus")

        def do_join():
            why = core.can_join(rt.state)
            if why:
                ui.notify(why, type="warning")
                return
            tid, secret = core.add_team(rt.state, name.value)
            if rt.state["phase"] == "build":
                core.reset_draft(rt.state, tid)
            app.storage.user[f"team_{pin}"] = {"tid": tid, "secret": secret}
            rt.touch()
            ui.navigate.to(f"/play/{pin}")
        ui.button(tr("Beitreten"), on_click=do_join).props("color=primary")
        if rt.state["stage"] > 0:
            ui.label(tr("Hinweis: Das Spiel läuft schon – neue Teams starten in der aktuellen Stufe.")).classes("ptz-muted")


@ui.page("/play/{pin}")
def play(pin: str):
    page_frame("Team")
    rt = runtime.get(pin)
    stored = app.storage.user.get(f"team_{pin}")
    if not rt or not stored or stored.get("tid") not in rt.state["teams"] \
            or rt.state["teams"][stored["tid"]]["secret"] != stored.get("secret"):
        ui.navigate.to(f"/join?pin={pin}")
        return
    player.build_player(rt, stored["tid"])


@ui.page("/solo")
def solo(neu: str = ""):
    page_frame("Einzelspiel")
    ui.add_head_html(player.CSS)
    if not ARGS["local"]:
        with ui.column().classes("w-full max-w-md mx-auto p-4 gap-2"):
            ui.label(tr("Das Einzelspiel ist im Netzwerk-Modus ausgeschaltet.")).classes("text-lg font-bold")
            ui.label(tr("Zum alleine Spielen den Server im lokalen Modus starten (start_spiel -Local bzw. --local).")).classes(
                "ptz-muted")
            ui.button(tr("Zur Startseite"), on_click=lambda: ui.navigate.to("/")).props("outline")
        return
    pin = app.storage.user.get("solo_pin")
    rt = runtime.get(pin) if pin and not neu else None
    if rt is None:
        with ui.column().classes("w-full max-w-4xl mx-auto p-4"):
            name = ui.input(tr("Dein Teamname"), value=tr("Mein Team")).classes("w-64")

            def create(cfg):
                cfg = {**cfg, "timer_minutes": [0] * cfg["stages"]}
                r = runtime.create(cfg, mode="solo")
                core.add_team(r.state, name.value)
                core.start_stage(r.state)
                r.touch()
                app.storage.user["solo_pin"] = r.pin
                ui.navigate.to("/solo")
            host.settings_form(create, solo=True)
        return
    tid = next(iter(rt.state["teams"]))
    player.build_player(rt, tid, solo=True)


@ui.page("/host")
def host_page(request: Request, neu: str = ""):
    page_frame("Spielleitung")
    ui.add_head_html(player.CSS)
    if not host_allowed(request):
        with ui.column().classes("w-full max-w-md mx-auto p-4 gap-2"):
            ui.label(tr("Die Spielleitung ist nur am Spielleitungs-Rechner erreichbar.")).classes("text-lg font-bold")
            ui.button(tr("Zur Startseite"), on_click=lambda: ui.navigate.to("/")).props("outline")
        return
    if not app.storage.user.get("host_ok"):
        with ui.column().classes("w-full max-w-sm mx-auto p-4 gap-2"):
            ui.label(tr("Spielleitung – Anmeldung")).classes("text-xl font-bold")
            pw = ui.input(tr("Passwort"), password=True, password_toggle_button=True)

            async def login():
                if secrets.compare_digest((pw.value or "").encode("utf-8"), ARGS["password"].encode("utf-8")):
                    app.storage.user["host_ok"] = True
                    ui.navigate.to("/host")
                else:
                    await asyncio.sleep(1.0)   # slows down guessing
                    ui.notify(tr("Falsches Passwort"), type="negative")
            pw.on("keydown.enter", login)
            ui.button(tr("Anmelden"), on_click=login).props("color=primary")
        return
    pin = app.storage.user.get("host_pin")
    rt = runtime.get(pin) if pin and not neu else None
    if rt is None:
        with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-2"):
            running = [r for r in runtime.REGISTRY.values() if r.state["mode"] == "server" and r.state["phase"] != "finished"]
            if running:
                ui.label(tr("Laufende Spiele fortsetzen")).classes("text-lg font-bold")
                for r in running:
                    def resume(r=r):
                        app.storage.user["host_pin"] = r.pin
                        ui.navigate.to("/host")
                    ui.button(tr("PIN {0} | Stufe {1} | {2} Teams", r.pin, r.state['stage'] + 1, len(r.state['teams'])),
                              on_click=resume).props("outline")
                ui.separator()

            def create(cfg):
                r = runtime.create(cfg, mode="server")
                app.storage.user["host_pin"] = r.pin
                ui.navigate.to("/host")
            host.settings_form(create)
        return
    def logout():
        app.storage.user.pop("host_ok", None)
        ui.navigate.to("/")
    with ui.row().classes("w-full max-w-7xl mx-auto px-3 justify-end"):
        ui.button(tr("Neues Spiel"), on_click=lambda: ui.navigate.to("/host?neu=1")).props("flat dense")
        ui.button(tr("Abmelden"), on_click=logout).props("flat dense")
    host.build_host(rt, ARGS["join_urls"])


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Zero45 – energy transition game")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--local", action="store_true", help="local mode: this computer only, with single-player game")
    ap.add_argument("--solo", action="store_true", help="like --local, opens the single-player game directly")
    ap.add_argument("--password", default=None, help="password for the game master page")
    ap.add_argument("--workers", type=int, default=None, help="number of parallel simulation processes (default: automatic)")
    ap.add_argument("--host-remote", action="store_true",
                    help="allow the game master page (/host) from other devices in the network (default: this computer only)")
    a = ap.parse_args()
    if a.password:
        ARGS["password"] = a.password
    local = a.local or a.solo
    ARGS["local"] = local
    ARGS["host_remote"] = a.host_remote
    addrs = lan_addresses()
    ARGS["own_ips"] |= {ip for _, ip, _ in addrs}
    host_ip = "127.0.0.1" if local else "0.0.0.0"
    port = free_port(host_ip, a.port)
    if port != a.port:
        print(f"\n  Note: port {a.port} is in use – using port {port} instead.")
    a.port = port
    ARGS["join_urls"] = [f"http://{ip}:{a.port}" for ip in lan_ips()] if not local else [f"http://localhost:{a.port}"]
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    runtime.load_all()
    print("\n  ⚡ Zero45 – energy transition game")
    print("  " + "─" * 50)
    print(f"  This computer:    http://localhost:{a.port}")
    print("  Mode:             " + ("local (with single-player game)" if local else "network (teams in the Wi-Fi)"))
    if not local:
        for name, ip, virt in addrs:
            note = "   (virtual adapter/VPN – usually not for teams)" if virt else ""
            print(f"  In the network:   http://{ip}:{a.port}/join   [{name}]{note}")
        if not addrs:
            print("  In the network:   no network connection found!")
        print(f"  Game master:      http://localhost:{a.port}/host   password: {ARGS['password']}"
              + ("" if a.host_remote else "   (this computer only)"))
        print("  Other devices cannot connect?  See \"Network tips\" in the README (firewall, private network).")
        if a.host_remote and ARGS["password"] == "energiewende":
            print("  WARNING: --host-remote with the default password – everyone in the network can log in as game master."
                  "\n           Set your own password: -Password <secret> / --password <secret>")
    print("  Quit: Ctrl+C\n")
    storage_secret = os.environ.get("PTZ_SECRET") or _secret_file()
    run.process_pool_start_method = "spawn"
    if a.workers:
        runtime.WORKERS["n"] = max(1, a.workers)

    async def warm():
        import asyncio
        from ptz.game.runner import warmup
        n = runtime.WORKERS["n"] or runtime.default_workers()
        try:
            await asyncio.gather(*[runtime.run_job(warmup) for _ in range(n)])
            logging.info("Rechenkerne bereit (%d)", n)
        except Exception:
            logging.exception("warm-up failed")

    def stop_pool():
        if runtime._POOL is not None:
            runtime._POOL.shutdown(wait=False, cancel_futures=True)
    app.on_startup(warm)
    app.on_shutdown(stop_pool)
    ui.run(host=host_ip, port=a.port, title="Zero45", reload=False, show=("/solo" if a.solo else local),
           storage_secret=storage_secret, language="de", favicon="⚡", show_welcome_message=False,
           reconnect_timeout=30)


def free_port(host_ip: str, port: int, tries: int = 20) -> int:
    """First port >= port that can be bound (8000 is sometimes taken by other dev servers)."""
    for p in range(port, port + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if os.name != "nt":   # like uvicorn; on Windows this flag would allow sharing a used port
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host_ip, p))
                return p
            except OSError:
                continue
    return port


def _secret_file() -> str:
    p = runtime.GAMES_DIR / ".secret"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(secrets.token_hex(16))
    return p.read_text().strip()


if __name__ in {"__main__", "__mp_main__"} and "pytest" not in sys.modules:
    if __name__ == "__main__":
        main()
