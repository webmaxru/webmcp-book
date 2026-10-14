# WebMCP: Book Outline

*A book about the web standard that lets websites hand AI agents real tools*

*Prepared for Maxim · 14 October 2026 · Status checked against official sources on that date*

## Where WebMCP stands today

WebMCP is a draft proposal being incubated, not a shipped standard. Two Chromium browsers are running origin trials, and the other engines are split. The book’s structure assumes this will keep moving through 2027.

| Area             | State as of 14 Oct 2026                                                                                                                                                                                                                                                                                |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Specification    | Draft Community Group Report of the W3C Web Machine Learning Community Group, latest version dated 13 Oct 2026. Not a W3C Standard and not on the standards track. Editors from Microsoft and Google.                                                                                                  |
| API shape        | Imperative only in the spec: document.modelContext.registerTool(), getTools(), executeTool(), and tool events. The declarative (HTML form) API was taken out of the spec on 8 Oct 2026 and now lives in a separate explainer.                                                                          |
| Chrome           | Developer trial behind a flag from Chrome 146 (early preview, Feb 2026). Origin trial from Chrome 149 (announced at Google I/O 2026), originally through Chrome 156 and now extended to Chrome 162. Chrome Status lists the feature as “Proposed”, with the TAG, security and privacy reviews pending. |
| Microsoft Edge   | Origin trial live in Edge 150, with trial expiry on 30 Mar 2027. Edge 149 DevTools ships WebMCP debugging.                                                                                                                                                                                             |
| Firefox          | Mozilla’s standards position is “neutral” (Aug 2026). Talks continue about API changes that could move it.                                                                                                                                                                                             |
| Safari / WebKit  | WebKit’s standards position is “oppose” (Jun 2026), citing duplication of HTML and ARIA, security, privacy, consent and venue.                                                                                                                                                                         |
| W3C TAG          | Early design review open since Jun 2026, labelled “Missing: multi-stakeholder support”. The editors asked the TAG on 9 Oct 2026 to wait for Mozilla’s refreshed position and for TPAC.                                                                                                                 |
| Agents and tools | The explainer’s status page lists ChatGPT Desktop (supported), Brave Leo (experimental) and Meta Ray-Ban Display (coming). Also: Chrome’s inspector and example agent extensions, the MCP-B polyfill and bridges, and React (usewebmcp) and Angular integrations.                                      |

## Working titles and premise

1. Tools, Not Clicks: Building Agent-Ready Websites with WebMCP
2. The Agent-Ready Web: A Practical Guide to WebMCP for Developers and Product Leaders
3. WebMCP in Action: Exposing Your Web App to AI Agents, Safely

### Premise

AI agents already browse on our behalf, but most of them still work like a tourist with a phrasebook: they take screenshots, guess which button does what, and break the moment a layout changes. WebMCP is the web platform’s proposed answer. A page declares what it can do as named, described, schema-typed tools, and the browser’s agent calls them directly, inside the user’s live, logged-in session, with the human watching and in control. This book explains why that matters, how WebMCP relates to Anthropic’s Model Context Protocol (MCP), and how to use the API to make a real product agent-ready without rebuilding it. It covers registering tools, wiring them into React and Angular, testing them with evals, and hardening them against prompt injection and over-reach. It also gives an honest map of a standard still being argued over, with Google and Microsoft shipping trials, Mozilla neutral, and WebKit opposed, so readers can build now and still be ready for whatever WebMCP becomes.

## Target reader

| Primary reader | Front-end and full-stack web developers who build production web apps (JavaScript or TypeScript, with React, Angular or similar) and want a hands-on path from first tool to production.                         |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Second reader  | Product managers, tech leads and engineering managers who must decide whether, where and when to invest in agent-readiness. Part VI and the chapter openers are written so they can read those without the code. |
| Alternative 1  | Make it a narrower reference for framework and library authors, focused on spec algorithms, lifecycle and integration. It would be smaller and date faster.                                                      |
| Alternative 2  | Make it a short strategy book for executives and product leaders about the agentic web, with WebMCP as the main case study and little code.                                                                      |
| Alternative 3  | Make it a security-first book for AppSec and privacy engineers: threat models, consent and agent safety across MCP and WebMCP.                                                                                   |

