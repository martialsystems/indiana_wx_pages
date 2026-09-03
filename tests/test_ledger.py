# Copyright (c) 2026 Martial Systems LLC
"""Ledger JSON rows appear in the page with bar, numbers, and SHA links."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ledger_rows_in_html() -> None:
    ledger = json.loads((ROOT / "data/ledger.json").read_text(encoding="utf-8"))
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert ledger["caption"] in html
    assert "Details stay in the linked repos." in ledger["caption"]
    assert len(ledger["rows"]) == 5
    for rec in ledger["rows"]:
        assert rec["bar"] in html
        assert rec["held_out"] in html
        assert rec["science_sha"] in html
        assert rec["commit_url"] in html
        assert rec["tree_url"] in html
        assert rec["science_sha"] in rec["commit_url"]
        assert rec["tree"] in rec["tree_url"]
