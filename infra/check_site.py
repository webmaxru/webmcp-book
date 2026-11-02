#!/usr/bin/env python3
"""Pre-upload check of the built web edition against staticwebapp.config.json.

    python3 infra/check_site.py [dist/site] [--update-csp]

Checks, with the Python standard library only:
  - staticwebapp.config.json (repo root) is valid JSON and has the keys the deploy relies on;
  - dist/site has index.html and 404.html and fits the Static Web Apps Free plan
    (250 MB per environment, 15,000 files: https://learn.microsoft.com/azure/static-web-apps/quotas);
  - the Content-Security-Policy allows what the pages actually load:
      * every inline <script> has its sha256 hash in script-src,
      * no inline event handlers (onclick=...) and no style="" attributes (blocked by style-src 'self'),
      * every inline <style> block has its sha256 hash in style-src,
      * every external host in <script src>, <link href> (stylesheets, preload, icons, manifest)
        and <img src> is allowed by the matching directive.
--update-csp rewrites the script-src / style-src hash lists in staticwebapp.config.json (and the
copy in dist/site) from what the pages contain, then checks again.
Exit code 0 = ready to upload, 1 = a problem that would break or weaken the live site.
"""
import base64
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "staticwebapp.config.json"
MAX_BYTES = 250 * 1024 * 1024
MAX_FILES = 15000


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.inline_scripts, self.inline_styles, self.problems, self.external = [], [], [], []
        self._in = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for name, _ in attrs:
            if name.startswith("on"):
                self.problems.append(f"inline event handler <{tag} {name}=...> (blocked by the CSP)")
            if name == "style":
                self.problems.append(f"style attribute on <{tag}> (blocked by style-src 'self')")
        if tag == "script":
            if a.get("src"):
                self.external.append(("script-src", a["src"]))
            elif a.get("type", "text/javascript") in ("text/javascript", "module", "application/javascript", ""):
                self._in, self._buf = "script", []
        elif tag == "style":
            self._in, self._buf = "style", []
        elif tag == "link" and a.get("href"):
            rel = (a.get("rel") or "").lower()
            if "stylesheet" in rel:
                self.external.append(("style-src", a["href"]))
            elif "preload" in rel and a.get("as") == "font":
                self.external.append(("font-src", a["href"]))
            elif "manifest" in rel:
                self.external.append(("manifest-src", a["href"]))
            elif "icon" in rel:
                self.external.append(("img-src", a["href"]))
        elif tag in ("img", "source") and a.get("src"):
            self.external.append(("img-src", a["src"]))
        elif tag == "iframe" and a.get("src"):
            self.external.append(("frame-src", a["src"]))

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)

    def handle_entityref(self, name):
        if self._in:
            self._buf.append(f"&{name};")

    def handle_charref(self, name):
        if self._in:
            self._buf.append(f"&#{name};")

    def handle_endtag(self, tag):
        if self._in and tag == self._in:
            body = "".join(self._buf)
            if body.strip():
                (self.inline_scripts if tag == "script" else self.inline_styles).append(body)
            self._in = None


def sha(body):
    return "'sha256-" + base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode() + "'"


def parse_csp(csp):
    out = {}
    for part in csp.split(";"):
        bits = part.split()
        if bits:
            out[bits[0].lower()] = bits[1:]
    return out


def allowed(directive, csp, url):
    sources = csp.get(directive, csp.get("default-src", []))
    u = urlparse(url)
    if not u.scheme and not url.startswith("//"):
        return True  # same-origin relative URL
    if u.scheme == "data":
        return "data:" in sources
    host = u.netloc
    for s in sources:
        s2 = s.strip("'")
        if s in ("*", "https:") and u.scheme == "https":
            return True
        if s2 == host or s2 == f"https://{host}" or (s2.startswith("https://*.") and host.endswith(s2[9:])):
            return True
    return False


def main(argv):
    site = Path(next((a for a in argv if not a.startswith("--")), ROOT / "dist" / "site")).resolve()
    update = "--update-csp" in argv
    errors, warnings = [], []

    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: {CONFIG} not found"); return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: {CONFIG.name} is not valid JSON: {e}"); return 1
    csp_text = cfg.get("globalHeaders", {}).get("Content-Security-Policy", "")
    if not csp_text:
        errors.append("globalHeaders.Content-Security-Policy is missing")
    if cfg.get("responseOverrides", {}).get("404", {}).get("rewrite") != "/404.html":
        warnings.append("responseOverrides.404 does not rewrite to /404.html")

    if not site.is_dir():
        print(f"ERROR: {site} does not exist. Build first: python3 tools/build.py site"); return 1
    files = [p for p in site.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    for need in ("index.html", "404.html"):
        if not (site / need).is_file():
            errors.append(f"{need} is missing from {site.name}/")
    if len(files) > MAX_FILES:
        errors.append(f"{len(files)} files; the Free plan allows {MAX_FILES}")
    if total > MAX_BYTES:
        errors.append(f"{total / 1048576:.1f} MB; the Free plan allows 250 MB per environment")

    script_hashes, style_hashes, external, problems = set(), set(), set(), {}
    pages = sorted(site.rglob("*.html"))
    for p in pages:
        parser = Page()
        parser.feed(p.read_text(encoding="utf-8", errors="replace"))
        script_hashes.update(sha(b) for b in parser.inline_scripts)
        style_hashes.update(sha(b) for b in parser.inline_styles)
        external.update(parser.external)
        for msg in parser.problems:
            problems.setdefault(msg, []).append(str(p.relative_to(site)))

    if update and csp_text:
        csp = parse_csp(csp_text)
        for directive, hashes in (("script-src", script_hashes), ("style-src", style_hashes)):
            keep = [s for s in csp.get(directive, ["'self'"]) if not s.startswith("'sha256-")]
            csp[directive] = keep + sorted(hashes)
        csp_text = "; ".join(" ".join([k] + v) for k, v in csp.items())
        cfg["globalHeaders"]["Content-Security-Policy"] = csp_text
        text = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
        CONFIG.write_text(text, encoding="utf-8")
        if (site / CONFIG.name).exists() or site.name == "site":
            (site / CONFIG.name).write_text(text, encoding="utf-8")
        print(f"updated CSP hashes: {len(script_hashes)} script, {len(style_hashes)} style")

    csp = parse_csp(csp_text)
    for h in sorted(script_hashes):
        if h not in csp.get("script-src", []):
            errors.append(f"inline <script> with hash {h} is not in script-src (run with --update-csp)")
    for h in sorted(style_hashes):
        if h not in csp.get("style-src", []):
            errors.append(f"inline <style> with hash {h} is not in style-src (run with --update-csp)")
    for directive, url in sorted(external):
        if not allowed(directive, csp, url):
            errors.append(f"{directive} does not allow {url}")
    for msg, where in sorted(problems.items()):
        errors.append(f"{msg}: {len(where)} page(s), e.g. {where[0]}")
    deployed_cfg = site / CONFIG.name
    if not deployed_cfg.exists():
        warnings.append(f"{CONFIG.name} is not in {site.name}/ yet (deploy.sh and the workflow copy it)")
    elif deployed_cfg.read_bytes() != CONFIG.read_bytes():
        warnings.append(f"{site.name}/{CONFIG.name} differs from the repo root copy (rebuild or re-copy)")

    print(f"{site}: {len(pages)} HTML pages, {len(files)} files, {total / 1048576:.1f} MB; "
          f"inline scripts {len(script_hashes)}, inline styles {len(style_hashes)}, "
          f"external URLs {len({u for _, u in external if urlparse(u).netloc})}")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print("OK: ready to upload" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
