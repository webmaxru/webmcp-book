#!/usr/bin/env python3
"""Build the EPUB 3 edition from the manuscript (the same files as the PDF and the web edition).

    python3 tools/build_epub.py [--manuscript manuscript] [--out PATH]

One XHTML file per part, chapter and appendix, rendered by tools/bookmd.py, with the figures,
the theme's web fonts (theme/site/fonts, OFL), theme/epub/epub.css and an EPUB 3 navigation
document (plus an NCX for older readers). Validate with EPUBCheck: java -jar epubcheck.jar FILE.epub
(CI and the release workflow run it).
"""
import argparse, datetime, html, os, pathlib, re, sys, uuid, zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd  # noqa: E402
from bookmd import ROOT, THEME, esc  # noqa: E402
from lxml import etree, html as lhtml  # noqa: E402

NS = "http://www.w3.org/1999/xhtml"
EPUB_NS = "http://www.idpf.org/2007/ops"
FONTS = ["literata.woff2", "literata-italic.woff2", "bricolage-grotesque.woff2", "ibm-plex-mono-400.woff2", "ibm-plex-mono-600.woff2"]
DROP_ATTRS = ("data-lines", "data-cols", "data-lang", "data-url", "loading", "role", "aria-current")

def default_out(cfg):
    return ROOT / "dist" / f'{cfg["file_stem"]}-v{bookmd.book_version(cfg)}.epub'

def xhtml_doc(title, body_html, lang="en", epub_type=None):
    """Wrap an HTML fragment as a well-formed XHTML5 document (parsed and re-serialised as XML)."""
    frag = lhtml.fragment_fromstring(body_html, create_parent="div")
    root = etree.Element(f"{{{NS}}}html", nsmap={None: NS, "epub": EPUB_NS})
    root.set("lang", lang); root.set("{http://www.w3.org/XML/1998/namespace}lang", lang)
    head = etree.SubElement(root, f"{{{NS}}}head")
    etree.SubElement(head, f"{{{NS}}}meta", charset="utf-8")
    etree.SubElement(head, f"{{{NS}}}title").text = title
    etree.SubElement(head, f"{{{NS}}}link", rel="stylesheet", type="text/css", href="css/epub.css")
    body = etree.SubElement(root, f"{{{NS}}}body")
    if epub_type:
        body.set(f"{{{EPUB_NS}}}type", epub_type)
    def copy(src, dst):
        for child in src:
            if not isinstance(child.tag, str):
                continue
            el = etree.SubElement(dst, f"{{{NS}}}{child.tag}")
            for k, v in child.attrib.items():
                if k in DROP_ATTRS or k.startswith("on"):
                    continue
                if k == "epub-type":
                    el.set(f"{{{EPUB_NS}}}type", v); continue
                el.set(k, v)
            el.text, el.tail = child.text, child.tail
            copy(child, el)
    body.text = frag.text
    copy(frag, body)
    return etree.tostring(root, xml_declaration=True, encoding="utf-8", doctype="<!DOCTYPE html>")

