# ✕ CI

_Plan `ci` · [doc](../docs/ci.md) · data as of 2026-10-22 20:30 UTC · [all subsets](README.md)_

**0% done** · ✓ 0 done · ▶ 0 active · ○ 1 ready · ✕ 2 blocked

```mermaid
pie showData title Items by status
  "○ ready" : 1
  "✕ blocked" : 2
```

| Item | Status | Ticked | Depends on |
|---|---|--:|---|
| [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker | ○ ready | 0/3 | ✓ #1 |
| [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI | ✕ blocked | 0/2 | ○ #7, ○ #4, ○ #5 |
| [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file | ✕ blocked | 0/2 | ○ #7 |

## Changes

_No earlier snapshot yet; changes appear from the next update._

## Needs attention

### ✕ Blocked

- [#8](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/8) Pipelines for GitHub Actions and GitLab CI, waiting on ○ [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker, ○ [#4](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/4) Run the GitHub reader against a live repo, ○ [#5](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/5) Run the GitLab reader against a live project
- [#9](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/9) Install pmtrack without copying the file, waiting on ○ [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker


## Next up

- ○ [#7](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/issues/7) Scheduled review on Woodpecker (unblocks 2)

## Dependency graph

_Legend: ✓ done · ▶ active (assigned or partly ticked) · ○ ready (nothing it waits on is open) · ✕ blocked · arrows point from a dependency to what waits on it; dotted lines join a plan to its items._

```mermaid
flowchart LR
  n0["✓ #1 Progress review and issue templ…"]:::done
  n1["○ #4 Run the GitHub reader against a…"]:::ready
  n2["○ #5 Run the GitLab reader against a…"]:::ready
  n3["○ #7 Scheduled review on Woodpecker"]:::ready
  n4["✕ #8 Pipelines for GitHub Actions an…"]:::blocked
  n5["✕ #9 Install pmtrack without copying…"]:::blocked
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
