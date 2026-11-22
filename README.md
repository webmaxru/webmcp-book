# Tools, Not Clicks

This repository holds the manuscript of *Tools, Not Clicks: Building Agent-Ready Websites with WebMCP* by Maxim Salnikov, second edition, together with its figure sources, editorial records, theme, build tools and hosting setup. The runnable demos live in the companion repository [webmaxru/webmcp-book-demos](https://github.com/webmaxru/webmcp-book-demos). The web edition is hosted on Azure Static Web Apps at https://webmcp.salnikov.no once deployed (see [`DEPLOY.md`](DEPLOY.md)).

## What lives where

| Path | What it is |
| --- | --- |
| [`manuscript/`](manuscript/) | The book: one Markdown file per part, chapter and appendix, in the order of [`Book.txt`](manuscript/Book.txt). Plain Markdown, no styling. Images are in [`manuscript/resources/images/`](manuscript/resources/images/) and are referenced as `images/<file>.png` (Leanpub's layout). |
| [`figures/`](figures/) | Sources of the figures and the script that renders them into `manuscript/resources/images/`. |
| [`theme/`](theme/) | Everything about how the book looks: the web edition (`site/`), the PDF (`print/`), the EPUB (`epub/`) and the fonts. Swapping the theme never touches the manuscript. See [`theme/README.md`](theme/README.md). |
| [`tools/`](tools/) | The build: [`build.py`](tools/build.py) is the one entry point; [`book.json`](tools/book.json) holds the title, version, copyright lines and links; [`lint_manuscript.py`](tools/lint_manuscript.py) checks the manuscript; [`wordcount.py`](tools/wordcount.py) writes the table below. |
| [`editorial/`](editorial/) | Editorial logs, one per chapter: the passes each chapter went through and what was checked. |
| [`infra/`](infra/) | Azure Static Web Apps infrastructure for the web edition, with a one-command deploy. See [`DEPLOY.md`](DEPLOY.md) and [`CUSTOM-DOMAIN.md`](CUSTOM-DOMAIN.md). |
| [`staticwebapp.config.json`](staticwebapp.config.json) | The web edition's hosting rules and security headers; the site build copies it into `dist/site/`. |
| [`.github/workflows/`](.github/workflows/) | Book CI (lint and build on every pull request), Release (on a `v*` tag) and the web deploy. |
| [`.agents/skills/`](.agents/skills/) | Supporting agent instructions, not book content. |
| [`CHANGELOG.md`](CHANGELOG.md), [`RELEASING.md`](RELEASING.md) | What changed in each version, and how to cut a release. |
| [`VALIDATION.md`](VALIDATION.md) | How the second edition was checked against the Chrome documentation, the specification and the WebMCP repository, with every finding and its source. |
| `dist/` | Build output (not committed). |

## Manuscript

Read in this order. Word counts are `wc -w` on the Markdown source (code included); the last column is the share of words inside code blocks. The table is generated: `python3 tools/wordcount.py --update`.

<!-- wordcount:start -->
| File | Title | Words | Code |
| --- | --- | ---: | ---: |
| [`part-1.md`](manuscript/part-1.md) | **Part I: Why the Web Needs an Agent Interface** | 11 |  |
| [`01-the-agentic-web-arrives.md`](manuscript/01-the-agentic-web-arrives.md) | Chapter 1: The Agentic Web Arrives | 6,246 | 0 % |
| [`02-from-apis-to-tools.md`](manuscript/02-from-apis-to-tools.md) | Chapter 2: From APIs to Tools: A Short History | 5,535 | 0 % |
| [`03-mcp-in-practice.md`](manuscript/03-mcp-in-practice.md) | Chapter 3: MCP in Practice | 9,163 | 13 % |
| [`04-enter-webmcp.md`](manuscript/04-enter-webmcp.md) | Chapter 4: Enter WebMCP | 8,046 | 3 % |
| [`part-2.md`](manuscript/part-2.md) | **Part II: The WebMCP API in Depth** | 9 |  |
| [`05-registering-tools.md`](manuscript/05-registering-tools.md) | Chapter 5: Registering Tools with document.modelContext | 10,487 | 11 % |
| [`06-annotations-lifecycle-errors.md`](manuscript/06-annotations-lifecycle-errors.md) | Chapter 6: Annotations, Lifecycle and Errors | 10,918 | 14 % |
| [`07-frames-origins-agents.md`](manuscript/07-frames-origins-agents.md) | Chapter 7: Frames, Origins and Page-Embedded Agents | 9,105 | 15 % |
| [`08-declarative-api.md`](manuscript/08-declarative-api.md) | Chapter 8: The Declarative API: Forms as Tools | 9,333 | 11 % |
| [`part-3.md`](manuscript/part-3.md) | **Part III: Building Agent-Ready Apps** | 7 |  |
| [`09-first-webmcp-app.md`](manuscript/09-first-webmcp-app.md) | Chapter 9: Your First WebMCP App, End to End | 9,439 | 22 % |
| [`10-webmcp-in-frameworks.md`](manuscript/10-webmcp-in-frameworks.md) | Chapter 10: WebMCP in Frameworks | 9,936 | 20 % |
| [`11-designing-tools.md`](manuscript/11-designing-tools.md) | Chapter 11: Designing Tools Agents Can Actually Use | 12,353 | 21 % |
| [`part-4.md`](manuscript/part-4.md) | **Part IV: Trust: Security, Privacy and Consent** | 9 |  |
| [`12-threat-models.md`](manuscript/12-threat-models.md) | Chapter 12: Threat Models for Tool-Exposing Pages | 8,355 | 14 % |
| [`13-privacy-consent-human-in-the-loop.md`](manuscript/13-privacy-consent-human-in-the-loop.md) | Chapter 13: Privacy, Consent and the Human in the Loop | 7,073 | 11 % |
| [`part-5.md`](manuscript/part-5.md) | **Part V: Shipping and the Ecosystem** | 8 |  |
| [`14-testing-debugging-evals.md`](manuscript/14-testing-debugging-evals.md) | Chapter 14: Testing, Debugging and Evals | 12,628 | 20 % |
| [`15-browser-support-and-standards.md`](manuscript/15-browser-support-and-standards.md) | Chapter 15: Browser Support and the Standards Road | 10,884 | 6 % |
| [`part-6.md`](manuscript/part-6.md) | **Part VI: Strategy and the Future** | 8 |  |
| [`16-product-and-business-implications.md`](manuscript/16-product-and-business-implications.md) | Chapter 16: Product and Business Implications | 8,853 | 10 % |
| [`17-the-road-ahead.md`](manuscript/17-the-road-ahead.md) | Chapter 17: The Road Ahead | 8,557 | 7 % |
| [`appendix-a-api-reference.md`](manuscript/appendix-a-api-reference.md) | Appendix A: API Quick Reference (IDL, Attributes, Events, Errors) | 5,377 | 8 % |
| [`appendix-b-glossary.md`](manuscript/appendix-b-glossary.md) | Appendix B: Glossary | 7,332 | 0 % |
| [`appendix-c-resources.md`](manuscript/appendix-c-resources.md) | Appendix C: Resources and Further Reading | 4,222 | 0 % |
| [`appendix-d-migration.md`](manuscript/appendix-d-migration.md) | Appendix D: Migration Notes: navigator.modelContext and provideContext() to document.modelContext | 3,653 | 20 % |
| [`about-the-author.md`](manuscript/about-the-author.md) | About the Author | 300 | 0 % |
| | **Total** | **177,847** | 12 % |
<!-- wordcount:end -->

## Manuscript conventions

The manuscript stays clean Markdown, so the same files work on Leanpub and in this repo's build. `python3 tools/lint_manuscript.py` checks most of these rules.

1. CommonMark with pipe tables, fenced code with a language tag and footnotes. No raw HTML, CSS classes, inline styles, front matter or Leanpub-only asides. The only Markua attribute lines are `{class: part}` in the part files and `{sample: true}` / `{sample: false}`, which mark the Leanpub sample.
2. One `#` heading per file: `# Chapter N: Title`, `# Appendix X: Title`, `# About the Author`, and `# Part I: Title #` in the part files. Sections use `##` to `####`.
3. Figures are one line, `![Figure N.M — Caption.](images/figure-N-M.png)`. The alt text is the caption. The SVG source lives in `figures/src/`, and `python3 figures/render.py figure-N-M` renders it to `manuscript/resources/images/` (read `figures/PALETTE.md` first).
4. Listings have a bold label line above the fence: `**Listing 5.3** `fjord-table/booking-tools.js` — title`. Every listing is byte-identical to a file in the demos repository, or marked as an excerpt.
5. Callouts are blockquotes that start with a bold word: `> **Note:**`, `> **Warning:**`, `> **Tip:**` or `> **Still in flux:**`.
6. Footnote ids are unique across the book: `[^ch05-3]`, `[^appa-2]`.
7. Cross-references use chapter numbers in words ("Chapter 6"), not file links.
8. No placeholders of any kind. If something is unknown, the text says so in plain words.

## Build

Python 3.11 or later.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r tools/requirements.txt
python -m playwright install chromium      # only for the PDF

python3 tools/lint_manuscript.py            # placeholders, raw HTML, images, footnotes, numbering, Book.txt, anchors
python3 tools/build.py                      # everything; or: build.py site | zip | epub | pdf
```

| Command | Output |
| --- | --- |
| `python3 tools/build.py site` | `dist/site/`: the web edition (home page, one page per part, chapter and appendix, About, Release history, 404, sitemap, search) |
| `python3 tools/build.py zip` | `dist/Tools-Not-Clicks-HTML-v<version>.zip`: the web edition for offline reading |
| `python3 tools/build.py epub` | `dist/Tools-Not-Clicks-Maxim-Salnikov-v<version>.epub` |
| `python3 tools/build.py pdf` | `dist/Tools-Not-Clicks-Maxim-Salnikov-v<version>.pdf`: 7 × 9.25 in |

To preview the web edition: `python3 -m http.server -d dist/site 8000`, then open http://localhost:8000. The PDF build uses Playwright's Chromium, or the browser in `CHROME_PATH`.

## Editions and releases

Every release is a Git tag `vX.Y.Z` with a GitHub Release carrying the PDF, the EPUB and the HTML edition (zip), all built from that tag, with the version's [`CHANGELOG.md`](CHANGELOG.md) section as its notes. The current version is in [`tools/book.json`](tools/book.json) and on the book's copyright page. The web edition shows the release history at https://webmcp.salnikov.no/releases.html.

- **PDF**, 7 × 9.25 in, for reading, Leanpub and the KDP paperback.
- **EPUB 3**, checked with EPUBCheck, for Leanpub, KDP (Kindle) and other e-book stores.
- **Web edition**, deployed to Azure Static Web Apps on every change to `main` and on every release.
- [Book CI](.github/workflows/ci.yml) lints the manuscript and builds all three editions on every pull request; the built files are attached to the run.
- [`RELEASING.md`](RELEASING.md): version numbers, and how to cut, rebuild or roll back a release.

Version 1.0.0 (15 October 2026) was the first edition and was never tagged. Version 2.0.0 is the first tagged release.

## Leanpub

The book's Leanpub page is https://leanpub.com/webmcp. Leanpub can publish it in two ways.

**Upload the files built here (recommended).** In the book's Leanpub settings, choose to upload your own files, then upload the release's PDF and EPUB. Readers then get exactly the editions on the GitHub Release, with this theme. Upload the new files for every release.

**Let Leanpub build from this repository.** Leanpub's GitHub writing mode reads `manuscript/Book.txt` and the files it lists, with images from `manuscript/resources/images/`, which is how this repository is laid out. Leanpub then renders the book with its own Markua styling, not this theme. Notes for this mode:

- `Book.txt` lists one file per line, in reading order; `tools/lint_manuscript.py` fails if it names a missing file or misses one.
- Each part file starts with `{class: part}` and a heading in the part form, `# Part I: … #`.
- Chapter headings already carry their numbers (`# Chapter 1: …`), so turn off Leanpub's own chapter numbering in the book's settings.
- The free sample is marked in the manuscript: `{sample: true}` above Part I, Chapter 1, Chapter 5 and About the Author, and `{sample: false}` above Chapters 2 and 6. Leanpub ignores `Sample.txt` for Markua books; this repository keeps it only as a readable list that matches the markers. In upload mode, Leanpub asks for a separate sample file.
- Code blocks, tables, footnotes and `![Figure …](images/…)` figures are standard Markua.

Either way, the version on Leanpub is the version you upload or publish; note it in the release notes Leanpub sends to readers.

## Kindle Direct Publishing (KDP)

**Paperback.** Create a paperback with trim size **7 × 9.25 in (17.78 × 23.5 cm)**, **no bleed**, black-and-white or color interior (the figures are in color; a black-and-white interior prints them in grey). Upload the release's PDF as the manuscript. The PDF's inside margin is 0.875 in, which KDP accepts for any page count up to its maximum. The cover is made separately: use KDP's cover calculator with the final page count (on the PDF's last page, and in the build's report) and the paper type to get the spine width.

**Kindle e-book.** Upload the release's EPUB as the manuscript. Check it in Kindle Previewer before publishing; it shows how the code listings and tables reflow on small screens.

Whenever the page count changes, the paperback cover's spine changes with it.
