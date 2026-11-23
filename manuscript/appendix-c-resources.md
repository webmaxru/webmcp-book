# Appendix C: Resources and Further Reading

> *“Community Groups are for incubation. The Recommendation Track is for standardization.”*
>
> — W3C, Community and Business Groups FAQ[^appc-1]

WebMCP keeps moving after a book is printed, so this appendix is less a reading list than a map of where to look. It lists the primary sources the chapters rely on, grouped by who publishes them, with one line on what each one is good for. Then it maps the folders of the book’s demos repository to the chapters, and it ends with a short routine for tracking changes.

The resources in the second edition were fetched again on 2 November 2026, with two kinds of exception you should know about. The polyfill entry in Section C.7 was checked on 18 November 2026. The npmjs.com package pages serve a bot check to scripts, so for packages I give the npm registry’s own record, which is what `npm install` reads. And the book’s own repositories in Section C.9 open only for readers who have access to them.[^appc-2] Dates in the annotations are the dates printed on the pages themselves.

## C.1 The specification and its repository

- **WebMCP specification (Draft Community Group Report).** The normative text: the IDL, the algorithms, the security and privacy sections. Check the date under the title first. It read 27 October 2026 when I last checked, on 2 November 2026, and since that draft the spec has four editors. *Chapters 4–7 and Appendix A.*
  <https://webmachinelearning.github.io/webmcp/>
- **The webmcp repository and explainer.** The README is the explainer: goals, use cases, open questions and the “Future Exploration” notes. *Chapters 4 and 17.*
  <https://github.com/webmachinelearning/webmcp>
- **Issues.** Where design questions are argued and resolved. Chapter 17 explains how to read an issue thread and which ones to watch.
  <https://github.com/webmachinelearning/webmcp/issues>
- **Pull requests.** Proposed spec changes. A merged pull request is the moment something becomes spec text, or leaves it. Appendix A, Section A.9, lists the open ones that would change the API.
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

Chrome’s WebMCP documentation is a small set of pages, and they change more often than the spec does. Here they are one by one, with the dates printed on each page on 2 November 2026. Two of them carry my name in the byline.

- **WebMCP** (published 18 May 2026, updated 7 October 2026). Chrome’s overview: the definition of *actuation*, how to turn on `chrome://flags/#enable-webmcp-testing`, the origin trial, the Permissions Policy and the extensions Chrome recommends for testing. *Chapters 1, 4 and 9.*
  <https://developer.chrome.com/docs/ai/webmcp>
- **Imperative API** (updated 16 October 2026). Chrome’s guide to `registerTool()` and friends, with the version notes (Chrome 153, 155 and 156) and the framework section, which now points React developers to `use-webmcp-tool` and Vue developers to `@vueuse/core`. *Chapters 5, 6 and 10.*
  <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
- **Declarative API** (updated 25 September 2026). The form attributes, events and CSS pseudo-classes that still ship in Chrome. *Chapter 8.*
  <https://developer.chrome.com/docs/ai/webmcp/declarative-api>
- **When to use WebMCP and MCP** (published 11 March 2026, updated 27 October 2026). Chrome’s side-by-side of the two, rewritten in October with a new comparison table (“Tools only” for WebMCP against MCP’s tools, resources and prompts). *Chapters 4 and 16.*
  <https://developer.chrome.com/docs/ai/webmcp/compare-mcp>
- **How WebMCP fits in user journeys** (published 18 May 2026). Chrome’s use cases. *Chapters 16 and 17.*
  <https://developer.chrome.com/docs/ai/webmcp/use-cases>
- **Build your user’s agentic workflows with WebMCP tools** (published 26 August 2026, updated 30 October 2026, by André Cipriani Bandarra and me). Designing tools around the tasks people actually do, enforcing trust boundaries in application logic, binding approval to the exact plan, and testing with pinned versions. *Chapters 11–14.*
  <https://developer.chrome.com/docs/ai/webmcp/build-tools>
