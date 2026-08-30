# Methodology: indiana_wx_pages

Static GitHub Pages. Not a science tree. Not a second vol server. The forecast stripe is official public fields. The Martial Systems stripe is locked nos and named Indiana points.

Live URL (after Pages is on): https://martialsystems.github.io/indiana_wx_pages/

First sentence on the site:

Official winter outlook and station normals for Indiana, plus a ledger of models that did not beat those fields.

## What v1 is

Three blocks on one page (and optional subpages). No XGBoost at build time.

**A. Official now / outlook**

NOAA CPC DJF temperature and precipitation lean for Indiana, issue date stamped (text plus link to CPC, not a reforecast).  
1991-2020 DJF snow normals at South Bend, Fort Wayne, Indianapolis, Evansville (the four cores from `indiana_djf_snow_tercile`).  
Optional: Open-Meteo or NWS current conditions client-side for those four cities. If the API dies, the page still renders A's static table.

**B. Ledger**

One table, links to SHAs and gists. Frozen rows from locked trees, hand-copied into `data/ledger.json`.

**C. Maps footnote (optional, last)**

Link gist 16584e78 and the Nora PNGs on GitHub raw. Caption: not a winter forecast, not a FIRM. No Thursday Pools table on this site.

Stage 0 ships a stub only. Do not skip to a map before B.

## Copy lock

Hero: CPC plus normals only.  
"ML" appears only inside the ledger as lost to a named bar.  
Every official number has an issue date or climate period.  
Banner: Not NWS. Not a warning. Studies are dated holdouts.

Claim scan on `index.html` and README: fail on "will get N inches," "flood warning," `p_sfha`, "unmapped risk," casualty language.

## Stages

| Stage | Job | Success |
|-------|-----|---------|
| 0 | Repo plus Pages stub plus this contract | `martialsystems.github.io/indiana_wx_pages/` serves a stub |
| A | Normals table plus CPC paragraph with issue date plus `SOURCES.md` | Four cities; links work logged-out |
| B | Ledger JSON rendered as HTML table | Each row has bar, numbers, SHA link |
| C | Claim scan plus README first sentence | No ML hero; gist index updated under Site |

## GitHub Pages

Settings: Pages, `main`, site root. MIT. `data/official/` is public NOAA/NCEI numbers with `source_url` and retrieved date in `SOURCES.md`. Do not commit RadarOnly stacks or NWIS dumps.

Readable index is gist `66b896b0` (Site heading lists this stub). `RESEARCH.md` in `.github` is a pointer, not a second full copy.

## Later, still static

After April: one DJF 2025-26 scorecard row, hand-edit.  
Subpage `/white-river/` that only links the hydro gist.  
Client-side USGS instant values for 03351000 as now, not a model.

Living RadarOnly-vs-CoCoRaHS stays off Pages unless a server is accepted.

## CI

Light: pytest that (1) ledger SHAs match `data/ledger.json` once B exists, (2) forbidden phrases absent, (3) four station IDs present at Stage A. No NOAA live fetch in CI.

## Parked

`indiana_djf_snow_tercile` refit, winter page on the snow repo, SPY vol, second paid host, Eagle Creek RMSE on the hero.
