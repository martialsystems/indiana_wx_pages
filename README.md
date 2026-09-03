# Indiana weather pages

The live site is the Indiana research console. CPC remains the Official/Winter outlook panel.

[![Open the research console](https://img.shields.io/badge/Open_the_research_console-2e7d32?style=for-the-badge)](https://martialsystems.github.io/indiana_wx_pages/)

Official winter outlook and station normals for Indiana, plus a ledger of models that did not beat those fields.

Stage B: CPC DJF 2026-27 outlook issued 20 August 2026, 1991-2020 DJF snowfall normals at four GHCND cores, and a ledger of locked holdouts. Details stay in the linked repos.

Hero copy is CPC plus 1991-2020 normals. Ridge and HGB appear only in the ledger, each against a named bar.

Public HTML is the console snapshot. Do not regenerate the Stage B outlook stub.

```bash
python3 scripts/build_page.py
python3 -m pytest tests -q
python3 scripts/viewport_sanity.py
```

MIT. Martial Systems LLC.

[![Open the research console](https://img.shields.io/badge/Open_the_research_console-2e7d32?style=for-the-badge)](https://martialsystems.github.io/indiana_wx_pages/)
