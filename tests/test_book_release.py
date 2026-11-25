import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import book_release as controller
import release_policy as policy


class Repository(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.g("init", "-q", "-b", "main")
        self.g("config", "user.email", "book@example.test")
        self.g("config", "user.name", "Book test")
        self.g("config", "commit.gpgsign", "false")
        self.g("config", "tag.gpgsign", "false")
        self.cfg = {"version": "2.2.0", "file_stem": "Book", "html_zip_stem": "Web"}
        self.chapter = "manuscript/01-intro.md"
        self.write(policy.META, json.dumps(self.cfg))
        self.write(self.chapter, "# First chapter\n")
        self.write("CHANGELOG.md", "## [Unreleased]\n\n## [2.2.0] - 2026-11-18\n\nOld.\n")
        self.stable = self.commit()
        self.g("tag", "v2.2.0")
        self.write(self.chapter, "# Revised first chapter\n")
        self.base = self.commit()

    def g(self, *args):
        return policy.git(self.root, *args).strip()

    def commit(self):
        self.g("add", "-A")
        self.g("commit", "-qm", "fixture")
        return self.g("rev-parse", "HEAD")

    def write(self, name, text):
        file = self.root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")

    def prepare(self, **extra):
        self.cfg.update(version="2.3.0")
        self.cfg.update(extra)
        self.write(policy.META, json.dumps(self.cfg))
        self.write("CHANGELOG.md", "## [Unreleased]\n\n## [2.3.0] - 2026-11-24\n\nCatch up.\n")
        return self.commit()

    def validate(self, head):
        return policy.validate(self.root, self.base, head)


class PolicyTests(Repository):
    def test_catchup_is_content_even_if_only_metadata_in_pr(self):
        self.assertEqual(self.validate(self.prepare()), "v2.3.0")

    def test_no_content_since_tag(self):
        self.g("switch", "-qc", "clean", self.stable)
        self.base = self.stable
        with self.assertRaisesRegex(policy.Rejected, "without reader-facing"):
            self.validate(self.prepare())

    def test_tooling_only_during_drift(self):
        self.write("tools/build.py", "# tooling")
        self.assertIsNone(self.validate(self.commit()))
        with self.assertRaisesRegex(policy.Rejected, "Separate content"):
            self.validate(self.prepare())

    def test_config_restricted_even_when_mixed_with_metadata(self):
        with self.assertRaisesRegex(policy.Rejected, "tools/book.json"):
            self.validate(self.prepare(file_stem="Other"))

    def test_config_only_is_tooling(self):
        self.write(policy.META, json.dumps(dict(self.cfg, file_stem="Other")))
        self.assertIsNone(self.validate(self.commit()))

    def test_content_must_advance_and_tag_must_be_unused(self):
        self.write(self.chapter, "changed")
        with self.assertRaisesRegex(policy.Rejected, "Tag already exists|exceed"):
            self.validate(self.commit())
        h = self.prepare()
        self.g("tag", "v2.3.0", h)
        with self.assertRaises(policy.Rejected):
            self.validate(h)

    def test_evidence_bound_to_chapter(self):
        self.write(self.chapter, "changed")
        h = self.prepare()
        for file in ["editorial/01-intro-editorial-log.md", "editorial/fidelity/01-intro.md", "VALIDATION.md"]:
            with self.assertRaises(policy.Rejected):
                self.validate(h)
            self.write(file, "reviewed with source")
            h = self.commit()
        self.assertEqual(self.validate(h), "v2.3.0")

    def test_allowlist(self):
        for p in ["manuscript/x", "figures/a.svg", "outline/ch", "editorial/log", "VALIDATION.md",
                  "tools/book.json", "CHANGELOG.md"]:
            self.assertTrue(policy.allowed(p), p)
        for p in ["tools/build.py", "manuscript.bak/ch", "theme/x", ".github/workflows/release.yml", "infra/x"]:
            self.assertFalse(policy.allowed(p), p)

    def test_dated_nonempty_unique_notes(self):
        for text in ["## [2.3.1] - 2026-11-18\nbody", "## [2.3.0] - unreleased\nbody",
                     "## [2.3.0] - 2026-02-30\nbody", "## [2.3.0] - 2026-11-18\n",
                     "## [2.3.0] - 2026-11-18\none\n## [2.3.0] - 2026-11-19\ntwo"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                policy.release_notes(text, "2.3.0")

    def test_latest(self):
        tags = ["v2.9.0", "v2.10.0", "v3.0.0-rc.10", "other"]
        self.assertTrue(policy.latest("v2.10.0", tags))
        self.assertFalse(policy.latest("v2.9.0", tags))
        self.assertFalse(policy.latest("v3.0.0-rc.10", tags))
        self.assertLess(policy.semver("3.0.0-rc.2"), policy.semver("3.0.0-rc.10"))
        self.assertLess(policy.semver("3.0.0-rc.10"), policy.semver("3.0.0"))


def review(head, state="APPROVED", date="2026-11-21", rid=1):
    return {"user": {"login": "webmaxru"}, "commit_id": head, "state": state, "submitted_at": date, "id": rid}


class ApprovalTests(unittest.TestCase):
    head = "a" * 40

    def setUp(self):
        self.pr = {"head": {"sha": self.head}, "user": {"login": "writer"}}
        self.dismissed = [{"event": "review_dismissed", "created_at": "2026-11-23",
                           "dismissed_review": {"review_id": 1}}]

    def test_exact_head_and_review_barriers(self):
        valid = review(self.head)
        later = review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2)
        for reviews, timeline, expected in [
            ([valid], [], True), ([review("b" * 40)], [], False), ([valid, later], [], False),
            ([review(self.head, "DISMISSED")], self.dismissed, False), ([valid], self.dismissed, False),
            ([valid, later, review(self.head, date="2026-11-24", rid=3)], self.dismissed, True),
        ]:
            self.assertEqual(controller.approved(self.pr, reviews, [], timeline), expected)

    def test_self_approval_needs_new_exact_owner_comment(self):
        self.pr["user"]["login"] = "webmaxru"
        body = "/release-book " + self.head
        for user, text, day, expected in [
            ("other", body, "24", False), ("webmaxru", body, "22", False),
            ("webmaxru", body + " ", "24", False), ("webmaxru", "/release-book " + "b"*40, "24", False),
            ("webmaxru", body, "24", True),
        ]:
            c = {"body": text, "user": {"login": user}, "created_at": "2026-11-" + day, "updated_at": "2026-11-" + day}
            self.assertEqual(controller.approved(self.pr, [review(self.head)], [c], self.dismissed), expected)


class Rehearsal(Repository):
    """CLI → loopback API → local Git objects → gh upload shim. No real credentials."""
    def setUp(self):
        super().setUp()
        self.head = self.prepare()
        self.g("update-ref", "refs/pull/7/head", self.head)
        self.g("remote", "add", "origin", str(self.root))
        self.squash = self.g("commit-tree", self.head + "^{tree}", "-p", self.base, "-m", "squash")
        self.g("update-ref", "refs/remotes/origin/main", self.squash)
        self.main = self.base
        self.pr = {"number": 7, "state": "open", "draft": False, "mergeable": True, "merged": False,
                   "user": {"login": "author"}, "base": {"ref": "main", "sha": self.base, "repo": {"full_name": "test/book"}},
                   "head": {"sha": self.head, "ref": "update", "repo": {"full_name": "test/book"}}}
        self.writes = []
        self.tagged = None
        self.release = None
        self.success = True
        self.upload_log = self.root / "uploads.json"
        self.write("shim.py", "import json, os, pathlib, sys\n"
                   "assert sys.argv[1:6] == ['release','upload','v2.3.0','--repo','test/book']\n"
                   "assets=[dict(name=p.name,size=p.stat().st_size,state='uploaded') for p in map(pathlib.Path,sys.argv[6:])]\n"
                   "pathlib.Path(os.environ['UPLOAD_LOG']).write_text(json.dumps(assets))\n")
        if os.name == "nt":
            self.write("gh.cmd", f'@"{sys.executable}" "{self.root / "shim.py"}" %*\n')
        else:
            self.write("gh", f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(self.root/'shim.py'))} \"$@\"\n")
            (self.root / "gh").chmod(0o755)
        test = self

        class Handler(BaseHTTPRequestHandler):
            def handle_api(self):
                path = urlsplit(self.path).path.removeprefix("/repos/test/book/")
                size = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(size)) if size else None
                try:
                    status, result = test.respond(self.command, path, body)
                except (AssertionError, KeyError) as e:
                    status, result = 400, str(e)
                self.send_response(status)
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            do_GET = do_PUT = do_POST = do_PATCH = handle_api

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.write("event", '{"inputs":{"pr":"7"}}')
        self.env = {**os.environ, "PATH": str(self.root) + os.pathsep + os.environ["PATH"],
                    "GH_TOKEN": "fixture", "GITHUB_REPOSITORY": "test/book", "UPLOAD_LOG": str(self.upload_log),
                    "GITHUB_EVENT_PATH": str(self.root/"event"), "GITHUB_OUTPUT": str(self.root/"outputs"),
                    "GITHUB_API_URL": f"http://127.0.0.1:{server.server_port}"}
        self.params = ["--pr", "7", "--head", self.head, "--base", self.base]
        self.release_args = self.params + ["--merge", self.squash, "--tag", "v2.3.0"]

    def respond(self, method, path, body):
        if method != "GET":
            self.writes.append((method, path, body))
        if path == "pulls/7/merge":
            assert body == {"sha": self.head, "merge_method": "squash"}
            self.pr.update(merged=True, merge_commit_sha=self.squash, merged_at="2026-11-25",
                           merged_by={"login": "github-actions[bot]"}, state="closed")
            self.main = self.squash
            return 200, {"merged": True, "sha": self.squash}
        if path == "git/refs":
            self.tagged = self.squash
            return 201, {}
        if path == "git/tags":
            assert body["type"] == "commit" and body["object"] == self.squash
            return 201, {"sha": "e"*40}
        if path == "git/tags/" + "e"*40:
            return 200, {"tag": "v2.3.0", "object": {"type": "commit", "sha": self.tagged}}
        if path == "git/ref/tags/v2.3.0":
            return (200, {"object": {"type": "tag", "sha": "e"*40}}) if self.tagged else (404, {})
        if path == "releases" and method == "POST":
            self.release = {**body, "id": 12}
            return 201, self.release
        if path == "releases/12" and method == "PATCH":
            self.release.update(body)
            return 200, self.release
        if path == "actions/workflows/deploy-swa.yml/dispatches":
            assert body["inputs"] == {"ref": "v2.3.0"}
            return 200, {"workflow_run_id": 99, "html_url": "http://example.test/runs/99"}
        if path == "actions/workflows/release.yml/dispatches":
            assert body["ref"] == "main" and body["inputs"] == dict(
                pr="7", head_sha=self.head, base_sha=self.base, merge_sha=self.squash, tag="v2.3.0")
            return 200, {}
        routes = {"pulls/7": self.pr, "pulls/7/reviews": [review(self.head)], "issues/7/comments": [],
                  "issues/7/timeline": [], "git/ref/heads/main": {"object": {"sha": self.main}},
                  "actions/workflows/ci.yml/runs": {"workflow_runs": [dict(id=5, head_sha=self.head, head_branch="update",
                      head_repository={"full_name": "test/book"}, conclusion="success")]},
                  "actions/runs/5/jobs": {"jobs": [dict(name=controller.CHECK, conclusion="success" if self.success else "failure")]},
                  "actions/runs/99": {"status": "completed", "conclusion": "success"},
                  "actions/runs/99/jobs": {"jobs": [{"steps": [{"name": "Smoke test", "conclusion": "success"}]}]},
                  "releases": [self.release] if self.release else [], "tags": [{"name": "v2.2.0"}],
                  "releases/12/assets": json.loads(self.upload_log.read_text()) if self.upload_log.exists() else []}
        return 200, routes[path]

    def cli(self, action, *args, ok=True):
        p = subprocess.run([sys.executable, str(TOOLS/"book_release.py"), action, *args], cwd=self.root,
                           env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(p.returncode == 0, ok, p.stdout + p.stderr)
        return p

    def test_cli_controller_to_deployment_and_recovery(self):
        self.cli("inspect")
        self.assertIn("eligible=true", (self.root/"outputs").read_text())
        self.cli("merge", *self.params)
        self.cli("release-plan", *self.release_args)
        self.assertIn("recovery=false", (self.root/"outputs").read_text())
        sums = []
        for name in sorted(controller.asset_names(self.cfg, "v2.3.0") - {"SHA256SUMS.txt"}):
            self.write("release/" + name, "asset")
            sums.append(hashlib.sha256(b"asset").hexdigest() + "  " + name)
        self.write("release/SHA256SUMS.txt", "\n".join(sums))
        self.cli("publish", *self.release_args)
        self.assertEqual([p for _, p, _ in self.writes], ["pulls/7/merge", "actions/workflows/release.yml/dispatches",
                         "git/tags", "git/refs", "releases", "releases/12", "actions/workflows/deploy-swa.yml/dispatches"])
        self.assertFalse(self.release["draft"])
        self.assertEqual(self.release["make_latest"], "true")
        self.writes.clear()
        self.cli("release-plan", *self.release_args)
        self.assertIn("recovery=true", (self.root/"outputs").read_text())
        self.cli("publish", *self.release_args)
        self.upload_log.write_text("[]")
        self.cli("publish", *self.release_args, ok=False)
        self.tagged = self.base
        self.cli("publish", *self.release_args, ok=False)
        self.assertEqual(self.writes, [])

    def test_no_write_on_failed_check_stale_head_or_behind_main(self):
        self.success = False
        self.cli("merge", *self.params, ok=False)
        self.success = True
        self.cli("merge", "--pr", "7", "--head", self.stable, "--base", self.base, ok=False)
        ahead = self.g("commit-tree", self.base + "^{tree}", "-p", self.base, "-m", "main advanced")
        self.pr["base"]["sha"] = self.main = ahead
        p = self.cli("merge", "--pr", "7", "--head", self.head, "--base", ahead, ok=False)
        self.assertIn("behind main", p.stderr)
        self.assertFalse(self.writes)

    def test_forged_or_manual_merge_cannot_publish(self):
        self.cli("release-plan", *self.release_args, ok=False)
        self.cli("merge", *self.params)
        self.writes.clear()
        self.cli("publish", *self.params, "--merge", self.base, "--tag", "v2.3.0", ok=False)
        self.cli("publish", *self.params, "--merge", self.squash, "--tag", "v2.4.0", ok=False)
        self.pr["merged_by"]["login"] = "webmaxru"
        self.cli("publish", *self.release_args, ok=False)
        self.assertFalse(self.writes)
