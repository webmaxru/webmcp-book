#!/usr/bin/env python3
"""Build the web edition (a static site) from the manuscript.

    python3 tools/build_site.py [--manuscript manuscript] [--out dist/site]

Reads manuscript/ (Book.txt order), tools/book.json, CHANGELOG.md (the release history page)
and theme/site/ (CSS, JS, templates, fonts, icons). Writes one page per part, chapter and
appendix, an about page, the release history, index.html, 404.html, sitemap.xml, robots.txt
and search-index.json. Pages are flat <slug>.html files with relative links, so the same
output works on Azure Static Web Apps, on any static host and opened from a zip.
If book/staticwebapp.config.json exists it is copied into the output.
"""
import argparse, datetime, html, json, pathlib, re, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd
from bookmd import esc, ROOT, THEME

SITE_THEME = THEME / "site"

def tpl(name):
    return (SITE_THEME / "templates" / name).read_text(encoding="utf-8")

def fill(template, **kw):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(kw.get(m.group(1), "")), template)

def page_name(s):
    return "about.html" if s.kind == "about" else f"{s.slug}.html"

def strip_tags(h):
    return html.unescape(re.sub(r"<[^>]+>", " ", h))

def short_label(s):
    if s.kind == "chapter":
        return f"Ch {s.number}"
    if s.kind == "appendix":
        return f"App {s.number}"
    return ""

# ------------------------------------------------------------------ navigation
def nav_html(secs, current, root=""):
    out, cur_idx = [], (secs.index(current) if current in secs else -1)
    open_list = False
    def close():
        nonlocal open_list
        if open_list:
            out.append("</ol>")
            open_list = False
    group = None
    for i, s in enumerate(secs):
        if s.kind == "part":
            close()
            out.append(f'<p class="nav-part"><a href="{root}{page_name(s)}">{esc(s.label)} · {esc(s.title)}</a></p>')
            group = "part"
            continue
        g = "appendix" if s.kind == "appendix" else "back" if s.kind in ("about", "other") else "chapter"
        if g != "chapter" and group != g:
            close()
            out.append(f'<p class="nav-part">{"Appendices" if g == "appendix" else "Back matter"}</p>')
            group = g
        if not open_list:
            out.append('<ol class="spine">')
            open_list = True
        state = "current" if s is current else "resolved" if (cur_idx >= 0 and i < cur_idx) else "pending"
        pin = f'<span class="pin-tag">{esc(short_label(s))}</span>' if short_label(s) else ""
        cls = ' class="is-current" aria-current="page"' if s is current else ""
        li = f'<li data-state="{state}"><a href="{root}{page_name(s)}"{cls}>{pin}<span class="chapter-name">{esc(s.title)}</span></a>'
        if s is current:
            h2 = [h for h in bookmd.headings(s) if h[0] == 2]
            if h2:
                li += '<ol class="sections">' + "".join(f'<li><a href="#{slug}">{esc(t)}</a></li>' for _, t, slug in h2) + "</ol>"
        out.append(li + "</li>")
    close()
    return "\n".join(out)

def common(cfg, root, title, desc, canonical, kind="chapter", og_type="article"):
    return dict(lang=cfg.get("language", "en"), page_title=esc(title), description=esc(desc), author=esc(cfg["author"]),
                canonical=esc(canonical), og_type=og_type, book_title=esc(cfg["title"]), book_subtitle=esc(cfg["subtitle"]),
                root=root, version=esc(bookmd.book_version(cfg)), newsletter_url=esc(cfg["newsletter_url"]),
                contact_url=esc(cfg["contact_url"]), kind=kind)

def footer_html(cfg, root=""):
    lines = bookmd.copyright_lines(cfg)
    first = esc(lines[0]) if lines else ""
    meta = [esc(bookmd.edition_line(cfg))]
    tw = bookmd.tested_with(cfg)
    if tw:
        meta.append(esc(tw))
    return (f'<p>{first} Free to read online; the text may not be republished without permission.</p>'
            f'<p class="meta">{" · ".join(meta)} · <a href="{root}releases.html">Release history</a></p>'
            f'<p><a href="{esc(cfg["newsletter_url"])}" rel="noopener">Get the PDF</a> · '
            f'<a href="{esc(cfg["contact_url"])}" rel="noopener">For publishers: contact {esc(cfg["author"])}</a> · '
            f'<a href="{esc(cfg["demo_url"])}" rel="noopener">Demo code (MIT)</a></p>')

