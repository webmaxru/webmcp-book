#!/usr/bin/env python3
"""Manuscript lint: fails (exit 1) on anything that must not ship in the clean manuscript.

    python3 tools/lint_manuscript.py [--manuscript manuscript] [--json report.json]

Reads ONLY manuscript/ (Book.txt, Sample.txt, the files they list, resources/). Checks:
  * Book.txt / Sample.txt entries that do not exist, and .md files that Book.txt does not list
  * placeholders: TODO, TBD, FIXME, XXX, [insert, [[MAXIM, lorem, "coming soon", "to be published",
    "to be written" (outside code blocks and inline code)
  * raw HTML (tags or HTML comments outside code; <https://...> autolinks are fine)
  * Markua attribute lines ({class: ...}) outside part files ({sample: true|false} is allowed anywhere: it marks the Leanpub sample)
  * images that do not exist under resources/ (or manuscript/), figures that are not alone on their line
  * duplicate footnote ids in the whole book, footnote references without a definition and definitions
    never referenced
  * figure and listing numbering per chapter: gaps, duplicates, numbers from another chapter
  * broken internal anchors and links to files outside Book.txt
  * every file except part files has exactly one H1
"""
import argparse, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd  # noqa: E402

PLACEHOLDERS = [
    (r"\bTODO\b", "TODO"), (r"\bTBD\b", "TBD"), (r"\bFIXME\b", "FIXME"), (r"\bXXX+\b", "XXX"),
    (r"\[insert", "[insert"), (r"\[\[MAXIM", "[[MAXIM"), (r"\blorem\b", "lorem"),
    (r"coming soon", "coming soon"), (r"to be published", "to be published"), (r"to be written", "to be written"),
]
TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(\s[^<>]*)?/?>|<!--")
AUTOLINK_RE = re.compile(r"<(?:https?|mailto|ftp):[^>\s]+>|<[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+>")

def strip_inline_code(line):
    return re.sub(r"(`+)(.+?)\1", lambda m: " " * len(m.group(0)), line)

def prose_lines(md):
    """(line_no, text) for lines outside fenced code, with inline code blanked."""
    out, fence = [], None
    for i, line in enumerate(md.splitlines(), 1):
        m = re.match(r"^\s*(```+|~~~+)", line)
        if m:
            tok = m.group(1)[0] * 3
            if fence is None:
                fence = tok
            elif line.strip().startswith(fence):
                fence = None
            continue
        if fence is None:
            out.append((i, strip_inline_code(line)))
    return out