## Chapter outline

17 chapters in six parts. Each chapter has a summary, its key sections, and the running projects it uses.

### Part I: Why the Web Needs an Agent Interface

#### Chapter 1: The Agentic Web Arrives

Agents now act inside browsers on users’ behalf. This chapter shows why today’s approach, “actuation” through screenshots and DOM scraping, is slow, costly and fragile, and why sites have a stake in fixing it.

- What browser agents are: built-in assistants, extensions and page-embedded agents
- Actuation explained, and where it fails: layout changes, ambiguous controls, multi-step forms
- Cost, latency and reliability: the case for structured interaction
- Humans and agents working together in the same tab
- What this book will and will not cover

*Projects:* All projects introduced

#### Chapter 2: From APIs to Tools: A Short History

The path from REST and OpenAPI to LLM function calling, ChatGPT Actions and agent-to-agent protocols, which explains why “tools” became the unit of agent capability.

- Function calling and JSON Schema as a common language
- OpenAPI and platform plug-ins (ChatGPT Actions)
- Why a different integration for every platform does not scale
- A2A and other agent-to-agent efforts
- Where the browser fits

*Projects:* —

#### Chapter 3: MCP in Practice

A working understanding of Anthropic’s Model Context Protocol: hosts, clients and servers over JSON-RPC, and what servers and clients offer each other. This is the vocabulary WebMCP borrows.

- Architecture: hosts, clients, servers; JSON-RPC 2.0; capability negotiation
- Server features (tools, resources, prompts) and client features (elicitation)
- Building a tiny MCP server for the running store project
- MCP Apps and streaming: MCP’s move toward UI
- Spec versioning: what “2026-07-28 (latest)” means for authors

*Projects:* Trailhead (backend MCP server)

#### Chapter 4: Enter WebMCP

Where WebMCP came from: community experiments such as MCP-B, a joint Microsoft and Google explainer, and incubation in the W3C Web Machine Learning Community Group. Also what it deliberately is not.

- Origin story: MCP-B, the explainer repo (Aug 2025) and the Community Group
- Goals and non-goals; the “page as a client-side MCP server” idea
- WebMCP vs MCP: “call center vs in-store expert”; tab-bound and ephemeral vs persistent
- Alternatives considered: adopting MCP directly, static manifests, a toolcall event
- Who’s involved and how decisions get made

*Projects:* —

### Part II: The WebMCP API in Depth

#### Chapter 5: Registering Tools with document.modelContext

The core imperative API: registering a tool with a name, title, description, JSON Schema input and an async execute callback, and removing it again.

- Feature detection and secure-context requirements
- registerTool(): name rules, title, description, inputSchema
- The execute callback: inputs, return values, serialization to the agent
- Unregistering with AbortSignal, and why the API moved from navigator.modelContext and provideContext()
- TypeScript typings (webmcp-types)

*Projects:* Fjord Table, Trailhead

#### Chapter 6: Annotations, Lifecycle and Errors

How the four annotation hints shape agent behaviour, what happens step by step when a tool is called, and how failures and cancellation reach the caller.

- readOnlyHint, untrustedContentHint, consequentialHint and debugging
- Lifecycle of a tool call; tool execution across navigations (null results)
- Cancellation via the execute signal; long-running work
- Platform errors (NotFoundError, DataError, OperationError, AbortError) vs tool-level errors
- The toolchange event and keeping agents in sync

*Projects:* Trailhead

#### Chapter 7: Frames, Origins and Page-Embedded Agents

WebMCP beyond the top-level page: Permissions Policy gating, exposing tools to specific origins, and discovering and executing tools from an agent that lives in the page or in an extension.

