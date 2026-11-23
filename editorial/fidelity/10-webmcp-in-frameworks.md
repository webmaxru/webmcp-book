# Fidelity check: Chapter 10, WebMCP in Frameworks

Date: 22 November 2026. Register pass only. Compared with `python3 /tmp/check_fidelity.py manuscript/10-webmcp-in-frameworks.md`.

## Protected spans

Checker: `OK 10-webmcp-in-frameworks.md fences=12 tables=4 figures=3 footnotes=24 quotes=110`.

Counted in the file after editing: 12 fenced blocks (24 fence lines), 3 figure lines (`![Figure 10.1`, `![Figure 10.2`, `![Figure 10.3`), 4 tables (10.1, 10.2, 10.3, and the table’s separator rows included in the checker’s table spans), 24 footnote definitions (`[^ch10-1]` through `[^ch10-24]`). Listing labels and paths were not edited. The H1 was not edited. No callout was added or removed. The *Still in flux* labels were not edited.

## Numbers, dates, and quotes confirmed still present

Versions and dates read in the prose and notes and found unchanged: Vite 8.3.4, TypeScript 7.0.2, React 19.3.1, React Router 8.4.0, `` `usewebmcp` 6.0.3 ``, npm checks on 14 October 2026 and 2 November 2026, Chrome 156 Stable on 20 October 2026, Chromium test build 156.0.8078.4, Chrome’s React-docs change on 16 October 2026, best-practices update 30 October 2026, “As of Chrome 153”, a probe of a tool unregistered 50 milliseconds into a 400-millisecond call, Angular 22.2.2 (examples) and 22.2.4 (latest on 2 November 2026), Angular annotation dates July, August, and September 2026, async-validator note of 21 October 2026, `debugging` on 20 October 2026, 12 Playwright tests for React and 5 for the Angular listings.

Quotes read and found unchanged, including: the epigraph “Register tools when they’re useful in a certain page state, then unregister when the tool is no longer usable.”, “The page must expose either the complete tool surface or none of it. Roll back the whole batch on failure instead of leaving half a workflow callable.”, “signal is aborted without reason”, the Chromium `TypeError` on `inputSchema`, “has experimental support for WebMCP using the use-webmcp-tool package”, “Share the application service”, “to subscribe to an external store”, “Reduce complexity: For most applications, static registration should be the default approach.”, the specification sentence beginning “Unregistering a tool does not cancel an execution”, “As of Chrome 153, you can unregister a tool without cancelling and breaking in-flight executions.”, “If you receive a later abort signal, it’s possible the change was not cancelled and still completed.”, “Only resolve a tool execution with success when the output matches the application state.”, “so a changing closure never churns the registration”, “will remain accessible to AI agents even after the user has navigated to a different route”, and “by default, async validators don’t block submission”.

## Generalized

Tutorial “we” was rewritten as “this chapter” or as a reference to the cart page. “the app logic we already have” became “existing application logic”. “I won’t print untested code here” became “this chapter doesn’t print untested code”. The reason, that the demos folder has no Vue Trailhead, is unchanged. No frequency claim was turned into a general fact.

## Flags

None.
