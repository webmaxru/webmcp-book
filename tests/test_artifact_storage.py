import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest import mock
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import artifact_storage as storage
import workflow_text as wf


def run(number, **changes):
    return dict(id=number, repository={"full_name": "test/book"}, head_repository={"full_name": "test/book"},
                path=storage.WORKFLOW, event="workflow_dispatch", head_branch="feature/a", head_sha="a" * 40,
                status="completed", conclusion="success", workflow_id=7, run_number=number, run_attempt=1, **changes)


def artifact(number, producer, ref="refs/heads/feature/a", **changes):
    return dict(id=number, name=storage.preview_name("test/book", 42, ref, producer["id"], producer["run_attempt"]),
                expired=False, created_at=f"2026-11-27T00:00:{number:02}Z",
                workflow_run=dict(id=producer["id"], repository_id=42, head_branch=producer["head_branch"],
                                  head_sha=producer["head_sha"]), **changes)


class PreviewCleanup(unittest.TestCase):
    def setUp(self):
        self.runs = {i: run(i) for i in range(1, 5)}
        self.artifacts = [artifact(i, self.runs[i]) for i in range(1, 5)]
        self.deleted = []
        self.upload = "success"
        self.fail = None
        self.restart = False
        self.reads = {}
        self.attempts = {}
        self.pages = []
        test = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                test.handle(self)

            def do_DELETE(self):
                test.handle(self)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01})
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        patch = mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "test/book", "GH_TOKEN": "fixture",
                                "GITHUB_API_URL": f"http://127.0.0.1:{self.server.server_port}"})
        patch.start()
        self.addCleanup(patch.stop)
        self.api = storage.GitHub()

    def handle(self, request):
        url = urlsplit(request.path)
        path = url.path.removeprefix("/repos/test/book/")
        if self.fail == (request.command, path):
            status, data = 500, {"message": "forced cleanup failure"}
        else:
            status, data = 200, {}
            if request.command == "DELETE":
                self.deleted.append(int(path.split("/")[-1]))
                status = 204
            elif path == "actions/artifacts":
                page = int(parse_qs(url.query)["page"][0])
                self.pages.append(page)
                data = {"artifacts": self.artifacts[(page - 1) * 100:page * 100]}
            elif path.startswith("actions/artifacts/"):
                data = next(a for a in self.artifacts if a["id"] == int(path.split("/")[-1]))
            elif path.endswith("/artifacts"):
                number = int(path.split("/")[2])
                data = {"artifacts": [a for a in self.artifacts if a["workflow_run"]["id"] == number]}
            elif path.endswith("/jobs"):
                data = {"jobs": [{"steps": [{"name": "Upload book preview", "conclusion": self.upload}]}]}
            elif "/attempts/" in path:
                data = self.attempts[tuple(map(int, (path.split("/")[2], path.split("/")[-1])))]
            else:
                number = int(path.split("/")[-1])
                self.reads[number] = self.reads.get(number, 0) + 1
                data = copy.deepcopy(self.runs[number])
                if self.restart and number == 1 and self.reads[number] > 1:
                    data["status"] = "in_progress"
                    data["run_attempt"] = 2
        request.send_response(status)
        request.end_headers()
        request.wfile.write(json.dumps(data).encode() if status != 204 else b"")

    def cleanup(self, number=3):
        storage.cleanup_previews(self.api, number, 42)

    def test_replacement_and_newer_previews_survive_reversed_completions(self):
        self.cleanup()
        self.assertEqual(self.deleted, [1, 2])
        self.deleted.clear()
        self.cleanup(2)
        self.assertEqual(self.deleted, [1])

    def test_pagination_is_snapshotted_and_unrelated_artifacts_survive(self):
        old = self.artifacts[0]
        self.artifacts = [dict(old, id=100 + i, name="diagnostic") for i in range(100)] + self.artifacts
        self.artifacts += [dict(old, id=300, name="editions-v3.0.0"),
                           dict(old, id=301, name=storage.preview_name("test/book", 42, "refs/heads/other", 1, 1))]
        self.cleanup()
        self.assertEqual(self.pages, [1, 2])
        self.assertEqual(self.deleted, [1, 2])

    def test_active_runs_other_workflows_and_restarted_runs_survive(self):
        self.runs[1]["status"] = "in_progress"
        self.runs[2]["workflow_id"] = 90
        self.cleanup()
        self.assertEqual(self.deleted, [])
        self.runs[1]["status"] = "completed"
        self.restart = True
        self.cleanup()
        self.assertEqual(self.deleted, [])

    def test_newer_run_with_an_earlier_upload_survives(self):
        self.artifacts[3]["created_at"] = self.artifacts[0]["created_at"]
        self.cleanup()
        self.assertEqual(self.deleted, [1, 2])

    def test_failed_or_missing_replacement_never_deletes_previous(self):
        for field in ("upload", "expired", "identity", "conclusion"):
            with self.subTest(field), mock.patch.object(self, "deleted", []):
                saved = copy.deepcopy(self.artifacts)
                if field == "upload":
                    self.upload = "failure"
                elif field == "expired":
                    self.artifacts[2]["expired"] = True
                elif field == "identity":
                    self.artifacts[2]["workflow_run"]["head_sha"] = "b" * 40
                else:
                    self.runs[3]["conclusion"] = "failure"
                with self.assertRaises(storage.Rejected):
                    self.cleanup()
                self.assertEqual(self.deleted, [])
                self.artifacts = saved
                self.upload = self.runs[3]["conclusion"] = "success"
        self.artifacts = [a for a in self.artifacts if a["id"] != 3]
        with self.assertRaisesRegex(storage.Rejected, "identity is missing"):
            self.cleanup()
        self.assertEqual(self.deleted, [])
        self.upload = "skipped"
        self.cleanup()
        self.assertEqual(self.deleted, [])

    def test_rerun_selects_current_upload_and_removes_completed_older_attempt(self):
        self.attempts[3, 1] = copy.deepcopy(self.runs[3])
        self.runs[3]["run_attempt"] = 2
        replacement = artifact(10, self.runs[3])
        self.artifacts.append(replacement)
        self.cleanup()
        self.assertEqual(self.deleted, [1, 2, 3])
        self.assertNotIn(10, self.deleted)

    def test_api_errors_are_not_success(self):
        for route in [("GET", "actions/artifacts"), ("DELETE", "actions/artifacts/1")]:
            self.fail = route
            with self.subTest(route), self.assertRaises(HTTPError):
                self.cleanup()
        self.assertEqual(self.deleted, [])

    def test_full_ref_and_repository_namespaces_are_distinct(self):
        names = {storage.preview_name(repo, 42, ref, 1, 1)
                 for repo in ["test/book", "test/other"] for ref in
                 ["refs/heads/feature/a", "refs/heads/feature-a", "refs/tags/feature/a"]}
        self.assertEqual(len(names), 6)


