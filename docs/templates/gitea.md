---
title: pmtrack on Gitea
subtitle: Issue metadata, templates and defaults
---

# pmtrack on Gitea

Not yet checked against a live Gitea. Forgejo started as a fork of
Gitea and pmtrack reads both through the same API, so what follows
leans on the [Forgejo guide](forgejo.md).

## How Gitea shows the `pm` block

| Form in the issue body | Gitea shows |
|---|---|
| Frontmatter (`---` … `---` at the start) | probably a collapsed table, as on Forgejo (not checked) |
| Fenced ` ```yaml ` block | a YAML code block |

**Recommendation: use the fence.** It reads as a code block on every
forge checked so far, and it's what the generated template writes.
Frontmatter still works for pmtrack (see
[What pmtrack accepts](#what-pmtrack-accepts)).

## Sane defaults

`.pm.yml`:

```yaml
forge: gitea
url: https://gitea.example       # web address
repo: owner/name
labels: ["area/*"]
```

Templates: keep the source in `templates/<name>.md` and run
`pmtrack templates`. It writes `.github/ISSUE_TEMPLATE/<name>.md`, which
Gitea reads, with the template settings as frontmatter and the issue's
`pm` block as a fence.

Token: an access token with `read:issue` (and `write:repository` to
commit the review back).

CI: Woodpecker also runs on Gitea, so the Woodpecker examples should
work as they are
([`woodpecker-publish.yml`](../../examples/woodpecker-publish.yml),
[`woodpecker.yml`](../../examples/woodpecker.yml)); not checked.

Links: issues are `https://gitea.example/owner/name/issues/N`; either
that or `#N` works in `depends`.

## What pmtrack accepts

What pmtrack can read is the only hard rule; the recommendation above
is only about how Gitea shows the issue. pmtrack looks for the `pm`
mapping:

1. in frontmatter at the very start of the body, then
2. in each ` ```yaml ` or ` ```yml ` fenced block, anywhere in the body,
   in order.

The first that holds a `pm:` mapping is used, and other YAML blocks are
left alone. If a block doesn't parse, or `pm:` isn't a mapping, the issue
is listed under *Metadata problems* in the review and tracked without
dependencies. An issue with no `pm` block at all is tracked too.

Plan docs are repo files rather than issues: keep their metadata in
frontmatter.