- The “tools” Permissions Policy: defaults, allow="tools", Permissions-Policy: tools=()
- exposedTo and fromOrigins: two-sided cross-origin opt-in
- getTools() and executeTool(): building an in-page agent
- Extensions as agents: content scripts and the proposed WebExtensions API
- Design note: is this really a general communication primitive?

*Projects:* Helpdesk Widget

#### Chapter 8: The Declarative API: Forms as Tools

Turning existing HTML forms into tools with attributes, and the events, submit handling and CSS hooks that support it. The chapter is explicit that this part has been taken out of the spec and is being explored separately.

- toolname, tooldescription, toolparamdescription; schema synthesis from labels
- Submission: toolautosubmit, SubmitEvent.agentInvoked and respondWith()
- toolactivated and toolcancel events; :tool-form-active and :tool-submit-active
- Limits for JS-driven forms; validation feedback to agents
- Status: in Chrome’s docs and trial, out of the spec since Oct 2026

*Projects:* Fjord Table

### Part III: Building Agent-Ready Apps

#### Chapter 9: Your First WebMCP App, End to End

A full walkthrough: enable the flag or origin trial, add tools to a small app as a progressive enhancement, and drive it with Chrome’s inspector extension and a test agent.

- Local setup: chrome://flags/#enable-webmcp-testing; registering for the origin trial
- Progressive enhancement and graceful fallback when the API is missing
- Using the Model Context Tool Inspector and the example agent extension
- Polyfills and bridges (MCP-B) for non-supporting browsers and desktop MCP clients
- Deploying with an origin-trial token

*Projects:* Fjord Table

#### Chapter 10: WebMCP in Frameworks

Production patterns for component-based apps: tool registration tied to component and DI lifecycles, shared state, and routing.

- React: the usewebmcp hook, mount and unmount, schema-driven types
- Angular: DI-scoped tools and Signal Forms as tools
- Tools as thin wrappers over existing app logic, not a second app
- SPAs, routing and dynamic tool sets per view; unregistering without breaking in-flight calls
- State sync: telling the agent what changed on the page

*Projects:* Trailhead (React)

#### Chapter 11: Designing Tools Agents Can Actually Use

Tool design as product design: how many tools, how coarse, how to name and describe them, and what to return so an LLM picks the right one and uses it correctly.

- Tool strategy and budget; coarse vs fine-grained tools; collections and “skills” proposals
- Naming, descriptions and character budgets (descriptions, parameters, outputs)
- Schemas that reduce ambiguity: enums, oneOf with titles, required fields
- Returning useful results and errors; refusals vs failures
- Keeping agent-facing text in step with the UI

*Projects:* Trailhead, Helpdesk Widget

### Part IV: Trust: Security, Privacy and Consent

#### Chapter 12: Threat Models for Tool-Exposing Pages

The attack surface WebMCP creates for sites, agents and users, mapped to the spec’s own threat analysis and to concrete mitigations a team can apply today.

- Indirect prompt injection and untrusted tool output
- Tool poisoning: misleading descriptions and declared vs actual behaviour
- Over-parameterisation and personalisation-to-fingerprinting
- Cross-origin exposure, third-party scripts and compromised dependencies
- Mitigations: Permissions Policy, input limits, hints, least-exposure defaults

*Projects:* Helpdesk Widget, Trailhead

#### Chapter 13: Privacy, Consent and the Human in the Loop

Who approves what, and when. This chapter covers confirmation for consequential actions, the unresolved elicitation design, authenticated sessions, accessibility, and how to build UX that keeps users in control.

- Consequential actions and confirmation UX; agent vs browser vs page responsibilities
- Elicitation proposals (requestUserInteraction, requestUserInput) and their status
- Logged-in state, sensitive data and cross-origin data flow
- Agent identity, allowlists and user activation
- Accessibility: agents as assistive technology, and the WebKit critique

*Projects:* Trailhead checkout

### Part V: Shipping and the Ecosystem

#### Chapter 14: Testing, Debugging and Evals