def lint(manuscript):
    d = pathlib.Path(manuscript)
    issues = []
    def add(f, line, kind, msg):
        issues.append({"file": f, "line": line, "kind": kind, "message": msg})
    if not (d / "Book.txt").exists():
        add("Book.txt", 0, "booktxt", "Book.txt is missing")
        return issues
    listed = bookmd.read_booktxt(d)
    for n in listed:
        if not (d / n).exists():
            add("Book.txt", 0, "booktxt", f"lists {n}, which does not exist")
    if (d / "Sample.txt").exists():
        for n in [l.strip() for l in (d / "Sample.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().endswith(":")]:
            if not (d / n).exists():
                add("Sample.txt", 0, "booktxt", f"lists {n}, which does not exist")
            elif n not in listed:
                add("Sample.txt", 0, "booktxt", f"lists {n}, which Book.txt does not list")
    for p in sorted(d.glob("*.md")):
        if p.name not in listed:
            add(p.name, 0, "booktxt", "not listed in Book.txt (it would not be published)")
    secs = [bookmd.Section(d / n) for n in listed if (d / n).exists()]

    fn_defs, fn_refs = {}, {}
    for s in secs:
        f = s.path.name
        raw = s.raw
        lines = prose_lines(raw)
        for no, text in lines:
            for pat, label in PLACEHOLDERS:
                if re.search(pat, text, re.I if label in ("lorem", "coming soon", "to be published", "to be written", "[insert") else 0):
                    add(f, no, "placeholder", f"placeholder '{label}': {text.strip()[:100]}")
            t2 = AUTOLINK_RE.sub("", text)
            m = TAG_RE.search(t2)
            if m:
                add(f, no, "raw-html", f"raw HTML {m.group(0)[:40]!r}: {text.strip()[:90]}")
            if bookmd.ATTR_LINE_RE.match(text.strip()) and s.kind != "part" and not re.match(r"^\{sample:\s*(true|false)\}$", text.strip()):
                add(f, no, "markua-attribute", f"Markua attribute line outside a part file: {text.strip()}")
            for img in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)", text):
                src = img.group(2)
                if not re.match(r"^[a-z]+:", src) and not bookmd.resolve_image(d, src):
                    add(f, no, "missing-image", f"image not found under resources/: {src}")
                if text.strip() != img.group(0) + ")" and not text.strip().startswith("!["):
                    add(f, no, "figure-inline", "a figure image must be alone on its line")
            for ref in re.finditer(r"\[\^([^\]\s]+)\](?!:)", text):
                fn_refs.setdefault(ref.group(1), []).append((f, no))
            dm = re.match(r"^\[\^([^\]\s]+)\]:", text)
            if dm:
                fid = dm.group(1)
                if fid in fn_defs:
                    add(f, no, "footnote-duplicate", f"footnote id [^{fid}] is also defined in {fn_defs[fid][0]}:{fn_defs[fid][1]}")
                else:
                    fn_defs[fid] = (f, no)
        # numbering of figures and listings
        if s.kind in ("chapter", "appendix"):
            body = "\n".join(t for _, t in lines)
            for kind, pat in (("Figure", r"^!\[Figure\s+([0-9A-Z]+)\.(\d+)"), ("Listing", r"^\*\*Listing\s+([0-9A-Z]+)\.(\d+)")):
                nums = [(a, int(b)) for a, b in re.findall(pat, body, re.M)]
                for a, b in nums:
                    if a != s.number:
                        add(f, 0, "numbering", f"{kind} {a}.{b} in {s.label}")
                seq = [b for a, b in nums if a == s.number]
                if seq and sorted(seq) != list(range(1, len(seq) + 1)):
                    add(f, 0, "numbering", f"{kind}s are numbered {seq}; expected 1..{len(seq)} without gaps or repeats")
                if seq and seq != sorted(seq):
                    add(f, 0, "numbering", f"{kind}s appear out of order: {seq}")
    for fid, where in fn_refs.items():
        if fid not in fn_defs:
            add(where[0][0], where[0][1], "footnote-missing", f"[^{fid}] has no definition")
    for fid, (f, no) in fn_defs.items():
        if fid not in fn_refs:
            add(f, no, "footnote-unused", f"[^{fid}] is defined but never referenced")
    for w in bookmd.check_refs(secs, d):
        f, _, msg = w.partition(": ")
        if "expected exactly one H1" in msg and any(s.path.name == f and s.kind == "part" for s in secs):
            continue
        add(f, 0, "reference", msg)
    return issues

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manuscript", default=str(bookmd.MANUSCRIPT))
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    issues = lint(a.manuscript)
    by_file = {}
    for i in issues:
        by_file.setdefault(i["file"], []).append(i)
    for f in sorted(by_file):
        print(f"{f}: {len(by_file[f])} issue(s)")
        for i in by_file[f]:
            loc = f":{i['line']}" if i["line"] else ""
            print(f"  {f}{loc} [{i['kind']}] {i['message']}")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(issues, indent=2, ensure_ascii=False))
    print(f"\n{len(issues)} issue(s) in {len(by_file)} file(s)" if issues else "manuscript lint: clean")
    sys.exit(1 if issues else 0)

if __name__ == "__main__":
    main()
