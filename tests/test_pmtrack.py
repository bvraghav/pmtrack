import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pmtrack  # noqa: E402


def issue(n, title, body="", state="open", labels=(), assignees=(), updated="2026-10-20T00:00:00Z"):
    return {"number": n, "title": title, "body": body, "state": state, "labels": list(labels),
            "assignees": list(assignees), "url": "https://f.example/o/app/issues/%d" % n,
            "updated": updated}


def fm(**pm):
    import yaml
    return "---\n%s---\n\nBody\n" % yaml.safe_dump({"pm": pm}, sort_keys=False)


ISSUES = {
    "o/app": [
        issue(1, "DB schema", fm(id="db"), state="closed", labels=["area/core"]),
        issue(2, "Login form", fm(id="login", depends=["db", "lib:token"]) + "- [x] a\n- [ ] b\n",
              labels=["area/auth"]),
        issue(3, "Session store", fm(id="session", depends=["login"]), labels=["area/auth"]),
        issue(4, "Logout", fm(id="logout", depends=["#3", "nope"]), labels=["area/auth"]),
        issue(5, "Docs site", "no frontmatter", labels=["area/docs"], assignees=["ann"],
              updated="2026-09-01T00:00:00Z"),
        issue(6, "Old idea", state="closed", labels=["wontfix"]),
        issue(7, "Cycle a", fm(id="ca", depends=["cb"])),
        issue(8, "Cycle b", fm(id="cb", depends=["ca"])),
        issue(9, "Fenced", "Intro\n\n```yaml\npm:\n  id: fenced\n  plan: auth\n```\n"),
    ],
    "o/lib": [issue(4, "Token API", fm(id="token"))],
}


class FakeForge(pmtrack.Forge):
    calls = []

    def issues(self):
        FakeForge.calls.append(self.repo)
        return [dict(i) for i in ISSUES[self.repo]]


CONFIG = """
forge: forgejo
url: https://f.example
repo: o/app
remotes:
  lib: {forge: gitlab, url: https://g.example, repo: o/lib}
subsets:
  - {name: v1, labels: [area/auth]}
labels: ["area/*"]
"""

