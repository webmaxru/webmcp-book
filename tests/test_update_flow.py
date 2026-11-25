import pathlib
import sys
import unittest
from urllib.error import URLError

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_upstream import survey


class UpstreamTests(unittest.TestCase):
    def test_error_does_not_hide_remaining_sources(self):
        def get(url):
            if "chromiumdash" in url:
                return url, '[{"version":"160.0"}]'
            if "registry.npmjs" in url:
                return url, "invalid json"
            if "chromestatus" in url:
                return url, ")]}'\n" + '{"stages":[],"updated":{"when":"today"},"browsers":{"chrome":{"status":{"text":"trial"}}}}'
            if "specification/latest" in url:
                return url.replace("latest", "2026-07-28"), "<html></html>"
            if "webmcp-book-demos" in url:
                raise URLError("offline")
            self.assertIn("since=2026-10-27T00:00:00Z", url)
            return url, '[{"html_url":"source","commit":{"committer":{"date":"date"},"message":"change\\ndetail"}}]'
        rows = {r["source"]: r for r in survey({"spec_date": "27 October 2026", "chrome_version": "156"}, get)}
        self.assertEqual(rows["WebMCP draft"]["state"][0]["change"], "change")
        self.assertEqual(rows["Chrome stable (Linux)"]["state"], {"current": "160.0", "book_tested": "156"})
        self.assertEqual(rows["MCP specification"]["state"], "2026-07-28")
        self.assertEqual(rows["Chrome status"]["state"]["status"], "trial")
        self.assertIn("offline", rows["Companion demos"]["unavailable"])
        self.assertIn("unavailable", rows["W3C polyfill"])


class WorkflowTests(unittest.TestCase):
    def test_controller_and_release_trust_boundaries(self):
        workflows = ROOT / ".github/workflows"
        text = (workflows / "approved-book.yml").read_text()
        for trigger in ["workflow_run:", "issue_comment:", "schedule:", "workflow_dispatch:"]:
            self.assertIn(trigger, text)
        self.assertIn("permissions: {}", text)
        self.assertIn("group: approved-book", text)
        self.assertIn("trusted/tools/release_policy.py --root book", text)
        self.assertNotIn("contents: write", text.split("\n  merge:")[0])
        signal = (workflows / "book-approval-signal.yml").read_text()
        self.assertIn("pull_request_review:", signal)
        self.assertIn("permissions: {}", signal)
        self.assertNotIn("checkout", signal)
        ci = (workflows / "ci.yml").read_text()
        self.assertIn("name: Book release preflight", ci)
        self.assertIn("needs: build", ci)
        self.assertIn("if: always()", ci)
        release = (workflows / "release.yml").read_text()
        self.assertNotIn("push:", release)
        self.assertIn("workflow_dispatch:", release)
        self.assertIn("ref: ${{ inputs.merge_sha }}", release)
        self.assertIn("publish:\n    needs: build", release)
        self.assertNotIn("--clobber", release)
        self.assertNotIn("contents: write", release.split("\n  publish:")[0])
        build = (ROOT / ".github/actions/build-editions/action.yml").read_text()
        self.assertNotIn("--with-deps", ci + release + text + build)
        self.assertIn("timeout 4m python -m playwright install chromium", build)
        self.assertIn("timeout 12m python tools/build.py all", build)
        self.assertIn("epubcheck.jar", build)