- **WebMCP best practices** (published 18 May 2026, updated 30 October 2026, by Alexandra Klepper, me and François Beaufort). Naming, descriptions and granularity, plus the architectural constraints added in October: register tools all at once, share one application service, wait for the UI, explicit commit points and stale workflow state. *Chapters 6, 11 and 13.*
  <https://developer.chrome.com/docs/ai/webmcp/best-practices>
- **WebMCP tool security** (updated 1 September 2026). Guidance for site authors, including the character budgets, plus the `requestUserInteraction()` text the draft no longer has. *Chapters 11–13.*
  <https://developer.chrome.com/docs/ai/webmcp/secure-tools>
- **Test WebMCP with Evals** (updated 28 May 2026). Chrome’s eval workflow. *Chapter 14.*
  <https://developer.chrome.com/docs/ai/webmcp/evals>
- **Agent security considerations for WebMCP** (published 9 June 2026). The same topic from the agent builder’s side, and one of the two Chrome pages the spec’s security section now links to. *Chapter 12.*
  <https://developer.chrome.com/docs/agents/security>
- **WebMCP and AI agents.** Chrome’s landing page for agents in the browser. *Chapter 1.*
  <https://developer.chrome.com/docs/ai/agents>
- **Debug WebMCP tools.** The DevTools WebMCP pane in the Application panel: available tools, invoked tools, manual runs and filters. *Chapters 9 and 14.*
  <https://developer.chrome.com/docs/devtools/application/webmcp>
- **Chrome DevTools Protocol: WebMCP domain.** The commands and events automation uses to list and invoke tools (`WebMCP.enable`, `WebMCP.invokeTool`, `WebMCP.toolsAdded`). *Chapter 14.*
  <https://chromedevtools.github.io/devtools-protocol/tot/WebMCP/>
- **WebMCP early preview** (blog, 10 February 2026). Where Chrome first showed the API to developers. *Chapter 15.*
  <https://developer.chrome.com/blog/webmcp-epp>
- **Join the WebMCP origin trial** (blog, 9 June 2026). The announcement: “In Chrome 149, you can sign up for the WebMCP origin trial.” *Chapters 9 and 15.*
  <https://developer.chrome.com/blog/ai-webmcp-origin-trial>
- **Get started with origin trials.** How tokens work and the three ways to deliver one. *Chapters 9 and 15.*
  <https://developer.chrome.com/docs/web-platform/origin-trials>
- **Third-party origin trials.** How an embedded script, such as a widget vendor’s, can register for a trial across the sites that embed it. *Chapter 15.*
  <https://developer.chrome.com/docs/web-platform/third-party-origin-trials>
- **Chrome Platform Status: WebMCP.** Chrome’s feature entry: status, trial milestones (Chrome 149 to 156, extended to 162) and the reasons for the extension. The page renders in script, and the JSON form below is easier to read and to watch. *Chapters 4 and 15.*
  <https://chromestatus.com/feature/5117755740913664>
  <https://chromestatus.com/api/v0/features/5117755740913664>
- **Chromium Dash.** Which Chrome version is stable, beta, dev and canary today, and when the next one ships. On 2 November 2026 Chrome 156 was stable, with 157 due on 3 November. *Chapter 15.*
  <https://chromiumdash.appspot.com/schedule>
- **The Prompt API** (updated 26 August 2026). Chrome’s on-device model, which the Test Agent and the example extension can use as a planner. *Chapter 9.*
  <https://developer.chrome.com/docs/ai/prompt-api>
- **GoogleChromeLabs/webmcp-tools.** Chrome’s demos (among them the pizza maker, the French bistro and a React flight search), the eval tool and skills, in one repository. *Chapters 8, 9 and 14.*
  <https://github.com/GoogleChromeLabs/webmcp-tools>
- **Model Context Tool Inspector.** An extension to inspect, monitor and execute a page’s tools by hand or through Gemini. The first link is its source, the second its Chrome Web Store listing. *Chapters 9 and 14.*
  <https://github.com/beaufortfrancois/model-context-tool-inspector>
  <https://chromewebstore.google.com/detail/webmcp-model-context-tool/gbpdfapgefenggkahomfgkhfehlcenpd>
