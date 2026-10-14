#!/usr/bin/env python3
"""Build the electronic edition of "Tools, Not Clicks" (working title) as a static site.

Modelled on the generator of Maxim Salnikov's earlier book,
https://github.com/webmaxru/github-agentic-workflows-book (site/generate.py): the same
"Reader" design system (site/assets/style.css and app.js are copied from it), a cover
page with the contents grouped by parts, chapter pages with a sidebar and prev/next
navigation, light / sepia / dark reading themes, and a single-page edition (book.html).

THE MANUSCRIPT IS NEVER MODIFIED. outline/outline.md and chapters/*/*.md stay exactly as
they are (publication-ready Markdown). Everything here happens at build time, in memory:
  * the chapter list (17 chapters in 6 parts, plus appendices) is read from outline/outline.md;
  * a chapter counts as published when a Markdown file whose first heading is
    "# Chapter N: ..." exists under chapters/; every other chapter is shown as
    "To be published";
  * Markdown is rendered with markdown-it (CommonMark + GFM tables + footnotes);
  * figure images are copied next to the rendered page, "Listing N.N" captions become
    code figures, "Figure N.N" captions become <figcaption>s, and "> **Still in flux: ...**"
    blockquotes become styled callouts.

Usage:
    python -m pip install -r site/requirements.txt
    python site/generate.py            # writes the site into site/_site/
    python site/generate.py --out DIR  # or anywhere else
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin

ROOT = Path(__file__).resolve().parents[1]
SITE_SRC = ROOT / "site"
OUTLINE_MD = ROOT / "outline" / "outline.md"
OUTLINE_PDF = ROOT / "outline" / "WebMCP_Book_Outline.pdf"
CHAPTERS_DIR = ROOT / "chapters"

# --- Book identity ---------------------------------------------------------------
BOOK_TITLE = "Tools, Not Clicks"
BOOK_SUBTITLE = "Building Agent-Ready Websites with WebMCP"
FULL_TITLE = f"{BOOK_TITLE}: {BOOK_SUBTITLE}"
SHORT_NAME = "WebMCP · the book"
BOOK_TAGLINE = (
    "A book about WebMCP, the proposed web standard that lets websites hand AI agents "
    "real tools: named, described, schema-typed functions the browser's agent calls "
    "directly, inside the user's own session, with the human watching and in control."
)
AUTHOR_NAME = "Maxim Salnikov"
REPO_URL = "https://github.com/vibeprogrammer/webmcp-book"
DEMOS_URL = "https://github.com/vibeprogrammer/webmcp-book-demos"
SITE_URL = "https://vibeprogrammer.github.io/webmcp-book/"

# --- Calls to action --------------------------------------------------------------
# Both links come from the example book's generator (webmaxru/github-agentic-workflows-book,
# site/generate.py): AUTHOR_URL is its AUTHOR_URL; the newsletter is the isainative
# Substack that its BOOK_DOWNLOAD_URL (https://isainative.substack.com/p/free-agentic-workflows-book)
# lives on, linked at the publication's own sign-up page.
CONTACT_URL = "https://www.linkedin.com/in/webmax/"
NEWSLETTER_URL = "https://isainative.substack.com/subscribe"

STATUS_PENDING = "To be published"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def slugify(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value).lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_]+", "-", value).strip("-")
    return re.sub(r"-{2,}", "-", value) or "section"


# --- Markdown -------------------------------------------------------------------
def make_md() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable("table").enable("strikethrough")
    md.use(footnote_plugin)
    md.use(anchors_plugin, min_level=2, max_level=3, slug_func=slugify, permalink=False)

    # Footnote markers as plain superscript numbers (instead of "[1]").
    def footnote_caption(self, tokens, idx, options, env):
        n = tokens[idx].meta["id"] + 1
        sub = tokens[idx].meta.get("subId", 0)
        return f"{n}" + (f":{sub}" if sub > 0 else "")

    md.add_render_rule("footnote_caption", footnote_caption)
    return md


MD = make_md()


def inline_md(text: str) -> str:
    return MD.renderInline(text)


def wbr(fragment: str) -> str:
    """Allow long API names (document.modelContext) to wrap after a dot."""
    return re.sub(r"(?<=\w)\.(?=\w)", ".<wbr>", fragment)


# --- Outline ---------------------------------------------------------------------
@dataclass
class Chapter:
    number: int
    title: str           # inline Markdown
    summary: str = ""     # inline Markdown
    topics: list[str] = field(default_factory=list)
    part: "Part | None" = None
    source: Path | None = None   # Markdown file when published
    slug: str = ""
    kicker: str = ""
    words: int = 0

    @property
    def published(self) -> bool:
        return self.source is not None

    @property
    def title_text(self) -> str:
        return html.unescape(re.sub(r"<[^>]+>", "", inline_md(self.title)))


@dataclass
class Part:
    number: str      # roman numeral as written in the outline
    title: str
    chapters: list[Chapter] = field(default_factory=list)


def parse_outline() -> tuple[list[Part], list[str]]:
    text = OUTLINE_MD.read_text(encoding="utf-8")
    start = text.index("## Chapter outline")
    end_m = re.search(r"^## (?!Chapter outline)", text[start + 5:], re.M)
    block = text[start: start + 5 + end_m.start()] if end_m else text[start:]
    parts: list[Part] = []
    appendices: list[str] = []
    current: Chapter | None = None
    in_appendix = False
    for line in block.splitlines():
        m = re.match(r"^### Part ([IVXLC]+):\s*(.+)$", line)
        if m:
            parts.append(Part(m.group(1), m.group(2).strip()))
            current, in_appendix = None, False
            continue
        if re.match(r"^### Appendices", line):
            current, in_appendix = None, True
            continue
        m = re.match(r"^#### Chapter (\d+):\s*(.+)$", line)
        if m:
            current = Chapter(int(m.group(1)), m.group(2).strip(), part=parts[-1])
            parts[-1].chapters.append(current)
            continue
        if in_appendix and line.startswith("- "):
            appendices.append(line[2:].strip())
            continue
        if current is None or not line.strip():
            continue
        if line.startswith("- "):
            current.topics.append(line[2:].strip())
        elif line.startswith("*Projects:*"):
            continue
        elif not current.summary:
            current.summary = line.strip()
    return parts, appendices


def find_published(chapters: list[Chapter]) -> None:
    by_number = {c.number: c for c in chapters}
    for md_file in sorted(CHAPTERS_DIR.glob("*/*.md")):
        head = md_file.read_text(encoding="utf-8")[:2000]
        m = re.search(r"^# Chapter (\d+):", head, re.M)
        if not m or int(m.group(1)) not in by_number:
            continue
        ch = by_number[int(m.group(1))]
        ch.source = md_file
        ch.slug = md_file.parent.name          # e.g. 04-enter-webmcp


# --- HTML transforms applied to rendered chapters (build time only) --------------------
def transform_body(body: str) -> str:
    # "**Listing 5.1 — caption**" followed by a code block -> a code figure.
    body = re.sub(
        r"<p><strong>(Listing [\d.]+[^<]*(?:<(?!/strong>)[^<]*)*)</strong></p>\s*(<pre><code[^>]*>.*?</code></pre>)",
        lambda m: f'<figure class="code"><figcaption>{m.group(1)}</figcaption>\n{m.group(2)}</figure>',
        body, flags=re.S)
    # Image paragraph followed by an italic "Figure N.N — ..." caption -> <figure>.
    body = re.sub(
        r"<p>(<img [^>]+>)</p>\s*<p><em>(Figure [\d.]+.*?)</em></p>",
        lambda m: f'<figure class="book-figure">{m.group(1)}<figcaption>{m.group(2)}</figcaption></figure>',
        body, flags=re.S)
    body = re.sub(r"<p>(<img [^>]+>)</p>", r'<figure class="book-figure">\1</figure>', body)
    body = body.replace("<img ", '<img decoding="async" ')

    # Blockquotes: "Still in flux" -> warning callout; the opening quote -> epigraph.
    def bq(m: re.Match) -> str:
        inner = m.group(1).strip()
        t = re.match(r"<p><strong>(Still in flux:.*?)</strong>\s*</p>(.*)$", inner, re.S)
        if t:
            return (f'<aside class="callout callout--warning flux"><p class="callout-title">{t.group(1)}</p>'
                    f"{t.group(2)}</aside>")
        t = re.match(r"<p><strong>([^<]{2,80}?)</strong>\s*</p>(.*)$", inner, re.S)
        if t:
            return f'<aside class="callout callout--note"><p class="callout-title">{t.group(1)}</p>{t.group(2)}</aside>'
        if inner.startswith("<p><em>"):
            return f'<blockquote class="epigraph">{inner}</blockquote>'
        return f"<blockquote>{inner}</blockquote>"

    body = re.sub(r"<blockquote>(.*?)</blockquote>", bq, body, flags=re.S)
    body = re.sub(r"(<table>.*?</table>)", r'<div class="table-wrap">\1</div>', body, flags=re.S)
    body = body.replace('<hr class="footnotes-sep" />', "")
    body = body.replace('<section class="footnotes">',
                        '<section class="footnotes" aria-labelledby="notes"><h2 id="notes">Notes</h2>')
    # Headings: self-links like the example's anchor-link.
    body = re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>',
                  lambda m: f'<h{m.group(1)} id="{m.group(2)}"><a class="anchor-link" href="#{m.group(2)}">{m.group(3)}</a></h{m.group(1)}>',
                  body, flags=re.S)
    return body


def render_chapter_markdown(ch: Chapter) -> tuple[str, list[tuple[str, str]]]:
    text = ch.source.read_text(encoding="utf-8")
    # The kicker ("*Part I · ...*") and the H1 become the page header; drop them from the body.
    lines = text.splitlines()
    out, seen_h1 = [], False
    for line in lines:
        if not seen_h1 and re.match(r"^\*Part [IVX]+ .*\*$", line.strip()):
            ch.kicker = line.strip().strip("*")
            continue
        if not seen_h1 and line.startswith("# "):
            seen_h1 = True
            continue
        out.append(line)
    src = "\n".join(out)
    ch.words = len(re.sub(r"\[\^\d+\]:.*", "", src).split())
    body = MD.render(src)
    sections = [(m.group(1), re.sub(r"<[^>]+>", "", m.group(2)))
                for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)]
    return transform_body(body), sections


# --- Page chrome ------------------------------------------------------------------
def head(title: str, description: str, prefix: str) -> str:
    return f"""<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="{esc(AUTHOR_NAME)}">
  <meta name="color-scheme" content="light dark">
  <meta property="og:type" content="book">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <script>(function(){{try{{var t=localStorage.getItem('aw-theme');if(t&&t!=='system'){{document.documentElement.setAttribute('data-theme',t);}}}}catch(e){{}}}})();</script>
  <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;0,7..72,700;1,7..72,400&display=swap">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="stylesheet" href="{prefix}assets/style.css">
  <link rel="stylesheet" href="{prefix}assets/book.css">
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/typescript.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script defer src="{prefix}assets/app.js"></script>"""


def theme_toggle() -> str:
    return '''<div class="theme-toggle" role="group" aria-label="Reading theme">
        <button type="button" class="theme-opt" data-theme-value="light" aria-pressed="false" title="Light"><span aria-hidden="true">☀</span><span class="visually-hidden">Light theme</span></button>
        <button type="button" class="theme-opt" data-theme-value="sepia" aria-pressed="false" title="Sepia"><span aria-hidden="true">◑</span><span class="visually-hidden">Sepia theme</span></button>
        <button type="button" class="theme-opt" data-theme-value="dark" aria-pressed="false" title="Dark"><span aria-hidden="true">☾</span><span class="visually-hidden">Dark theme</span></button>
      </div>'''


def ext(href: str, label: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{esc(href)}" target="_blank" rel="noopener">{label}</a>'


def cta_band(compact: bool = False) -> str:
    """The two calls to action, on the cover and at the end of every chapter."""
    cls = "cta-band cta-band--compact" if compact else "cta-band"
    return f'''<section class="{cls}" aria-label="Get in touch">
      <div class="cta-grid">
        <div class="cta-card cta-card--publisher">
          <p class="cta-kicker">For publishers</p>
          <p class="cta-title">If you represent a publishing house, contact {esc(AUTHOR_NAME)}.</p>
          <p class="cta-text">Interested in publishing this book? Get in touch with the author directly.</p>
          {ext(CONTACT_URL, f"Contact {esc(AUTHOR_NAME)} ↗", "btn btn-primary")}
        </div>
        <div class="cta-card cta-card--newsletter">
          <p class="cta-kicker">New chapters</p>
          <p class="cta-title">Get notified about the next chapters.</p>
          <p class="cta-text">Sign up for the newsletter to hear when the next chapter is published.</p>
          {ext(NEWSLETTER_URL, "Sign up for the newsletter ↗", "btn btn-quiet")}
        </div>
      </div>
    </section>'''


def chapter_href(ch: Chapter, prefix: str = "chapters/") -> str:
    return f"{prefix}{ch.slug}.html"


def colophon(prefix: str = "") -> str:
    return f'''<footer class="colophon">
    <div class="colophon-inner">
      <p class="colophon-author">By <strong>{esc(AUTHOR_NAME)}</strong> · <em>{esc(FULL_TITLE)}</em> (working title)</p>
      <p class="colophon-meta">{ext(CONTACT_URL, "Publishers: contact Maxim Salnikov")} · {ext(NEWSLETTER_URL, "Newsletter")} · <a href="{prefix}outline.html">Full outline</a> · {ext(REPO_URL, "Book repository on GitHub ↗")} · {ext(DEMOS_URL, "Demos ↗")}</p>
    </div>
  </footer>'''


def reader_bar(prefix: str, published: list[Chapter]) -> str:
    start = chapter_href(published[0], prefix + "chapters/") if published else "#contents"
    return f'''<header class="reader-bar" role="banner">
    <div class="reader-bar-inner">
      <a class="brand" href="{prefix}index.html"><span class="brand-mark">W</span> {esc(SHORT_NAME)}</a>
      <nav class="reader-nav" aria-label="Primary">
        <a href="{prefix}index.html#contents">Contents</a>
        <a href="{start}">Start reading</a>
        <a href="{prefix}outline.html">Outline</a>
        {ext(NEWSLETTER_URL, "Newsletter")}
        {ext(CONTACT_URL, "Publishers")}
      </nav>
      {theme_toggle()}
    </div>
  </header>'''


# --- Pages ------------------------------------------------------------------------
def toc_row(ch: Chapter) -> str:
    num = f"{ch.number:02d}"
    topics = "".join(f"<li>{inline_md(t)}</li>" for t in ch.topics)
    topics_html = f'<ul class="toc-topics">{topics}</ul>' if topics else ""
    if ch.published:
        minutes = max(1, round(ch.words / 200))
        return f'''            <li class="toc-row toc-row--ready">
              <a class="toc-link" href="{chapter_href(ch)}">
                <span class="toc-num">{num}</span>
                <span class="toc-text">
                  <span class="toc-title">{inline_md(ch.title)}</span>
                  <span class="toc-obj">{inline_md(ch.summary)}</span>
                </span>
                <span class="toc-status toc-status--ready">Read · {minutes} min</span>
              </a>
            </li>'''
    return f'''            <li class="toc-row toc-row--pending">
              <div class="toc-link" aria-disabled="true">
                <span class="toc-num">{num}</span>
                <span class="toc-text">
                  <span class="toc-title">{inline_md(ch.title)}</span>
                  <span class="toc-obj">{inline_md(ch.summary)}</span>
                </span>
                <span class="toc-status toc-status--pending">{STATUS_PENDING}</span>
              </div>
            </li>'''


def render_index(parts: list[Part], appendices: list[str], published: list[Chapter]) -> str:
    chapters = [c for p in parts for c in p.chapters]
    minutes = sum(max(1, round(c.words / 200)) for c in published)
    start = chapter_href(published[0]) if published else "#contents"
    pub_list = ", ".join(str(c.number) for c in published) or "none yet"
    blocks = []
    for p in parts:
        rows = "\n".join(toc_row(c) for c in p.chapters)
        ready = sum(1 for c in p.chapters if c.published)
        note = f"{ready} of {len(p.chapters)} published" if ready else STATUS_PENDING
        blocks.append(f'''        <section class="toc-part" aria-labelledby="part-{p.number}">
          <header class="toc-part-head">
            <span class="toc-part-kicker">Part {p.number}</span>
            <h3 id="part-{p.number}" class="toc-part-title">{inline_md(p.title)}</h3>
            <span class="toc-part-note">{note}</span>
          </header>
          <ol class="toc-list">
{rows}
          </ol>
        </section>''')
    app_rows = "\n".join(
        f'''            <li class="toc-row toc-row--pending"><div class="toc-link" aria-disabled="true"><span class="toc-num">{esc(a.split(".")[0])}</span><span class="toc-text"><span class="toc-title">{inline_md(a.split(".", 1)[1].strip() if "." in a else a)}</span></span><span class="toc-status toc-status--pending">{STATUS_PENDING}</span></div></li>'''
        for a in appendices)
    if app_rows:
        blocks.append(f'''        <section class="toc-part" aria-labelledby="part-appendices">
          <header class="toc-part-head">
            <span class="toc-part-kicker">Back matter</span>
            <h3 id="part-appendices" class="toc-part-title">Appendices</h3>
            <span class="toc-part-note">{STATUS_PENDING}</span>
          </header>
          <ol class="toc-list">
{app_rows}
          </ol>
        </section>''')
    return f"""<!doctype html>
