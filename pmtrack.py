#!/usr/bin/env python3
"""pmtrack: project overview and progress review from plan docs and issues.

Forge agnostic: uses only what GitHub, GitLab, Gitea and Forgejo all have
(repo files, issues with title/body/state/labels/assignees, Markdown with
mermaid). Everything else lives in YAML frontmatter under the `pm` key.

Commands:
  pmtrack templates [--check]   write per-forge issue templates from templates/
  pmtrack review    [--dry-run] fetch issues, write the progress review
"""
import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

VERSION = "0.1.0"
NS = "pm"
STATUSES = ("done", "active", "ready", "blocked")
ICON = {"done": "✓", "active": "▶", "ready": "○", "blocked": "✕",
        "dropped": "–", "unknown": "?"}
# Validated (dataviz check) for light and dark surfaces: fill, text.
COLOR = {"done": ("#0ca30c", "#000"), "active": ("#2a78d6", "#fff"),
         "ready": ("#eda100", "#000"), "blocked": ("#d03b3b", "#fff"),
         "unknown": ("#898781", "#000"), "dropped": ("#898781", "#000")}
TEMPLATE_KEYS = ("name", "about", "title", "labels", "assignees", "ref")
DEFAULTS = {
    "forge": "forgejo", "url": None, "repo": None, "token_env": "PM_TOKEN",
    "docs": ["docs"], "out": "progress", "templates": "templates",
    "labels": "*", "ignore_labels": ["wontfix", "duplicate", "invalid"],
    "subsets": [], "remotes": {}, "stale_days": 14, "window_days": 7,
    "graph_limit": 80,
}


# ---------------------------------------------------------------- frontmatter

FM_RE = re.compile(r"\A﻿?\s*---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
FENCE_RE = re.compile(r"^```ya?ml[^\n]*\n(.*?)\n```", re.S | re.M)
CHECK_RE = re.compile(r"^\s*[-*+]\s+\[([ xX])\]", re.M)


def split_frontmatter(text):
    """Return (yaml_text or None, body)."""
    m = FM_RE.match(text or "")
    if not m:
        return None, text or ""
    return m.group(1), (text or "")[m.end():]


def parse_meta(text):
    """Find the pm metadata in a doc or issue body.

    Looks at leading `---` frontmatter first, then at fenced ```yaml blocks
    (fallback for forges that render issue frontmatter badly). Returns
    (full_metadata_dict, error_or_None).
    """
    fm, _ = split_frontmatter(text)
    candidates = ([fm] if fm is not None else []) + FENCE_RE.findall(text or "")
    error = None
    for c in candidates:
        try:
            d = yaml.safe_load(c)
        except yaml.YAMLError as e:
            error = "unparseable YAML: %s" % str(e).splitlines()[0]
            continue
        if isinstance(d, dict) and isinstance(d.get(NS), dict):
            return d, None
        if isinstance(d, dict) and NS in d and d[NS] is not None:
            error = "`%s:` must be a mapping" % NS
    return {}, error


def checkboxes(text):
    marks = CHECK_RE.findall(text or "")
    return sum(1 for m in marks if m.lower() == "x"), len(marks)


def as_list(v):
    if v is None or v == "":
        return []
    return [str(x) for x in v] if isinstance(v, (list, tuple)) else [str(v)]


# --------------------------------------------------------------------- forges

class Forge:
    """Reads issues through each forge's REST API, normalised to one shape:
    number, title, body, state (open|closed), labels, assignees, url, updated.
    """
    page_size = 50

    def __init__(self, kind, url, repo, token=None):
        self.kind, self.url, self.repo, self.token = kind, url.rstrip("/"), repo, token
        if kind not in ("forgejo", "gitea", "github", "gitlab"):
            raise SystemExit("unknown forge %r" % kind)

    @property
    def web(self):
        return "%s/%s" % (self.url, self.repo)

    def _get(self, path, params):
        q = urllib.parse.urlencode(params)
        if self.kind in ("forgejo", "gitea"):
            base, auth = self.url + "/api/v1", ("Authorization", "token %s")
        elif self.kind == "github":
            base = ("https://api.github.com" if self.url == "https://github.com"
                    else self.url + "/api/v3")
            auth = ("Authorization", "Bearer %s")
        else:
            base, auth = self.url + "/api/v4", ("PRIVATE-TOKEN", "%s")
        req = urllib.request.Request("%s%s?%s" % (base, path, q))
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "pmtrack/" + VERSION)
        if self.token:
            req.add_header(auth[0], auth[1] % self.token)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit("%s %s: HTTP %s %s" % (self.kind, self.repo, e.code, e.reason))

    def issues(self):
        out, page = [], 1
        while True:
            if self.kind in ("forgejo", "gitea"):
                batch = self._get("/repos/%s/issues" % self.repo, {
                    "state": "all", "type": "issues", "limit": self.page_size, "page": page})
            elif self.kind == "github":
                batch = self._get("/repos/%s/issues" % self.repo, {
                    "state": "all", "per_page": 100, "page": page})
            else:
                batch = self._get("/projects/%s/issues" % urllib.parse.quote(self.repo, safe=""),
                                  {"state": "all", "per_page": 100, "page": page})
            if not batch:
                return out
            out += [self.normalise(i) for i in batch if not i.get("pull_request")]
            page += 1

    def normalise(self, i):
        if self.kind == "gitlab":
            return {"number": i["iid"], "title": i["title"], "body": i.get("description") or "",
                    "state": "closed" if i["state"] == "closed" else "open",
                    "labels": list(i.get("labels") or []),
                    "assignees": [a["username"] for a in i.get("assignees") or []],
                    "url": i["web_url"], "updated": i.get("updated_at")}
        return {"number": i["number"], "title": i["title"], "body": i.get("body") or "",
                "state": i["state"], "labels": [l["name"] for l in i.get("labels") or []],
                "assignees": [a["login"] for a in i.get("assignees") or []],
                "url": i["html_url"], "updated": i.get("updated_at")}