def reading_cta(cfg):
    return (f'<aside class="reading-cta" aria-label="The book in other formats"><strong>Reading offline?</strong> '
            f'<a href="{esc(cfg["newsletter_url"])}" rel="noopener">Get the PDF</a>'
            f'<span>·</span><a href="{esc(cfg["contact_url"])}" rel="noopener">For publishers: contact {esc(cfg["author"])}</a></aside>')

def pager(secs, s):
    reading = [x for x in secs]
    i = reading.index(s)
    prev_ = reading[i - 1] if i > 0 else None
    next_ = reading[i + 1] if i + 1 < len(reading) else None
    def a(x, cls, d):
        lab = f"{x.label}: " if x.label and x.kind != "part" else (f"{x.label} · " if x.kind == "part" else "")
        return f'<a class="{cls}" href="{page_name(x)}" rel="{ "prev" if cls == "prev" else "next"}"><span class="dir">{d}</span><span class="ttl">{esc(lab + x.title)}</span></a>'
    inner = (a(prev_, "prev", "Previous") if prev_ else "") + (a(next_, "next", "Next") if next_ else "")
    return f'<nav class="pager" aria-label="Previous and next">{inner}</nav>'

def header_html(s, cfg):
    crumbs = ['<a href="index.html">Contents</a>']
    if s.part is not None:
        crumbs.append(f'<span>/</span><a href="{page_name(s.part)}">{esc(s.part.label)}</a>')
    elif s.kind == "appendix":
        crumbs.append('<span>/</span><span>Appendices</span>')
    label = f'<span class="label eyebrow">{esc(s.label)}</span>' if s.label else ""
    return (f'<header class="chapter-header"><div class="chapter-header-inner"><nav class="breadcrumb" aria-label="Breadcrumb">{"".join(crumbs)}</nav>'
            f'{label}<h1>{esc(s.title)}</h1></div></header>')

def add_heading_anchors(body):
    return re.sub(r'<h([234]) id="([^"]+)">(.*?)</h\1>', lambda m: f'<h{m.group(1)} id="{m.group(2)}"><a class="heading-anchor" href="#{m.group(2)}">{m.group(3)}</a></h{m.group(1)}>', body, flags=re.S)

# ------------------------------------------------------------------ pages
def link_mapper(secs):
    names = {s.slug: page_name(s) for s in secs}
    def lm(href):
        sp = bookmd.split_internal_link(href)
        if sp is None:
            return None
        path, frag = sp
        if not path:
            return None
        target = names.get(path)
        if not target:
            return None
        return target + (f"#{frag}" if frag else "")
    return lm

def chapter_desc(s, body):
    text = strip_tags(re.sub(r'<blockquote class="epigraph">.*?</blockquote>', "", body, flags=re.S))
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:180].rsplit(" ", 1)[0] + "…") if len(text) > 180 else text