<html lang="en">
<head>
  {head(f"{FULL_TITLE} — {AUTHOR_NAME}", BOOK_TAGLINE, "")}
</head>
<body class="home">
  <a class="skip-link" href="#main-content">Skip to main content</a>
  {reader_bar("", published)}

  <main id="main-content" tabindex="-1">
    <section class="cover" aria-labelledby="cover-title">
      <div class="cover-inner">
        <p class="cover-series">A book in progress · working title</p>
        <h1 id="cover-title" class="cover-title">{esc(BOOK_TITLE)}</h1>
        <p class="cover-subtitle">{esc(BOOK_SUBTITLE)}</p>
        <p class="cover-sub">{esc(BOOK_TAGLINE)}</p>
        <p class="cover-author">by <strong>{esc(AUTHOR_NAME)}</strong></p>
        <div class="cover-actions">
          <a class="btn btn-primary" href="{start}">Start reading</a>
          <a class="btn btn-quiet" href="#contents">Browse the outline</a>
        </div>
        <dl class="cover-meta">
          <div class="cover-meta-item"><dt>Length</dt><dd>{len(chapters)} chapters across {len(parts)} parts</dd></div>
          <div class="cover-meta-item"><dt>Published so far</dt><dd>{len(published)} of {len(chapters)} (ch. {pub_list})</dd></div>
          <div class="cover-meta-item"><dt>Reading time</dt><dd>about {minutes} minutes</dd></div>
        </dl>
      </div>
    </section>

    {cta_band()}

    <section id="contents" class="contents" aria-labelledby="contents-title">
      <div class="contents-inner">
        <div class="contents-head">
          <h2 id="contents-title">Outline</h2>
          <p class="contents-note">{len(chapters)} chapters across {len(parts)} parts · <a href="outline.html">full outline</a>{' · <a href="outline/WebMCP_Book_Outline.pdf">PDF</a>' if OUTLINE_PDF.exists() else ''}</p>
        </div>
        <p class="pending-note">Chapters marked <strong>{STATUS_PENDING}</strong> are still being written. {ext(NEWSLETTER_URL, "Sign up for the newsletter")} to hear when they come out.</p>
{chr(10).join(blocks)}
      </div>
    </section>
  </main>

  {colophon()}
