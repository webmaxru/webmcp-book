import pathlib
import re
import sys
import unittest
from urllib.error import URLError

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import book_release as controller
import release_policy as policy
import workflow_text as wf
from check_upstream import survey


class UpstreamTests(unittest.TestCase):
    def test_error_does_not_hide_remaining_sources(self):
        def get(url):
            if "chromiumdash" in url:
                return url, '[{"version":"160.0"}]'
            if "registry.npmjs" in url:
                return url, "invalid json"
            if "releases/latest" in url:
                return url, '{"tag_name":"v0.2.0","html_url":"source","published_at":"date"}'
            if "chromestatus" in url:
                return url, (")]}'\n" + '{"stages":[{"stage_type":150,"desktop_first":149,"desktop_last":156,'
                             '"extensions":[{"stage_type":151,"desktop_last":162}]}],"updated":{"when":"today"},'
                             '"browsers":{"chrome":{"status":{"text":"trial"}}}}')
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
        self.assertEqual(rows["Chrome status"]["state"]["stages"][-1]["last"], 162)
        self.assertEqual(rows["W3C polyfill release"]["state"]["tag"], "v0.2.0")
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


class FlowSurfaceTests(unittest.TestCase):
    """What only a reader of the workflow files can check: where code comes from, who can write, what deploys."""

    CONTROLLED = ("approved-book.yml", "release.yml", "deploy-swa.yml")

    def test_every_job_that_can_merge_release_or_deploy_runs_only_from_main(self):
        for name in self.CONTROLLED:
            for job in wf.jobs(name):
                with self.subTest(f"{name}: {job}"):
                    self.assertTrue(wf.main_only(name, job))

    def test_trusted_code_comes_from_main_and_pull_request_code_is_only_read(self):
        approved, release = wf.jobs("approved-book.yml"), wf.jobs("release.yml")
        base, head = "${{ needs.authorize.outputs.base }}", "${{ needs.authorize.outputs.head }}"
        self.assertEqual(wf.checkout_refs(approved["authorize"]), ["main"])
        self.assertEqual(wf.checkout_refs(approved["merge"]), [base])
        self.assertEqual(wf.checkout_refs(release["authorize"]), ["main"])
        self.assertEqual(wf.checkout_refs(release["publish"]), ["main"])
        self.assertEqual(wf.checkout_refs(release["build"]), ["${{ inputs.merge_sha }}"])
        preflight = approved["preflight"]
        self.assertEqual(wf.checkout_refs(preflight), [base, head])
        self.assertEqual(re.findall(r"(?m)^          path:\s*(\S+)$", preflight), ["trusted", "book"])
        self.assertEqual(preflight.count("persist-credentials: false"), 2)
        self.assertIn('run: python -I -B trusted/tools/release_policy.py --root book --base "$BASE" --content-only',
                      preflight)
        self.assertIn("uses: ./trusted/.github/actions/build-editions", preflight)
        self.assertNotIn("uses: ./.github", preflight)
        self.assertNotRegex(preflight, r"GH_TOKEN|secrets\.")
        for name in ("approved-book.yml", "release.yml"):
            self.assertNotRegex(wf.read(name), r"pull_request_target|github\.head_ref|event\.pull_request\.head")

    def test_only_the_merge_job_and_the_publish_job_can_write(self):
        writers = {(name, job) for name in self.CONTROLLED for job, chunk in wf.jobs(name).items()
                   if "write" in wf.permissions(chunk).values()}
        self.assertEqual(writers, {("approved-book.yml", "merge"), ("release.yml", "publish")})
        self.assertEqual(wf.permissions(wf.jobs("approved-book.yml")["preflight"]), {"contents": "read"})
        self.assertEqual(wf.permissions(wf.jobs("release.yml")["build"]), {"contents": "read"})
        self.assertEqual(wf.permissions(wf.jobs("deploy-swa.yml")["published-source"]), {"contents": "read"})
        self.assertNotIn("write", wf.top_level(wf.read("deploy-swa.yml"), "permissions"))

    def test_production_deploys_only_what_the_gate_approved(self):
        name = "deploy-swa.yml"
        body, parts = wf.read(name), wf.jobs(name)
        self.assertEqual(set(parts), {"published-source", "deploy"})
        self.assertEqual(wf.needs(parts["deploy"]), ["published-source"])
        self.assertIn("needs.published-source.outputs.deploy == 'true'", parts["deploy"])
        self.assertIn("DEPLOY_REF: ${{ needs.published-source.outputs.sha }}", parts["deploy"])
        self.assertEqual(wf.checkout_refs(parts["deploy"]), ["${{ env.DEPLOY_REF }}"])
        self.assertEqual(wf.checkout_refs(parts["published-source"]), [None])
        self.assertIn("fetch-depth: 0", parts["published-source"])
        self.assertEqual(wf.commands(name), {"published-source": {frozenset({"--head", "--ref"})}})
        on = wf.top_level(body, "on")
        self.assertEqual(re.findall(r"(?m)^  ([\w-]+):", on), ["push", "workflow_dispatch"])
        self.assertNotRegex(on, r"(?m)^\s+(paths|paths-ignore|tags):")
        self.assertEqual(wf.dispatch_inputs(name), {"ref": True})
        self.assertRegex(wf.top_level(body, "concurrency"), r"group:\s*swa-production")
        self.assertRegex(wf.top_level(body, "concurrency"), r"cancel-in-progress:\s*false")
        for path in (*policy.DIRS, policy.META, "CHANGELOG.md", "VALIDATION.md"):
            self.assertNotIn(path, body, "the content definition belongs to tools/release_policy.py")

    def test_the_workflows_agree_with_each_other(self):
        titles = {path.name: re.search(r"(?m)^name:\s*(.+?)\s*$", path.read_text(encoding="utf-8"))[1]
                  for path in wf.WORKFLOWS.glob("*.yml")}
        for path in wf.WORKFLOWS.glob("*.yml"):
            for listed in re.findall(r"workflows:\s*\[(.+?)\]", wf.top_level(path.read_text(encoding="utf-8"), "on")):
                for title in listed.split(","):
                    self.assertIn(title.strip(), titles.values(), f"{path.name} listens to a workflow that is missing")
        self.assertIn(f"name: {controller.CHECK}", wf.read("ci.yml"))
        self.assertIn("- name: Smoke test", wf.read("deploy-swa.yml"))
        self.assertIs(controller.unreleased, policy.unreleased)

    def test_nothing_but_the_controller_publishes(self):
        for path in sorted(wf.WORKFLOWS.glob("*.yml")):
            body = path.read_text(encoding="utf-8")
            with self.subTest(path.name):
                self.assertNotRegex(wf.top_level(body, "on"), r"(?m)^\s+(tags|tags-ignore|release|create|delete):")
                self.assertNotRegex(wf.top_level(body, "on"), r"labeled|pull_request_target")
                for forbidden in ("--clobber", "gh release", "git push", "git tag", "action-gh-release", "create-release"):
                    self.assertNotIn(forbidden, body)
        source = (ROOT / "tools" / "book_release.py").read_text(encoding="utf-8")
        self.assertNotIn("--clobber", source)
        self.assertEqual(re.findall(r'"release", "(\w+)"', source), ["upload"])