# ---------------------------------------------------------------------- model

@dataclass
class Node:
    key: str                  # "#12", "lib#4", "plan:auth"
    kind: str                 # issue | plan
    repo: str = ""            # "" = this repo, else remote alias
    title: str = ""
    url: str = ""
    id: str = ""
    depends: list = field(default_factory=list)
    weight: float = 1.0
    labels: list = field(default_factory=list)
    assignees: list = field(default_factory=list)
    state: str = "open"
    updated: str = ""
    checks: tuple = (0, 0)
    plans: list = field(default_factory=list)   # plan ids this issue names
    scope: list = field(default_factory=list)   # plan: labels its issues carry
    path: str = ""                              # plan: doc path
    status: str = ""
    progress: float = 0.0

    @property
    def label(self):
        return "plan " + self.id if self.kind == "plan" else self.key


class Project:
    def __init__(self, root, cfg, forge_factory=Forge):
        self.root, self.cfg, self.forge_factory = Path(root), cfg, forge_factory
        self.nodes, self.ids, self.nums = {}, {}, {}
        self.loaded_remotes = set()
        self.problems = []           # (node_key or "", message)
        self.edges = {}              # key -> [resolved dep keys]
        self.unresolved = {}         # key -> [raw refs]

    # -- loading
    def forge_for(self, alias):
        c = self.cfg if alias == "" else self.cfg["remotes"].get(alias)
        if c is None:
            return None
        token = os.environ.get(c.get("token_env") or self.cfg["token_env"])
        return self.forge_factory(c.get("forge", "forgejo"), c["url"], c["repo"], token)

    def add_issue(self, alias, i):
        meta, err = parse_meta(i["body"])
        pm = meta.get(NS) or {}
        key = "%s#%d" % (alias, i["number"])
        n = Node(key=key, kind="issue", repo=alias, title=i["title"], url=i["url"],
                 id=str(pm.get("id") or "").strip(), depends=as_list(pm.get("depends")),
                 weight=float(pm.get("weight") or 1), labels=i["labels"],
                 assignees=i["assignees"], state=i["state"], updated=i.get("updated") or "",
                 checks=checkboxes(i["body"]), plans=as_list(pm.get("plan")))
        if err and alias == "":
            self.problems.append((key, err))
        self.register(n)

    def register(self, n):
        self.nodes[n.key] = n
        if n.kind == "issue":
            self.nums[(n.repo, int(n.key.split("#")[1]))] = n.key
        if n.id:
            if (n.repo, n.id) in self.ids and n.repo == "":
                self.problems.append((n.key, "duplicate id `%s` (also %s)"
                                      % (n.id, self.nodes[self.ids[(n.repo, n.id)]].label)))
            else:
                self.ids[(n.repo, n.id)] = n.key

    def load_local(self):
        for i in self.forge_for("").issues():
            self.add_issue("", i)
        for d in self.cfg["docs"]:
            base = self.root / d
            for p in sorted(base.rglob("*.md")) if base.is_dir() else []:
                meta, err = parse_meta(p.read_text(encoding="utf-8"))
                pm = meta.get(NS) or {}
                rel = str(p.relative_to(self.root))
                if err:
                    self.problems.append(("", "%s: %s" % (rel, err)))
                if not pm.get("id"):
                    continue
                scope = pm.get("scope") or {}
                self.register(Node(
                    key="plan:" + str(pm["id"]), kind="plan", id=str(pm["id"]),
                    title=str(meta.get("title") or p.stem), url=rel, path=rel,
                    depends=as_list(pm.get("depends")),
                    scope=as_list(scope.get("labels") if isinstance(scope, dict) else scope)))

    def load_remote(self, alias):
        if alias in self.loaded_remotes:
            return
        self.loaded_remotes.add(alias)
        forge = self.forge_for(alias)
        if forge:
            for i in forge.issues():
                self.add_issue(alias, i)

    # -- references
    def resolve(self, ref, alias=""):
        """Ref forms: id, #12, alias:id, alias#12, or a full issue URL."""
        ref = ref.strip()
        if "://" in ref:
            for a, c in [("", self.cfg)] + list(self.cfg["remotes"].items()):
                web = "%s/%s/" % (c["url"].rstrip("/"), c["repo"])
                m = re.match(re.escape(web) + r"(?:-/)?issues/(\d+)\b", ref)
                if m:
                    return self.resolve("%s#%s" % (a, m.group(1)))
            return None
        m = re.fullmatch(r"([A-Za-z0-9_.-]*)#(\d+)", ref)
        if m:
            a = m.group(1) or alias
            if a:
                self.load_remote(a)
            return self.nums.get((a, int(m.group(2))))
        a, _, ident = ref.rpartition(":")
        a = a or alias
        if a and a not in self.cfg["remotes"]:
            return None
        if a:
            self.load_remote(a)
        return self.ids.get((a, ident))

    # -- status
    def members(self, plan):
        return [n for n in self.local_issues()
                if plan.id in n.plans or (plan.scope and set(plan.scope) <= set(n.labels))]

    def local_issues(self):
        return sorted((n for n in self.nodes.values() if n.kind == "issue" and n.repo == ""),
                      key=lambda n: int(n.key[1:]))

    def compute(self):
        visiting = set()

        def status(key):
            n = self.nodes[key]
            if n.status:
                return n.status
            if key in visiting:
                self.problems.append((key, "dependency cycle through %s" % n.label))
                return "blocked"
            visiting.add(key)
            deps, missing = [], []
            if n.repo == "":   # remote nodes: only their own state counts
                for r in n.depends:
                    k = self.resolve(r)
                    (deps if k else missing).append(k or r)
            self.edges[key], self.unresolved[key] = deps, missing
            for r in missing:
                self.problems.append((key, "unresolved dependency `%s`" % r))
            dep_ok = all(status(k) in ("done", "dropped") for k in deps) and not missing
            if n.kind == "plan":
                ms = [m for m in self.members(n)]
                live = [status(m.key) for m in ms if status(m.key) != "dropped"]
                n.status = ("done" if live and all(s == "done" for s in live) else
                            "blocked" if not dep_ok else
                            "active" if any(s in ("done", "active") for s in live) else
                            "ready" if "ready" in live or not live else "blocked")
            elif n.state == "closed":
                n.status = "dropped" if set(n.labels) & set(self.cfg["ignore_labels"]) else "done"
            elif not dep_ok:
                n.status = "blocked"
            elif n.assignees or n.checks[0]:
                n.status = "active"
            else:
                n.status = "ready"
            done, total = n.checks
            n.progress = 1.0 if n.status == "done" else (done / total if total else 0.0)
            visiting.discard(key)
            return n.status

        for key in list(self.nodes):
            if self.nodes[key].repo == "":
                status(key)
        for key, deps in self.edges.items():
            for k in deps:
                if self.nodes[k].status == "dropped":
                    self.problems.append((key, "depends on dropped %s" % self.nodes[k].label))

    # -- subsets
    def subsets(self):
        """[(name, kind, [issue nodes])] in display order."""
        issues = self.local_issues()
        out = [("all", "all", issues)]
        for s in self.cfg["subsets"]:
            want = set(as_list(s.get("labels")))
            out.append((s["name"], "subset", [n for n in issues if want <= set(n.labels)]))
        pats = as_list(self.cfg["labels"])
        labels = sorted({l for n in issues for l in n.labels} - set(self.cfg["ignore_labels"]))
        for l in labels:
            if any(fnmatch.fnmatchcase(l, p) for p in pats):
                out.append((l, "label", [n for n in issues if l in n.labels]))
        return out

    def plans(self):
        return sorted((n for n in self.nodes.values() if n.kind == "plan"), key=lambda n: n.id)

    def downstream(self, key):
        """Open local nodes that (transitively) wait on key."""
        rev = {}
        for k, deps in self.edges.items():
            for d in deps:
                rev.setdefault(d, set()).add(k)
        seen, todo = set(), [key]
        while todo:
            for k in rev.get(todo.pop(), ()):
                if k not in seen and self.nodes[k].status not in ("done", "dropped"):
                    seen.add(k)
                    todo.append(k)
        return seen


