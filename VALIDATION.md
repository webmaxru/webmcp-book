# Validation report — Tools, Not Clicks v2.0.0

This file records how the second edition was checked. Every chapter, listing, figure and status statement in the first edition (15 October 2026) was checked against the sources below on 2 November 2026, and each finding was either confirmed, corrected in the text or marked as unverified. The tables are the working records of that pass, one per manuscript file, 765 rows in total.

## Sources

- Chrome's WebMCP documentation on developer.chrome.com: every page under <https://developer.chrome.com/docs/ai/webmcp> (overview, imperative API, declarative API, build tools, best practices, when to use WebMCP and MCP, evals, debugging and the related DevTools page), read in full on 2 November 2026 and compared with archived copies from before 15 October.
- The WebMCP specification, Draft Community Group Report of 27 October 2026: <https://webmachinelearning.github.io/webmcp/>, including its IDL index.
- The webmachinelearning/webmcp repository: commits, pull requests and issues since 1 October 2026, and the declarative API explainer. <https://github.com/webmachinelearning/webmcp>
- Behaviour probes in Chromium 156.0.8078.4 with WebMCP testing enabled, and the demo test suites in the webmcp-book-demos repository, re-run on 2 November 2026.
- For the About the Author page: the Chrome documentation bylines, the W3C Web Machine Learning Community Group participant list, the webmaxru/ai-native-dev repository, skills.sh and the npm registry.

## Summary

The API the book teaches has not changed. The IDL in the 27 October draft has the same shape as the 15 October draft the first edition was written against: `document.modelContext` with `registerTool()`, `getTools()` and `executeTool()`, the three events, and `ToolAnnotations` with `readOnlyHint`, `untrustedContentHint`, `consequentialHint` and `debugging`. No listing needed an API change.

What changed between 15 October and 2 November 2026:

