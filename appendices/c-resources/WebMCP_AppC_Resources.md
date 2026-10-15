*Appendices*

# Appendix C: Resources and Further Reading

> *“Community Groups are for incubation. The Recommendation Track is for standardization.”*
>
> — W3C, Community and Business Groups FAQ[^1]

WebMCP will keep moving after this book is printed, so this appendix is less a reading list than a map of where to look. It lists the primary sources the chapters rely on, grouped by who publishes them, with one line on what each is good for. It then maps the folders of the book’s demos repository to the chapters they belong to, and ends with a short routine for tracking changes yourself.

Every URL here was fetched on 14 October 2026 and fetched again for the technical review on 15 October 2026, and answered with a working page. Dates in the annotations are the dates printed on the pages themselves. A few npm pages served a bot check to my script; for those I give the npm registry’s own record of the package, which is what `npm install` reads.[^2]

## C.1 The specification and its repository

- **WebMCP specification (Draft Community Group Report).** The normative text: the IDL, the algorithms, the security and privacy sections. Check the date under the title first; it read 15 October 2026 when this appendix was last checked. *Chapters 4–7; Appendix A.*
  <https://webmachinelearning.github.io/webmcp/>
- **The webmcp repository and explainer.** The README is the explainer: goals, use cases, open questions and the “Future Exploration” notes. *Chapters 4 and 17.*
  <https://github.com/webmachinelearning/webmcp>
- **Issues.** Where design questions are argued and resolved. Chapter 17 explains how to read an issue thread and which ones to watch.
  <https://github.com/webmachinelearning/webmcp/issues>
- **Pull requests.** Proposed spec changes. A merged pull request is the moment something becomes spec text, or leaves it.
  <https://github.com/webmachinelearning/webmcp/pulls>
- **Commit history.** The fastest way to date a change. The move of the `modelContext` getter from `Navigator` to `Document` (27 May 2026), the removal of `provideContext()` (5 March 2026) and of the declarative API (8 October 2026) are all single commits here. *Appendix D.*
  <https://github.com/webmachinelearning/webmcp/commits/main>
- **Implementation status.** The project’s own list of browsers and agents that support WebMCP, from Chrome’s origin trial to Brave Leo and ChatGPT Desktop. *Chapter 15.*
  <https://github.com/webmachinelearning/webmcp/blob/main/implementation-status.md>
- **Declarative API explainer.** Where the HTML form attributes went when they left the spec. *Chapter 8.*
  <https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md>
- **Continuations explainer.** The proposal for returning a tool’s result across a navigation. *Chapter 17.*
  <https://github.com/webmachinelearning/webmcp/blob/main/continuations-explainer.md>
- **WebMCP for Service Workers.** A supplementary explainer, first published 28 August 2025, about tools for sites that aren’t open. *Chapter 17.*
  <https://github.com/webmachinelearning/webmcp/blob/main/docs/service-workers.md>
- **Contributing guide.** How to take part: the group works under the W3C Community License Agreement, and substantive contributions require joining the Community Group.
  <https://github.com/webmachinelearning/webmcp/blob/main/CONTRIBUTING.md>
- **Web Machine Learning Community Group.** The group that publishes the draft, with its charter and participant list. *Chapter 4.*
  <https://www.w3.org/community/webmachinelearning/>
- **web-platform-tests for WebMCP.** The shared conformance tests the draft links to. Reading a test is often the quickest way to learn what a browser actually does. *Chapters 6 and 14.*
  <https://github.com/web-platform-tests/wpt/tree/master/webmcp>
- **wpt.fyi results.** The same tests, run in every browser’s nightly builds.
  <https://wpt.fyi/results/webmcp>

## C.2 Chrome

- **WebMCP overview** (published 18 May 2026, updated 7 October 2026). Chrome’s introduction, the definition of *actuation*, and how to turn on `chrome://flags/#enable-webmcp-testing`. *Chapters 1, 4 and 9.*
  <https://developer.chrome.com/docs/ai/webmcp>
- **Imperative API** (updated 21 September 2026). Chrome’s guide to `registerTool()` and friends. *Chapters 5 and 6.*
  <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
- **Declarative API** (updated 25 September 2026). The form attributes, events and CSS pseudo-classes that still ship in the trial. *Chapter 8.*
  <https://developer.chrome.com/docs/ai/webmcp/declarative-api>
