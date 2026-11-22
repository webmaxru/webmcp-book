# Editorial log — Chapter 13: Privacy, Consent and the Human in the Loop

v2 rewrite, 2 November 2026. Base text: the Oct 15 manuscript (6,095 words incl. listings). Result: 7,058 words incl. listings. Growth comes from new, sourced material: Chrome's 30 October guidance (commit points, binding approval to the exact plan, stale workflow state, register tools all at once), the W3C TAG early comment of 26 October, and the Agentic Web WG charter's agent-identity deliverables.

## Pass 1 — voice draft
- Full rewrite in Maxim's voice: "Let's build that rule so that it really holds", "So let's be precise about what Listing 13.1 buys you", "Personally for me, this is the right trade-off for money", "Have a look at get_cart", "And please note", asides in parentheses, one dash-pause for "because you can't".
- The co-authorship of the Chrome build-tools page is mentioned once, in passing, where the chapter quotes it (verified fact).
- No semicolons outside code (footnote citations "opened …; open" changed to commas in the final self-check). Few "not X, but Y" contrasts; several from the Oct text reworded.

## Pass 2 — substantive edit
- New subsection "Bind the yes to the exact plan" after the checkout tools, and a "commit point" paragraph. Fidelity rule applied: the demo does not implement plan binding, so the text says so and describes what a production version adds (snapshot, version/hash, compare after the click, error on change) instead of pretending the listing does it.
- "What a trusted click proves" gained one bridging sentence linking Chrome's page-side "private grant" with #288's browser-side "decision grant".
- Session section gained the "register tools all at once" rule, tied to the one-controller design that Listing 13.4 already has.
- Accessibility section gained the TAG paragraph (quotes checked against the comment body via the API) and a one-line link from parity to the TAG's "web for agents" concern.
- Listing labels converted to the house format with repo-relative paths. The Listing 13.3 label now names its file, proposal/request-user-input.webidl.

## Pass 3 — voice recheck + fidelity check
All claims checked (VALIDATION.md 37 rows).
- Kept: every listing byte-identical (5/5), every test fact (800 ms, TH-100200, 7,297 NOK, SESSION_ENDED, CART_EMPTY, four keys, userActivation false), 16 tests (re-run 2 Nov 2026: 16/16), all WebKit and explainer quotes.
- Corrected: spec date 15 Oct → 27 Oct 2026; §7 still empty in the 27 Oct draft; "#165 and #204 open as of 15 October" → re-checked open on 2 Nov (#204 last updated 29 Oct, its IDL re-read and unchanged); #155, #331, #110, #62, #105, #54, #116, #277 re-checked open on 2 Nov.
- Footnote ids: new notes use ch13-40 to ch13-43 so the old ids keep their meaning; 33 defined, 33 referenced.
- Figures 13.1 and 13.2 redrawn and re-rendered (13.1 fixed after inspection: the execute label sat on the browser box, the commit-point note crossed the page lifeline).
- Placeholder grep: zero. Raw HTML in prose: zero (the role="status" paragraph is in a code span).

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: The page cannot see what the agent already asked, so a consequential tool has to wait for the person’s own confirmation, and a trusted click is still not proof that a person clicked.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “First we’ll split the responsibility for consent between the agent, the browser and the page. Then we build Trailhead’s checkout…”
  - After: “First it splits the responsibility for consent between the agent, the browser and the page. Then it builds Trailhead’s checkout…”
  - Removed “Let’s build that rule”, “So let’s be precise”, “And please note”, and “Have a look at”. “that we met in Chapter 5” became “that Chapter 5 already covered”.
- Generalized: “the most direct answer I know” became “a direct answer”. The superlative was the author’s ranking and was not kept as a fact.
- Kept on purpose: “I recommend this trade-off for money” replaces “Personally for me”. The recommendation stays marked as the author’s, not as a spec rule, and the behavior it describes was already in Listing 13.2. “a page I co-authored” stays. Quoted agent speech “I’ve opened the order for you to confirm” stays. No Lars, Kari, or Jonas. Five fences, two figures, 33 footnotes, and 75 baseline quotes were not edited. There is no table.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - None. The commit-point trade-off is now explicitly the author’s recommendation. The chapter does not claim a spec requires the order to finish after the click.
