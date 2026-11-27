"""Bound temporary Actions artifacts. Cleanup runs trusted main code, never preview code."""
import argparse
import hashlib
import os
import re
import sys
import urllib.error

from book_release import GitHub, Rejected, metadata, release_files, release_plan, require


WORKFLOW = ".github/workflows/ci.yml"


def preview_name(repo, repo_id, ref, run_id, attempt):
    require(ref.startswith(("refs/heads/", "refs/tags/")), "Preview requires a full branch or tag ref")
    kind = ref.split("/")[1]
    key = hashlib.sha256((repo + "\nwebmcp-book\n" + ref).encode()).hexdigest()
    return f"book-preview-v1-{int(repo_id)}-{kind}-{key}-{int(run_id)}-{int(attempt)}"


def producer(api, run, workflow):
    require(run["repository"]["full_name"] == api.repo
            and run["head_repository"]["full_name"] == api.repo
            and run["path"].split("@")[0] == workflow, "Artifact producer identity mismatch")


def preview_identity(api, artifact, run, repo_id):
    producer(api, run, WORKFLOW)
    match = re.fullmatch(r"book-preview-v1-\d+-(heads|tags)-[0-9a-f]{64}-\d+-\d+", artifact["name"])
    require(match and run["event"] == "workflow_dispatch", "Not an explicit preview")
    ref = f"refs/{match[1]}/{run['head_branch']}"
    require(artifact["name"] == preview_name(api.repo, repo_id, ref, run["id"], run["run_attempt"]),
            "Preview namespace or producing attempt mismatch")
    producing = artifact["workflow_run"]
    require(producing["id"] == run["id"] and producing["repository_id"] == repo_id
            and producing["head_sha"] == run["head_sha"]
            and producing["head_branch"] == run["head_branch"], "Artifact run metadata mismatch")
    return ref


def cleanup_previews(api, run_id, repo_id):
    run = api.api(f"actions/runs/{run_id}")
    producer(api, run, WORKFLOW)
    require(run["status"] == "completed" and run["conclusion"] == "success", "Preview producer did not succeed")
    artifacts = list(api.rows(f"actions/runs/{run_id}/artifacts", "artifacts"))
    previews = [a for a in artifacts if a["name"].startswith("book-preview-v1-")]
    if not previews:
        print("No preview uploaded; nothing to replace.")
        return
    require(len(previews) == 1, "Ambiguous replacement preview")
    replacement = previews[0]
    ref = preview_identity(api, replacement, run, repo_id)
    require(not replacement["expired"], "Replacement preview expired")
    require(any(s["name"] == "Upload book preview" and s["conclusion"] == "success"
                for j in api.rows(f"actions/runs/{run_id}/jobs", "jobs") for s in j["steps"]),
            "Replacement upload did not succeed")
    replacement_id = int(replacement["id"])
    # Snapshot before deleting: pagination offsets must not move as we remove artifacts.
    candidates = list(api.rows("actions/artifacts", "artifacts"))
    prefix = replacement["name"].rsplit("-", 2)[0] + "-"
    for artifact in candidates:
        if (artifact["id"] == replacement_id or not artifact["name"].startswith(prefix)
                or artifact["created_at"] > replacement["created_at"]):
            continue
        old_id = artifact["workflow_run"]["id"]
        if old_id == run_id:
            continue
        old = api.api(f"actions/runs/{old_id}")
        if old["status"] != "completed":
            continue
        if old["workflow_id"] != run["workflow_id"] or old["path"].split("@")[0] != WORKFLOW:
            continue
        if (old["run_number"], old["run_attempt"]) >= (run["run_number"], run["run_attempt"]):
            continue
        require(preview_identity(api, artifact, old, repo_id) == ref, "Preview ref changed")
        # Reruns can restart between listing and deletion; never delete from a live attempt.
        current = api.api(f"actions/runs/{old_id}")
        if current["status"] != "completed" or current["run_attempt"] != old["run_attempt"]:
            continue
        preview_identity(api, artifact, current, repo_id)
        live = api.api(f"actions/artifacts/{replacement_id}")
        require(live["id"] == replacement_id and not live["expired"]
                and live["name"] == replacement["name"], "Replacement is no longer available")
        preview_identity(api, live, run, repo_id)
        api.api(f"actions/artifacts/{int(artifact['id'])}", "DELETE")
        print(f"Deleted superseded preview artifact {artifact['id']}")


def cleanup_release(api, root, run_id, artifact_id, n, h, b, m, tag, folder):
    require(release_plan(api, root, n, h, b, m, tag), "Release is not completely published")
    files = release_files(metadata(root, m), tag, folder)
    releases = [r for r in api.rows("releases") if r["tag_name"] == tag and not r["draft"]]
    require(len(releases) == 1, "Published release identity missing")
    assets = list(api.rows(f"releases/{int(releases[0]['id'])}/assets"))
    expected = {p.name: (p.stat().st_size, "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
    require(len(assets) == len(expected) and
            {a["name"]: (a["size"], a.get("digest")) for a in assets if a["state"] == "uploaded"} == expected,
            "Published asset integrity is missing or differs; retaining recovery artifact")
    run = api.api(f"actions/runs/{run_id}")
    producer(api, run, ".github/workflows/release.yml")
    require(run["event"] == "workflow_dispatch" and run["head_branch"] == "main"
            and run["run_attempt"] == int(os.environ["GITHUB_RUN_ATTEMPT"]), "Untrusted release run or attempt")
    jobs = list(api.rows(f"actions/runs/{run_id}/jobs", "jobs"))
    require({j["name"] for j in jobs} == {"authorize", "build", "publish", "cleanup-staging"}
            and all(j["status"] == "completed" and j["conclusion"] == "success"
                    for j in jobs if j["name"] != "cleanup-staging"), "Artifact consumers have not all succeeded")
    artifact = api.api(f"actions/artifacts/{artifact_id}")
    require(artifact["id"] == artifact_id and artifact["name"] == f"editions-{tag}"
            and artifact["workflow_run"]["id"] == run_id
            and artifact["workflow_run"]["head_sha"] == run["head_sha"]
            and artifact["workflow_run"]["head_branch"] == "main" and not artifact["expired"],
            "Release staging identity mismatch")
    api.api(f"actions/artifacts/{artifact_id}", "DELETE")
    print(f"Deleted verified publication staging artifact {artifact_id}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["preview-name", "previews", "release"])
    parser.add_argument("--run-id", type=int, default=os.environ.get("GITHUB_RUN_ID"))
    parser.add_argument("--repo-id", type=int, default=os.environ.get("GITHUB_REPOSITORY_ID"))
    parser.add_argument("--artifact-id", type=int)
    parser.add_argument("--pr", type=int)
    for name in ("head", "base", "merge", "tag"):
        parser.add_argument("--" + name)
    args = parser.parse_args()
    if args.action == "preview-name":
        name = preview_name(os.environ["GITHUB_REPOSITORY"], args.repo_id, os.environ["GITHUB_REF"],
                            args.run_id, os.environ["GITHUB_RUN_ATTEMPT"])
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            print("name=" + name, file=output)
    elif args.action == "previews":
        cleanup_previews(GitHub(), args.run_id, args.repo_id)
    else:
        require(args.artifact_id, "Replacement staging upload ID is missing")
        cleanup_release(GitHub(), ".", args.run_id, args.artifact_id,
                        args.pr, args.head, args.base, args.merge, args.tag, "release")


if __name__ == "__main__":
    try:
        main()
    except (Rejected, KeyError, ValueError, urllib.error.URLError) as error:
        sys.exit(f"::error::Artifact cleanup refused: {error}")
