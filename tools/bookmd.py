"""Shared Markdown -> HTML layer for the three editions (PDF, EPUB, HTML site).

Reads ONLY the manuscript (manuscript/Book.txt and the files it lists, manuscript/resources/)
and tools/book.json. Styling is never decided here: the HTML carries semantic classes
(figure, listing, callout-note, epigraph, ...) and theme/ decides how they look.

Manuscript conventions (see README.md, "Manuscript conventions"):
  * Book.txt lists the files in reading order. Part files start with a Markua attribute line
    `{class: part}` and an H1 `# Part I: Title`; the attribute is stripped for our outputs.
  * One H1 per file: `# Chapter N: Title`, `# Appendix X: Title`, `# About the Author`.
  * Figures: `![Figure N.M — Caption.](images/figure-N-M.png)`, resolved against
    manuscript/resources/ (Leanpub's Markua resources folder). The alt text is the caption.
  * Listings: a paragraph `**Listing N.M** `path` — title` directly above a fenced block.
  * Callouts: a blockquote whose first word is bold: Note, Warning, Tip, Still in flux.
  * Footnotes `[^ch05-3]`, numbered per file in the output.
"""
import html, json, os, pathlib, re, unicodedata
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = TOOLS.parent
MANUSCRIPT = ROOT / "manuscript"
THEME = ROOT / "theme"
esc = html.escape

# ------------------------------------------------------------------ config
def load_config():
    return json.loads((TOOLS / "book.json").read_text(encoding="utf-8"))

def book_version(cfg):
    """$BOOK_VERSION (set by the release workflow from the tag, "v" dropped) or book.json "version"."""
    v = os.environ.get("BOOK_VERSION", "").strip() or str(cfg.get("version", "")).strip()
    return v[1:] if v.startswith("v") else v

def fill(cfg, text):
    """Expand {chrome_version} / {spec_date} / {version} in a book.json string."""
    vals = {"chrome_version": cfg.get("chrome_version", ""), "spec_date": cfg.get("spec_date", ""),
            "version": book_version(cfg), "year": cfg.get("year", "")}
    return re.sub(r"\{(\w+)\}", lambda m: str(vals.get(m.group(1), m.group(0))), text)

def config_warnings(cfg):
    w = []
    for k in ("chrome_version", "spec_date"):
        if not str(cfg.get(k, "")).strip():
            w.append(f"tools/book.json: '{k}' is empty (the copyright and title pages print it)")
    return w

def tested_with(cfg):
    if not (cfg.get("chrome_version") and cfg.get("spec_date")):
        return ""
    return fill(cfg, cfg.get("tested_with", ""))

def edition_line(cfg):
    v = book_version(cfg)
    parts = [cfg.get("edition", "")] + ([f"Version {v}"] if v else [])
    return " · ".join(p for p in parts if p)

def copyright_lines(cfg):
    out = []
    for line in cfg.get("copyright_lines", []):
        if ("{chrome_version}" in line and not cfg.get("chrome_version")) or ("{spec_date}" in line and not cfg.get("spec_date")):
            continue  # never print an empty version; the build warns instead
        out.append(fill(cfg, line))
    return out

# ------------------------------------------------------------------ slugs
def github_slug(text):
    s = unicodedata.normalize("NFKC", text).strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")

# ------------------------------------------------------------------ code
LANG_ALIASES = {"sh": "bash", "shell": "bash", "zsh": "bash", "console": "console", "yml": "yaml",
                "ts": "typescript", "tsx": "tsx", "js": "javascript", "mjs": "javascript", "jsx": "jsx",
                "py": "python", "md": "markdown", "jsonc": "json", "webidl": "text", "idl": "text",
                "text": "text", "txt": "text", "plaintext": "text", "": "text"}

def _highlight(code, lang, attrs):
    lang = (lang or "").strip().split()[0] if lang else ""
    name = LANG_ALIASES.get(lang.lower(), lang.lower())
    try:
        lexer = get_lexer_by_name(name) if name and name != "text" else TextLexer()
    except Exception:
        lexer = TextLexer()
    body = highlight(code, lexer, HtmlFormatter(nowrap=True))
    # one span per line so print can hang-indent wrapped lines and copy can rebuild the text
    lines = body.rstrip("\n").split("\n")
    body = "".join(f'<span class="ln">{l}</span>' for l in lines)
    nlines = len(lines)
    cols = max((len(l.expandtabs(4)) for l in code.rstrip("\n").split("\n")), default=0)
    size = "short" if nlines <= 14 else "long"
    width = "" if cols <= 72 else " w80" if cols <= 80 else " w88" if cols <= 88 else " w96"
    label = esc(lang) if lang else ""
    return (f'<pre class="code {size}{width}" data-lang="{label}" data-lines="{nlines}" data-cols="{cols}">'
            f'<code class="language-{label or "text"}">{body}</code></pre>\n')

