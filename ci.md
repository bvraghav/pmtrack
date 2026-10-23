# ▶ CI

_Plan `ci` · [doc](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/branch/develop/docs/ci.md) · data as of 2026-10-23 04:56 UTC · [all subsets](README.md)_

**95% done** · ✓ 4 done · ▶ 1 active · ○ 0 ready · ✕ 0 blocked

Depends on: ✓ [Core](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/branch/develop/docs/core.md)

```mermaid
%%{init: {"themeVariables": {"pie1": "#0ca30c", "pie2": "#2a78d6", "pieOpacity": "1", "pieSectionTextColor": "#000", "pieStrokeColor": "#fff", "pieStrokeWidth": "2px", "pieOuterStrokeWidth": "0px"}}}%%
pie showData title Items by status
  "✓ done" : 4
  "▶ active" : 1
```

| Item | Status | Ticked | Depends on |
|---|---|--:|---|
| [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches | ✓ done | 3/3 | ✓ #9 |
| [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker | ✓ done | 3/3 | ✓ #1 |
| [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI | ✓ done | 2/2 | ✓ #7, ✓ #4, ✓ #5 |
| [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file | ✓ done | 2/2 | ✓ #7 |
| [#14](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/14) Create the forge release from CI on a version tag | ▶ active | 3/4 | ✓ #7, ✓ #8 |

## Changes

From 2026-10-22 20:30 to 2026-10-23 04:56 UTC:

- ✓ done: [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker
- ✓ done: [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI
- ✓ done: [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file
- new (done): [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches
- new (active): [#14](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/14) Create the forge release from CI on a version tag

## Needs attention

Nothing blocked, stale or malformed.

## Next up

Nothing ready to start.

## Dependency graph

_Legend: ✓ done · ▶ active (assigned or partly ticked) · ○ ready (nothing it waits on is open) · ✕ blocked · arrows point from a dependency to what waits on it; dotted lines join a plan to its items._

```mermaid
flowchart LR
  n0["✓ #1 Progress review and issue templ…"]:::done
  n1["✓ #11 Publish the review from CI with…"]:::done
  n2["▶ #14 Create the forge release from C…"]:::active
  n3["✓ #4 Run the GitHub reader against a…"]:::done
  n4["✓ #5 Run the GitLab reader against a…"]:::done
  n5["✓ #7 Scheduled review on Woodpecker"]:::done
  n6["✓ #8 Pipelines for GitHub Actions an…"]:::done
  n7["✓ #9 Install pmtrack without copying…"]:::done
  n7 --> n1
  n5 --> n2
  n6 --> n2
  n0 --> n5
  n5 --> n6
  n3 --> n6
  n4 --> n6
  n5 --> n7
  classDef done fill:#0ca30c,color:#000,stroke:#0ca30c
  classDef active fill:#2a78d6,color:#fff,stroke:#2a78d6
  classDef ready fill:#eda100,color:#000,stroke:#eda100
  classDef blocked fill:#d03b3b,color:#fff,stroke:#d03b3b
  classDef unknown fill:#898781,color:#000,stroke:#898781
  classDef dropped fill:#898781,color:#000,stroke:#898781
```

## Trend

```mermaid
%%{init: {"themeVariables": {"xyChart": {"backgroundColor": "#ffffff", "titleColor": "#222222", "plotColorPalette": "#0ca30c,#ffffff,#d03b3b,#ffffff,#898781,#2a78d6", "xAxisLabelColor": "#222222", "xAxisTitleColor": "#222222", "xAxisTickColor": "#222222", "xAxisLineColor": "#222222", "yAxisLabelColor": "#222222", "yAxisTitleColor": "#222222", "yAxisTickColor": "#222222", "yAxisLineColor": "#222222"}}, "xyChart": {"height": 360}}}%%
xychart-beta
  title "plan:ci: items done and scope"
  x-axis ["10-22 · 2.7/4", "10-23 · 4.8/5"]
  y-axis "items" 0 --> 7
  bar [0, 2.1]
  bar [0, 0]
  bar [0, 0]
  bar [0, 0]
  line [4, 5]
  line [2.7, 4.8]
```

_Grey line: items in scope. Blue line: items done, weighted, with partial credit for ticked boxes. Green bars: items done that day. Red bars below 0: items done that were lost that day (reopened, or boxes unticked). A step up in the grey line means scope grew._