def build(manuscript, out):
    t0 = datetime.datetime.now()
    cfg = bookmd.load_config()
    secs = bookmd.load_book(manuscript)
    warnings = bookmd.check_refs(secs, manuscript) + bookmd.config_warnings(cfg)
    for w in warnings:
        print("warning:", w, flush=True)
    out = pathlib.Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "assets" / "fonts").mkdir(parents=True)
    (out / "images").mkdir()
    for f in ("style.css", "app.js", "theme-toggle.js"):
        shutil.copy(SITE_THEME / f, out / "assets" / f)
    for f in (SITE_THEME / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "assets" / "fonts" / f.name)
    for f in (THEME / "fonts").glob("OFL-*.txt"):
        shutil.copy(f, out / "assets" / "fonts" / f.name)
    for f in ("favicon.svg", "apple-touch-icon.png"):
        if (SITE_THEME / f).exists():
            shutil.copy(SITE_THEME / f, out / f)
    site = cfg["site_url"].rstrip("/") + "/"
    lm = link_mapper(secs)
    used_images = set()
    def image_url(src):
        p = bookmd.resolve_image(manuscript, src)
        if p:
            used_images.add(p)
            return "images/" + p.name
        return src
    search = []
    page_t = tpl("page.html")
    pages_written = []
    for s in secs:
        name = page_name(s)
        if s.kind == "part":
            items = "".join(f'<li><span class="pin-tag">{esc(c.label)}</span><a href="{page_name(c)}">{esc(c.title)}</a></li>' for c in s.children)
            intro = bookmd.render(s, link_map=lm, image_url=image_url)
            body = (f'<p class="spine-part">{esc(s.label)}</p><h1>{esc(s.title)}</h1>{intro}'
                    f'<ol class="part-chapters">{items}</ol>')
            html_ = fill(page_t, **common(cfg, "", f"{s.label}: {s.title} | {cfg['title']}", f"{s.label} of {cfg['title']}: {s.title}.", site + name, "part"),
                         nav=nav_html(secs, s), header="", body=f'<div class="part-hero">{body}</div>', after=pager(secs, s), footer=footer_html(cfg))
            html_ = html_.replace('<main id="content" class="chapter-main">', '<main id="content">').replace('<article class="prose">', '<article>')
        else:
            body = bookmd.render(s, link_map=lm, image_url=image_url)
            body = add_heading_anchors(body)
            title = f"{s.label}: {s.title}" if s.label else s.title
            html_ = fill(page_t, **common(cfg, "", f"{title} | {cfg['title']}", chapter_desc(s, body), site + name, s.kind),
                         nav=nav_html(secs, s), header=header_html(s, cfg), body=body,
                         after=reading_cta(cfg) + pager(secs, s), footer=footer_html(cfg))
            # search entries: one per H2 section (plus the opening text)
            chunks = re.split(r'(?=<h2 id=")', body)
            for ch in chunks:
                m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', ch, re.S)
                text = re.sub(r"\s+", " ", strip_tags(re.sub(r'<section class="footnotes".*', "", ch, flags=re.S))).strip()
                if not text:
                    continue
                search.append({"u": name + (f"#{m.group(1)}" if m else ""), "c": s.label or s.title,
                               "t": strip_tags(m.group(2)).strip() if m else s.title, "x": text[:4000]})
        (out / name).write_text(html_, encoding="utf-8")
        pages_written.append(name)
    for p in used_images:
        shutil.copy(p, out / "images" / p.name)

    write_index(cfg, secs, out, site)
    write_releases(cfg, secs, out, site)
    write_404(cfg, out, site)
    (out / "search-index.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    today = datetime.date.today().isoformat()
    urls = ["", "releases.html"] + [p for p in pages_written]
    (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{esc(site + u)}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site}sitemap.xml\n", encoding="utf-8")
    swa = ROOT / "staticwebapp.config.json"
    if swa.exists():
        shutil.copy(swa, out / "staticwebapp.config.json")
    n = sum(1 for _ in out.rglob("*") if _.is_file())
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"site: {out} ({len(pages_written) + 3} pages, {len(used_images)} images, {n} files, {size / 1048576:.1f} MB) "
          f"in {(datetime.datetime.now() - t0).total_seconds():.1f} s", flush=True)
    return out

def hero_listing(secs, cfg):
    """The first listing of the book's first API chapter, shown on the cover as an artifact (content-driven)."""
    want = cfg.get("hero_listing", "4.1")
    for s in secs:
        body = bookmd.render(s)
        m = re.search(rf'<figure class="listing" id="listing-{re.escape(want.replace(".", "-"))}">(.*?)</figure>', body, re.S)
        if m:
            cap = re.search(r"<figcaption>(.*?)</figcaption>", m.group(1), re.S)
            pre = re.search(r"(<pre.*?</pre>)", m.group(1), re.S).group(1)
            lines = re.findall(r'<span class="ln">.*?</span>(?=<span class="ln">|</code>)', pre, re.S)
            if len(lines) > 24:  # the cover shows the head of the listing, the chapter has all of it
                pre = re.sub(r'(<code[^>]*>).*?(</code>)', lambda mm: mm.group(1) + "".join(lines[:24]) + mm.group(2), pre, flags=re.S)
            label = strip_tags(cap.group(1)).strip() if cap else ""
            lab = re.match(r"(Listing\s+\S+)", label)
            label = lab.group(1) + " · from the book" if lab else label
            return (f'<figure class="tool-artifact" aria-label="{esc(label)}"><div class="ta-bar"><i></i><i></i><i></i>'
                    f'<span>{esc(label)}</span></div>{pre}</figure>')
    return ""

