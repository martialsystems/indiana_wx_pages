# Copyright (c) 2026 Martial Systems LLC
"""Committed index.html matches scripts/build_page.py. Maps are on disk."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _builder():
    spec = importlib.util.spec_from_file_location(
        "build_page", ROOT / "scripts" / "build_page.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_index_matches_builder() -> None:
    mod = _builder()
    committed = (ROOT / "index.html").read_text(encoding="utf-8")
    assert committed == mod.build()


def test_cpc_maps_exist() -> None:
    temp = ROOT / "assets/cpc/off04_temp.gif"
    prcp = ROOT / "assets/cpc/off04_prcp.gif"
    assert temp.is_file() and temp.read_bytes()[:6] == b"GIF89a"
    assert prcp.is_file() and prcp.read_bytes()[:6] == b"GIF89a"
    assert temp.stat().st_size > 50_000
    assert prcp.stat().st_size > 50_000
