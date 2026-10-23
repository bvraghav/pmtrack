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


class TestForge(unittest.TestCase):
    def test_pull_requests_skipped_but_null_key_kept(self):
        raw = [{"number": 1, "title": "i", "body": None, "state": "open", "labels": [],
                "assignees": None, "html_url": "u", "pull_request": None},
               {"number": 2, "title": "pr", "state": "open", "html_url": "u",
                "pull_request": {"merged": False}}]
        f = pmtrack.Forge("forgejo", "https://f", "o/r")
        f.page_size = 2
        pages = iter([raw, []])
        f._get = lambda path, params: next(pages)
        self.assertEqual([i["number"] for i in f.issues()], [1])

    def test_paging_stops_on_short_page(self):
        def issue(n, pr=False):
            return {"number": n, "title": "t", "state": "open", "labels": [], "html_url": "u",
                    **({"pull_request": {"url": "u"}} if pr else {})}
        for kind, size_key in (("github", "per_page"), ("gitlab", "per_page"), ("forgejo", "limit")):
            f = pmtrack.Forge(kind, "https://f", "o/r")
            f.page_size = 2
            if kind == "gitlab":
                f.normalise = lambda i: i
            # GitLab's issue list has no merge requests in it.
            pages = iter([[issue(1), issue(2, pr=kind != "gitlab")], [issue(3)]])
            seen = []
            f._get = lambda path, params: (seen.append(params), next(pages))[1]
            want = [1, 2, 3] if kind == "gitlab" else [1, 3]
            self.assertEqual([i["number"] for i in f.issues()], want)
            self.assertEqual([(p["page"], p[size_key]) for p in seen], [(1, 2), (2, 2)])


    def test_unreachable_forge_is_a_clean_error(self):
        f = pmtrack.Forge("forgejo", "https://nowhere.invalid", "o/r")
        with self.assertRaises(SystemExit) as e:
            f.issues()
        self.assertIn("can't reach https://nowhere.invalid/api/v1", str(e.exception))

    def test_file_url(self):
        u = lambda kind: pmtrack.Forge(kind, "https://x.example/", "o/r").file_url("docs/a.md", "dev")
        self.assertEqual(u("forgejo"), "https://x.example/o/r/src/branch/dev/docs/a.md")
        self.assertEqual(u("github"), "https://x.example/o/r/blob/dev/docs/a.md")
        self.assertEqual(u("gitlab"), "https://x.example/o/r/-/blob/dev/docs/a.md")
    def test_gitlab_normalise(self):
        f = pmtrack.Forge("gitlab", "https://g", "grp/r")
        n = f.normalise({"iid": 3, "title": "t", "description": None, "state": "opened",
                         "labels": ["a"], "assignees": [{"username": "u"}],
                         "web_url": "w", "updated_at": "x"})
        self.assertEqual((n["number"], n["state"], n["body"], n["assignees"]), (3, "open", "", ["u"]))


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

    def test_every_dependency_gets_a_status(self):
        saved = dict(ISSUES)
        ISSUES["o/app"] = saved["o/app"] + [
            issue(10, "Both", fm(depends=["#3", "lib#5"]))]
        ISSUES["o/lib"] = saved["o/lib"] + [issue(5, "Shipped", state="closed")]
        try:
            p = self.project()
        finally:
            ISSUES.update(saved)
        self.assertEqual(p.nodes["#10"].status, "blocked")
        self.assertEqual(p.nodes["lib#5"].status, "done")

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


    def test_plan_page_names_what_it_waits_on(self):
        (self.root / "docs/release.md").write_text(
            "---\ntitle: Release\npm:\n  id: release\n  depends: [auth, db, gone]\n"
            "  scope: {labels: [area/docs]}\n---\n")
        (self.root / "docs/ui.md").write_text(   # #2, #3, #4: all blocked
            "---\ntitle: UI\npm:\n  id: ui\n  scope: {labels: [area/auth]}\n---\n")
        p = self.project()
        rel = pmtrack.plan_blockers(p, p.nodes["plan:release"], "progress")
        self.assertEqual(p.nodes["plan:release"].status, "blocked")
        self.assertIn("Depends on: ", rel[0])
        self.assertIn("[#1](", rel[0])                     # done deps listed too
        waits = rel[2]
        self.assertIn("waiting on ○ [Authentication](../docs/auth.md)", waits)
        self.assertIn("? `gone` (unresolved)", waits)
        self.assertNotIn("#1", waits)                      # done: not waited on
        self.assertEqual(pmtrack.plan_blockers(p, p.nodes["plan:auth"]), [])
        self.assertIn("every open item is blocked", pmtrack.plan_blockers(p, p.nodes["plan:ui"])[0])
    def test_url_ref(self):
        p = self.project()
        self.assertEqual(p.resolve("https://g.example/o/lib/-/issues/4"), "lib#4")
        self.assertEqual(p.resolve("https://g.example/o/lib/-/work_items/4"), "lib#4")
        self.assertEqual(p.resolve("https://f.example/o/app/issues/3"), "#3")
        self.assertIsNone(p.resolve("https://elsewhere/x/y/issues/1"))


    def test_graph_over_limit_warns_and_is_skipped(self):
        import contextlib, io
        p = self.project()
        keys = [k for k, n in p.nodes.items() if n.repo == ""]
        drawn = pmtrack.graph_section(p, keys, 100, "x.md")
        self.assertIn("```mermaid", drawn)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            out = pmtrack.graph_section(p, keys, 2, "x.md")
        self.assertNotIn("```mermaid", "\n".join(out))
        self.assertIn("graph_limit", out[0])
        self.assertIn("warning: x.md", err.getvalue())

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


    def test_publish_writes_elsewhere_and_leaves_docs(self):
        pub = self.root / "pub"
        before = (self.root / "docs/auth.md").read_text()
        args = ("--publish", str(pub), "--ref", "main")
        self.run_review("2026-10-21T10:00:00", *args)
        self.assertEqual((self.root / "docs/auth.md").read_text(), before)
        self.assertFalse((self.root / "progress").exists())
        self.assertTrue((pub / "history.jsonl").exists())
        page = (pub / "auth.md").read_text()
        self.assertIn("[doc](https://f.example/o/app/src/branch/main/docs/auth.md)", page)
        self.assertIn("(https://f.example/o/app/src/branch/main/docs/auth.md)",
                      (pub / "README.md").read_text())
        stamp = (pub / "README.md").stat().st_mtime_ns
        self.run_review("2026-10-21T11:00:00", *args)     # same data: nothing written
        self.assertEqual((pub / "README.md").stat().st_mtime_ns, stamp)
        with self.assertRaises(SystemExit):
            self.run_review("2026-10-21T12:00:00", "--publish", str(pub))
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