def write_index(cfg, secs, out, site):
    parts = [s for s in secs if s.kind == "part"]
    first = next((s for s in secs if s.kind == "chapter"), secs[0])
    pins = [f'<span class="pin-tag">v{esc(bookmd.book_version(cfg))}</span>', f'<span class="pin-tag">{esc(cfg.get("edition", ""))}</span>']
    tw = bookmd.tested_with(cfg)
    if tw:
        pins.append(f'<span class="pin-tag">{esc(tw)}</span>')
    artifact = hero_listing(secs, cfg)
    hero = (f'<section class="hero"><div class="container hero-grid"><div>'
            f'<p class="eyebrow">A book about WebMCP</p><h1>{esc(cfg["title"])}</h1>'
            f'<p class="subtitle">{esc(cfg["subtitle"])}</p><p class="byline">{esc(cfg["author"])}</p>'
            f'<div class="pins">{"".join(pins)}</div><p class="lead">{esc(cfg["tagline"])}</p>'
            f'<div class="actions"><a class="btn btn-primary" href="{page_name(first)}">Start reading</a>'
            f'<a class="btn btn-secondary" href="{esc(cfg["newsletter_url"])}" rel="noopener">Get the PDF</a>'
            f'<a class="btn btn-quiet" href="#contents">Contents ↓</a></div></div>'
            f'<div>{artifact}</div></div></section>')
    spine = "".join(f'<li class="spine-node"><a class="spine-link" href="#{p.slug}"><span class="spine-dot" aria-hidden="true"></span>'
                    f'<span class="spine-part">{esc(p.label)}</span><span class="spine-title">{esc(p.title)}</span></a></li>' for p in parts)
    blocks = []
    def entry(s):
        h2 = [t for lvl, t, _ in bookmd.headings(s) if lvl == 2 and t.lower() not in ("notes",)]
        secs_txt = esc(" · ".join(h2[:6]) + (" · …" if len(h2) > 6 else "")) if h2 else ""
        num = esc(s.number) if s.number else ""
        return (f'<li><span class="num">{num}</span><div><a href="{page_name(s)}">{esc(s.title)}</a>'
                + (f'<span class="secs">{secs_txt}</span>' if secs_txt else "") + "</div></li>")
    for p in parts:
        blocks.append(f'<div class="contents-part" id="{p.slug}"><div class="contents-part-head"><span class="spine-part">{esc(p.label)}</span>'
                      f'<h3><a href="{page_name(p)}">{esc(p.title)}</a></h3></div><ol class="contents-list">'
                      + "".join(entry(c) for c in p.children) + "</ol></div>")
    apps = [s for s in secs if s.kind == "appendix"]
    if apps:
        blocks.append('<div class="contents-part" id="appendices"><div class="contents-part-head"><span class="spine-part">Appendices</span>'
                      '<h3>Reference</h3></div><ol class="contents-list">' + "".join(entry(a) for a in apps) + "</ol></div>")
    others = [s for s in secs if s.kind in ("about", "other")]
    loose = [s for s in secs if s.kind == "chapter" and s.part is None]
    if loose:
        blocks.insert(0, '<div class="contents-part"><ol class="contents-list">' + "".join(entry(c) for c in loose) + "</ol></div>")
    if others:
        blocks.append('<div class="contents-part" id="back-matter"><div class="contents-part-head"><span class="spine-part">Back matter</span></div><ol class="contents-list">'
                      + "".join(f'<li><span class="num"></span><div><a href="{page_name(s)}">{esc(s.title)}</a></div></li>' for s in others)
                      + f'<li><span class="num"></span><div><a href="releases.html">Release history</a><span class="secs">Every edition, what changed, and when</span></div></li></ol></div>')
    words = sum(s.words for s in secs)
    contents = (f'<section class="section-block" id="contents"><div class="container"><p class="eyebrow">Contents</p><h2>{len([s for s in secs if s.kind == "chapter"])} chapters in {len(parts)} parts</h2>'
                f'<p class="lead">Free to read online, from the first chapter to the appendices. About {round(words, -3):,} words.</p>'
                f'<nav class="resolution-path" aria-label="Parts"><ol class="spine-track">{spine}</ol></nav>'
                f'<div class="contents">{"".join(blocks)}</div></div></section>')
    cta = (f'<section class="section-block"><div class="container"><div class="cta-band">'
           f'<div><h3>Get the PDF</h3><p>Subscribe to the newsletter and the PDF edition comes with the welcome email.</p>'
           f'<a class="btn btn-primary" href="{esc(cfg["newsletter_url"])}" rel="noopener">Get the PDF</a></div>'
           f'<div><h3>For publishers</h3><p>Interested in publishing this book? Contact {esc(cfg["author"])} directly.</p>'
           f'<a class="btn btn-secondary" href="{esc(cfg["contact_url"])}" rel="noopener">Contact {esc(cfg["author"])}</a></div>'
           f'</div></div></section>')
    copyright_ = "".join(f"<p>{esc(l)}</p>" for l in bookmd.copyright_lines(cfg))
    footer = (copyright_ + f'<p class="meta">{esc(bookmd.edition_line(cfg))} · <a href="releases.html">Release history</a> · '
              f'<a href="about.html">About the author</a></p>')
    page = fill(tpl("index.html"), **common(cfg, "", f'{cfg["title"]}: {cfg["subtitle"]}', cfg["description"], site, "index", "book"),
                body=hero + contents + cta, footer=footer)
    (out / "index.html").write_text(page, encoding="utf-8")

