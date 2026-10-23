---
title: pmtrack
subtitle: Project overview and progress review from plan docs and issues
---

pmtrack builds a project overview from two sources of truth, the plan
documents in the repo and the issue list, and writes a progress review
as Markdown with Mermaid charts. It uses only what GitHub, GitLab, Gitea
and Forgejo all have, so a project can move between forges unchanged.

## What it uses from the forge

| Used | Not used |
|---|---|
| Repo files rendered as Markdown, Mermaid blocks | Native issue dependencies, sub-issues, epics |
| Issues: title, body, open/closed, labels, assignees, URL, updated time | Project boards, weights, issue types, custom fields |
| Issue templates (`.github/ISSUE_TEMPLATE`, `.gitlab/issue_templates`) | Scoped labels, close reasons, forge CI or pages |

Everything else lives in YAML frontmatter under one key, `pm`, so it
never clashes with pandoc or md-preview keys (`title`, `md-preview-*`).

## The protocol

### Actionables: issues

An issue body may start with frontmatter:

```yaml
---
pm:
  id: login-form            # stable name, unique in the repo (optional)
  depends: [db-schema, lib:token-api, "#12"]
  plan: auth                # plan ids this belongs to (optional)
  weight: 2                 # share of progress, default 1
---
```

If a forge renders issue frontmatter badly, the same mapping can sit in a
fenced ` ```yaml ` block anywhere in the body instead. GitHub does: it
shows issue frontmatter as a rule and a heading, so use the fence there.
GitLab shows frontmatter as a code block, and Forgejo and Gitea hide it.

Issues without frontmatter are still tracked; they just have no
dependencies.

### Plans: docs

Any Markdown file under `docs/` with `pm.id` is a plan:

```yaml
---
title: Authentication
pm:
  id: auth
  scope: {labels: [area/auth]}   # issues carrying all these labels
  depends: [core-done]           # optional, like an issue
---
```

An issue belongs to a plan if it carries all the scope labels, or names
the plan in `pm.plan`. This is the link from plan to actionables: a plan
declares a label query, and issues opt in by label or by name.

A plan doc can show its own progress: put this pair anywhere in it and
`review` fills the space between them (not with `--publish`, which leaves
docs alone).

```markdown
<!-- pm:progress -->
<!-- /pm:progress -->
```

### Dependencies

| Ref | Means |
|---|---|
| `login-form` | node with that id in this repo (issue or plan) |
| `#12` | issue 12 in this repo |
| `lib:token-api` | node with that id in remote `lib` |
| `lib#4` | issue 4 in remote `lib` |
| full issue URL | resolved if it matches this repo or a remote |

Remotes are other repos, on any of the four forges, named in `.pm.yml`.
They are fetched only when some node refers to them. A remote issue
counts as done when it is closed; its own dependencies are not followed.
A dependency on a plan is met when every item of the plan is done.

### Status

| Status | Rule |
|---|---|
| ✓ done | closed |
| – dropped | closed with an `ignore_labels` label; left out of totals |
| ✕ blocked | open, and something it depends on isn't done (or can't be found) |
| ▶ active | open, unblocked, and assigned or with some boxes ticked |
| ○ ready | open, unblocked, not started |

Progress is weighted: a done item counts fully, an open one by the
share of its `- [ ]` boxes that are ticked.

## The review

`pmtrack review` writes to `progress/` (or to DIR with `--publish DIR`):

