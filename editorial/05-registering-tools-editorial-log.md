# Editorial log: Chapter 5, Registering Tools with `document.modelContext`

Manuscript: `manuscript/05-registering-tools.md`. Figures: `figures/src/figure-5-1.svg`, `figure-5-2.svg` → `manuscript/resources/images/`. Demo: `demos-new/fjord-table/` (Listings 5.3–5.6) and `demos-new/chapters/05-registering-tools/` (the Chromium probe). Old text (15 October 2026): 9,205 words by `wc -w`. New text: 10,209 words (including listings and 48 notes).

Skills loaded: personal-author-voice (his voice profile, the Book 2 voice report, slop-patterns reference, Book 2 intro and editorial log, the his recent article), professional-writing-editor, and the house style.

## Pass 1: voice draft (personal-author-voice)

- **Author presence.** "I" for observations Maxim made with the probe and the type-check, his recommendations ("This is my advice, not a rule from the spec"), and co-author disclosures on the two Chrome pages quoted. Service-worker parallel on the secure-context trap kept as a fact about service workers, not a personal story. "We" for Fjord Table, "you" for the reader.
- **Rhythm.** "In simple words" for the AbortSignal principle and the resolve-when-the-page-agrees rule, "Bottomline" for the `undefined` advice, "Of course" once, questions to open the results-shape and #361 discussions. Parentheses and full stops replace every semicolon.
- **Listings** unchanged byte for byte; labels converted to house format. Listing 5.1 is labelled as Listing 4.1 with markers added (the only listing that isn't a verbatim demo excerpt, by design), Listing 5.2 cites the spec's IDL index.

## Pass 2: substantive edit (professional-writing-editor)

- **Point of the chapter:** walk Listing 4.1 marker by marker, add `book_table`, and be exact about what the browser does and doesn't check. Structure kept (①–⑥), two subsections added: "Resolve when the page agrees" and the batch-registration paragraph in "Registering by page state".
- **Currency fixes from validation** (VALIDATION.md draft date 27 Oct with an explicit statement that the IDL is unchanged; issue #92's October debate (Beaufort, Dallstream, Hofmann quote); issue #361 (Chrome and WPT called wrong on string results, the `undefined` → `"null"` proposal, the Chromium CL); the best-practices update of 30 Oct (resolve only when output matches app state, register all at once with rollback, explicit commit points); PR #348; webmcp-types still 0.1.10; probe re-run on 2 Nov with identical results, including the renderer crash.
- **Error fixed:** "the four-character string `undefined`" was wrong in the first edition. It is nine characters.
- **Slop sweep:** no filler openers, no "it's worth noting", no stacked adjectives. Semicolons in prose, tables and notes: zero (five table cells in Tables 5.2, 5.3 and 5.6 rewritten). Em dashes 17 (about 1.7 per 1,000 words).

## Pass 3: voice recheck and fidelity check

- Kept unchanged: every spec quote (searched in the 27 Oct HTML), all tables except the Table 5.5 caption date and the semicolon cells, the probe observations, listing code, the PR and issue history.
- Checks: lint clean, all image paths exist, Listings 5.3–5.6 byte-identical to the demo files, footnotes `[^ch05-1]`…`[^ch05-48]` all defined and all used, Fjord Table tests and `typecheck` pass, chapter 5 probe clean.
- Figures 5.1 and 5.2 redrawn as SVG in the APM palette. Figure 5.1 is now a three-lane sequence (page, browser, agent) over four phases, with the in-image title removed. Figure 5.2 keeps the three-column anatomy (ModelContextTool → tool definition → RegisteredTool).

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: Register a tool on `document.modelContext`, know what the browser checks, and return a result only when the page agrees.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “It was there to give you a feel for the API, so we moved past most of the details quickly. In this chapter we go back over it slowly.”
  - After: “It was there to give you a feel for the API, so Chapter 4 moved past most of the details quickly. This chapter goes back over it slowly.”
  - Tutorial “we” at the event handoff, the unregistration callback, and the cancellation handoff is now “Chapter 6” or “the section”. “Please notice”, “Let’s look”, both “In simple words” glosses, and filler “of course” (twice) are gone. The claims under them stay, including the renderer crash and the string-quoting sidestep in issue #361.
- Generalized:
  - Ingrid, a one-off name, is now “the guest” (the booking-view user the chapter already uses). Closing the view still does not cancel an in-flight `book_table` call.
- Kept on purpose:
  - “Where Chrome and the draft disagree, I say so.” Co-authorship (“I’m one of its co-authors”, “which I co-wrote”). “I recommend” and “This is my advice, not a rule from the spec.” “My advice for now” on result shape. “I re-ran the check on 2 November 2026.” “Bottomline: always return something…” stays because that sentence is a baseline quote span. Removing the label made `check_fidelity.py` report a new missing quote, so it was restored.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - The opening says the 27 October 2026 IDL matches the 15 October IDL and that the changes since then are prose, not the API. Listing 5.2 (labelled 27 October) includes `outputSchema`, and the “Still in flux” note says pull request #254 merged on 2 November 2026 and added that member. Left as written.
  - `check_fidelity.py` still prints FAIL for three quote spans. The same three fail on `HEAD`. Each one runs across a fenced listing that the baseline quote omitted, so the span is not contiguous in the manuscript. Fence, table, figure, and footnote hashes match. No quote that is present in `HEAD` was dropped.

## Reconciliation (22 November 2026)

The sentence “Here is the listing again, unchanged except for numbered markers” and the Listing 5.1 title “Listing 4.1 again, annotated” were inaccurate. Listing 5.1 also declares `outputSchema`, so Listing 4.1 is not a contiguous excerpt of the runnable file. The prose now says that. The code fences were not changed. The listings themselves still need the author’s decision (see the fidelity ledger). “Bottomline:” on the empty-return advice is now “Until it is, always return something…”. The advice is unchanged.

## Pass: waitForToolsUntil (27 November 2026)

Chapter 5 is the method’s home. Listing 5.2 adds `undefined waitForToolsUntil(Promise<any> promise)`. New Listing 5.7 (`wait-for-tools.js`) uses `Promise.allSettled` and a rollback inside the passed promise. The 10-second Chrome behavior is a warning plus the actor observation timeout, not the specification’s implementation-defined removal of the promise. Not run in a browser. Sources and the listing ledger: `editorial/fidelity-ledger-wait-for-tools-until.md`.