How to know your tools work when the caller is probabilistic: DevTools support, protocol-level testing, eval suites and measurement in production.

- Chrome and Edge DevTools WebMCP panels; the WebMCP DevTools Protocol domain
- Unit and integration tests for execute callbacks; web-platform-tests
- Designing evals: task suites, success criteria, regression runs across models
- Real-user measurement and agent analytics
- Feeding origin-trial findings back to the Community Group

*Projects:* Fjord Table, Trailhead, Helpdesk Widget, Test Agent

#### Chapter 15: Browser Support and the Standards Road

Who implements what, how a Community Group draft becomes (or doesn’t become) a standard, and how to read origin trials, standards positions and TAG reviews.

- Chrome and Edge origin trials: timelines, tokens, extensions, what can change
- Firefox (neutral) and WebKit (oppose): the arguments in their own words
- Agents that consume WebMCP today: ChatGPT Desktop, Brave Leo, extensions, glasses
- Community libraries: MCP-B, polyfills, framework packages
- CG to WG: the possible paths and what each would mean for adopters

*Projects:* —

### Part VI: Strategy and the Future

#### Chapter 16: Product and Business Implications

What agent-readiness means for product strategy: which journeys to expose first, brand control versus aggregation, conversion and attribution, and how WebMCP and backend MCP fit into one plan.

- Agent-readiness as the new SEO: discoverability and its limits (no central registry)
- Choosing first journeys: search, configure, book, support
- Brand, UX ownership and keeping the agent a guest on your site
- Measuring agent-driven conversion; pricing and policy questions
- Org design: who owns tools, descriptions and evals

*Projects:* Trailhead

#### Chapter 17: The Road Ahead

The open questions that will decide what WebMCP becomes, and how to build today so that your investment survives either outcome.

- Output schemas, multimodal and streaming inputs and outputs
- Cross-document responses and service-worker tools for sites that aren’t open
- Built-in agent exposure defaults (a “native-agent” keyword)
- Competing futures: richer HTML and ARIA semantics, or a generic cross-environment call API
- A future-proofing checklist

*Projects:* —

### Appendices

- A. API quick reference (IDL, attributes, events, errors)
- B. Glossary (agent, browser agent, actuation, tool, annotation, origin trial)
- C. Resource directory and how to track changes
- D. Migration notes: navigator.modelContext and provideContext() to document.modelContext

## Hands-on projects that run through the book

| Project               | What it teaches                                                                                                                                                                                                                                      | Chapters              |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| Fjord Table           | A small restaurant-booking site. It starts as plain HTML forms made agent-callable with the declarative attributes, then moves to imperative tools when the form flow outgrows them. Used for the first-app walkthrough and the declarative chapter. | Ch 5, 8, 9            |
| Trailhead             | An outdoor-gear store in React with search_products, compare, add_to_cart and a checkout marked consequential. It shows annotations, framework lifecycles, consent UX, evals and the business chapter, alongside a companion backend MCP server.     | Ch 3, 5, 6, 10–14, 16 |
| Helpdesk Widget       | A support widget from a third-party origin embedded in a SaaS dashboard. It exercises Permissions Policy, exposedTo and fromOrigins, an in-page agent built on getTools() and executeTool(), and cross-origin threat modelling.                      | Ch 7, 11, 12, 14      |
| Test Agent (optional) | A minimal agent harness, either an extension or an in-page agent using an on-device model through Chrome’s Prompt API, used to call the tools and run evals without depending on any one assistant.                                                  | Ch 9, 14              |

## Key official resources