</body>
</html>
"""


def sidebar_nav(parts: list[Part], current: Chapter) -> str:
    out = []
    for p in parts:
        items = []
        for c in p.chapters:
            num = f'<span class="chapter-number">{c.number:02d}</span>'
            if c.published:
                cur = c is current
                attrs = ' class="is-current" aria-current="page"' if cur else ""
                items.append(f'<li><a{attrs} href="{c.slug}.html">{num}<span>{inline_md(c.title)}</span></a></li>')
            else:
                items.append(f'<li><span class="nav-pending" title="{STATUS_PENDING}">{num}<span>{inline_md(c.title)}<em class="nav-pending-tag">{STATUS_PENDING}</em></span></span></li>')
        out.append(f'''        <div class="nav-part">
          <p class="nav-part-title" id="navpart-{p.number}">Part {p.number} · {inline_md(p.title)}</p>
          <ol class="nav-chapters" aria-labelledby="navpart-{p.number}">
            {"".join(items)}
          </ol>
        </div>''')
    return "\n".join(out)


def render_chapter(ch: Chapter, body: str, sections, parts, published, prev_ch, next_ch) -> str:
    def pager_link(c: Chapter | None, rel: str) -> str:
        if not c:
            return "<span></span>"
        label = f"Chapter {c.number}: {c.title_text}"
        txt = f"← {esc(label)}" if rel == "prev" else f"{esc(label)} →"
        return f'<a class="pager-link" rel="{rel}" href="{c.slug}.html">{txt}</a>'

    nxt_pending = None
    if next_ch is None or next_ch.number != ch.number + 1:
        allc = [c for p in parts for c in p.chapters]
        nxt_pending = next((c for c in allc if c.number == ch.number + 1), None)
    pending_note = ""
    if nxt_pending is not None:
        pending_note = (f'<p class="pending-note next-pending">Next in the book: <strong>Chapter {nxt_pending.number}: '
                        f'{inline_md(nxt_pending.title)}</strong> — {STATUS_PENDING.lower()}. '
                        f'{ext(NEWSLETTER_URL, "Sign up for the newsletter")} to hear when it is out.</p>')
    toc = "".join(f'<li><a href="#{sid}">{esc(html.unescape(t))}</a></li>' for sid, t in sections)
    minutes = max(1, round(ch.words / 200))
    return f"""<!doctype html>
