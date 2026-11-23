# Editorial log — Chapter 12: Threat Models for Tool-Exposing Pages

v2 rewrite, 2 November 2026. Base text: the Oct 15 manuscript (7,543 words incl. listings). Result: 8,376 words incl. listings. The growth is new material (the merged §6.3.4 two-sided opt-in text, the §6.2 agent-ecosystem paragraph and §6.4.6 from PR #334, Chrome's 30 October "Enforce trust boundaries" guidance, the residual-risks paragraph), not padding.

## Pass 1 — voice draft
- Rewrote every section in Maxim's voice per his voice profile: first person for judgement ("I bet this is the most common real-world WebMCP bug you will ship", the co-authored Chrome guide mentioned in passing, a verified fact), "let's" for walkthroughs ("Let's start with the good news", "Let's have a look at what it checks"), "you" for the reader, parenthetical asides, a few spaced em dashes as spoken pauses (14 in the chapter), rhetorical questions ("Why both sides?"), "In simple words", "Please note", "Personally"-style judgement kept rare.
- No semicolons in prose (two found and removed in the self-check: the three consequences of over-parameterisation became three short sentences; the Table 12.1 sources line uses "and"). In the final self-check the list separators inside Table 12.1 cells and the "opened …; open" citations in footnotes also became commas, so the file has no semicolons outside code.
- Cut AI tells: "Read those three together and the shape of the problem is clear" became a plainer opener; several "not X, but Y" contrasts in the Oct text reworded ("Nothing in the page", "Linguistics is somebody else's department"); the symmetric section closers trimmed.
- No invented anecdotes. The only personal facts used: Maxim co-authored the Chrome build-tools page (the author facts, byline verified).

## Pass 2 — substantive edit (professional-writing-editor)
- Structure kept (seven attack paths ①–⑦ mapped to Figure 12.1) because the figure, the table and the audit all hang on it.
- "Where the line is drawn" now ends the argument with what the spec actually says since 20 October, instead of leaving PR #334 as an open promise.
- §⑤ restructured: "The section that used to be a stub" quotes the new spec text first, then each gate. Gate texts now cite the spec's own rationale ("Why Two-Sided Opt-In Matters"). Added the residual-risk paragraph (origin/window disambiguation, both sides stay separate trust domains).
- New paragraph closing "Shared attack datasets" on §6.4.6, framed as the mirror of the page-side advice.
- Listing labels converted to the house format (`**Listing 12.N** `path` — title`), paths now repo-relative (`chapters/12-threat-models/...`).
- Words cut where the Oct text repeated itself (the result-shaper explanation, the misrepresentation rules).

## Pass 3 — voice recheck + fidelity check
Every number, API name, URL and claim from the Oct 15 text checked (see VALIDATION.md 49 rows).
- Kept: all quotes from §6, the Chrome budgets (30/150/500/1,500, re-read on the page), the test facts (1,088 characters, 50,000-character query, NotAllowedError, collector output), all seven listings byte-identical to the demo files, 26 tests (re-run 2 Nov 2026: 26/26).
- Corrected: spec date 15 Oct → 27 Oct 2026; PR #334 open → merged 20 Oct (with quotes of the new text); §6.3.4 "still a TODO" → written by PR #326 (merged 27 Oct), with the new anchor; PR #326 open → merged; Imperative API page date 21 Sep → 16 Oct; every "open on 15 October" status → re-checked "open on 2 November 2026" (#313, #331, #110, #298, #333, #73, #106); requestUserInteraction box now says the replacement PR #204 was still open on 2 Nov.
- Added: PR #265 (input-length limits), build-tools "Enforcement belongs in your application logic" quote, best-practices "Share the application service", §6.3.4.2 residual risks, §6.4.6.
- Removed deliberately: the "TODO" wording for §6.3.4 (obsolete, and the word would trip the placeholder lint), #326 and #334 from the open-questions list in the summary.
- Images: figure-12-1.png and figure-12-2.png re-rendered from figures/src on 2 Nov 2026 and inspected.
- Placeholder grep (TODO, TBD, FIXME, XXX, [insert, [[, lorem, coming soon, to be published): zero. Raw HTML in prose: zero (the only angle brackets are inside code spans and fences). Footnotes: 45 defined, 45 referenced (ch12-42 unused as an id), all `ch12-` prefixed.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: WebMCP does not grant the page new powers. It adds a model that reads page text and acts with the user’s session, and the page has to validate, label, and confirm on its own side of that boundary.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Let’s start with the good news. WebMCP doesn’t give a page any power it didn’t have before.”
  - After: “WebMCP doesn’t give a page any power it didn’t have before.”
  - Removed “In simple words”, “Let’s have a look at what it checks”, “I’m sure”, and the tutorial “we’ll” in the opening, the length-budget pointer, and “As we saw”. “Please note what the shaper does not do” became “Note what the shaper does not do.”
- Generalized: “I bet this is the most common real-world WebMCP bug you will ship” became “This is an easy WebMCP bug to ship.” “Most common” was not kept as a fact. The next sentences still report the Chromium `executeTool()` calls: a 50,000-character `query` and an undeclared `accountEmail` both reached `execute`.
- Kept on purpose: “a page I co-authored.” “We’ll follow the unresolved elicitation design” and “we can now quote the spec… Here we look at them as security controls” were restored after the checker treated each clause as part of a span between `allow="tools"` quotes. No Lars, Kari, or Jonas. Code fences, the table, both figures, footnotes, listing paths, and the H1 were not edited.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - The frequency claim in “the most common real-world WebMCP bug” was the author’s bet. It is now “an easy WebMCP bug to ship”, supported only by the demonstration in the same paragraph.
  - `python3 /tmp/check_fidelity.py` prints one missing quote, the same quote it prints against `HEAD`. The span runs from the prose after one `allow="tools"` through Listing 12.4’s fence to the next `allow="tools"`. All 85 baseline quote strings are present once fences are removed. Fences (7), the table (1), figures (2), and footnotes (45) hash-match the baseline. The fence was not edited.