def tally(nodes):
    live = [n for n in nodes if n.status != "dropped"]
    c = {s: sum(1 for n in live if n.status == s) for s in STATUSES}
    w = sum(n.weight for n in live)
    c["total"] = len(live)
    c["pct"] = round(100 * sum(n.weight * n.progress for n in live) / w) if w else 0
    return c


# ------------------------------------------------------------------- history

def load_history(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def baseline(history, now, days):
    """Latest snapshot at or before now - days; else the oldest one."""
    cut = (now - dt.timedelta(days=days)).isoformat()
    older = [h for h in history if h["date"] <= cut]
    return older[-1] if older else (history[0] if history else None)


# ------------------------------------------------------------------ rendering

def mq(s):
    """Quote text for a mermaid string."""
    return '"%s"' % str(s).replace('"', "'")


def bar_chart(rows, title="% done"):
    """rows: [(name, pct)] -> horizontal mermaid xychart."""
    if not rows:
        return []
    return ["```mermaid", "xychart-beta horizontal", "  title %s" % mq(title),
            "  x-axis [%s]" % ", ".join(mq(n) for n, _ in rows),
            '  y-axis "% done" 0 --> 100',
            "  bar [%s]" % ", ".join(str(p) for _, p in rows), "```"]


def pie_chart(c, title):
    """Status breakdown. Mermaid orders slices by size, so each slice is
    named; colour alone does not identify a status."""
    parts = [(s, c[s]) for s in STATUSES if c[s]]
    if not parts:
        return []
    return ["```mermaid", "pie showData title %s" % title.replace('"', "'")] + [
        "  %s : %d" % (mq("%s %s" % (ICON[s], s)), n) for s, n in parts] + ["```"]


def esc(s):
    return str(s).replace("|", "\\|").replace("<", "&lt;").replace("\n", " ")


def link(n, rel_to=""):
    if n.kind == "plan":
        return "[%s](%s)" % (esc(n.title), os.path.relpath(n.path, rel_to or "."))
    return "[%s](%s) %s" % (n.label, n.url, esc(n.title))


def counts_cells(c):
    return " | ".join(str(c[s]) for s in STATUSES)


def delta(now_pct, base, name):
    if not base or name not in base["subsets"]:
        return "new"
    d = now_pct - base["subsets"][name]["pct"]
    return "±0" if d == 0 else "%+d" % d


def mermaid_graph(proj, keys, limit):
    keys = [k for k in keys if proj.nodes[k].status != "dropped"]
    if len(keys) > limit:   # keep it readable: open work and what it waits on
        keys = [k for k in keys if proj.nodes[k].status not in ("done", "dropped")]
        keys = keys[:limit]
    shown = set(keys)
    for k in list(keys):
        shown |= set(proj.edges.get(k, []))
    ids = {k: "n%d" % i for i, k in enumerate(sorted(shown))}
    lines = ["```mermaid", "flowchart LR"]
    for k in sorted(shown):
        n = proj.nodes[k]
        title = n.title if len(n.title) <= 32 else n.title[:31] + "…"
        text = "%s %s %s" % (ICON.get(n.status, "?"), n.label, title)
        text = text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")
        shape = '[["%s"]]' if n.kind == "plan" else '["%s"]'
        lines.append("  %s%s:::%s" % (ids[k], shape % text, n.status or "unknown"))
    for k in sorted(shown):
        n = proj.nodes[k]
        if n.kind == "plan":   # dotted: plan to the items it tracks
            for m in proj.members(n):
                if m.key in shown:
                    lines.append("  %s -.- %s" % (ids[k], ids[m.key]))
        for d in proj.edges.get(k, []):
            if d in shown and k in shown:
                lines.append("  %s --> %s" % (ids[d], ids[k]))
        for i, r in enumerate(proj.unresolved.get(k, [])):
            uid = "%s_u%d" % (ids[k], i)
            lines.append('  %s["? %s"]:::unknown --> %s' % (uid, r.replace('"', "#quot;"), ids[k]))
    for s, (fill, ink) in COLOR.items():
        lines.append("  classDef %s fill:%s,color:%s,stroke:%s" % (s, fill, ink, fill))
    lines.append("```")
    return lines


LEGEND = ("_Legend: %s done · %s active (assigned or partly ticked) · %s ready "
          "(nothing it waits on is open) · %s blocked · arrows point from a "
          "dependency to what waits on it; dotted lines join a plan to its items._" % (ICON["done"], ICON["active"],
                                                 ICON["ready"], ICON["blocked"]))


def changes_section(proj, nodes, base, date):
    if not base:
        return ["_No earlier snapshot yet; changes appear from the next update._"]
    before = base["nodes"]
    lines, moved, new, closed = [], [], [], []
    for n in nodes:
        was = before.get(n.key)
        if was is None:
            new.append(n)
        elif was != n.status:
            (closed if n.status == "done" else moved).append((n, was))
    for n, _ in closed:
        lines.append("- %s done: %s" % (ICON["done"], link(n)))
    for n, was in moved:
        lines.append("- %s → %s: %s" % (was, n.status, link(n)))
    for n in new:
        lines.append("- new (%s): %s" % (n.status, link(n)))
    head = "From %s to %s UTC:" % (base["date"][:16].replace("T", " "),
                                   date[:16].replace("T", " "))
    return [head, ""] + (lines or ["- no changes"])


def attention_section(proj, nodes, now, rel_to=""):
    lines = []
    blocked = [n for n in nodes if n.status == "blocked"]
    if blocked:
        lines += ["### %s Blocked" % ICON["blocked"], ""]
        for n in blocked:
            waits = ["%s %s" % (ICON.get(proj.nodes[k].status, "?"), link(proj.nodes[k], rel_to))
                     for k in proj.edges.get(n.key, [])
                     if proj.nodes[k].status not in ("done", "dropped")]
            waits += ["? `%s` (unresolved)" % r for r in proj.unresolved.get(n.key, [])]
            lines.append("- %s, waiting on %s" % (link(n, rel_to), ", ".join(waits) or "a cycle"))
        lines.append("")
    stale_cut = (now - dt.timedelta(days=proj.cfg["stale_days"])).isoformat()
    stale = [n for n in nodes if n.status == "active" and n.updated and n.updated < stale_cut]
    if stale:
        lines += ["### Stale (active, no update in %d days)" % proj.cfg["stale_days"], ""]
        lines += ["- %s, last update %s" % (link(n), n.updated[:10]) for n in stale] + [""]
    keys = {n.key for n in nodes}
    probs = [(k, m) for k, m in proj.problems if not k or k in keys]
    if probs:
        lines += ["### Metadata problems", ""]
        for k, m in dict.fromkeys(probs):
            lines.append("- %s%s" % ((link(proj.nodes[k], rel_to) + ": ") if k else "", m))
        lines.append("")
    return lines or ["Nothing blocked, stale or malformed."]


def next_up(proj, nodes):
    ready = [n for n in nodes if n.status == "ready"]
    ready.sort(key=lambda n: (-len(proj.downstream(n.key)), n.key))
    if not ready:
        return ["Nothing ready to start."]
    out = []
    for n in ready[:15]:
        k = len(proj.downstream(n.key))
        out.append("- %s %s%s" % (ICON["ready"], link(n), " (unblocks %d)" % k if k else ""))
    return out


def trend(history, name):
    pts = [(h["date"][5:10], h["subsets"][name]["pct"]) for h in history[-30:]
           if name in h["subsets"]]
    if len(pts) < 2:
        return []
    return ["```mermaid", "xychart-beta",
            '  title "%s: %% done"' % name.replace('"', "'"),
            "  x-axis [%s]" % ", ".join('"%s"' % d for d, _ in pts),
            '  y-axis "%" 0 --> 100',
            "  line [%s]" % ", ".join(str(p) for _, p in pts), "```"]


def render_overview(proj, date, now, base, history):
    out = proj.cfg["out"]
    L = ["# Progress review", "",
         "_Data as of %s UTC · changes compared with %s · generated by pmtrack %s_" % (
             date[:16].replace("T", " "), base["date"][:10] if base else "nothing yet", VERSION),
         ""]
    subsets = [(name, kind, tally(nodes)) for name, kind, nodes in proj.subsets()]
    L += bar_chart([(n, c["pct"]) for n, _, c in subsets], "% done by subset")
    L += ["", "| Subset | %% done | %s done | %s active | %s ready | %s blocked | Δ %% pts |"
          % tuple(ICON[s] for s in STATUSES), "|---|--:|--:|--:|--:|--:|--:|"]
    for name, kind, c in subsets:
        L.append("| %s | %d | %s | %s |" % (
            "**%s**" % name if kind == "all" else esc(name), c["pct"],
            counts_cells(c), delta(c["pct"], base, name)))
    L += [""] + pie_chart(subsets[0][2], "All items by status")
    plans = proj.plans()
    if plans:
        pc = [(p, tally(proj.members(p))) for p in plans]
        L += ["", "## Plans", ""] + bar_chart([(p.id, c["pct"]) for p, c in pc], "% done by plan")
        L += ["", "| Plan | %% done | %s | %s | %s | %s | Review |"
              % tuple(ICON[s] for s in STATUSES), "|---|--:|--:|--:|--:|--:|---|"]
        for p, c in pc:
            L.append("| %s %s | %d | %s | [%s.md](%s.md) |" % (
                ICON.get(p.status, "?"), link(p, out), c["pct"], counts_cells(c), p.id, p.id))
    issues = proj.local_issues()
    L += ["", "## Changes", ""] + changes_section(proj, issues, base, date)
    L += ["", "## Needs attention", ""] + attention_section(proj, issues, now, out)
    L += ["", "## Next up", "", "_Ready items, those that unblock the most first._", ""]
    L += next_up(proj, issues)
    L += ["", "## Dependency graph", "", LEGEND, ""]
    L += mermaid_graph(proj, [n.key for n in issues] + [p.key for p in plans],
                       proj.cfg["graph_limit"])
    t = trend(history, "all")
    if t:
        L += ["", "## Trend", ""] + t
    return "\n".join(L) + "\n"


def render_plan(proj, plan, date, now, base, history):
    out = proj.cfg["out"]
    ms = proj.members(plan)
    c = tally(ms)
    L = ["# %s %s" % (ICON.get(plan.status, "?"), esc(plan.title)), "",
         "_Plan `%s` · [doc](%s) · data as of %s UTC · [all subsets](README.md)_" % (
             plan.id, os.path.relpath(plan.path, out), date[:16].replace("T", " ")), "",
         "**%d%% done** · %s" % (c["pct"], summary(c)), ""] + pie_chart(c, "Items by status") + ["",
         "| Item | Status | Ticked | Depends on |", "|---|---|--:|---|"]
    for n in sorted(ms, key=lambda n: (STATUSES.index(n.status) if n.status in STATUSES else 9, n.key)):
        deps = ", ".join("%s %s" % (ICON.get(proj.nodes[k].status, "?"), proj.nodes[k].label)
                         for k in proj.edges.get(n.key, []))
        deps += "".join(", ? `%s`" % r for r in proj.unresolved.get(n.key, []))
        L.append("| %s | %s %s | %s | %s |" % (
            link(n), ICON.get(n.status, "?"), n.status,
            "%d/%d" % n.checks if n.checks[1] else "", deps.lstrip(", ")))
    L += ["", "## Changes", ""] + changes_section(proj, ms, base, date)
    L += ["", "## Needs attention", ""] + attention_section(proj, ms, now, out)
    L += ["", "## Next up", ""] + next_up(proj, ms)
    L += ["", "## Dependency graph", "", LEGEND, ""]
    L += mermaid_graph(proj, [n.key for n in ms], proj.cfg["graph_limit"])
    t = trend(history, "plan:" + plan.id)
    if t:
        L += ["", "## Trend", ""] + t
    return "\n".join(L) + "\n"


def summary(c):
    return " · ".join("%s %d %s" % (ICON[s], c[s], s) for s in STATUSES)


MARK_RE = re.compile(r"(<!-- pm:progress -->)(.*?)(<!-- /pm:progress -->)", re.S)


def fill_doc(proj, plan, text):
    c = tally(proj.members(plan))
    page = os.path.relpath(Path(proj.cfg["out"]) / (plan.id + ".md"), Path(plan.path).parent)
    block = "\n".join(["", "**%d%% done** · %s · [review](%s)" % (c["pct"], summary(c), page), ""]
                      + pie_chart(c, "Items by status") + [""])
    return MARK_RE.sub(lambda m: m.group(1) + block + m.group(3), text)


# --------------------------------------------------------------------- review

def snapshot(proj):
    snap = {"nodes": {n.key: n.status for n in proj.local_issues()}, "subsets": {}}
    for name, _, nodes in proj.subsets():
        snap["subsets"][name] = tally(nodes)
    for p in proj.plans():
        snap["subsets"]["plan:" + p.id] = tally(proj.members(p))
    return snap


def cmd_review(root, cfg, args, forge_factory=Forge):
    now = (dt.datetime.fromisoformat(args.now) if args.now
           else dt.datetime.now(dt.timezone.utc)).replace(microsecond=0)
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    proj = Project(root, cfg, forge_factory)
    proj.load_local()
    proj.compute()
    out = root / cfg["out"]
    hist_path = out / "history.jsonl"
    history = load_history(hist_path)
    snap = snapshot(proj)
    last = history[-1] if history else None
    if not last or {k: last[k] for k in ("nodes", "subsets")} != snap:
        snap = {"date": now.isoformat()} | snap
        history.append(snap)
    date = history[-1]["date"]
    data_now = dt.datetime.fromisoformat(date)
    base = baseline(history[:-1], data_now, cfg["window_days"])
    files = {out / "README.md": render_overview(proj, date, data_now, base, history)}
    for p in proj.plans():
        files[out / (p.id + ".md")] = render_plan(proj, p, date, data_now, base, history)
        doc = root / p.path
        text = doc.read_text(encoding="utf-8")
        files[doc] = fill_doc(proj, p, text)
    files[hist_path] = "".join(json.dumps(h, sort_keys=True) + "\n" for h in history)
    changed = 0
    for path, text in files.items():
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        changed += 1
        if args.dry_run:
            print("would write %s" % path.relative_to(root))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("wrote %s" % path.relative_to(root))
    c = tally(proj.local_issues())
    print("%d%% done · %s · %d metadata problem(s) · %d file(s) changed" % (
        c["pct"], summary(c), len(set(proj.problems)), changed))
    return 1 if args.strict and proj.problems else 0


# ------------------------------------------------------------------ templates

def dump(d):
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True, default_flow_style=None)


