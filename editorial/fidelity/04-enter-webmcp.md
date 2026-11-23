# Fidelity check: Chapter 4, Enter WebMCP

Checked 22 November 2026 against `python3 /tmp/check_fidelity.py manuscript/04-enter-webmcp.md`. Result: OK. Hashes matched the baseline.

## Protected spans

- Fences: 2. Listing 4.1 (`search-availability.js`) and Listing 4.2 (`in-page-agent.js`) hash-matched the baseline, including language tags, comments, and closing fences. The listing labels were not retitled.
- Figures: 1. The Figure 4.1 line was not edited.
- Tables: 2. Table 4.1 and Table 4.2, including separator rows. The italic table captions and the bold table titles above them were not edited. The “Sources:” line under Table 4.1 was not edited.
- Footnotes: 34 (`[^ch04-1]` through `[^ch04-34]`). Definitions were not edited.
- Quotes: 113, all still present per the checker.
- Also left byte-identical: the H1 and the epigraph and its attribution. Callout labels (`Note`, `Still in flux`) were not changed. No `{sample:}` line in this file.

## Numbers, dates, and quotations confirmed still present

Confirmed by search after the edit:

- Ingrid, Friday, around seven, window, 19:00, a dozen model round trips, `search_availability`, `book_table`.
- Spec draft 27 October 2026. `provideContext()` / `clearContext()` removed 5 March 2026 (pull request #132). `modelContext` moved in May 2026 (pull requests #177 and #184).
- Inside the fence, still present and not retyped: `date: '2026-11-20'`, `time: '19:00'`, `partySize: 4`.
- TAG comment 26 October 2026, including “Is there time to rename the proposal to something like ‘Tools’?”
- Declarative API removed 8 October 2026 (pull request #338). Status section checked 2 November 2026. Chrome 156 stable 20 October 2026. Origin trial Chrome 149 through 156, extended through Chrome 162, extension recorded 28 September 2026. Edge 150 released 2 July 2026, trial expiry 30 March 2027.
- Charter pull request closed 13 October 2026. Marcos Cáceres, 13 August. Philippe le Hégaret, 28 September. Charter refinement opened 1 October 2026, “until approximately 10 November 2026.” Ilya Grigorik of Shopify, 26 October, “Shopify deploys WebMCP across millions of storefronts”.
- Pull request #348 opened 15 October 2026. Samuel Dallstream added 20 October 2026.
- Names: Jason McGhee, Alex Nahas, Brandon Walderman, Dominic Farolino, Benjamin VanderSloot. Quotation kept: “I was just a guy with a dream.”
- Kept authorial “I”: “I present it as community history, not as established fact.” “I recommend reading it in full.” “I’m one of its co-authors.”

## Generalized

No Lars, Kari, or Jonas in this chapter. Ingrid was not generalized. The contract names only those three. Blog scaffolding and the smiley were removed. The service-worker “soft spot” and “something I’ve done for years” were removed. The rejection reason for the `toolcall` event stayed.

## Flags

None. Ingrid remains a named customer in the opening, on purpose.