def _make_md():
    md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": False,
                                   "highlight": _highlight})
    md.enable(["table", "strikethrough", "linkify"])
    md.use(footnote_plugin)
    return md

MD = _make_md()

# ------------------------------------------------------------------ manuscript model
H1_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.M)
CHAP_RE = re.compile(r"^(Chapter|Appendix)\s+([0-9]+|[A-Z])[.:]\s*(.+)$")
PART_RE = re.compile(r"^Part\s+([IVXLC]+|[0-9]+)[.:]\s*(.+)$")
ATTR_LINE_RE = re.compile(r"^\{\s*[a-z][\w-]*\s*:[^}]*\}\s*$", re.M)
FENCE_RE = re.compile(r"^(```|~~~).*?^\1\s*$", re.M | re.S)

def strip_code(md):
    return FENCE_RE.sub("", md)

class Section:
    """One file of the manuscript, as listed in Book.txt."""
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.slug = self.path.stem
        raw = self.path.read_text(encoding="utf-8")
        self.raw = raw
        self.attrs = ATTR_LINE_RE.findall(raw)
        self.md = ATTR_LINE_RE.sub("", raw).lstrip("\n")       # Markua attribute lines are Leanpub-only
        m = H1_RE.search(strip_code(self.md))
        self.h1 = _plain(m.group(1)) if m else self.slug
        self.label = ""
        self.number = None
        if any("class: part" in a.replace("  ", " ") for a in self.attrs) or PART_RE.match(self.h1):
            self.kind = "part"
            pm = PART_RE.match(self.h1)
            self.number = pm.group(1) if pm else ""
            self.title = pm.group(2).strip() if pm else self.h1
            self.label = f"Part {self.number}" if pm else ""
        elif CHAP_RE.match(self.h1):
            cm = CHAP_RE.match(self.h1)
            self.kind = cm.group(1).lower()
            self.number = cm.group(2)
            self.title = cm.group(3).strip()
            self.label = f"{cm.group(1)} {cm.group(2)}"
        elif "about" in self.slug and "author" in self.slug:
            self.kind = "about"
            self.title = self.h1
        else:
            self.kind = "other"
            self.title = self.h1
        self.words = len(self.md.split())
        self.code_words = sum(len(b.split()) for b in re.findall(r"^```[^\n]*\n(.*?)^```", self.md, re.M | re.S))
        self.part = None          # the Section of the part this file belongs to (chapters only)
        self.children = []        # for parts: their chapters

    @property
    def running_title(self):
        return f"{self.label}. {self.title}" if self.label and self.kind != "part" else self.title

    @property
    def nav_title(self):
        return self.title

    def body_md(self):
        """The Markdown without its H1 (editions print their own opener)."""
        return H1_RE.sub("", self.md, count=1) if H1_RE.search(self.md) else self.md

def read_booktxt(manuscript_dir):
    d = pathlib.Path(manuscript_dir)
    bt = d / "Book.txt"
    if not bt.exists():
        raise SystemExit(f"no Book.txt in {d}")
    names = []
    for line in bt.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.endswith(":"):   # comments, frontmatter:/mainmatter:
            continue
        names.append(line)
    return names

def load_book(manuscript_dir=MANUSCRIPT):
    """[Section] in Book.txt order, with parts linked to their chapters. Missing files raise."""
    d = pathlib.Path(manuscript_dir)
    secs, missing = [], []
    for n in read_booktxt(d):
        p = d / n
        if not p.exists():
            missing.append(n)
            continue
        secs.append(Section(p))
    if missing:
        raise SystemExit("Book.txt lists files that do not exist: " + ", ".join(missing))
    part = None
    for s in secs:
        if s.kind == "part":
            part = s
        elif s.kind == "chapter":
            s.part = part
            if part:
                part.children.append(s)
        else:
            part = None
    return secs

def resolve_image(manuscript_dir, src):
    """images/x.png -> manuscript/resources/images/x.png (Markua) or manuscript/images/x.png."""
    d = pathlib.Path(manuscript_dir)
    for cand in (d / "resources" / src, d / src):
        if cand.exists():
            return cand
    return None

# ------------------------------------------------------------------ headings
def _plain(md_inline):
    t = re.sub(r"`([^`]*)`", r"\1", md_inline)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"(\*\*|__)(.+?)\1", r"\2", t)
    t = re.sub(r"(?<![\w*])[*_]([^*_]+)[*_](?![\w*])", r"\1", t)
    return t.strip()

