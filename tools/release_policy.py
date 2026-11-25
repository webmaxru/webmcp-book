"""Local release policy. Inspect Git objects, not files imported from a candidate."""
import argparse
import datetime
import json
import re
import subprocess
from pathlib import PurePosixPath


class Rejected(ValueError):
    """The candidate does not meet release policy."""


META = "tools/book.json"
KEYS = {"version", "edition", "chrome_version", "spec_date", "year"}
DIRS = ("manuscript/", "outline/", "editorial/", "figures/")
NUMBER = r"(?:0|[1-9]\d*)"
VERSION = rf"({NUMBER})\.({NUMBER})\.({NUMBER})(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"


def require(ok, reason):
    if not ok:
        raise Rejected(reason)


def semver(version):
    m = re.fullmatch(VERSION, version, re.ASCII)
    require(m, f"Invalid book version: {version!r}")
    pre = m[4]
    parts = []
    for field in pre.split(".") if pre else ():
        require(not (field.isdigit() and len(field) > 1 and field.startswith("0")),
                f"Leading zero in prerelease: {version}")
        parts.append((0, int(field)) if field.isdigit() else (1, field))
    return (*map(int, m.groups()[:3]), pre is None, tuple(parts))


def highest_stable(tags):
    stable = [t for t in tags if re.fullmatch(rf"v{NUMBER}\.{NUMBER}\.{NUMBER}", t, re.ASCII)]
    require(stable, "No stable book tag")
    return max(stable, key=lambda t: semver(t[1:]))


def latest(tag, tags):
    return "-" not in tag and highest_stable([*tags, tag]) == tag


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args]).decode("utf-8")


def changed(root, base, head):
    return set(git(root, "diff", "--no-renames", "--name-only", "-z", base, head).split("\0")) - {""}


def allowed(path):
    return path in {META, "CHANGELOG.md", "VALIDATION.md"} or path.startswith(DIRS)


def metadata(root, rev):
    return json.loads(git(root, "show", f"{rev}:{META}"))


def release_notes(text, version):
    headings = list(re.finditer(r"^## \[([^\]\n]+)\]([^\n]*)$", text, re.M))
    hits = [i for i, h in enumerate(headings) if h[1] == version]
    require(len(hits) == 1, f"Expected one CHANGELOG section for {version}")
    i = hits[0]
    date = re.fullmatch(r" - (\d{4}-\d{2}-\d{2})", headings[i][2].rstrip())
    require(date, f"Missing release date for {version}")
    datetime.date.fromisoformat(date[1])
    end = headings[i+1].start() if i+1 < len(headings) else len(text)
    notes = re.sub(r"^\[[^\]]+\]: \S+[ \t]*$", "", text[headings[i].end():end], flags=re.M).strip()
    require(notes, "Empty release notes")
    return notes


def evidence(paths, existing):
    chapters = [PurePosixPath(p).stem for p in paths
                if re.fullmatch(r"manuscript/(?:\d\d-|appendix-)[^/]+\.md", p)]
    for chapter in chapters:
        log = f"editorial/{chapter}-editorial-log.md"
        fidelity = f"editorial/fidelity/{chapter}.md"
        require(log in paths & existing, f"Update {log}")
        require(fidelity in paths & existing or any(
            re.fullmatch(r"editorial/fidelity-ledger(?:-[\w-]+)?\.md", p) for p in paths & existing
        ), f"Update {fidelity} or a shared fidelity ledger for {chapter}")
    require(not chapters or "VALIDATION.md" in paths & existing, "Update VALIDATION.md for changed chapters")


def validate(root, base, head, *, content_only=False, existing_tag=False):
    """Use the PR delta for scope; the edition delta for release substance."""
    paths = changed(root, base, head)
    old, new = metadata(root, base), metadata(root, head)
    version = new["version"]
    key_changes = {k for k in old.keys() | new.keys() if k not in old or k not in new or old[k] != new[k]}
    tooling = {p for p in paths if not allowed(p)}
    if key_changes - KEYS:
        tooling.add(META)
    release_paths = paths - tooling - {META}
    candidate = bool(release_paths or key_changes & KEYS)
    if not candidate:
        require(not content_only, "Not a content PR")
        return None
    require(not tooling, f"Separate content from tooling: {sorted(tooling)}")
    tree = git(root, "ls-tree", "-r", "-z", head).split("\0")
    modes = {entry.split("\t", 1)[1]: entry.split()[0] for entry in tree if entry}
    for p in paths & modes.keys():
        require(modes[p] in {"100644", "100755"}, f"Not a regular file: {p}")
    tags = git(root, "tag", "--list").splitlines()
    tag = "v" + version
    require(existing_tag or tag not in tags, f"Tag already exists: {tag}")
    # During recovery, later editions may already exist. Use stable tags reachable
    # at the approved parent; never count the candidate's own tag as its baseline.
    previous = highest_stable(git(root, "tag", "--merged", base).splitlines() if existing_tag else tags)
    git(root, "merge-base", "--is-ancestor", previous, base)
    require(semver(version) > semver(previous[1:]), f"Version must exceed {previous}")
    require(semver(version) > semver(old["version"]), "PR must advance the version on main")
    edition = changed(root, previous, head)
    require(any(p.startswith(("manuscript/", "outline/", "figures/")) for p in edition),
            "Version bump without reader-facing changes since the last stable tag")
    evidence(paths, set(modes))
    release_notes(git(root, "show", f"{head}:CHANGELOG.md"), version)
    require("CHANGELOG.md" in paths, "Add the dated CHANGELOG section in this PR")
    return tag


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--content-only", action="store_true")
    args = ap.parse_args()
    print(validate(args.root, args.base, args.head, content_only=args.content_only) or "Tooling only")
