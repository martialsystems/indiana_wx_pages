# Copyright (c) 2026 Martial Systems LLC
"""Public freeze-date write-up on Pages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_freeze_date_page_is_in_the_snapshot() -> None:
    html = (ROOT / "trees" / "indiana_freeze_date" / "index.html").read_text(
        encoding="utf-8"
    )
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "First and last 32 F" in html
    assert "28941fb" in html
    assert "8.75" in html
    assert "11.67" in html
    assert "mae_bars.png" in html
    assert "scatter.png" in html
    assert "tree-page" in html
    assert "trees/indiana_freeze_date/" in index
    assert "../../index.html#home" in html
    assert 'data-go="home"' in html
    assert "Indiana will freeze on" not in html
    assert "frost outlook" not in html.lower()
    assert "\u2014" not in html
    assert "What it is not" not in html