def headings(section):
    """[(level, text, slug)] for every heading in source order (H1 included), GitHub-style unique slugs."""
    out, seen = [], {}
    for line in strip_code(section.md).splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not m:
            continue
        text = _plain(m.group(2))
        base = github_slug(text)
        n = seen.get(base, 0); seen[base] = n + 1
        out.append((len(m.group(1)), text, base if n == 0 else f"{base}-{n}"))
    return out

# ------------------------------------------------------------------ rendering
KNOWN_CALLOUTS = {"note": "note", "warning": "warning", "tip": "tip", "caution": "warning",
                  "important": "warning", "still in flux": "flux"}
CALLOUT_RE = re.compile(r"<blockquote>\s*<p><strong>(.+?)</strong>", re.S)
FIG_RE = re.compile(r'<p><img src="([^"]+)" alt="([^"]*)"( title="[^"]*")? ?/?></p>')
LISTING_RE = re.compile(r'<p><strong>(Listing\s+([0-9A-Z]+)\.([0-9]+))(.*?)</strong>(.*?)</p>\s*(<pre class="code.*?</pre>)', re.S)
HEAD_RE = re.compile(r"<h([1-6])>(.*?)</h\1>", re.S)
HREF_RE = re.compile(r'href="([^"]+)"')
FIGLABEL_RE = re.compile(r"^(Figure\s+([0-9A-Z]+)\.([0-9]+))\s*[—–:.-]?\s*(.*)$", re.S)

def render(section, id_prefix="", link_map=None, image_url=None, drop_h1=True):
    """Markdown -> HTML fragment with semantic classes only.
    id_prefix: prefix for ids (the PDF is one document). link_map(href) -> new href or None.
    image_url(src) -> URL for a manuscript image path (images/figure-1-1.png)."""
    md = section.body_md() if drop_h1 else section.md
    body = MD.render(md)
    hs = [h for h in headings(section) if not (drop_h1 and h[0] == 1)]
    it = iter(hs)
    def _h(m):
        level, inner = m.group(1), m.group(2)
        try:
            _, _, slug = next(it)
        except StopIteration:
            slug = github_slug(re.sub("<[^>]+>", "", inner))
        return f'<h{level} id="{id_prefix}{slug}">{inner}</h{level}>'
    body = HEAD_RE.sub(_h, body)

    def _fig(m):
        src, alt = m.group(1), m.group(2)
        url = image_url(src) if image_url else src
        fm = FIGLABEL_RE.match(html.unescape(alt))
        if fm:
            fid = f'{id_prefix}figure-{fm.group(2).lower()}-{fm.group(3)}'
            cap = f'<span class="fig-label">{esc(fm.group(1))}</span> {esc(fm.group(4))}'
        else:
            fid, cap = "", esc(html.unescape(alt))
        idattr = f' id="{fid}"' if fid else ""
        return (f'<figure class="figure"{idattr}><img src="{url}" alt="{alt}" loading="lazy">'
                f'<figcaption>{cap}</figcaption></figure>')
    body = FIG_RE.sub(_fig, body)
    if image_url:
        body = re.sub(r'<img src="(?!https?:|data:|file:)([^"]+)"', lambda m: f'<img src="{image_url(m.group(1))}"', body)

    def _listing(m):
        label, a, b, inside, rest, pre = m.groups()[0], m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)
        lid = f'{id_prefix}listing-{a.lower()}-{b}'
        inside = re.sub(r"^\s*[—–:-]\s*", " ", inside) if inside.strip() else ""
        cap = (f'<span class="listing-label">{label}</span>'
               + (f'<span class="listing-title">{inside.strip()}</span>' if inside.strip() else "")
               + (f'<span class="listing-rest">{rest.strip()}</span>' if rest.strip() else ""))
        return f'<figure class="listing" id="{lid}"><figcaption>{cap}</figcaption>{pre}</figure>'

    body = LISTING_RE.sub(_listing, body)

    # epigraph: a blockquote of italic text before the first H2
    first_h2 = body.find("<h2")
    m = re.match(r"\s*<blockquote>\s*<p><em>", body)
    if m and (first_h2 < 0 or first_h2 > 0):
        body = body.replace("<blockquote>", '<blockquote class="epigraph">', 1)

    def _call(m):
        label = m.group(1)
        text = html.unescape(re.sub("<[^>]+>", "", label)).strip()
        kind_word, _, rest = text.partition(":")
        kind = KNOWN_CALLOUTS.get(kind_word.strip().rstrip(".").lower())
        if kind:
            tail = label.split(":", 1)[1] if ":" in label else ""
            tail_html = f'<span class="callout-title">{tail.strip()}</span>' if tail.strip() else ""
            return (f'<blockquote class="callout callout-{kind}">\n<p class="callout-head"><strong class="callout-label">'
                    f'<span class="callout-kind">{esc(kind_word.strip().rstrip("."))}</span>{tail_html}</strong>')
        return (f'<blockquote class="callout callout-aside">\n<p class="callout-head"><strong class="callout-label">'
                f'<span class="callout-title">{label}</span></strong>')
    body = CALLOUT_RE.sub(_call, body)
    # a callout head that is the whole paragraph gets its own line
    body = re.sub(r'<p class="callout-head">(<strong class="callout-label">.*?</strong>)</p>',
                  r'<p class="callout-head callout-head--block">\1</p>', body, flags=re.S)

    if link_map:
        def _href(m):
            new = link_map(html.unescape(m.group(1)))
            return f'href="{esc(new)}"' if new else m.group(0)
        body = HREF_RE.sub(_href, body)
    # external links: class + data-url for print
    def _ext(m):
        href, inner = m.group(1), m.group(2)
        plain = html.unescape(re.sub("<[^>]+>", "", inner))
        cls = "bare" if plain.strip() in (html.unescape(href), html.unescape(href).replace("mailto:", "")) else "ext"
        return f'<a class="{cls}" href="{href}" data-url="{href}">{inner}</a>'
    body = re.sub(r'<a href="((?:https?:|mailto:)[^"]+)">(.*?)</a>', _ext, body, flags=re.S)
    # footnotes: plain numbers, ids unique per document
    body = re.sub(r'(<sup class="footnote-ref"><a [^>]*>)\[(\d+)(?::\d+)?\](</a></sup>)', r"\1\2\3", body)
    body = body.replace('<hr class="footnotes-sep">', '').replace('<hr class="footnotes-sep" />', '')
    body = body.replace('<section class="footnotes">', '<section class="footnotes" role="doc-endnotes"><p class="notes-title">Notes</p>')
    body = re.sub(r'\s*<a href="#fnref[\d:]+" class="footnote-backref">.*?</a>', "", body)
    if id_prefix:
        body = re.sub(r'(id|href)="(#?)(fn|fnref)(\d)', lambda m: f'{m.group(1)}="{m.group(2)}{id_prefix}{m.group(3)}{m.group(4)}', body)
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return body