class ReleaseCleanup(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.folder.joinpath("book.pdf").write_bytes(b"edition")
        self.folder.joinpath("SHA256SUMS.txt").write_text(hashlib.sha256(b"edition").hexdigest() + "  book.pdf\n")
        self.assets = [dict(name=p.name, state="uploaded", size=p.stat().st_size,
                            digest="sha256:" + hashlib.sha256(p.read_bytes()).hexdigest())
                       for p in self.folder.iterdir()]
        self.jobs = [dict(name=n, status="completed", conclusion="success") for n in ("authorize", "build", "publish")]
        self.jobs.append(dict(name="cleanup-staging", status="in_progress", conclusion=None))
        self.api = mock.Mock(repo="test/book")
        self.release_run = run(3)
        self.release_run.update(path=".github/workflows/release.yml", head_branch="main")
        self.staging = artifact(10, self.release_run)
        self.staging["name"] = "editions-v1.0.0"
        self.api.rows.side_effect = lambda path, key=None: {
            "releases": [dict(id=12, tag_name="v1.0.0", draft=False)],
            "releases/12/assets": self.assets, "actions/runs/3/jobs": self.jobs}[path]
        self.api.api.side_effect = lambda path, method="GET": {
            "actions/runs/3": self.release_run, "actions/artifacts/10": self.staging}[path]
        for target, value in [("release_plan", True), ("metadata", {"file_stem": "book", "html_zip_stem": "book"})]:
            patch = mock.patch.object(storage, target, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch("book_release.asset_names", return_value={"book.pdf", "SHA256SUMS.txt"})
        patch.start()
        self.addCleanup(patch.stop)
        patch = mock.patch.dict(os.environ, {"GITHUB_RUN_ATTEMPT": "1"})
        patch.start()
        self.addCleanup(patch.stop)

    def cleanup(self):
        storage.cleanup_release(self.api, ".", 3, 10, 7, "h", "b", "m", "v1.0.0", self.folder)

    def test_verified_publication_removes_only_consumed_staging_id(self):
        self.cleanup()
        self.api.api.assert_called_with("actions/artifacts/10", "DELETE")

    def test_failed_or_uncertain_publication_retains_recovery(self):
        cases = ["publication", "digest", "assets", "consumer", "new-consumer", "identity", "attempt", "checksums"]
        for case in cases:
            with self.subTest(case):
                assets, jobs = copy.deepcopy(self.assets), copy.deepcopy(self.jobs)
                staging, release_run = copy.deepcopy(self.staging), copy.deepcopy(self.release_run)
                checksum = self.folder.joinpath("SHA256SUMS.txt").read_text()
                if case == "publication":
                    storage.release_plan.return_value = False
                elif case == "digest":
                    self.assets[0].pop("digest")
                elif case == "assets":
                    self.assets.pop()
                elif case == "consumer":
                    self.jobs[2]["conclusion"] = "failure"
                elif case == "new-consumer":
                    self.jobs.append(dict(name="future-consumer", status="in_progress", conclusion=None))
                elif case == "identity":
                    self.staging["workflow_run"]["id"] = 99
                elif case == "attempt":
                    self.release_run["run_attempt"] = 2
                else:
                    self.folder.joinpath("SHA256SUMS.txt").write_text("bad checksum")
                with self.assertRaises(storage.Rejected):
                    self.cleanup()
                self.assertFalse(any(c.args[-1] == "DELETE" for c in self.api.api.call_args_list))
                self.assets, self.jobs = assets, jobs
                self.staging, self.release_run = staging, release_run
                self.folder.joinpath("SHA256SUMS.txt").write_text(checksum)
                storage.release_plan.return_value = True
                self.api.reset_mock()


class WorkflowStorage(unittest.TestCase):
    def test_full_build_is_preserved_and_upload_is_explicit(self):
        ci = wf.read("ci.yml")
        self.assertEqual(wf.dispatch_inputs("ci.yml"), {"upload_preview": False})
        self.assertRegex(ci, r"upload_preview:\n(?: +[^\n]+\n)*? +type: boolean\n +default: false")
        self.assertIn("uses: ./.github/actions/build-editions", ci)
        steps = ci.split("      - ")
        uploads = [s for s in steps if "uses: actions/upload-artifact@" in s]
        self.assertEqual(len(uploads), 1)
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.upload_preview", uploads[0])
        self.assertIn("retention-days: 1", uploads[0])

    def test_cleanup_trust_permissions_and_release_dependency(self):
        preview = wf.jobs("preview-cleanup.yml")["cleanup"]
        self.assertEqual(wf.checkout_refs(preview), ["main"])
        self.assertNotIn("download-artifact", preview)
        self.assertNotIn("secrets.", preview)
        self.assertEqual(wf.permissions(preview), {"contents": "read", "actions": "write"})
        self.assertIn("cancel-in-progress: false", wf.read("preview-cleanup.yml"))
        release = wf.jobs("release.yml")
        cleanup = release["cleanup-staging"]
        self.assertEqual(wf.needs(cleanup), ["build", "publish"])
        self.assertIn("needs.publish.result == 'success'", cleanup)
        self.assertIn('release --artifact-id "$STAGING_ID"', cleanup)
        self.assertEqual(wf.checkout_refs(cleanup), ["main"])
        self.assertIn("retention-days: 7", release["build"])
        self.assertIn("artifact-ids: ${{ needs.build.outputs.artifact-id }}", cleanup)
        self.assertNotIn("artifact", wf.read("deploy-swa.yml"))
