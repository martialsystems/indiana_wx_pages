# Copyright (c) 2026 Martial Systems LLC
"""Lead sentence, CPC dates, four cores, banned tokens, no slogan banner."""

from __future__ import annotations

import json
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
SLOGAN = "Not NWS. Not a warning. Studies are dated holdouts."
NOTICE = (
    "This is CPC and climate normals. It is not a National Weather Service forecast "
    "and it is not telling you to do anything."
)
CORES = ("USW00014848", "USW00014827", "USW00093819", "USW00093817")


def _hits(text: str) -> list:
    return [name for pat, name in BANS if re.search(pat, text, re.I)]


def test_index_lead_cpc_and_cores() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    cpc = json.loads((ROOT / "data/official/cpc.json").read_text(encoding="utf-8"))
    normals = json.loads((ROOT / "data/official/normals.json").read_text(encoding="utf-8"))
    assert "<h1>Indiana research console</h1>" in html
    assert "<h1>Indiana Winter Outlook</h1>" not in html
    assert "<h1>{0}</h1>".format(LEAD) not in html
    assert LEAD in html
    assert 'class="lead"' in html
    assert "<h1>Indiana weather pages</h1>" not in html
    assert "Science stays" not in html
    assert "those trees" not in html
    assert "Details stay in the linked repos." in html
    assert NOTICE in html
    assert html.rfind(NOTICE) > html.rfind('id="ledger"')
    assert SLOGAN not in html
    assert 'class="banner"' not in html
    assert "XGBoost" not in html
    assert "What it is not" not in html
    assert "\u2014" not in html
    assert "assets/console.js" in html
    assert "This page is the research index" in html
    assert "Live sibling:" not in html
    assert "gist 66b896b0" in html
    assert "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3" in html
    assert "https://github.com/martialsystems/indiana_research_console" in html
    assert 'data-go="outlook"' in html
    assert 'data-go="ledger"' in html
    assert 'data-go="nwm"' in html
    assert 'data-go="catalog"' in html
    assert 'data-go="maps"' in html
    assert cpc["issued"] in html
    assert "2026-08-20" in html
    assert cpc["season"] in html
    assert cpc["next_issue"] in html
    assert cpc["temp_map"] in html
    assert cpc["prcp_map"] in html
    for sid in CORES:
        assert sid in html
    for st in normals["stations"]:
        assert "{0:.1f}".format(st["djf_snow_in"]) in html
    assert _hits(html) == []
    outlook, _, rest = html.partition('id="ledger"')
    assert "Ridge" not in outlook
    assert "HGB" not in outlook
    assert "Ridge" in rest
    assert "HGB" in rest
    assert "indiana_freeze_date" in rest
    assert "28941fb" in rest
    assert "11.7" in rest
    assert "frost outlook" not in html.lower()
    assert "Indiana will freeze on" not in html
    assert "indiana_freeze_date" not in outlook
    assert "median date" not in outlook
    catalog = html[html.find('id="catalog"') : html.find('id="maps"')]
    ledger = html[html.find('id="ledger"') : html.find('id="nwm"')]
    assert 'href="https://github.com/martialsystems/' in catalog
    assert 'href="https://github.com/martialsystems/' in ledger
    assert "img.shields.io" not in catalog
    css = (ROOT / "assets/style.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/console.js").read_text(encoding="utf-8")
    assert "#catalog a" in css and "#ledger a" in css and ".map-card h3 a" in css
    idx = css.find("#catalog a")
    brace = css.find("{", idx)
    block = css[brace : css.find("}", brace) + 1]
    assert "#5a2a16" in block
    assert "underline" in block
    assert "color: inherit" not in block
    assert 'closest("a[href]")' in js
    assert 'data-panel="catalog"' in html


def test_methodology_names_stages() -> None:
    text = (ROOT / "METHODOLOGY.md").read_text(encoding="utf-8")
    assert "Stage 0" in text
    assert "Stage B" in text
    assert "ledger" in text.lower()
    assert SLOGAN not in text
    assert NOTICE in text
    assert "https://martialsystems.github.io/indiana_wx_pages/" in text
    assert "\u2014" not in text
    assert "What it is not" not in text