| Resource                                    | URL                                                                                                      | Date                                     |
|---------------------------------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------|
| WebMCP specification (Draft CG Report)      | https://webmachinelearning.github.io/webmcp                                                              | 13 Oct 2026                              |
| Explainer and issue tracker (GitHub)        | https://github.com/webmachinelearning/webmcp                                                             | repo since Aug 2025; updated 13 Oct 2026 |
| Implementation status (browsers and agents) | https://github.com/webmachinelearning/webmcp/blob/main/implementation-status.md                          | read 14 Oct 2026                         |
| Declarative API explainer                   | https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md                      | removed from spec 8 Oct 2026             |
| Chrome docs: WebMCP overview                | https://developer.chrome.com/docs/ai/webmcp                                                              | 18 May 2026; updated 7 Oct 2026          |
| Chrome docs: Imperative / Declarative API   | https://developer.chrome.com/docs/ai/webmcp/imperative-api                                               | updated 21 and 25 Sep 2026               |
| Chrome docs: WebMCP vs MCP                  | https://developer.chrome.com/docs/ai/webmcp/compare-mcp                                                  | 11 Mar 2026; updated 19 May 2026         |
| Chrome docs: Tool security guidance         | https://developer.chrome.com/docs/ai/webmcp/secure-tools                                                 | 9 Jun 2026; updated 1 Sep 2026           |
| Chrome blog: Join the origin trial          | https://developer.chrome.com/blog/ai-webmcp-origin-trial                                                 | 9 Jun 2026                               |
| Chrome Status entry                         | https://chromestatus.com/feature/5117755740913664                                                        | updated 28 Sep 2026                      |
| Microsoft Edge origin trial                 | https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a | expires 30 Mar 2027                      |
| Chrome demos and extensions                 | https://github.com/GoogleChromeLabs/webmcp-tools                                                         | read 14 Oct 2026                         |
| Model Context Protocol specification        | https://modelcontextprotocol.io/specification/latest                                                     | version 2026-07-28                       |
| Mozilla standards position (neutral)        | https://github.com/mozilla/standards-positions/issues/1412                                               | Aug 2026                                 |
| WebKit standards position (oppose)          | https://github.com/WebKit/standards-positions/issues/670                                                 | Jun 2026                                 |
| W3C TAG design review                       | https://github.com/w3ctag/design-reviews/issues/1238                                                     | open; update 9 Oct 2026                  |
| MCP-B documentation (community)             | https://docs.mcp-b.ai/                                                                                   | read 14 Oct 2026                         |

## What is still in flux and could date the book

- The entry point moved. The API moved from navigator.modelContext to document.modelContext (May 2026), and provideContext() and clearContext() were removed (Mar 2026). Many 2025–26 tutorials and some community notes still show the old shape.
- Declarative API status. It was removed from the spec on 8 Oct 2026 but is still documented and shipped in Chrome’s trial. Attribute names, events and CSS pseudo-classes could change or disappear.
- Origin-trial churn. Chrome changes the API between milestones: JSON-string inputs deprecated in 155, window-level tool events dropped in 156, the debugging hint added in 156. The trial now runs to Chrome 162, and there is no shipping decision yet.
- Consent and elicitation are unresolved. Chrome’s security page refers to requestUserInteraction(), but the current spec has no such method. Issues #165 and #204 are still open.
- Pending features. outputSchema (#254, #9), multimodal I/O, streaming, cross-document responses (#135), service workers, skills (#161), tool collections (#255) and a native-agent exposure keyword. Any of these could change chapters 5–8.
- Cross-browser future. WebKit is opposed, Mozilla is neutral but negotiating, and the TAG review is still open. A proposed repositioning as a generic cross-environment call API (#236) could reshape the API.
- Guidance numbers. Chrome’s character budgets and best practices are explicitly provisional, and the spec may set hard limits.
- Agent support list. Which assistants consume WebMCP is moving fast. ChatGPT Desktop, Brave Leo and Meta glasses are listed by the explainer, not by the vendors’ own docs. Whether Chrome’s built-in Gemini will call WebMCP tools is not stated in the sources.
- MCP itself versions often. Its latest spec is 2026-07-28. Keep MCP comparisons at the level of concepts.

> Suggested approach: write Parts I, IV and VI first, since they are the most durable. Keep API detail in Part II tied to a dated “as of” box per chapter, and keep a companion site or repository for code that will churn. Re-verify every API name against the live spec right before the manuscript is final.
