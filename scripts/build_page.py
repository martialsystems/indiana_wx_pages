#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Public HTML is the research console snapshot.

Do not regenerate the Stage B outlook stub. build() returns the committed
console index.html.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build() -> str:
    # Public HTML is the research console snapshot from
    # Documents/indiana_research_console/pages. Do not regenerate the Stage B outlook stub.
    return (ROOT / "index.html").read_text(encoding="utf-8")


def main() -> None:
    html_out = build()
    dest = ROOT / "index.html"
    dest.write_text(html_out, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
