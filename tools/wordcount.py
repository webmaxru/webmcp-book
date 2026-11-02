#!/usr/bin/env python3
"""Word counts for the manuscript, as a Markdown table for README.md.

    python3 tools/wordcount.py            # print the table
    python3 tools/wordcount.py --update   # rewrite the table between the markers in README.md

Counts are `wc -w` on each file in Book.txt order (code included), plus the code share.
README.md markers: <!-- wordcount:start --> and <!-- wordcount:end -->.
"""
import argparse, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd  # noqa: E402

def table(manuscript=bookmd.MANUSCRIPT):
    secs = bookmd.load_book(manuscript)
    rows = ["| File | Title | Words | Code |", "| --- | --- | ---: | ---: |"]
    total = code = 0
    for s in secs:
        title = f"{s.label}: {s.title}" if s.label else s.title
        if s.kind == "part":
            title = f"**{title}**"
        pct = f"{round(100 * s.code_words / s.words)} %" if s.words and s.kind != "part" else ""
        rows.append(f"| [`{s.path.name}`](manuscript/{s.path.name}) | {title} | {s.words:,} | {pct} |")
        total += s.words; code += s.code_words
    rows.append(f"| | **Total** | **{total:,}** | {round(100 * code / max(total, 1))} % |")
    return "\n".join(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--update", action="store_true")
    a = ap.parse_args()
    t = table()
    if not a.update:
        print(t); return
    readme = bookmd.ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    new, n = re.subn(r"(<!-- wordcount:start -->).*?(<!-- wordcount:end -->)", lambda m: m.group(1) + "\n" + t + "\n" + m.group(2), text, flags=re.S)
    if not n:
        sys.exit("README.md has no <!-- wordcount:start --> / <!-- wordcount:end --> markers")
    readme.write_text(new, encoding="utf-8")
    print("README.md word count table updated")

if __name__ == "__main__":
    main()