PLAN = """---
title: Authentication
pm:
  id: auth
  scope: {labels: [area/auth]}
---

# Auth

<!-- pm:progress -->
old
<!-- /pm:progress -->
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / ".pm.yml").write_text(CONFIG)
        (self.root / "docs").mkdir()
        (self.root / "docs/auth.md").write_text(PLAN)
        FakeForge.calls = []

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_review(self, now, *extra):
        return pmtrack.main(["-C", str(self.root), "review", "--now", now, *extra],
                            forge_factory=FakeForge)

    def project(self):
        cfg = pmtrack.load_config(self.root, ".pm.yml")
        p = pmtrack.Project(self.root, cfg, FakeForge)
        p.load_local()
        p.compute()
        return p


class TestParse(unittest.TestCase):
    def test_frontmatter_and_fence(self):
        self.assertEqual(pmtrack.parse_meta(fm(id="x"))[0]["pm"]["id"], "x")
        self.assertEqual(pmtrack.parse_meta("t\n```yaml\npm: {id: y}\n```\n")[0]["pm"]["id"], "y")
        self.assertEqual(pmtrack.parse_meta("plain")[0], {})
        self.assertIn("unparseable", pmtrack.parse_meta("---\npm: [\n---\n")[1])

    def test_checkboxes(self):
        self.assertEqual(pmtrack.checkboxes("- [x] a\n* [X] b\n- [ ] c\n"), (2, 3))


class TestStatus(Base):
    def test_statuses(self):
        p = self.project()
        s = {k: n.status for k, n in p.nodes.items() if n.repo == ""}
        self.assertEqual(s["#1"], "done")
        self.assertEqual(s["#2"], "blocked")      # waits on open lib:token
        self.assertEqual(s["#3"], "blocked")
        self.assertEqual(s["#4"], "blocked")      # unresolved + open dep
        self.assertEqual(s["#5"], "active")       # assigned
        self.assertEqual(s["#6"], "dropped")
        self.assertEqual(s["#9"], "ready")
        self.assertEqual(s["plan:auth"], "ready")   # #9 is ready

    def test_remote_resolved_lazily(self):
        p = self.project()
        self.assertEqual(FakeForge.calls, ["o/app", "o/lib"])
        self.assertIn("lib#4", p.edges["#2"])

    def test_problems(self):
        msgs = [m for _, m in self.project().problems]
        self.assertIn("unresolved dependency `nope`", msgs)
        self.assertTrue(any(m.startswith("dependency cycle") for m in msgs))

    def test_plan_members(self):
        p = self.project()
        keys = sorted(n.key for n in p.members(p.nodes["plan:auth"]))
        self.assertEqual(keys, ["#2", "#3", "#4", "#9"])   # labels or explicit plan

    def test_url_ref(self):
        p = self.project()
        self.assertEqual(p.resolve("https://g.example/o/lib/-/issues/4"), "lib#4")
        self.assertEqual(p.resolve("https://f.example/o/app/issues/3"), "#3")
        self.assertIsNone(p.resolve("https://elsewhere/x/y/issues/1"))


class TestReview(Base):
    def test_writes_and_is_stable(self):
        self.assertEqual(self.run_review("2026-10-21T10:00:00+00:00"), 0)
        out = self.root / "progress"
        readme = (out / "README.md").read_text()
        self.assertIn("| **all** |", readme)
        self.assertIn("| v1 |", readme)
        self.assertIn("```mermaid", readme)
        self.assertIn("classDef blocked", readme)
        self.assertNotIn("| wontfix |", readme)
        self.assertIn("xychart-beta horizontal", readme)
        self.assertIn('pie showData', readme)
        self.assertNotIn("█", readme)
        self.assertIn("Stale", readme)
        doc = (self.root / "docs/auth.md").read_text()
        self.assertIn("[review](../progress/auth.md)", doc)
        self.assertNotIn("old", doc)
        before = {p: p.read_text() for p in out.iterdir()}
        # nothing changed upstream: a later run rewrites nothing
        self.run_review("2026-10-22T10:00:00+00:00")
        self.assertEqual(before, {p: p.read_text() for p in out.iterdir()})
        self.assertEqual(len((out / "history.jsonl").read_text().splitlines()), 1)

    def test_changes_since_baseline(self):
        self.run_review("2026-10-10T10:00:00+00:00")
        ISSUES["o/app"][1]["state"] = "closed"
        try:
            self.run_review("2026-10-21T10:00:00+00:00")
        finally:
            ISSUES["o/app"][1]["state"] = "open"
        readme = (self.root / "progress/README.md").read_text()
        self.assertIn("✓ done: [#2]", readme)
        self.assertIn("blocked → ready", readme)
        hist = [json.loads(l) for l in (self.root / "progress/history.jsonl").read_text().splitlines()]
        self.assertEqual(len(hist), 2)
        self.assertIn("xychart-beta\n", readme)   # trend line


class TestTemplates(Base):
    SRC = """---
template:
  name: Actionable
  about: A unit of work
  labels: [actionable]
pm:
  id: ""
  depends: []
---

## Goal
"""

    def test_generate_and_check(self):
        (self.root / "templates").mkdir()
        (self.root / "templates/actionable.md").write_text(self.SRC)
        args = ["-C", str(self.root), "templates"]
        self.assertEqual(pmtrack.main(args + ["--check"]), 1)
        self.assertEqual(pmtrack.main(args), 0)
        self.assertEqual(pmtrack.main(args + ["--check"]), 0)
        gh = (self.root / ".github/ISSUE_TEMPLATE/actionable.md").read_text()
        gl = (self.root / ".gitlab/issue_templates/actionable.md").read_text()
        self.assertTrue(gh.startswith("---\n# generated"))
        self.assertIn("name: Actionable", gh)
        self.assertIn("---\npm:\n  id: ''", gh)
        self.assertTrue(gl.startswith("---\npm:"))
        self.assertTrue(gl.rstrip().endswith('/label ~"actionable"'))
        meta, _ = pmtrack.parse_meta(gl)
        self.assertEqual(meta["pm"]["depends"], [])


if __name__ == "__main__":
    unittest.main()