- **When to use WebMCP and MCP** (updated 19 May 2026). Chrome’s side-by-side of the two. *Chapters 4 and 16.*
  <https://developer.chrome.com/docs/ai/webmcp/compare-mcp>
- **WebMCP best practices** (18 May 2026). Naming, descriptions and tool granularity. *Chapter 11.*
  <https://developer.chrome.com/docs/ai/webmcp/best-practices>
- **Build your user’s agentic workflows with WebMCP tools** (26 August 2026). Chrome’s guide to designing tools around the tasks people actually do. *Chapter 11.*
  <https://developer.chrome.com/docs/ai/webmcp/build-tools>
- **How WebMCP fits in user journeys** (18 May 2026). Chrome’s use cases. *Chapters 16 and 17.*
  <https://developer.chrome.com/docs/ai/webmcp/use-cases>
- **WebMCP tool security** (updated 1 September 2026). Guidance for site authors, including the character budgets, plus the `requestUserInteraction()` text the draft no longer has. *Chapters 11–13.*
  <https://developer.chrome.com/docs/ai/webmcp/secure-tools>
- **Agent security considerations for WebMCP** (9 June 2026). The same topic from the agent builder’s side. *Chapter 12.*
  <https://developer.chrome.com/docs/agents/security>
- **Test WebMCP with Evals** (updated 28 May 2026). Chrome’s eval workflow. *Chapter 14.*
  <https://developer.chrome.com/docs/ai/webmcp/evals>
- **Debug WebMCP tools.** The DevTools WebMCP pane: available tools, invoked tools and command-line flags. *Chapters 9 and 14.*
  <https://developer.chrome.com/docs/devtools/application/webmcp>
- **Chrome DevTools Protocol: WebMCP domain.** The commands and events automation uses to list and invoke tools (`WebMCP.enable`, `WebMCP.invokeTool`, `WebMCP.toolsAdded`). *Chapter 14.*
  <https://chromedevtools.github.io/devtools-protocol/tot/WebMCP/>
- **Join the WebMCP origin trial** (9 June 2026). The announcement: “In Chrome 149, you can sign up for the WebMCP origin trial.” *Chapters 9 and 15.*
  <https://developer.chrome.com/blog/ai-webmcp-origin-trial>
- **Get started with origin trials.** How tokens work and the three ways to deliver one. *Chapters 9 and 15.*
  <https://developer.chrome.com/docs/web-platform/origin-trials>
- **Third-party origin trials.** How an embedded script, such as a widget vendor’s, can register for a trial across the sites that embed it. *Chapter 15.*
  <https://developer.chrome.com/docs/web-platform/third-party-origin-trials>
- **Chrome Platform Status: WebMCP.** Chrome’s feature entry: status (“Proposed” on 15 October 2026), trial milestones and the reasons for the extension. The page renders in script; the JSON form below is easier to read and to watch. *Chapters 4 and 15.*
  <https://chromestatus.com/feature/5117755740913664>
  <https://chromestatus.com/api/v0/features/5117755740913664>
- **The Prompt API** (updated 26 August 2026). Chrome’s on-device model, which the Test Agent and the example extension can use as a planner. *Chapter 9.*
  <https://developer.chrome.com/docs/ai/prompt-api>
- **GoogleChromeLabs/webmcp-tools.** Chrome’s demos, the Model Context Tool Inspector, the eval tool and skills, in one repository. *Chapters 8, 9 and 14.*
  <https://github.com/GoogleChromeLabs/webmcp-tools>
- **Model Context Tool Inspector.** An extension to inspect, monitor and execute a page’s tools by hand or through Gemini. *Chapters 9 and 14.*
  <https://github.com/beaufortfrancois/model-context-tool-inspector>
- **Example Agentic Chrome Extension.** A small, complete agent in the side panel, for testing your tools with a real model. *Chapter 9.*
  <https://github.com/GoogleChromeLabs/webmcp-extension>
- **Chrome DevTools for agents (`chrome-devtools-mcp`).** An MCP server that lets a coding assistant drive Chrome, with experimental WebMCP tools. *Chapter 14.*
  <https://github.com/ChromeDevTools/chrome-devtools-mcp>

## C.3 Microsoft Edge

- **Edge origin trial: WebMCP.** Registration for Edge’s trial, with a trial expiration date of 30 March 2027. *Chapters 9 and 15.*
  <https://developer.microsoft.com/en-us/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a>