1. Chrome published two new or extended guidance pages on 30 October, "Build your user's agentic workflows with WebMCP tools" and "WebMCP best practices". Maxim Salnikov is a co-author of both. Their guidance (register tools all at once, share one application service, wait for the UI, commit points, stale workflow state, recompute on confirmation, trust boundaries in application logic, binding approval to the exact plan, idempotency, time-travel tests, pinned versions) is now in Chapters 6, 9–14 and 16.
2. Chrome's comparison page was rewritten on 27 October as "When to use WebMCP and MCP". Chapters 3, 4 and 16 quote its current text.
3. Chrome's imperative-API page moved its React example to `use-webmcp-tool` and added Vue on 16 October (Chapter 10, Appendix B).
4. The spec's same-origin section, which the first edition described as a TODO, was written: §6.3.4 "Interaction with the Same-Origin Policy" with its two-sided opt-in (pull request #326, merged 27 October). New text in §6.2 on untrusted annotations and §6.4.6 on agent-level guardrails (pull request #334, merged 20 October). Chapters 6, 7 and 12 and Appendix A follow it.
5. The spec has a fourth editor, Samuel Dallstream (pull request #352, 20 October), and is dated 27 October (Chapter 4).
6. The editors ruled on result serialization (issue #361): the spec is right and Chrome and the web-platform tests are wrong. A proposal would turn `undefined` into `"null"`. The book's advice to always return an object holds either way (Chapters 5, 6, 8, 14, Appendix A).
7. The declarative API's `toolcanceled` event in the explainer is now `toolcancel` (pull request #350, Chapter 8).
8. Standards status: the W3C TAG posted an early review comment on 26 October, TPAC 2026 took place on 26–30 October, and the proposed Agentic Web charter names the deliverable "Site Capabilities for Agents" (Chapters 4, 8, 15 and 17).
9. Chrome 156 became Stable on 20 October with WebMCP still off by default. Chrome 157 is due on 3 November. The origin trial is unchanged (Chapter 15).
10. Package versions moved: the MCP TypeScript SDK 2.4.0 and Inspector 2.13.0 (Chapter 3), chrome-devtools-mcp 1.12.0 (Chapter 14).

One error in the first edition's sources was corrected along the way: pull request #338, which removed the declarative API from the spec, merged on 8 October 2026.

## Unverified

These items are kept in the text with their original source and date, or marked in the text as unverified:

- Chrome 158 behaviour (specific error types from `executeTool()` and a `Tool` interface) is inferred from Chromium main-branch commits of 15–16 October. Only Chromium 156 was tested (Chapters 14 and 15).
- The two Chrome extensions (the Model Context Tool Inspector and the Example Agentic Chrome Extension) were not run on 2 November (Chapters 8, 9 and 14).
- The real-model eval runs reported in Chapter 14 were not repeated and are kept as October results.
- Third-party documentation that is rendered by script was not re-read: the MCP-B framework guide quotes in Chapter 10 and OpenAI's function-calling guidance in Chapter 11.
- The Angular demo suite in Chapter 10 was not re-run. Its listings are unchanged.
- Whether a Chrome build later than 156 fixes the renderer crash in Appendix A (crbug 573722078).
- The Google Developer Expert listing in About the Author is confirmed by the author's GitHub profile, not by the GDE directory.
- The book's repositories moved to github.com/webmaxru on 2 November 2026, and the demos repository is now public. The manuscript repository stays private, so its link in Appendix C works only for people with access.
- Nothing in this edition was tested in Chrome 157 or later.

## Per-file records

### Chapter 1: The Agentic Web Arrives


File: `book/manuscript/01-the-agentic-web-arrives.md` (2 November 2026). Checked against the shared validation notes and primary sources read on 2 November 2026: the spec (Draft CG Report, 27 October 2026), the explainer README and implementation-status.md on `main` (raw files), Chrome for Developers "WebMCP" (updated 7 October 2026), the Edge origin-trial page. Non-WebMCP sources (vendor blogs, benchmarks) are historical statements with dates and were not re-fetched; they describe events in 2023–2025 and cannot change.

#### Chapter 1: The Agentic Web Arrives

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Spec terminology: agent = "an autonomous assistant…", browser agent = "provided by or through the browser…" (l.13) | OK | Unchanged quotes; re-read in the 27 Oct draft | https://webmachinelearning.github.io/webmcp/#terminology |
| 2 | Gemini in Chrome quotes, Sept 2025 (l.21) | OK (historical) | Unchanged | https://blog.google/products/chrome/chrome-reimagined-with-ai/ |
| 3 | ChatGPT Atlas introduced Oct 2025, now retired (l.21) | OK (historical, read 15 Oct 2026) | Unchanged | https://help.openai.com/en/articles/20001371-chatgpt-atlas-retirement |
| 4 | Claude in Chrome: 1,000-user preview Aug 2025, all paid plans Dec 2025 (l.27) | OK (historical) | Unchanged | https://www.anthropic.com/news/claude-for-chrome |
| 5 | Chrome docs offer an example agent extension and a tool inspector; "Chrome Extensions can query and execute WebMCP tools with content scripts" (l.27) | OK | Unchanged; both extensions still listed (the shared validation notes) | https://developer.chrome.com/docs/ai/webmcp |
| 6 | Explainer: tools "can be invoked by AI agents, including those built into the browser, hosted in iframes, or running in extensions" (l.35) | OK | Unchanged (README on main) | https://github.com/webmachinelearning/webmcp |
| 7 | Prompt API exposes Gemini Nano, no network after first download (l.35) | OK (page dated 26 Aug 2026, outside this pass) | Unchanged | https://developer.chrome.com/docs/ai/prompt-api |
| 8 | Chrome docs definition of *actuation* (l.41) | OK | Unchanged; "Key Term" box still on the page | https://developer.chrome.com/docs/ai/webmcp |
| 9 | Explainer quotes on observation via screenshots / DOM / a11y tree, "struggle to navigate…", "simple operations often require multiple steps…" (l.41, l.59) | OK | Unchanged | https://github.com/webmachinelearning/webmcp |
| 10 | CUA quotes and benchmark numbers (58.1 % WebArena, 87 % WebVoyager) (l.52, l.104) | OK (historical) | Unchanged | https://openai.com/index/computer-using-agent/ |
| 11 | Chrome docs: tool can tell whether "a field requires a full name versus a separate first and last name" (l.73) | OK | Unchanged (also on the OT blog post) | https://developer.chrome.com/docs/ai/webmcp |
| 12 | Brave's Comet prompt-injection disclosure, Aug 2025 (l.85) | OK (historical) | Unchanged | https://brave.com/blog/comet-prompt-injection/ |
| 13 | Anthropic red-team numbers 23.6 % → 11.2 %, 35.7 % → 0 (l.87) | OK (historical) | Unchanged | https://www.anthropic.com/news/claude-for-chrome |
| 14 | Screenshots "roughly 1,000–1,800 input tokens each" (l.95) | OK (doc quote, not re-fetched) | Unchanged | https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool |
| 15 | WebArena 14.41 % vs 78.24 % (l.101) | OK (historical, arXiv) | Unchanged | https://arxiv.org/abs/2307.13854 |
| 16 | Explainer: "more control over whether and how…", disintermediation goal, code reuse goal (l.132–138) | OK | Unchanged | https://github.com/webmachinelearning/webmcp#goals--non-goals |
| 17 | Chrome docs: "users gain trust…", "keeps your brand and human-centered design choices intact" (l.136) | OK | Unchanged | https://developer.chrome.com/docs/ai/webmcp |
| 18 | Explainer goals/non-goals quotes ("enable human-in-the-loop workflows", "fully autonomous workflows", "The human web interface remains primary; agent tools augment…") (l.156) | OK | Same words; the last quote is now split into two quoted halves so the prose carries no semicolon | https://github.com/webmachinelearning/webmcp#goals--non-goals |
| 19 | Chrome limitation "primarily designed for local browser workflows with a human in the loop" (l.156) | OK | Unchanged | https://developer.chrome.com/docs/ai/webmcp |
| 20 | Spec intro: pages "can be thought of as Model Context Protocol servers that implement tools in client-side script instead of on the backend" (l.166) | OK | Unchanged, re-read in the 27 Oct draft | https://webmachinelearning.github.io/webmcp/#intro |
| 21 | "Chrome and Edge are both running origin trials … Chrome also offers a flag" (l.168) | OK | Unchanged. Chrome OT from 149, extended to 162 (chromestatus); Edge OT from Edge 150, expires 30 Mar 2027; flag `chrome://flags/#enable-webmcp-testing` | the shared validation notes; https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a |
| 22 | Chrome docs: "offers higher accuracy for agentic task completion … progressive enhancement" (l.168) | OK | Unchanged | https://developer.chrome.com/docs/ai/webmcp |
| 23 | Implementation status "As of 15 October 2026 … ChatGPT Desktop … Brave's Leo … Meta Ray-Ban Display as 'coming soon'" (l.172) | CHANGED (date) | Re-checked 2 Nov 2026 (file unchanged since before the book): ChatGPT Desktop supported, Brave Leo experimental, Chrome OT from 149, Edge OT from 150, Meta Ray-Ban Display on its way (off by default, enabled per device). The literal "coming soon" is paraphrased so the manuscript lint passes | https://github.com/webmachinelearning/webmcp/blob/main/implementation-status.md |
| 24 | Spec "dated 15 October 2026 … Draft Community Group Report … not a W3C Standard nor … Standards Track" (l.214) | CHANGED | "dated 27 October 2026"; status sentence verbatim unchanged; footnote ch01-2 updated | https://webmachinelearning.github.io/webmcp/ (the shared validation notes, CHANGED #8) |
| 25 | Moving-target callout "Most were checked in mid-October 2026" (l.218) | CHANGED | "This edition was re-checked … in early November 2026" | (editorial) |
| 26 | Projects (Fjord Table, Trailhead, Helpdesk Widget, Test Agent), tool names, chapter numbers (l.176–198) | OK | Unchanged; tool names match chapters 3–14 | book/manuscript |
| 27 | Part structure (Parts I–VI and their chapters) (l.204–210) | OK | Unchanged; matches Book.txt | book/manuscript/Book.txt |
| 28 | Callout format `> **Still in flux: title**` + blank line (three places) | CHANGED (format) | house style rule 5: `> **Still in flux:** text` as one paragraph | the house style |

Nothing in this chapter depended on an API shape that changed (the shared validation notes headline: the IDL is unchanged since 15 October). The chapter has no code listings.

#### Demo changes

None. Chapter 1 has no code and no demo folder.

#### Figures

- Figure 1.1 (three places a browser agent lives): redrawn as `figures/src/figure-1-1.svg` in the APM palette. Same meaning.
- Figure 1.2 (actuation loop vs one tool call): redrawn as `figures/src/figure-1-2.svg`. Same meaning.
- Figure 1.3 (four projects and their chapters): redrawn as `figures/src/figure-1-3.svg`. Chapter numbers unchanged.

### Chapter 2: From APIs to Tools: A Short History


File: `book/manuscript/02-from-apis-to-tools.md` (2 November 2026). Checked against the shared validation notes and primary sources read on 2 November 2026: Chrome for Developers "When to use WebMCP and MCP" (updated 27 Oct 2026), "WebMCP best practices" (updated 30 Oct 2026), "WebMCP" (7 Oct 2026); the explainer README on `main`; the MCP specification site; the OpenAPI and A2A specification pages. Historical sources (papers, 2023–2025 announcements) describe dated events and were not re-fetched.

#### Chapter 2: From APIs to Tools: A Short History

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Fielding 2000, REST (l.19) | OK (historical) | Unchanged | https://ics.uci.edu/~fielding/pubs/dissertation/top.htm |
| 2 | OpenAPI began as Swagger, donated by SmartBear, Linux Foundation project (l.23) | OK | Unchanged | https://www.openapis.org/about |
| 3 | "latest published version … 3.2.1, dated 10 September 2026" (l.23) | OK, re-checked | Kept, with "still the latest when I checked in November 2026" | https://spec.openapis.org/oas/latest.html |
| 4 | JSON Schema current version 2020-12 (l.25) | OK | Unchanged | https://json-schema.org/specification |
| 5 | ReAct (Oct 2022) and Toolformer (Feb 2023) quotes (l.31) | OK (historical) | Unchanged | arXiv links in notes |
| 6 | OpenAI function calling June 2023 quotes and examples (l.41) | OK (historical) | Unchanged | https://openai.com/index/function-calling-and-other-api-updates/ |
| 7 | Anthropic `name`/`description`/`input_schema`, `tool_use`; Gemini "a subset of the OpenAPI schema" (l.43) | OK | Unchanged | notes ch02-9, ch02-10 |
| 8 | Structured Outputs Aug 2024, `strict: true`, 100 % vs < 40 % (l.45) | OK (historical) | Unchanged | https://openai.com/index/introducing-structured-outputs-in-the-api/ |
| 9 | "In WebMCP … the browser passes the schema to the agent but does not validate calls against it" (l.69) | OK | Unchanged (spec IDL unchanged; inputSchema is passed through, the shared validation notes) | https://webmachinelearning.github.io/webmcp/#idl-index |
| 10 | ChatGPT plug-ins 23 March 2023, manifest fields, launch partners (l.77) | OK (historical) | Unchanged | notes ch02-12, ch02-13 |
| 11 | GPTs and actions Nov 2023 (l.81) | OK (historical) | Unchanged | https://openai.com/index/introducing-gpts/ |
| 12 | 2026 ChatGPT "plugins" and MCP events (l.85) | OK (as read 15 Oct) | Unchanged in substance, callout reformatted | notes ch02-12, ch02-15 |
| 13 | Chrome best-practices quotes: "A clear description should describe what the tool does and when to use it", "Don't use this tool for weather", `create-event` vs `start-event-creation-process` (l.97–99) | OK, re-checked | Quotes still on the page (updated 30 Oct 2026). Text now says the page is one Maxim co-authors (byline: Alexandra Klepper, Maxim Salnikov, François Beaufort); footnote ch02-16 updated with authors and dates | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 14 | Anthropic MCP announcement quotes, 25 Nov 2024 (l.107) | OK (historical) | Unchanged | https://www.anthropic.com/news/model-context-protocol |
| 15 | MCP hosts/clients/servers, JSON-RPC 2.0; tool fields `name`, `title`, `description`, `inputSchema`; current version 2026-07-28 (l.111) | OK, re-checked | Unchanged. `modelcontextprotocol.io/specification/latest` still redirects to 2026-07-28; the versioning page still says "The current protocol version is 2026-07-28" | https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning |
| 16 | MCP donated to the Agentic AI Foundation, 9 Dec 2025, co-founders and supporters, three founding projects (l.113) | OK (historical) | Unchanged | notes ch02-19, ch02-20 |
| 17 | A2A announced 9 April 2025, quotes, Agent Card at `/.well-known/agent-card.json` (l.121) | OK | Unchanged | notes ch02-21, ch02-22 |
| 18 | A2A at Linux Foundation 23 June 2025, spec 1.0.0, AAIF Growth Stage Aug 2026 (l.123) | OK, re-checked | 1.0.0 is still "Latest Released Version" (2 Nov 2026) | https://a2a-protocol.org/latest/specification/ |
| 19 | Explainer: backend integrations' three weaknesses (l.141–145) | OK, re-checked | Unchanged (UI disintermediation, replication of state and auth, developer burden) | https://github.com/webmachinelearning/webmcp |
| 20 | Chrome compare page: WebMCP "accesses live session data, cookies, and DOM elements that are available only in a live browser tab. Instead of your application being a guest within an agent, the agent is a guest on your platform." (l.147) | CHANGED | The page was rewritten on 27 Oct 2026 and retitled "When to use WebMCP and MCP". The first sentence is gone. Text now quotes the current wording: "Tools run in the page with the user's session. Instead of your application being a guest within an agent, the agent is a guest on your platform." Added the page's "WebMCP is not an extension or a replacement of MCP." Footnote ch02-26 retitled and re-dated | https://developer.chrome.com/docs/ai/webmcp/compare-mcp |
| 21 | Explainer: "in-page Model Context Protocol (MCP) servers that implement tools exposing client-side logic and DOM interaction rather than server-side APIs" (l.149) | OK | Unchanged | https://github.com/webmachinelearning/webmcp |
| 22 | Repository created 5 Aug 2025 (l.149) | OK (API metadata, read 15 Oct 2026) | Unchanged | https://api.github.com/repos/webmachinelearning/webmcp |
| 23 | Explainer "Alternatives considered" quotes: "MCP was built primarily for server-to-client…", "coupling a web API directly to an actively evolving backend protocol…", "shares a common vocabulary…" and prior art list (MCP-B, OpenAPI/ChatGPT Actions, A2A) (l.153–157) | OK, re-checked | Unchanged | https://github.com/webmachinelearning/webmcp#alternatives-considered |
| 24 | Table 2.1 (five approaches); WebMCP envelope "A W3C Community Group draft" (l.163) | OK | Unchanged (spec is a Draft CG Report, 27 Oct 2026) | https://webmachinelearning.github.io/webmcp/ |
| 25 | Chrome limitation "Clients and browsers must visit a site directly to know if it has callable tools" (l.175) | OK, re-checked | Unchanged | https://developer.chrome.com/docs/ai/webmcp |
| 26 | "Still in flux" callouts in `> **Still in flux: title**` form (l.85, l.131) | CHANGED (format) | house style rule 5 form; A2A version note says 1.0.0 is still the latest in November 2026 | the house style |

No code listings in this chapter.

#### Demo changes

None. Chapter 2 has no code and no demo folder.

#### Figures

- Figure 2.1 (N × M vs N + M): redrawn as `figures/src/figure-2-1.svg` in the APM palette, same meaning.
- Figure 2.2 (timeline 2000–2026): redrawn as `figures/src/figure-2-2.svg`, two rows of seven, colour plus fill style for the five categories (readable in greyscale). Same stages and dates as the old figure, except the WebMCP end: the two WebMCP boxes (explainer 2025, CG draft) are now one "2025–26 WebMCP" box naming the explainer and the origin trials (Chrome 149+, Edge), to match the chapter text and the shared validation notes

### Chapter 3: MCP in Practice


File: `book/manuscript/03-mcp-in-practice.md` (2 November 2026). Most of this chapter is about MCP, which the shared validation notes does not cover, so I checked the MCP sources myself on 2 November 2026: the MCP specification pages for revision 2026-07-28 (versioning, architecture, tools, stdio, elicitation, versioning-and-compatibility), the MCP blog index, the MCP Apps overview, the TypeScript SDK v2 documentation pages quoted in the chapter, and the npm registry. WebMCP statements were checked against the shared validation notes v1, the spec (27 October 2026), Chrome's "When to use WebMCP and MCP" (27 October 2026) and "WebMCP tool security" (1 September 2026), issue #165 and PR #204.

#### Chapter 3: MCP in Practice

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | MCP open-sourced 25 Nov 2024, announcement quotes (l.17) | OK (historical) | Unchanged | https://www.anthropic.com/news/model-context-protocol |
| 2 | "MCP takes some inspiration from the Language Server Protocol" (l.19) | OK | Unchanged | https://modelcontextprotocol.io/specification/2026-07-28 |
| 3 | Current revision 2026-07-28 (l.21, l.264) | OK, re-checked | Unchanged. `/specification/latest` redirects to 2026-07-28; versioning page: "The current protocol version is 2026-07-28" | https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning |
| 4 | Host/client/server definitions, host duties, "1:1 relationship", "extremely easy to build", "see into" (l.25–33) | OK, re-checked | Unchanged | https://modelcontextprotocol.io/specification/2026-07-28/architecture |
| 5 | JSON-RPC 2.0, Jan 2013, three message types (l.39) | OK | Unchanged | https://www.jsonrpc.org/specification |
| 6 | stdio "MUST NOT write anything to its stdout…"; Streamable HTTP single endpoint, per-request SSE (l.43–44) | OK, re-checked | Unchanged | stdio and streamable-http pages |
| 7 | Handshake removed, `Mcp-Session-Id` removed, `_meta` keys, "MCP is a stateless protocol…", `server/discover`, "free to invoke any RPC inline" (l.48–54) | OK, re-checked | Unchanged | changelog, architecture, versioning pages |
| 8 | Listing 3.1 (`server/discover` wire capture) | OK | Byte-identical to `wire/listing-3-1.txt`; test 9 re-captured the live exchange with SDK 2.4.0 and it still matches | demo test suite, 2 Nov 2026 |
| 9 | Cache hints `resultType`, `ttlMs`, `cacheScope`; error `-32022`; dual-era / legacy / modern (l.100–110) | OK, re-checked | Unchanged | versioning page; release post |
| 10 | Table 3.1 (legacy vs modern) | OK | Unchanged content; semicolons inside cells replaced by commas | changelog |
| 11 | Server features quotes; Table 3.2 (l.124–134) | OK | Unchanged | tools/resources/prompts pages |
| 12 | Tool names 1–128 chars; inputSchema root object, 2020-12 default; structured results MUST/SHOULD; annotations and "untrusted unless they come from trusted servers"; two kinds of error; "human in the loop" (l.140–152) | OK, re-checked | Unchanged | https://modelcontextprotocol.io/specification/2026-07-28/server/tools |
| 13 | Chrome compare guide: WebMCP "omits various server-side concepts, such as resources" (l.162) | OK, re-checked; page CHANGED around it | Quote still on the page (retitled "When to use WebMCP and MCP", 27 Oct 2026). Added the page's new table row "Building blocks: Tools, resources, prompts" vs "Tools only". Footnote ch03-31 retitled and re-dated | https://developer.chrome.com/docs/ai/webmcp/compare-mcp |
| 14 | Elicitation modes and rules; MRTR with `input_required`, `inputResponses`, `requestState`; sampling/roots/logging deprecated (l.166–178) | OK, re-checked | Unchanged | elicitation and patterns pages |
| 15 | "the WebMCP draft I checked today (dated 15 October 2026) contains no such method [requestUserInteraction]"; issue #165 "still open" (l.180) | CHANGED | Draft now dated 27 October 2026, still no `requestUserInteraction` (or `requestUserInput`); #165 still open on 2 Nov 2026; added: open PR #204 proposes `requestUserInput()` with modes aligned with MCP elicitation (new footnote ch03-36). Chrome's tool-security page still says "the spec draft includes requestUserInteraction()" (page last updated 1 Sep 2026) | https://webmachinelearning.github.io/webmcp/ ; https://github.com/webmachinelearning/webmcp/issues/165 ; https://github.com/webmachinelearning/webmcp/pull/204 ; the shared validation notes, CHANGED #14 |
| 16 | SDK v2 package split; README quotes (l.188) | OK, re-checked | README of 2.4.0 has the same sentences | npm `@modelcontextprotocol/server` 2.4.0 README |
| 17 | "On 15 October 2026 the npm registry listed server and client at 2.3.1, node at 2.1.1, Zod 4.6.7 … the exact versions the companion repository pins" (l.188) | CHANGED | npm on 2 Nov 2026: server 2.4.0 and client 2.4.0 (published 23 Oct 2026), node 2.1.2, Zod 4.6.7. Demo `package.json` re-pinned to these and the lock file regenerated; all 11 tests pass. Footnote ch03-20 records both sets | https://registry.npmjs.org/@modelcontextprotocol/server |
| 18 | Listings 3.2–3.8, 3.10 (catalog, tools, context, server, stdio, http, client, inspect.sh) | OK | Code unchanged, byte-identical to the demo files (`check-listings.mjs` 10/10). Label lines converted to the house style form `**Listing 3.N** \`trailhead-mcp-server/<file>\` — title` | demo folder |
| 19 | SDK doc quotes: "the only schema you write", "derives the JSON Schema…", "only documentation the model gets", "Input validation error", "before the result leaves your server" (l.239–263) | OK, re-checked | Unchanged | https://ts.sdk.modelcontextprotocol.io/v2/servers/tools |
| 20 | Per-request factory quote, "cheap and side-effect free… module scope", `authInfo` (l.269–339) | OK, re-checked | Unchanged (page wording "side-effect-free"; the book paraphrases "free of side effects") | https://ts.sdk.modelcontextprotocol.io/v2/serving/http |
| 21 | stdio logging to stderr (l.360) | OK, re-checked | Unchanged | https://ts.sdk.modelcontextprotocol.io/v2/serving/stdio |
| 22 | Handler "trusts its caller…", DNS rebinding; Host: evil.example → 403 (l.390) | OK, re-checked + tested | Unchanged; test 10 passed on 2 Nov 2026 | SDK http page; demo tests |
| 23 | `Mcp-Method` missing → HTTP 400 with "…the required Mcp-Method header is absent" (l.392) | OK, tested | Unchanged; test 10 asserts the message with SDK 2.4.0 | demo tests |
| 24 | Callout: migration-guide quote "Nothing in v2 puts a 2026-07-28 byte on the wire by default…", `legacy: 'stateless'` / `'reject'` (l.394) | OK, re-checked | Unchanged; callout reformatted to house style form | migration and legacy-clients pages |
| 25 | `versionNegotiation` modes ("byte for byte", auto, pin), stdio probe on a sibling process (l.426) | OK, re-checked | Unchanged | protocol-versions and migration pages |
| 26 | Client output block and Listing 3.9 (`tools/call` wire capture) | OK | Listing byte-identical; test 8 (client end to end) and test 9 (wire) pass with 2.4.0 | demo tests |
| 27 | Inspector "Version 2.11.0, current on npm on 15 October 2026", modes `--web`/`--cli`/`--tui` (l.494) | CHANGED | 2.13.0, current on 2 Nov 2026 (published 28 Oct); `--help` still lists `--web`, `--cli`, `--tui` | npm; `mcp-inspector --help` |
| 28 | "Inspector CLI 2.11.0 opened with a 2025-11-25 initialize request" (l.517) | CHANGED (re-tested) | Re-tested with 2.13.0 through `tests/wire-tap.mjs`: it still sends `initialize` with `protocolVersion: "2025-11-25"` | wire log, 2 Nov 2026 |
| 29 | Tests: eleven tests, under four seconds, all passed (l.521) | OK, re-run | 11/11 passed on 2 Nov 2026 in about 3.9 s with the new pins, Node 22.23.2 | demo tests |
| 30 | Streaming, `notifications/progress`, closing the stream cancels, `subscriptions/listen` (l.529) | OK | Unchanged | streamable-http page; changelog |
| 31 | MCP Apps quotes, `_meta.ui.resourceUri`, `ui://`, "their own dialect of MCP", `io.modelcontextprotocol/ui`, host list (Claude, Claude Desktop, VS Code GitHub Copilot, Microsoft 365 Copilot, Goose, Postman, MCPJam, Archestra.AI) (l.531) | OK, re-checked | Unchanged; host list identical on 2 Nov 2026 | https://modelcontextprotocol.io/extensions/apps/overview |
| 32 | Chrome: "Instead of your application being a guest within an agent, the agent is a guest on your platform." (l.535) | OK, re-checked | Unchanged | compare-mcp page |
| 33 | Versioning quotes, statuses, deprecation windows (l.543–547) | OK, re-checked | Unchanged | versioning page; release post |
| 34 | "latest" redirect "when I fetched it today" (l.553) | CHANGED (date) | "when I fetched it in November 2026" | https://modelcontextprotocol.io/specification/latest |
| 35 | "all four Tier 1 SDKs (TypeScript, Python, Go and C#) spoke the new revision on the day it shipped" (l.555) | OK + ADDED | Kept as the state on release day, now "all four Tier 1 SDKs of that moment"; added: by end of September Rust and Ruby had joined as Tier 1, Ruby with full 2026-07-28 support (new footnote ch03-37) | https://blog.modelcontextprotocol.io/ (post of 29 Sep 2026) |
| 36 | Callout "MCP after 2026-07-28": deprecations, tasks extension, roadmap of 22 Aug 2026; "as checked on 15 October 2026" (l.561) | CHANGED (date) | "as re-checked on 2 November 2026"; no newer roadmap or spec post found on the MCP blog | https://blog.modelcontextprotocol.io/ |
| 37 | `document.modelContext.registerTool()` (l.567) | OK | Unchanged (the shared validation notes: entry point and method unchanged) | spec IDL |
| 38 | Chrome: "Manage core logic with MCP", "Build a contextual UI with WebMCP" (l.569) | OK, re-checked | Unchanged | compare-mcp page |

#### Demo changes

Folder `demos-new/chapters/03-mcp-in-practice/trailhead-mcp-server/`:

- `package.json`: `@modelcontextprotocol/server` 2.3.1 → 2.4.0, `@modelcontextprotocol/client` 2.3.1 → 2.4.0, `@modelcontextprotocol/node` 2.1.1 → 2.1.2, `@modelcontextprotocol/inspector` (dev) 2.11.0 → 2.13.0; `zod` stays 4.6.7. `package-lock.json` regenerated by `npm install`.
- `tests/check-listings.mjs`: regex and usage comment updated for the v2 label format (`**Listing 3.N** \`path\` — title`) and the new manuscript path.
- `README.md`: pins, the 2 November test result, the Inspector 2.13.0 observation, the listing-check usage.
- No source file and no captured wire file changed.

Test results on 2 November 2026 (Node.js 22.23.2, Linux, box heavily loaded): `npm test` 11 passed, 0 failed (3.9 s). `node tests/check-listings.mjs manuscript/03-mcp-in-practice.md`: 10 of 10 listings identical. Inspector 2.13.0 era probe via `tests/wire-tap.mjs`: opens with a 2025-11-25 `initialize`. `npm run check` (node --check on each file) was started but did not finish within 130 s because the shared box was at load 59 with 124 MB free memory; every source file was already executed by the passing test suite. `node_modules` deleted after the run.

#### Figures

- Figure 3.1 (client–host–server architecture with Trailhead's server): redrawn as `figures/src/figure-3-1.svg`, same meaning.
- Figure 3.2 (legacy vs modern MCP, with the MRTR `input_required` retry): redrawn as `figures/src/figure-3-2.svg`, same meaning.

### Chapter 4: Enter WebMCP


File: `book/manuscript/04-enter-webmcp.md` (2 November 2026). Checked against the shared validation notes and primary sources read on 2 November 2026: the spec (Draft CG Report, 27 October 2026, full HTML), the explainer README on `main`, the GitHub API for every issue and pull request cited, Chrome for Developers pages ("WebMCP" updated 7 Oct, "Imperative API" updated 16 Oct, "When to use WebMCP and MCP" updated 27 Oct, "WebMCP best practices" and "Build your user's agentic workflows" updated 30 Oct), chromestatus, the W3C TAG review #1238 and the Agentic Web WG charter draft. Listings were compared byte for byte with `demos-new/fjord-table/`.

#### Chapter 4: Enter WebMCP

| # | Claim / API / listing (short quote, old section) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph from the Chrome page comparing WebMCP and MCP | CHANGED | Page rewritten 27 Oct 2026 and retitled "When to use WebMCP and MCP" (new author Kasper Kulikowski). Epigraph re-quoted from the current text, footnote title and date updated | https://developer.chrome.com/docs/ai/webmcp/compare-mcp |
| 2 | Spec intro: pages "can be thought of as Model Context Protocol servers that implement tools in client-side script" | OK | Unchanged, re-read in the 27 Oct draft | https://webmachinelearning.github.io/webmcp/#intro |
| 3 | Spec dated 15 October 2026, three editors | CHANGED | 27 October 2026 draft, four editors: Samuel Dallstream (Microsoft) added by PR #352, merged 20 Oct | https://github.com/webmachinelearning/webmcp/pull/352 |
| 4 | IDL: `document.modelContext`, `registerTool`/`getTools`/`executeTool`, events `toolchange`/`toolactivated`/`toolcancel`, annotations `readOnlyHint`, `untrustedContentHint`, `consequentialHint`, `debugging` | OK | Unchanged; IDL index identical to the 15 Oct draft (diffed) | https://webmachinelearning.github.io/webmcp/#idl-index |
| 5 | Declarative API removed from the spec, PR #338, 8 Oct 2026 | OK | 8 Oct is the merge date (GitHub API `merged_at`); the shared validation notes lists 13 Oct, which is `updated_at`. Book keeps 8 Oct | https://github.com/webmachinelearning/webmcp/pull/338 |
| 6 | Table 4.1 (WebMCP vs MCP) | CHANGED | Rows "Who can call tools" (quoted: "Any agent or client with access to the rendered page (browsers, webviews, etc.)") and "Building blocks: Tools only" added from the 27 Oct page. "MCP for backend / WebMCP for frontend" framing removed (no longer on the page). MCP transport described as JSON-RPC 2.0 | https://developer.chrome.com/docs/ai/webmcp/compare-mcp |
| 7 | Call-centre / in-store expert analogy | CHANGED | Reworded on the 27 Oct page; the book paraphrases the current wording | https://developer.chrome.com/docs/ai/webmcp/compare-mcp |
| 8 | MCP current protocol version 2026-07-28 | OK | Unchanged | https://modelcontextprotocol.io/specification/2026-07-28 |
| 9 | Chrome origin trial 149–162, flag `chrome://flags/#enable-webmcp-testing` | OK | Unchanged (chromestatus) | https://chromestatus.com/feature/5117755740913664 |
| 10 | Chrome 156 stable | CHANGED | 156 went stable 20 Oct 2026 (156.0.8078.80); 157 due 3 Nov. Table 4.2 dated 2 Nov | https://chromiumdash.appspot.com/schedule |
| 11 | Imperative API page: "requires a name, description, and input schema with relevant properties" | OK | Quote still present (page updated 16 Oct) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 12 | Chrome 153: unregistering no longer cancels in-flight executions; Chrome 155 deprecates string input; `debugging` annotation from Chrome 156 | OK | All three still on the page | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 13 | webmcp-types 0.1.10 | OK | Still latest on npm on 2 Nov | https://www.npmjs.com/package/webmcp-types |
| 14 | Build-tools page quote | OK + NEW | Quote still present. Page byline now André Cipriani Bandarra and Maxim Salnikov; text says "(I'm one of its co-authors)" | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 15 | Best-practices page | OK + NEW | Byline Klepper, Salnikov, Beaufort (updated 30 Oct); disclosure added where quoted | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 16 | "Coming soon" wording for a planned feature | CHANGED | Replaced by "listed as planned" (house style placeholder rule; the source still lists it as planned) | https://developer.chrome.com/docs/ai/webmcp |
| 17 | Open issues cited (#234, #224, #158, #92, #255, #254, #236, #165, #204, #73, #9) | OK | All still open on 2 Nov (GitHub API) | https://github.com/webmachinelearning/webmcp/issues |
| 18 | "Still in flux" callout | CHANGED | Adds PR #348 (`Tool` interface, opened 15 Oct, open) | https://github.com/webmachinelearning/webmcp/pull/348 |
| 19 | W3C TAG review | CHANGED | Christian Liebel's early comment of 26 Oct quoted, including the naming question ("Is there time to rename the proposal to something like 'Tools'?"), the declarative-first ask and the "web for agents" concern. Framed as a comment, not a resolution | https://github.com/w3ctag/design-reviews/issues/1238 |
| 20 | Agentic Web WG charter | CHANGED | Deliverable now named "Site Capabilities for Agents" with WebMCP as initial input; refinement until about 10 Nov. Ilya Grigorik (Shopify) on strategy #576, 26 Oct: "Shopify deploys WebMCP across millions of storefronts" | https://github.com/w3c/strategy/issues/576 |
| 21 | Old numeric citations "[4,7]", "[26,27]", "[18,19]" | FIXED | Converted to book-unique footnotes `[^ch04-N]` (34 notes) | — |
| 22 | Listing 4.1 `fjord-table/search-availability.js` | OK | Byte-identical to the demo file; label in house style format | demos-new/fjord-table/search-availability.js |
| 23 | Listing 4.2 in-page agent | CHANGED | Now has a home: `fjord-table/dev/in-page-agent.js` (new file, listing verbatim) | demos-new/fjord-table/dev/in-page-agent.js |
| 24 | Fjord Table tests | OK | `npm test`, `npm run test:chrome` and `npm run typecheck` pass on Chromium 156.0.8078.4 (2 Nov) | demos-new/fjord-table |
| 25 | Figure 4.1 | REDRAWN | Same content, APM palette, SVG source in figures/src/figure-4-1.svg | — |

### Chapter 5: Registering Tools with `document.modelContext`


File: `book/manuscript/05-registering-tools.md` (2 November 2026). Checked against the shared validation notes and primary sources read on 2 November 2026: the spec (Draft CG Report, 27 October 2026, full HTML, every quoted sentence searched in the text), the explainer README and continuations explainer on `main`, the GitHub API for each cited issue and pull request, Chrome for Developers pages (dates in the notes), npm for webmcp-types. Browser behaviour was re-observed with the chapter's probe (`chapters/05-registering-tools`, `npm run probe:chrome`) in Chromium 156.0.8078.4 on 2 November 2026. Listings were compared byte for byte with `demos-new/fjord-table/`.

#### Chapter 5: Registering Tools

| # | Claim / API / listing (short quote, old section) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph: "WebMCP tool declaration should be clear, without a need for developers or agents to look at outputs and retry." | OK | Still on the best-practices page (updated 30 Oct, byline Klepper, Salnikov, Beaufort) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 2 | "checked against the 15 October 2026 draft" | CHANGED | 27 October 2026 draft; text states the IDL is identical to 15 Oct (diffed) | https://webmachinelearning.github.io/webmcp/#idl-index |
| 3 | Listing 5.2 IDL excerpt | OK | Matches the 27 Oct IDL index verbatim | https://webmachinelearning.github.io/webmcp/#idl-index |
| 4 | Events `toolchange`, `toolactivated`, `toolcancel` | OK | Unchanged (§4.3) | https://webmachinelearning.github.io/webmcp/#events |
| 5 | `provideContext()`/`clearContext()` removed by PR #132, 5 Mar 2026 (issue #101) | OK | Unchanged | https://github.com/webmachinelearning/webmcp/issues/101 |
| 6 | Move to `Document`: PR #177 (19 May), PR #184 (27 May), issue #173 | OK | Unchanged | https://github.com/webmachinelearning/webmcp/issues/173 |
| 7 | `[SecureContext]` on attribute and interface | OK | Unchanged | https://webmachinelearning.github.io/webmcp/#idl-index |
| 8 | Permissions Policy feature "tools", default `'self'`, `allow="tools"` | OK | Unchanged (§4.4, Chrome overview page) | https://webmachinelearning.github.io/webmcp/#permissions-policy |
| 9 | registerTool rejects with `InvalidStateError` (not fully active, bad/duplicate name, empty description), `NotAllowedError` (policy) | OK | Unchanged | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool |
| 10 | Name rule 1–128 chars `[A-Za-z0-9_.-]` | OK | Unchanged; matches MCP 2026-07-28 SHOULD text | https://modelcontextprotocol.io/specification/2026-07-28/server/tools |
| 11 | Duplicate check twice, PR #347 (merged 15 Oct) | OK | Unchanged | https://github.com/webmachinelearning/webmcp/pull/347 |
| 12 | Renderer crash on re-registration during `toJSON()` (crbug 573722078) | OK, re-observed | Probe on 2 Nov still shows the renderer crash in 156.0.8078.4; text says "it still did on 2 November 2026" | https://issues.chromium.org/issues/573722078 |
| 13 | Title "to reference the tool in the user interface"; empty string when absent (#224 open) | OK | Unchanged | https://github.com/webmachinelearning/webmcp/issues/224 |
| 14 | Best-practices quotes on descriptions (positive capability statement, calendar example) | OK + NEW | Unchanged quotes; author disclosure added ("I'm one of its co-authors") | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 15 | Table 5.4 character budgets (WebMCP tool security) | OK | Page last updated 1 Sep, unchanged | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 16 | Schema stringified, not validated; calls not validated (DataError only for non-object) | OK, re-observed | Unchanged; probe confirms on 2 Nov | https://webmachinelearning.github.io/webmcp/#invoke-the-execute-callback |
| 17 | Imperative API: registration "requires a name, description, and input schema" | OK | Quote present on the 16 Oct page; Chromium still registers without one (probe) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 18 | Issue #92 "Who owns the validation layer?" | CHANGED | Adds Beaufort (14 Oct, optional schemas with spec defaults), Samuel Dallstream (16 Oct, argue for required; editor from 20 Oct per PR #352), Johann Hofmann (30 Oct, quoted: "Full support from security for requiring and validating these schemas in the spec."). WG resolution 5 Mar and PR #289 closed 1 Oct unchanged | https://github.com/webmachinelearning/webmcp/issues/92 |
| 19 | Over-parameterization, §6.3.3 | OK | Unchanged | https://webmachinelearning.github.io/webmcp/#privacy-leakage-over-parameterization |
| 20 | Build-tools quote on short-lived private grants | OK + NEW | Quote present on the 30 Oct page; byline Bandarra and Salnikov, disclosed ("which I co-wrote") | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 21 | `executeTool()` with no input gives `{}` (PR #324, 29 Sep) | OK | Unchanged | https://github.com/webmachinelearning/webmcp/pull/324 |
| 22 | "Only resolve a tool execution with success when the output matches the application state." | NEW | From the 30 Oct best-practices update ("Enforce architectural constraints"); new subsection "Resolve when the page agrees" | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 23 | Results serialized with Infra "serialize a JavaScript value to a JSON string" | OK | Unchanged | https://infra.spec.whatwg.org/#serialize-a-javascript-value-to-a-json-string |
| 24 | Table 5.5 return values, Chromium column | OK, re-observed; caption date changed | Caption now "per the 27 October 2026 draft"; every Chromium cell re-observed on 2 Nov with identical results | probe output, chapters/05-registering-tools |
| 25 | "the four-character string `undefined`" | FIXED (error in v1) | "nine-character string" — `undefined` has nine characters | — |
| 26 | Issue #361 (string results and `undefined`) | NEW | Beaufort, 26 Oct: "The WPT assertions are wrong, and so is Chrome."; strings should resolve JSON-encoded (`'"hi"'`); proposes `undefined` → `null` → `"null"`; Chromium CL 8657321 started. Text marks it as a proposal, not in the draft | https://github.com/webmachinelearning/webmcp/issues/361 |
| 27 | Platform failure names (PR #339, 8 Oct): NotFoundError, DataError, OperationError, AbortError; Chromium still UnknownError | OK, re-observed | Unchanged | https://github.com/webmachinelearning/webmcp/pull/339 |
| 28 | outputSchema: issue #9, PR #254 open | OK | PR #254 still open (updated 26 Oct); silently ignored in Chromium (probe) | https://github.com/webmachinelearning/webmcp/pull/254 |
| 29 | Continuation tokens explainer (PR #327, 2 Oct); options carry only `signal` | OK, re-observed | Unchanged | https://github.com/webmachinelearning/webmcp/blob/main/continuations-explainer.md |
| 30 | `executeTool()` null after navigation (PR #336 closed 7 Oct) | OK | Unchanged | https://github.com/webmachinelearning/webmcp/pull/336 |
| 31 | registerTool resolves `undefined` (#234 open); PR #348 `Tool` interface | OK + NEW | #234 open; PR #348 (opened 15 Oct, open) added as the possible change | https://github.com/webmachinelearning/webmcp/pull/348 |
| 32 | AbortSignal unregistration: PR #147 (26 Mar), PR #202 (17 Jun); in-flight calls not cancelled; Chrome 153 note | OK | Unchanged | https://webmachinelearning.github.io/webmcp/#model-context-unregister-a-tool |
| 33 | "Establish explicit commit points", "if you receive a later abort signal, it's possible the change was not cancelled and still completed." | NEW | From the 30 Oct best-practices update | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 34 | "Register tools all at once … Roll back the whole batch on failure instead of leaving half a workflow callable." | NEW | From the 30 Oct best-practices update; applied to view-owned tool groups | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 35 | Explainer re-registration guidance; #167 closed 29 Sep; #255 open | OK | Unchanged | https://github.com/webmachinelearning/webmcp#best-practices |
| 36 | #158 rename `execute` → `run` open | OK | Unchanged | https://github.com/webmachinelearning/webmcp/issues/158 |
| 37 | webmcp-types 0.1.10, TS ≥ 5.0, optional `document.modelContext`, schema-inferred input | OK | Still latest on 2 Nov; Listing 5.6 type-checks (`npm run typecheck`, TS 5.9) | https://www.npmjs.com/package/webmcp-types |
| 38 | DevTools WebMCP pane | OK | Unchanged | https://developer.chrome.com/docs/devtools/application/webmcp |
| 39 | Listing 5.1 | OK (annotated) | Listing 4.1 with ①–⑥ markers added, label says so; code otherwise identical to search-availability.js | demos-new/fjord-table/search-availability.js |
| 40 | Listings 5.3–5.6 (agent-tools.js, booking-tools.js, booking-view.js, typed/agent-tools.ts) | OK | Byte-identical excerpts of the demo files; labels converted to house style format | demos-new/fjord-table/ |
| 41 | Figures 5.1, 5.2 | REDRAWN | Same content in the APM palette; title removed from inside Figure 5.1 | — |

### Chapter 6: Annotations, Lifecycle and Errors


File: `book/manuscript/06-annotations-lifecycle-errors.md`. 2 November 2026. Sources read this session: spec draft dated 27 October 2026 (fetched 2 Nov), Chrome docs imperative-api (last updated 16 Oct), best-practices (30 Oct), build-tools (30 Oct), secure-tools (1 Sep), overview (7 Oct), the webmcp README, GitHub issue/PR states via the API on 2 Nov, the shared validation notes v1. Line numbers refer to the Oct 15 file (`book/manuscript/06-…` before this rewrite, same text as `orig/`).

#### Chapter 6: Annotations, Lifecycle and Errors

| # | Claim / API / listing (old) | Status | Now | Source URL |
|---|---|---|---|---|
| 1 | “checked against the WebMCP Draft Community Group Report dated 15 October 2026” (intro) | CHANGED | Checked against the 27 Oct 2026 draft; text says the API surface covered here is unchanged between the drafts | https://webmachinelearning.github.io/webmcp/ ; the shared validation notes–1.2 |
| 2 | Listing 6.1 `ToolAnnotations` IDL (4 booleans, default false) | OK | Same IDL, label dated 27 Oct 2026 | https://webmachinelearning.github.io/webmcp/#idl-index |
| 3 | Spec one-line meanings of the four hints (quotes) | OK | Quotes verified verbatim in 27 Oct draft | https://webmachinelearning.github.io/webmcp/#dictdef-toolannotations |
| 4 | Spec §6.4.4 / §6.4.5 quotes (“sanitize the payload…”, “selectively enforce…”) | OK | Verified | https://webmachinelearning.github.io/webmcp/#mitigation-untrusted-annotation |
| 5 | Chrome imperative quotes (“help agents and browsers understand…”, “allows agents and browsers to enforce…”, “heightened security handling…”, “external web data”, deleting data, `debugging` from Chrome 156) | OK | Verified on page last updated 16 Oct 2026 (footnote date corrected from 21 Sep) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 6 | (new) Spec now says a malicious site “can omit or misrepresent those hints” and agent security is primarily the agent’s responsibility | ADDED | New paragraph + footnote ch06-40 (§6.2, PR #334 merged 20 Oct) | https://webmachinelearning.github.io/webmcp/#agent-baseline-capabilities ; https://github.com/webmachinelearning/webmcp/pull/334 |
| 7 | (new) Chrome build-tools: “Enforcement belongs in your application logic…”, separate raw input, bind approval to exact plan, idempotency key | ADDED | Quoted in annotations, read-only tools, checkout, cancellation sections (ch06-38) | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 8 | Unknown annotation members dropped, `getTools()` omits `annotations` when none given (observed) | OK | Re-observed 2 Nov 2026 (`annotationsWhenOmitted: undefined`) | demos ch06 tests/results/chromium-observations.json |
| 9 | (new) “a missing annotations member = all false” is not an assurance — open PR #358 | ADDED | Mentioned, open | https://github.com/webmachinelearning/webmcp/pull/358 |
| 10 | Secure-tools quotes (“on tools that don’t change state…”, “set consequentialHint: true so…”) | OK | Verified. Page title corrected to “WebMCP tool security” (old footnote said “Build secure WebMCP tools”) | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 11 | Issue #291 closed 4 Sep, consequentialHint added the day before | OK | Unchanged | https://github.com/webmachinelearning/webmcp/issues/291 |
| 12 | Issue #331 “still open” | OK (re-dated) | Open as of 2 Nov 2026, latest comment 20 Oct argues for separate sensitiveHint | https://github.com/webmachinelearning/webmcp/issues/331 |
| 13 | `debugging` history (PR #253, CG resolution 20 Aug), Chrome 156 | OK | Unchanged | https://github.com/webmachinelearning/webmcp/pull/253 |
| 14 | Listing 6.2 product-tools.js | OK | Byte-identical to demo file (diffed) | demos ch06 trailhead/product-tools.js |
| 15 | Listing 6.3 checkout-tool.js | OK | Byte-identical. Text adds build-tools “bind approval to a short-lived private grant…” | demos ch06 trailhead/checkout-tool.js |
| 16 | Still-in-flux list of proposals #53, #198, #110, #331 “open on 15 October” | CHANGED | All still open on 2 Nov. Added PR #355 (openWorldHint, open) and PR #358 (open) | GitHub API 2 Nov 2026 |
| 17 | Listing 6.4 debug-tools.js | OK | Byte-identical | demos ch06 |
| 18 | Lifecycle steps 1–7 (spec algorithms) | OK | Unchanged. Step 1 adds Chrome note “JSON stringified input arguments are deprecated from Chrome 155” and step 6 says “JSON serialization” | https://webmachinelearning.github.io/webmcp/#invoke-the-execute-callback ; imperative-api |
| 19 | Chromium fires toolactivated after execute; issue #332 open | OK (re-dated) | Re-observed 2 Nov. #332 open, last comment 28 Oct, no decision | https://github.com/webmachinelearning/webmcp/issues/332 |
| 20 | Concurrent calls interleave; issue #47 open | OK | Re-observed. #47 open | https://github.com/webmachinelearning/webmcp/issues/47 |
| 21 | Events toolactivated/toolcancel with toolName; PR #146 | OK | Unchanged | https://webmachinelearning.github.io/webmcp/#events |
| 22 | Listing 6.5 tool-lifecycle.js; issue #85 open | OK | Byte-identical. #85 open | https://github.com/webmachinelearning/webmcp/issues/85 |
| 23 | Navigation mid-call: draft AbortError, Chrome docs `null`, Chromium UnknownError | OK | Chrome page (16 Oct) still says “or null when a navigation is triggered”. Re-observed UnknownError 2 Nov | imperative-api ; https://webmachinelearning.github.io/webmcp/#pending-tool-executions |
| 24 | Issue #135 open, CG resolution 16 Apr | OK | Open as of 2 Nov | https://github.com/webmachinelearning/webmcp/issues/135 |
| 25 | Caller unload → toolcancel at target (observed) | OK | Re-observed | demos ch06 probe |
| 26 | Two signals, abort steps (spec) and observed behaviour list | OK | Re-observed | https://webmachinelearning.github.io/webmcp/#cancel-a-pending-tool-execution |
| 27 | Chrome cancellation quote (“to long-running asynchronous tasks…”) | OK | Verified on 16 Oct page | imperative-api |
| 28 | Issue #344 note; “The 15 October draft doesn’t yet contain that note” | CHANGED (date) | “The 27 October draft doesn’t contain that note” (verified: phrase absent from current spec) | https://webmachinelearning.github.io/webmcp/ ; https://github.com/webmachinelearning/webmcp/issues/344 |
| 29 | (new) Best-practices “Establish explicit commit points” quote | ADDED | Quoted, tied to `throwIfAborted()` | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 30 | #299 closed 25 Sep; draft “will never observe the tool’s natural resolution/rejection” | OK | Verified in 27 Oct draft | https://webmachinelearning.github.io/webmcp/#cancel-a-pending-tool-execution |
| 31 | Unregistering doesn’t cancel (spec note quote, Chrome 153 quote, #218) | OK | Verified verbatim | https://webmachinelearning.github.io/webmcp/#model-context-unregister-a-tool ; imperative-api |
| 32 | Listing 6.6 compare-tool.js; DOM AbortSignal.any/timeout | OK | Byte-identical | demos ch06 ; https://dom.spec.whatwg.org/#interface-AbortSignal |
| 33 | Table 6.1 platform errors (draft names vs Chromium 156) | OK (re-dated) | Re-observed 2 Nov. Header now “27 October 2026 draft” | https://webmachinelearning.github.io/webmcp/#tool-execution-error |
| 34 | `undefined` result: draft OperationError, Chromium "undefined" | CHANGED (context) | Table row and a new note: issue #361 (open), editor François Beaufort 26 Oct: strings should be JSON-quoted (“The WPT assertions are wrong, and so is Chrome”), proposes undefined → "null". Rule 3 updated | https://github.com/webmachinelearning/webmcp/issues/361 |
| 35 | PR #339 (UnknownError → specific names, 8 Oct) | OK | Unchanged | https://github.com/webmachinelearning/webmcp/pull/339 |
| 36 | Error messages and console text (observed) | OK | Re-observed | demos ch06 |
| 37 | Best-practices “Validate strictly in code, loosely in schema … Add descriptive errors…” | OK | Verified on 30 Oct page | best-practices |
| 38 | Listing 6.7 cart-tools.js | OK | Byte-identical. Text adds best-practices “Wait for the UI” quote | demos ch06 |
| 39 | toolchange semantics, “cannot be relied upon”, README quote, Chrome “Frames can listen…” | OK | Verified | https://webmachinelearning.github.io/webmcp/#notify-documents-of-a-tool-change ; README ; imperative-api |
| 40 | toolchange counts 3+3 (observed) | OK | Re-observed | demos ch06 |
| 41 | Best-practices “Register tools when…” and “static registration should be the default” | OK | Verified | best-practices |
| 42 | (new) Best-practices “Register tools all at once… Roll back the whole batch on failure” | ADDED | Quoted. Demo `trailhead/app.js` changed to abort the shared controller when a registration fails | best-practices |
| 43 | Listing 6.8 tool-sync.js | OK | Byte-identical | demos ch06 |
| 44 | Issue #312 open | OK | Open as of 2 Nov. Added related issue #328 (open) | https://github.com/webmachinelearning/webmcp/issues/312 ; https://github.com/webmachinelearning/webmcp/issues/328 |
| 45 | Demo test counts “31 scenarios, 73 checks” | OK | Re-run 2 Nov 2026: 73 passed, 0 failed | demos ch06 tests/results/summary.json |
| 46 | Chromium version statement (156.0.8078.4) | CHANGED (context) | Text adds: Chrome 156 stable since 20 Oct 2026, tested build is an early 156 build, 157+ untested | the shared validation notes (chromiumdash) |
| 47 | Best-practices footnote had no author/date | CHANGED | Footnote names authors Alexandra Klepper, Maxim Salnikov, François Beaufort, last updated 30 Oct 2026. Text mentions Maxim co-authored it (and build-tools) | the shared validation notes ; AUTHOR-the shared validation notes |

UNVERIFIED: behaviour of Chrome 157+ (no newer browser on the box). Who wrote Chrome’s Imperative API wording is not relevant and not checked. The exact Chromium change for #361 (crrev 8657321) was not inspected.

#### Demo changes
- `chapters/06-annotations-lifecycle-errors/trailhead/app.js` (support file, not printed): on a failed registration the page now aborts the shared `AbortController`, rolling back the batch (Chrome best practices, 30 Oct). No listing changed.
- Tests: `npm install --no-save playwright@1.64.1` + `node tests/run-tests.mjs` with cached Chromium 156.0.8078.4: 73 passed, 0 failed (2 Nov 2026, before and after the app.js change — see README). node_modules deleted.
- README status lines updated.

#### Figures
- figure-6-1, figure-6-2, figure-6-3 redrawn as SVG in figures/src (APM palette), same meaning. No content change needed from the shared validation notes (annotations, lifecycle and cancellation unchanged). Figure 6.1’s legend no longer uses a card row.

### Chapter 7: Frames, Origins and Page-Embedded Agents


File: `book/manuscript/07-frames-origins-agents.md`. 2 November 2026. Same sources as the Chapter 6 file, plus issues #236, #227, #317, #74, #348, #349 and their comments since 15 Oct (GitHub API, 2 Nov).

#### Chapter 7: Frames, Origins and Page-Embedded Agents

| # | Claim / API / listing (old) | Status | Now | Source URL |
|---|---|---|---|---|
| 1 | “checked against … dated 15 October 2026”, three editors (fn 3) | CHANGED | 27 Oct 2026 draft, four editors (Samuel Dallstream added 20 Oct) | https://webmachinelearning.github.io/webmcp/ ; https://github.com/webmachinelearning/webmcp/pull/352 |
| 2 | “The tests … all 29 of them pass” (intro) vs “npm test runs 30 checks” (later) | CHANGED (internal inconsistency fixed) | 30 checks, all passed 15 Oct and 2 Nov 2026 | demos ch07 test run 2 Nov |
| 3 | Browser agent observation, origin note quote, “does not run JavaScript on the page” | OK | Verified | https://webmachinelearning.github.io/webmcp/#observations |
| 4 | “and possibly living in iframes” | OK | Verified | https://webmachinelearning.github.io/webmcp/#model-context-container |
| 5 | `tools` policy, default `'self'`, NotAllowedError, getTools skips disallowed docs | OK | Verified | https://webmachinelearning.github.io/webmcp/#permissions-policy |
| 6 | Chrome “Tool registration is disabled by default in cross-origin iframes…” | OK | Verified on 16 Oct page | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 7 | Listings 7.1, 7.2 | OK | Byte-identical (diffed) | demos ch07 |
| 8 | MDN allowlist / `src` default | OK (not re-fetched) | Unchanged, read 14 Oct | MDN Permissions-Policy |
| 9 | Spec §6.4.1 `tools=()` quotes | OK | Verified | https://webmachinelearning.github.io/webmcp/#mitigation-disable-permissions-policy |
| 10 | Table 7.1 (tested) | OK | Re-tested 2 Nov | demos ch07 |
| 11 | Issue #317 open (split policy) | OK (re-dated) + ADDED | Open 2 Nov. Added #236 post-TPAC comments (VanderSloot: policy should mean roll-up into tool list, Hofmann: “I think we need to add a second permissions policy”, 30 Oct) | https://github.com/webmachinelearning/webmcp/issues/317 ; https://github.com/webmachinelearning/webmcp/issues/236 |
| 12 | Chrome secure-tools “By default, other websites or cross-origin iframes can’t observe…” | OK | Verified. Page title corrected to “WebMCP tool security” (old footnote: “Secure your WebMCP tools”) | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 13 | exposedTo definition quote | OK | Verified | https://webmachinelearning.github.io/webmcp/#model-context-register-tool-options |
| 14 | Listing 7.3 widget-tools.js | OK | Byte-identical | demos ch07 |
| 15 | SecurityError for non-secure origins (spec + observed message) | OK | Re-tested | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool |
| 16 | (new) no wildcard in exposedTo, editor comment that `*` may be reconsidered | ADDED | Khushal Sagar, #317, 26 Oct | https://github.com/webmachinelearning/webmcp/issues/317 |
| 17 | fromOrigins definition, exposure algorithm, Chrome “Even if a tool is exposed…” | OK | Verified | https://webmachinelearning.github.io/webmcp/#model-context-get-tool-options ; imperative-api |
| 18 | Quote from PR #326 “prevents unsolicited tool-list pollution and unauthorized cross-origin tool invocation” | CHANGED | Now quotes the merged spec text: “prevents both unauthorized cross-origin actuation and unsolicited tool-list pollution” | https://webmachinelearning.github.io/webmcp/#in-page-cross-origin-exposure |
| 19 | “Still in flux: the security section is still a TODO” (§6.3.4, PR #326 open, reviewer asked for retitle) | CHANGED | Replaced by a subsection “What the specification now says about it”: §6.3.4 “Interaction with the Same-Origin Policy” (PR #326 merged 27 Oct): rationale, three gates, “Why Two-Sided Opt-In Matters”, residual risks. Old anchor #violation-same-origin-boundaries no longer exists, footnote points to #interaction-with-same-origin-policy | https://webmachinelearning.github.io/webmcp/#interaction-with-same-origin-policy ; https://github.com/webmachinelearning/webmcp/pull/326 |
| 20 | toolchange driven by exposedTo, timing note | OK | Verified | https://webmachinelearning.github.io/webmcp/#notify-documents-of-a-tool-change |
| 21 | Listing 7.4 IDL excerpt (15 Oct) | OK (re-dated) | IDL unchanged, label dated 27 Oct | https://webmachinelearning.github.io/webmcp/#idl-index |
| 22 | RegisteredTool members, window/origin, origin quote | OK | Verified | https://webmachinelearning.github.io/webmcp/#registered-tool |
| 23 | Discovery limited to top-level frame tree, issue #227 open | OK + ADDED | #227 open, now carries the ModelContextClient proposal (26 Oct), described in new subsection “Where the consumer API may be heading” as a proposal only | https://github.com/webmachinelearning/webmcp/issues/227 |
| 24 | Sorted by name (tested) | OK | Re-tested | demos ch07 |
| 25 | Listing 7.5 discover.js | OK | Byte-identical | demos ch07 |
| 26 | executeTool quotes (“on the document it was registered on”, “the stringified result…”) | OK | Verified (note: #361 proposes rewording to “JSON serialization”, open) | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-executetool |
| 27 | Dictionary not a handle, forged dict → NotFoundError, note quotes, Chromium UnknownError | OK | Verified, re-tested | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-executetool |
| 28 | (new) PR #348 Tool interface, #349 opaque origins | ADDED | Still-in-flux box (both open) | https://github.com/webmachinelearning/webmcp/pull/348 |
| 29 | Only error name crosses (quote + hunter2 test) | OK | Verified, re-tested | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-executetool |
| 30 | Cancellation crosses origins (tested) | OK | Re-tested | https://webmachinelearning.github.io/webmcp/#pending-tool-executions |
| 31 | Listing 7.6 run-tool.js | OK | Byte-identical | demos ch07 |
| 32 | Table 7.3 “15 October draft” | OK (re-dated) | “27 October 2026 draft”, re-tested | https://webmachinelearning.github.io/webmcp/#supporting-concepts |
| 33 | Chrome “null when a navigation is triggered” | OK | Still on 16 Oct page | imperative-api |
| 34 | Listing 7.7 agent-loop.js, Prompt API tool use flag via example extension | OK | Byte-identical. Extension README re-read | https://github.com/GoogleChromeLabs/webmcp-extension |
| 35 | Explainer quote “can be invoked by AI agents, including those … running in extensions” | OK | Verified in README | https://github.com/webmachinelearning/webmcp |
| 36 | Extension README quote (“reads document.modelContext.getTools() and listens for ontoolchange…”) | OK | Verified | webmcp-extension README |
| 37 | (new) Chrome secure-tools “Chrome Extensions can query and execute WebMCP tools using content scripts.” | ADDED | Quoted as support for the content-script approach | secure-tools |
| 38 | Content scripts in isolated world can call document.modelContext (tested) | OK + CONTEXT | Re-tested 2 Nov with the testing flag. Added Kenneth Christiansen’s 20 Oct comment in #74 that his extension injects into the page world, flagged as an unexplained discrepancy (origin-trial pages untested) | https://github.com/webmachinelearning/webmcp/issues/74 |
| 39 | Listings 7.8–7.10 | OK | Byte-identical | demos ch07 |
| 40 | Chrome “can manipulate the page by running custom JavaScript, even without WebMCP” | OK | Verified | secure-tools |
| 41 | Issue #74 open on 15 Oct | OK (re-dated) | Open 2 Nov, TPAC breakout mentioned | https://github.com/webmachinelearning/webmcp/issues/74 |
| 42 | #236 “open and last updated on 24 September” | CHANGED | Open, active again after TPAC (comments 25 and 30 Oct) | https://github.com/webmachinelearning/webmcp/issues/236 |
| 43 | Summary bullet “Still open: … the security section on cross-origin exposure (PR #326)” | CHANGED | Removed (merged). New bullet on §6.3.4. Open list now #74, #227, #317, #236, #348 | GitHub API |
| 44 | Demo description (ports, mock, 30 checks breakdown) | OK | 11 syntax + 1 mock + 17 Chromium + 1 extension = 30, passed 2 Nov | demos ch07 |
| 45 | Semicolons in prose (e.g. “isn’t a document; only…”) | STYLE | Removed (house style: none in prose) | — |

UNVERIFIED: Chrome 157+ behaviour. Whether isolated-world content scripts reach `document.modelContext` on origin-trial pages without the testing flag. Mozilla/Google affiliations of commenters are as listed in the shared validation notes (not re-checked on profiles).

#### Demo changes
- No listing or code change needed (IDL and algorithms unchanged).
- Tests: `npm install --no-save playwright@1.64.1` + `node tests/run-tests.mjs`, Chromium 156.0.8078.4: 30/30 passed (2 Nov 2026). node_modules deleted.
- README status lines updated.

#### Figures
- figure-7-1, figure-7-2 redrawn as SVG in figures/src (APM palette), same meaning. Figure 7.1 now cites §6.3.4 (two-sided opt-in) in its gate legend.

### Chapter 8: The Declarative API: Forms as Tools


File: `book/manuscript/08-declarative-api.md`. Checked 2 November 2026 by chapter the reviewer against the shared validation notes and the primary sources below (all fetched 2 Nov 2026). Line numbers are from the Oct 15 file (`orig` text as restructured in book/manuscript before the rewrite).

#### Chapter 8: The Declarative API: Forms as Tools

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Declarative API removed from the spec "On 8 October 2026 ... six days before this chapter was written" (l.15) | CHANGED (framing) | Removal date kept (8 Oct 2026, PR #338 merged 2026-10-08T11:26Z, verified via GitHub API). "Six days before" dropped; text says it was still out of the spec when re-checked on 2 Nov 2026. Note: the shared validation notes §1.1 says PR #338 merged 2026-10-13 — that is wrong, the API returns merged_at 2026-10-08 (13 Oct is the date of the PR author's comment). | https://github.com/webmachinelearning/webmcp/pull/338 |
| 2 | "The current draft, dated 15 October 2026, defines only registerTool(), getTools(), executeTool() and the tool events" (l.21) | CHANGED | Draft dated 27 October 2026, IDL unchanged (same three methods + three events). | https://webmachinelearning.github.io/webmcp/ ; the shared validation notes–1.2 |
| 3 | PR #338 deleted the placeholder section ("entirely a TODO") and rewrote README: "is being explored separately", "not part of the specification at this time" (l.21) | OK | Kept; "entirely a TODO" paraphrased as "never been more than a to-do note" so the manuscript lint (TODO/TBD) passes. README quotes re-verified verbatim on raw README 2 Nov. | https://github.com/webmachinelearning/webmcp/blob/main/README.md |
| 4 | Chrome "Declarative API" page last updated 25 Sep 2026 documents every attribute/event/pseudo-class (l.23) | OK | Unchanged; page re-read 2 Nov (still "Last updated: September 25, 2026"). | https://developer.chrome.com/docs/ai/webmcp/declarative-api |
| 5 | PR author comment 13 Oct: "The Chrome team plans to ship the imperative API **first**, with the declarative API following shortly after." (l.23) | OK | Kept verbatim; it is still the only comment on #338 (checked 2 Nov). | https://github.com/webmachinelearning/webmcp/pull/338 |
| 6 | Observations from "Chromium 156.0.8078.4 ... run on 14 October 2026" (l.15) | OK + re-run | Kept; full suite re-run 2 Nov 2026 on the same build: 17 passed, 0 failed. Added: Chrome 156 became Stable 20 Oct 2026 (current Stable 156.0.8078.80, a later build than tested), 157 stable 3 Nov. | chromiumdash fetch_milestone_schedule?mstone=156/157 ; https://chromiumdash.appspot.com/schedule |
| 7 | Issue #22 (Sep 2025), PR #26, PR #76 merged 9 Mar 2026 (l.29) | OK | Unchanged history. | https://github.com/webmachinelearning/webmcp/issues/22 |
| 8 | Explainer quotes: "take some effort to rewrite with an agent invoker in mind", "Much of a site's functionality ..." (l.1, l.31) | OK | Re-verified verbatim in the current explainer. | https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md |
| 9 | WebKit objection paragraph (l.33) | OK + EXTENDED | Kept, and added the W3C TAG early comment of 26 Oct 2026 (not a resolution): quotes "creates an agent-only description of a page's functionality that might be unreachable by human users or screen readers" and "ask to fully work out the declarative version before shipping the imperative one" — verified verbatim on the comment. | https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845 |
| 10 | Explainer: schema-synthesis algorithms "are TBD"; "Chromium is implementing a loose version of this ..." (l.35) | OK (reworded) | "TBD" paraphrased ("not decided yet" / "still to be determined") for the lint; the "loose version" sentence kept verbatim (re-verified). | explainer, as above |
| 11 | README: "Even if a declarative API is added, it would complement rather than replace the imperative API." (l.35) | OK | Verbatim, re-verified. | README, as above |
| 12 | Listings 8.1, 8.2, 8.4 (HTML forms) | OK | Byte-identical to `listings/listing-8-1-...`, `-8-2-...`, `-8-4-...`; test "listings 8.2 and 8.4 appear byte-for-byte in index.html" passed 2 Nov. Label lines converted to the house style format. | demos-new/chapters/08-declarative-api |
| 13 | `toolname` naming rules; bad/duplicate names silently not registered; `registerTool()` rejects with `InvalidStateError` (l.~85) | OK | Unchanged; spec IDL unchanged; PR #347 (15 Oct) adds another InvalidStateError case for imperative re-registration during serialization (not relevant to forms). | spec; the shared validation notes |
| 14 | Issue #182 (failed declarative registration, `toolerror` idea) open (l.~85) | OK | Still open 2 Nov (GitHub API). Footnote re-dated. | https://github.com/webmachinelearning/webmcp/issues/182 |
| 15 | Chrome guide: removing either attribute unregisters; `tooldescription=""` stays registered (observed) | OK | Guide text re-verified; observation unchanged. | Chrome declarative page |
| 16 | `toolparamdescription` → label → `aria-description` order (l.~95) | OK | Guide text re-verified ("uses the content within the associated <label> ... If there isn't a label, the browser refers to the aria-description"). | Chrome declarative page |
| 17 | Best-practices: manage registration "by adding or removing the tool attributes on a form" (l.~101) | OK | Verbatim on the page (last updated 30 Oct 2026). Byline now lists Maxim Salnikov as co-author — text says "(I'm one of its co-authors)", footnote names the three authors. | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 18 | `toolchange` fires on add/remove of tool forms (observed) | OK | Unchanged. | tests |
| 19 | Empty `title`, undocumented `tooltitle` (observed); early spellings `tool-name` | OK | Unchanged. | tests; #22, #26 |
| 20 | Listing 8.3 synthesized schema | OK | Byte-identical to `listings/listing-8-3-synthesized-schema.json`; test "schema matches Listing 8.3" passed 2 Nov on Chromium 156.0.8078.4. | tests |
| 21 | Table 8.1 control → schema mapping (observed 14 Oct) | OK | Unchanged (one-off probes, not re-run; the Listing 8.3 schema test was re-run). Semicolon inside one cell replaced by full stops. | demos README |
| 22 | JSON Schema `format` vs `pattern` (draft 2020-12) | OK | Unchanged. | https://json-schema.org/draft/2020-12/json-schema-validation |
| 23 | Argument checking for declarative calls; error texts "Input contains a parameter "guests"...", "Invalid value "rooftop"..." | OK | Unchanged; validation test passed 2 Nov. | tests |
| 24 | Life of a call steps 1–6; DevTools Protocol `autosubmit` annotation | OK | CDP `WebMCP` domain re-read 2 Nov: commands enable/disable/invokeTool/cancelInvocation, events toolsAdded/toolsRemoved/toolInvoked/toolResponded, InvocationStatus Completed/Canceled/Error — unchanged. | https://github.com/ChromeDevTools/devtools-protocol/blob/master/json/browser_protocol.json |
| 25 | `toolautosubmit` explainer quotes; Le Petit Bistro demo default | OK | Verbatim in current explainer. | explainer; https://github.com/GoogleChromeLabs/webmcp-tools/tree/main/demos/french-bistro |
| 26 | submit-before-`toolactivated` with autosubmit (observed) | OK | Unchanged. | tests |
| 27 | `SubmitEvent.agentInvoked`, `respondWith(Promise<any>)`, "preventDefault() must be called before" | OK | IDL in explainer unchanged; Chrome guide "serialized and returned to the model as the tool's output" verbatim. | explainer; Chrome page |
| 28 | Listings 8.5, 8.6 (search-form.js, book-form.js) | OK | Byte-identical to the demo files; tests passed 2 Nov (respondWith answer, booking on click, refused value, reset-after-answer). | demos-new |
| 29 | `InvalidStateError` texts for respondWith on human submit / without preventDefault (observed) | OK | Unchanged. | tests |
| 30 | Table 8.2 "string without JSON quotes", "`undefined` → "undefined"" (observed) | OK + NOTE ADDED | Observations kept; added a paragraph on issue #361 (opened 23 Oct): spec JSON-encodes strings, Chrome/WPT don't; spec author (26 Oct): "The WPT assertions are wrong, and so is Chrome."; agrees `undefined` should not reject (proposal maps it to "null"). Text says honestly that I can't tell whether Chromium's declarative path will change with it. | https://github.com/webmachinelearning/webmcp/issues/361 |
| 31 | `UnknownError` everywhere; spec replaced UnknownError on 8 Oct (#339, commit b206dae) | OK | Unchanged; footnote now names PR #339. Sentence "that is the browser lagging the draft" kept (Chapter 5). | https://github.com/webmachinelearning/webmcp/pull/339 |
| 32 | JSON-LD cross-document response; explainer's collapsed proposal; issue #135 open | OK | Collapsed `<details>` text re-verified ("the first `<script type=application/ld+json>` tag ... "); #135 still open 2 Nov. | explainer; https://github.com/webmachinelearning/webmcp/issues/135 |
| 33 | Listing 8.7 results.html; JSON-LD read when parsing ends (observed) | OK | Byte-identical; navigation test passed 2 Nov. | tests |
| 34 | Events moved into spec by PR #245 (17 Sep 2026); `window.ontoolactivated`/`ontoolcancel` "not supported from Chrome 156" | OK | Verbatim on Chrome page; spec §4.3 unchanged. | spec; Chrome page |
| 35 | Listing 8.8 agent-feedback.js | OK | Byte-identical; cancel test passed 2 Nov. | demos-new |
| 36 | Chrome guide vs explainer on `toolcancel` after `reset()`; Chromium follows explainer (observed) | OK | Both sources re-verified (Chrome: "if a user cancels the agentic operation or the reset() method is invoked"; explainer: "does not fire when the site itself cancels the tool"). Reset test passed 2 Nov. | Chrome page; explainer |
| 37 | Callout "The explainer still calls the cancel event `toolcanceled`" (l.~410) | CHANGED | Explainer now says `toolcancel` (PR #350, merged 16 Oct 2026). Callout rewritten; added the explainer's still-open question "fired at `ModelContext` or at the `<form>`". | https://github.com/webmachinelearning/webmcp/pull/350 |
| 38 | Issue #126 closed 24 Sep 2026 after #245 | OK | Unchanged (GitHub API). | https://github.com/webmachinelearning/webmcp/issues/126 |
| 39 | Listing 8.9 tool-styles.css; `@supports selector()`; SyntaxError in plain Chromium (observed) | OK | Byte-identical; "WebMCP CSS inert" test passed 2 Nov. | tests; Selectors 4; css-conditional-4 |
| 40 | Chrome guide "critical to inform users and agents where they're on a page" | OK | Verbatim. | Chrome page |
| 41 | Validation error texts with doubled full stop; custom validity "closed on Mondays" | OK | Unchanged; validation tests passed 2 Nov. | tests |
| 42 | Best practices "validate strictly in code, loosely in schema" | OK | Verbatim on the 30 Oct page. | best-practices |
| 43 | "put the clearest possible constraints in the schema" (l.~470) | CHANGED (wording) | "...into the form" — for a declarative tool the schema is derived from the form, so the form is where the author can act. | — |
| 44 | Listing 8.10 JS-driven form; error text "No submit button was found, but for a form without `toolautosubmit`, there must be a submit button" | OK (formatting fix) | Error text now one clean code span (the old text had broken nested backticks). Test passed 2 Nov. | tests |
| 45 | No annotations or outputSchema for declarative tools | OK + NOTE | Added: no `outputSchema` in the imperative API either as of the 27 Oct draft (open PR #254), pointer to Appendix A. | the shared validation notes, §2 #14 |
| 46 | Table 8.3; "Most real sites will use both" | OK | Unchanged. | — |
| 47 | Testing section: two kinds of agent, CDP domain | OK | Unchanged; sentence on the 2 Nov re-run added. | tests |
| 48 | Footnotes 1–20 | OK / re-dated | Re-checked pages marked "(retrieved November 2026)"; #182/#135 "still open on 2 November 2026"; ch08-5 now the 27 Oct draft; ch08-11 names the three authors and the 30 Oct date; ch08-16 names PR #339. New: ch08-21 (chromiumdash), ch08-22 (TAG comment), ch08-23 (PR #350), ch08-24 (issue #361). | as listed |

#### Demo changes

- `demos-new/chapters/08-declarative-api/`: no code change needed (no API change affects it). README status block updated (re-run date, result).
- Tests: `npm install --no-save playwright@1.64.1` (browsers from the cache, no download), `node tests/run-tests.mjs` on 2 Nov 2026, Chromium 156.0.8078.4: **17 passed, 0 failed**. node_modules deleted afterwards.

#### Figures

- Figure 8.1 and Figure 8.2 redrawn as SVG in the APM figure kit (`figures/src/figure-8-1.svg`, `figure-8-2.svg`), same meaning; no factual change was needed.

### Chapter 9: Your First WebMCP App, End to End


File: `book/manuscript/09-first-webmcp-app.md`. Checked 2 November 2026 by chapter the reviewer against the shared validation notes and the primary sources below (fetched 2 Nov 2026). Demo: `demos-new/chapters/09-first-webmcp-app` (Chromium 156.0.8078.4, Playwright 1.64.1).

#### Chapter 9: Your First WebMCP App, End to End

| # | Claim / API / listing | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph: "WebMCP is available as a Chrome flag for local development." (overview) | OK | Re-verified verbatim on the overview page (last updated 7 Oct 2026). | https://developer.chrome.com/docs/ai/webmcp |
| 2 | Flag chrome://flags/#enable-webmcp-testing, enable + relaunch | OK | Unchanged (overview, 2 Nov). | https://developer.chrome.com/docs/ai/webmcp |
| 3 | Developer trial from Chrome 146 (chromestatus) | OK | Unchanged; chromestatus entry still last updated 28 Sep 2026. | https://chromestatus.com/feature/5117755740913664 |
| 4 | Chrome version context (book pinned to Chromium 156 pre-release era) | CHANGED | Added: Chrome 156 Stable since 20 Oct 2026, WebMCP still off by default (flag or token). New footnote ch09-22 (Chromium Dash). | https://chromiumdash.appspot.com/schedule ; the shared validation notes |
| 5 | Model Context Tool Inspector needs "WebMCP for testing" flag, Chrome 150.0.7861.0+ | OK | Unchanged (the shared validation notes, store listing v1.9.19). | https://github.com/beaufortfrancois/model-context-tool-inspector |
| 6 | Secure context: draft dated 15 Oct 2026 marks modelContext and ModelContext [SecureContext] | CHANGED | Draft date now 27 Oct 2026; [SecureContext] on both unchanged (IDL identical). | https://webmachinelearning.github.io/webmcp/#idl-index |
| 7 | fjord.test insecure origin: isSecureContext false, 'modelContext' in document false | OK (re-run) | Test re-run 2 Nov on Chromium 156.0.8078.4. | companion tests |
| 8 | Table 9.1 console-check results (3 rows) | OK (re-run) | Observed values re-run 2 Nov. | companion tests |
| 9 | OT announced from Chrome 149; trial 149–156 extended to 162; reason quote; third-party tokens | OK | Unchanged (chromestatus 28 Sep; blog 9 Jun). | https://chromestatus.com/feature/5117755740913664 ; https://developer.chrome.com/blog/ai-webmcp-origin-trial |
| 10 | Edge OT expires 30 Mar 2027, subdomain + third-party matching | OK | Unchanged (the shared validation notes). | Edge origin-trials page (fn ch09-7) |
| 11 | Status "Proposed", "Specification being incubated in a Community Group" (dated 14 Oct) | CHANGED (date) | Re-dated to 2 Nov 2026, values unchanged. | chromestatus JSON |
| 12 | Still-in-flux box: "several open pull requests would reshape the imperative API" | OK/EXPANDED | Kept; declarative left the spec on 8 Oct 2026 named; points to Appendix A for the open PRs (#348, #254, #204, #355/#358). | the shared validation notes |
| 13 | Listing 9.2 enable.js (polyfill 6.0.3 pinned, SRI) | OK | Unchanged; npm latest still 6.0.3 (published 14 Oct) on 2 Nov; hash test passes. | https://registry.npmjs.org/@mcp-b/webmcp-polyfill/latest |
| 14 | Polyfill bundle 27 KB download | OK | Unchanged package version, so unchanged size. | npm 6.0.3 |
| 15 | Tools as thin wrappers (Listing 9.3) | OK + NEW CITATION | Added Chrome best-practices "Share the application service" (30 Oct; Maxim co-author). Footnote ch09-23. | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 16 | Listing 9.4 app.js: registerFjordTools({ signal: new AbortController().signal }) | CHANGED (code) | Best practices (30 Oct): "Register tools all at once ... Roll back the whole batch on failure". app.js now keeps the controller and calls tools.abort() in catch. Demo file changed identically; new test 'a refused registration rolls back the whole tool surface' (refuses book_table, expects getTools() = []). | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 17 | Table 9.2 start-up paths (6 rows) | OK + 1 ROW | Re-run 2 Nov; new row for the rollback test (InvalidStateError, no tools left). | companion tests |
| 18 | NotAllowedError under tools=(); default allowlist 'self'; tools=() recommended | OK | Unchanged in 27 Oct draft §4.4 / §6.4.1. | https://webmachinelearning.github.io/webmcp/ |
| 19 | Still-in-flux: Chromium UnknownError vs named exceptions in the draft "since 8 October 2026" | OK | Kept, plus "rolls back" added to the start-up stance. | the shared validation notes (probe) |
| 20 | DevTools WebMCP pane: Available/Invoked tools, statuses, Run tool, replay; DevTools MCP list_webmcp_tools/execute_webmcp_tool, --categoryExperimentalWebmcp | OK | Page footer still 12 May 2026. | https://developer.chrome.com/docs/devtools/application/webmcp |
| 21 | Inspector: side panel, table, execute JSON args; Gemini with API key quote | OK | Overview quote unchanged. | https://developer.chrome.com/docs/ai/webmcp |
| 22 | Example extension: back ends (AI SDK server: Google/OpenAI/Anthropic/Ollama; Prompt API needs #prompt-api-tool-use); annotation behavior; 8,000 chars; 100 tool uses, check-in after 10; "hints ... not guarantees" | OK | README re-read 2 Nov. | https://github.com/GoogleChromeLabs/webmcp-extension |
| 23 | "I did not run the two extensions" | OK | Honest scope statement kept. | n/a |
| 24 | Test Agent uses getTools()/executeTool(); Chromium needs the object from getTools() | OK + NOTE | Added PR #348 (Tool interface, open) note: harness re-looks up each time, so it adapts. Footnote ch09-24. | https://github.com/webmachinelearning/webmcp/pull/348 |
| 25 | Chromium returns plain strings as-is (parse fallback) | OK + NEW | Added issue #361 (opened 23 Oct): spec author 26 Oct "The WPT assertions are wrong, and so is Chrome." Footnote ch09-25. | https://github.com/webmachinelearning/webmcp/issues/361 |
| 26 | Page Agent demo uses getTools()/executeTool() with Gemini | OK | Unchanged. | https://github.com/GoogleChromeLabs/webmcp-tools/tree/main/demos/page-agent |
| 27 | Testing advice | NEW | Build-tools "Pin versions" quote (30 Oct; Maxim co-author). The suite prints the Chromium version and the README records versions. Footnote ch09-26. | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 28 | Prompt API page: web from Chrome 148, availability/create/prompt, responseConstraint; "last updated 26 August 2026" | CHANGED (date) | Page now last updated 21 Oct 2026, the facts used unchanged. Footnote re-dated. | https://developer.chrome.com/docs/ai/prompt-api |
| 29 | LanguageModel availability() "downloadable" in Playwright Chromium 156 | OK (re-run) | Observed again 2 Nov. | companion tests |
| 30 | CDP WebMCP domain (enable, invokeTool, toolsAdded/Removed, toolResponded) | OK | Unchanged. | https://chromedevtools.github.io/devtools-protocol/tot/WebMCP/ |
| 31 | MCP-B docs scope; three packages at 6.0.3 on 14 Oct | OK + RE-CHECK | Still latest 6.0.3 on 2 Nov. | https://registry.npmjs.org/@mcp-b/global/latest |
| 32 | Choose a runtime order; polyfill packages CG polyfill pinned + declarative layer; baseline Chrome 126/Firefox 126/Safari 18; no argument validation | OK | Docs re-read 2 Nov. | https://docs.mcp-b.ai/packages/webmcp-polyfill/reference |
| 33 | Google standalone polyfill demos/shared/webmcp-polyfill.js | OK | Unchanged. | https://github.com/GoogleChromeLabs/webmcp-tools |
| 34 | Relay: embed.js iframe, localhost WebSocket, stdio; --widget-origin; port 9333; webmcp_list_sources | OK | Docs re-read 2 Nov. | https://docs.mcp-b.ai/tutorials/desktop-agent-relay |
| 35 | Origin-trial rules (meta/header/script, per origin, invalid ignored, third-party external script, extensions trial_tokens) | OK | Chrome OT guide unchanged. | https://developer.chrome.com/docs/web-platform/origin-trials |
| 36 | Listings 9.1, 9.3, 9.5–9.9 and two console snippets | OK | Byte-identical to the demo files (CHAPTER_MD listing test). | companion repo |
| 37 | Test count "21 checks" | CHANGED | 22 checks (rollback test added). | companion tests |

### Chapter 10: WebMCP in Frameworks


File: `manuscript/10-webmcp-in-frameworks.md`. Old line numbers refer to the 15 October 2026 text. Checked against the shared validation notes and the primary sources named per row, read 2 November 2026.

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | `document.modelContext`, one object per document; tools removed by aborting a signal (l. 13) | OK | Unchanged. IDL of 27 Oct 2026 draft identical in shape | https://webmachinelearning.github.io/webmcp/#idl-index |
| 2 | No `unregisterTool()`; abort the registration signal (l. 92) | OK | Kept | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool |
| 3 | Spec date “Draft Community Group Report, 15 October 2026” (Table 10.3 source line, notes 2, 15, 16, 17) (l. 384) | CHANGED | 27 October 2026 everywhere. Section numbers (§3, §4.2.x, §4.3.x, §5.2) re-checked: unchanged | https://webmachinelearning.github.io/webmcp/ |
| 4 | Explainer quotes (“A tool’s implementation can by dynamic”, “Re-register changed agent-facing metadata”) (l. 37) | OK | Quotes still in README on 2 Nov 2026 | https://github.com/webmachinelearning/webmcp#best-practices |
| 5 | StrictMode quote, abort steps synchronous, first promise rejects AbortError (probe) (l. 94) | OK | Kept (behaviour re-run in the 2 Nov test suite) | https://react.dev/reference/react/StrictMode |
| 6 | Chromium 156 rejects `inputSchema: null` with TypeError (l. 102) | OK | Kept (mock + Chromium tests pass 2 Nov) | demos-new chapters/10 tests |
| 7 | NEW: Chrome best practices “Register tools all at once” (30 Oct 2026) (l. —) | CHANGED (added) | New subsection “The whole set, or none of it”, with a Chromium 156 probe: one shared signal unregisters a batch, duplicate name rejects with InvalidStateError, abort rolls back | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 8 | “Chrome’s documentation … ‘React support’ … usewebmcp package”, quotes of the old section (l. 106) | CHANGED | Page updated 16 Oct 2026: React → `use-webmcp-tool` (`useWebMCP` hook, conditional registration, normalizes results); Vue → `@vueuse/core`. Section rewritten as “React: two hooks”; explains why Trailhead stays on usewebmcp | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 9 | Table 10.2 versions (usewebmcp 6.0.3, @mcp-b/* 6.0.3, use-webmcp-tool 0.3.0, webmcp-types 0.1.10) (l. 110) | OK | Re-checked on npm 2 Nov 2026: no newer versions. Table reordered with Chrome’s hook first | https://registry.npmjs.org/usewebmcp |
| 10 | use-webmcp-tool result normalization (string → content, throw → isError, undefined → empty content) (l. 122) | OK | Expanded from the 0.3.0 README (objects JSON-serialized to a text block, returned Error = throw); no `exposedTo` option | https://github.com/GoogleChromeLabs/use-webmcp-tool |
| 11 | “Trailhead uses usewebmcp, because Chrome’s documentation points to it” (l. 122) | CHANGED | Reason replaced: plain results, type inference, exposedTo. Chrome’s hook presented as the documented alternative | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 12 | usewebmcp behaviour (re-registration triggers, layout effect, registrationError, ‘is registered as metadata’ quote) (l. 179) | OK | Kept (quote split to avoid a semicolon) | https://docs.mcp-b.ai/packages/usewebmcp/reference |
| 13 | Thin wrappers section (l. 191) | CHANGED (extended) | Tied to Chrome’s new “Share the application service” constraint (quote) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 14 | Best-practices quotes: “manage tool registration”, “Reduce complexity: … static registration…”, “each tool takes up part of the context window”, “update the interface state after functions are completed”, epigraph (l. 313) | OK | All still on the page (last updated 30 Oct 2026). Note 1 now names authors incl. Maxim Salnikov | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 15 | Listing 10.5 checkout description (l. 317) | CHANGED | Description lists the new `refused` outcome. Demo file updated | demos-new trailhead-react/src/pages/CartPage.tsx |
| 16 | Spec note: unregistering does not cancel an in-flight execution (quote) (l. 370) | OK | Quote verified in the 27 Oct draft. Added Chrome doc line “As of Chrome 153, you can unregister a tool without cancelling…” | https://webmachinelearning.github.io/webmcp/#model-context-unregister-a-tool |
| 17 | Listing 10.6 checkout (l. 388) | CHANGED | Commit point + stale-state guard: refuses with CART_CHANGED if the cart snapshot changed during confirmation (new test passes in mock + Chromium 156) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 18 | NEW: “Stale workflow state”, “Recompute on confirmation”, “Establish explicit commit points” (30 Oct 2026) (l. —) | CHANGED (added) | New subsection “A commit point, and a cart that must not move” | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 19 | Aborting executeTool signal → AbortError, tool signal aborted, toolcancel fired (l. 463) | OK | Kept (test passes 2 Nov) | https://webmachinelearning.github.io/webmcp/#events |
| 20 | Page observations quote (“an observation”, “often includes screenshots”) (l. 469) | OK | Verified in 27 Oct draft, §5.2 | https://webmachinelearning.github.io/webmcp/#observations |
| 21 | “Update the interface state…” plus NEW “Only resolve a tool execution with success when the output matches the application state” (l. 473) | CHANGED (added quote) | Added the 30 Oct “Wait for the UI” sentence | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 22 | toolactivated / toolcancel events, toolName; Still-in-flux box “in the 14 October 2026 draft” (l. 520) | CHANGED | “27 October 2026 draft”. Added Chrome docs: both non-cancelable, window.ontoolactivated/ontoolcancel not supported from Chrome 156 | https://developer.chrome.com/docs/ai/webmcp/declarative-api |
| 23 | NEW: Vue support via @vueuse/core useWebMCP (l. —) | CHANGED (added) | Short section, no listing (no Vue demo). VueUse 15.0.0 docs: scope lifecycle, refs/getters, live execute, normalization, isSupported/isRegistered/error | https://vueuse.org/core/usewebmcp/ |
| 24 | Angular guide quotes and three APIs (l. 524) | OK | Guide re-checked (last change 21 Oct 2026) | https://angular.dev/ai/webmcp |
| 25 | “Async validators don’t run for tool calls” (l. 671) | CHANGED | Guide corrected 21 Oct 2026 (angular#71445): async validators don’t block submission, their errors aren’t reported to the agent. Text quotes the new wording | https://github.com/angular/angular/pull/71445 |
| 26 | Angular 22.2.2 “the current release” (l. 526) | CHANGED | Kept as tested version, added: 22.2.4 is latest (29 Oct 2026) | https://www.npmjs.com/package/@angular/core |
| 27 | Angular annotation history (readOnlyHint Sept, consequentialHint Sept) (l. 612) | CHANGED (added) | Added `debugging` annotation (angular#71123, merged to main 20 Oct 2026, declareExperimentalWebMcpTool only; forms hard-code false) and official webmcp-types (angular#71354, 28 Oct) | https://github.com/angular/angular/pull/71123 |
| 28 | Signal Forms inferred schema / error result observed in Chromium 156 (l. 663) | OK | Kept (observed 14 Oct, listings unchanged; Angular suite not re-run 2 Nov) | demos-new angular/tests |
| 29 | “This chapter covers the two frameworks that Chrome’s imperative-API page names” (l. 685) | CHANGED | Page now names three: React, Vue, Angular | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 30 | Test counts: 11 React tests, 5 Angular, passed 14 Oct (l. 691) | CHANGED | 12 React tests passed in mock and Chromium 156.0.8078.4 on 2 Nov 2026; Angular 5 (14 Oct, not re-run) | demos-new chapters/10 |
| 31 | “Chromium 156” framing as preview build (l. —) | CHANGED (added) | Chrome 156 Stable since 20 Oct 2026 (156.0.8078.80); tests use Chromium 156.0.8078.4 | https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Windows |
| 32 | MCP-B framework guide quotes (server rendering, ‘use client’, native lifecycle guidance) (l. 683) | UNVERIFIED (not re-fetched) | Kept as in the first edition (third-party docs, retrieved Oct 2026) | https://docs.mcp-b.ai/how-to/frameworks |

##### Demo changes

- `chapters/10-webmcp-in-frameworks/trailhead-react/src/checkout.ts` (Listing 10.6): after the person confirms, the snapshot is compared with the one shown in the dialog. A change returns `{ status: 'refused', code: 'CART_CHANGED' }` and nothing is ordered.
- `trailhead-react/src/pages/CartPage.tsx` (Listing 10.5): the tool description names the `refused` outcome.
- `trailhead-react/tests/run-tests.mjs`: new test “checkout orders exactly the cart the person confirmed; a change behind the dialog is refused”.
- `check-listings.mjs`: reads the new listing label format and the new manuscript path. 11/11 listings byte-identical.
- `README.md`: test-results section dated 2 November 2026.
- Test results, 2 November 2026, Playwright 1.64.1 + Chromium 156.0.8078.4: `npm test` (mock) 12 passed, 0 failed. `WEBMCP=chrome` (WebMCPTesting) 12 passed, 0 failed. node_modules and dist deleted afterwards.
- Angular suite not re-run (listings 10.9–10.11 unchanged, disk budget). Last run: 5/5 mock and Chromium, 14 October 2026.
- Probe (not kept as a file): in Chromium 156.0.8078.4, two `registerTool()` calls sharing one AbortSignal were both removed by one abort. A batch whose second name was taken got `InvalidStateError`, and aborting the shared signal removed the first.

##### Figures

- Figure 10.2 (component tree; numbered 10.1 in the first edition, renumbered because 10.2 is now cited first) redrawn as `figures/src/figure-10-2.svg` (APM palette): same meaning, rows now say “checkout disabled” / “dialog open, call in flight”.
- Figure 10.1 (shared service; 10.2 in the first edition) redrawn as `figures/src/figure-10-1.svg`: the shared layer is now labelled “One application service” (Chrome’s 30 Oct wording), with `checkout.ts` marked as the commit point.
- Figure 10.3 is a screenshot from the 14 October 2026 Chromium test run, not a diagram. Kept as is (the dialog and pill it shows are unchanged).

### Chapter 11: Designing Tools Agents Can Actually Use


File: `manuscript/11-designing-tools.md`. Old line numbers refer to the 15 October 2026 text. Checked against the shared validation notes and the primary sources named per row, read 2 November 2026.

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Spec quotes on `description` and `title` (§4.2.1) (l. 11) | OK | Verified in the 27 Oct 2026 draft. Note date 15 → 27 Oct | https://webmachinelearning.github.io/webmcp/#dictdef-modelcontexttool |
| 2 | Explainer “Every registered tool … consumes tokens…”, “dozens or hundreds”, “severely degrade…” (l. 21) | OK | Quotes still in README, 2 Nov 2026 | https://github.com/webmachinelearning/webmcp#best-practices |
| 3 | Chrome best practices: “each tool takes up part of the context window…”, “the more tools you provide…” (l. 21) | OK | Page last updated 30 Oct 2026, quotes present. Note now names authors incl. Maxim Salnikov | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 4 | NEW: jjhub data point (126 tools, ChatGPT browser message, Chrome no error, budget of 20 with loader tools) (l. —) | CHANGED (added) | New paragraph in “Every tool costs something” and in “Collections, skills”. Quote verified in the issue thread | https://github.com/webmachinelearning/webmcp/issues/255 |
| 5 | OpenAI “fewer than 20 functions”, “just a soft suggestion”, intern test, enums, “Don’t make the model fill…”, “Combine functions…” (l. 23) | UNVERIFIED (not re-fetched) | Kept. Docs page is script-rendered, not re-read on 2 Nov. Note says “read 14 October 2026 (not re-read for this edition)” | https://platform.openai.com/docs/guides/function-calling |
| 6 | Measured characters: Trailhead 1,798, widget 1,850, create_ticket 415 → 1,014, before-total 955 (l. 25) | OK | Re-measured 2 Nov 2026 in Chromium 156.0.8078.4: identical (observations.json) | demos-new chapters/11 tests/results/observations.json |
| 7 | Anthropic quotes (wrap endpoints, schedule_event, prefixes/suffixes, user_id, new hire, high signal, identifiers, truncation, opaque errors, small refinements) (l. 29) | OK | All quotes re-checked on the article page, 2 Nov 2026 | https://www.anthropic.com/engineering/writing-tools-for-agents |
| 8 | NEW: Chrome build-tools framework (user goal, initial state, role-play), authored by Bandarra and Maxim Salnikov (l. —) | CHANGED (added) | New paragraph in “Start from tasks, not endpoints” | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 9 | Chrome “consist of a single function”, explainer “single, well-defined function” (l. 49) | OK | Quote corrected to the page’s exact wording “each tool should consist of a single function” | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 10 | NEW: “Trust the agent to complete the task” (l. —) | CHANGED (added) | Added to “Coarse or fine?” | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 11 | Issue #255 opened 22 Aug 2026, open, quotes (l. 61) | OK | Open on 2 Nov 2026. Added Kenneth Rohde Christiansen’s 20 Oct comment (hints, not a grouping API) | https://github.com/webmachinelearning/webmcp/issues/255 |
| 12 | Issue #161 skills, opened 3 Apr 2026, open (l. 61) | OK | Open on 2 Nov 2026 | https://github.com/webmachinelearning/webmcp/issues/161 |
| 13 | Issue #167 closed (l. 61) | OK | Closed | https://github.com/webmachinelearning/webmcp/issues/167 |
| 14 | Explainer “does not currently define an in-place updateTool()…” (l. 61) | OK | Still in README | https://github.com/webmachinelearning/webmcp#best-practices |
| 15 | Still-in-flux box: “Neither … is in the 15 October 2026 draft” (l. 65) | CHANGED | 27 October 2026 draft. Callout reformatted to `**Still in flux:**` | https://webmachinelearning.github.io/webmcp/ |
| 16 | Name limit 1–128 ASCII chars (Chapter 5), Chrome verbs, create-event / start-event-creation-process (l. 71) | OK | Quotes adjusted to exact page wording (“is a tool for immediate event creation”, “redirects the user to a form…”) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 17 | Chrome security guide budgets 500/150/30/1,500, “some variation across agents” (l. 107) | OK | Page unchanged (last updated 1 Sep 2026) | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 18 | Chrome description guidance: positive language, calendar example vs weather (l. 86) | OK | Quotes adjusted to exact wording (“should describe what the tool does and when to use it”, “rely on positive language and preferences…”) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 19 | Spec misalignment §6.3.2 (finalizeCart) quotes (l. 94) | OK | Verified in 27 Oct 2026 draft | https://webmachinelearning.github.io/webmcp/#security-privacy |
| 20 | Spec §6.4.2 input lengths quotes, issue #73 open (l. 107) | OK | #73 open on 2 Nov 2026 | https://webmachinelearning.github.io/webmcp/#security-privacy |
| 21 | Spec §3 “the stringified representation of the inputSchema” (l. 183) | OK | Verified in 27 Oct 2026 draft | https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool |
| 22 | Over-parameterization scenario quotes §6.3.3 (l. 191) | OK | Verified in 27 Oct 2026 draft | https://webmachinelearning.github.io/webmcp/#security-privacy |
| 23 | NEW: “Accept raw user input” (11:00 to 15:00) (l. —) | CHANGED (added) | New bullet in “The schema is advice” | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 24 | JSON Schema enum/oneOf/const/title quotes (l. 185) | OK | Unchanged reference pages | https://json-schema.org/understanding-json-schema/reference/combining |
| 25 | NEW: honorifics example, “adding narrow rules to patch this issue” (l. —) | CHANGED (added) | New paragraph after the cost of `oneOf` titles | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 26 | Still-in-flux #92 / #289 / MCP 2020-12 dialect (l. 234) | CHANGED | #92 still open, #289 closed unmerged. Added 16 Oct comment (make inputSchema and outputSchema required) and Johann Hofmann’s 30 Oct “Full support from security for requiring and validating these schemas in the spec.” MCP latest revision still 2026-07-28 (checked) | https://github.com/webmachinelearning/webmcp/issues/92 |
| 27 | “Validate strictly in code, loosely in schema” (l. 240) | OK | Still on the page | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 28 | NEW: build-tools “Enforce trust boundaries” (“Enforcement belongs in your application logic, beyond readOnlyHint or untrustedContentHint”) (l. —) | CHANGED (added) | New closing paragraph in “One schema, two jobs” | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 29 | Observed INVALID_ARGUMENT JSON for maxPrice, 1,312-char search result, 10 of 16 (l. 315) | OK | Re-observed 2 Nov 2026 (tests pass) | demos-new chapters/11 |
| 30 | Still-in-flux outputSchema: #9 open since 12 Aug 2025, PR #254 opened 21 Aug 2026, open (l. 442) | CHANGED | Both still open on 2 Nov. Added “last updated 26 October 2026” for #254. Note now links the PR | https://github.com/webmachinelearning/webmcp/pull/254 |
| 31 | MCP tools spec quotes (actionable feedback, isError, SHOULD provide) (l. 448) | OK | Re-checked on revision 2026-07-28 (still the latest revision listed) | https://modelcontextprotocol.io/specification/2026-07-28/server/tools |
| 32 | Spec error-table note (“only tracks…”, “tool execution failures defined by tool authors…”) (l. 448) | OK | Verified in 27 Oct 2026 draft | https://webmachinelearning.github.io/webmcp/#tool-execution-error |
| 33 | NEW: build-tools “Fail gracefully and enable recovery” examples (flights, YYYY-MM-DD, Order 123) (l. —) | CHANGED (added) | New paragraph after the six rules | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 34 | Chrome rate-limit quote (l. 459) | OK | Still on the page | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 35 | NEW: build-tools “Address variance” (NYC next week, “Which day next week?”) (l. —) | CHANGED (added) | Paragraph after Table 11.3, ties `needs_input` to the guide | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 36 | Observed needs_input / PURCHASE_LIMIT / OUT_OF_STOCK results (l. 576) | OK | Re-observed 2 Nov 2026 | demos-new chapters/11 |
| 37 | NEW: build-tools “Duplication conflict” idempotency key (l. —) | CHANGED (added) | New subsection “The same request, twice” and the DUPLICATE_TICKET check in Listing 11.8 (demo + test) | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 38 | NEW: best practices “Share the application service” (l. —) | CHANGED (added) | Added to “Two descriptions of one product” | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 39 | Explainer “loaded into the model’s context statically”, “still validate current inputs…” (l. 639) | OK | Still in README | https://github.com/webmachinelearning/webmcp#best-practices |
| 40 | NEW: “Stale workflow state”, “Recompute on confirmation” (l. —) | CHANGED (added) | Added to “Changing the words” | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 41 | Listing 11.8 callouts ④–⑥ (l. 772) | CHANGED | Renumbered ④–⑦: ④ is the new duplicate check (observed SUP-1044 returned, form hidden), ⑤ rate limit, ⑥ no existence leak, ⑦ ticketState | demos-new chapters/11 helpdesk/widget-tools.js |
| 42 | Figure 11.3 caption “measured … on 14 October 2026” (l. 780) | CHANGED | “measured with measureTools() in Chromium 156” (numbers identical on 2 Nov) | demos-new chapters/11 observations.json |
| 43 | “evaluation-driven development” presented as a quote (l. 784) | CHANGED | The page has it as a Key Term, now paraphrased without quote marks | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 44 | Test totals: 99 checks, 36 behavioural, passed 14 and 15 Oct (l. 790) | CHANGED | 101 checks (37 behavioural ×2), all passed 2 Nov 2026 in Chromium 156.0.8078.4 | demos-new chapters/11 |
| 45 | Summary bullet “not part of the 15 October 2026 draft” (l. 796) | CHANGED | 27 October 2026 draft | https://webmachinelearning.github.io/webmcp/ |

##### Demo changes

- `chapters/11-designing-tools/helpdesk/helpdesk-api.js` (not printed): `findDuplicate()` keyed on the exact subject, body and priority, one-hour window.
- `helpdesk/widget-tools.js` (Listing 11.8): `create_ticket` returns `refuse('DUPLICATE_TICKET', …, { ticketId })` before the form opens and before the hourly limit. Callouts renumbered ④–⑦.
- `tests/run-tests.mjs`: new check “the same ticket sent twice -> refused DUPLICATE_TICKET with the first ticket ID, form stays hidden”.
- `tests/check-listings.mjs`: reads the new listing label format and the new manuscript path. 8/8 listings byte-identical.
- `README.md`: results dated 2 November 2026.
- Test results, 2 November 2026, Playwright 1.64.1 + Chromium 156.0.8078.4 (WebMCPTesting) and the mock: 101 passed, 0 failed. node_modules deleted afterwards. Character measurements unchanged from 14 October.

##### Figures

- Figure 11.1 redrawn as `figures/src/figure-11-1.svg`: same eleven operations and five tools, tools coloured by annotation (read-only, changes the cart, consequential).
- Figure 11.2 redrawn as `figures/src/figure-11-2.svg`: five statuses, who acts next, retry rule, coloured agent / person / stop.
- Figure 11.3 redrawn as `figures/src/figure-11-3.svg` from `observations.json` (2 Nov 2026): 624→818, 395→503, 283→404, 415→1,014, 257→432.

### Chapter 12: Threat Models for Tool-Exposing Pages


2 November 2026. Sources: the shared validation notes, the spec draft of 27 October 2026 read directly (https://webmachinelearning.github.io/webmcp/), Chrome docs pages read directly (secure-tools, build-tools, best-practices, /docs/agents/security), GitHub issue/PR states read via the API on 2 Nov 2026. Old line numbers refer to manuscript/12-threat-models.md as of the Oct 15 text.

#### Chapter 12: Threat Models for Tool-Exposing Pages

| # | Claim / API / listing (short quote, old line) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph, Chrome "WebMCP tool security" quote (l.3) | OK | Unchanged; page still updated 1 Sep 2026 | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 2 | "checked against the WebMCP Draft Community Group Report dated 15 October 2026" (l.17) | CHANGED | 27 October 2026 draft; text names the two §6 additions since 15 Oct | https://webmachinelearning.github.io/webmcp/ |
| 3 | §6 non-normative, "cannot define precise mitigation strategies…" (l.13) | OK | Quote still in §6.1 | https://webmachinelearning.github.io/webmcp/#approach-to-risk-assessment-and-mitigations |
| 4 | Four parties; identity inheritance, extended user context, cross-site context (§6.1/6.2) | OK | Kept | https://webmachinelearning.github.io/webmcp/#agent-baseline-capabilities |
| 5 | Chrome agent guidance "assume WebMCP tools mutate state" | OK | Kept | https://developer.chrome.com/docs/agents/security |
| 6 | "must assume good faith from site developers" (§6.3.2.4) | OK | Kept | https://webmachinelearning.github.io/webmcp/#intent-current-gaps |
| 7 | Issue #313 open; editors defer to agents/browsers | OK | Still open (last update 8 Oct 2026) | https://github.com/webmachinelearning/webmcp/issues/313 |
| 8 | "PR #334 … open" and Still-in-flux box "both open on 15 October 2026" (l.37–41) | CHANGED | #334 merged 20 Oct 2026: §6.2 now says agent-level risks "apply broadly to any agent … regardless of whether a site exposes WebMCP tools", "a malicious site can omit or misrepresent those hints", responsibility "primarily … the agent's own security model"; new §6.4.6 Agent-Level Guardrails. Box rewritten: #313 still open, AWWG in charter refinement | https://github.com/webmachinelearning/webmcp/pull/334 ; https://webmachinelearning.github.io/webmcp/#mitigation-agent-level-guardrails |
| 9 | Prompt-injection definition and quotes (§6.3.1) | OK | Kept | https://webmachinelearning.github.io/webmcp/#prompt-injection |
| 10 | Tool poisoning example `search-web` with fake SYSTEM INSTRUCTION (§6.3.1.1) | OK | Kept | https://webmachinelearning.github.io/webmcp/#metadata-description-attacks |
| 11 | Name limit 128 chars ASCII letters/digits/_-. ; length limits future work, issue #73 | OK + ADDED | Kept; added open PR #265 (input-length limits in code points) | https://github.com/webmachinelearning/webmcp/issues/73 ; https://github.com/webmachinelearning/webmcp/pull/265 |
| 12 | Chrome budgets 30/150/500/1,500 | OK | Re-read on secure-tools "Set character budgets" (500 / 150 / 30 / 1.5K) | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 13 | Output injection, "malicious actors influencing website content" (§6.3.1.2) | OK | Kept | https://webmachinelearning.github.io/webmcp/#output-injection-attacks |
| 14 | untrustedContentHint "requires heightened security handling" (§6.4.4); Chrome asks to set it for UGC | OK | Kept | https://webmachinelearning.github.io/webmcp/#mitigation-untrusted-annotation |
| 15 | Spotlighting / Base64 in agent guidance | OK | Kept | https://developer.chrome.com/docs/agents/security |
| 16 | Listing 12.1 result shaper; test "3 of 14 matches in 1,088 characters" | OK | Byte-identical to demo; test re-run 2 Nov 2026 passes | demos-new/chapters/12-threat-models |
| 17 | ToolAnnotations: four members default false; Chromium passes untrustedContentHint through getTools() | OK | IDL unchanged (27 Oct); test re-run passes; box adds the new "omit or misrepresent" sentence | https://webmachinelearning.github.io/webmcp/#idl-index |
| 18 | §6.3.1.3 "exercise a different code path" | OK | Kept | https://webmachinelearning.github.io/webmcp/#tool-implementation-targets |
| 19 | Browser does not enforce inputSchema (50,000-char query, undeclared field reached execute) | OK | Re-tested 2 Nov 2026 in Chromium 156.0.8078.4 | demos-new/chapters/12-threat-models/tests |
| 20 | (new) Chrome build-tools "Enforcement belongs in your application logic, beyond readOnlyHint or untrustedContentHint" | ADDED | Quoted in ⑦; page co-authored by Maxim (byline verified) | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 21 | (new) best-practices "Share the application service" | ADDED | Cited after Listing 12.2 | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 22 | Listing 12.2 guards | OK | Byte-identical | demos-new |
| 23 | Misrepresentation of intent quotes, finalizeCart scenario (§6.3.2.x) | OK | Kept | https://webmachinelearning.github.io/webmcp/#scenario-ambiguous-finalization |
| 24 | consequentialHint "significant, real-world, or non-reversible"; grew out of #176 (closed 3 Sep) | OK | Kept | https://webmachinelearning.github.io/webmcp/#mitigation-consequential-annotation |
| 25 | #298 / PR #333 "Neither had been merged on 15 October" | CHANGED (date) | Both still open on 2 Nov 2026 (#333 last updated 1 Nov) | https://github.com/webmachinelearning/webmcp/pull/333 |
| 26 | Still-in-flux box on requestUserInteraction (Chrome page still mentions it) | CHANGED (wording) | Draft has no such method; replacement requestUserInput() (#204) still open, updated 29 Oct; Chrome secure-tools page still says "the spec draft includes requestUserInteraction()" (re-read 2 Nov) | https://github.com/webmachinelearning/webmcp/pull/204 |
| 27 | Over-parameterisation §6.3.3 example and three implications | OK | Kept | https://webmachinelearning.github.io/webmcp/#privacy-leakage-over-parameterization |
| 28 | Mozilla neutral (#1412), WebKit oppose (#670) | OK | Unchanged per the shared validation notes (Mozilla "refreshed" position announced, not published) | https://github.com/mozilla/standards-positions/issues/1412 |
| 29 | Listing 12.3 schemas | OK | Byte-identical | demos-new |
| 30 | #331 / #110 sensitivity hint "Nothing had been merged on 15 October" | CHANGED (date) | Both still open on 2 Nov 2026 | https://github.com/webmachinelearning/webmcp/issues/331 |
| 31 | §6.3.5 private browsing | OK | Kept | https://webmachinelearning.github.io/webmcp/#interaction-with-private-browsing |
| 32 | "### The section that is still a TODO" + §6.3.4 "Violation of Same-Origin Boundaries" + PR #326 open (l.215–221, fn 32/33) | CHANGED | PR #326 merged 27 Oct 2026. §6.3.4 is now "Interaction with the Same-Origin Policy" with §6.3.4.1 "Enforcing Same-Origin Isolation via Two-Sided Opt-In" (three gates, "Why Two-Sided Opt-In Matters") and §6.3.4.2 Residual Risks. Section retitled "The section that used to be a stub", rewritten to quote the spec; footnote anchors updated (old anchor gone) | https://webmachinelearning.github.io/webmcp/#interaction-with-same-origin-policy ; https://github.com/webmachinelearning/webmcp/pull/326 |
| 33 | Permissions Policy `tools`, default 'self' (§4.4); Chrome overview "Permissions policy" | OK | Kept; added spec sentence that without delegation a cross-origin iframe cannot register or expose tools | https://webmachinelearning.github.io/webmcp/#permissions-policy |
| 34 | Listing 12.4; NotAllowedError without allow / with tools=(self) | OK | Byte-identical; tests re-run pass | demos-new |
| 35 | tools=() disables for document and frames (§6.4.1) | OK | Kept | https://webmachinelearning.github.io/webmcp/#mitigation-disable-permissions-policy |
| 36 | exposedTo / fromOrigins, potentially trustworthy origins | OK | Kept; spec rationale paragraph added | https://webmachinelearning.github.io/webmcp/#dictdef-modelcontextregistertooloptions |
| 37 | Imperative API page "Origin exposure", footnote said updated 21 Sep | CHANGED | Page last updated 16 Oct 2026 (the shared validation notes #6) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 38 | Listing 12.5; gate tests (plain getTools empty; fromOrigins returns 2; partner gets none) | OK | Byte-identical; re-run pass | demos-new |
| 39 | (new) Residual risks: callers check origin/window on same-named tools | ADDED | Paragraph after Figure 12.2 | https://webmachinelearning.github.io/webmcp/#same-origin-residual-risks |
| 40 | Extensions can query/execute tools via content scripts | OK | Kept (Chrome secure-tools) | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 41 | provideContext() removed March 2026 (cross-ref to Ch5) | OK | Kept | Chapter 5 / the shared validation notes |
| 42 | Listing 12.6 wrap attack; collector output | OK | Byte-identical; re-run pass | demos-new |
| 43 | SRI, CSP references | OK | Kept | w3c drafts |
| 44 | Table 12.1 | OK | Kept, sources line adds build-tools guide | — |
| 45 | Listing 12.7 audit | OK | Byte-identical; re-run pass | demos-new |
| 46 | #106 shared attack datasets "still open on 15 October" | CHANGED (date) | Still open on 2 Nov 2026 | https://webmachinelearning.github.io/webmcp/#mitigation-shared-attack-evals |
| 47 | (new) §6.4.6 Agent-Level Guardrails ("agents cannot rely solely on site-asserted tool descriptions or annotations") | ADDED | New paragraph in "Shared attack datasets" | https://webmachinelearning.github.io/webmcp/#mitigation-agent-level-guardrails |
| 48 | "all twenty-six of them pass" | OK | Re-run 2 Nov 2026: 26/26 pass | demos-new/chapters/12-threat-models |
| 49 | Summary list of open questions incl. #326 | CHANGED | #326 removed (merged); #265 added; #334 removed (merged) | — |

Removed deliberately: the claim that §6.3.4 is a TODO (now written), the "#334 open" claims, the old anchor `#violation-same-origin-boundaries`. Nothing technical was dropped.

#### Demo changes

None needed (no API change affects the listings). README status line updated to the 2 Nov 2026 re-run. Tests: `npm install --no-save playwright@1.64.1` + `npm test` with the cached Chromium 156.0.8078.4 (`--enable-features=WebMCPTesting`): **26 passed, 0 failed**. node_modules deleted afterwards.

#### Figures

- Figure 12.1 redrawn as SVG (figures/src/figure-12-1.svg) in the APM palette. Change: attack ⑥ now maps to §6.4.1 (the old figure said "not in §6"), ⑤ labelled as the two-sided opt-in of §6.3.4, footer names the 27 October 2026 draft; no title inside the image.
- Figure 12.2 redrawn (figures/src/figure-12-2.svg): three gates labelled embedder / provider / consumer, cites §6.3.4.1; partner.example row kept.

### Chapter 13: Privacy, Consent and the Human in the Loop


2 November 2026. Sources as for Chapter 12 (the shared validation notes v1; spec 27 Oct 2026 read directly; Chrome pages read directly; issue/PR states via the GitHub API on 2 Nov 2026; the W3C TAG comment read via the API).

#### Chapter 13: Privacy, Consent and the Human in the Loop

| # | Claim / API / listing (short quote, old line) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph from Chrome "Agent security considerations" | OK | Kept | https://developer.chrome.com/docs/agents/security |
| 2 | Explainer goal "enable human-in-the-loop workflows", non-goal fully autonomous | OK | Kept (README unchanged since before 15 Oct per the shared validation notes) | https://github.com/webmachinelearning/webmcp |
| 3 | "checked against … 15 October 2026 … all read on 15 October" | CHANGED | 27 October 2026 draft, sources re-read 2 Nov 2026 | https://webmachinelearning.github.io/webmcp/ |
| 4 | Spec has no consent/confirmation API; §7 accessibility empty | OK | Re-checked in 27 Oct draft: §7 heading only, no consent API in IDL | https://webmachinelearning.github.io/webmcp/#accessibility |
| 5 | consequentialHint "selectively enforce mandatory user confirmation prompts" (§6.4.5) | OK | Kept | https://webmachinelearning.github.io/webmcp/#mitigation-consequential-annotation |
| 6 | toolactivated / toolcancel events, AbortSignal | OK | IDL unchanged | https://webmachinelearning.github.io/webmcp/#idl-index |
| 7 | Issue #155 consent signal, open | OK | Still open on 2 Nov 2026 | https://github.com/webmachinelearning/webmcp/issues/155 |
| 8 | Listing 13.1 confirm sheet (800 ms arming, isTrusted, Esc/Back decline, abort closes) | OK | Byte-identical; tests re-run 2 Nov pass | demos-new/chapters/13-privacy-consent-human-in-the-loop |
| 9 | DOM isTrusted definition | OK | Kept | https://dom.spec.whatwg.org/#dom-event-istrusted |
| 10 | Listing 13.2 checkout tools; outcomes placed / cancelled_by_user / CART_EMPTY / SESSION_ENDED | OK | Byte-identical; tests re-run pass (TH-100200, 7,297 NOK) | demos-new |
| 11 | Unregistering doesn't cancel running executions (spec §3) | OK | Kept; consistent with Chrome imperative-api note "As of Chrome 153, you can unregister a tool without cancelling … in-flight executions" | https://webmachinelearning.github.io/webmcp/#supporting-concepts |
| 12 | (new) Commit points | ADDED | Click on Place order described as the tool's commit point, per best-practices "Establish explicit commit points" (30 Oct) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 13 | (new) Bind approval to the exact plan / stale workflow state / recompute on confirmation | ADDED | New subsection "Bind the yes to the exact plan"; quotes build-tools; states honestly that the demo keeps the simpler version and its tests do not cover concurrent edits | https://developer.chrome.com/docs/ai/webmcp/build-tools ; best-practices |
| 14 | Issue #288 report, 700 ms hold, isTrusted quote, decision-grant comment | OK | Still open (last update 21 Sep 2026); text kept | https://github.com/webmachinelearning/webmcp/issues/288 |
| 15 | HTML user activation model | OK | Kept | https://html.spec.whatwg.org/multipage/interaction.html#tracking-user-activation |
| 16 | requestUserInteraction history; #165 open; CG resolution 11 June; #205 merged 11 June | OK | #165 still open (updated 26 Oct); #205 merged 11 June confirmed | https://github.com/webmachinelearning/webmcp/issues/165 ; /pull/205 |
| 17 | "As of 15 October 2026, #165 and #204 are both open" | CHANGED (date) | Both open on 2 Nov 2026; #204 last updated 29 Oct | https://github.com/webmachinelearning/webmcp/pull/204 |
| 18 | Chrome secure-tools still says "the spec draft includes requestUserInteraction()" | OK | Re-read 2 Nov 2026: sentence still there | https://developer.chrome.com/docs/ai/webmcp/secure-tools |
| 19 | Listing 13.3 IDL from PR #204 | OK | Re-checked the PR diff on 2 Nov 2026: IDL identical; listing byte-identical to proposal/request-user-input.webidl | https://github.com/webmachinelearning/webmcp/pull/204/files |
| 20 | Three modes description (interactive/form/url), url "where user-provided data must not flow through the agent" | OK | Kept | PR #204 |
| 21 | Issue #316 sensitive fields guidance, open | OK | Still open | https://github.com/webmachinelearning/webmcp/issues/316 |
| 22 | Identity inheritance §6.2; "without additional verification" §6.3.2.1 | OK | Kept | https://webmachinelearning.github.io/webmcp/#agent-baseline-capabilities |
| 23 | Listing 13.4 session tools; registerTool AbortError (PR #202) | OK | Byte-identical; re-run pass | demos-new |
| 24 | (new) Register tools all at once (best-practices 30 Oct) | ADDED | One sentence after Listing 13.4 | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 25 | get_cart summaries (Oslo 0150, Visa ending 4242; four keys) | OK | Kept; re-run pass | demos-new |
| 26 | #331 / #110 sensitiveHint | CHANGED (date) | Still open on 2 Nov 2026 | https://github.com/webmachinelearning/webmcp/issues/331 |
| 27 | §6.3.5 private browsing | OK | Kept | https://webmachinelearning.github.io/webmcp/#interaction-with-private-browsing |
| 28 | Agent identity #105, #54, allowlists #116 — open | OK | All open on 2 Nov 2026 | GitHub issues |
| 29 | (new) Agentic Web WG draft charter lists agent identity and agent delegation as tentative deliverables | ADDED | One sentence, sourced from the shared validation notes (w3c/strategy #576, charter-drafts PR #901) | https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html |
| 30 | WebKit position quotes ("in effect, assistive technology", etc.) | OK | Kept; WebKit position unchanged (closed 11 June, no activity since 17 June) | https://github.com/WebKit/standards-positions/issues/670 |
| 31 | #62 user activation, open; Chromium 156 grants no activation | OK | #62 open (last updated 31 Oct); re-test pass | https://github.com/webmachinelearning/webmcp/issues/62 |
| 32 | Explainer accessibility quotes | OK | Kept | https://github.com/webmachinelearning/webmcp |
| 33 | (new) W3C TAG early comment, 26 Oct 2026 | ADDED | New paragraph in the accessibility section: "web for agents", removed incentive for semantic/accessible sites, "to fully work out the declarative version before shipping the imperative one", per-node language/direction, planned Finding on Agentic Browsing; quotes checked against the comment body | https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845 |
| 34 | #277, #65, #272 open | OK | Open on 2 Nov 2026 (#277 checked via API) | https://github.com/webmachinelearning/webmcp/issues/277 |
| 35 | Listing 13.5 agent presence; title localisation (§4.2.1) | OK | Byte-identical; re-run pass | https://webmachinelearning.github.io/webmcp/#model-context-tool |
| 36 | Accessibility box "§7 is empty in the 15 October 2026 draft" | CHANGED (date) | "still empty in the 27 October 2026 draft"; TAG added | https://webmachinelearning.github.io/webmcp/#accessibility |
| 37 | "The sixteen tests behind every claim" | OK | Re-run 2 Nov 2026: 16/16 pass | demos-new |

Not changed on purpose: the demo does not implement plan binding (snapshot + version check). The text says so plainly rather than claiming it. A follow-up could add it with a "time travel" test (Chapter 14's territory).

#### Demo changes

None. Tests: `npm install --no-save playwright@1.64.1` + `npm test`, cached Chromium 156.0.8078.4, `--enable-features=WebMCPTesting`: **16 passed, 0 failed** (2 Nov 2026). node_modules deleted.

#### Figures

- Figure 13.1 redrawn (figures/src/figure-13-1.svg): agent / browser / page swimlanes, the confirmation sheet, the commit point after the click, and the "no party tells the others what it asked (#155)" footer.
- Figure 13.2 redrawn (figures/src/figure-13-2.svg): the three proposed modes, labelled as a PR #204 proposal (not in the spec, not in Chromium), with the `{ action, content }` result mapped to Trailhead's outcomes.

### Chapter 14: Testing, Debugging and Evals


2 November 2026 (replacing the reviewer, whose run ended before it touched this chapter). Sources: the shared validation notes (STATUS: final), the spec draft of 27 October 2026, and these pages and records read directly on 2 November 2026: Chrome docs build-tools, best-practices, evals, the WebMCP overview, imperative-api and the DevTools "Debug WebMCP tools" page; GitHub API for issues #92 and #361, chrome-devtools-mcp releases, webmcp-tools commits, the WPT `webmcp/` tree and its commits since 15 October; the tip-of-tree CDP JSON (`json/browser_protocol.json`, roll of 31 Oct 2026); the npm registry; Chromium Dash milestones. Old line numbers refer to the Oct 15 text as restructured in `book/manuscript/` before this rewrite.

#### Chapter 14: Testing, Debugging and Evals

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph from build-tools “When testing systems that use generative AI…” (l.3) | OK | Kept, sentence still on the page (updated 30 Oct 2026, byline Bandarra + Salnikov) | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 2 | “checked against the WebMCP Draft CG Report of 15 October 2026” (l.19) | CHANGED | 27 October 2026 draft, docs and CDP re-read 2 Nov 2026 | https://webmachinelearning.github.io/webmcp/ |
| 3 | Observed in Chromium 156.0.8078.4 with WebMCPTesting (l.19) | OK + dated | Same build, described as an early build of the version that went Stable on 20 Oct 2026 | the shared validation notes item 11; chromiumdash |
| 4 | Demo test script runs every listing (l.19) | OK | 21/21 checks re-run 2 Nov 2026 (17 node --check + 21 tests) | demos-new/chapters/14-testing-debugging-evals |
| 5 | DevTools WebMCP pane in Application panel; Available/Invoked Tools; statuses; filters (l.26) | OK | Kept, plus clickable status icons in the invocation counter (on the page) | https://developer.chrome.com/docs/devtools/application/webmcp |
| 6 | DevTools page “last updated 12 May 2026” (fn 4) | CHANGED | Page shows no date; footnote says so | same |
| 7 | Manual “Run tool”, pre-filled from a logged call; schema-violation messages; invocation counter (l.28) | OK | Kept | same |
| 8 | Edge 149 lists “WebMCP debugging” (l.30) | OK (not re-fetched) | Kept | https://learn.microsoft.com/en-us/microsoft-edge/devtools/whats-new/149 |
| 9 | Issue #92 open on 15 Oct (l.32, l.161, summary) | CHANGED | Still open 2 Nov; new comments 13–30 Oct (Foltz, Beaufort, Dallstream, Hofmann) favour required + browser-validated schemas; nothing merged | https://github.com/webmachinelearning/webmcp/issues/92 |
| 10 | Model Context Tool Inspector: Gemini key or Prompt API via chrome://flags/#prompt-api-tool-use (l.36) | OK | Kept | https://developer.chrome.com/docs/ai/webmcp |
| 11 | Only the Inspector named as an agent extension (l.36) | CHANGED (added) | Example Agentic Chrome Extension added (“always trusts WebMCP annotations”) and the page’s caution that extensions can query/execute tools | https://developer.chrome.com/docs/ai/webmcp |
| 12 | webmcp-tools repo carries Inspector, demos, polyfill, evals (l.36) | OK | Latest commit 29 Oct 2026 | https://github.com/GoogleChromeLabs/webmcp-tools |
| 13 | chrome-devtools-mcp 1.10.1 on 15 Oct (l.39) | CHANGED | 1.12.0 (22 Oct 2026) latest; 1.11.0 (15 Oct) surfaces WebMCP tool exceptions, rejects JSON arrays as params | https://registry.npmjs.org/chrome-devtools-mcp ; https://github.com/ChromeDevTools/chrome-devtools-mcp/releases |
| 14 | `list_webmcp_tools`, `execute_webmcp_tool`, off by default, `--categoryExperimentalWebmcp` (l.39) | OK | Kept (DevTools page 2 Nov) | https://developer.chrome.com/docs/devtools/application/webmcp |
| 15 | `debugging` annotation “available from Chrome 156” (l.43) | OK | Kept; imperative-api now updated 16 Oct 2026 (fn date fixed from 21 Sep) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 16 | getTools()/CDP annotation shapes with debugging (l.45) | OK | Kept (the shared validation notes probe 2 Nov confirms getTools annotation keys and missing member) | the shared validation notes |
| 17 | ToolAnnotations has `debugging` default false (l.47) | OK | 27 Oct IDL identical | https://webmachinelearning.github.io/webmcp/#idl-index |
| 18 | “a hint, not a lock” (l.49) | OK + added | Added the spec’s new sentence (PR #334, 20 Oct) that a malicious site can omit or misrepresent hints | https://github.com/webmachinelearning/webmcp/pull/334 |
| 19 | Listing 14.1 trailhead-tools.js | OK | Byte-identical; label converted to house style form | demo file |
| 20 | Factory pattern (l.148) | OK + added | Linked to best-practices “Share the application service” (30 Oct) | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 21 | node:test stable since Node 20 (l.152) | OK | Kept | https://nodejs.org/api/test.html |
| 22 | Listing 14.2 unit tests | OK | Byte-identical; 4/4 pass 2 Nov | demo file |
| 23 | Browser does not validate against inputSchema; execute steps reject only non-objects (l.161) | OK | Kept; probe 2 Nov: invalid JSON-Schema type accepted at registration | spec §3.1; the shared validation notes |
| 24 | “about 80 milliseconds” for four unit tests (l.169) | OK (Oct measurement, kept as such) | Kept | demo run |
| 25 | (new) “Test time travel states”, “Pin versions” | ADDED | Quoted from build-tools (30 Oct) with how to apply them | https://developer.chrome.com/docs/ai/webmcp/build-tools |
| 26 | Mock vs real Chromium; Playwright’s Chromium 156 accepts the switch (l.175) | OK | Kept | demo tests |
| 27 | Table 14.1 string result: spec JSON-quoted vs Chromium bare (l.239) | OK + dated | Added #361 editor ruling (26 Oct): spec right, Chrome and WPT wrong | https://github.com/webmachinelearning/webmcp/issues/361 |
| 28 | Table 14.1 `undefined` → OperationError (spec) vs "undefined" (l.240) | OK + flux | Added: #361 proposes `undefined` → `"null"` (not merged) | same |
| 29 | Table 14.1 throws → OperationError vs UnknownError; unregistered → NotFoundError vs UnknownError (l.241–242) | OK | Kept; Chromium 156 re-observed 2 Nov (fjord-table README; the shared validation notes) | demos-new/fjord-table/README.md; the shared validation notes |
| 30 | Invalid name / empty description / duplicate → InvalidStateError (l.244) | OK | Kept (probe 2 Nov: duplicate and empty name → InvalidStateError) | the shared validation notes |
| 31 | #339 merged 8 Oct; Chromium 156 still UnknownError (l.250) | OK + added | Added: Chromium CL 8546218 “Reject executeTool() with granular DOMExceptions” landed 16 Oct (#1720407, after M157 branch #1717349, before M158 #1727472) → expected in Chrome 158; not observed | https://chromium-review.googlesource.com/c/chromium/src/+/8546218 ; https://chromiumdash.appspot.com/fetch_milestones |
| 32 | (new) Tool interface in Chromium | ADDED | CL 8510757 (15 Oct, #1719188) replaces RegisteredTool with a `Tool` interface object; spec PR #348 still open; not observed | https://chromium-review.googlesource.com/c/chromium/src/+/8510757 ; https://github.com/webmachinelearning/webmcp/pull/348 |
| 33 | WPT webmcp/: imperative 49 HTML files (l.254) | CHANGED | 51 imperative, 25 declarative on 2 Nov; new `tool-re-registration-race` named | https://github.com/web-platform-tests/wpt/tree/master/webmcp |
| 34 | toolcancel WPT comment on ordering (l.256) | OK (file present) | Kept | https://github.com/web-platform-tests/wpt/blob/master/webmcp/tool-cancel-event.https.html |
| 35 | (new) WPT follows Chrome on serialization | ADDED | From #361 | https://github.com/webmachinelearning/webmcp/issues/361 |
| 36 | CDP WebMCP domain: 4 commands, 4 events, experimental, tip-of-tree (l.265–282) | OK | Re-read 2 Nov (roll 31 Oct 2026): identical; `Tool` also has backendNodeId (not used by the text) | https://chromedevtools.github.io/devtools-protocol/tot/WebMCP/ |
| 37 | invokeTool response “is sent before tool events”; output “poses a prompt injection risk” (l.284) | OK | Kept (output description re-read 2 Nov) | same |
| 38 | CDP Annotation names differ, `autosubmit` field still present; #338 merged 8 Oct (l.440) | OK | Kept (8 Oct per GitHub API; an earlier working note’s 13 Oct was wrong) | https://github.com/webmachinelearning/webmcp/pull/338 |
| 39 | (new) DevTools still identifies tools by name | ADDED | From the Tool interface CL description | CL 8510757 |
| 40 | Listings 14.3, 14.4 | OK | Byte-identical; CDP tests 3/3 pass 2 Nov | demo files |
| 41 | Observations: toolsAdded per registration; Tool not found; exception object; cancel; object output; toolactivated after execute start (l.429–439) | OK | Kept; suite re-run 2 Nov; added the new “register tools all at once” guidance next to the first one | demo tests; best-practices |
| 42 | Evals verify “tool selection, parameter extraction, and state management” (l.445) | OK | Kept | build-tools |
| 43 | (new) Chrome evals page | ADDED | “Test WebMCP with Evals” (Kulikowski, 19/28 May 2026): failure modes, isolation, full tool list, direct vs ambiguous, ordered/unordered, mid-chain failure | https://developer.chrome.com/docs/ai/webmcp/evals |
| 44 | webmcp-evals 0.0.4, experimental; modes local/browser/smoke/simulate; README quote (l.453, 510) | OK | 0.0.4 still latest (28 Aug 2026) | https://registry.npmjs.org/webmcp-evals |
| 45 | Listings 14.5–14.7 | OK | Byte-identical; eval harness 5/5 pass 2 Nov | demo files |
| 46 | Matcher semantics follow webmcp-evals matcher.ts (l.514) | OK (not re-read) | Kept | https://github.com/GoogleChromeLabs/webmcp-tools/blob/main/webmcp-evals/src/matcher.ts |
| 47 | gpt-6-sol runs on 14 Oct: 2×5/5 + 0/5, then 15/15 (l.641–650) | OK | Kept as an October measurement; report files carry agent, model, Chromium build, date | evals/results/*.txt |
| 48 | Test Agent (Ch9) unchanged, 2 tests (l.636) | OK | 2/2 pass 2 Nov against the current ch09 demo | demo tests |
| 49 | Table 14.3 “manual session with the Inspector extension” | CHANGED | “one of Chrome’s two agent extensions” | Chrome overview page |
| 50 | Listing 14.8 instrument-tool.js; RUM tests (l.688–735) | OK | Byte-identical; RUM mock 3/3, Chromium 4/4 pass 2 Nov | demo files |
| 51 | Beacon API (l.724) | OK | Kept | https://w3c.github.io/beacon/ |
| 52 | Spec privacy §6.3.3 over-parameterization (l.740) | OK | 27 Oct draft keeps the section | https://webmachinelearning.github.io/webmcp/ |
| 53 | Nothing tells execute who calls (l.751) | OK | 27 Oct IDL: no caller info (proposals #227/#204 open) | spec IDL |
| 54 | Table 14.4 channels (explainer repo issues, Blink>Agentic Platform>WebMCP, EPP, Edge surveys, WPT) | OK | Kept | chromestatus; OT blog; Edge OT page |
| 55 | CONTRIBUTING: substantive contributions need CG membership + CLA (l.766) | OK | Kept; Maxim’s own CG membership mentioned (AUTHOR-the shared validation notes: on the participant list) | https://github.com/webmachinelearning/webmcp/blob/main/CONTRIBUTING.md ; AUTHOR-the shared validation notes |
| 56 | Example bug report (blockquote) | CHANGED (form) | Now a `text` code block (house style: blockquotes are callouts only) | — |
| 57 | Author statement “a page I co-authored” (build-tools) | ADDED | Verified byline (30 Oct revision) | https://developer.chrome.com/docs/ai/webmcp/build-tools ; the shared validation notes item 1 |

Unverified, said so in the text: Chrome 158 behaviour (granular errors, Tool interface) is inferred from Chromium commit positions and milestone branch points, not observed (only Chromium 156 is on this box). The real-model eval runs were not repeated for the second edition.

#### Demo changes

- `chapters/14-testing-debugging-evals`: no code change (all eight listings byte-identical to their files, compared after the rewrite). README: second-edition status line (2 Nov 2026 run) and dates. `npm test` on 2 Nov 2026 (Node 22, Playwright 1.64.1, Chromium 156.0.8078.4): 17 × `node --check` ok, unit 4/4, RUM mock 3/3, RUM Chromium 4/4, Fjord Table over CDP 3/3, eval harness 5/5, Test Agent 2/2 — all checks passed. node_modules deleted.

#### Figures

- Figure 14.1 redrawn as SVG (figures/src/figure-14-1.svg): five layers with what runs and what each catches; layer contents updated (time-travel sequences in Layer 1).
- Figure 14.2 redrawn as SVG (figures/src/figure-14-2.svg): sequence test → Chromium (WebMCP domain) → Fjord Table → person, with the cancel path; dated “re-run on 2 November 2026”.

### Chapter 15: Browser Support and the Standards Road


2 November 2026. Re-checked the most time-sensitive statements directly (GitHub API on 2 Nov 2026 ~10:15 UTC: mozilla/standards-positions#1412, WebKit/standards-positions#670, w3ctag/design-reviews#1238, w3c/strategy#576, webmachinelearning/webmcp#236/#361; Chromium Dash milestone schedule for 157/158/162; npm registry for the MCP-B packages; WPT and Chromium commits since 15 Oct), applied the corrections below, and compared every URL, number and code-quoted name of the Oct 15 text with the new text (none dropped except the bare repository name `webmcp-book-demos`, which now appears in the folder sentence). Rows marked “G, 2 Nov” are statements the text itself dates to the first 2 November re-check and that the reviewer did not re-fetch.

#### Chapter 15: Browser Support and the Standards Road

| # | Claim / API / listing (short quote) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | Epigraph: “Community Groups do not create W3C standards” | OK | Kept | https://www.w3.org/community/about/faq/ |
| 2 | Spec status: Draft CG Report, not on the standards track | CHANGED | 27 October 2026 draft, four editors | https://webmachinelearning.github.io/webmcp/ |
| 3 | Mozilla position neutral (label 5 Aug 2026), VanderSloot quotes | OK | Issue closed, last update 26 Aug 2026, labels “venue: W3C CG”, “position: neutral” (the reviewer re-checked) | https://github.com/mozilla/standards-positions/issues/1412 |
| 4 | Mozilla meta bug “[meta] Implement a prototype WebMCP API” still open | OK (G, 2 Nov) | Kept | Bugzilla (fn ch15-21) |
| 5 | #236 generic communication tool; Hofmann 22 Sep requirements | OK | Kept | https://github.com/webmachinelearning/webmcp/issues/236 |
| 6 | Post-TPAC: VanderSloot on a different policy meaning, Hofmann “second permissions policy” (30 Oct) | OK + ADDED | Added Archibald’s replies (30 Oct “just a naming change”, 2 Nov 10:10 UTC “a single policy for the external tools to be exposed at the top level”) — the policy shape is undecided | same |
| 7 | Mozilla’s refreshed position not posted | OK | Re-checked 2 Nov: no new comment since 26 Aug | mozilla/standards-positions#1412 |
| 8 | WebKit oppose (3 Jun / label 11 Jun), five arguments, 17 Jun follow-up, issue closed | OK | Re-checked 2 Nov: closed, last update 17 Jun, labels match the text | https://github.com/WebKit/standards-positions/issues/670 |
| 9 | TAG early review filed 11 Jun; labels of 10 Jul incl. “Missing: Multi-stakeholder support” | OK | Re-checked 2 Nov: labels unchanged | https://github.com/w3ctag/design-reviews/issues/1238 |
| 10 | Old text: TAG had no position, waiting until after TPAC | CHANGED (by G) | New section on the 26 Oct early comment (explicitly not a resolution); last update on the issue is that comment (re-checked 2 Nov) | same |
| 11 | TAG comment contents (Finding on agentic browsing, web for agents, declarative first, i18n, JSON Schema, rename to “Tools”) | OK (G, 2 Nov) | Kept | same |
| 12 | Yoav Weiss / Shopify storefront tools; vendor benchmark 5–10× tokens, 4–5× slower (labelled vendor claim) | OK (G) | Kept with the caveat | same |
| 13 | Chrome: dev trial from 146, OT 149→156, extended to 162 on 28 Sep, chromestatus quote | OK | the shared validation notes unchanged; text says the entry did not change | https://chromestatus.com/feature/5117755740913664 |
| 14 | Chrome 156 stable 20 Oct; 157 stable 3 Nov; 162 stable 2 Feb 2027 | OK | Re-checked on Chromium Dash: 157 stable_date 2026-11-03, 162 stable_date 2027-02-02 | https://chromiumdash.appspot.com/schedule |
| 15 | Edge OT live in Edge 150, expires 30 Mar 2027 | OK | Kept (the shared validation notes) | Edge OT page; implementation-status.md |
| 16 | Local testing: chrome://flags/#enable-webmcp-testing ↔ WebMCPTesting | OK | Probe in the shared validation notes and ch15 tests 2 Nov | https://developer.chrome.com/docs/ai/webmcp |
| 17 | Token delivery: meta tag, header, script-injected meta | OK | Kept | https://developer.chrome.com/docs/web-platform/origin-trials |
| 18 | Listing 15.1 origin-trial-head.html + headers | OK | Byte-identical (check-listings 2 Nov) | demo files |
| 19 | Table 15.1 breaking spec changes (#132, #184, #200, #225, #246, #330, #338, #339) with dates | OK | #338 and #339 dated 8 Oct (GitHub API; the shared validation notes’s 13 Oct for #338 is wrong) | https://github.com/webmachinelearning/webmcp/commits/main |
| 20 | Commits 15 Oct–2 Nov: #345, #347, #352, #334, #326; IDL unchanged | OK | the shared validation notes–1.3 | spec repo |
| 21 | Open PRs #348, #254, #204, #355 not merged | OK + ADDED | Added: Chromium main already implemented the `Tool` interface (CL 8510757, 15 Oct) ahead of #348 | https://chromium-review.googlesource.com/c/chromium/src/+/8510757 |
| 22 | Chrome overview page (7 Oct) still describes two APIs | OK | Page re-read 2 Nov, still updated 7 Oct | https://developer.chrome.com/docs/ai/webmcp |
| 23 | Error types: Chromium 156 still UnknownError | OK + ADDED | Added: CL 8546218 (16 Oct, #1720407) switches executeTool() to specific DOMExceptions; after M157 branch (#1717349), before M158 (#1727472) → expected in Chrome 158, not tested | https://chromium-review.googlesource.com/c/chromium/src/+/8546218 ; https://chromiumdash.appspot.com/fetch_milestones |
| 24 | #361 serialization ruling (26 Oct), undefined → null proposal | OK | Re-checked 2 Nov: open, last activity 26 Oct | https://github.com/webmachinelearning/webmcp/issues/361 |
| 25 | Listing 15.2 webmcp-support.js and its feature-detection behaviour | OK | Byte-identical; 4 Playwright tests pass 2 Nov (full surface, tools=() policy blocks, no flag, legacy navigator mock) | demo tests |
| 26 | implementation-status.md: Chrome, Edge, Brave (Leo, Nightly flag), ChatGPT Desktop, Meta Ray-Ban Display, Firefox/Safari | OK (G, 2 Nov) | Kept; the shared validation notes confirms the page | https://github.com/webmachinelearning/webmcp/blob/main/implementation-status.md |
| 27 | ChatGPT Atlas retired (9 Jul 2026) | OK (G) | Kept | OpenAI help centre (fn ch15-24) |
| 28 | Shopify “deploys WebMCP across millions of storefronts” (26 Oct, strategy issue) | OK (deployer claim, labelled) | Strategy issue re-checked 2 Nov: 13 comments, last 30 Oct | https://github.com/w3c/strategy/issues/576 |
| 29 | MCP-B packages 6.0.3 (14 Oct), MIT | OK | npm re-checked for @mcp-b/webmcp-polyfill 6.0.3 (14 Oct) | https://registry.npmjs.org/@mcp-b/webmcp-polyfill |
| 30 | Chrome imperative-api: React → use-webmcp-tool 0.3.0 (Apache-2.0), Vue `@vueuse/core` (16 Oct) | OK | the shared validation notes item 6 | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 31 | WG history: #192 (28 May), WebML charter PR (9 Jun), 13 Aug resolution and Apple objection warning, 28 Sep change of course, PR closed 13 Oct | OK (G, 2 Nov) | Kept | https://github.com/webmachinelearning/webmcp/issues/192 ; https://github.com/w3c/charter-drafts |
| 32 | WebML WG chartered until 30 Apr 2027 | OK | Kept | https://www.w3.org/groups/wg/webmachinelearning/ |
| 33 | Agentic Web WG charter: refinement since 1 Oct (est. until ~10 Nov), label “In Charter Refinement” | OK | Re-checked 2 Nov: labels AI, Horizontal review requested, In Charter Refinement, charter | https://github.com/w3c/strategy/issues/576 |
| 34 | Charter PR #901 (merged 29 Oct): “Site Capabilities for Agents”, initial input WebMCP; tentative Identity/Delegation/Measurement; Interaction Modes note | OK (G, 2 Nov) | Kept | https://github.com/w3c/charter-drafts/pull/901 |
| 35 | Process: refinement ≥ 28 days, Formal Objections → Council | OK | Kept | https://www.w3.org/policies/process/ |
| 36 | CR exit: two independent interoperable implementations | OK | Kept | charter draft |
| 37 | Listing 15.3 standards-watch.mjs; Listing 15.4 snapshot 2026-11-02.json | OK | Byte-identical; parser tests 7/7 pass 2 Nov; snapshot is the first live run of 2 Nov | demo files |
| 38 | Figure 15.1 timeline | CHANGED | Redrawn; adds 15–16 Oct Chromium main changes, 20 Oct stable, 26 Oct TAG comment + TPAC, 27 Oct draft, 29 Oct charter deliverable, the two editions; caption no longer claims the 15 months run to 2027 | — |
| 39 | Figure 15.2 routes | CHANGED | Redrawn: WebML route closed, Agentic Web WG route (Site Capabilities for Agents), stays-in-CG route including #236 reshaping | — |

Unverified, said so in the text: Chrome 158 behaviour (inferred from Chromium commit positions); third-party consumer claims on implementation-status.md and the Shopify/benchmark numbers (labelled as the vendors’ own claims).

#### Demo changes

- `chapters/15-browser-support-and-standards`: no code change. `snapshots/2026-11-02.json` and `standards-watch.mjs` were last written by the reviewer on 2 Nov 2026 (09:00 UTC), and the chapter prints them. README updated (Listing 15.4 row now points at the 2 Nov snapshot, second-edition status line). `npm test` with `CHAPTER_MD` set, 2 Nov 2026 (Node 22, Playwright 1.64.1, Chromium 156.0.8078.4): 12/12 pass (check-listings 1, standards-watch parsers 7, webmcp-support Playwright 4). node_modules deleted.

#### Figures

- Figure 15.1 redrawn as SVG (figures/src/figure-15-1.svg): vertical timeline, four colour-coded lanes (spec, browsers, positions/TAG, W3C process), with both editions marked.
- Figure 15.2 redrawn as SVG (figures/src/figure-15-2.svg): three routes from the CG draft, each with what it means for your code.

### Chapter 16: Product and Business Implications


2 November 2026. Checked against the shared validation notes and primary sources read on 2 November 2026 (Chrome for Developers pages, the WebMCP spec dated 27 October 2026, the explainer and supplementary explainers, GitHub issues/PRs via the API, chromestatus, w3c/strategy#576). Source texts and quotes are saved in the editor's source notes.

| # | Claim in chapter | Source | Result | Action |
|---|---|---|---|---|
| 1 | Chrome overview: published 18 May, updated 7 Oct 2026, “Use cases”, “Limitations”, discoverability quote | developer.chrome.com/docs/ai/webmcp | Verified | none |
| 2 | Best practices quotes (context window, overlapping tools, “Register tools all at once”, “Roll back the whole batch on failure”, share the application service) | best-practices, updated 30 Oct 2026, authors Klepper, Salnikov, Beaufort | Verified, page updated since v1 | Added all-or-nothing registration to text, Listing 16.4 and demo; footnote ch16-3 updated with authors and date |
| 3 | compare-mcp: call center / in-store expert, “Manage core logic with MCP”, “Build a contextual UI with WebMCP”, “foundational service layer”, “platform-agnostic and always available to agents”, comparison table | compare-mcp, rewritten 27 Oct 2026 | Old quotes in v1 text no longer on page | Rewrote the two-surfaces section on the new quotes, ch16-5 updated |
| 4 | build-tools: “Start by identifying journeys where agentic support offers the most added value”, telemetry/interaction logs loop, version pinning | build-tools, updated 30 Oct 2026, authors Bandarra and Salnikov | Verified | New footnote ch16-25 |
| 5 | Evals failure modes | evals page, updated 28 May 2026 | Verified | none |
| 6 | Character budgets 500/150/30/1500 | secure-tools, updated 1 Sep 2026 | Verified | none |
| 7 | Use-cases quotes (purchases, repeat purchases, warranty claim) | use-cases page | Verified | none |
| 8 | Spec sections 4.2.2, 4.3.1, 4.3.2, 6.3.2, 6.3.3, 6.4.4, 6.4.5 | spec, Draft CG Report 27 Oct 2026 | Numbers and titles unchanged, IDL unchanged | Footnotes re-dated to 27 Oct |
| 9 | `execute` receives input and `{ signal }` only; events carry tool name only | spec IDL + demo run in Chromium 156.0.8078.4 | Verified | none |
| 10 | Declarative API removed from spec (PR #338) | GitHub PR #338 | Merged 8 Oct 2026 | Book says 8 Oct. An earlier working note said 13 Oct, which is the date of a later comment, not the merge. Beaufort’s “imperative first” comment is 13 Oct |
| 11 | `SubmitEvent.agentInvoked` called “unspecified and incomplete” | w3c/strategy#576, Grigorik 26 Oct 2026, webmcp #365 open | Verified | New, ch16-26 |
| 12 | “Shopify deploys WebMCP across millions of storefronts” | w3c/strategy#576, Grigorik 26 Oct 2026 | Verified (vendor’s own statement, not independently checked) | Attributed in text |
| 13 | EU CRD Art. 8(2): “whether an agent’s click satisfies that is an open question” | w3c/strategy#576, GitHub user frmoretto, 26 Oct 2026 | Verified. Commenter’s real name not confirmed, so cited by handle only | ch16-26 |
| 14 | Tool collections / skills deferred 3 Sep, harness feedback 20 Oct | #161, #255 | Verified, both open | ch16-24 updated |
| 15 | Elicitation: igrigorik proposal 26 Oct on #165, #204 handed over 29 Oct | #165, #204 | Verified, both open | ch16-28 added |
| 16 | #236 post-F2F second permissions policy discussion | #236 comments 30 Oct | Verified | ch16-27 |
| 17 | Implementation status page (vendors, Meta Ray-Ban listed as upcoming) | implementation-status.md, unchanged since 14 Oct | Verified. Phrase “coming soon” avoided | none |
| 18 | Chromestatus “Proposed”, 7 owners, OT to M162 | chromestatus, updated 28 Sep | Verified | none |
| 19 | Service-worker explainer, static manifests in Alternatives Considered | explainer + service-workers.md | Verified, unchanged | none |
| 20 | Demo results (“tested on 2 November 2026”) | demo runs on Chromium 156.0.8078.4, Playwright 1.64.1 | See report: suites rerun 2 Nov | ch16-2 states the date |

Nothing in the chapter relies on an unverified number. The chapter contains no invented anecdotes: Trailhead, Kari and Jonas are the book’s running fictional example, presented as such in earlier chapters.

### Chapter 17: The Road Ahead


2 November 2026. Same sources as the Chapter 16 file, plus the MCP 2026-07-28 spec (still the current protocol version on 2 November 2026), standards-positions threads, the TAG review and the W3C charter drafts.

| # | Claim | Source | Result | Action |
|---|---|---|---|---|
| 1 | Spec draft date | spec | Now 27 Oct 2026 (v1 text: 15 Oct) | Updated throughout |
| 2 | §6.3.4 is a TODO, PR #326 open | spec, PR #326 | **Changed:** #326 merged 27 Oct, §6.3.4 is now “Interaction with the Same-Origin Policy” with §6.3.4.1 “Enforcing Same-Origin Isolation via Two-Sided Opt-In” | Rewrote the paragraph, table row, summary and ch17-20 |
| 3 | OT to Chrome 162, chromestatus “Proposed”, 7 owners | chromestatus (updated 28 Sep) | Verified | none |
| 4 | Edge OT to 30 Mar 2027 | Edge OT page | Verified | none |
| 5 | PR #338 merged 8 Oct, Chrome’s “imperative first” | PR #338 | Merged 8 Oct. Comment is François Beaufort’s, 13 Oct. v1 note called it “the author’s comment” | Named Beaufort, fixed ch17-7. **the shared validation notes date 13 Oct is updated_at: flag** |
| 6 | Output schemas: #9 resolution 5 Feb, PR #254 open, author experimenting | #9, #254 | Verified, PR still open | Added #92 debate (Beaufort 14 Oct, Dallstream 16 Oct, Hofmann 30 Oct) and kenchris’s 20 Oct note |
| 7 | MCP 2026-07-28 outputSchema / structuredContent / sessions removed | modelcontextprotocol.io | Verified, still current version | none |
| 8 | #86 closed 28 Sep with Farolino quote | #86 | Verified | none |
| 9 | #41 size concerns | #41 comment 20 Oct | Verified | Added one sentence |
| 10 | #135 resolutions 16 Apr and 1 Oct, continuation explainer (Foltz, PR #327 merged 2 Oct), 60 s | #135, continuations-explainer.md | Verified, explainer unchanged since 14 Oct | Named Mark Foltz |
| 11 | Service-worker explainer | docs/service-workers.md | Verified, unchanged | none |
| 12 | native-agent keyword | explainer Open Questions | Verified, unchanged | none |
| 13 | #317 Farolino quote, Sagar `*` comment | #317 | Verified, open | Added Sagar 26 Oct |
| 14 | #299 closed 25 Sep, quote | #299 | Verified | none |
| 15 | #344 opened and closed 14 Oct, Farolino quotes | #344 | Verified. v1 said “the day before this chapter was written” | Replaced with dates, added Beaufort 15 Oct follow-up |
| 16 | #332 ordering mismatch | #332 | Open, Beaufort comments 15 and 28 Oct | Added |
| 17 | #331 sensitiveHint | #331 | Open | none |
| 18 | Elicitation #165 / PR #204, security guide still mentions requestUserInteraction() | #165, #204, secure-tools | Verified. #204 picked up by Samuel Dallstream 29 Oct, Grigorik proposal 26 Oct | Added |
| 19 | #161/#255 deferred 3 Sep | #255 | Verified, harness feedback 20 Oct | Added |
| 20 | WebKit “oppose” quotes | WebKit/standards-positions#670 | Verified | none |
| 21 | #236 Archibald quotes, handles, Mozilla #1412 neutral | #236, mozilla#1412 | Verified, plus 30 Oct comments (VanderSloot, Hofmann, Archibald “just a naming change”) | Added, ch17-36 |
| 22 | TAG review open, “Missing: Multi-stakeholder support” | w3ctag/design-reviews#1238 | Verified, plus early comment 26 Oct (not a resolution, Finding on Agentic Browsing, “web for agents”, declarative first, first JSON Schema API, rename to “Tools”?) | Added in two places. Commenter not named because authorship was not confirmed |
| 23 | charter-drafts #829 closed 13 Oct, Apple quotes | charter-drafts#829 | Verified | none |
| 24 | Agentic Web WG draft charter, refinement from 1 Oct to about 10 Nov | charter draft, strategy#576, public-new-work mail | Verified as an estimate | Phrased as the W3C team’s estimate |
| 25 | strategy#576 late-Oct comments (Shopify scale, agentInvoked, EU CRD), charter-drafts#901 Agent Identity / Delegation | strategy#576 | Verified | Added, ch17-35 |
| 26 | Chrome guidance: register all at once, roll back, share the application service | best-practices, 30 Oct | Verified | New checklist item 3 and item 1 note, ch17-37 |
| 27 | “Record and isolate the specification revision, browser version, agent client, and model” | build-tools, 30 Oct | Verified | Checklist item 11, ch17-38 |
| 28 | Probe JSON and “fourteen checks pass in both modes” | demo run 2 Nov 2026, Chromium 156.0.8078.4 | Verified: 14/14 mock, 14/14 Chromium flag | v1 said thirteen, now fourteen with the rollback test |
| 29 | TPAC dates | notes | TPAC week 26–30 Oct | No city named |

No invented anecdotes. Lars, Kari, Jonas and Trailhead are the book’s established fictional example.

#### Added after re-reading the shared validation notes (STATUS: final)
| 30 | PR #348 `Tool` interface (Farolino, 15 Oct, open) | PR #348 / the shared validation notes item 14 | Verified | Added to the generic-call-API section and Table 17.1, ch17-39 |
| 31 | Spec §6.2 text from PR #334 (20 Oct): manipulation “is primarily the responsibility of the agent’s own security model …”, points to the Agentic Web WG | spec 27 Oct, the shared validation notes item 9 | Verified | Added to “Who decides”, ch17-40 |
| 32 | #361: result serialisation, Beaufort: “The WPT assertions are wrong, and so is Chrome.” | #361, the shared validation notes item 10 | Verified | Checklist item 9 now says Chromium’s string serialisation is the browser’s bug, ch17-41 |
| 33 | PR #338 merge date | the shared validation notes final | the shared validation notes now agrees with 8 Oct | No flag needed |

### Appendix A: API Quick Reference (IDL, Attributes, Events, Errors)


2 November 2026. Sources checked first-hand this session: the spec (https://webmachinelearning.github.io/webmcp/, Draft CG Report dated 27 October 2026, IDL index extracted and diffed against Listing A.1), the GitHub API for every issue/PR cited, Chrome docs via the shared validation notes v1 (imperative-api 16 Oct, declarative-api 25 Sep), chromiumdash. Demo probes re-run in Chromium 156.0.8078.4.

#### Appendix A: API Quick Reference

| # | Claim / API / listing (short quote, old line no.) | Status | Now (what the text says after the edit) | Source URL |
|---|---|---|---|---|
| 1 | "checked against the WebMCP Draft Community Group Report dated 15 October 2026" (l.9) | CHANGED | Checked against the 27 October 2026 draft, read 2 Nov 2026; IDL identical to 15 Oct | https://webmachinelearning.github.io/webmcp/ |
| 2 | Listing A.1, IDL index "(15 October 2026)" (l.15–99) | OK (relabelled) | Listing A.1 byte-identical to `webmcp.idl`; normalised diff vs 27 Oct IDL index = 0 lines; label now "(27 October 2026 draft)" in house style listing format | https://webmachinelearning.github.io/webmcp/#idl-index |
| 3 | Editors: three (fn appa-2) | CHANGED | Four editors, Samuel Dallstream (Microsoft) added 20 Oct by PR #352 (merged 2026-10-20) | https://github.com/webmachinelearning/webmcp/pull/352 |
| 4 | `document.modelContext`, SecureContext, no `navigator` (l.103) | OK | unchanged; re-tested 2 Nov | spec §4.1 |
| 5 | No `unregisterTool()`, unregister by abort (l.104) | OK | unchanged | spec §4.2 |
| 6 | `executeTool()` resolves a DOMString (l.105) | OK + added | plus pointer to the serialization disagreement (A.4) | spec IDL |
| 7 | Table A.1 registration rules, `InvalidStateError`/`TypeError` | OK | re-tested 2 Nov, same results | spec registerTool steps |
| 8 | Table A.2 annotations (4 members, default false) | OK + added | `debugging` "available from Chrome 156" (Chrome docs) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 9 | Annotations are hints, agent policy (l.128) | OK + added | new spec text (PR #334, 20 Oct): a malicious site can omit/misrepresent hints, agent's security model is responsible | https://github.com/webmachinelearning/webmcp/pull/334 |
| 10 | Unregister doesn't cancel in-flight calls (l.137) | OK + added | Chrome docs date it to Chrome 153 | imperative-api |
| 11 | Table A.4 `RegisteredTool`, empty title "" | OK | re-tested | spec getTools steps |
| 12 | Issue #224 "open on 15 October 2026" | CHANGED | still open on 2 November 2026 (API) | https://github.com/webmachinelearning/webmcp/issues/224 |
| 13 | executeTool lookup / missing input → {} / signal | OK + added | Chrome docs: returns null when a navigation is triggered; JSON-string input deprecated from Chrome 155 | imperative-api |
| 14 | Table A.5 results: draft vs Chromium (string unquoted, undefined → "undefined", 10n → "10") | OK + added | re-tested; new Still-in-flux box: issue #361 (opened 23 Oct) confirms in 156.0.8078.48 and 158.0.8119.0, WPT follows Chrome, F. Beaufort 26 Oct: "The WPT assertions are wrong, and so is Chrome…", proposes undefined → "null"; not merged (quote verified in the issue comments via API) | https://github.com/webmachinelearning/webmcp/issues/361 |
| 15 | Table A.6 events | OK + added | Chrome docs: `window.ontoolactivated`/`window.ontoolcancel` not supported from Chrome 156, both events non-cancelable | https://developer.chrome.com/docs/ai/webmcp/declarative-api |
| 16 | Permissions Policy `tools`, default 'self', `tools=()` (A.6) | OK + added | §6.4.1 anchor still exists; new §6.3.4 "Interaction with the Same-Origin Policy" / 6.3.4.1 "Enforcing Same-Origin Isolation via Two-Sided Opt-In" names the three gates (PR #326 merged 27 Oct) | https://github.com/webmachinelearning/webmcp/pull/326 |
| 17 | Table A.7 exception names, "15 October 2026 draft" | CHANGED (label) | same names in 27 Oct draft (PR #339 merged 8 Oct, #347 merged 15 Oct); re-tested all Chromium cells | spec §3, §4.2 |
| 18 | Renderer kill, crbug 573722078 (fn appa-22) | OK + UNVERIFIED | still reproduces in 156.0.8078.4 on 2 Nov; whether a later build has the fix is unverified (issues.chromium.org not checked, only Chrome 149/156 test builds on the box) | https://issues.chromium.org/issues/573722078 |
| 19 | Listing A.2 `classifyToolError` | OK | unchanged, byte-identical to `classify-tool-error.js`, its unit check passes | demo |
| 20 | Still in flux: UnknownError replaced 8 Oct (PR #339) | OK | merged 2026-10-08T17:58Z (API) | https://github.com/webmachinelearning/webmcp/pull/339 |
| 21 | Issue #234 "open on 15 October 2026" | CHANGED | still open on 2 November 2026; pointer to PR #348 | https://github.com/webmachinelearning/webmcp/issues/234 |
| 22 | Declarative API removed 8 October 2026 (PR #338) | OK | merged 2026-10-08T11:26:24Z per API. | https://github.com/webmachinelearning/webmcp/pull/338 |
| 23 | Table A.8 declarative surface (Chrome page 25 Sep) | OK | page unchanged per the shared validation notes (Wayback diff); re-tested form tool in Chromium 156 | declarative-api |
| 24 | (new) Explainer: `toolcanceled` → `toolcancel`, events at ModelContext or <form> | ADDED | PR #350 merged 16 Oct | https://github.com/webmachinelearning/webmcp/pull/350 |
| 25 | (new) Chrome 156 stable since 20 Oct, 157 on 3 Nov | ADDED | chromiumdash | https://chromiumdash.appspot.com/schedule |
| 26 | (new) A.9 open PRs #348 Tool interface (domfarolino, upd. 27 Oct), #254 outputSchema (beaufortfrancois, 26 Oct), #204 requestUserInput (bwalderman, 29 Oct), #355 openWorldHint (kenchris, draft, 20 Oct), #358 (kenchris, 20 Oct) | ADDED | all open on 2 Nov per API; described as proposals, not spec | https://github.com/webmachinelearning/webmcp/pulls |
| 27 | Footnotes "Read 15 October 2026" for re-checked pages | CHANGED | "(retrieved November 2026)" where re-checked; historical commit footnotes keep their original read dates | — |

#### Demo changes
- `appendices/a-api-reference/README.md`: Listing A.1 row (27 Oct draft) and a new "Result (2 November 2026, second edition)" section. No code changed; `webmcp.idl` and `classify-tool-error.js` are byte-identical to Listings A.1 and A.2.
- Tests: `node tests/run-tests.mjs` with playwright@1.64.1 (no browser download, cached Chromium 156.0.8078.4): **25 passed, 0 failed** (2 Nov 2026). node_modules deleted afterwards.

#### Figures
- Appendix A has no figures.

### Appendix B: Glossary


2 November 2026. Scope: targeted validation of the terms that changed (158 terms, the rest re-checked by reading against the shared validation notes v2 final and the 27 Oct spec IDL, which is identical to 15 Oct). Every URL in the appendix was fetched on 2 Nov 2026 (all 200, see appendix-c validation for the method).

#### Appendix B: Glossary

| # | Claim / API / listing | Status | Now | Source URL |
|---|---|---|---|---|
| 1 | Intro "read on 14 October … checked again on 15 October 2026" | CHANGED | adds re-check against the 27 Oct draft and pages as of 2 Nov | spec, the shared validation notes v2 |
| 2 | Still in flux "not in the 15 October 2026 draft" | CHANGED | 27 Oct draft, plus pointer to open PRs (`Tool` interface) | https://webmachinelearning.github.io/webmcp/ |
| 3 | annotations: members readOnlyHint, untrustedContentHint, consequentialHint, debugging, default false | OK | same in 27 Oct IDL ("In the 27 October draft") | spec §4.2.1 |
| 4 | `debugging` | OK + added | "available from Chrome 156" (Imperative API page, 16 Oct) | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 5 | `outputSchema` "adding it is open spec work" | OK + added | PR #254 open, updated 26 Oct | https://github.com/webmachinelearning/webmcp/pull/254 |
| 6 | RegisteredTool | OK + added | PR #348 proposes a `Tool` interface keyed by a unique ID (open, updated 27 Oct) | https://github.com/webmachinelearning/webmcp/pull/348 |
| 7 | `requestUserInteraction()` "issues #165 and #204 discuss replacing it" | CORRECTED | #204 is a pull request ("Replace requestUserInteraction with requestUserInput", open, updated 29 Oct, modes interactive/form/url) | https://github.com/webmachinelearning/webmcp/pull/204 |
| 8 | `usewebmcp` 6.0.3 | OK + added | still 6.0.3 on 2 Nov; Chrome's page now points to `use-webmcp-tool` | registry |
| 9 | (new) `use-webmcp-tool` entry | ADDED | 0.3.0 on 2 Nov, Chrome quote verbatim, Vue `useWebMCP` in @vueuse/core | imperative-api, registry |
| 10 | (new) two-sided opt-in entry | ADDED | spec §6.3.4.1 (PR #326, 27 Oct): three gates allow="tools", exposedTo, fromOrigins; §6.3.4.2 residual risks | https://webmachinelearning.github.io/webmcp/#interaction-with-same-origin-policy |
| 11 | TAG #1238 "still open on 15 October 2026" | CHANGED | still open 2 Nov, early comment 26 Oct | https://github.com/w3ctag/design-reviews/issues/1238 |
| 12 | TPAC "runs from 26 to 30 October" | CHANGED | past tense, charter discussed | the shared validation notes v2 §1.9 |
| 13 | standards position: Mozilla neutral "On 15 October 2026" | CHANGED (date) | still neutral 2 Nov | https://github.com/mozilla/standards-positions/issues/1412 |
| 14 | WebMCP: Draft CG Report (15 October 2026) | CHANGED | 27 October 2026 | spec |
| 15 | polyfill / webmcp-types versions | OK | unchanged on 2 Nov | registry |
| 16 | MCP tool annotations (openWorldHint etc.) | OK | MCP 2026-07-28 unchanged; WebMCP has no openWorldHint (proposed in open PR #355, not added to the glossary as it is a draft PR) | the shared validation notes v2 §1.2 |
| 17 | origin trial Chrome 149–162, Edge to 30 Mar 2027 | OK | unchanged | the shared validation notes v2 §1.7 |
| 18 | Agentic Web WG, refinement until ~10 Nov | OK | unchanged | the shared validation notes v2 §1.9 |
| 19 | Other footnotes "Read 15 October 2026" | OK (reachability) | URLs re-fetched 2 Nov, all 200; content of those pages not re-read word by word unless listed above | — |

#### Demo changes
- None (Appendix B has no demo folder).

#### Figures
- Appendix B has no figures.

### Appendix C: Resources and Further Reading


2 November 2026. Every URL in the four appendices (118 unique) was fetched by script on 2 November 2026 with a browser User-Agent (GET, redirects followed); new URLs added in this edition were fetched too. Full results: tasks folder urlcheck.json (the reviewer); summary below.

#### Appendix C: Resources and Further Reading

| # | Claim / API / listing | Status | Now | Source URL |
|---|---|---|---|---|
| 1 | "Every URL here was fetched on 14 October 2026 … 15 October 2026" | CHANGED | re-fetched 2 Nov 2026: all HTTP 200 except (a) npmjs.com pages 403 bot check → registry records used and all 200, (b) github.com/webmaxru/webmcp-book and webmcp-book-demos 404 for anonymous readers (private repos), (c) webmcp.salnikov.no not serving yet (connection error; DNS/SWA not set up), (d) docs/proposal.md@adbc2c5 429 rate limit | script |
| 2 | Spec date "read 15 October 2026" | CHANGED | 27 October 2026, four editors | https://webmachinelearning.github.io/webmcp/ |
| 3 | C.2 Chrome pages: Imperative "updated 21 September 2026" | CHANGED | updated 16 October 2026 | the shared validation notes §1.10 |
| 4 | compare-mcp "updated 19 May 2026" | CHANGED | published 11 March 2026, updated 27 October 2026 (rewritten, new table) | the shared validation notes §1.10, §2.5 |
| 5 | best-practices "(18 May 2026)" | CHANGED | updated 30 October 2026, byline Alexandra Klepper, Maxim Salnikov, François Beaufort; new architectural-constraints guidance | the shared validation notes §1.10, §2.1–2.2 |
| 6 | build-tools "(26 August 2026)" | CHANGED | updated 30 October 2026, byline André Cipriani Bandarra, Maxim Salnikov | the shared validation notes §1.10, §2.3 |
| 7 | webmcp overview (7 Oct), declarative (25 Sep), secure-tools (1 Sep), evals (28 May), use-cases, agents/security (9 Jun) | OK | unchanged dates | the shared validation notes §1.10 |
| 8 | (new) /docs/ai/agents, blog/webmcp-epp (10 Feb 2026), Chromium Dash, Chrome Web Store listing of the Inspector, VueUse useWebMCP, use-webmcp-tool, @vueuse/core | ADDED | all 200 (npm via registry) | URLs in text |
| 9 | chromestatus "Proposed on 15 October 2026" | CHANGED | now described by its trial milestones (149→156, extended to 162); status word not repeated | https://chromestatus.com/api/v0/features/5117755740913664 |
| 10 | chrome-devtools-mcp, WebMCP flag | OK + added | `--categoryExperimentalWebmcp` | the shared validation notes §1.8 |
| 11 | Edge OT expiry 30 March 2027 | OK | unchanged | the shared validation notes §1.7 |
| 12 | Mozilla neutral "on 15 October 2026" | CHANGED (date) | still neutral 2 Nov; refreshed position announced, not published | the shared validation notes §1.9 |
| 13 | TAG #1238 "Open on 15 October 2026" | CHANGED | still open; early non-resolution comment 26 Oct (Christian Liebel), incl. the "rename to Tools" question | https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845 |
| 14 | Agentic WG draft charter "many fields still template placeholders" | CHANGED | fetched 2 Nov: start/end dates and chairs still template fields; agent identity listed among possible future deliverables | https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html |
| 15 | strategy #576 | OK + added | TPAC 2026 (26–30 Oct, Dublin), still "In Charter Refinement" | the shared validation notes §1.9 |
| 16 | MCP `latest` redirects to 2026-07-28 | OK | still true 2 Nov (fetched) | https://modelcontextprotocol.io/specification/latest |
| 17 | SDK Tier 1 list | OK | TypeScript, Python, C#, Go, Rust, Ruby still Tier 1 (Java Tier 2) on the SDK page, fetched 2 Nov | https://modelcontextprotocol.io/docs/sdk |
| 18 | Table C.1 versions "15 October 2026" | CHANGED | two columns: demos pin (Oct) and registry latest 2 Nov: server/client 2.4.0, node 2.1.2, inspector 2.13.0, Angular 22.2.4, rest unchanged; added use-webmcp-tool 0.3.0 and @vueuse/core 15.0.0 | https://registry.npmjs.org/ |
| 19 | C.9 website URL vibeprogrammer.github.io/webmcp-book | CHANGED | https://webmcp.salnikov.no (house style rule 8, planned home; not serving on 2 Nov) | — |
| 20 | Demo repo links | UNVERIFIED for readers | the demos and book repos return 404 to anonymous users (private). Lead/Maxim: decide visibility or ship demos as a zip; the book text links them per house style rule 8 | — |
| 21 | Table C.2 rows for other chapters' demos | OK (not re-validated) | checked with each chapter. The Chapter 10 row says `usewebmcp`, which matches Chapter 10's demo (Trailhead stays on `usewebmcp`; `use-webmcp-tool` is covered in the text) | — |

#### Demo changes
- None (Appendix C has no demo folder).

#### Figures
- Appendix C has no figures.

### Appendix D: Migration Notes: navigator.modelContext and provideContext() to document.modelContext


2 November 2026. Sources: spec IDL (27 Oct draft, diffed against 15 Oct = identical), GitHub API (PR/issue states and merge times), README commit history (last change 8 Oct), Chrome docs via the shared validation notes v1 (imperative-api 16 Oct, best-practices 30 Oct), chromiumdash.

#### Appendix D: Migration Notes

| # | Claim / API / listing (short quote, old line no.) | Status | Now | Source URL |
|---|---|---|---|---|
| 1 | Epigraph: README "currently focused on the imperative document.modelContext.registerTool() API" (Oct 2026) | OK | still verbatim on the README (fetched 2 Nov); README last changed 8 Oct (PR #338); attribution now "November 2026" | https://github.com/webmachinelearning/webmcp |
| 2 | Table D.1 dates (5 Mar #132 … 8 Oct #338/#339) | OK | not re-derived from git log this time; #338 and #339 merge times re-checked via API (8 Oct 11:26Z / 17:58Z). Other rows keep the 14/15 Oct verification (fn appd-2) | GitHub API |
| 3 | "after code tested … all 20 checks pass" | CHANGED | re-run 2 Nov: 21/21 (one new check) | demo |
| 4 | Listing D.3 "for the 15 October 2026 draft" | CHANGED | "current draft, dated 27 October 2026" (IDL identical); code comment in after/fjord-tools.js updated, listing byte-identical | spec |
| 5 | Table D.2 caption "to the 15 October 2026 draft" | CHANGED | "to the 27 October 2026 draft" | spec |
| 6 | Table D.2 results row: Chromium passes strings unquoted | OK + added | "which the spec’s editors call a Chrome bug" (issue #361, 26 Oct) | https://github.com/webmachinelearning/webmcp/issues/361 |
| 7 | JSON-string input deprecated from Chrome 155 (fn appd-14, page "updated 21 September 2026") | OK, date CHANGED | page now "last updated 16 October 2026", sentence still there | https://developer.chrome.com/docs/ai/webmcp/imperative-api |
| 8 | Still in flux: requestUserInteraction removed 11 Jun (#205), "#165 and #204 settle a more permanent design" | OK + added | #204 now titled "Replace requestUserInteraction with requestUserInput", open, updated 29 Oct (API) | https://github.com/webmachinelearning/webmcp/pull/204 |
| 9 | Listing D.4 tool set | CHANGED (code) | now rolls back a failed batch (Chrome best-practices 30 Oct "register tools all at once"); new test "a failed replace() rolls back the whole set" passes | https://developer.chrome.com/docs/ai/webmcp/best-practices |
| 10 | Listing D.5 / grep list | OK | unchanged | demo |
| 11 | Figure D.1 caption "February to October 2026" | CHANGED | "February to November 2026", adds the 27 Oct no-IDL-change marker and open proposals | — |
| 12 | (new) D.6 table: #361, React `use-webmcp-tool` / Vue `@vueuse/core` (imperative-api 16 Oct), spec §6.3.4 anchor change (#326, 27 Oct; old anchor `violation-same-origin-boundaries` absent from the spec HTML on 2 Nov, new `interaction-with-same-origin-policy` present), best-practices 30 Oct, Chrome 156 stable 20 Oct / 157 on 3 Nov, OT to 162 | ADDED | all sourced | see footnotes appd-16…22 |
| 13 | (new) Still in flux: next migration (#348, #254, #204, #355 open) | ADDED | states via API 2 Nov | https://github.com/webmachinelearning/webmcp/pulls |
| 14 | Checklist | CHANGED | +item 9 (all-or-nothing registration), item 7 and 10 extended | — |
| 15 | fn appd-12 `docs/proposal.md` at adbc2c5 | OK | page answered 429 (rate limit) to the URL check; commit exists (cited since first edition); not re-read | — |

#### Demo changes
- `appendices/d-migration/after/tool-set.js` (Listing D.4): all-or-nothing rollback in `replace()`.
- `appendices/d-migration/after/fjord-tools.js` (Listing D.3): header comment "27 October 2026 draft".
- `appendices/d-migration/tests/run-tests.mjs`: new check "Listing D.4: a failed replace() rolls back the whole set (all or nothing)".
- `appendices/d-migration/README.md`: result section for 2 Nov 2026.
- Tests: playwright@1.64.1 with cached Chromium 156.0.8078.4: **21 passed, 0 failed** (2 Nov 2026; two earlier attempts timed out on page load while the box was at load average ~55, the third run passed). node_modules deleted.
- All five listings byte-identical to their files (checked by script).

#### Figures
- Figure D.1 redrawn as `figures/src/figure-d-1.svg` (APM palette, vertical timeline instead of the old horizontal one, legend for breaking / porting / no-change, plus a dashed box for the four open PRs as of 2 Nov 2026). Rendered to `manuscript/resources/images/figure-d-1.png` (2400 px wide) and inspected: no clipping or overlaps after one fix (the proposals line was split into two lines).

### About the Author


2 November 2026. Every sentence below is checked against the author facts gathered on 2 Nov 2026 and the author details of Book 2 (Reproducible AI Agent Environments).

#### About the Author

| # | Claim | Status | Source |
|---|---|---|---|
| 1 | Senior Solution Engineer at Microsoft, focused on AI-native developer tools and platforms | OK | Book 2 author details; Sessionize body (AUTHOR-the shared validation notes e) |
| 2 | More than two decades of experience as a developer | OK | Sessionize; Book 2 author details ("two decades") |
| 3 | Previously web frontend/full-stack developer and technical lead | OK | Book 2 author details |
| 4 | Wrote and spoke about PWAs, service workers and Workbox for years | OK | His dev.to corpus 2017–2020 (author voice profile) and GitHub bio "#PWA" |
| 5 | Google Developer Expert in Web Technologies | OK (self-reported, consistent) | GitHub bio "@google Dev Expert in Web"; official GDE directory not checked (JS app) |
| 6 | Microsoft MVP alumnus | OK | Book 2 author details |
| 7 | Co-author of two Chrome WebMCP docs pages: "Build your user's agentic workflows with WebMCP tools" and "WebMCP best practices" | VERIFIED | Bylines on https://developer.chrome.com/docs/ai/webmcp/build-tools and /best-practices (both updated 30 Oct 2026) |
| 8 | Participant in the W3C Web Machine Learning Community Group, which incubates WebMCP | VERIFIED | https://www.w3.org/community/webmachinelearning/participants ; spec header |
| 9 | Maintains the `webmcp` agent skill, part of web-ai-skills in the AI-Native Dev marketplace (webmaxru/ai-native-dev) | VERIFIED | https://github.com/webmaxru/ai-native-dev ; skill at https://github.com/webmaxru/web-ai-agent-skills (skills/webmcp) |
| 10 | Most-installed skill in that set, 531 installs on skills.sh on 2 Nov 2026 | VERIFIED (dated) | https://skills.sh/webmaxru/web-ai-agent-skills/webmcp — Maxim said "popular"; the text uses this concrete signal instead of the word |
| 11 | Maintainer of agentprose, MIT, makes any blog/CMS readable by agents through WebMCP with one script tag | VERIFIED | https://github.com/webmaxru/agentprose ; https://www.npmjs.com/package/agentprose |
| 12 | Based in Oslo, Norway; tech communities lead | OK | GitHub location; Sessionize headline |
| 13 | Founder of multiple developer conferences; organiser of Mobile Era, ngVikings, PWA Summit, Prompt Engineering Conference; runs events for some of Norway's largest web, AI and cloud communities | OK | Book 2 author details ("founder of multiple developer conferences"); GitHub bio (organizer of the four); Sessionize ("runs events for some of Norway's largest…") |
| 14 | Other book: Reproducible AI Agent Environments | OK | Book 2 repo/Book 2 author details |

Left out on purpose: LinkedIn URL (only a search snippet, not verified), follower counts, the claim that he wrote specific sections of the Chrome pages (AUTHOR-the shared validation notes: not stated on the page), any claim of authoring spec text (no issues/PRs by webmaxru found in the WebMCP repo).

#### Short bio (60 words, for store pages)

Maxim Salnikov is a Senior Solution Engineer at Microsoft and a Google Developer Expert in Web Technologies. He co-authored two pages of Chrome's official WebMCP documentation, takes part in the W3C Web Machine Learning Community Group that incubates WebMCP, maintains the webmcp agent skill and the agentprose library, and organises developer conferences and communities in Oslo, Norway.
