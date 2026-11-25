"""Read-only inventory for /update-book. A signal is a lead, not a verified claim."""
import argparse
import datetime as dt
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

from release_policy import changed, git, highest_stable, metadata

GH = "https://api.github.com/repos/"
SOURCES = {
    "WebMCP draft": GH + "webmachinelearning/webmcp/commits?path=index.bs",
    "Blink implementation": GH + "chromium/chromium/commits?path=third_party/blink/renderer/core/script_tools",
    "Chrome status": "https://chromestatus.com/api/v0/features/5117755740913664",
    "Chrome stable (Linux)": "https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Linux&num=1",
    "W3C polyfill": "https://registry.npmjs.org/@w3c/webmcp-polyfill/latest",
    "MCP specification": "https://modelcontextprotocol.io/specification/latest",
    "Companion demos": GH + "webmaxru/webmcp-book-demos/commits?sha=main",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "webmcp-book/check-upstream"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.geturl(), r.read().decode("utf-8")


def survey(cfg, read=fetch):
    since = dt.datetime.strptime(cfg["spec_date"], "%d %B %Y").date()
    rows = []
    for name, url in SOURCES.items():
        try:
            if url.startswith(GH):
                url += f"&since={since}T00:00:00Z&per_page=10"
            final, body = read(url)
            if name == "MCP specification":
                match = re.search(r"/specification/(\d{4}-\d\d-\d\d)", final)
                if not match:
                    raise ValueError(f"Cannot determine revision from {final}")
                state = match[1]
            else:
                obj = json.loads(body.removeprefix(")]}'\n"))
                if url.startswith(GH):
                    state = [{"date": c["commit"]["committer"]["date"], "change": c["commit"]["message"].splitlines()[0],
                              "source": c["html_url"]} for c in obj]
                elif name == "Chrome status":
                    state = {"updated": obj["updated"]["when"], "status": obj["browsers"]["chrome"]["status"]["text"],
                             "stages": [{"stage": s["stage_type"], "first": s.get("desktop_first"),
                                         "last": s.get("desktop_last")} for s in obj["stages"] if s.get("desktop_first")]}
                elif name.startswith("Chrome stable"):
                    state = {"current": obj[0]["version"], "book_tested": cfg["chrome_version"]}
                else:
                    state = obj["version"]
            rows.append({"source": name, "url": url, "state": state})
        except (OSError, ValueError, IndexError, TypeError, KeyError) as e:
            rows.append({"source": name, "url": url, "unavailable": str(e)})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=Path(__file__).resolve().parents[1])
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    cfg = metadata(a.root, a.ref)
    tag = highest_stable(git(a.root, "tag", "--merged", a.ref).splitlines())
    print(json.dumps({"baseline": {k: cfg[k] for k in ("version", "edition", "spec_date", "chrome_version")},
                      "previous_stable": tag, "ref": git(a.root, "rev-parse", a.ref).strip(),
                      "unreleased_reader_files": sorted(p for p in changed(a.root, tag, a.ref)
                                                        if p.startswith(("manuscript/", "outline/", "figures/"))),
                      "signals": survey(cfg)}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