class TestCharts(unittest.TestCase):
    def test_pie_colour_follows_status_not_position(self):
        c = {"done": 2, "active": 0, "ready": 5, "blocked": 1}
        src = "\n".join(pmtrack.pie_chart(c, "t"))
        init = json.loads(src.split("%%{init: ")[1].split("}%%")[0])["themeVariables"]
        # active is empty and skipped, so ready is the 2nd slice and gets ready's colour
        self.assertEqual([init["pie1"], init["pie2"], init["pie3"]],
                         [pmtrack.COLOR[s][0] for s in ("done", "ready", "blocked")])
        self.assertEqual(init["pieOpacity"], "1")
        self.assertLess(src.index('"✓ done"'), src.index('"○ ready"'))

    def test_bar_labels_carry_values(self):
        src = "\n".join(pmtrack.bar_chart([("all", 22), ("x", 0)]))
        self.assertIn('x-axis ["all · 22%", "x · 0%"]', src)
        self.assertIn("bar [22, 0]\n  bar [0, 0]\n```", src)   # bars, then the mask at 0
        self.assertIn('"plotColorPalette": "#0ca30c,#ffffff"', src)
        self.assertIn("plotColorPalette", src)

    def test_trend_by_day(self):
        h = lambda d, p, t=10: {"date": d, "subsets": {"all": {"pct": p, "total": t}}}
        one_day = [h("2026-10-22T10:00:00", 5), h("2026-10-22T20:00:00", 20)]
        self.assertTrue(pmtrack.trend(one_day, "all")[0].startswith("_The trend starts"))
        src = "\n".join(pmtrack.trend(one_day + [h("2026-10-23T09:00:00", 25, 12)], "all"))
        self.assertIn('x-axis ["10-22 · 2/10", "10-23 · 3/12"]', src)   # last snapshot per day
        self.assertIn('y-axis "items" 0 --> 14', src)
        self.assertIn("bar [0, 1]\n  bar [0, 0]\n  bar [0, 0]\n  bar [0, 0]\n  line", src)
        self.assertIn("line [10, 12]", src)     # scope
        self.assertIn("line [2, 3]", src)       # items done

    def test_trend_partial_credit_reopen_and_window(self):
        h = lambda d, p: {"date": "2026-10-%02dT10:00:00" % d, "subsets": {"all": {"pct": p, "total": 4}}}
        src = "\n".join(pmtrack.trend([h(1, 25), h(2, 50), h(3, 30)], "all"))
        self.assertIn('y-axis "items" -1 --> 6', src)   # room below 0 for the loss
        self.assertIn("bar [0, 1, 0]", src)          # gains
        self.assertIn("bar [0, 0, -0.8]", src)       # losses, drawn below 0
        self.assertIn("line [1, 2, 1.2]", src)       # partial credit, one decimal
        old, pmtrack.TREND_DAYS = pmtrack.TREND_DAYS, 2
        try:   # the first day shown still gets its gain from the day before it
            src = "\n".join(pmtrack.trend([h(1, 25), h(2, 50), h(3, 30)], "all"))
        finally:
            pmtrack.TREND_DAYS = old
        self.assertIn("bar [1, 0]", src)

    def test_long_trend_turns_dates_upright(self):
        h = [{"date": "2026-10-%02dT10:00:00" % d, "subsets": {"all": {"pct": d, "total": 5}}}
             for d in range(1, 13)]
        src = "\n".join(pmtrack.trend(h, "all"))
        self.assertIn('"labelRotation": -90', src)
        self.assertIn('"10-12"', src)
        self.assertNotIn("·", src)


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
