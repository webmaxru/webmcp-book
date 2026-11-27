"""GitHub Actions controller. Never import or execute code from the PR in a write job."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # find release_policy next to this file, whoever loads it
from release_policy import (Rejected, git, is_stable, latest, metadata, release_notes, require, semver, unreleased,
                            validate)

OWNER = "webmaxru"
CHECK = "Book release preflight"


class GitHub:
    def __init__(self):
        self.repo = os.environ["GITHUB_REPOSITORY"]
        self.base = os.environ.get("GITHUB_API_URL", "https://api.github.com") + "/repos/" + self.repo + "/"

    def api(self, path, method="GET", body=None, optional=False):
        req = urllib.request.Request(self.base + path, method=method, headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2026-03-10" if path.endswith("/dispatches") else "2022-11-28",
        }, data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                data = res.read()
                return json.loads(data) if data else None
        except urllib.error.HTTPError as e:
            if optional and e.code == 404:
                return None
            raise

    def rows(self, path, key=None):
        separator = "&" if "?" in path else "?"
        for page in range(1, 101):
            obj = self.api(f"{path}{separator}per_page=100&page={page}")
            rows = obj[key] if key else obj
            yield from rows
            if len(rows) < 100:
                return
        raise Rejected("Pagination limit exceeded")


def sha(value):
    require(isinstance(value, str) and re.fullmatch("[0-9a-f]{40}", value), "Invalid commit SHA")
    return value


def login(row):
    return (row.get("user") or {}).get("login")


def approved(pr, reviews, comments, timeline, until=None):
    """Whether the owner authorized exactly this head, as of `until` (the merge time) or now.

    Only the owner authorizes. Someone else's pull request: the owner's latest formal review is an Approve on the
    head, and a comment-only review is neutral. The owner's own pull request: an owner comment that is exactly
    `/release-book <head>` and was never edited. Either must come strictly after the barrier, the latest Request
    changes or dismissed review by ANY reviewer or any review dismissal; only a fresh owner authorization crosses it.
    """
    end = until or "9999"
    head = pr["head"]["sha"]
    submitted = [r for r in reviews if r.get("submitted_at") and r["submitted_at"] <= end]
    formal = sorted((r for r in submitted if login(r) == OWNER
                     and r["state"] in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}),
                    key=lambda r: (r["submitted_at"], r["id"]))
    vetoes = [r["submitted_at"] for r in submitted if r["state"] in {"CHANGES_REQUESTED", "DISMISSED"}]
    dismissals = [e["created_at"] for e in timeline if e["event"] == "review_dismissed" and e["created_at"] <= end]
    barrier = max([""] + vetoes + dismissals)
    if login(pr) == OWNER:
        return any(login(c) == OWNER and c.get("body") == f"/release-book {head}"
                   and barrier < c["created_at"] <= end and c["updated_at"] == c["created_at"] for c in comments)
    latest = formal[-1] if formal else None
    return bool(latest and latest["state"] == "APPROVED" and latest.get("commit_id") == head
                and latest["submitted_at"] > barrier)


def approval(api, pr, until=None):
    n = pr["number"]
    return approved(pr, api.rows(f"pulls/{n}/reviews"), api.rows(f"issues/{n}/comments"),
                    api.rows(f"issues/{n}/timeline"), until)


def preflight(api, pr):
    head = sha(pr["head"]["sha"])
    runs = api.rows(f"actions/workflows/ci.yml/runs?event=pull_request&head_sha={head}", "workflow_runs")
    for r in runs:
        if (r["head_sha"] != head or r["head_branch"] != pr["head"]["ref"]
                or (r.get("head_repository") or {}).get("full_name") != api.repo):
            continue
        return r["conclusion"] == "success" and any(
            j["name"] == CHECK and j["conclusion"] == "success"
            for j in api.rows(f"actions/runs/{int(r['id'])}/jobs", "jobs"))
    return False


def scope(api, pr):
    require(pr["base"]["ref"] == "main" and (pr["head"].get("repo") or {}).get("full_name") == api.repo
            and pr["base"]["repo"]["full_name"] == api.repo, "Requires same repository and base main")


def fetch(root, ref):
    git(root, "fetch", "--quiet", "--no-tags", "origin", ref)


def candidate(api, root, n, head=None, base=None):
    pr = api.api(f"pulls/{n}")
    scope(api, pr)
    require(pr["state"] == "open" and not pr["draft"] and pr["mergeable"] is True, "Not open and mergeable")
    h, b = sha(pr["head"]["sha"]), sha(pr["base"]["sha"])
    require((not head or head == h) and (not base or base == b), "PR moved")
    require(approval(api, pr) and preflight(api, pr), "Missing current owner approval or preflight")
    fetch(root, f"refs/pull/{n}/head")
    require(git(root, "rev-parse", "FETCH_HEAD").strip() == h, "Fetched PR changed")
    require(git(root, "merge-base", b, h).strip() == b, "Head is behind main")
    tag = validate(root, b, h, content_only=True)
    require(api.api("git/ref/heads/main")["object"]["sha"] == b, "main moved")
    return {"pr": n, "head_sha": h, "base_sha": b, "tag": tag}


def event_numbers(api):
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    if "inputs" in event:
        return [int(event["inputs"]["pr"])]
    if "comment" in event:
        return [event["issue"]["number"]] if "pull_request" in event["issue"] else []
    if "workflow_run" in event and event["workflow_run"]["pull_requests"]:
        return [p["number"] for p in event["workflow_run"]["pull_requests"]][:20]
    return [p["number"] for p in api.api("pulls?state=open&base=main&sort=updated&per_page=30")]


def output(**values):
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
        for key, val in values.items():
            print(f"{key}={val}", file=f)


def summarize(text):
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            print(text, file=f)


def merge(api, root, n, h, b):
    data = candidate(api, root, n, sha(h), sha(b))
    response = api.api(f"pulls/{n}/merge", "PUT", {"sha": h, "merge_method": "squash"})
    require(response["merged"], "Conditional squash merge failed")
    data["merge_sha"] = sha(response["sha"])
    print("Release recovery inputs:", json.dumps(data), flush=True)
    api.api("actions/workflows/release.yml/dispatches", "POST",
            {"ref": "main", "inputs": {k: str(v) for k, v in data.items()}})


def asset_names(cfg, tag):
    return {cfg["file_stem"] + "-" + tag + ext for ext in [".pdf", ".epub"]} | {
        cfg["html_zip_stem"] + "-" + tag + ".zip", "SHA256SUMS.txt"}


def release_plan(api, root, n, h, b, m, tag):
    h, b, m = map(sha, (h, b, m))
    pr = api.api(f"pulls/{n}")
    scope(api, pr)
    require(pr["merged"] and pr["merge_commit_sha"] == m and pr["head"]["sha"] == h
            and pr["merged_by"]["login"] == "github-actions[bot]", "Not the controller-merged PR")
    require(approval(api, pr, pr["merged_at"]) and preflight(api, pr), "Missing approved-head provenance")
    fetch(root, h)
    git(root, "merge-base", "--is-ancestor", m, "origin/main")
    require(git(root, "show", "-s", "--format=%P", m).strip() == b, "Not a squash of the supplied base")
    require(git(root, "merge-base", b, h).strip() == b and
            git(root, "rev-parse", h + "^{tree}").strip() == git(root, "rev-parse", m + "^{tree}").strip(),
            "Merged tree differs from the approved tree")
    require(validate(root, b, h, content_only=True, existing_tag=True) == tag, "Wrong release tag")
    ref = api.api("git/ref/tags/" + tag, optional=True)
    if ref:
        require(ref["object"]["type"] == "tag", "Existing tag is not annotated")
        obj = api.api("git/tags/" + sha(ref["object"]["sha"]))
        require(obj["tag"] == tag and obj["object"]["type"] == "commit" and obj["object"]["sha"] == m,
                "Existing tag points elsewhere")
    releases = [r for r in api.rows("releases") if r["tag_name"] == tag]
    require(len(releases) <= 1, "Ambiguous release")
    if releases:
        release = releases[0]
        assets = list(api.rows(f"releases/{int(release['id'])}/assets"))
        names = asset_names(metadata(root, m), tag)
        require(ref and not release["draft"] and len(assets) == len(names)
                and {a["name"] for a in assets} == names
                and all(a["state"] == "uploaded" and a["size"] > 0 for a in assets),
                "Existing draft or incomplete release: inspect manually; no writes")
        return True
    require(not ref, "Tag exists without a release: inspect manually; no writes")
    return False


def newest(api, tag):
    """True when tag is the highest stable version, the only one that may be Latest or replace the live site."""
    return latest(tag, [t["name"] for t in api.rows("tags")])


def publish(api, root, n, h, b, m, tag, folder):
    if release_plan(api, root, n, h, b, m, tag):
        return False
    names = asset_names(metadata(root, m), tag)
    files = sorted(Path(folder).iterdir())
    require({p.name for p in files} == names and all(p.is_file() and p.stat().st_size for p in files),
            "Incomplete build artifact")
    checksums = {hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name for p in files
                 if p.name != "SHA256SUMS.txt"}
    require(set((Path(folder) / "SHA256SUMS.txt").read_text().splitlines()) == checksums, "Invalid checksums")
    notes = release_notes(git(root, "show", f"{m}:CHANGELOG.md"), tag[1:])
    notes = re.sub(r"\]\((?!https?:|#|mailto:)([^)]+)\)", rf"](https://github.com/{api.repo}/blob/{tag}/\1)", notes)
    obj = api.api("git/tags", "POST", {"tag": tag, "message": tag, "object": m, "type": "commit"})
    api.api("git/refs", "POST", {"ref": "refs/tags/" + tag, "sha": sha(obj["sha"])})
    draft = api.api("releases", "POST", {"tag_name": tag, "name": tag, "body": notes,
                                        "draft": True, "prerelease": "-" in tag})
    gh = shutil.which("gh")
    require(gh, "GitHub CLI is required for asset upload")
    subprocess.run([gh, "release", "upload", tag, "--repo", api.repo, *map(str, files)], check=True)
    endpoint = f"releases/{int(draft['id'])}"
    uploaded = list(api.rows(endpoint + "/assets"))
    sizes = {p.name: p.stat().st_size for p in files}
    require({a["name"]: a["size"] for a in uploaded if a["state"] == "uploaded"} == sizes,
            "Upload incomplete; leaving draft untouched")
    api.api(endpoint, "PATCH", {"draft": False, "make_latest": str(newest(api, tag)).lower()})
    return True


def deploy(api, tag):
    run = api.api("actions/workflows/deploy-swa.yml/dispatches", "POST",
                  {"ref": "main", "inputs": {"ref": tag}})
    require(run and run.get("workflow_run_id"), "Deploy dispatched but no run ID returned")
    run_id = int(run["workflow_run_id"])
    print(f"Watching deployment: {run['html_url']}", flush=True)
    for _ in range(150):
        status = api.api(f"actions/runs/{run_id}")
        if status["status"] == "completed":
            require(status["conclusion"] == "success", f"deploy-swa: {status['conclusion']}")
            jobs = api.rows(f"actions/runs/{run_id}/jobs", "jobs")
            require(any(s["name"] == "Smoke test" and s["conclusion"] == "success"
                        for job in jobs for s in job["steps"]), "Deployment smoke test did not run successfully")
            return
        time.sleep(10)
    raise Rejected(f"Timed out waiting for deployment run {run_id}")


def commit_of(root, tag):
    try:
        return git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}").strip()
    except subprocess.CalledProcessError:
        raise Rejected(f"Release tag {tag} is missing from this checkout") from None


def editions(api):
    """Tags of published stable releases, highest version first. A draft, a prerelease or a bare tag is no edition."""
    tags = {r["tag_name"] for r in api.rows("releases")
            if not r["draft"] and not r["prerelease"] and is_stable(r["tag_name"])}
    return sorted(tags, key=lambda t: semver(t[1:]), reverse=True)


def published_source(api, root, head, ref=""):
    """Production serves released editions only: decide what the deploy may build.

    Push to main: main itself, and only while its book content equals the latest published release.
    Manual run (the rollback path): a published release tag, or the full SHA of its commit.
    """
    def verdict(deploy, note, sha="", tag=""):
        return {"deploy": deploy, "sha": sha, "tag": tag, "note": note}

    tags = editions(api)
    if ref:
        if is_stable(ref):
            require(ref in tags, f"{ref} is not a published release")
            return verdict(True, f"Deploying released edition {ref}.", commit_of(root, ref), ref)
        require(re.fullmatch("[0-9a-f]{40}", ref),
                "A manual deploy takes a release tag (vX.Y.Z) or the full 40-character commit SHA of one")
        for tag in tags:
            try:
                if commit_of(root, tag) == ref:
                    return verdict(True, f"Deploying released edition {tag}.", ref, tag)
            except Rejected:
                continue
        raise Rejected(f"{ref} is not the commit of a published release")
    head = sha(head)
    if not tags:
        return verdict(False, "No published release exists yet, so there is nothing to serve. Deploy skipped.")
    tag = tags[0]
    paths = unreleased(root, commit_of(root, tag), head)
    if paths:
        shown = ", ".join(paths[:10]) + (f" and {len(paths) - 10} more" if len(paths) > 10 else "")
        return verdict(False, f"main carries book content that is not in the latest release {tag} ({shown}). "
                              "Production serves released editions only, so the deploy is skipped. Release that "
                              "content through the controller, or open a catch-up pull request with a higher "
                              "version.", tag=tag)
    return verdict(True, f"Book content equals the latest release {tag}; deploying {head[:12]}.", head, tag)


def report(decision):
    output(deploy=str(decision["deploy"]).lower(), sha=decision["sha"], tag=decision["tag"])
    print(("" if decision["deploy"] else "::notice::") + decision["note"], flush=True)
    summarize(("Deploy allowed. " if decision["deploy"] else "Deploy skipped. ") + decision["note"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["inspect", "merge", "release-plan", "publish", "published-source"])
    ap.add_argument("--root", default=".")
    ap.add_argument("--pr", type=int)
    for k in ["head", "base", "merge", "tag", "ref"]:
        ap.add_argument("--" + k)
    args = ap.parse_args()
    api = GitHub()
    if args.action == "published-source":
        report(published_source(api, args.root, args.head, args.ref or ""))
    elif args.action == "inspect":
        for number in event_numbers(api):
            try:
                data = candidate(api, args.root, number)
            except Rejected as e:
                print(f"PR {number}: {e}")
                continue
            output(eligible="true", **data)
            return
        output(eligible="false")
    elif args.action == "merge":
        merge(api, args.root, args.pr, args.head, args.base)
    else:
        params = (api, args.root, args.pr, args.head, args.base, args.merge, args.tag)
        if args.action == "release-plan":
            output(recovery=str(release_plan(*params)).lower())
        elif publish(*params, "release") and "-" not in args.tag:
            if newest(api, args.tag):
                deploy(api, args.tag)
            else:
                print(f"::notice::{args.tag} is published but is not the highest stable version, so the live "
                      "site keeps the newer edition. To serve it anyway: gh workflow run deploy-swa.yml -f ref="
                      + args.tag)


if __name__ == "__main__":
    try:
        main()
    except Rejected as error:
        sys.exit(str(error))