- `README.md`: a bar chart of % done for every subset (all items,
  `subsets` from the config, and each label) and every plan, a status pie,
  a table with counts and the change since the review window began,
  what changed, what needs attention (blocked, stale, metadata problems),
  what to start next (ready items, those that unblock most first), the
  dependency graph and a burn-up by day (items in scope, items done, and
  each day's gain or loss as bars; from the second day).
  Pies use one fixed colour per status. Bar and line charts are drawn on
  a white card with dark text in both light and dark mode: Mermaid draws
  every bar from below 0, so a background-coloured bar at 0 is drawn over
  it, and that needs a known background. Values sit in the bar labels.
- `<plan-id>.md`: the same for one plan, item by item. If the plan
  depends on other plans or items, it lists them; if it's blocked, it
  says by what (open dependencies, or that every open item is blocked).
- `history.jsonl`: one line per change of state, which drives the
  change lists, the deltas and the trend.

The review only changes when the data does: re-running with no issue or
doc changes writes nothing, so a scheduled job doesn't add empty commits.

## Issue templates

Keep one source per template in `templates/`:

```markdown
---
template:              # forge template settings
  name: Actionable
  about: A unit of work in the plan
  labels: [actionable]
pm:                    # copied into each new issue
  id: ""
  depends: []
---

## Goal
```

`pmtrack templates` writes `.github/ISSUE_TEMPLATE/<name>.md` (read by
GitHub, Gitea and Forgejo) and `.gitlab/issue_templates/<name>.md`
(GitLab: labels and assignees become `/label` and `/assign` quick
actions). `--check` exits 1 if they're out of date. Symlinks don't work:
forges read a symlink as its target path.

## Configuration: `.pm.yml`

```yaml
forge: forgejo                 # forgejo | gitea | github | gitlab
url: https://forgejo.example   # web address (https://github.com for GitHub)
repo: owner/name
token_env: PM_TOKEN            # env var holding the API token
docs: [docs]
out: progress
templates: templates
labels: ["area/*"]             # labels that get a subset ("*" = all)
ignore_labels: [wontfix, duplicate, invalid]
subsets:
  - {name: v1, labels: [milestone/v1]}
remotes:
  lib: {forge: gitlab, url: https://gitlab.com, repo: group/lib}
stale_days: 14                 # active but not updated for this long
window_days: 7                 # review window for changes and deltas
graph_limit: 80                # above this many nodes, warn and skip the graph
```

## Installing

Install a tagged version straight from the repo; pyyaml comes with it:

```sh
pip install "git+https://forgejo.lab.bvraghav.com/pm-bot/pmtrack@v0.1.2"
# or run it without installing:
uvx --from "git+https://forgejo.lab.bvraghav.com/pm-bot/pmtrack@v0.1.2" pmtrack review
```

The same tags are on a read-only mirror,
`git+https://github.com/bvraghav/pmtrack@v0.1.2`, for machines (such as
GitHub's and GitLab's CI runners) that can't reach the Forgejo server.

pmtrack is a single file, so copying `pmtrack.py` (from
`…/pm-bot/pmtrack/raw/tag/v0.1.2/pmtrack.py`) and installing pyyaml works
too. It isn't on PyPI.

## Running

```sh
PM_TOKEN=… pmtrack templates [--check]
PM_TOKEN=… pmtrack review [--dry-run] [--strict] [--publish DIR --ref BRANCH]
python3 -m unittest discover -s tests     # from a checkout
```

## In CI

Issue edits don't trigger CI on any forge, so run the review on a
schedule as well as on push. There are two Woodpecker examples:

- `examples/woodpecker-publish.yml` (suggested): CI keeps the review on
  its own branch, `pm-progress`, and never commits to working branches,
  so developers have nothing to pull. It runs
  `pmtrack review --publish DIR --ref BRANCH`, which writes the review and
  `history.jsonl` into DIR (a checkout of the review branch) and links plan
  docs on BRANCH through the forge's web pages. Plan docs' progress blocks
  aren't filled; link to the plan's page on the review branch instead,
  e.g. `…/src/branch/pm-progress/<plan-id>.md` on Forgejo.
- `examples/woodpecker.yml`: CI commits `progress/` and the plan docs'
  progress blocks back to the branch it ran on.

The same commit-back pipeline for the other forges:

- `examples/github-actions.yml` (copy to `.github/workflows/pm.yml`): the
  job's own token reads the issues and pushes, so no secret is needed.
- `examples/gitlab-ci.yml` (copy to `.gitlab-ci.yml`): needs a masked
  CI/CD variable `PM_TOKEN`, a project access token with `read_api` and
  `write_repository`, and a pipeline schedule.

## Status of forge support

Forgejo, GitHub and GitLab are tested against live repos (GitHub and
GitLab with a test project, `bvraghav/pm-dummy` on each). Gitea uses the
same API as Forgejo.

## Licence

MIT, see [LICENCE.md](LICENCE.md). Changes are listed in
[CHANGELOG.md](CHANGELOG.md).
