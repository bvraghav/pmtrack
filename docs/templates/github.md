---
title: pmtrack on GitHub
subtitle: Issue metadata, templates and defaults
---

# pmtrack on GitHub

## How GitHub shows the `pm` block

| Form in the issue body | GitHub shows |
|---|---|
| Frontmatter (`---` … `---` at the start) | a horizontal rule, then the YAML squashed into one large heading |
| Fenced ` ```yaml ` block | a highlighted code block |

Checked on 2026-10-23 with GitHub's Markdown API and the test repo
[bvraghav/pm-dummy](https://github.com/bvraghav/pm-dummy) (issue 2 has
frontmatter, issue 4 a fence).

**Recommendation: use the fence.** Frontmatter still works for pmtrack
(see [What pmtrack accepts](#what-pmtrack-accepts)), but it's hard to
read on GitHub.

## Sane defaults

`.pm.yml`:

```yaml
forge: github
url: https://github.com          # GitHub Enterprise: its web address
repo: owner/name
labels: ["area/*"]
```

Templates: keep the source in `templates/<name>.md` and run
`pmtrack templates`. It writes `.github/ISSUE_TEMPLATE/<name>.md` with
GitHub's template settings (`name`, `about`, `title`, `labels`,
`assignees`) as frontmatter, which GitHub strips from the new issue, and
the issue's `pm` block as a fence. Template labels are applied only when
the issue is made in GitHub's web form, not through the API.

Token: in GitHub Actions, the job's own token is enough
(`issues: read`, plus `contents: write` to commit the review back). For a
run elsewhere, a fine-grained personal access token limited to the repo,
with Issues read (and Contents read and write to commit back).

CI: [`examples/github-actions.yml`](../../examples/github-actions.yml).
GitHub pauses scheduled workflows in a public repo after 60 days without
activity; re-enable it in the Actions tab.

Links: issues are `https://github.com/owner/name/issues/N`; either that
or `#N` works in `depends`. Pull requests share the numbering with
issues, and pmtrack leaves them out.

## What pmtrack accepts

What pmtrack can read is the only hard rule; the recommendation above
is only about how GitHub shows the issue. pmtrack looks for the `pm`
mapping:

1. in frontmatter at the very start of the body, then
2. in each ` ```yaml ` or ` ```yml ` fenced block, anywhere in the body,
   in order.

The first that holds a `pm:` mapping is used, and other YAML blocks are
left alone. If a block doesn't parse, or `pm:` isn't a mapping, the issue
is listed under *Metadata problems* in the review and tracked without
dependencies. An issue with no `pm` block at all is tracked too.

Plan docs are repo files rather than issues: keep their metadata in
frontmatter, which GitHub shows as a table above the file.
