#!/usr/bin/env python3
"""Build the print PDF (7 x 9.25 in, for Leanpub and KDP) from the manuscript.

    python3 tools/build_pdf.py [--manuscript manuscript] [--out PATH] [--toc-depth 2] [--keep-html]

Pipeline (the same as the author's Book 2, "Reproducible AI Agent Environments"): Markdown
(tools/bookmd.py) -> one print HTML styled by theme/print/print.css with the fonts in theme/fonts
-> PDF with headless Chromium (Playwright). Chromium cannot number a table of contents, start
chapters on right-hand pages or vary running heads per chapter, so the script renders in passes:
it reads where every part, chapter and section landed from the PDF outline, inserts blank pages so
every part and chapter opens on a recto, writes the real page numbers into the contents, renders
again until nothing moves, stamps running heads and folios from an overlay, rebuilds the bookmarks
(Part > Chapter > Section > Subsection) and sets page labels (roman front matter, arabic from Part I).
Never commit the PDF.
"""
import argparse, html, json, os, pathlib, re, shutil, sys, tempfile, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd  # noqa: E402
from bookmd import ROOT, THEME, esc  # noqa: E402

PAGE_W_IN, PAGE_H_IN = 7.0, 9.25
INNER_IN, OUTER_IN = 0.875, 0.75
PRINT_CSS = THEME / "print" / "print.css"

