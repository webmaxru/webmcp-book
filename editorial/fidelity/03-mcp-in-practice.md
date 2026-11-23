# Fidelity: Chapter 3, MCP in Practice

Pass: serious technical prose, 22 November 2026.

## Protected spans

Verified against `/tmp/fidelity-baseline.json` with the same hash functions as `/tmp/check_fidelity.py`. All match the baseline and match `HEAD`.

- Fences: 12
- Tables: 2 (Table 3.1, Table 3.2, including separator rows)
- Figures: 2 (`![Figure 3.1`, `![Figure 3.2`)
- Footnotes: 37 (`[^ch03-1]` through `[^ch03-37]`), byte-identical blocks

Listing label paths were not retitled except Listing 3.8, and only the prose after the em dash changed. The path remains `` `trailhead-mcp-server/src/client.js` ``. Code fences were not edited. The H1, epigraph, and both figure lines were not edited.

## Numbers, dates, and quotes confirmed still present

Checked by search in the edited file:

- Scenario: Jotunheimen, end of October, two-person tent, 4,000 kroner, Trailhead, Fjellheim 2 Tent, 3,499 NOK, rated 4.6, order TH-100231, Posten, Saturday, `search_products`, `get_order_status`.
- Dates and versions: 25 November 2024, revision 2026-07-28, 2025-11-25, error `-32022`, 2 November 2026, `@modelcontextprotocol/server` and `client` 2.4.0 (23 October 2026), `@modelcontextprotocol/node` 2.1.2, Zod 4.6.7, Inspector 2.13.0 (28 October), eleven tests, draft 27 October 2026, `trailhead.example`.
- Quotes: “in client-side script instead of on the backend”, “Servers should be extremely easy to build”, “Servers should not be able to read the whole conversation, nor ‘see into’ other servers.”, “MUST NOT write anything to its stdout that is not a valid MCP message”, “Any request can now land on any server instance behind a plain round-robin load balancer without needing shared storage.”, “Instead of your application being a guest within an agent, the agent is a guest on your platform.”

## Generalized

Lars is “a customer” / “the customer” in the opening, the isolation example, the laptop, Listing 3.8’s title, Listing 3.9’s prose, and the MCP Apps close. “his favourite” went with the character. The service-worker sentence no longer says the lesson was taught to the author years ago. The technical constraint is unchanged.

## Flags

None in the chapter.

Checker: `python3 /tmp/check_fidelity.py manuscript/03-mcp-in-practice.md` prints `FAIL` with `missing quotes: 2`. The same two strings are missing from `git show HEAD:manuscript/03-mcp-in-practice.md`. They are baseline excerpts that jump across a fenced listing (`package.json` / Listing 3.2, and Listing 3.10). Fence hashes match. Restoring the file does not clear the FAIL, and the fences were not edited.