def changelog_sections(text):
    """[(version, date, markdown body)] from CHANGELOG.md (Keep a Changelog)."""
    out = []
    for m in re.finditer(r"^## \[([^\]]+)\]\s*[-–—]?\s*(.*?)\s*$\n(.*?)(?=^## \[|\Z)", text, re.M | re.S):
        body = re.sub(r"(?m)^\[[^\]]+\]: \S+\s*$", "", m.group(3)).strip()
        out.append((m.group(1), m.group(2), body))
    return out

def write_releases(cfg, secs, out, site):
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    rels = changelog_sections(text)
    current = bookmd.book_version(cfg)
    parts = ['<p class="lead">Every edition of the book is a numbered version. Each one is also published as a PDF and an EPUB '
             'built from exactly the same text. A major version is a new edition, a minor version adds or rewrites sections, '
             'and a patch version fixes mistakes.</p>']
    nav = []
    for ver, date, body in rels:
        vid = "v" + ver.replace(".", "-")
        nav.append((vid, ver))
        md_body = re.sub(r"\]\((?!https?:|#|mailto:)([^)]+)\)", "](#)", body)  # repo-relative links make no sense here
        md_body = re.sub(r"\[([^\]]+)\]\(#\)", r"\1", md_body)
        state = '<span class="pin-tag">this edition</span>' if ver == current else ""
        date_txt = esc(date) if date else ""
        parts.append(f'<h2 id="{vid}">Version {esc(ver)}</h2><p class="release-assets"><span class="pin-tag">{date_txt}</span>{state}</p>'
                     + bookmd.render_markdown(md_body))
    body = "\n".join(parts)
    fake = type("S", (), {})()
    nav_extra = '<ol class="spine">' + "".join(f'<li data-state="pending"><a href="#{v}"><span class="pin-tag">v{esc(x)}</span><span class="chapter-name">Version {esc(x)}</span></a></li>' for v, x in nav) + "</ol>"
    header = ('<header class="chapter-header"><div class="chapter-header-inner"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Contents</a></nav>'
              '<span class="label eyebrow">Release history</span><h1>Editions and changes</h1></div></header>')
    page = fill(tpl("page.html"), **common(cfg, "", f"Release history | {cfg['title']}", f"Every edition of {cfg['title']} and what changed.", site + "releases.html", "releases"),
                nav=nav_html(secs, None) + '<p class="nav-part">Release history</p>' + nav_extra, header=header,
                body=f'<div class="release-history">{body}</div>', after=reading_cta(cfg), footer=footer_html(cfg))
    (out / "releases.html").write_text(page, encoding="utf-8")

def write_404(cfg, out, site):
    body = ('<section class="notfound"><div><p class="code404">404</p><h1>This page is not in the book</h1>'
            '<p class="lead">The link may be from an older edition. The contents page has every chapter.</p>'
            '<p><a class="btn btn-primary" href="/index.html">Go to the contents</a></p></div></section>')
    page = fill(tpl("plain.html"), **common(cfg, "/", f"Page not found | {cfg['title']}", cfg["description"], site + "404.html", "plain", "website"), body=body)
    page = page.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n  <link rel="canonical"')
    (out / "404.html").write_text(page, encoding="utf-8")

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manuscript", default=str(bookmd.MANUSCRIPT))
    ap.add_argument("--out", default=str(ROOT / "dist" / "site"))
    a = ap.parse_args(argv)
    build(pathlib.Path(a.manuscript), pathlib.Path(a.out))

if __name__ == "__main__":
    main()
