# SPDX-FileCopyrightText: 2026 Manuel Lerschmacher
# SPDX-License-Identifier: GPL-2.0-or-later
"""Language per browser (German default, English optional).

Texts stay German in the code; tr() looks up the English version in i18n_en.EN when the current viewer uses English.
Templates use positional placeholders ({0}, {1:.1f}) so that word order can change in the translation.
The language belongs to the NiceGUI client (= one browser tab): set once when the page is built, read in all later
event handlers and timers of that tab. Outside a page (worker processes, logging, tests) the default is German,
unless force_lang() is used.
"""
from __future__ import annotations

import contextvars
import logging
import os

LANGS = ("de", "en")
DEFAULT = "de"
_forced: contextvars.ContextVar[str | None] = contextvars.ContextVar("ptz_lang", default=None)
MISSES: set[str] = set()      # English texts that were requested but are missing (checked by the tests)


def lang() -> str:
    f = _forced.get()
    if f:
        return f
    try:
        from nicegui import context
        return getattr(context.client, "ptz_lang", DEFAULT)
    except Exception:   # no client (e.g. worker process, tests)
        return DEFAULT


def force_lang(code: str | None):
    """For tests and scripts: use this language outside a page. Returns a token for reset_lang()."""
    return _forced.set(code)


def reset_lang(token) -> None:
    _forced.reset(token)


def is_en() -> bool:
    return lang() == "en"


def tr(text: str, *args, **kwargs) -> str:
    """Translate a German text (template) and fill its placeholders."""
    if is_en():
        from ptz.i18n_en import EN
        tr = EN.get(text)
        if tr is None:
            if text not in MISSES and os.environ.get("PTZ_I18N_DEBUG"):
                logging.getLogger("ptz.i18n").warning("missing English text: %r", text)
            MISSES.add(text)
            tr = text
    else:
        tr = text
    if args or kwargs:
        return tr.format(*args, **kwargs)
    return tr


def num(x: float, d: int = 1) -> str:
    """Number in the viewer's format: German 1.234,5 – English 1,234.5"""
    s = f"{x:,.{d}f}"
    if is_en():
        return s
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


class TDict(dict):
    """A dict whose string values are translated when read. For tuple values, `idx` lists the positions to translate
    (default: all strings)."""

    def __init__(self, *a, idx: tuple | None = None, **kw):
        super().__init__(*a, **kw)
        self._idx = idx

    def _tr(self, v):
        if isinstance(v, str):
            return tr(v)
        if isinstance(v, tuple):
            return tuple(tr(x) if isinstance(x, str) and (self._idx is None or i in self._idx) else x
                         for i, x in enumerate(v))
        return v

    def __getitem__(self, k):
        return self._tr(super().__getitem__(k))

    def get(self, k, default=None):
        return self._tr(super().__getitem__(k)) if k in self else default

    def values(self):
        return [self._tr(v) for v in super().values()]

    def items(self):
        return [(k, self._tr(v)) for k, v in super().items()]

    def raw(self, k):
        """Untranslated value (German)."""
        return super().__getitem__(k)


class TList(list):
    """A list of strings translated when read by index."""

    def __getitem__(self, i):
        v = super().__getitem__(i)
        return [tr(x) for x in v] if isinstance(i, slice) else tr(v)