def render_markdown(md_text):
    """Render free Markdown (CHANGELOG.md) with the same parser."""
    return MD.render(md_text).replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

def split_internal_link(href):
    """'05-x.md#y' -> ('05-x', 'y'); '#y' -> ('', 'y'); external or non-.md -> None."""
    if re.match(r"^[a-z]+:", href) or href.startswith("//"):
        return None
    path, _, frag = href.partition("#")
    path = path.split("/")[-1]
    if path and not path.endswith(".md"):
        return None
    return (path[:-3] if path else "", frag)

def anchor_ids(section):
    """Every id a link may target in a rendered section: headings, figures, listings."""
    ids = {h[2] for h in headings(section)}
    body = strip_code(section.md)
    for a, b in re.findall(r"!\[Figure\s+([0-9A-Z]+)\.([0-9]+)", body):
        ids.add(f"figure-{a.lower()}-{b}")
    for a, b in re.findall(r"^\*\*Listing\s+([0-9A-Z]+)\.([0-9]+)", body, re.M):
        ids.add(f"listing-{a.lower()}-{b}")
    return ids

def check_refs(sections, manuscript_dir):
    """Warnings: missing images, links to missing files/anchors, files without exactly one H1."""
    d = pathlib.Path(manuscript_dir)
    by_slug = {s.slug: anchor_ids(s) for s in sections}
    warn = []
    for s in sections:
        body = strip_code(s.md)
        body = re.sub(r"`[^`\n]*`", "", body)
        for src in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", body):
            if not re.match(r"^[a-z]+:", src) and not resolve_image(d, src):
                warn.append(f"{s.path.name}: missing image {src}")
        for href in re.findall(r"(?<!!)\[[^\]]*\]\(([^)\s]+)", body):
            sp = split_internal_link(href)
            if sp is None:
                continue
            path, frag = sp
            target = path or s.slug
            if path and target not in by_slug:
                warn.append(f"{s.path.name}: link to a file that is not in Book.txt: {href}")
                continue
            if frag and frag not in by_slug.get(target, set()):
                warn.append(f"{s.path.name}: link to unknown anchor {href}")
        n = len(H1_RE.findall(body))
        if n != 1:
            warn.append(f"{s.path.name}: expected exactly one H1, found {n}")
    return warn

def word_count(md):
    return len(md.split())
