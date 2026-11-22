# Editorial log: Chapter 4, Enter WebMCP

Manuscript: `manuscript/04-enter-webmcp.md`. Figures: `figures/src/figure-4-1.svg` → `manuscript/resources/images/figure-4-1.png`. Demo: `demos-new/fjord-table/` (Listings 4.1 and 4.2). Old text (15 October 2026): 7,207 words by `wc -w`. New text: 8,191 words (including listings and 34 notes).

Skills loaded: personal-author-voice (his voice profile, the Book 2 voice report, slop-patterns reference, Book 2 intro and editorial log, the his recent article), professional-writing-editor, and the house style.

## Pass 1: voice draft (personal-author-voice)

- **Author presence.** "I" for Maxim's own documented roles and judgments: the co-author disclosures on Chrome's build-tools and best-practices pages, the W3C Web Machine Learning CG membership where the standards process is discussed, the service worker parallels (a fact about service workers, not an anecdote). "We" for building Fjord Table together, "you" for the reader. No invented stories.
- **Rhythm.** Questions where the old text announced its point, short checkpoint sentences, "In simple words" and "Bottomline" used once each, one ":)" on the TAG naming question. Parentheses and full stops instead of semicolons.
- **Listings** unchanged byte for byte; labels converted to `**Listing 4.N** \`fjord-table/<file>\` (excerpt) — title`.

## Pass 2: substantive edit (professional-writing-editor)

- **Point of the chapter:** WebMCP turns the page into the tool provider, inside the user's session, mediated by the browser; here is the smallest real tool; here is where the standard stands on 2 November 2026.
- **Currency fixes from validation** (VALIDATION.md spec date 27 Oct and fourth editor (PR #352); the Chrome comparison page's rewrite (new title "When to use WebMCP and MCP", new rows in Table 4.1, the backend/frontend framing dropped because the page dropped it); Chrome 156 stable on 20 Oct; the TAG's early comment of 26 Oct (including the "Tools" rename question); the Agentic Web WG charter's new deliverable name "Site Capabilities for Agents" and Shopify's comment; PR #348 in the "Still in flux" callout. New section "Status and standards politics, November 2026" with Table 4.2 dated 2 Nov.
- **Mechanics:** the old numeric citations ("[4,7]", "[26,27]", "[18,19]") became book-unique footnotes `[^ch04-1]`…`[^ch04-34]`. "Coming soon" replaced by "listed as planned". Semicolons in prose, tables and notes: zero.
- **Slop sweep:** no "landscape/robust/seamless/delve/game-changer", no tricolon stacks, no "it's not X, it's Y" constructions added. Em dashes kept to 13 (about 1.6 per 1,000 words).

## Pass 3: voice recheck and fidelity check

- Kept unchanged: every spec and explainer quote (re-verified against the 27 Oct draft), all Chrome quotes still on their pages, the declarative-API removal date (8 Oct, the merge date; an earlier working note had `updated_at`), all listing code.
- Corrected or added: compare-page epigraph source and wording, Table 4.1 rows, Chrome release status, TAG and charter sections, footnote dates.
- Checks: `check()` lint clean (no placeholders, no prose semicolons, no raw HTML), every image path exists, Listing 4.1 and 4.2 byte-identical to `search-availability.js` and the new `dev/in-page-agent.js`, Fjord Table `npm test`, `test:chrome` and `typecheck` pass on Chromium 156.0.8078.4.
- Figure 4.1 redrawn as SVG in the APM palette (indigo for page and person, amber for the agent, teal for the browser), no title text inside the image, same five-step story as the first edition.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: WebMCP lets the page register tools that run in the user’s tab, with the user’s session, while the browser mediates. The API is in origin trials, and the standards argument is unresolved as of 2 November 2026.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - The Ingrid scene and the heading “Two Fridays at Fjord Table” stayed. The second paragraph no longer announces itself.
  - Before: “Let’s see how that request plays out on most of the web today.”
  - After: “On most of the web today, the agent takes a screenshot…”
  - Also removed “In simple words”, “As we’ll see”, “Let’s have a look”, “Let’s say”, “Please note”, “Please treat”, “with some charm”, “Bottomline”, “and a bit less exciting”, “We now have the idea”, the aside “If you have ever seen”, “I see this as a feature”, “I can’t say I mind :)”, “As a service worker person, I have a soft spot”, and “something I’ve done for years with service worker APIs”. Tutorial “we” became “Chapter 3 builds”, “Chapter 8 looks”, and “The next section”.
- Generalized: none under the contract’s name list. Ingrid stays the Fjord Table customer.
- Kept on purpose: “I present it as community history, not as established fact.” “I recommend reading it in full.” “I’m one of its co-authors.” The McGhee quotation “I was just a guy with a dream.” Listings 4.1 and 4.2, both fences, Table 4.1, Table 4.2, Figure 4.1, all footnotes, the epigraph, and the H1. Every status date and name checked below is still in the chapter.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - None. Ingrid is a named fictional customer. The contract’s generalization list is Lars, Kari, and Jonas only, so she was left.

## Reconciliation (22 November 2026)

Ingrid is now “a guest” / “the guest”, the same treatment as Lars. The Wednesday booking, the party of four, Friday at about seven, the window, and the email interruption stay. The `fetch`-handler aside (“anyone who has maintained…”) was cut. The rejection reason (declaration separated from implementation, sprawling `switch` statements) stays. `guest: 'Ingrid Hansen'` in Chapter 8 is inside a code listing and was not changed.
