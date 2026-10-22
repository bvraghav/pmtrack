# Changelog

All notable changes to pmtrack. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `review --publish DIR --ref BRANCH`: writes the review and its history
  to DIR, a checkout of a review branch, and leaves plan docs alone;
  plan docs are linked on BRANCH through the forge's web pages.
- `examples/woodpecker-publish.yml`: CI keeps the review on branch
  `pm-progress` and never commits to working branches.

### Changed

- pmtrack's own review is published to `pm-progress`; `progress/` is
  gone from develop and plan docs link to their review page.

## [0.1.1] - 2026-10-23

### Added

- MIT licence (`LICENCE.md`) and this changelog.

### Changed

- pmtrack's own CI installs the package before testing, and also tests
  on tags and releases, checking the tag matches the version.
- Example pipeline and README install `v0.1.1`.

## [0.1.0] - 2026-10-23

First release.

### Added

- `pmtrack review`: writes a progress review to `progress/` from plan docs
  (`pm` frontmatter under `docs/`) and the issue list, using only what
  GitHub, GitLab, Gitea and Forgejo all share.
  - Dependencies in issue and plan frontmatter, across repos via remotes
    in `.pm.yml`; statuses done, dropped, blocked, active and ready;
    weighted progress with partial credit for ticked boxes.
  - Overview with % done per subset and plan, status pie, counts and
    deltas, changes, what needs attention, what to start next, the
    dependency graph and a burn-up by day.
  - A page per plan, naming what the plan depends on and what blocks it.
  - Progress blocks filled in plan docs between `<!-- pm:progress -->`
    markers.
  - `history.jsonl`; the review is only rewritten when the data changes.
  - Mermaid charts in fixed status colours. Bars start at 0 and losses
    are drawn below 0, with true values only.
  - Above `graph_limit` nodes the graph is skipped with a warning.
- `pmtrack templates`: one source per issue template, written for
  GitHub, Gitea and Forgejo and for GitLab; `--check` for CI.
- Forge readers for Forgejo and Gitea (tested live), GitHub and GitLab
  (not yet run against a live server).
- Woodpecker example pipeline: review on push and on a schedule,
  committing `progress/` back.
- Install from a git tag with pip or uv; `pmtrack` command.

[Unreleased]: https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/compare/v0.1.1...develop
[0.1.1]: https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/tag/v0.1.1
[0.1.0]: https://forgejo.lab.bvraghav.com/pm-bot/pmtrack/src/tag/v0.1.0
