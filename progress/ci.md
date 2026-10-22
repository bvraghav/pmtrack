# ✕ CI

_Plan `ci` · [doc](../docs/ci.md) · data as of 2026-10-22 20:50 UTC · [all subsets](README.md)_

**33% done** · ✓ 1 done · ▶ 0 active · ○ 1 ready · ✕ 1 blocked

```mermaid
%%{init: {"themeVariables": {"pie1": "#0ca30c", "pie2": "#eda100", "pie3": "#d03b3b", "pieOpacity": "1", "pieSectionTextColor": "#000", "pieStrokeColor": "#fff", "pieStrokeWidth": "2px", "pieOuterStrokeWidth": "0px"}}}%%
pie showData title Items by status
  "✓ done" : 1
  "○ ready" : 1
  "✕ blocked" : 1
```

| Item | Status | Ticked | Depends on |
|---|---|--:|---|
| [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker | ✓ done | 3/3 | ✓ #1 |
| [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file | ○ ready | 0/2 | ✓ #7 |
| [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI | ✕ blocked | 0/2 | ✓ #7, ○ #4, ○ #5 |

## Changes

From 2026-10-22 20:30 to 2026-10-22 20:50 UTC:

- ✓ done: [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker
- blocked → ready: [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file

## Needs attention

### ✕ Blocked

- [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI, waiting on ○ [#4](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/4) Run the GitHub reader against a live repo, ○ [#5](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/5) Run the GitLab reader against a live project


## Next up

- ○ [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file

## Dependency graph

_Legend: ✓ done · ▶ active (assigned or partly ticked) · ○ ready (nothing it waits on is open) · ✕ blocked · arrows point from a dependency to what waits on it; dotted lines join a plan to its items._

```mermaid
flowchart LR
  n0["✓ #1 Progress review and issue templ…"]:::done
  n1["○ #4 Run the GitHub reader against a…"]:::ready
  n2["○ #5 Run the GitLab reader against a…"]:::ready
  n3["✓ #7 Scheduled review on Woodpecker"]:::done
  n4["✕ #8 Pipelines for GitHub Actions an…"]:::blocked
  n5["○ #9 Install pmtrack without copying…"]:::ready
  n0 --> n3
  n3 --> n4
  n1 --> n4
  n2 --> n4
  n3 --> n5
  classDef done fill:#0ca30c,color:#000,stroke:#0ca30c
  classDef active fill:#2a78d6,color:#fff,stroke:#2a78d6
  classDef ready fill:#eda100,color:#000,stroke:#eda100
  classDef blocked fill:#d03b3b,color:#fff,stroke:#d03b3b
  classDef unknown fill:#898781,color:#000,stroke:#898781
  classDef dropped fill:#898781,color:#000,stroke:#898781
```

## Trend

_The trend starts once there are two days of history._
