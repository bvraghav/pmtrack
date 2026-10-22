# ▶ CI

_Plan `ci` · [doc](../docs/ci.md) · data as of 2026-10-22 22:22 UTC · [all subsets](README.md)_

**25% done** · ✓ 1 done · ▶ 0 active · ○ 1 ready · ✕ 2 blocked

Depends on: ✓ [Core](../docs/core.md)

```mermaid
%%{init: {"themeVariables": {"pie1": "#0ca30c", "pie2": "#eda100", "pie3": "#d03b3b", "pieOpacity": "1", "pieSectionTextColor": "#000", "pieStrokeColor": "#fff", "pieStrokeWidth": "2px", "pieOuterStrokeWidth": "0px"}}}%%
pie showData title Items by status
  "✓ done" : 1
  "○ ready" : 1
  "✕ blocked" : 2
```

| Item | Status | Ticked | Depends on |
|---|---|--:|---|
| [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker | ✓ done | 3/3 | ✓ #1 |
| [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file | ○ ready | 0/2 | ✓ #7 |
| [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches | ✕ blocked | 0/3 | ○ #9 |
| [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI | ✕ blocked | 0/2 | ✓ #7, ○ #4, ○ #5 |

## Changes

From 2026-10-22 20:30 to 2026-10-22 22:22 UTC:

- ✓ done: [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker
- blocked → ready: [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file
- new (blocked): [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches

## Needs attention

### ✕ Blocked

- [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI, waiting on ○ [#4](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/4) Run the GitHub reader against a live repo, ○ [#5](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/5) Run the GitLab reader against a live project
- [#11](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/11) Publish the review from CI without commits on working branches, waiting on ○ [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file


## Next up

- ○ [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file (unblocks 1)

## Dependency graph

_Legend: ✓ done · ▶ active (assigned or partly ticked) · ○ ready (nothing it waits on is open) · ✕ blocked · arrows point from a dependency to what waits on it; dotted lines join a plan to its items._

```mermaid
flowchart LR
  n0["✓ #1 Progress review and issue templ…"]:::done
  n1["✕ #11 Publish the review from CI with…"]:::blocked
  n2["○ #4 Run the GitHub reader against a…"]:::ready
  n3["○ #5 Run the GitLab reader against a…"]:::ready
  n4["✓ #7 Scheduled review on Woodpecker"]:::done
  n5["✕ #8 Pipelines for GitHub Actions an…"]:::blocked
  n6["○ #9 Install pmtrack without copying…"]:::ready
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

_The trend starts once there are two days of history._