<html lang="en">
<head>
  {head(f"Chapter {ch.number}: {ch.title_text} — {BOOK_TITLE}", re.sub(r'<[^>]+>', '', inline_md(ch.summary)), "../")}
</head>
<body class="chapter-page">
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <button class="sidebar-toggle" type="button" aria-controls="chapter-sidebar" aria-expanded="false">☰ Chapters</button>

  <div class="page-shell">
    <aside id="chapter-sidebar" class="sidebar" aria-label="Book chapters">
      <div class="sidebar-inner">
        <div class="sidebar-top">
          <a class="site-title" href="../index.html">{esc(FULL_TITLE)}</a>
          {theme_toggle()}
        </div>
        <nav class="chapter-nav" aria-label="Chapter navigation">
{sidebar_nav(parts, ch)}
        </nav>
        <div class="sidebar-cta">
          {ext(NEWSLETTER_URL, "Get notified about the next chapters ↗")}
          {ext(CONTACT_URL, "Publishers: contact Maxim Salnikov ↗")}
        </div>
      </div>
    </aside>

    <div class="content-shell">
      <header class="chapter-header">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Home</a> / Chapter {ch.number} <span class="fm-sep">·</span> {ext(NEWSLETTER_URL, "Get notified about new chapters")} <span class="fm-sep">·</span> {ext(CONTACT_URL, "Publishers: contact the author")}</nav>
        <p class="fm"><span class="fm-k">chapter:</span> <span class="fm-v">{ch.number:02d}</span><span class="fm-sep">·</span><span class="fm-k">part:</span> <span class="fm-v">{esc(ch.part.number)} — {inline_md(ch.part.title)}</span><span class="fm-sep">·</span><span class="fm-k">reading:</span> <span class="fm-v">{minutes} min</span></p>
        <h1>Chapter {ch.number}: {wbr(inline_md(ch.title))}</h1>
        <p class="lead">{inline_md(ch.summary)}</p>
      </header>

      <main id="main-content" class="chapter-main" tabindex="-1">
        <div class="chapter-meta">
          <nav class="metadata-card" aria-labelledby="section-nav-heading">
            <h2 id="section-nav-heading">On this page</h2>
            <ol>{toc}</ol>
          </nav>
        </div>

        <article class="chapter-body section-content">
{body}
        </article>

        {pending_note}
        {cta_band(compact=True)}

        <nav class="pager" aria-label="Chapter pagination">
          {pager_link(prev_ch, "prev")}
          {pager_link(next_ch, "next")}
        </nav>
      </main>

      <footer class="site-footer chapter-footer">
        <p>By <strong>{esc(AUTHOR_NAME)}</strong> · {ext(CONTACT_URL, "Publishers: contact Maxim Salnikov")} · {ext(NEWSLETTER_URL, "Newsletter")} · <a href="../outline.html">Full outline</a> · {ext(REPO_URL, "Book repository on GitHub ↗")} · {ext(DEMOS_URL, "Demos ↗")}</p>
      </footer>
    </div>
  </div>
