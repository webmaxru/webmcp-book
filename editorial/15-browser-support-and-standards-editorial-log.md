# Editorial log — Chapter 15: Browser Support and the Standards Road

v2 rewrite. Passes 1–2 on 2 November 2026. Pass 3, corrections and figures by the editor (2 November 2026). Base text: the Oct 15 manuscript (8,020 words incl. listings). Result: 10,877 words incl. listings and notes. Growth comes from events after the first edition: the TAG early comment of 26 October (new subsection), TPAC 2026, the Agentic Web WG charter and its 29 October “Site Capabilities for Agents” deliverable, Chrome 156 going stable, the #361 ruling, Chrome’s React/Vue change and the post-TPAC #236 exchange.

## Pass 1 — voice draft (the editor)
- Full rewrite in Maxim’s voice: “let’s see what moved”, “let’s have a look at what is in it”, “Personally for me, two of those points matter most”, “In simple words: for almost three weeks the surface you program against stood still”, “Please note”, “I wouldn’t be surprised if the name changed”, “Treat them as the weather forecast, not as the weather”, first-person honesty on unreproduced vendor numbers.
- Every time-sensitive statement dated “as of 2 November 2026”.

## Pass 2 — substantive edit (the editor)
- New subsection “The early comment of 26 October”, rewritten WG history (“What happened in 2026”), the Agentic Web WG charter with the 29 October deliverable change, the new `use-webmcp-tool` row in the libraries table, Table 15.1 kept with #338/#339 dated 8 October, a “good news” paragraph on the unchanged IDL between 15 October and 2 November.
- Listing 15.4 now prints the watcher’s live snapshot of 2 November 2026.

## Pass 3 — voice recheck + fidelity check (the editor)
All claims checked (VALIDATION.md 39 rows; the most time-sensitive ones re-fetched  on 2 November ~10:15 UTC).
- Fidelity: a token diff of the Oct 15 text against the rewrite found every URL, number and code-quoted name kept (only the bare word `webmcp-book-demos` moved into the folder sentence). All four listings byte-identical (check-listings passes).
- Corrections and additions :
  - #236: added Jake Archibald’s replies (30 October, and 2 November 10:10 UTC: a single renamed policy for external tools at the top level), so the text no longer reads as if a second permissions policy were settled. Summary line and footnote updated.
  - Error types: added that Chromium’s main branch switched `executeTool()` to specific DOMExceptions on 16 October (CL 8546218), after the Chrome 157 branch point, so Chrome 158 should be first, not observed.
  - Open PRs: added that Chromium implemented the `Tool` interface on main on 15 October (CL 8510757) ahead of spec PR #348.
  - Figure 15.1 caption: “fifteen months” now runs to this edition, with the 2027 trial ends named separately (August 2025 to March 2027 was nineteen months).
  - New footnote ch15-35 (Chromium CLs and Chromium Dash branch positions).
- Re-confirmed  on 2 November: Mozilla #1412 (neutral, closed, last update 26 Aug), WebKit #670 (oppose, closed, last update 17 Jun), TAG #1238 labels and last comment (26 Oct), strategy #576 labels (In Charter Refinement) and last comment (30 Oct), #361 (open), Chrome 157 stable 3 Nov 2026 and Chrome 162 stable 2 Feb 2027 on Chromium Dash, @mcp-b/webmcp-polyfill 6.0.3.
- Self-check: 0 placeholders, 0 prose semicolons, 0 raw HTML (the `<...>` hits are inside code or autolinks), both image paths exist, footnotes consistent.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: The chapter still gives the engineering answer (Chromium origin trials only) and the standards answer (Community Group draft, positions, TAG review, Agentic Web charter). Announcers and taste-based first person came out. Dated checks and the planning order of confidence stayed.
- What changed (voice/register), with one before/after pair if you changed the opening: Tutorial “we”, “Let’s” / “let’s have a look”, “Please note”, “please remember”, “Now the good news”, and both “In simple words” lines were cut. The claim under each one stayed. Before: “Seventeen days is not much, you might think — let’s see what moved in them.” After: “Seventeen days separate the two checks.” “Personally for me” came off the TAG-comment paragraph. “I wouldn’t be surprised if the name changed on the way to a standard” became “The name may change on the way to a standard.”
- Generalized: The rename sentence. The author’s personal surprise is now a hedged possibility. The chapter does not state that a rename will happen. No frequency claim was promoted into a fact.
- Kept on purpose: “I re-checked”, “When I wrote the first edition”, “I re-ran”, “I could not test”, “I have not reproduced it”, “I have no independent count”, and “my order of confidence”. Quotations that contain “we” (chromestatus, the TAG, Hofmann, Archibald) stayed inside their quotation marks. The epigraph’s “Please note that Community Groups do not create W3C standards.” stayed. No Lars, Kari, or Jonas in this file.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none. `outputSchema` / pull request #254 is a merged change in Table 15.1 and in the 2 November paragraph, and an “open pull request” in the charter-consequences paragraph. The chapter summary still lists `outputSchema` among four open pull requests. Left as written. “Seventeen days” between 15 October 2026 and 2 November 2026 was kept. The calendar difference between those dates is eighteen days. Not corrected.
