# Editorial log: Chapter 3, MCP in Practice

Manuscript: `manuscript/03-mcp-in-practice.md`. Old text (15 October 2026): 8,948 words by `wc -w` (including listings). New text: 9,168 words (including listings, which are unchanged).

## Pass 1: voice draft (personal-author-voice)

- **Author presence.** "I" for the author's own work and judgment: "I captured it from the wire, not wrote it by hand", "While testing, I also put the logging proxy between the Inspector and the server", "a line I use as the epigraph of Chapter 4", "when I fetched it in November 2026", and one aside from his documented background (service workers can be stopped by the browser at any moment, so stateless code survives; this is a fact about service workers, not an anecdote). "We" for the build-along sections, "you" for the reader.
- **Rhythm.** Rhetorical question added where the old text announced its reasons ("Why does a book about WebMCP need a whole chapter on it? For two reasons."), "Please keep that division of labour in mind", "Time to build.", short checkpoint sentences, parentheses instead of semicolons. Technical paragraphs keep their precision; the voice sits mostly in transitions.
- **Listings** unchanged byte for byte; label lines converted to `**Listing 3.N** \`trailhead-mcp-server/<file>\` — title`.

## Pass 2: substantive edit (professional-writing-editor)

- **Point:** MCP is the backend half of the same idea; its tools vocabulary is what WebMCP borrowed; its wire format changed radically in 2026-07-28; build it once to see the parts; MCP Apps and WebMCP are mirror images.
- **Currency fixes from validation:** SDK 2.4.0 / node 2.1.2 / Inspector 2.13.0 (with the demo re-pinned and re-tested, so the "exact versions the repository pins" sentence stays true), spec date 27 October 2026, PR #204 added next to issue #165, Chrome compare page retitled and its "Tools only" row cited, Tier 1 SDK list brought up to date (Rust and Ruby), "today" replaced by explicit dates.
- **Slop sweep:** no "landscape/robust/seamless/delve", no announcement sentences added. Semicolons in prose and tables: zero (the old text had several, including in Table 3.1 cells; replaced by commas, full stops or parentheses).
- **Length:** no technical section removed; the chapter is slightly longer because of the new currency facts and the voice transitions.

## Pass 3: voice recheck and fidelity check

- Kept unchanged: every MCP quote (re-verified on the live pages), JSON-RPC facts, Tables 3.1 and 3.2, all listing code and wire captures, the client output, test descriptions, the MCP Apps host list (identical on 2 November 2026), the versioning quotes and deprecation windows, the Chrome quotes.
- Corrected: npm versions and dates (ch03-20), Inspector version and its era behaviour re-tested (ch03-28), WebMCP draft date (ch03-34), issue #165 status (ch03-33), compare page title and date (ch03-31), tool-security page dates (ch03-32), "latest" redirect date, the "as checked on" date in the final callout.
- Added: footnotes ch03-36 (PR #204) and ch03-37 (Ruby SDK Tier 1 post).
- Removed: nothing.