- **Example Agentic Chrome Extension.** A small, complete agent in the side panel, for testing your tools with a real model. *Chapter 9.*
  <https://github.com/GoogleChromeLabs/webmcp-extension>
- **Chrome DevTools for agents (`chrome-devtools-mcp`).** An MCP server that lets a coding assistant drive Chrome, with experimental WebMCP tools behind `--categoryExperimentalWebmcp`. *Chapter 14.*
  <https://github.com/ChromeDevTools/chrome-devtools-mcp>

## C.3 Microsoft Edge

- **Edge origin trial: WebMCP.** Registration for Edge’s trial, with a trial expiration date of 30 March 2027. *Chapters 9 and 15.*
  <https://developer.microsoft.com/en-us/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a>
- **What’s new in DevTools (Microsoft Edge 149).** Lists “WebMCP debugging” among the updates Edge takes from Chromium. *Chapter 14.*
  <https://learn.microsoft.com/en-us/microsoft-edge/devtools/whats-new/149>

## C.4 Standards positions, reviews and process

- **Mozilla standards position on WebMCP** (issue #1412). Labelled “position: neutral”, and still so on 2 November 2026. The thread explains what would move it, and the spec’s editors have said a refreshed Mozilla position is on its way. *Chapter 15.*
  <https://github.com/mozilla/standards-positions/issues/1412>
- **WebKit standards position on WebMCP** (issue #670). Labelled “position: oppose”, with WebKit’s reasons and its proposed alternative process. *Chapter 15.*
  <https://github.com/WebKit/standards-positions/issues/670>
- **W3C TAG design review** (issue #1238, “Incubation: WebMCP”). Still open on 2 November 2026 and labelled “Missing: Multi-stakeholder support”. On 26 October 2026 the TAG posted an early comment, explicitly not a resolution, with its current thinking: a planned finding on agentic browsing, concerns about functionality that only agents can reach, and even the question whether there is still time to rename the proposal to something like “Tools”. *Chapters 4 and 15.*
  <https://github.com/w3ctag/design-reviews/issues/1238>
  <https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845>
- **TAG design reviews repository.** How the TAG takes and prioritises reviews, useful context for reading #1238.
  <https://github.com/w3ctag/design-reviews>
- **The Web Machine Learning Working Group charter pull request** (w3c/charter-drafts #829). The attempt to add WebMCP to that group’s charter, closed on 13 October 2026. *Chapter 15.*
  <https://github.com/w3c/charter-drafts/pull/829>
- **Web Machine Learning Working Group.** The existing W3C Working Group that pull request targeted.
  <https://www.w3.org/groups/wg/webmachinelearning/>
- **Draft Agentic Web Working Group charter.** The proposed new group whose one named normative deliverable is WebMCP. On 2 November 2026 its start and end dates and its chairs were still unfilled template fields, and its list of possible future deliverables named agent identity. *Chapters 15 and 17.*
  <https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html>
- **W3C strategy issue #576, “[wg/agenticweb] Agentic Web Group Charter”.** The W3C’s tracking issue for that charter, with its list of known concerns. It was discussed at TPAC 2026 in Dublin (26–30 October), and on 2 November 2026 it was still labelled “In Charter Refinement”. *Chapter 15.*
  <https://github.com/w3c/strategy/issues/576>
- **Start of charter refinement for the Agentic Web WG** (public-new-work, 1 October 2026). The W3C’s announcement, which expected refinement to last until about 10 November 2026. *Chapter 15.*
  <https://lists.w3.org/Archives/Public/public-new-work/2026Oct/0002.html>
- **W3C Process Document** (18 August 2025). The rules for Working Groups, charters, the TAG and formal objections. *Chapter 15 and Appendix B.*
  <https://www.w3.org/policies/process/>
- **W3C Community and Business Groups FAQ.** What a Community Group can and can’t do. *Chapter 4 and Appendix B.*
  <https://www.w3.org/community/about/faq/>

## C.5 The Model Context Protocol

- **MCP specification, version 2026-07-28.** The revision this book follows: stateless, self-contained requests. The `latest` address still redirected here on 2 November 2026. *Chapter 3.*
  <https://modelcontextprotocol.io/specification/2026-07-28>
- **Changelog for 2026-07-28.** What changed from the legacy revisions, starting with the removal of the `initialize` handshake. *Chapter 3.*
  <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
- **Tools.** MCP’s tool definition, results, `outputSchema` and annotations, the comparison point for WebMCP’s own. *Chapters 3, 11 and 17.*
  <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>
- **Elicitation.** How an MCP server asks the user a question mid-call, and the model for WebMCP’s proposed `requestUserInput()` (pull request #204). *Chapters 3 and 13.*
  <https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation>
- **Transports.** stdio and Streamable HTTP. *Chapter 3.*
  <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports>
- **“The 2026-07-28 Specification”** (MCP blog). The release post, in plain language: MCP becomes “a request/response stateless protocol.” *Chapter 3.*
  <https://blog.modelcontextprotocol.io/posts/2026-07-28/>
- **Official SDKs.** The list of SDKs by language and support tier. On 2 November 2026 TypeScript, Python, C#, Go, Rust and Ruby were Tier 1.
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

The middle column is what the demos pin, which is what the npm registry reported as `latest` on 15 October 2026 (except Angular, where the demos pin 22.2.2). The right column is what the registry reported on 2 November 2026.[^appc-2] Several of these change weekly, so pin them. The demos stay on the October versions unless a chapter says otherwise.

**Table C.1 — npm packages used in the chapters and demos**

| Package | Demos pin | Latest, 2 November 2026 | What it is | Chapters |
|---|---|---|---|---|
| `@modelcontextprotocol/server` | 2.3.1 | 2.4.0 | MCP TypeScript SDK v2, server package | 3 |
| `@modelcontextprotocol/client` | 2.3.1 | 2.4.0 | MCP TypeScript SDK v2, client package | 3 |
| `@modelcontextprotocol/node` | 2.1.1 | 2.1.2 | Node.js HTTP middleware for the SDK | 3 |
| `@modelcontextprotocol/inspector` | 2.11.0 | 2.13.0 | The MCP Inspector | 3 |
| `zod` | 4.6.7 | 4.6.7 | Schema library the SDK uses for tool inputs | 3 |
| `webmcp-types` | 0.1.10 | 0.1.10 | TypeScript definitions for WebMCP | 5, 9, 10 |
| `@mcp-b/global` | 6.0.3 | 6.0.3 | WebMCP polyfill from MCP-B | 9, 15 |
| `@mcp-b/webmcp-polyfill` | 6.0.3 | 6.0.3 | Upstream polyfill “plus temporary declarative tools” | 9, 10, 15 |
| `@mcp-b/webmcp-local-relay` | 6.0.3 | 6.0.3 | Relay from a tab’s tools to desktop MCP clients | 9 |
| `usewebmcp` | 6.0.3 | 6.0.3 | React hooks for `document.modelContext` | 10, 15 |
| `@mcp-b/react-webmcp` | 6.0.3 | 6.0.3 | MCP-B’s broader React hooks package | 10 |
| `use-webmcp-tool` | not used | 0.3.0 | The React hook package Chrome’s Imperative API page now points to | 10 |
| `@vueuse/core` | not used | 15.0.0 | Vue utilities, including the `useWebMCP` composable Chrome’s page points to | 10 |
| `@angular/core`, `@angular/forms` | 22.2.2 | 22.2.4 | Angular, whose WebMCP guide Chapter 10 follows | 10 |
| `playwright` | 1.64.1 | 1.64.1 | Browser automation used by every demo’s tests | 6–17 |

The packages’ registry records (the npmjs.com pages show the same data to a browser):

- <https://registry.npmjs.org/@modelcontextprotocol/server>
- <https://registry.npmjs.org/@modelcontextprotocol/client>
- <https://registry.npmjs.org/@modelcontextprotocol/node>
- <https://registry.npmjs.org/@modelcontextprotocol/inspector>
- <https://registry.npmjs.org/webmcp-types>
- <https://registry.npmjs.org/@mcp-b/global>
- <https://registry.npmjs.org/@mcp-b/webmcp-polyfill>
- <https://registry.npmjs.org/@mcp-b/webmcp-local-relay>
- <https://registry.npmjs.org/@mcp-b/react-webmcp>
- <https://registry.npmjs.org/usewebmcp>
- <https://registry.npmjs.org/use-webmcp-tool>
- <https://registry.npmjs.org/@vueuse/core>

## C.7 Community projects and framework guides

- **W3C WebMCP polyfill** (`@w3c/webmcp-polyfill`). This open-source JavaScript package gives a page `document.modelContext` so you can register tools, discover them and call them before a browser exposes the native API. It is useful both for web developers exposing app features and for people building in-page agents or extensions that can reach the page's tools. You can also use it to try the draft before giving feedback.
  <https://www.npmjs.com/package/@w3c/webmcp-polyfill>
  <https://github.com/w3c-oss/webmcp-polyfill>

  Install the package and load its automatic entry point before registering tools:

  ```bash
  npm install @w3c/webmcp-polyfill
  ```

  ```js
  import "@w3c/webmcp-polyfill/auto";
  ```

  The package follows the WebMCP draft, ships TypeScript definitions based on `webmcp-types` and has no runtime JavaScript dependencies. Version 0.1.1 targets `webmcp-types` 0.1.10. It installs only in a secure context (HTTPS or localhost) and does not replace a native `document.modelContext`.

  There are boundaries to keep in mind. The polyfill does not provide a browser agent, and its documentation says that talking to an actual browser agent needs browser support. Declarative forms are not implemented, and the project's testing notes list differences from the draft. WebMCP is still a Community Group draft, not a W3C Standard, so expect both the API and the package to change. Check the testing notes before depending on a particular behaviour. *Chapters 9, 14 and 15.*
  <https://github.com/w3c-oss/webmcp-polyfill/blob/main/TESTING.md>

- **MCP-B documentation.** Guides and references for the polyfill, the React hooks and the desktop relay. *Chapters 9, 10 and 15.*
  <https://docs.mcp-b.ai/>
- **WebMCP-org/npm-packages.** The source of the `@mcp-b/*` packages and `usewebmcp`. *Chapter 15.*
  <https://github.com/WebMCP-org/npm-packages>
- **Angular: WebMCP.** Angular’s own guide to exposing tools from an Angular app. *Chapter 10.*
  <https://angular.dev/ai/webmcp>
- **VueUse: useWebMCP.** The Vue composable Chrome’s Imperative API page has pointed to since 16 October 2026. *Chapter 10.*
  <https://vueuse.org/core/usewebmcp/>

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

- **The book.** The manuscript (one Markdown file per chapter and appendix), the theme and the build scripts for the PDF, EPUB and web editions, and the release history.
  <https://github.com/webmaxru/webmcp-book>
- **The demos.** Every listing as a runnable file, with tests.
  <https://github.com/webmaxru/webmcp-book-demos>
- **The website.** The web edition, built from the same manuscript, at its new home.
  <https://webmcp.salnikov.no>

Every folder in the demos repository has a README that maps its files to listings, explains how to run the tests and records what passed. The listings are byte-identical to the book, and most folders include a test that checks this against the chapter’s Markdown. Behavioural tests run against a small `document.modelContext` mock and, wherever the API allows, against Chromium 156 with `--enable-features=WebMCPTesting`. Table C.2 maps the folders to the chapters. Chapters 1 and 2 have no code, and Chapter 4’s first listing is the seed of `fjord-table/`, which Chapter 5 builds out.

**Table C.2 — Folders in the demos repository and what each one demonstrates**

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
| `appendices/a-api-reference/` | Appendix A | The WebMCP IDL and the 25 probes behind Appendix A’s tables, run in Chromium 156. |
| `appendices/d-migration/` | Appendix D | Before-and-after migration listings, with the “after” code (including the all-or-nothing tool set) tested in Chromium 156. |
| `appendices/e-tool-interface/` | Appendix E | `read-tool.js`, the `source`/`window` reader for Chrome 160 and earlier Chrome. A `null` `source` is skipped. Not part of the Chromium 156 probe set. |
| — | Appendix F | No demo. The listing is an excerpt of open pull request #375, not code to ship. |


## C.10 How to track changes

Most of what dates this book shows up in five places first. A twenty-minute check once a month covers them, and that is exactly how the second edition’s changes were found.

1. **The spec’s date line and commit history.** If the date under the title has changed, read the commits since your last visit. Each one is small and dated.
2. **New and closed issues.** Watch the repository on GitHub (Watch → Custom → Issues and Pull requests) and skim the titles. Chapter 17 lists the open questions most likely to change your code.
3. **chromestatus and Chrome’s docs.** The JSON form of the feature entry changes when a trial is extended, a stage moves or a review lands. The “Last updated” dates on the pages in Section C.2 tell you which Chrome guide to re-read (three of them changed in the two weeks after the first edition).
4. **Positions and reviews.** The labels on the Mozilla, WebKit and TAG issues are the signal, and the comments explain it.
5. **The charter.** The Agentic Web WG draft, its strategy issue and the public-new-work list will show whether WebMCP gets a Working Group home.

Chapter 15’s `standards-watch.mjs`, in the demos repository, automates most of this list. It fetches the spec, the commit history, chromestatus, the Edge trial page and the three position and review threads, saves a snapshot, and exits with a non-zero code when anything changed, so you can run it on a schedule in CI.

> **Still in flux: this appendix**
>
> URLs are the most fragile thing in a book. Several moved while this one was being written: `modelcontextprotocol.io/specification/latest` redirects to the dated 2026-07-28 page, the MCP specification repository lives at `modelcontextprotocol/modelcontextprotocol`, the spec’s old `#violation-same-origin-boundaries` anchor gave way to `#interaction-with-same-origin-policy` on 27 October 2026, and the book’s own web edition moved to webmcp.salnikov.no. If an address here fails, search the publisher’s site for the title. The repositories in C.1 are the least likely to move.

## C.11 Summary

- The spec, its issues and its commit history are the primary sources. Chrome’s documentation shows what one implementation does, and the demos repository shows what Chromium 156 actually did.
- Chrome’s WebMCP pages each carry a “Last updated” date. Re-read the ones that changed.
- Chrome and Edge both run origin trials, and chromestatus and the Edge trial page carry their dates.
- The standards picture lives in four GitHub threads (Mozilla, WebKit, the TAG and the W3C charter work) plus the W3C’s own announcements.
- Pin package versions. Table C.1 shows both what the demos pin and what was current on 2 November 2026.
- Run a monthly check, or Chapter 15’s watcher, to know when the book has drifted.

## Notes

[^appc-1]: W3C, “Community and Business Groups: Frequently Asked Questions”, answer to “Does the Community Group Process replace the Recommendation Track?” (retrieved November 2026). <https://www.w3.org/community/about/faq/>
[^appc-2]: Every URL in this appendix was fetched on 14 and 15 October 2026 for the first edition, and again on 2 November 2026 for this one, with a script. On 2 November every URL returned HTTP 200 with three exceptions. The npmjs.com package pages answered the script with a bot check (HTTP 403), so packages and versions were confirmed in the npm registry records instead, for example <https://registry.npmjs.org/usewebmcp/latest>. The book’s manuscript repository in Section C.9 is private and answers HTTP 404 to anyone without access. The demos repository is public. And webmcp.salnikov.no, the web edition’s new address, was not yet serving when this appendix was checked. One commit-pinned GitHub page (Appendix D’s `docs/proposal.md`) answered with GitHub’s rate limit and was confirmed through the GitHub API.
