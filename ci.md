# ✓ CI

_Plan `ci` · [doc](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/branch/develop/docs/ci.md) · data as of 2026-10-23 04:38 UTC · [all subsets](README.md)_

**100% done** · ✓ 4 done · ▶ 0 active · ○ 0 ready · ✕ 0 blocked

Depends on: ✓ [Core](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/branch/develop/docs/core.md)

```mermaid
%%{init: {"themeVariables": {"pie1": "#0ca30c", "pieOpacity": "1", "pieSectionTextColor": "#000", "pieStrokeColor": "#fff", "pieStrokeWidth": "2px", "pieOuterStrokeWidth": "0px"}}}%%
pie showData title Items by status
  "✓ done" : 4
```

| Item | Status | Ticked | Depends on |
|---|---|--:|---|
| [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches | ✓ done | 3/3 | ✓ #9 |
| [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker | ✓ done | 3/3 | ✓ #1 |
| [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI | ✓ done | 2/2 | ✓ #7, ✓ #4, ✓ #5 |
| [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file | ✓ done | 2/2 | ✓ #7 |

## Changes

From 2026-10-22 20:30 to 2026-10-23 04:38 UTC:

- ✓ done: [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker
- ✓ done: [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI
- ✓ done: [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file
- new (done): [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches

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
  n2["✓ #4 Run the GitHub reader against a…"]:::done
  n3["✓ #5 Run the GitLab reader against a…"]:::done
  n4["✓ #7 Scheduled review on Woodpecker"]:::done
  n5["✓ #8 Pipelines for GitHub Actions an…"]:::done
  n6["✓ #9 Install pmtrack without copying…"]:::done
  n6 --> n1
  n0 --> n4
  n4 --> n5
  n2 --> n5
  n3 --> n5
  n4 --> n6
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
  x-axis ["10-22 · 2.7/4", "10-23 · 4/4"]
  y-axis "items" 0 --> 6
  bar [0, 1.3]
  bar [0, 0]
  bar [0, 0]
  bar [0, 0]
  line [4, 4]
  line [2.7, 4]
```

_Grey line: items in scope. Blue line: items done, weighted, with partial credit for ticked boxes. Green bars: items done that day. Red bars below 0: items done that were lost that day (reopened, or boxes unticked). A step up in the grey line means scope grew._
