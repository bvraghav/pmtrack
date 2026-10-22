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
schedule and publishes the review to its own branch. This plan covers the pipelines
and how a project gets pmtrack in the first place.

Progress: [review on the pm-progress branch](https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/branch/pm-progress/ci.md)
