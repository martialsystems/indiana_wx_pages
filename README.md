# Indiana weather pages

Official winter outlook and station normals for Indiana, plus a ledger of models that did not beat those fields.

Live: https://martialsystems.github.io/indiana_wx_pages/

Stage B: CPC DJF 2026-27 outlook issued 20 August 2026, 1991-2020 DJF snowfall normals at four GHCND cores, and a ledger of locked holdouts. Science stays in the locked trees.

Hero copy is CPC plus 1991-2020 normals. Ridge and HGB appear only in the ledger, each against a named bar.

Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3

```bash
python3 scripts/build_page.py
python3 -m pytest tests -q
python3 scripts/viewport_sanity.py
```

MIT. Martial Systems LLC.