- **What’s new in DevTools (Microsoft Edge 149).** Lists “WebMCP debugging” among the updates Edge takes from Chromium. *Chapter 14.*
  <https://learn.microsoft.com/en-us/microsoft-edge/devtools/whats-new/149>

## C.4 Standards positions, reviews and process

- **Mozilla standards position on WebMCP** (issue #1412). Labelled “position: neutral” on 15 October 2026; the thread explains what would move it. *Chapter 15.*
  <https://github.com/mozilla/standards-positions/issues/1412>
- **WebKit standards position on WebMCP** (issue #670). Labelled “position: oppose”, with WebKit’s reasons and its proposed alternative process. *Chapter 15.*
  <https://github.com/WebKit/standards-positions/issues/670>
- **W3C TAG design review** (issue #1238, “Incubation: WebMCP”). Open on 15 October 2026, labelled “Missing: Multi-stakeholder support”. *Chapters 4 and 15.*
  <https://github.com/w3ctag/design-reviews/issues/1238>
- **TAG design reviews repository.** How the TAG takes and prioritises reviews, useful context for reading #1238.
  <https://github.com/w3ctag/design-reviews>
- **The Web Machine Learning Working Group charter pull request** (w3c/charter-drafts #829). The attempt to add WebMCP to that group’s charter, closed on 13 October 2026. *Chapter 15.*
  <https://github.com/w3c/charter-drafts/pull/829>
- **Web Machine Learning Working Group.** The existing W3C Working Group that pull request targeted.
  <https://www.w3.org/groups/wg/webmachinelearning/>
- **Draft Agentic Web Working Group charter.** The proposed new group whose one named normative deliverable is WebMCP. On 15 October 2026 many of its fields were still template placeholders. *Chapters 15 and 17.*
  <https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html>
- **W3C strategy issue #576, “[wg/agenticweb] Agentic Web Group Charter”.** The W3C’s tracking issue for that charter, with its list of known concerns. *Chapter 15.*
  <https://github.com/w3c/strategy/issues/576>
- **Start of charter refinement for the Agentic Web WG** (public-new-work, 1 October 2026). The W3C’s announcement, with the expected end of refinement. *Chapter 15.*
  <https://lists.w3.org/Archives/Public/public-new-work/2026Oct/0002.html>
- **W3C Process Document** (18 August 2025). The rules for Working Groups, charters, the TAG and formal objections. *Chapter 15; Appendix B.*
  <https://www.w3.org/policies/process/>
- **W3C Community and Business Groups FAQ.** What a Community Group can and can’t do. *Chapter 4; Appendix B.*
  <https://www.w3.org/community/about/faq/>

## C.5 The Model Context Protocol

- **MCP specification, version 2026-07-28.** The revision this book follows: stateless, self-contained requests. The `latest` address redirected here on 15 October 2026. *Chapter 3.*
  <https://modelcontextprotocol.io/specification/2026-07-28>
- **Changelog for 2026-07-28.** What changed from the legacy revisions, starting with the removal of the `initialize` handshake. *Chapter 3.*
  <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
- **Tools.** MCP’s tool definition, results, `outputSchema` and annotations; the comparison point for WebMCP’s own. *Chapters 3, 11 and 17.*
  <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>
- **Elicitation.** How an MCP server asks the user a question mid-call; the model for WebMCP’s proposed `requestUserInput()`. *Chapters 3 and 13.*
  <https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation>
- **Transports.** stdio and Streamable HTTP. *Chapter 3.*
  <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports>
- **“The 2026-07-28 Specification”** (MCP blog). The release post, in plain language: MCP becomes “a request/response stateless protocol.” *Chapter 3.*
  <https://blog.modelcontextprotocol.io/posts/2026-07-28/>
- **Official SDKs.** The list of SDKs by language and support tier; on 15 October 2026 TypeScript, Python, C#, Go, Rust and Ruby were Tier 1.
  <https://modelcontextprotocol.io/docs/sdk>
- **TypeScript SDK, repository and v2 documentation.** The SDK Trailhead’s backend server is built on. *Chapter 3.*
  <https://github.com/modelcontextprotocol/typescript-sdk>
  <https://ts.sdk.modelcontextprotocol.io/v2/>
- **MCP Inspector.** The official tool for exercising servers by hand or from the command line. *Chapter 3.*
  <https://github.com/modelcontextprotocol/inspector>
- **MCP Apps.** The extension for servers that return interactive UI. *Chapter 3.*
  <https://modelcontextprotocol.io/extensions/apps/overview>
- **Specification repository.** The source of the MCP specification and its proposals (SEPs). The old `specification` address now redirects to `modelcontextprotocol/modelcontextprotocol`.
  <https://github.com/modelcontextprotocol/modelcontextprotocol>

## C.6 Packages the chapters use

Versions are what the npm registry reported as `latest` on 15 October 2026, which is also what the demos pin, except Angular: the demos pin 22.2.2, and 22.2.3 was published late on 14 October.[^2] Pin them; several of these change weekly.

| Package | Version | What it is | Chapters |
|---|---|---|---|
| `@modelcontextprotocol/server` | 2.3.1 | MCP TypeScript SDK v2, server package | 3 |
| `@modelcontextprotocol/client` | 2.3.1 | MCP TypeScript SDK v2, client package | 3 |
| `@modelcontextprotocol/node` | 2.1.1 | Node.js HTTP middleware for the SDK | 3 |
| `@modelcontextprotocol/inspector` | 2.11.0 | The MCP Inspector | 3 |
| `zod` | 4.6.7 | Schema library the SDK uses for tool inputs | 3 |
| `webmcp-types` | 0.1.10 | TypeScript definitions for WebMCP | 5, 9, 10 |
| `@mcp-b/global` | 6.0.3 | WebMCP polyfill from MCP-B | 9, 15 |
| `@mcp-b/webmcp-polyfill` | 6.0.3 | Upstream polyfill “plus temporary declarative tools” | 9, 10, 15 |
| `@mcp-b/webmcp-local-relay` | 6.0.3 | Relay from a tab’s tools to desktop MCP clients | 9 |
| `usewebmcp` | 6.0.3 | React hooks for `document.modelContext` | 10, 15 |
| `@mcp-b/react-webmcp` | 6.0.3 | MCP-B’s broader React hooks package | 10 |
| `@angular/core`, `@angular/forms` | 22.2.2 (latest: 22.2.3) | Angular, whose WebMCP guide Chapter 10 follows | 10 |
| `playwright` | 1.64.1 | Browser automation used by every demo’s tests | 6–17 |

*Table C.1 — npm packages used in the chapters and demos, with versions read from the npm registry on 15 October 2026.*

The packages’ pages:

- <https://www.npmjs.com/package/@modelcontextprotocol/server>
- <https://www.npmjs.com/package/@modelcontextprotocol/client>
- <https://www.npmjs.com/package/@modelcontextprotocol/node>
- <https://www.npmjs.com/package/@modelcontextprotocol/inspector>
- <https://www.npmjs.com/package/webmcp-types>
- <https://www.npmjs.com/package/@mcp-b/global>
- <https://www.npmjs.com/package/@mcp-b/webmcp-polyfill>
- <https://www.npmjs.com/package/@mcp-b/webmcp-local-relay>
- <https://www.npmjs.com/package/@mcp-b/react-webmcp>
- `usewebmcp` (registry record; the npmjs.com page served a bot check): <https://registry.npmjs.org/usewebmcp>

## C.7 Community projects and framework guides

- **MCP-B documentation.** Guides and references for the polyfill, the React hooks and the desktop relay. *Chapters 9, 10 and 15.*
  <https://docs.mcp-b.ai/>
- **WebMCP-org/npm-packages.** The source of the `@mcp-b/*` packages and `usewebmcp`. *Chapter 15.*
  <https://github.com/WebMCP-org/npm-packages>
- **Angular: WebMCP.** Angular’s own guide to exposing tools from an Angular app. *Chapter 10.*
  <https://angular.dev/ai/webmcp>

## C.8 Web platform background

- **MDN: Permissions-Policy.** The header and the `allow` attribute that the `tools` feature plugs into. *Chapter 7.*
  <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy>
- **Permissions Policy specification.** The normative rules for policy-controlled features and allowlists.
  <https://w3c.github.io/webappsec-permissions-policy/>
- **MDN: AbortSignal.** The signal you pass to `registerTool()` and receive in `execute`. *Chapters 5 and 6.*
  <https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal>
- **DOM Standard: AbortSignal.** The normative definition.
  <https://dom.spec.whatwg.org/#interface-AbortSignal>
- **MDN: Secure contexts.** Why `document.modelContext` is missing on plain HTTP. *Chapter 5.*
  <https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts>
- **Secure Contexts specification.** Including the definition of a potentially trustworthy origin. *Chapters 5 and 7.*
  <https://w3c.github.io/webappsec-secure-contexts/>
- **HTML Standard: tracking user activation.** What a user gesture is, and why a tool call isn’t one. *Chapter 13.*
  <https://html.spec.whatwg.org/multipage/interaction.html#tracking-user-activation>
- **WAI-ARIA.** The accessibility semantics WebKit argues agents should build on instead. *Chapters 13, 15 and 17.*
  <https://www.w3.org/TR/wai-aria/>
- **JSON Schema specification.** The 2020-12 vocabulary for `inputSchema`. *Chapters 2, 5 and 11.*
  <https://json-schema.org/specification>
- **JSON-RPC 2.0.** MCP’s message format. *Chapter 3.*
  <https://www.jsonrpc.org/specification>

## C.9 The book’s own repositories

- **The book.** The Markdown for every chapter and appendix, the outline, and the generator for the website.
  <https://github.com/vibeprogrammer/webmcp-book>
- **The demos.** Every listing as a runnable file, with tests.
  <https://github.com/vibeprogrammer/webmcp-book-demos>
- **The website.** The e-book edition, built from the same Markdown.
  <https://vibeprogrammer.github.io/webmcp-book/>

Every folder in the demos repository has a README that maps its files to listings, explains how to run the tests and records what passed. The listings are byte-identical to the book, and most folders include a test that checks this against the chapter’s Markdown. Behavioural tests run against a small `document.modelContext` mock and, wherever the API allows, against Chromium 156 with `--enable-features=WebMCPTesting`. Table C.2 maps the folders to the chapters.

| Folder | Chapter | What it demonstrates |
|---|---|---|
| `fjord-table/` | 4, 5 | Fjord Table’s booking page in plain HTML and JavaScript modules, with `search_availability` and `book_table` registered through `document.modelContext`, unregistered with an `AbortSignal`, and typed with `webmcp-types`. |
| `chapters/03-mcp-in-practice/` | 3 | Trailhead’s backend MCP server on the TypeScript SDK v2: `search_products`, `get_order_status`, a returns-policy resource and a `packing_list` prompt, served over stdio and Streamable HTTP in both protocol eras, tested with an SDK client and the Inspector CLI. |
| `chapters/05-registering-tools/` | 5 | A Chromium 156 probe that backs Chapter 5’s statements about what Chromium does where it differs from the draft: `outputSchema` dropped, no input validation, return values, `UnknownError`. Chapter 5’s listings themselves live in `fjord-table/`. |
| `chapters/06-annotations-lifecycle-errors/` | 6 | Trailhead’s product, cart and checkout tools with annotations, the call lifecycle, cancellation through the execution signal, tool-level errors versus platform errors, `toolactivated`/`toolcancel` logging, `toolchange` and debugging tools. |
| `chapters/07-frames-origins-agents/` | 7 | The Helpdesk Widget across two origins: Ledgerly delegating the `tools` policy to Supportly’s iframe, `exposedTo` and `fromOrigins`, an in-page agent built on `getTools()` and `executeTool()`, and an extension that uses the API from a content script. |
| `chapters/08-declarative-api/` | 8 | Fjord Table’s search and booking forms as declarative tools: `toolname`, `tooldescription`, `toolparamdescription`, `toolautosubmit`, `agentInvoked`, `respondWith()`, the CSS pseudo-classes and validation feedback, tested in Chrome’s trial implementation. |
| `chapters/09-first-webmcp-app/` | 9 | Fjord Table end to end: progressive enhancement with native WebMCP or an opt-in pinned polyfill, the scriptable Test Agent with a Prompt API planner, an origin-trial meta tag and a desktop-relay configuration. |
| `chapters/10-webmcp-in-frameworks/` | 10 | Trailhead in React 19 with Vite and `usewebmcp` (route-scoped `checkout`, StrictMode-safe registration, a shared external store), and an Angular version with tools in the injector and Signal Forms. |
| `chapters/11-designing-tools/` | 11 | Trailhead’s catalogue and cart tools and the Helpdesk Widget redesigned: descriptions within character budgets, `oneOf` enums with titles, a validator that uses the published schema, a description linter, and results and errors a model can act on. |
| `chapters/12-threat-models/` | 12 | Attacks and mitigations: a same-origin `registerTool()` wrapper attack (demonstration only), a pre-release audit of the registered tools, cross-origin exposure between Ledgerly and Supportly, and Trailhead tools hardened against injection and over-parameterisation. |
| `chapters/13-privacy-consent-human-in-the-loop/` | 13 | Trailhead’s checkout, which never completes without a person: the confirmation sheet with trusted clicks and an arming delay, cancellation, and the proposed `requestUserInput()` IDL. |
| `chapters/14-testing-debugging-evals/` | 14 | Testing in layers: unit tests for `execute`, a browser-contract suite, a driver for the DevTools Protocol’s WebMCP domain, an eval runner with a task suite for Fjord Table, and an instrumentation wrapper for real-user measurement. |
| `chapters/15-browser-support-and-standards/` | 15 | Origin-trial tokens for Chrome and Edge (meta tags and headers), feature detection across WebMCP builds, and `standards-watch.mjs`, which snapshots seven primary sources and reports what changed. |
| `chapters/16-product-and-business-implications/` | 16 | Trailhead’s tool catalog owned like product copy, a CI check for Chrome’s character budgets, a measurement wrapper and order attribution, in TypeScript. |
| `chapters/17-the-road-ahead/` | 17 | Future-proofing: tools as plain data, one adapter that knows the API shape (feature detection, input validation, one signal for the whole catalog), and a probe that reports what a browser supports, from `navigator.modelContext` to whether `outputSchema` survives `getTools()`. |
| `appendices/a-api-reference/` | Appendix A | The WebMCP IDL and the probes behind Appendix A’s error table, run in Chromium 156. |
| `appendices/d-migration/` | Appendix D | Before-and-after migration listings, with the “after” code tested in Chromium 156. |

*Table C.2 — Folders in vibeprogrammer/webmcp-book-demos and what each demonstrates. Chapters 1 and 2 have no code. Chapter 4’s first listing is the seed of `fjord-table/`, which Chapter 5 builds out.*

## C.10 How to track changes

Most of what dates this book will show up in five places first. A twenty-minute check once a month covers them.

1. **The spec’s date line and commit history.** If the date under the title has changed, read the commits since your last visit. Each one is small and dated.
2. **New and closed issues.** Watch the repository on GitHub (Watch → Custom → Issues and Pull requests) and skim the titles. Chapter 17 lists the open questions most likely to change your code.
3. **chromestatus.** The JSON form of the feature entry changes when a trial is extended, a stage moves or a review lands.
4. **Positions and reviews.** The labels on the Mozilla, WebKit and TAG issues are the signal; the comments explain it.
5. **The charter.** The Agentic Web WG draft, its strategy issue and the public-new-work list will show whether WebMCP gets a Working Group home.

Chapter 15’s `standards-watch.mjs`, in the demos repository, automates most of this list. It fetches the spec, the commit history, chromestatus, the Edge trial page and the three position and review threads, saves a snapshot, and exits with a non-zero code when anything changed, so you can run it on a schedule in CI.

> **Still in flux: this appendix**
>
> URLs are the most fragile thing in a book. Two moved while this one was being written: `modelcontextprotocol.io/specification/latest` now redirects to the dated 2026-07-28 page, and the MCP specification repository now lives at `modelcontextprotocol/modelcontextprotocol`. If an address here fails, search the publisher’s site for the title; the repositories in C.1 and C.9 are the least likely to move.

## C.11 Summary

- The spec, its issues and its commit history are the primary sources. Chrome’s documentation shows what one implementation does, and the demos repository shows what Chromium 156 actually did.
- Chrome and Edge both run origin trials; chromestatus and the Edge trial page carry their dates.
- The standards picture lives in four GitHub threads (Mozilla, WebKit, the TAG and the W3C charter work) plus the W3C’s own announcements.
- Pin package versions. The ones in Table C.1 were current on 15 October 2026.
- Run a monthly check, or Chapter 15’s watcher, to know when the book has drifted.

## Notes

[^1]: W3C, “Community and Business Groups: Frequently Asked Questions”, answer to “Does the Community Group Process replace the Recommendation Track?” Read 15 October 2026. <https://www.w3.org/community/about/faq/>
[^2]: Every URL in this appendix was fetched on 14 October 2026 with `curl`, or for npmjs.com pages with a headless Chromium, and returned HTTP 200. All of them were fetched again on 15 October 2026: every non-npm URL returned HTTP 200, and every npmjs.com page answered a script with a bot check, so the packages and versions were confirmed in the registry records instead. Package versions are the `latest` versions in the npm registry’s package records, for example <https://registry.npmjs.org/usewebmcp/latest>.