</body>
</html>
"""


def render_simple_page(title: str, body: str, published: list[Chapter], cls: str = "doc-page") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  {head(f"{title} — {BOOK_TITLE}", BOOK_TAGLINE, "")}
</head>
<body class="home {cls}">
  <a class="skip-link" href="#main-content">Skip to main content</a>
  {reader_bar("", published)}
  <main id="main-content" tabindex="-1">
    <div class="doc-column chapter-body section-content">
{body}
    </div>
    {cta_band(compact=True)}
  </main>
  {colophon()}
</body>
</html>
"""


def render_outline_page(published: list[Chapter]) -> str:
    body = transform_body(MD.render(OUTLINE_MD.read_text(encoding="utf-8")))
    # Mark every chapter heading with its status; published ones link to their page.
    by_num = {c.number: c for c in published}

    def mark(m: re.Match) -> str:
        c = by_num.get(int(m.group(2)))
        badge = (f' <a class="toc-status toc-status--ready" href="chapters/{c.slug}.html">Read</a>' if c
                 else f' <span class="toc-status toc-status--pending">{STATUS_PENDING}</span>')
        return f"{m.group(1)}{badge}</h4>"

    body = re.sub(r"(<h4[^>]*>.*?Chapter (\d+):.*?)</h4>", mark, body, flags=re.S)
    if OUTLINE_PDF.exists():
        body += '\n<p class="pending-note">This outline is also available as a <a href="outline/WebMCP_Book_Outline.pdf">PDF</a>.</p>'
    return render_simple_page("Book outline", body, published)


