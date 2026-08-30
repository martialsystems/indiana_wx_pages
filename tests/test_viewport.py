# Copyright (c) 2026 Martial Systems LLC
"""Static half of scripts/viewport_sanity.py (Chrome run is the named command)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_static_viewport_css() -> None:
    spec = importlib.util.spec_from_file_location(
        "viewport_sanity", ROOT / "scripts" / "viewport_sanity.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    assert mod.static_errors() == []
