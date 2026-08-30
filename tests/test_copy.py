# Copyright (c) 2026 Martial Systems LLC
"""Stage 0: first sentence, banner, banned tokens, no ML hero."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAD = (
    "Official winter outlook and station normals for Indiana, "
    "plus a ledger of models that did not beat those fields."
)
BANS = (
    (r"will get\s+\d+\s+inches", "hero_in"),
    (r"flood warning", "flood_warning"),
    (r"p_sfha", "p_sfha"),
    (r"unmapped risk", "unmapped"),
    (r"\b(deaths?|fatalit(?:y|ies)|casualt(?:y|ies)|killed)\b", "casualty"),
)


def _hits(text: str) -> list[str]:
    return [name for pat, name in BANS if re.search(pat, text, re.I)]


def test_index_lead_and_banner() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert LEAD in html
    assert "Not NWS. Not a warning. Studies are dated holdouts." in html
    assert "XGBoost" not in html
    assert _hits(html) == []
    assert "\u2014" not in html


def test_readme() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(LEAD)
    assert "martialsystems.github.io/indiana_wx_pages" in text
    assert "Stage 0" in text
    assert "What it is not" not in text
    assert _hits(text) == []
    assert "\u2014" not in text


def test_methodology_names_stages() -> None:
    text = (ROOT / "METHODOLOGY.md").read_text(encoding="utf-8")
    assert "Stage 0" in text
    assert "ledger" in text.lower()
    assert "https://martialsystems.github.io/indiana_wx_pages/" in text
