# Copyright (c) 2026 Martial Systems LLC
"""Frozen ledger JSON rows are on the page by tree, SHA, and URLs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ledger_rows_in_html() -> None:
    ledger = json.loads((ROOT / "data/ledger.json").read_text(encoding="utf-8"))
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert ledger["caption"] in html
    assert "Details stay in the linked repos." in ledger["caption"]
    assert len(ledger["rows"]) == 7
    outlook, _, rest = html.partition('id="ledger"')
    for rec in ledger["rows"]:
        assert rec["tree"] in rest
        assert rec["science_sha"] in rest
        assert rec["commit_url"] in rest
        assert rec["tree_url"] in rest
        assert rec["science_sha"] in rec["commit_url"]
        assert rec["tree"] in rec["tree_url"]
    assert "indiana_freeze_date" not in outlook
    assert "11.7" in rest
    assert "28941fb" in rest
    assert "indiana_cpc_djf_skill" in rest
    assert "eacba62" in rest
    assert "0.643" in rest
