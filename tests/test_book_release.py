import copy
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import book_release as controller
import release_policy as policy
import workflow_text


class Repository(unittest.TestCase):
    version = "2.3.0"

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
        self.cfg.update(version=self.version)
        self.cfg.update(extra)
        self.write(policy.META, json.dumps(self.cfg))
        self.write("CHANGELOG.md", f"## [Unreleased]\n\n## [{self.version}] - 2026-11-24\n\nCatch up.\n")
        return self.commit()

    def commit_on(self, parent, files):
        """A commit on top of parent. main and the work tree end up where they were."""
        self.g("switch", "-q", "--detach", parent)
        for name, text in files.items():
            self.write(name, text)
        head = self.commit()
        self.g("switch", "-q", "main")
        return head

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


def review(head, state="APPROVED", date="2026-11-21", rid=1, user="webmaxru"):
    return {"user": {"login": user}, "commit_id": head, "state": state, "submitted_at": date, "id": rid}


def owner_comment(head, day="24", body=None):
    date = "2026-11-" + day
    return {"body": "/release-book " + head if body is None else body, "user": {"login": "webmaxru"},
            "created_at": date, "updated_at": date}


def dismissal(date, rid=1):
    return {"event": "review_dismissed", "created_at": date, "dismissed_review": {"review_id": rid}}


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

    def test_the_latest_formal_review_decides(self):
        h, other = self.head, "b" * 40
        approval, veto = review(h), review(h, "CHANGES_REQUESTED", "2026-11-21", 1)
        note = review(h, "COMMENTED", "2026-11-22", 2)
        for name, reviews, expected in [
            ("an approval", [approval], True),
            ("a comment after the approval", [approval, note], True),
            ("a comment alone", [note], False),
            ("a review that was never submitted", [approval, review(h, "PENDING", None, 2)], True),
            ("a comment after a change request", [veto, note], False),
            ("a change request after the approval", [approval, dict(veto, submitted_at="2026-11-22", id=2)], False),
            ("an approval after a change request", [veto, review(h, date="2026-11-22", rid=2)], True),
            ("an approval at the instant of a change request", [veto, review(h, date="2026-11-21", rid=2)], False),
            ("a later approval of another head", [approval, review(other, date="2026-11-22", rid=2)], False),
            ("an earlier approval of another head", [review(other), review(h, date="2026-11-22", rid=2)], True),
        ]:
            for order, rows in (("as listed", reviews), ("reversed", reviews[::-1])):
                with self.subTest(name, order=order):
                    self.assertEqual(controller.approved(self.pr, rows, [], []), expected)

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

    def test_the_owners_command_is_the_whole_body_and_names_the_head(self):
        self.pr["user"]["login"] = "webmaxru"
        command = "/release-book " + self.head
        for name, body, expected in [
            ("the exact command", command, True),
            ("text after it", command + " thanks", False),
            ("a trailing newline", command + "\n", False),
            ("a leading space", " " + command, False),
            ("a second line", command + "\nand merge it", False),
            ("a quoted reply", "> " + command, False),
            ("two spaces", "/release-book  " + self.head, False),
            ("an upper-case SHA", "/release-book " + self.head.upper(), False),
            ("an abbreviated SHA", "/release-book " + self.head[:12], False),
            ("another head", "/release-book " + "b" * 40, False),
            ("no SHA", "/release-book", False),
            ("another command", "/release " + self.head, False),
            ("an empty body", "", False),
        ]:
            with self.subTest(name):
                self.assertEqual(controller.approved(self.pr, [], [owner_comment(self.head, body=body)], []), expected)
        with self.subTest("an exact command among other comments"):
            noise = [owner_comment(self.head, body="looks good"), owner_comment("b" * 40)]
            self.assertTrue(controller.approved(self.pr, [], noise + [owner_comment(self.head)], []))

    def test_only_the_owner_authorizes(self):
        stranger = review(self.head, user="someone")
        for name, reviews, comments, expected in [
            ("an owner approval", [review(self.head)], [], True),
            ("a non-owner approval", [stranger], [], False),
            ("an owner comment on someone else's pull request", [], [owner_comment(self.head)], False),
            ("a non-owner change request after the owner's approval", [review(self.head), dict(
                stranger, state="CHANGES_REQUESTED", submitted_at="2026-11-22", id=2)], [], False),
            ("a new owner approval after a non-owner change request", [review(self.head), dict(
                stranger, state="CHANGES_REQUESTED", submitted_at="2026-11-22", id=2),
                review(self.head, date="2026-11-23", rid=3)], [], True),
            ("a non-owner comment-only review after the owner's approval", [review(self.head), dict(
                stranger, state="COMMENTED", submitted_at="2026-11-22", id=2)], [], True),
        ]:
            with self.subTest(name):
                self.assertEqual(controller.approved(self.pr, reviews, comments, []), expected)
        self.pr["user"]["login"] = "webmaxru"
        for name, reviews, comments, expected in [
            ("an owner comment on the owner's own pull request", [], [owner_comment(self.head)], True),
            ("an owner approval of the owner's own pull request", [review(self.head)], [], False),
            ("a non-owner comment", [], [dict(owner_comment(self.head), user={"login": "someone"})], False),
        ]:
            with self.subTest(name):
                self.assertEqual(controller.approved(self.pr, reviews, comments, []), expected)

    def test_a_push_revokes_the_approval(self):
        for author, reviews, comments in [("writer", [review(self.head)], []),
                                          ("webmaxru", [], [owner_comment(self.head)])]:
            with self.subTest(author=author):
                self.pr.update(user={"login": author}, head={"sha": self.head})
                self.assertTrue(controller.approved(self.pr, reviews, comments, []))
                self.pr["head"]["sha"] = "b" * 40
                self.assertFalse(controller.approved(self.pr, reviews, comments, []))

    def test_a_deleted_or_edited_comment_does_not_authorize(self):
        self.pr["user"]["login"] = "webmaxru"
        posted, merged = "2026-11-24T09:00:00Z", "2026-11-24T10:00:00Z"
        comment = dict(owner_comment(self.head), created_at=posted, updated_at=posted)
        self.assertTrue(controller.approved(self.pr, [], [comment], []))
        self.assertTrue(controller.approved(self.pr, [], [comment], [], until=merged))
        self.assertFalse(controller.approved(self.pr, [], [], []))
        self.assertFalse(controller.approved(self.pr, [], [dict(comment, body=comment["body"] + " (edited)")], []))
        for name, updated, until in [
            ("an edit after the merge", "2026-11-24T11:00:00Z", merged),
            ("an edit before the merge", "2026-11-24T09:05:00Z", merged),
            ("an edit that made the body exact", "2026-11-24T09:05:00Z", None),
        ]:
            with self.subTest(name):
                edited = dict(comment, updated_at=updated)
                self.assertEqual(edited["body"], "/release-book " + self.head)
                self.assertFalse(controller.approved(self.pr, [], [edited], [], until=until))
                self.assertTrue(controller.approved(self.pr, [], [edited, comment], [], until=until))

    def test_the_owners_command_is_judged_as_of_the_merge(self):
        self.pr["user"]["login"] = "webmaxru"
        merged, before, after = "2026-11-25", owner_comment(self.head, day="24"), owner_comment(self.head, day="26")
        self.assertTrue(controller.approved(self.pr, [], [before], [], until=merged))
        self.assertTrue(controller.approved(self.pr, [], [owner_comment(self.head, day="25")], [], until=merged))
        self.assertFalse(controller.approved(self.pr, [], [after], [], until=merged))
        self.assertTrue(controller.approved(self.pr, [], [after], []))

    def test_the_approval_is_judged_as_of_the_merge(self):
        merged = "2026-11-25"
        valid, veto = review(self.head), review(self.head, "CHANGES_REQUESTED", "2026-11-26", 2)
        late = review(self.head, date="2026-11-26", rid=3)
        late_dismissal = [{"event": "review_dismissed", "created_at": "2026-11-26",
                           "dismissed_review": {"review_id": 1}}]
        self.assertFalse(controller.approved(self.pr, [valid, veto], [], []))
        self.assertTrue(controller.approved(self.pr, [valid, veto], [], [], until=merged))
        self.assertTrue(controller.approved(self.pr, [valid], [], late_dismissal, until=merged))
        self.assertFalse(controller.approved(self.pr, [late], [], [], until=merged))

    def test_a_veto_by_anyone_is_a_barrier_only_a_fresh_owner_authorization_crosses(self):
        head, merged = self.head, "2026-11-25"

        def vetoes(day):
            date = "2026-11-" + day
            return {
                "a change request by someone else": ([review(head, "CHANGES_REQUESTED", date, 2, "someone")], []),
                "a dismissed review by someone else": ([review(head, "DISMISSED", date, 2, "someone")], []),
                "the dismissal of someone else's review": ([], [dismissal(date, 99)]),
                "a dismissal that names no review": ([], [{"event": "review_dismissed", "created_at": date}]),
            }

        def decide(author, days, veto=([], []), until=None):
            """The owner authorizes on each of the days: an approval, or a command on their own pull request."""
            self.pr["user"]["login"] = author
            reviews = [] if author == "webmaxru" else [review(head, date="2026-11-" + d, rid=10 + i)
                                                       for i, d in enumerate(days)]
            comments = [owner_comment(head, day=d) for d in days] if author == "webmaxru" else []
            return controller.approved(self.pr, reviews + veto[0], comments, veto[1], until=until)

        for author in ("writer", "webmaxru"):
            for name, veto in vetoes("22").items():
                with self.subTest(name, author=author):
                    self.assertTrue(decide(author, ["21"]))
                    self.assertFalse(decide(author, ["21"], veto))
                    self.assertFalse(decide(author, ["21"], veto, until=merged))
                    self.assertFalse(decide(author, ["21", "22"], veto), "at the same instant the barrier wins")
                    self.assertTrue(decide(author, ["21", "23"], veto))
                    self.assertTrue(decide(author, ["21", "23"], veto, until=merged))
                    self.assertFalse(decide(author, ["21", "26"], veto, until=merged), "too late for the merge")
            for name, veto in vetoes("26").items():
                with self.subTest(name + " after the merge", author=author):
                    self.assertFalse(decide(author, ["21"], veto))
                    self.assertTrue(decide(author, ["21"], veto, until=merged))