def build(manuscript, out):
    cfg = bookmd.load_config()
    version = bookmd.book_version(cfg)
    sections = bookmd.load_book(manuscript)
    for w_ in bookmd.check_refs(sections, manuscript) + bookmd.config_warnings(cfg):
        print("warning:", w_, flush=True)
    names = {s.slug: f"{s.slug}.xhtml" for s in sections}
    def link_map(href):
        sp = bookmd.split_internal_link(href)
        if sp is None or not sp[0] or sp[0] not in names:
            return None
        return names[sp[0]] + (f"#{sp[1]}" if sp[1] else "")
    images = {}
    def image_url(src):
        p = bookmd.resolve_image(manuscript, src)
        if not p:
            return src
        images[p.name] = p
        return f"images/{p.name}"

    files, spine, nav = {}, [], []
    title_html = (f'<section class="titlepage" epub-type="titlepage"><p class="t-title">{esc(cfg["title"])}</p>'
                  f'<p class="t-sub">{esc(cfg["subtitle"])}</p><p class="t-author">{esc(cfg["author"])}</p>'
                  f'<p>{esc(bookmd.tested_with(cfg))}</p></section>')
    files["title.xhtml"] = xhtml_doc(cfg["title"], title_html)
    cp = "".join(f"<p>{esc(l)}</p>" for l in bookmd.copyright_lines(cfg))
    files["copyright.xhtml"] = xhtml_doc("Copyright", f'<section class="copyright" epub-type="copyright-page"><p><strong>{esc(cfg["title"])}: '
                                         f'{esc(cfg["subtitle"])}</strong></p>{cp}<p>{esc(bookmd.edition_line(cfg))}</p></section>')
    spine += ["title.xhtml", "copyright.xhtml", "nav.xhtml"]
    for s in sections:
        name = names[s.slug]
        if s.kind == "part":
            lis = "".join(f'<li><a href="{names[c.slug]}">{esc(c.label)}: {esc(c.title)}</a></li>' for c in s.children)
            intro = bookmd.render(s, link_map=link_map, image_url=image_url)
            files[name] = xhtml_doc(f"{s.label}: {s.title}", f'<section class="part" epub-type="part"><h1><span class="label">{esc(s.label)}</span>{esc(s.title)}</h1>{intro}<ol>{lis}</ol></section>')
            nav.append((name, f"{s.label}: {s.title}", [], True))
        else:
            body = bookmd.render(s, link_map=link_map, image_url=image_url)
            body = body.replace('<div class="table-wrap">', "<div>")
            body = body.replace('<section class="footnotes"', '<section class="footnotes" epub-type="endnotes"')
            label = f'<span class="label">{esc(s.label)}</span>' if s.label else ""
            etype = {"chapter": "chapter", "appendix": "appendix", "about": "afterword"}.get(s.kind, "chapter")
            files[name] = xhtml_doc(s.running_title, f'<section epub-type="{etype}"><h1 id="top">{label}{esc(s.title)}</h1>{body}</section>')
            subs = [(f"{name}#{slug}", t) for lvl, t, slug in bookmd.headings(s) if lvl == 2]
            nav.append((name, s.running_title, subs, False))
        spine.append(name)

    # navigation document: parts nest their chapters
    lis, open_part = [], False
    for href, title, subs, is_part in nav:
        sub = ("<ol>" + "".join(f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for h, t in subs) + "</ol>") if subs else ""
        if is_part:
            if open_part:
                lis.append("</ol></li>")
            lis.append(f'<li><a href="{esc(href)}">{esc(title)}</a><ol>')
            open_part = True
        else:
            if open_part and not re.match(r"^\d", href):
                lis.append("</ol></li>"); open_part = False
            lis.append(f'<li><a href="{esc(href)}">{esc(title)}</a>{sub}</li>')
    if open_part:
        lis.append("</ol></li>")
    nav_doc = xhtml_doc("Contents", f'<nav epub-type="toc" id="toc"><h1>Contents</h1><ol>{"".join(lis)}</ol></nav>'
                        f'<nav epub-type="landmarks" hidden="hidden"><ol><li><a epub-type="toc" href="nav.xhtml">Contents</a></li>'
                        f'<li><a epub-type="bodymatter" href="{spine[3] if len(spine) > 3 else "title.xhtml"}">Start of the book</a></li></ol></nav>')
    files["nav.xhtml"] = nav_doc

    book_id = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, cfg.get("repo_url", cfg["title"]) + "#" + version))
    when = datetime.datetime.now(datetime.timezone.utc)
    if os.environ.get("SOURCE_DATE_EPOCH"):
        when = datetime.datetime.fromtimestamp(int(os.environ["SOURCE_DATE_EPOCH"]), datetime.timezone.utc)
    modified = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    mt = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
    manifest = ['<item id="css" href="css/epub.css" media-type="text/css"/>',
                '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
    ids = {}
    for i, name in enumerate(n for n in files if n != "nav.xhtml"):
        ids[name] = f"x{i:02d}"
        manifest.append(f'<item id="{ids[name]}" href="{name}" media-type="application/xhtml+xml"/>')
    for i, (n, p) in enumerate(sorted(images.items())):
        manifest.append(f'<item id="img{i:03d}" href="images/{n}" media-type="{mt.get(p.suffix.lower(), "application/octet-stream")}"/>')
    for i, f in enumerate(FONTS):
        manifest.append(f'<item id="font{i:02d}" href="fonts/{f}" media-type="font/woff2"/>')
    spine_xml = "".join(f'<itemref idref="{"nav" if n == "nav.xhtml" else ids[n]}"/>' for n in spine)
    lang = cfg.get("language", "en")
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{lang}">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{book_id}</dc:identifier>
<dc:title>{esc(cfg["title"])}: {esc(cfg["subtitle"])}</dc:title>
<dc:creator>{esc(cfg["author"])}</dc:creator>
<dc:language>{lang}</dc:language>
<dc:rights>{esc(bookmd.copyright_lines(cfg)[0] if bookmd.copyright_lines(cfg) else "")}</dc:rights>
<dc:description>{esc(cfg.get("description", ""))}</dc:description>
<meta property="dcterms:modified">{modified}</meta>
<meta property="schema:version">{esc(version)}</meta>
</metadata>
<manifest>{"".join(manifest)}</manifest>
<spine toc="ncx">{spine_xml}</spine>
</package>
"""
    points, order = [], 0
    for href, title, subs, is_part in nav:
        order += 1
        points.append(f'<navPoint id="np{order}" playOrder="{order}"><navLabel><text>{esc(title)}</text></navLabel><content src="{esc(href)}"/></navPoint>')
    ncx = (f'<?xml version="1.0" encoding="utf-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
           f'<head><meta name="dtb:uid" content="{book_id}"/></head><docTitle><text>{esc(cfg["title"])}</text></docTitle>'
           f'<navMap>{"".join(points)}</navMap></ncx>')
    out = pathlib.Path(out or default_out(cfg))
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        def put(name, data):
            z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
        put("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        put("OEBPS/content.opf", opf)
        put("OEBPS/toc.ncx", ncx)
        put("OEBPS/css/epub.css", (THEME / "epub" / "epub.css").read_text(encoding="utf-8"))
        for name, data in files.items():
            put(f"OEBPS/{name}", data)
        for n, p in images.items():
            put(f"OEBPS/images/{n}", p.read_bytes())
        for f in FONTS:
            put(f"OEBPS/fonts/{f}", (THEME / "site" / "fonts" / f).read_bytes())
    print(f"EPUB: {out} ({len(sections)} files, {len(images)} images, {out.stat().st_size / 1048576:.1f} MB, version {version})", flush=True)
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manuscript", default=str(bookmd.MANUSCRIPT))
    ap.add_argument("--out", default=None, help="default: dist/<file_stem>-v<version>.epub")
    a = ap.parse_args(argv)
    build(pathlib.Path(a.manuscript), a.out)

if __name__ == "__main__":
    main()