def build_templates(root, cfg):
    """templates/<name>.md -> per-forge files. Source frontmatter holds the
    forge template settings under `template:`; everything else is copied
    into the new issue's own frontmatter."""
    src = root / cfg["templates"]
    out = {}
    for p in sorted(src.glob("*.md")) if src.is_dir() else []:
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"))
        meta = yaml.safe_load(fm or "") or {}
        tmpl = meta.pop("template", None) or {}
        bad = set(tmpl) - set(TEMPLATE_KEYS)
        if bad:
            raise SystemExit("%s: unknown template keys %s" % (p, sorted(bad)))
        tmpl.setdefault("name", p.stem)
        tmpl.setdefault("about", tmpl["name"])
        own = ("---\n%s---\n" % dump(meta)) if meta else ""
        rel = p.relative_to(root)
        out[root / ".github/ISSUE_TEMPLATE" / p.name] = (
            "---\n# generated by pmtrack from %s; edit that file instead\n%s---\n%s%s"
            % (rel, dump(tmpl), own, body))
        actions = "".join('/label ~"%s"\n' % l for l in as_list(tmpl.get("labels")))
        actions += "".join("/assign @%s\n" % a for a in as_list(tmpl.get("assignees")))
        out[root / ".gitlab/issue_templates" / p.name] = (
            own + body + ("\n" + actions if actions else ""))
    return out