def ci_run(number, head, conclusion="success", branch="update", repo="test/book"):
    return {"id": number, "head_sha": head, "head_branch": branch, "head_repository": {"full_name": repo},
            "conclusion": conclusion}


def options(args):
    return frozenset(a for a in args if a.startswith("--"))


class RehearsalBase(Repository):
    """CLI → loopback API → local Git objects → gh upload shim. No real credentials.

    The scenarios turn these knobs: reviews, comments, timeline, runs, job_name and success (approval and CI),
    tags and published (what the API lists), tagged, tag_type, release and the upload log (the release itself),
    smoke and deploy_run (the deployment), pushed_at_merge and fail_routes.

    The API accepts no other write than these, so a moved tag, a deleted release or an edited asset fails the run.
    """
    WRITES = {("PUT", "pulls/7/merge"), ("POST", "git/tags"), ("POST", "git/refs"), ("POST", "releases"),
              ("PATCH", "releases/12"), ("POST", "actions/workflows/release.yml/dispatches"),
              ("POST", "actions/workflows/deploy-swa.yml/dispatches")}

    def setUp(self):
        super().setUp()
        self.write(".git/info/exclude", "shim.py\ngh\ngh.cmd\nevent\noutputs\nsummary\nuploads.json*\nrelease/\n")
        self.tag = "v" + self.version
        self.head = self.prepare()
        self.g("update-ref", "refs/pull/7/head", self.head)
        self.g("remote", "add", "origin", str(self.root))
        self.squash = self.g("commit-tree", self.head + "^{tree}", "-p", self.base, "-m", "squash")
        self.g("update-ref", "refs/remotes/origin/main", self.squash)
        self.main = self.base
        self.pr = {"number": 7, "state": "open", "draft": False, "mergeable": True, "merged": False,
                   "user": {"login": "author"}, "base": {"ref": "main", "sha": self.base, "repo": {"full_name": "test/book"}},
                   "head": {"sha": self.head, "ref": "update", "repo": {"full_name": "test/book"}}}
        self.reviews = [review(self.head)]
        self.comments = []
        self.timeline = []
        self.runs = [ci_run(5, self.head)]
        self.job_name = controller.CHECK
        self.success = True
        self.tags = [{"name": "v2.2.0"}]
        self.published = []
        self.smoke = "success"
        self.deploy_run = "success"
        self.tag_type = "tag"
        self.pushed_at_merge = None
        self.fail_routes = set()
        self.dispatched = {}
        self.writes = []
        self.tagged = None
        self.release = None
        self.upload_log = self.root / "uploads.json"
        self.write("shim.py", "import json, os, pathlib, sys\n"
                   f"assert sys.argv[1:6] == ['release', 'upload', {self.tag!r}, '--repo', 'test/book'], sys.argv\n"
                   "assert '--clobber' not in sys.argv\n"
                   "assets = [dict(name=p.name, size=p.stat().st_size, state='uploaded')\n"
                   "          for p in map(pathlib.Path, sys.argv[6:])]\n"
                   "log = pathlib.Path(os.environ['UPLOAD_LOG'])\n"
                   "log.write_text(json.dumps(assets))\n"
                   "with open(str(log) + '.calls', 'a') as calls:\n"
                   "    calls.write('upload\\n')\n")
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
                    "GITHUB_STEP_SUMMARY": str(self.root/"summary"),
                    "GITHUB_API_URL": f"http://127.0.0.1:{server.server_port}"}
        shared = ("GH_TOKEN", "GITHUB_REPOSITORY", "GITHUB_API_URL", "GITHUB_EVENT_PATH")
        patch = mock.patch.dict(os.environ, {k: self.env[k] for k in shared})
        patch.start()
        self.addCleanup(patch.stop)
        self.client = controller.GitHub()

    @property
    def params(self):
        return ["--pr", "7", "--head", self.head, "--base", self.pr["base"]["sha"]]

    @property
    def release_args(self):
        return self.params + ["--merge", self.squash, "--tag", self.tag]

    def respond(self, method, path, body):
        if method != "GET":
            self.writes.append((method, path, body))
            assert (method, path) in self.WRITES, f"the controller must not {method} {path}"
        if path in self.fail_routes:
            return 500, {"message": "forced failure"}
        if path == "pulls/7/merge":
            assert body == {"sha": self.head, "merge_method": "squash"}, body
            if self.pushed_at_merge:
                self.pr["head"]["sha"] = self.pushed_at_merge
            if body["sha"] != self.pr["head"]["sha"]:
                return 409, {"message": "Head branch was modified. Review and try the merge again."}
            self.pr.update(merged=True, merge_commit_sha=self.squash, merged_at="2026-11-25",
                           merged_by={"login": "github-actions[bot]"}, state="closed")
            self.main = self.squash
            return 200, {"merged": True, "sha": self.squash}
        if path == "git/refs":
            assert body == {"ref": "refs/tags/" + self.tag, "sha": "e" * 40}, body
            self.tagged = self.squash
            return 201, {}
        if path == "git/tags":
            assert body["tag"] == self.tag and body["type"] == "commit" and body["object"] == self.squash, body
            return 201, {"sha": "e" * 40}
        if path == "git/tags/" + "e" * 40:
            return 200, {"tag": self.tag, "object": {"type": "commit", "sha": self.tagged}}
        if path == "git/ref/tags/" + self.tag:
            return (200, {"object": {"type": self.tag_type, "sha": "e" * 40}}) if self.tagged else (404, {})
        if path == "releases" and method == "POST":
            assert body["tag_name"] == self.tag and body["draft"] is True, body
            self.release = {**body, "id": 12}
            return 201, self.release
        if path == "releases/12" and method == "PATCH":
            assert self.upload_log.exists(), "published before the assets were uploaded"
            self.release.update(body)
            return 200, self.release
        if path == "actions/workflows/deploy-swa.yml/dispatches":
            assert body == {"ref": "main", "inputs": {"ref": self.tag}}, body
            self.dispatched["deploy-swa.yml"] = body
            return 200, {"workflow_run_id": 99, "html_url": "http://example.test/runs/99"}
        if path == "actions/workflows/release.yml/dispatches":
            assert body["ref"] == "main" and body["inputs"] == dict(
                pr="7", head_sha=self.head, base_sha=self.pr["base"]["sha"], merge_sha=self.squash, tag=self.tag), body
            self.dispatched["release.yml"] = body
            return 200, {}
        routes = {"pulls/7": self.pr, "pulls/7/reviews": self.reviews, "issues/7/comments": self.comments,
                  "issues/7/timeline": self.timeline, "git/ref/heads/main": {"object": {"sha": self.main}},
                  "pulls": [{"number": 7}], "actions/workflows/ci.yml/runs": {"workflow_runs": self.runs},
                  "actions/runs/99": {"status": "completed", "conclusion": self.deploy_run},
                  "actions/runs/99/jobs": {"jobs": [{"steps": [{"name": "Smoke test", "conclusion": self.smoke}]}]},
                  "releases": ([self.release] if self.release else []) + self.published,
                  "tags": self.tags + ([{"name": self.tag}] if self.tagged else []),
                  "releases/12/assets": json.loads(self.upload_log.read_text()) if self.upload_log.exists() else []}
        if path not in routes and re.fullmatch(r"actions/runs/\d+/jobs", path):
            return 200, {"jobs": [dict(name=self.job_name, conclusion="success" if self.success else "failure")]}
        return 200, routes[path]

    def cli(self, action, *args, ok=True):
        for name in ("outputs", "summary"):
            (self.root / name).unlink(missing_ok=True)
        p = subprocess.run([sys.executable, str(TOOLS/"book_release.py"), action, *args], cwd=self.root,
                           env=self.env, text=True, capture_output=True, timeout=60)
        self.assertEqual(p.returncode == 0, ok, p.stdout + p.stderr)
        return p

    def outputs(self):
        file = self.root / "outputs"
        lines = file.read_text(encoding="utf-8").splitlines() if file.exists() else []
        return dict(line.split("=", 1) for line in lines if "=" in line)

    def summary(self):
        file = self.root / "summary"
        return file.read_text(encoding="utf-8") if file.exists() else ""

    def upload_calls(self):
        log = Path(str(self.upload_log) + ".calls")
        return len(log.read_text().splitlines()) if log.exists() else 0

    def written(self):
        return [path for _, path, _ in self.writes]

    def build_assets(self):
        shutil.rmtree(self.root / "release", ignore_errors=True)
        sums = []
        for name in sorted(controller.asset_names(self.cfg, self.tag) - {"SHA256SUMS.txt"}):
            self.write("release/" + name, "asset")
            sums.append(hashlib.sha256(b"asset").hexdigest() + "  " + name)
        self.write("release/SHA256SUMS.txt", "\n".join(sums))

    def release_flow(self, ok=True):
        """The controller's whole run: merge, plan, build, publish. Returns the publish step."""
        self.cli("merge", *self.params)
        self.cli("release-plan", *self.release_args)
        self.build_assets()
        return self.cli("publish", *self.release_args, ok=ok)

    def retarget(self, head, base=None, approve=True):
        """The pull request gets a new head (a push), optionally on top of a newer main.

        CI is green on the new head. The owner's approval follows it only when approve is true."""
        if base:
            self.pr["base"]["sha"] = self.main = base
        self.head = head
        self.pr["head"]["sha"] = head
        self.runs[0]["head_sha"] = head
        if approve:
            self.reviews = [review(head)]
        self.squash = self.g("commit-tree", head + "^{tree}", "-p", self.pr["base"]["sha"], "-m", "squash")
        self.g("update-ref", "refs/pull/7/head", head)
        self.g("update-ref", "refs/remotes/origin/main", self.squash)

    def checkpoint(self):
        """A function that puts the pull request, its reviews and its CI runs back as they are now."""
        names = ("pr", "reviews", "comments", "timeline", "runs", "job_name", "success", "head", "squash", "main")
        saved = copy.deepcopy({name: getattr(self, name) for name in names})

        def restore():
            for name, value in copy.deepcopy(saved).items():
                setattr(self, name, value)
            self.g("update-ref", "refs/pull/7/head", saved["head"])
            self.g("update-ref", "refs/remotes/origin/main", saved["squash"])
            self.writes.clear()
        return restore

    def refuse(self, message="Missing current owner approval or preflight", head=None, base=None):
        """The controller refuses to merge the pull request as it is now, and writes nothing."""
        with self.assertRaisesRegex(policy.Rejected, message):
            controller.merge(self.client, self.root, 7, head or self.head, base or self.pr["base"]["sha"])
        self.assertEqual(self.writes, [])

    def refuse_release(self, message, **inputs):
        """release-plan and publish both stop on the message, and neither writes anything."""
        args = {"head": self.head, "base": self.pr["base"]["sha"], "merge": self.squash, "tag": self.tag, **inputs}
        before = list(self.writes)
        with mock.patch.object(controller.shutil, "which", side_effect=AssertionError("gh must not run")):
            for call in (controller.release_plan, controller.publish):
                folder = [str(self.root / "release")] if call is controller.publish else []
                with self.assertRaisesRegex(policy.Rejected, message):
                    call(self.client, self.root, 7, args["head"], args["base"], args["merge"], args["tag"], *folder)
        self.assertEqual(self.writes, before)