def render_book(parts: list[Part], published: list[Chapter], bodies: dict[int, str]) -> str:
    """Single-page edition: every published chapter on one printable page."""
    chunks = []
    for c in published:
        b = bodies[c.number]
        b = re.sub(r'(id|href)="#?(fn|fnref)(\d+(?::\d+)?)"',
                   lambda m: f'{m.group(1)}="{"#" if m.group(1) == "href" else ""}c{c.number}-{m.group(2)}{m.group(3)}"', b)
        b = re.sub(r'(id="|href="#)(?!c\d+-)([^"]+)"', lambda m: f'{m.group(1)}c{c.number}-{m.group(2)}"', b)
        b = b.replace('src="', f'src="chapters/').replace('src="chapters/http', 'src="http')
        chunks.append(f'<section class="book-chapter" id="chapter-{c.number}"><p class="kicker">{esc(c.kicker)}</p>'
                      f'<h1>Chapter {c.number}: {inline_md(c.title)}</h1>{b}</section>')
    toc = "".join(f'<li><a href="#chapter-{c.number}">Chapter {c.number}: {inline_md(c.title)}</a></li>' for c in published)
    body = (f'<h1>{esc(FULL_TITLE)}</h1><p><em>Working title. Single-page edition of the published chapters.</em></p>'
            f'<ol class="book-toc">{toc}</ol>' + "\n".join(chunks))
    return render_simple_page("Single-page edition", body, published, cls="doc-page book-page")


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#4f46e5"/><text x="32" y="44" font-family="Georgia,serif" font-size="36" font-weight="700" text-anchor="middle" fill="#fff">W</text></svg>"""