def cmd_templates(root, cfg, args):
    files = build_templates(root, cfg)
    stale = [p for p, t in files.items()
             if not p.exists() or p.read_text(encoding="utf-8") != t]
    if args.check:
        for p in stale:
            print("out of date: %s" % p.relative_to(root))
        print("%d template file(s), %d out of date" % (len(files), len(stale)))
        return 1 if stale else 0
    for p in stale:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(files[p], encoding="utf-8")
        print("wrote %s" % p.relative_to(root))
    print("%d template file(s), %d written" % (len(files), len(stale)))
    return 0


# ------------------------------------------------------------------------ cli

def load_config(root, name):
    path = root / name
    if not path.exists():
        raise SystemExit("no %s in %s" % (name, root))
    cfg = dict(DEFAULTS)
    cfg.update(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    cfg["docs"] = as_list(cfg["docs"])
    for alias in cfg["remotes"]:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", alias):
            raise SystemExit("remote alias %r: use letters, digits, _ . -" % alias)
    return cfg


def main(argv=None, forge_factory=Forge):
    ap = argparse.ArgumentParser(prog="pmtrack", description=__doc__.split("\n")[0])
    ap.add_argument("-C", dest="root", default=".", help="project root (default .)")
    ap.add_argument("-c", dest="config", default=".pm.yml", help="config file in root")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("templates", help="write per-forge issue templates")
    t.add_argument("--check", action="store_true", help="only report out-of-date files")
    r = sub.add_parser("review", help="write the progress review")
    r.add_argument("--dry-run", action="store_true", help="show what would change")
    r.add_argument("--strict", action="store_true", help="exit 1 on metadata problems")
    r.add_argument("--now", help="ISO timestamp to use as now (tests)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    cfg = load_config(root, args.config)
    if args.cmd == "templates":
        return cmd_templates(root, cfg, args)
    return cmd_review(root, cfg, args, forge_factory)


if __name__ == "__main__":
    sys.exit(main())