class Rehearsal(RehearsalBase):
    def test_cli_controller_to_deployment_and_recovery(self):
        produced = {}
        self.cli("inspect")
        produced["inspect"] = self.outputs()
        self.assertEqual(produced["inspect"], {"eligible": "true", "pr": "7", "head_sha": self.head,
                                               "base_sha": self.base, "tag": self.tag})
        self.cli("merge", *self.params)
        self.assertEqual(self.writes[0], ("PUT", "pulls/7/merge", {"sha": self.head, "merge_method": "squash"}))
        self.cli("release-plan", *self.release_args)
        produced["release-plan"] = self.outputs()
        self.assertEqual(produced["release-plan"], {"recovery": "false"})
        self.build_assets()
        self.cli("publish", *self.release_args)
        self.assertEqual(self.written(), ["pulls/7/merge", "actions/workflows/release.yml/dispatches", "git/tags",
                                          "git/refs", "releases", "releases/12",
                                          "actions/workflows/deploy-swa.yml/dispatches"])
        self.assertFalse(self.release["draft"])
        self.assertFalse(self.release["prerelease"])
        self.assertEqual(self.release["make_latest"], "true")
        self.assertEqual(self.upload_calls(), 1)
        for name in ("release.yml", "deploy-swa.yml"):
            declared = workflow_text.dispatch_inputs(name)
            self.assertEqual(set(self.dispatched[name]["inputs"]), set(declared), name)
            self.assertTrue(all(declared.values()), name)
        self.writes.clear()
        self.cli("release-plan", *self.release_args)
        self.assertEqual(self.outputs(), {"recovery": "true"})
        self.cli("publish", *self.release_args)
        self.assertEqual((self.writes, self.upload_calls()), ([], 1))
        self.g("tag", self.tag, self.squash)
        self.published = [{"tag_name": "v2.2.0", "draft": False, "prerelease": False}]
        self.cli("published-source", "--head", self.squash)
        produced["published-source"] = self.outputs()
        for name, step, action in [("approved-book.yml", "inspect", "inspect"), ("release.yml", "plan", "release-plan"),
                                   ("deploy-swa.yml", "gate", "published-source")]:
            read = {output for found, output in workflow_text.step_outputs(name) if found == step}
            self.assertTrue(read, f"{name} reads no output of the step {step}")
            self.assertLessEqual(read, set(produced[action]), name)

    def test_workflows_call_the_controller_with_the_options_it_takes(self):
        self.assertEqual(workflow_text.commands("approved-book.yml", "release.yml", "deploy-swa.yml"), {
            "inspect": {frozenset()}, "merge": {options(self.params)},
            "release-plan": {options(self.release_args)}, "publish": {options(self.release_args)},
            "published-source": {frozenset({"--head", "--ref"})}})

    def test_every_trigger_resolves_to_pull_requests(self):
        declared = workflow_text.dispatch_inputs("approved-book.yml")
        self.assertEqual(list(declared), ["pr"])
        comment = {"body": "/release-book " + self.head}
        for name, event, expected in [
            ("a manual dispatch", {"inputs": {key: "7" for key in declared}}, [7]),
            ("a comment on a pull request", {"comment": comment, "issue": {"number": 7, "pull_request": {}}}, [7]),
            ("a comment on an issue", {"comment": comment, "issue": {"number": 7}}, []),
            ("a finished workflow run", {"workflow_run": {"pull_requests": [{"number": 7}]}}, [7]),
            ("a workflow run without a pull request", {"workflow_run": {"pull_requests": []}}, [7]),
            ("the schedule", {"schedule": "17,47 * * * *"}, [7]),
        ]:
            with self.subTest(name):
                self.write("event", json.dumps(event))
                self.assertEqual(controller.event_numbers(self.client), expected)

    def test_head_must_contain_current_main(self):
        ahead = self.g("commit-tree", self.base + "^{tree}", "-p", self.base, "-m", "main advanced")
        self.pr["base"]["sha"] = self.main = ahead
        p = self.cli("merge", *self.params, ok=False)
        self.assertIn("Head is behind main", p.stderr)
        self.cli("inspect")
        self.assertEqual(self.outputs(), {"eligible": "false"})
        self.assertEqual(self.writes, [])
        rebased = self.g("commit-tree", self.head + "^{tree}", "-p", ahead, "-m", "rebased")
        self.retarget(rebased, base=ahead)
        self.cli("merge", *self.params)
        self.assertEqual(self.writes[0], ("PUT", "pulls/7/merge", {"sha": rebased, "merge_method": "squash"}))

    def test_a_failed_check_a_stale_head_or_a_moved_main_stops_the_merge(self):
        self.success = False
        self.refuse()
        self.success = True
        self.refuse("PR moved", head=self.stable)
        self.refuse("PR moved", base=self.stable)
        self.main = self.g("commit-tree", self.base + "^{tree}", "-p", self.base, "-m", "main advanced")
        self.refuse("main moved")

    def test_a_missing_vetoed_dismissed_or_outdated_approval_blocks_the_merge(self):
        restore = self.checkpoint()
        newer = self.commit_on(self.head, {"outline/plan.md": "pushed after the approval"})

        def dismissed():
            self.reviews[:] = [review(self.head, "DISMISSED")]
            self.timeline.append({"event": "review_dismissed", "created_at": "2026-11-23",
                                  "dismissed_review": {"review_id": 1}})

        for name, change in {
            "no review": lambda: self.reviews.clear(),
            "changes requested after the approval": lambda: self.reviews.append(
                review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2)),
            "changes requested by someone else after the approval": lambda: self.reviews.append(
                review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2, user="someone")),
            "a dismissed review": dismissed,
            "the dismissal of someone else's review": lambda: self.timeline.append(dismissal("2026-11-23", 99)),
            "a comment-only review instead of an approval": lambda: self.reviews.__setitem__(
                0, review(self.head, "COMMENTED")),
            "an approval of another head": lambda: self.reviews.__setitem__(0, review("b" * 40)),
            "a later approval of another head": lambda: self.reviews.append(
                review("b" * 40, date="2026-11-22", rid=2)),
            "an approval by someone else": lambda: self.reviews.__setitem__(0, review(self.head, user="someone")),
            "an owner comment on someone else's pull request": lambda: (
                self.reviews.clear(), self.comments.append(owner_comment(self.head))),
            "a push after the approval": lambda: self.retarget(newer, approve=False),
        }.items():
            with self.subTest(name):
                change()
                self.refuse()
                restore()
        with self.subTest("a new approval after the change request"):
            self.reviews += [review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2),
                             review(self.head, date="2026-11-24", rid=3)]
            self.assertEqual(controller.candidate(self.client, self.root, 7, self.head, self.base)["pr"], 7)
        restore()
        with self.subTest("a new approval after someone else's change request and dismissal"):
            self.reviews += [review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2, user="someone"),
                             review(self.head, date="2026-11-24", rid=3)]
            self.timeline.append(dismissal("2026-11-23", 99))
            self.assertEqual(controller.candidate(self.client, self.root, 7, self.head, self.base)["pr"], 7)
        restore()
        with self.subTest("a comment-only review after the approval"):
            self.reviews.append(review(self.head, "COMMENTED", "2026-11-22", 2))
            self.assertEqual(controller.candidate(self.client, self.root, 7, self.head, self.base)["pr"], 7)
        self.assertEqual(self.writes, [])

    def test_the_owners_own_pull_request_needs_a_new_command_after_anyones_veto(self):
        self.pr["user"]["login"] = "webmaxru"
        self.reviews.clear()
        self.comments.append(owner_comment(self.head, day="21"))
        self.assertEqual(controller.candidate(self.client, self.root, 7, self.head, self.base)["pr"], 7)
        self.reviews.append(review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2, user="someone"))
        self.refuse()
        self.comments.append(owner_comment(self.head, day="22"))
        self.refuse()
        self.timeline.append(dismissal("2026-11-23", 99))
        self.comments.append(owner_comment(self.head, day="23"))
        self.refuse()
        self.comments.append(owner_comment(self.head, day="24"))
        self.cli("merge", *self.params)
        self.assertEqual(self.writes, [("PUT", "pulls/7/merge", {"sha": self.head, "merge_method": "squash"}),
                                       ("POST", "actions/workflows/release.yml/dispatches", mock.ANY)])
        self.writes.clear()
        self.cli("release-plan", *self.release_args)
        self.assertEqual((self.outputs(), self.writes), ({"recovery": "false"}, []))

    def test_the_owners_own_pull_request_needs_a_comment_on_the_current_head(self):
        self.pr["user"]["login"] = "webmaxru"
        self.refuse()
        self.comments.append(owner_comment(self.head))
        self.assertEqual(controller.candidate(self.client, self.root, 7, self.head, self.base)["pr"], 7)
        newer = self.commit_on(self.head, {"outline/plan.md": "pushed after the comment"})
        self.retarget(newer)
        self.refuse()
        self.comments.append(dict(owner_comment(newer, day="25"), updated_at="2026-11-25T12:00:00Z"))
        self.refuse()
        self.comments.append(owner_comment(newer, day="25"))
        self.cli("merge", *self.params)
        self.assertEqual(self.writes[0], ("PUT", "pulls/7/merge", {"sha": newer, "merge_method": "squash"}))

    def test_only_an_eligible_pull_request_is_merged(self):
        restore = self.checkpoint()
        fork = {"full_name": "fork/book"}
        scope, state, ci = "same repository and base main", "Not open and mergeable", "approval or preflight"
        for message, name, change in [
            (scope, "a fork", lambda: self.pr["head"].update(repo=fork)),
            (scope, "a deleted fork", lambda: self.pr["head"].update(repo=None)),
            (scope, "a pull request into another branch", lambda: self.pr["base"].update(ref="release")),
            (scope, "a pull request into another repository", lambda: self.pr["base"].update(repo=fork)),
            (state, "a draft", lambda: self.pr.update(draft=True)),
            (state, "a closed pull request", lambda: self.pr.update(state="closed")),
            (state, "a conflict", lambda: self.pr.update(mergeable=False)),
            (state, "an unknown mergeability", lambda: self.pr.update(mergeable=None)),
            (ci, "no run", lambda: self.runs.clear()),
            (ci, "a run of another head", lambda: self.runs[0].update(head_sha="b" * 40)),
            (ci, "a run of another branch", lambda: self.runs[0].update(head_branch="other")),
            (ci, "a run from a fork", lambda: self.runs[0].update(head_repository=fork)),
            (ci, "a failed run", lambda: self.runs[0].update(conclusion="failure")),
            (ci, "a green run without the aggregate check", lambda: setattr(self, "job_name", "build")),
            (ci, "a failed aggregate check", lambda: setattr(self, "success", False)),
            (ci, "a newer failed run", lambda: self.runs.insert(0, ci_run(6, self.head, "failure"))),
        ]:
            with self.subTest(name):
                change()
                self.refuse(message)
                restore()
        self.cli("inspect")
        self.assertEqual(self.outputs(), {"eligible": "true", "pr": "7", "head_sha": self.head,
                                          "base_sha": self.base, "tag": self.tag})
        self.pr["head"]["repo"] = fork
        p = self.cli("inspect")
        self.assertEqual(self.outputs(), {"eligible": "false"})
        self.assertIn("PR 7: Requires same repository and base main", p.stdout)

    def test_only_book_content_is_merged_by_the_controller(self):
        restore = self.checkpoint()
        other_name = json.dumps(dict(self.cfg, file_stem="Other"))
        for name, files in {
            "a build script": {"tools/build.py": "# changed"},
            "a workflow": {".github/workflows/ci.yml": "name: changed"},
            "the theme": {"theme/style.css": "body {}"},
            "the infrastructure": {"infra/main.bicep": "// changed"},
            "the deployment guide": {"DEPLOY.md": "changed"},
            "a setting in the book configuration": {policy.META: other_name},
        }.items():
            with self.subTest(name):
                self.retarget(self.commit_on(self.head, files))
                self.refuse("Separate content from tooling")
                restore()
        with self.subTest("tooling only"):
            self.retarget(self.commit_on(self.base, {"tools/build.py": "# changed"}))
            self.refuse("Not a content PR")
            restore()
        with self.subTest("a changed chapter without evidence"):
            self.retarget(self.commit_on(self.head, {self.chapter: "# Changed again\n"}))
            self.refuse("Update editorial/01-intro-editorial-log.md")

    def test_the_merge_is_conditional_on_the_approved_head(self):
        self.pushed_at_merge = "f" * 40
        p = self.cli("merge", *self.params, ok=False)
        self.assertIn("HTTP Error 409", p.stderr)
        self.assertEqual(self.writes, [("PUT", "pulls/7/merge", {"sha": self.head, "merge_method": "squash"})])
        self.assertFalse(self.pr["merged"])
        self.assertEqual(self.main, self.base)
        self.assertNotIn("actions/workflows/release.yml/dispatches", self.written())

    def test_a_forged_merge_cannot_publish(self):
        self.cli("release-plan", *self.release_args, ok=False)
        self.cli("merge", *self.params)
        self.writes.clear()
        restore = self.checkpoint()
        other = self.g("commit-tree", self.base + "^{tree}", "-p", self.base, "-m", "another tree")

        def another_tree():
            self.pr["merge_commit_sha"] = other
            self.g("update-ref", "refs/remotes/origin/main", other)

        by_controller, provenance = "Not the controller-merged PR", "Missing approved-head provenance"
        for message, name, change, inputs in [
            (by_controller, "another merge commit", None, {"merge": self.base}),
            (by_controller, "a head the pull request never had", None, {"head": self.stable}),
            (by_controller, "a manual merge", lambda: self.pr["merged_by"].update(login="webmaxru"), {}),
            ("Wrong release tag", "another version", None, {"tag": "v2.4.0"}),
            ("Not a squash of the supplied base", "another base", None, {"base": self.stable}),
            (provenance, "no approval", lambda: self.reviews.clear(), {}),
            (provenance, "a comment-only review instead of the approval",
             lambda: self.reviews.__setitem__(0, review(self.head, "COMMENTED")), {}),
            (provenance, "a later approval of another head",
             lambda: self.reviews.append(review("b" * 40, date="2026-11-24", rid=2)), {}),
            (provenance, "changes requested by someone else after the approval",
             lambda: self.reviews.append(review(self.head, "CHANGES_REQUESTED", "2026-11-22", 2, user="someone")), {}),
            (provenance, "the dismissal of someone else's review after the approval",
             lambda: self.timeline.append(dismissal("2026-11-23", 99)), {}),
            (provenance, "an approval after the merge",
             lambda: self.reviews.__setitem__(0, review(self.head, date="2026-11-26")), {}),
            (provenance, "a failed check", lambda: setattr(self, "success", False), {}),
            ("Merged tree differs from the approved tree", "another tree", another_tree, {"merge": other}),
        ]:
            with self.subTest(name):
                if change:
                    change()
                self.refuse_release(message, **inputs)
                restore()
        with self.subTest("a merge commit that is not on main"):
            self.g("update-ref", "refs/remotes/origin/main", self.base)
            self.cli("release-plan", *self.release_args, ok=False)
            self.assertEqual(self.outputs(), {})
            restore()
        with self.subTest("a veto by someone else after the merge changes nothing"):
            self.reviews.append(review(self.head, "CHANGES_REQUESTED", "2026-11-26", 2, user="someone"))
            self.timeline.append(dismissal("2026-11-26", 99))
            self.cli("release-plan", *self.release_args)
            self.assertEqual((self.outputs(), self.writes), ({"recovery": "false"}, []))
            restore()
        self.cli("release-plan", *self.release_args)
        self.assertEqual((self.outputs(), self.writes), ({"recovery": "false"}, []))

    def test_the_owners_command_must_stay_untouched_until_the_release_is_published(self):
        self.pr["user"]["login"] = "webmaxru"
        self.reviews.clear()
        command = owner_comment(self.head)
        self.comments.append(command)
        self.cli("merge", *self.params)
        self.writes.clear()
        restore = self.checkpoint()
        for name, change in [
            ("an edited command", lambda: self.comments.__setitem__(
                0, dict(command, updated_at="2026-11-24T23:00:00Z"))),
            ("a deleted command", lambda: self.comments.clear()),
            ("a command posted after the merge", lambda: self.comments.__setitem__(
                0, owner_comment(self.head, day="26"))),
            ("a command by someone else", lambda: self.comments.__setitem__(
                0, dict(command, user={"login": "someone"}))),
        ]:
            with self.subTest(name):
                change()
                self.refuse_release("Missing approved-head provenance")
                restore()
        self.cli("release-plan", *self.release_args)
        self.assertEqual((self.outputs(), self.writes), ({"recovery": "false"}, []))

    def test_a_partial_release_is_never_resumed_moved_or_overwritten(self):
        self.release_flow()
        self.writes.clear()
        saved = (copy.deepcopy(self.release), self.tagged, self.tag_type, self.upload_log.read_text())

        def restore():
            self.release, self.tagged, self.tag_type = copy.deepcopy(saved[0]), saved[1], saved[2]
            self.published = []
            self.upload_log.write_text(saved[3])

        def assets(change):
            rows = json.loads(saved[3])
            change(rows)
            self.upload_log.write_text(json.dumps(rows))

        incomplete = "Existing draft or incomplete release"
        for message, name, change in [
            (incomplete, "a draft", lambda: self.release.update(draft=True)),
            (incomplete, "a missing asset", lambda: assets(lambda rows: rows.pop())),
            (incomplete, "an empty asset", lambda: assets(lambda rows: rows[0].update(size=0))),
            (incomplete, "an asset still uploading", lambda: assets(lambda rows: rows[0].update(state="starter"))),
            (incomplete, "an extra asset", lambda: assets(lambda rows: rows.append(dict(rows[0], name="extra.zip")))),
            ("Tag exists without a release", "a tag without a release", lambda: setattr(self, "release", None)),
            ("Existing tag points elsewhere", "a tag on another commit", lambda: setattr(self, "tagged", self.base)),
            ("Existing tag is not annotated", "a lightweight tag", lambda: setattr(self, "tag_type", "commit")),
            ("Ambiguous release", "two releases of one tag",
             lambda: setattr(self, "published", [dict(self.release)])),
        ]:
            with self.subTest(name):
                change()
                self.refuse_release(message)
                restore()
        self.cli("release-plan", *self.release_args)
        self.assertEqual(self.outputs(), {"recovery": "true"})
        self.cli("publish", *self.release_args)
        self.assertEqual((self.writes, self.upload_calls()), ([], 1))

    def test_a_failed_deployment_keeps_the_release_and_is_retried_through_deploy_swa(self):
        self.smoke = "skipped"
        p = self.release_flow(ok=False)
        self.assertIn("Deployment smoke test did not run successfully", p.stderr)
        self.assertFalse(self.release["draft"])
        self.assertEqual(self.written()[-1], "actions/workflows/deploy-swa.yml/dispatches")
        self.writes.clear()
        self.cli("release-plan", *self.release_args)
        self.assertEqual(self.outputs(), {"recovery": "true"})
        self.cli("publish", *self.release_args)
        self.assertEqual((self.writes, self.upload_calls()), ([], 1))
        self.deploy_run = "failure"
        with self.assertRaisesRegex(policy.Rejected, "deploy-swa: failure"):
            controller.deploy(self.client, self.tag)
        self.deploy_run = "success"
        self.smoke = "success"
        controller.deploy(self.client, self.tag)
        self.assertEqual(self.dispatched["deploy-swa.yml"], {"ref": "main", "inputs": {"ref": self.tag}})

    def test_latest_and_the_live_site_follow_only_the_highest_stable_version(self):
        self.tags = [{"name": "v2.2.0"}, {"name": "v2.4.0"}]
        p = self.release_flow()
        self.assertEqual((self.release["draft"], self.release["make_latest"]), (False, "false"))
        self.assertNotIn("actions/workflows/deploy-swa.yml/dispatches", self.written())
        self.assertIn("gh workflow run deploy-swa.yml -f ref=" + self.tag, p.stdout)

    def test_a_higher_prerelease_does_not_take_latest_from_a_stable_version(self):
        self.tags = [{"name": "v2.2.0"}, {"name": "v2.4.0-rc.1"}]
        self.release_flow()
        self.assertEqual(self.release["make_latest"], "true")
        self.assertEqual(self.dispatched["deploy-swa.yml"], {"ref": "main", "inputs": {"ref": self.tag}})

    def test_the_deploy_gate_serves_released_content_only(self):
        self.release_flow()
        self.g("tag", self.tag, self.squash)
        self.published = [{"tag_name": "v2.2.0", "draft": False, "prerelease": False}]

        def gate(*args, ok=True):
            p = self.cli("published-source", *args, ok=ok)
            return self.outputs(), p

        released = {"deploy": "true", "sha": self.squash, "tag": self.tag}
        self.assertEqual(gate("--head", self.squash)[0], released)
        for ref, sha, tag in [(self.tag, self.squash, self.tag), (self.squash, self.squash, self.tag),
                              ("v2.2.0", self.stable, "v2.2.0"), (self.stable, self.stable, "v2.2.0")]:
            with self.subTest("manual deploy of " + ref):
                self.assertEqual(gate("--head", self.squash, "--ref", ref)[0], {"deploy": "true", "sha": sha, "tag": tag})
        for ref in ("main", "refs/heads/main", "v2.4.0", self.base, self.squash[:12]):
            with self.subTest("refused manual deploy of " + ref):
                gate("--head", self.squash, "--ref", ref, ok=False)
                self.assertNotIn("deploy", self.outputs())
        with self.subTest("content merged by hand"):
            hand = self.commit_on(self.squash, {self.chapter: "# Merged by hand\n"})
            outputs, p = gate("--head", hand)
            self.assertEqual(outputs, {"deploy": "false", "sha": "", "tag": self.tag})
            self.assertIn("::notice::main carries book content that is not in the latest release " + self.tag, p.stdout)
            self.assertIn("Deploy skipped.", self.summary())
            self.assertIn(self.chapter, self.summary())
        with self.subTest("tooling pushed after the release"):
            tooling = self.commit_on(self.squash, {"tools/build.py": "# tooling\n"})
            self.assertEqual(gate("--head", tooling)[0], {"deploy": "true", "sha": tooling, "tag": self.tag})
            self.assertIn("Deploy allowed.", self.summary())
        with self.subTest("no published release"):
            self.release, self.published = None, []
            outputs, p = gate("--head", self.squash)
            self.assertEqual(outputs["deploy"], "false")
            self.assertIn("No published release exists yet", p.stdout)
        with self.subTest("the API is down"):
            self.fail_routes = {"releases"}
            gate("--head", self.squash, ok=False)
            self.assertNotIn("deploy", self.outputs())

    def test_pull_request_code_never_runs_in_the_controller(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        marker = Path(scratch.name) / "ran"
        evil = f"import pathlib\npathlib.Path({str(marker)!r}).write_text('pwned')\n"
        names = ["tools/release_policy.py", "tools/book_release.py", "json.py", "git.py", "sitecustomize.py"]
        self.retarget(self.commit_on(self.head, dict.fromkeys(names, evil)))
        p = self.cli("inspect")
        self.assertEqual(self.outputs(), {"eligible": "false"})
        self.assertIn("PR 7: Separate content from tooling", p.stdout)
        p = self.cli("merge", *self.params, ok=False)
        self.assertIn("Separate content from tooling", p.stderr)
        self.assertEqual(self.writes, [])
        self.assertFalse(marker.exists())
        for name in names:
            self.assertFalse((self.root / name).exists(), name)


class PrereleaseRehearsal(RehearsalBase):
    version = "2.3.0-rc.1"

    def test_a_prerelease_is_never_latest_and_never_deployed(self):
        self.release_flow()
        self.assertEqual((self.release["prerelease"], self.release["draft"]), (True, False))
        self.assertEqual(self.release["make_latest"], "false")
        self.assertEqual(set(self.dispatched), {"release.yml"})
        self.assertEqual(self.upload_calls(), 1)
        self.g("tag", self.tag, self.squash)
        self.published = [{"tag_name": "v2.2.0", "draft": False, "prerelease": False}]
        self.cli("published-source", "--head", self.squash)
        self.assertEqual(self.outputs()["deploy"], "false")
        for ref in (self.tag, self.squash):
            with self.subTest(ref):
                self.cli("published-source", "--head", self.squash, "--ref", ref, ok=False)
                self.assertNotIn("deploy", self.outputs())


class TrustedValidatorTests(Repository):
    """The preflight job validates the head with the validator from the base, never the one in the head."""

    def test_the_workflow_never_runs_the_validator_of_the_pull_request(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        work = Path(scratch.name)
        marker = work / "ran"
        evil = f"import pathlib\npathlib.Path({str(marker)!r}).write_text('pwned')\n"
        hostile = self.commit_on(self.prepare(), {"tools/release_policy.py": evil, "json.py": evil})
        self.g("worktree", "add", "-q", "--detach", str(work / "book"), hostile)
        self.addCleanup(self.g, "worktree", "remove", "--force", str(work / "book"))
        (work / "trusted" / "tools").mkdir(parents=True)
        shutil.copy(TOOLS / "release_policy.py", work / "trusted" / "tools" / "release_policy.py")
        line = re.search(r"run: (python .*release_policy\.py.*)", workflow_text.read("approved-book.yml")).group(1)
        command = shlex.split(line.replace('"$BASE"', self.base))
        command[0] = sys.executable

        def run(*args, cwd=work):
            return subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=60)

        p = run(*command)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Separate content from tooling", p.stderr)
        self.assertFalse(marker.exists())
        inside = [{"book": ".", "trusted/tools/release_policy.py": "../trusted/tools/release_policy.py"}.get(a, a)
                  for a in command]
        p = run(*inside, cwd=work / "book")
        self.assertIn("Separate content from tooling", p.stderr)
        self.assertFalse(marker.exists())
        with self.subTest("control: the hostile files do run without the isolated mode"):
            run(sys.executable, "-c", "import json", cwd=work / "book")
            self.assertTrue(marker.exists())
            marker.unlink()
            run(sys.executable, "book/tools/release_policy.py", "--root", "book", "--base", self.base)
            self.assertTrue(marker.exists())
