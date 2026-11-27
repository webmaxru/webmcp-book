# Editorial log — Appendix C: Resources and Further Reading

the editor, 2 November 2026. Old: 3,307 words. New: about 4,000 words (Chrome pages listed one by one with dates and bylines, a second version column in Table C.1, new framework links).

## Pass 1 — voice draft
- Intro rewritten in the author's voice ("the short routine I use to track changes myself"), with the URL-check result stated plainly, including the two kinds of exception.
- The C.2 opener says which pages carry Maxim's byline as a plain fact ("Two of them carry my name in the byline"), verified in the validation notes

## Pass 2 — substantive edit
- C.2 rebuilt: every Chrome WebMCP docs page listed individually , with published/updated dates and bylines where they matter; added the agents landing page, the early-preview blog post, Chromium Dash and the Inspector's Web Store listing.
- Table C.1: label moved above the table (bold, house style), second column for the 2 November registry versions, two new packages. Package links switched from npmjs.com (bot check) to registry records.
- C.9: web edition at webmcp.salnikov.no; Table C.2 caption moved above as a bold label, its notes moved into the paragraph.
- C.10/C.11 updated (Chrome page dates as a signal, anchors that moved).

## Pass 3 — voice recheck + fidelity
- Kept: every URL of the first edition (all re-fetched), every annotation's chapter pointer, Edge expiry, the C.10 routine.
- Corrected: dates of four Chrome pages, Mozilla/TAG status dates, charter status, MCP checks, package versions, website URL.
- Removed: the chromestatus "Proposed" status word (not re-verified as a word; replaced by milestones).
- Self-checks: 0 placeholders, 0 semicolons (chapter pointers "Chapter 15; Appendix B" became "Chapter 15 and Appendix B"), 0 raw HTML, footnotes defined and used.

## 18 November 2026 — WebMCP polyfill
- Added the W3C polyfill to C.7 in the book's author voice, with the install command, automatic entry point, intended audiences, secure-context and native-API boundaries, and links to the package and its testing notes.
- Checked the package documentation and the Community Group draft on 18 November 2026. Version 0.1.1 targets webmcp-types 0.1.10. No new browser behaviour was observed for this addition.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: Resource list. Entries, URLs, versions, and dates stayed. Three scaffolding phrases came out.
- What changed (voice/register), with one before/after pair if you changed the opening: Before: “and it ends with the short routine I use to track changes myself.” After: “and it ends with a short routine for tracking changes.” “so please pin them” became “so pin them.” The polyfill opener “Want to build and test tools before a browser exposes the native API?” was folded into the following sentence. No resource was deleted.
- Generalized: None.
- Kept on purpose: “when I last checked”, “for packages I give the npm registry’s own record”, “Two of them carry my name in the byline”, and the bylines “and me”. No Lars, Kari, or Jonas in this file.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none. None.

## Pass: waitForToolsUntil (27 November 2026)

Appendix C’s demo table names Listing 5.7, Listing 10.12 and the Chapter 17 adapter and probe changes. None of those files were executed. Sources and the listing ledger: `editorial/fidelity-ledger-wait-for-tools-until.md`.
