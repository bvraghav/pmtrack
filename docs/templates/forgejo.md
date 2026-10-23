---
title: pmtrack on Forgejo
subtitle: Issue metadata, templates and defaults
---

# pmtrack on Forgejo

## How Forgejo shows the `pm` block

| Form in the issue body | Forgejo shows |
|---|---|
| Frontmatter (`---` … `---` at the start) | a collapsed table: a small table icon that opens into nested tables |
| Fenced ` ```yaml ` block | a YAML code block |

Checked on 2026-10-23 on Forgejo 15.0.10 with its Markdown API and
pmtrack's own issues.

**Recommendation: use the fence.** It's readable without a click, and
it's what the generated template writes. Frontmatter still works for
pmtrack (see [What pmtrack accepts](#what-pmtrack-accepts)) and is
tidy enough here if you prefer it.

## Sane defaults

`.pm.yml`:

```yaml
forge: forgejo
url: https://forgejo.example     # web address
repo: owner/name
labels: ["area/*"]
```

Templates: keep the source in `templates/<name>.md` and run
`pmtrack templates`. It writes `.github/ISSUE_TEMPLATE/<name>.md`, which
Forgejo reads, with the template settings (`name`, `about`, `title`,
`labels`, `assignees`) as frontmatter and the issue's `pm` block as a
fence.

Token: an access token with issue read (and repository write to commit
the review back). It can be limited to specific repositories. Forgejo
returns at most 50 issues per page; pmtrack pages through them.

CI: [`examples/woodpecker-publish.yml`](../../examples/woodpecker-publish.yml)
(review on its own branch) or
[`examples/woodpecker.yml`](../../examples/woodpecker.yml) (commit back).

Links: issues are `https://forgejo.example/owner/name/issues/N`; either
that or `#N` works in `depends`.

## What pmtrack accepts

What pmtrack can read is the only hard rule; the recommendation above
is only about how Forgejo shows the issue. pmtrack looks for the `pm`
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
