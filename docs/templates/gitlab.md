---
title: pmtrack on GitLab
subtitle: Issue metadata, templates and defaults
---

# pmtrack on GitLab

## How GitLab shows the `pm` block

| Form in the issue body | GitLab shows |
|---|---|
| Frontmatter (`---` … `---` at the start) | a YAML code block |
| Fenced ` ```yaml ` block | a YAML code block |

Checked on 2026-10-23 with GitLab's Markdown API and the test project
[bvraghav/pm-dummy](https://gitlab.com/bvraghav/pm-dummy) (issue 2 has
frontmatter, issue 4 a fence).

**Recommendation: either form.** They look the same on GitLab. The
generated GitLab template keeps frontmatter; use the fence if the same
issue text also goes to another forge.

## Sane defaults

`.pm.yml`:

```yaml
forge: gitlab
url: https://gitlab.com          # self-managed: its web address
repo: group/project
labels: ["area/*"]
```

Templates: keep the source in `templates/<name>.md` and run
`pmtrack templates`. It writes `.gitlab/issue_templates/<name>.md` with
the issue's `pm` block as frontmatter. GitLab templates have no settings
of their own, so the template's labels and assignees become `/label` and
`/assign` quick actions at the end. GitLab applies those however the
issue is made, in the web form or through the API.

Token: a project access token with `read_api` (and `write_repository`,
role Maintainer or a Developer who may push, to commit the review back),
saved as a masked CI/CD variable `PM_TOKEN`. The job's own
`CI_JOB_TOKEN` can't read issues or push.

CI: [`examples/gitlab-ci.yml`](../../examples/gitlab-ci.yml), plus a
pipeline schedule (Build → Pipeline schedules), since issue edits don't
start pipelines. On gitlab.com, shared runners need a verified account.

Links: GitLab links issues as `…/-/issues/N` or, lately,
`…/-/work_items/N`; both work in `depends`, as does `#N`.

## What pmtrack accepts

What pmtrack can read is the only hard rule; the recommendation above
is only about how GitLab shows the issue. pmtrack looks for the `pm`
mapping:

1. in frontmatter at the very start of the body, then
2. in each ` ```yaml ` or ` ```yml ` fenced block, anywhere in the body,
   in order.

The first that holds a `pm:` mapping is used, and other YAML blocks are
left alone. If a block doesn't parse, or `pm:` isn't a mapping, the issue
is listed under *Metadata problems* in the review and tracked without
dependencies. An issue with no `pm` block at all is tracked too.

Plan docs are repo files rather than issues: keep their metadata in
frontmatter, which GitLab shows as a code block above the file.
