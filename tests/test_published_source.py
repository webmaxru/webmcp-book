"""The deploy gate: production serves released editions only (tools/book_release.py published-source)."""
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_book_release as fixtures

controller, policy = fixtures.controller, fixtures.policy

TOOLING = ["tools/build.py", "theme/site.css", "README.md", "DEPLOY.md", "RELEASING.md", ".github/workflows/ci.yml",
           "infra/main.bicep", "tests/test_x.py", "staticwebapp.config.json", "manuscript.bak/old.md"]
CONTENT = ["manuscript/01-intro.md", "manuscript/02-new.md", "outline/plan.md", "editorial/log.md", "figures/a.svg",
           "VALIDATION.md", "CHANGELOG.md"]


class FakeAPI:
    repo = "test/book"

    def __init__(self, *releases, error=None):
        self.releases, self.error = releases, error

    def rows(self, path, key=None):
        assert (path, key) == ("releases", None), path
        if self.error:
            raise self.error
        yield from self.releases


def rel(tag, draft=False, prerelease=False):
    return {"tag_name": tag, "draft": draft, "prerelease": prerelease}


class GateTests(fixtures.Repository):
    def setUp(self):
        super().setUp()
        self.released = self.prepare()
        self.g("tag", "v2.3.0", self.released)
        self.api = FakeAPI(rel("v2.3.0"), rel("v2.2.0"))

    def decide(self, head, ref="", api=None):
        return controller.published_source(api or self.api, self.root, head, ref)

    def after_release(self, files):
        return self.commit_on(self.released, files)

    def outcome(self, verdict):
        return verdict["deploy"], verdict["sha"], verdict["tag"]

    def test_a_push_of_tooling_deploys_the_released_content(self):
        for path in TOOLING:
            with self.subTest(path):
                self.assertFalse(policy.allowed(path))
                head = self.after_release({path: "changed"})
                self.assertEqual(self.outcome(self.decide(head)), (True, head, "v2.3.0"))
        self.assertEqual(self.outcome(self.decide(self.released)), (True, self.released, "v2.3.0"))

    def test_a_push_of_unreleased_book_content_is_skipped(self):
        for path in CONTENT:
            with self.subTest(path):
                self.assertTrue(policy.allowed(path))
                verdict = self.decide(self.after_release({path: "changed"}))
                self.assertEqual(self.outcome(verdict), (False, "", "v2.3.0"))
                self.assertIn(path, verdict["note"])

    def test_only_the_release_keys_of_the_book_configuration_are_content(self):
        for key in sorted(policy.KEYS):
            with self.subTest(key):
                head = self.after_release({policy.META: json.dumps(dict(self.cfg, **{key: "changed"}))})
                verdict = self.decide(head)
                self.assertFalse(verdict["deploy"])
                self.assertIn(policy.META, verdict["note"])
        head = self.after_release({policy.META: json.dumps(dict(self.cfg, file_stem="Other"))})
        self.assertTrue(self.decide(head)["deploy"])

    def test_the_gate_asks_the_release_policy_what_content_is(self):
        head = self.after_release({"chapters/new.md": "text"})
        self.assertTrue(self.decide(head)["deploy"])
        with mock.patch.object(policy, "DIRS", policy.DIRS + ("chapters/",)):
            self.assertFalse(self.decide(head)["deploy"])

    def test_main_ahead_of_the_latest_release_is_skipped_and_the_note_lists_what_differs(self):
        verdict = self.decide(self.released, api=FakeAPI(rel("v2.2.0")))
        self.assertEqual(self.outcome(verdict), (False, "", "v2.2.0"))
        for path in ("CHANGELOG.md", self.chapter, policy.META):
            self.assertIn(path, verdict["note"])
        many = self.after_release({f"manuscript/{i:02d}-new.md": "text" for i in range(12)})
        self.assertIn("and 2 more", self.decide(many)["note"])

    def test_content_equal_to_an_older_release_is_not_served_on_push(self):
        verdict = self.decide(self.stable)
        self.assertEqual(self.outcome(verdict), (False, "", "v2.3.0"))

    def test_drafts_prereleases_and_unpublished_tags_are_not_editions(self):
        api = FakeAPI(rel("v2.3.0", draft=True), rel("v2.4.0-rc.1", prerelease=True), rel("v2.5.0-rc.2"),
                      rel("nightly"), rel("v2.2.0"))
        self.assertEqual(controller.editions(api), ["v2.2.0"])
        self.assertEqual(self.outcome(self.decide(self.released, api=api)), (False, "", "v2.2.0"))

    def test_without_a_published_release_nothing_is_served_on_push(self):
        for api in (FakeAPI(), FakeAPI(rel("v2.3.0", draft=True), rel("v2.3.1-rc.1", prerelease=True))):
            verdict = self.decide(self.released, api=api)
            self.assertEqual(self.outcome(verdict), (False, "", ""))
            self.assertIn("No published release exists yet", verdict["note"])

    def test_the_gate_fails_closed(self):
        with self.assertRaisesRegex(policy.Rejected, "Release tag v2.4.0 is missing"):
            self.decide(self.released, api=FakeAPI(rel("v2.4.0"), rel("v2.3.0")))
        down = FakeAPI(error=urllib.error.HTTPError("http://example.test", 500, "down", {}, None))
        with self.assertRaises(urllib.error.HTTPError):
            self.decide(self.released, api=down)
        with self.assertRaisesRegex(policy.Rejected, "Invalid commit SHA"):
            self.decide("main")

    def test_a_manual_deploy_takes_the_tag_or_the_sha_of_a_published_release(self):
        for ref, sha, tag in [("v2.3.0", self.released, "v2.3.0"), (self.released, self.released, "v2.3.0"),
                              ("v2.2.0", self.stable, "v2.2.0"), (self.stable, self.stable, "v2.2.0")]:
            with self.subTest(ref):
                self.assertEqual(self.outcome(self.decide(self.released, ref)), (True, sha, tag))

    def test_a_manual_deploy_refuses_everything_unreleased(self):
        drafted = self.after_release({"outline/plan.md": "not released"})
        self.g("tag", "v2.4.0", drafted)
        api = FakeAPI(rel("v2.3.0"), rel("v2.2.0"), rel("v2.4.0", draft=True))
        unpublished, unknown = "is not a published release", "manual deploy takes"
        for ref, message in [
            ("v2.4.0", unpublished), ("v9.9.9", unpublished),
            ("v2.5.0-rc.1", unknown), ("main", unknown), ("refs/heads/main", unknown),
            (self.released[:12], unknown), (self.released.upper(), unknown),
            (self.base, "is not the commit of a published release"),
            (drafted, "is not the commit of a published release"),
        ]:
            with self.subTest(ref), self.assertRaisesRegex(policy.Rejected, message):
                self.decide(self.released, ref, api)


if __name__ == "__main__":
    unittest.main()