def build(out: Path) -> dict:
    parts, appendices = parse_outline()
    chapters = [c for p in parts for c in p.chapters]
    if not chapters:
        sys.exit("No chapters found in outline/outline.md")
    find_published(chapters)
    published = [c for c in chapters if c.published]

    if out.exists():
        shutil.rmtree(out)
    (out / "chapters").mkdir(parents=True)
    shutil.copytree(SITE_SRC / "assets", out / "assets")
    (out / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    if OUTLINE_PDF.exists():
        (out / "outline").mkdir()
        shutil.copy2(OUTLINE_PDF, out / "outline" / OUTLINE_PDF.name)

    bodies: dict[int, str] = {}
    sections_by: dict[int, list] = {}
    for c in published:
        body, sections = render_chapter_markdown(c)
        # Figure paths: chapters/<dir>/images/x.png is published at chapters/<slug>/images/x.png
        img_dir = c.source.parent / "images"
        if img_dir.exists():
            shutil.copytree(img_dir, out / "chapters" / c.slug / "images")
        body = re.sub(r'src="(?:\./)?images/', f'src="{c.slug}/images/', body)
        bodies[c.number], sections_by[c.number] = body, sections

    for i, c in enumerate(published):
        prev_ch = published[i - 1] if i > 0 else None
        next_ch = published[i + 1] if i + 1 < len(published) else None
        (out / "chapters" / f"{c.slug}.html").write_text(
            render_chapter(c, bodies[c.number], sections_by[c.number], parts, published, prev_ch, next_ch), encoding="utf-8")

    (out / "index.html").write_text(render_index(parts, appendices, published), encoding="utf-8")
    (out / "outline.html").write_text(render_outline_page(published), encoding="utf-8")
    (out / "book.html").write_text(render_book(parts, published, bodies), encoding="utf-8")
    (out / "404.html").write_text(render_simple_page(
        "Page not found", '<h1>Page not found</h1><p><a href="index.html">Back to the book</a></p>', published), encoding="utf-8")
    report = {"chapters": len(chapters), "parts": len(parts), "published": [c.number for c in published],
              "words": {c.number: c.words for c in published}, "out": str(out)}
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(SITE_SRC / "_site"), help="output directory (default: site/_site)")
    args = ap.parse_args()
    report = build(Path(args.out).resolve())
    print(f"Built {report['out']}: {report['chapters']} chapters in {report['parts']} parts; "
          f"published: {', '.join(map(str, report['published'])) or 'none'}")


if __name__ == "__main__":
    main()
