# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Zero45 – energy transition game (based on the game idea of "Path to Zero", Princeton ZERO Lab)."""
import os as _os
import platform as _platform

# Windows on ARM: the x64 Python runs under emulation and reports the machine as ARM64, so Polars (used by linopy)
# cannot read the CPU flags and refuses to load ("unknown feature flag: 'sse3'"). The emulator supports the SSE4.2
# level of Polars' "compat" runtime (installed on Windows via pyproject.toml), so the check is skipped there.
if _os.name == "nt" and _platform.machine().lower() in ("arm64", "aarch64"):
    _os.environ.setdefault("POLARS_SKIP_CPU_CHECK", "1")
