# Editorial log: Chapter 6, "Annotations, Lifecycle and Errors"

Manuscript: `manuscript/06-annotations-lifecycle-errors.md`
Figures: `figures/src/figure-6-1.svg`, `figure-6-2.svg`, `figure-6-3.svg` (hand-written SVG, APM figure kit) rendered to `manuscript/resources/images/figure-6-1.png` … `figure-6-3.png`
Demo: `chapters/06-annotations-lifecycle-errors/` (one support-file change in `trailhead/app.js`, see below; suite re-run 2 Nov 2026 on Chromium 156.0.8078.4: 73 passed, 0 failed)
Validation: VALIDATION.md (47 rows)
Length: 9,863 words (Oct 15) → 10,956 words (`wc -w`, listings and notes included). Growth is new material: the spec’s §6.2 text on misrepresented hints, the build-tools and best-practices guidance of 30 Oct (commit points, all-at-once registration, waiting for the UI, approval bound to the exact plan, idempotency), the #361 serialization proposal, #328, #355 and #358. Roughly 1,100 words, the rest tightened slightly.

Materials read before writing: his voice profile, professional-writing-editor/references/slop-patterns.md, the RAAE editorial log and introduction (Book 2), his recent article. the validation notes and the spec draft of 27 October 2026 for every technical claim.

## How the passes ran (honest note)

The plan asks for three passes (voice draft, substantive edit, line edit). For this chapter they were done as one combined rewrite in a single sitting, section by section, with the slop-pattern list and the voice profile open, followed by mechanical checks. I did not produce three separate drafts. The checks listed under Pass 3 were run on the final file.

## Voice (personal-author-voice)

- Register: technical walkthrough, with the exploratory register in the “Still in flux” boxes and the design notes.
- Maxim as author: “I” for the tests and for real choices (“I tested it”, “my answer here”), “we/let’s” for the walkthrough, “you” for the reader.
- One verified biographical fact: he co-authors Chrome’s “WebMCP best practices” and “Build WebMCP tools” pages (bylines verified 2 Nov 2026). Used once, as a parenthesis where the chapter first quotes them. No invented anecdotes.
- Repertoire used where it fits: “Some important things to notice here”, “Pretty much”, rhetorical questions that open a real distinction, parenthetical asides, spaced em dashes kept moderate (17 in prose, about 2.1 per 1,000 words).

## Substantive edit

- Structure kept: hints → life of a call → cancellation → errors → tool lists change. The order already follows a call.
- The annotations section now opens with the spec’s own statement (§6.2, PR #334) that a malicious site can omit or misrepresent hints, so the “hints are not enforcement” point rests on the spec and not only on my reading.
- Cancellation: added the best-practices “Establish explicit commit points” advice next to `throwIfAborted()`. The old text implied this, now it is said once, clearly.
- Errors: Table 6.1 keeps the draft vs Chromium columns. The `undefined` row now notes the open #361 proposal (François Beaufort, 26 Oct). Rule 3 of the error checklist no longer promises a stable string for `undefined`.
- Registration: added “Register tools all at once” and the matching demo change (roll back the batch by aborting the shared controller).
- Removed two paragraphs that repeated the cancellation summary from earlier in the chapter.

## Line edit and mechanical checks

- Semicolons in prose: 0 (were 25, mostly in tables and long sentences, split or rewritten).
- Placeholders (TODO/TBD/FIXME/XXX/[insert/[[/lorem/coming soon/to be published): 0.
- Raw HTML: none.
- Listings: 8 labels in `**Listing 6.N** \`path\` — title` format. 6.2–6.8 byte-identical to the demo files (diffed), 6.1 is an IDL excerpt.
- Footnotes: `[^ch06-1]` … `[^ch06-41]`, all defined and all referenced.
- Every quotation re-checked against the source text fetched on 2 Nov (spec, Chrome pages, issue comments). One quoted gloss of PR #358 replaced with a paraphrase because it was not the PR’s exact wording.
- Slop-pattern scan on the final file: no “worth noting”, “In today’s”, “not just/not only … but” constructions (the October text had none of these either).

## Figures

All three redrawn from scratch in the APM palette (indigo page, amber agent, teal platform, magenta risk), with no figure numbers or titles inside the image.
- 6.1: tools × hints matrix with a one-line “why” per tool, filled check = hint set. The old card-style legend became a single key line.
- 6.2: the seven steps of a call across three lanes (agent, browser, page), with the draft’s exception name for each failure on the right and a band for abort and unload.
- 6.3: cancellation timeline, caller and tool lanes, showing that the caller’s promise rejects at once while the tool keeps running until it checks its signal at a commit point.

## Demo

- `trailhead/app.js` (not printed in the book): registration failure now calls `agentTools.abort()`, rolling back the tools already registered, as Chrome’s best practices recommend.
- README status lines updated to 2 Nov 2026 and Chromium 156.0.8078.4.
- `npm install --no-save playwright@1.64.1`, `node tests/run-tests.mjs`: 73/73. `node_modules` deleted afterwards.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: Hints inform an agent and do not enforce anything. A call’s signal, errors, and `toolchange` are what the page can actually rely on.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Let’s tie those ends up. For that we leave the restaurant and go shopping. Trailhead, the Norwegian outdoor-gear store whose backend MCP server we built in Chapter 3, now gets its in-page tools.”
  - After: “The examples leave the restaurant for the shop. Trailhead, the Norwegian outdoor-gear store whose backend MCP server Chapter 3 built, now gets its in-page tools.”
  - “I left” / “I never explained” is now Chapter 5 leaving the loose ends. “The good news”, “Please note”, and “in simple words” are gone. The API-stability claim, the Chrome 156 build limit, and the “hints are not protection” claim stay. “One more detail worth noticing”, “it is worth stating”, “brings us”, and “We will meet” are cut. The cart-snapshot claim, the caller retry rule, and the later rejection stay.
- Generalized:
  - “For a purchase I can live with that cost” is not restated as a fact that a second prompt is acceptable. What remains is the safety claim: the page’s own confirmation is still the only arrangement that stays safe whichever browser and agent the user has.
- Kept on purpose:
  - Tests and limits: “I ran”, “the build I tested”, “I haven’t tested 157 or later”, “I tested”, “I couldn’t produce”, “in my tests”, “I reproduced”. “I found no primary source”. Co-authorship with André Cipriani Bandarra, and with Alexandra Klepper and François Beaufort. “My rules” for the error split, marked as the author’s advice rather than a spec rule. “Aborting it means ‘I no longer want the result’” stays. That “I” is the caller, not the author. Beaufort’s “I don’t think” stays inside the quotation.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - The author’s personal acceptance of a double confirmation on checkout was removed and not replaced with a general claim that the cost is acceptable.
  - A quoted spec note still reads “the lifetime of an specific invocation.” Left as a quotation.
