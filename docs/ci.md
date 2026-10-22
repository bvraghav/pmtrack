---
title: CI
subtitle: Keeping the review current without anyone running it
pm:
  id: ci
  scope: {labels: [area/ci]}
  depends: [core]
---

# CI

Issue edits don't trigger CI on any forge, so the review runs on a
schedule and commits `progress/` back. This plan covers the pipelines
and how a project gets pmtrack in the first place.

<!-- pm:progress -->
**0% done** · ✓ 0 done · ▶ 0 active · ○ 1 ready · ✕ 2 blocked · [review](../progress/ci.md)

```mermaid
pie showData title Items by status
  "○ ready" : 1
  "✕ blocked" : 2
```
<!-- /pm:progress -->
