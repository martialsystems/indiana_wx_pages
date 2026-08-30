#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Render index.html from committed official JSON and the ledger."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAD = (
    "Official winter outlook and station normals for Indiana, "
    "plus a ledger of models that did not beat those fields."
)
HEADING = "Indiana Winter Outlook"
INDEX_GIST = "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
LIVE = "https://martialsystems.github.io/indiana_wx_pages/"
NOTICE = (
    "This is CPC and climate normals. It is not a National Weather Service forecast "
    "and it is not telling you to do anything."
)


def build() -> str:
    cpc = json.loads((ROOT / "data/official/cpc.json").read_text(encoding="utf-8"))
    normals = json.loads((ROOT / "data/official/normals.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "data/ledger.json").read_text(encoding="utf-8"))

    def e(value: object) -> str:
        return html.escape(str(value), quote=True)

    rows = []
    for st in normals["stations"]:
        rows.append(
            "            <tr>"
            f"<td>{e(st['city'])}</td>"
            f"<td><code>{e(st['id'])}</code></td>"
            f"<td>{e('{0:.1f}'.format(st['dec_in']))}</td>"
            f"<td>{e('{0:.1f}'.format(st['jan_in']))}</td>"
            f"<td>{e('{0:.1f}'.format(st['feb_in']))}</td>"
            f"<td>{e('{0:.1f}'.format(st['djf_snow_in']))}</td>"
            "</tr>"
        )

    ledger_rows = []
    for rec in ledger["rows"]:
        ledger_rows.append(
            "            <tr>"
            f"<td><a href=\"{e(rec['tree_url'])}\">{e(rec['tree'])}</a></td>"
            f"<td>{e(rec['bar'])}</td>"
            f"<td>{e(rec['held_out'])}</td>"
            f"<td><a href=\"{e(rec['commit_url'])}\">{e(rec['science_sha'])}</a></td>"
            "</tr>"
        )

    issued = e(cpc["issued"])
    season = e(cpc["season"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(HEADING)}</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <main>
    <h1>{e(HEADING)}</h1>
    <p>{e(LEAD)}</p>

    <section id="outlook">
      <h2>CPC {season}</h2>
      <p>Issued {issued}. Valid {e(cpc["valid"])}. Next CPC update {e(cpc["next_issue"])}. Climatology {e(cpc["climatology"])}.</p>
      <p>Indiana temperature: {e(cpc["indiana_temperature"])} Precipitation: {e(cpc["indiana_precipitation"])}</p>
      <p>{e(cpc["enso"])} Forecaster {e(cpc["forecaster"])}, {e(cpc["issued_text"])}.</p>
      <figure>
        <img src="{e(cpc["temp_map"])}" alt="NOAA CPC seasonal temperature outlook, {season}, issued {issued}">
      </figure>
      <figure>
        <img src="{e(cpc["prcp_map"])}" alt="NOAA CPC seasonal precipitation outlook, {season}, issued {issued}">
      </figure>
      <p><a href="{e(cpc["discussion_url"])}">CPC prognostic discussion</a>. The GIFs in this repo are the {issued} snapshots. CPC's live lead-4 URL changes when the next outlook is issued.</p>
    </section>

    <section id="normals">
      <h2>{e(normals["period"])} DJF snowfall normals</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>City</th>
              <th>Station</th>
              <th>Dec</th>
              <th>Jan</th>
              <th>Feb</th>
              <th>DJF (in)</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(rows)}
          </tbody>
        </table>
      </div>
      <p>NCEI {e(normals["period"])} {e(normals["element"])}. {e(normals["definition"])} Inches. Retrieved {e(normals["retrieved"])}.</p>
    </section>

    <section id="ledger">
      <h2>Ledger</h2>
      <p>{e(ledger["caption"])}</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Study</th>
              <th>Bar</th>
              <th>Held-out</th>
              <th>SHA</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(ledger_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <p class="foot">Martial Systems LLC. CPC and NCEI numbers are dated official fields. Ledger SHAs are frozen. Live: <a href="{e(LIVE)}">{e(LIVE.replace("https://", ""))}</a>. Research index: <a href="{e(INDEX_GIST)}">gist 66b896b0</a>.</p>
    <p class="notice">{e(NOTICE)}</p>
  </main>
</body>
</html>
"""


def main() -> None:
    html_out = build()
    dest = ROOT / "index.html"
    dest.write_text(html_out, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
