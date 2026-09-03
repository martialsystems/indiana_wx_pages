# Copyright (c) 2026 Martial Systems LLC
"""Live site is the research console. CPC stays the Official panel."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOTER = (
    "Research index: "
    "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
)
FIRST = (
    "The live site is the Indiana research console. "
    "CPC remains the Official/Winter outlook panel."
)
LEAD = (
    "Official winter outlook and station normals for Indiana, "
    "plus a ledger of models that did not beat those fields."
)


def test_readme() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "# Indiana weather pages"
    body = "\n".join(lines[1:]).lstrip()
    first = body.split("\n", 1)[0]
    assert first == FIRST
    assert "martialsystems.github.io/indiana_wx_pages" in text
    assert "Stage B" in text
    assert LEAD in text
    assert "Details stay in the linked repos." in text
    assert "What it is not" not in text
    assert "\u2014" not in text
    assert FOOTER in text
    assert "66b896b0" in text.split("Research index:")[-1]
    assert "will get" not in text.lower()
    assert "flood warning" not in text.lower()