def roman(n):
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
            (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s; n -= v
    return out

def norm(s):
    return re.sub(r"[^a-z0-9]", "", html.unescape(re.sub("<[^>]+>", "", s)).lower())

def default_out(cfg):
    return ROOT / "dist" / f'{cfg["file_stem"]}-v{bookmd.book_version(cfg)}.pdf'

# ---------------------------------------------------------------- document model
class Block:
    def __init__(self, kind, recto, title="", section=None):
        self.kind, self.recto, self.title, self.section = kind, recto, title, section
        self.h1_text = title
        self.start = self.length = self.dest = None
        self.children = []

def make_blocks(sections):
    blocks = [Block("title", True, "Title page"), Block("copyright", False, "Copyright"), Block("toc", True, "Contents")]
    for s in sections:
        if s.kind == "part":
            b = Block("part", True, f"{s.label}. {s.title}", section=s)
            b.h1_text = s.label + s.title
        else:
            b = Block("section", True, s.running_title, section=s)
            b.h1_text = s.title
        blocks.append(b)
    return blocks

# ---------------------------------------------------------------- HTML
def link_mapper(sections):
    slugs = {s.slug for s in sections}
    def make(cur_slug):
        def m(href):
            sp = bookmd.split_internal_link(href)
            if sp is None:
                return None
            path, frag = sp
            target = path or cur_slug
            if target not in slugs:
                return None
            return f"#{target}--{frag}" if frag else f"#sec-{target}"
        return m
    return make

def short_urls(body):
    return re.sub(r'data-url="https?://([^"]+)"', r'data-url="\1"', body)

def inline_code(body):
    """Under justified text, spaces inside short inline code would stretch, and long tokens leave gaps:
    short code gets no-break spaces; every span gets break opportunities after / . _ - = : ,"""
    def f(m):
        raw = html.unescape(m.group(1))
        short = len(raw) <= 24
        out = []
        for i, ch in enumerate(raw):
            if short and ch == " ":
                out.append("&nbsp;")
            elif ch == "-":
                out.append("&#8209;")
            else:
                out.append(esc(ch))
            if (ch in "/._-=:,(" and i >= 2 and len(raw) - i > 3 and raw[i + 1] not in "/._-=:, "
                    and raw[i - 1] not in "/._-=:, "):
                out.append("<wbr>")
        return "<code>" + "".join(out) + "</code>"
    return re.sub(r"<code>(.*?)</code>", f, body, flags=re.S)

def section_html(s, mapper, manuscript_dir):
    def image_url(src):
        p = bookmd.resolve_image(manuscript_dir, src)
        return p.resolve().as_uri() if p else src
    body = bookmd.render(s, id_prefix=f"{s.slug}--", link_map=mapper(s.slug), image_url=image_url)
    body = inline_code(short_urls(body))
    label = f'<div class="o-label">{esc(s.label)}</div>' if s.label else ""
    return (f'<div class="opener">{label}<h1 id="sec-{s.slug}">{esc(s.title)}</h1><div class="o-rule"></div></div>'
            f'<div class="chapter-body">{body}</div>')

def toc_html(blocks, numbers, depth):
    rows = []
    def entry(cls, text, key, inner=""):
        n = numbers.get(key, "000")
        return (f'<li class="{cls}"><div class="e"><span class="t">{text}</span><span class="d"></span>'
                f'<span class="n">{n}</span></div>{inner}</li>')
    for b in blocks:
        if b.kind == "part":
            rows.append(entry("part", esc(f"{b.section.label} · {b.section.title}"), b.title))
        elif b.kind == "section":
            s = b.section
            subs = ""
            if depth >= 2 and s.kind in ("chapter", "appendix"):
                hs = [h for h in bookmd.headings(s) if h[0] == 2]
                subs = "<ol>" + "".join(entry("sec", esc(t), f"{s.slug}#{slug}") for _, t, slug in hs) + "</ol>"
            rows.append(entry("chap", esc(s.running_title), s.slug, subs))
    return f'<div class="toc"><h1 id="contents">Contents</h1><ol>{"".join(rows)}</ol></div>'

def linkify_plain(text):
    return re.sub(r"(https?://[^\s<]+)", r'<a class="bare" href="\1">\1</a>', esc(text))

def book_html(cfg, blocks, sections, manuscript_dir, fillers, numbers, depth):
    mapper = link_mapper(sections)
    out = [f'<!doctype html><html lang="{cfg.get("language", "en")}"><head><meta charset="utf-8"><title>{esc(cfg["title"])}</title>'
           f'<link rel="stylesheet" href="{PRINT_CSS.resolve().as_uri()}"></head><body>']
    for i, b in enumerate(blocks):
        if i in fillers:
            out.append('<div class="blank"></div>')
        if b.kind == "title":
            out.append(f'<section class="block fullpage titlepage"><div class="t-eyebrow">A book about WebMCP</div>'
                       f'<div class="t-title">{esc(cfg["title"])}</div>'
                       f'<div class="t-sub">{esc(cfg["subtitle"])}</div><div class="t-rule"></div>'
                       f'<div class="t-author">{esc(cfg["author"])}</div><div class="t-spacer"></div>'
                       f'<div class="t-tested">{esc(bookmd.tested_with(cfg))}</div></section>')
        elif b.kind == "copyright":
            ps = "".join(f"<p>{linkify_plain(l)}</p>" for l in bookmd.copyright_lines(cfg))
            ed = f'<p class="c-version">{esc(bookmd.edition_line(cfg))}</p>'
            site = cfg.get("site_url", "")
            web = f"<p>Read the web edition at {linkify_plain(site)}</p>" if site else ""
            out.append(f'<section class="block fullpage copyright"><p class="c-title">{esc(cfg["title"])}: '
                       f'{esc(cfg["subtitle"])}</p>{ps}{web}{ed}</section>')
        elif b.kind == "toc":
            out.append(f'<section class="block">{toc_html(blocks, numbers, depth)}</section>')
        elif b.kind == "part":
            s = b.section
            intro = bookmd.render(s, id_prefix=f"{s.slug}--").strip()
            intro_html = f'<div class="p-intro">{intro}</div>' if intro else ""
            lis = "".join(f'<li><span class="pl">{esc(c.label)}</span><span>{esc(c.title)}</span></li>' for c in s.children)
            out.append(f'<section class="block fullpage partpage"><h1 id="sec-{s.slug}"><span class="p-label">{esc(s.label)}</span>'
                       f'{esc(s.title)}</h1><div class="p-rule"></div>{intro_html}<ol>{lis}</ol></section>')
        else:
            out.append(f'<section class="block chapter" id="blk-{b.section.slug}">'
                       f'{section_html(b.section, mapper, manuscript_dir)}</section>')
    out.append("</body></html>")
    return "".join(out)

# ---------------------------------------------------------------- rendering
def render_pdf(browser, html_text, path, workdir, attempts=3):
    """Print one HTML file to PDF. Chromium sometimes fails a large print when memory is short
    ("Printing failed", "Target crashed"); that is retried on a fresh page, up to `attempts` times."""
    hp = pathlib.Path(workdir) / (pathlib.Path(path).stem + ".html")
    hp.write_text(html_text, encoding="utf-8")
    for attempt in range(1, attempts + 1):
        page = browser.new_page()
        page.set_default_timeout(900_000)
        try:
            page.goto(hp.as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready.then(() => true)")
            page.pdf(path=str(path), prefer_css_page_size=True, outline=True, tagged=True, print_background=True)
            return hp
        except Exception as e:  # playwright.Error
            msg = str(e)
            if attempt == attempts or not any(k in msg for k in ("Printing failed", "Target crashed", "Target closed")):
                raise
            print(f"  print attempt {attempt} failed ({msg.splitlines()[0][:80]}); retrying", flush=True)
            time.sleep(5)
        finally:
            try:
                page.close()
            except Exception:
                pass
    return hp

def read_outline(path):
    from pypdf import PdfReader
    r = PdfReader(str(path))
    def walk(items):
        out, last = [], None
        for it in items:
            if isinstance(it, list):
                if last is not None:
                    last[3].extend(walk(it))
                continue
            try:
                pg = r.get_destination_page_number(it)
            except Exception:
                pg = None
            top = float(it.get("/Top", 0) or 0)
            last = [str(it.title), pg, top, []]
            out.append(last)
        return out
    return walk(r.outline), len(r.pages)

def flatten(items):
    out = []
    for it in items:
        out.append(it)
        out.extend(flatten(it[3]))
    return out

def analyze(blocks, pdf_path, fillers_used):
    items, npages = read_outline(pdf_path)
    flat = flatten(items)
    blocks[0].start, blocks[1].start = 0, 1
    j = 0
    for b in blocks[2:]:
        want = norm(b.h1_text) if b.kind != "toc" else "contents"
        k = j
        while k < len(flat) and norm(flat[k][0]) != want:
            k += 1
        if k == len(flat):
            raise SystemExit(f"build_pdf: could not find the heading of '{b.title}' in the PDF outline")
        it = flat[k]; j = k + 1
        b.start, b.dest, b.children = it[1], (it[1], it[2]), it[3]
    for i, b in enumerate(blocks):
        nxt = blocks[i + 1].start - (1 if (i + 1) in fillers_used else 0) if i + 1 < len(blocks) else npages
        b.length = nxt - b.start
    return npages

def plan(blocks):
    fillers, pos, starts = set(), 0, []
    for i, b in enumerate(blocks):
        if b.recto and pos % 2 == 1:
            fillers.add(i); pos += 1
        starts.append(pos); pos += b.length
    return fillers, starts, pos

def labels_for(blocks, starts, total):
    main = next((starts[i] for i, b in enumerate(blocks) if b.kind in ("section", "part")), total)
    def lab(p):
        return roman(p + 1) if p < main else str(p - main + 1)
    return lab, main

def toc_numbers(blocks, starts, lab):
    nums = {}
    for i, b in enumerate(blocks):
        if b.kind == "part":
            nums[b.title] = lab(starts[i])
        elif b.kind == "section":
            s = b.section
            nums[s.slug] = lab(starts[i])
            shift = starts[i] - b.start
            h2 = [h for h in bookmd.headings(s) if h[0] == 2]
            for (lvl, t, slug), ch in zip(h2, b.children):
                if ch[1] is not None:
                    nums[f"{s.slug}#{slug}"] = lab(ch[1] + shift)
    return nums

# ---------------------------------------------------------------- stamping
def overlay_html(pages):
    st = f"""
    @page {{ size: {PAGE_W_IN}in {PAGE_H_IN}in; margin: 0; }}
    html, body {{ margin: 0; background: transparent; }}
    .pg {{ position: relative; width: {PAGE_W_IN}in; height: {PAGE_H_IN}in; break-after: page; overflow: hidden; }}
    .pg:last-child {{ break-after: auto; }}
    .verso .hd {{ left: {OUTER_IN}in; }}
    .recto .hd {{ right: {OUTER_IN}in; }}
    """
    divs = []
    for p in pages:
        inner = ""
        if p.get("head") is not None and p.get("folio"):
            f, h = f'<span class="f">{esc(p["folio"])}</span>', f'<span class="h">{esc(p["head"])}</span>'
            inner = f'<div class="hd">{f}{h}</div>' if p["side"] == "verso" else f'<div class="hd">{h}{f}</div>'
        elif p.get("folio"):
            inner = f'<div class="ft">{esc(p["folio"])}</div>'
        divs.append(f'<div class="pg {p["side"]}">{inner}</div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{PRINT_CSS.resolve().as_uri()}">'
            f'<style>{st}</style></head><body class="overlay">{"".join(divs)}</body></html>')

def page_plan(cfg, blocks, fillers, npages, lab):
    info = [None] * npages
    for i, b in enumerate(blocks):
        end = blocks[i + 1].start - (1 if (i + 1) in fillers else 0) if i + 1 < len(blocks) else npages
        for p in range(b.start, end):
            side = "recto" if p % 2 == 0 else "verso"
            d = {"side": side, "folio": lab(p), "head": None}
            if b.kind in ("title", "copyright", "part"):
                d["folio"] = None
            elif p == b.start:
                pass  # opener: folio at the foot, no running head
            elif b.kind == "toc":
                d["head"] = "Contents"
            else:
                d["head"] = cfg["title"] if side == "verso" else b.section.running_title
            info[p] = d
        if i + 1 < len(blocks) and (i + 1) in fillers:
            p = blocks[i + 1].start - 1
            info[p] = {"side": "recto" if p % 2 == 0 else "verso", "folio": None, "head": None}
    for p in range(npages):
        if info[p] is None:
            info[p] = {"side": "recto" if p % 2 == 0 else "verso", "folio": None, "head": None}
    return info

def finalize(cfg, blocks, body_pdf, overlay_pdf, out_path, main_start, npages):
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import Fit
    rb, ro = PdfReader(str(body_pdf)), PdfReader(str(overlay_pdf))
    if len(ro.pages) != len(rb.pages):
        raise SystemExit(f"build_pdf: overlay has {len(ro.pages)} pages, body {len(rb.pages)}")
    w = PdfWriter()
    w.append(rb, import_outline=False)
    for i, pg in enumerate(w.pages):
        pg.merge_page(ro.pages[i])
        pg.compress_content_streams()
    def add(title, page, top, parent=None):
        return w.add_outline_item(title, page, parent=parent, fit=Fit.xyz(left=0, top=top, zoom=None))
    part_item = None
    for b in blocks:
        if b.kind == "toc":
            add("Contents", b.dest[0], b.dest[1])
        elif b.kind == "part":
            part_item = add(f"{b.section.label}: {b.section.title}", b.dest[0], b.dest[1])
        elif b.kind == "section":
            parent = part_item if b.section.kind == "chapter" else None
            if b.section.kind != "chapter":
                part_item = None
            it = add(b.section.running_title, b.dest[0], b.dest[1], parent)
            hs = bookmd.headings(b.section)
            h2 = [t for lvl, t, _ in hs if lvl == 2]
            h3 = [[]]
            for lvl, t, _ in hs:
                if lvl == 2:
                    h3.append([])
                elif lvl == 3:
                    h3[-1].append(t)
            h3 = h3[1:]
            same = len(h2) == len(b.children)
            for k, (t, pg, top, kids) in enumerate(b.children):
                if pg is None:
                    continue
                c = add(h2[k] if same else t, pg, top, it)
                same3 = same and len(h3[k]) == len(kids)
                for k2, (t2, pg2, top2, _) in enumerate(kids):
                    if pg2 is not None:
                        add(h3[k][k2] if same3 else t2, pg2, top2, c)
    if main_start > 0:
        w.set_page_label(0, main_start - 1, style="/r", start=1)
    if main_start < npages:
        w.set_page_label(main_start, npages - 1, style="/D", start=1)
    v = bookmd.book_version(cfg)
    w.add_metadata({"/Title": f'{cfg["title"]}: {cfg["subtitle"]}', "/Author": cfg["author"],
                    "/Subject": bookmd.tested_with(cfg) or cfg.get("description", ""),
                    "/Creator": "tools/build_pdf.py (Chromium + pypdf)", **({"/Version": v} if v else {})})
    w.page_mode = "/UseOutlines"
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        w.write(f)

# ---------------------------------------------------------------- main
def find_chrome(arg):
    return arg or os.environ.get("CHROME_PATH") or None

def build(manuscript, out, toc_depth=2, chrome=None, keep_html=False, report_json=None, max_passes=6):
    t0 = time.time()
    cfg = bookmd.load_config()
    sections = bookmd.load_book(manuscript)
    for w_ in bookmd.check_refs(sections, manuscript) + bookmd.config_warnings(cfg):
        print("warning:", w_, flush=True)
    blocks = make_blocks(sections)
    out = pathlib.Path(out or default_out(cfg)).resolve()
    work = pathlib.Path(tempfile.mkdtemp(prefix="tnc-pdf-"))
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as pw:
            exe = find_chrome(chrome)
            browser = pw.chromium.launch(**({"executable_path": exe} if exe else {}))
            fillers, numbers, passes = set(), {}, 0
            while True:
                passes += 1
                body = work / f"body{passes}.pdf"
                hp = render_pdf(browser, book_html(cfg, blocks, sections, manuscript, fillers, numbers, toc_depth), body, work)
                npages = analyze(blocks, body, fillers)
                new_fillers, starts, total = plan(blocks)
                lab, main_start = labels_for(blocks, starts, total)
                new_numbers = toc_numbers(blocks, starts, lab)
                stable = new_fillers == fillers and new_numbers == numbers and all(b.start == s for b, s in zip(blocks, starts))
                print(f"pass {passes}: {npages} pages, {len(new_fillers)} blank pages planned, stable={stable}", flush=True)
                if stable:
                    break
                if passes >= max_passes:
                    print("warning: the layout did not settle; using the last pass", flush=True)
                    break
                fillers, numbers = new_fillers, new_numbers
            lab, main_start = labels_for(blocks, [b.start for b in blocks], npages)
            pages = page_plan(cfg, blocks, fillers, npages, lab)
            ov = work / "overlay.pdf"
            hp2 = work / "overlay.html"
            hp2.write_text(overlay_html(pages), encoding="utf-8")
            page = browser.new_page(); page.set_default_timeout(600_000)
            page.goto(hp2.as_uri(), wait_until="load"); page.evaluate("document.fonts.ready.then(() => true)")
            page.pdf(path=str(ov), prefer_css_page_size=True, print_background=False)
            page.close(); browser.close()
        finalize(cfg, blocks, body, ov, out, main_start, npages)
        if keep_html:
            shutil.copy(hp, out.with_suffix(".html"))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    rows, tw = [], 0
    for i, b in enumerate(blocks):
        if b.kind != "section":
            continue
        s = b.section
        end = blocks[i + 1].start - (1 if (i + 1) in fillers else 0) if i + 1 < len(blocks) else npages
        n = end - b.start
        rows.append({"file": s.path.name, "title": s.running_title, "words": s.words,
                     "code_words_pct": round(100 * s.code_words / max(s.words, 1)), "pages": n,
                     "first_page": lab(b.start), "words_per_page": round(s.words / max(n, 1))})
        tw += s.words
    size = out.stat().st_size
    content_pages = sum(r["pages"] for r in rows)
    print()
    print(f"{'file':<46}{'words':>7}{'code%':>6}{'pages':>6}{'w/p':>6}  first")
    for r in rows:
        print(f"{r['file']:<46}{r['words']:>7}{r['code_words_pct']:>6}{r['pages']:>6}{r['words_per_page']:>6}  {r['first_page']}")
    print(f"{'TOTAL':<46}{tw:>7}{'':>6}{content_pages:>6}{round(tw / max(content_pages, 1)):>6}")
    print()
    print(f"PDF: {out}")
    print(f"pages: {npages} (front matter {main_start}, blank pages {len(fillers)}, part pages "
          f"{sum(1 for b in blocks if b.kind == 'part')}, text pages {content_pages})")
    print(f"size: {size / 1048576:.2f} MB ({size} bytes)")
    print(f"passes: {passes}; time: {time.time() - t0:.0f} s", flush=True)
    if report_json:
        pathlib.Path(report_json).write_text(json.dumps({"pdf": str(out), "pages": npages, "bytes": size,
                                                         "front_matter_pages": main_start, "blank_pages": len(fillers),
                                                         "chapters": rows, "total_words": tw}, indent=2))
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manuscript", default=str(bookmd.MANUSCRIPT))
    ap.add_argument("--out", default=None, help="default: dist/<file_stem>-v<version>.pdf")
    ap.add_argument("--toc-depth", type=int, default=2, choices=(1, 2))
    ap.add_argument("--chrome", default=None, help="Chromium/Chrome binary (default: $CHROME_PATH or Playwright's own)")
    ap.add_argument("--keep-html", action="store_true")
    ap.add_argument("--json", default=None, help="also write the report as JSON")
    a = ap.parse_args(argv)
    build(pathlib.Path(a.manuscript), a.out, a.toc_depth, a.chrome, a.keep_html, a.json)

if __name__ == "__main__":
    main()
