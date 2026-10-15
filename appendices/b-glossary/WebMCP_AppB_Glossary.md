*Appendices*

# Appendix B: Glossary

> *“An agent is an autonomous assistant that can understand a user’s goals and take actions on the user’s behalf to achieve them.”*
>
> — WebMCP specification, §2 Terminology[^1]

This glossary collects the terms the book uses, defined the way the chapters use them. Each entry ends with a pointer to the chapter that introduces the term, and sometimes to the chapter that goes deepest. Where a definition comes from outside the book, from the WebMCP draft, the MCP specification, the W3C Process, MDN or Chrome’s documentation, a footnote names the page. Every one of those pages was read on 14 October 2026 and checked again on 15 October 2026.

Code identifiers are in `code font` and sort as if they had no punctuation, so `document.modelContext` sits under D and `:tool-form-active` under T. Section B.2 covers the book’s running examples and the people in them.

> **Still in flux: the vocabulary itself**
>
> WebMCP is a Community Group draft, and its words move with it. During 2026 the entry point has changed objects, two methods have gone, the annotations have moved into their own dictionary and the declarative attributes have left the specification (Appendix D). Entries marked *removed* or *proposed* describe things you will meet in older code, in Chrome’s trial or in open issues, but not in the 15 October 2026 draft.

## B.1 Terms, A to Z

### A

**A2A (Agent2Agent protocol).** A protocol, announced by Google in April 2025 and now under the Agentic AI Foundation, that connects opaque agents to each other. An A2A agent publishes an *Agent Card* describing what it can do, and other agents delegate whole tasks to it rather than calling individual tools. *Chapter 2.*

**AbortController, AbortSignal.** The DOM’s standard way to cancel asynchronous work. A controller owns a signal; calling `abort()` on the controller sets the signal’s `aborted` flag and fires its `abort` event.[^2] WebMCP uses signals twice: the `signal` you pass to `registerTool()` unregisters the tool when aborted, and the *execution signal* your `execute` callback receives tells you a running call has been cancelled. *Chapter 5 (registration), Chapter 6 (execution).*

**AbortError.** The `DOMException` the draft specifies when a tool call’s target document unloads. In the book’s tests Chromium 156 returned it only when the calling agent cancelled the call itself, and reported the other cases as `UnknownError`. *Chapter 5; Chapter 6; Chapter 8; Appendix A.*

**actuation.** How most browser agents operate websites today. Chrome’s documentation defines it as “the act of an agent simulating manual mouse clicks and text input, as though it were the human user engaging with your website.”[^3] The agent observes the page through screenshots, DOM or accessibility-tree snapshots, then clicks and types, one model call per step. *Chapter 1.*

**actuation tax.** The book’s name for what actuation costs: brittle, slow, ambiguous interaction with interfaces designed for people, paid in tokens, latency and failed tasks. *Chapter 4.*

**agent.** An autonomous assistant that understands a user’s goals and acts on the user’s behalf, today usually built on a large language model.[^1] *Chapter 1.*

**agent-driven conversion.** A business outcome, such as an order, that an agent’s tool calls helped to bring about. Trailhead records which tools succeeded in the current tab session and attaches that list to the order. *Chapter 16; real-user measurement in Chapter 14.*

**agent identity.** Whether, and how, a page can tell which agent is calling its tools. The draft gives the page no such signal today; open issues propose verification frameworks, allowlists and OAuth-style client identities. *Chapter 13; Chapter 16.*

**agent-readiness.** Making a product work well for people who arrive through an agent, the way accessibility and mobile layouts make it work for other ways of arriving. In this book it mostly means offering good tools. *Chapter 1; Chapter 16.*

**Agentic AI Foundation.** A directed fund under the Linux Foundation that has governed MCP since Anthropic donated it on 9 December 2025, and A2A since later in 2026. *Chapter 2.*

**Agentic Web Working Group.** A proposed W3C Working Group whose draft charter names WebMCP as its one normative deliverable, with the draft state “Adopted from the Web Machine Learning Community Group”. The charter’s mission is “to develop specifications that facilitate web pages and applications to be leveraged by LLMs and AI agents.”[^4] The W3C announced charter refinement on 1 October 2026 and expected it to last until about 10 November 2026.[^5] *Chapter 4; Chapter 15; Chapter 17.*

**agentInvoked.** *Declarative API, removed from the spec.* A boolean on `SubmitEvent` that is true when an agent, not a person, submitted a declarative tool’s form. *Chapter 8.*

**annotations.** The optional `annotations` member of a tool definition: a `ToolAnnotations` dictionary of boolean hints that tell agents how to treat the tool. In the 15 October draft the members are `readOnlyHint`, `untrustedContentHint`, `consequentialHint` and `debugging`, all defaulting to `false`.[^6] They are hints, not enforcement. MCP has its own, different set (see *MCP tool annotations*). *Chapter 6.*

**attribution.** In Chapter 16, linking an agent’s tool calls to the outcomes they led to, so that agent help shows up next to the orders it contributed to. *Chapter 16.*

### B

**book_table.** Fjord Table’s consequential tool. It books a table and is only completed after the person confirms in the site’s own dialog. *Chapter 4; in detail in Chapter 5.*

**browser agent.** In the draft, “an agent provided by or through the browser,” built in or hosted through an extension or plug-in.[^1] It doesn’t run JavaScript on the page; it sees tools through an *observation*. The book also uses the phrase loosely, as in Chapter 1, for any agent that acts on web pages: built-in assistants, extensions and page-embedded agents. *Chapter 1; precise sense in Chapter 7.*

### C

**`cancelled_by_user`.** The result status a tool returns when the person declined in the page’s own UI, shaped `{ status: 'cancelled_by_user', message }`. The agent stops and doesn’t retry unless the user asks again. Not to be confused with `toolcancel`, which is a platform event, not a result. *Chapter 5 (Fjord Table’s `book_table`); Chapter 6; the convention in Chapter 11.*

**carrier.** One of the three roles Chapter 12 gives a tool-exposing page in an attack: the page whose tool delivers somebody else’s text, such as a community answer, into an agent’s context. The other roles are *target* and *attacker*. *Chapter 12.*

**character budget.** A cap on the length of agent-facing text. Chrome’s security guidance recommends about 500 characters per tool description and 150 per parameter description,[^7] and Chapter 11 enforces budgets in a test. *Chapter 11; Chapter 16.*

**charter.** The document that creates a W3C Working Group and sets its scope, deliverables, duration and decision policy. A Community Group has a charter too, but only a Working Group’s charter goes through W3C-wide review. *Chapter 4; Chapter 15.*

**chromestatus.** Chrome’s public feature tracker. The WebMCP entry records a developer trial from Chrome 146 and an origin trial from Chrome 149 through 156 (since extended to 162), with the feature’s status shown as “Proposed”.[^8] *Chapter 4; Chapter 15.*

**`clearContext()`.** *Removed 5 March 2026.* An early method that unregistered every tool a page had provided. Today you abort each tool’s signal instead. *Chapter 4; Appendix D.*

**client (MCP).** A connector inside an MCP host. Each client “communicates with exactly one server” and attaches the protocol version and capabilities to every request.[^9] *Chapter 3.*

**Community Group (CG).** An open W3C forum, without fees, for incubating new technology. The W3C’s own FAQ is plain about the limit: “Community Groups do not create W3C standards.”[^10] WebMCP is incubated in the Web Machine Learning Community Group. *Chapter 4; Chapter 15.*

**confirmation sheet.** Trailhead’s own checkout dialog, which a person must click to complete a purchase an agent started. It accepts only a trusted click, after a short arming delay, and closes if the call is cancelled. *Chapter 13.*

**confused deputy.** A program that holds someone’s authority and can be tricked into using it for someone else. Chapter 12 calls a WebMCP agent “a confused deputy waiting to happen”: it carries the user’s sessions and reads text from every site it touches. *Chapter 12.*

**consequential.** The book’s word for an action with real-world effects that is hard or impossible to undo, such as booking, paying or sending. *Chapter 5; formalised as `consequentialHint` in Chapter 6.*

**`consequentialHint`.** An annotation that says executing the tool “will result in consequential actions that are significant, real-world, or non-reversible”.[^6] Trailhead’s `checkout` and Fjord Table’s `book_table` set it. *Chapter 6.*

**continuation token.** *Proposed.* A design, published as a supplementary explainer and merged into the WebMCP repository on 2 October 2026, for returning a tool’s result after the call causes a navigation. *Chapter 17.*

**cross-origin exposure.** Chapter 12’s fifth threat: tools reaching, or being reached by, frames from other origins in ways the author didn’t intend. The mitigations are the `tools` Permissions Policy, `exposedTo` and `fromOrigins`. *Chapter 12; mechanisms in Chapter 7.*

### D

**DataError.** The `DOMException` the draft specifies when a tool call’s input is invalid, for example input that isn’t a JSON object. *Chapter 5; Chapter 6; Appendix A.*

**`debugging`.** An annotation that marks a tool as intended for developer tooling rather than for agents serving users. *Chapter 6; use in Chapter 14.*

**declarative API.** *Removed from the spec on 8 October 2026; still in Chrome’s trial.* Turning an HTML `<form>` into a tool with attributes (`toolname`, `tooldescription`, `toolparamdescription`, `toolautosubmit`), with the browser synthesizing the input schema from the form’s controls. It now lives in a separate explainer. *Chapter 8; Appendix A.*

**developer trial.** A feature available behind a browser flag, for local testing only. WebMCP’s Chromium developer trial began in Chrome 146.[^8] *Chapter 4; Chapter 15.*

**DevTools WebMCP pane.** A pane in the Application panel of Chrome DevTools. It lists a page’s tools as the agent sees them and logs every call with its status. *Chapter 9; Chapter 14.*

**`document.modelContext`.** The entry point of the WebMCP API: a `ModelContext` object on every `Document` in a secure context. The getter moved here from `Navigator` on 27 May 2026; before that the API was `navigator.modelContext`. *Chapter 4; in detail in Chapter 5.*

**dual-era server.** An MCP server that serves both protocol eras: stateless *modern* requests (2026-07-28) and handshake-based *legacy* sessions (2025-11-25 and earlier). Trailhead’s backend server is one. *Chapter 3.*

### E

**elicitation.** In MCP, a server asking the user for more information through the client in the middle of an interaction, in a form mode or a URL mode.[^11] WebMCP has no equivalent in the current draft; see `requestUserInteraction()`. *Chapter 3; for WebMCP, Chapter 13.*

**eval.** A test that hands the choice of tool to a model. You give a model a user’s request and the page’s tools, run the calls it makes against the real page, and score the result for tool selection, parameter extraction and state management. *Chapter 14.*

**Example Agentic Chrome Extension.** A small but complete sample agent from Chrome’s WebMCP tooling. It chats in the side panel, discovers tools with `getTools()`, follows `toolchange` and talks to a cloud model through a local server or to the on-device model through the Prompt API. *Chapter 9.*

**execute.** The callback in a tool definition that does the work. The browser calls `execute(input, { signal })` on the page’s main thread with the parsed input and an execution signal; whatever it returns becomes the tool’s result. The browser doesn’t validate input against `inputSchema`, so `execute` must. *Chapter 5; lifecycle in Chapter 6.*

**execution signal.** The `AbortSignal` in the second argument to `execute`. The browser creates a fresh one for each call and aborts it when the call is cancelled. Aborting the *registration* signal does not abort calls already running. *Chapter 6; Chapter 10.*

**`executeTool()`.** The `ModelContext` method an in-page agent uses to call a tool it got from `getTools()`. It resolves with the tool’s result as a string. *Chapter 7.*

**explainer.** A non-normative document that sets out the problem a web feature solves, its use cases and the proposed shape, usually before or alongside a specification. WebMCP’s main explainer is its repository’s README; *supplementary explainers* cover the declarative API, service workers and continuations. *Chapter 4; reading explainers in Chapter 17.*

**`exposedTo`.** A `registerTool()` option: a list of origins whose documents in the same frame tree may see the tool through `getTools()`. Without it, a tool is visible only to same-origin documents. It does not affect the browser agent. *Chapter 7.*

**extended user context, cross-site context.** Two of the draft’s assumptions about agents. Besides the user’s identity, an agent may hold personalisation data, history and payment information, and it may correlate what it learned on one site with what it does on another. *Chapter 12.*

### F

**feature detection.** Checking for an API before using it, here `if ('modelContext' in document)`. It tells you the API exists, not that a Permissions Policy allows you to use it. *Chapter 5; the policy gap in Chapter 7.*

**formal objection.** A W3C member’s formal disagreement with a decision, such as a charter. Under the W3C Process it must receive formal consideration and a formal response, and one the Team cannot resolve goes to the W3C Council.[^12] Apple warned of one when a pull request proposed moving WebMCP into the Web Machine Learning Working Group; that pull request was closed unmerged on 13 October 2026. *Chapter 15.*

**`fromOrigins`.** A `getTools()` option: the other origins whose exposed tools the caller wants to see. A tool appears only if its owner listed the caller in `exposedTo` and the caller listed the owner in `fromOrigins`. *Chapter 7.*

**function calling.** The model-API feature, introduced by OpenAI in June 2023 and adopted across vendors, in which an application describes functions with a name, a description and a JSON Schema, and the model returns structured calls to them. *Chapter 2.*

### G

**`getTools()`.** The `ModelContext` method an in-page agent uses to list the tools it may call, from its own document and from frames that exposed tools to it. It resolves with `RegisteredTool` objects, sorted by name. *Chapter 7.*

### H

**host (MCP).** The AI application in MCP’s architecture: it creates one client per server connection and keeps the conversation history and the security boundaries between servers.[^9] *Chapter 3.*

**human in the loop.** Keeping the person present and in control while an agent acts. The WebMCP explainer puts cooperative, human-in-the-loop use ahead of full autonomy, which is why the site’s own confirmations matter. *Chapter 1; Chapter 13.*

### I

**in-page agent.** An agent written in JavaScript that runs inside a document, possibly in an iframe, and reaches tools through `getTools()` and `executeTool()`. Chapter 1 calls this kind a *page-embedded agent*. *Chapter 7.*

**`inputSchema`.** The JSON Schema object in a tool definition that describes the tool’s input. Optional in the draft. The agent treats it as guidance; the browser does not enforce it. *Chapter 5; schema design in Chapter 11.*

**`instrumentTool()`.** Chapter 14’s wrapper for real-user measurement. It wraps a tool’s `execute`, records how long each call took and how it ended, and reports no inputs or outputs. The outcome is one of seven words: `ok`, the four non-success result statuses (`error`, `needs_input`, `refused`, `cancelled_by_user`), `threw` for an exception, and `aborted` when the caller’s signal ended the call. A caller’s abort is never counted as `cancelled_by_user`. Chapter 16’s `measure.ts` uses the same seven words. *Chapter 14; Chapter 16.*

**InvalidStateError.** The `DOMException` `registerTool()` rejects with for an empty or invalid name, an empty description or a duplicate name. Chromium 156 agrees with the draft here. *Chapter 5; Appendix A.*

**`isTrusted`.** A property of DOM events that is true only for events the browser generated from a real user action. Chapter 13’s confirmation sheet uses it to ignore synthetic clicks. *Chapter 13.*

### J

**JSON-LD response.** *Declarative API.* How Chrome’s trial answers an agent when a declarative tool’s form navigates without `respondWith()`: the agent receives the JSON-LD on the next page, as an array. *Chapter 8; successor designs in Chapter 17.*

**JSON-RPC 2.0.** The message format MCP uses: requests, responses and notifications as JSON objects. Its specification calls it “a stateless, light-weight remote procedure call (RPC) protocol.”[^13] *Chapter 3.*

**JSON Schema.** The vocabulary for describing the shape of JSON data that function calling, MCP and WebMCP all use for tool inputs. Its current version is 2020-12.[^14] *Chapter 2.*

### L

**legacy and modern (MCP).** The MCP specification’s names for the two protocol eras: *legacy* revisions (2025-11-25 and earlier) open a session with an `initialize` handshake; *modern* ones (2026-07-28 on) are stateless. *Chapter 3.*

**local relay.** A bridge that connects a browser tab’s WebMCP tools to desktop MCP clients. The book uses `@mcp-b/webmcp-local-relay`, which talks to the page through a hidden iframe and a localhost WebSocket. *Chapter 9.*

### M

**MCP (Model Context Protocol).** An open protocol, open-sourced by Anthropic on 25 November 2024, for connecting AI applications to tools and data. Hosts run clients; clients talk to servers, which offer tools, resources and prompts. WebMCP borrows its vocabulary but is a separate specification. *Chapter 2; Chapter 3.*

**MCP 2026-07-28.** The MCP revision current while this book was written. It made the protocol stateless. The changelog’s words are “Make MCP stateless: remove the initialize / notifications/initialized handshake”, and every request now carries its protocol version and client capabilities.[^15] *Chapter 3.*

**MCP Apps.** An MCP extension that lets servers return interactive user interface for the host to render. *Chapter 3.*

**MCP-B.** The community project that built WebMCP-shaped libraries before the browsers did, and that maintains the `@mcp-b/*` packages and `usewebmcp`. *Chapter 4 (history); Chapter 9.*

**MCP Inspector.** The official developer tool for exercising MCP servers, available as a web UI and a CLI. Chapter 3 tests Trailhead’s server with version 2.11.0. *Chapter 3.*

**MCP tool annotations.** MCP’s behaviour hints on a tool: `readOnlyHint` (default `false`), `destructiveHint` (default `true`), `idempotentHint` (default `false`) and `openWorldHint` (default `true`), plus a display `title`. `destructiveHint` and `idempotentHint` only mean something when `readOnlyHint` is `false`.[^31] The MCP specification requires clients to treat them as untrusted unless they come from trusted servers.[^16] They are not the same set as WebMCP’s annotations: WebMCP has `consequentialHint` and `untrustedContentHint` and no destructive, idempotent or open-world hints. *Chapter 3.*

**misrepresentation of intent.** Chapter 12’s fourth threat: a tool whose name or description says one thing while its code does another, whether by malice or by drift. *Chapter 12.*

**ModelContext.** The interface of `document.modelContext`. It has three methods, `registerTool()`, `getTools()` and `executeTool()`, and three events, `toolchange`, `toolactivated` and `toolcancel`. *Chapter 5; Appendix A.*

**ModelContextTool.** The dictionary you pass to `registerTool()`: `name`, `title`, `description`, `inputSchema`, `execute` and `annotations`. *Chapter 5.*

**Model Context Tool Inspector.** A Chrome extension from the WebMCP tooling collection that lists a page’s tools in the side panel and lets you call them with JSON arguments, or hand a natural-language prompt to a model to see which tools it picks. *Chapter 9; Chapter 14.*

### N

**N × M problem.** The arithmetic behind MCP: N AI applications and M services need up to N × M bespoke integrations, but only N + M if both sides speak one protocol. *Chapter 2.*

**`native-agent`.** *Proposed.* A keyword the explainer’s authors are considering for `exposedTo`, to control whether the browser’s built-in agent sees a tool. *Chapter 17.*

**`navigator.modelContext`.** *Moved to `document.modelContext` on 27 May 2026.* The original location of the API. Chromium 156 doesn’t expose it. *Chapter 4; Appendix D.*

**`needs_input`.** The result status for a call that needs something only the user knows, shaped `{ status: 'needs_input', code: 'MISSING_INFORMATION', missing, message }`, where `missing` lists what to ask for (for example `missing: ['size']`). The agent asks the user, then calls again. *Chapter 11; used in Chapter 13.*

**NotAllowedError.** The `DOMException` the WebMCP methods reject with when the `tools` Permissions Policy doesn’t allow the document to use them. *Chapter 7; Appendix A.*

**NotFoundError.** The `DOMException` the draft specifies when a called tool doesn’t exist in the target document (for example after it was unregistered), when the target’s origin doesn’t match the tool’s `origin`, or when the tool isn’t exposed to the caller. Chromium 156 reports `UnknownError` instead, which is spec lag, not a bug. *Chapter 5; Chapter 6; Appendix A.*

### O

**observation.** In the draft, the implementation-defined snapshot a browser agent takes of a page, which includes at least a tool map: every document in the frame tree with its origin and tools. *Chapter 7.*

**OpenAPI.** A standard way to describe HTTP APIs, which began as Swagger. ChatGPT plug-ins and GPT actions used it to give assistants tools. *Chapter 2.*

**OperationError.** The `DOMException` the draft specifies when a tool’s callback rejects or its result can’t be serialized. Chromium 156 reports a thrown error as `UnknownError` (spec lag, not a bug) and resolves some unserializable results, such as `undefined`, instead of rejecting. *Chapter 5; Chapter 6; Appendix A.*

**`orderState`.** The field that carries a Trailhead order’s state (`'shipped'`, `'processing'`) in the backend MCP server’s `get_order_status` results. Like `ticketState`, it is named so that `status` stays reserved for the call’s outcome (see *result status*). *Chapter 3.*

**origin trial.** A time-limited way for a site to turn on an experimental feature for real visitors by registering its origin and serving a token. Chrome’s documentation says origin trials give access to a feature “so that you can test this feature and offer it to your users, for a limited time.”[^17] WebMCP has trials in Chrome (149 to 162) and Edge (until 30 March 2027).[^8][^18] *Chapter 4; tokens in Chapter 9; Chapter 15.*

**origin-trial token.** The signed string that enables a trial feature on a registered origin, delivered in a `<meta http-equiv="origin-trial">` tag or an `Origin-Trial` response header. *Chapter 9; Chapter 15.*

**`outputSchema`.** A JSON Schema describing a tool’s result. MCP has one, paired with `structuredContent`. WebMCP doesn’t yet; adding it is open spec work. *Chapter 3 (MCP); Chapter 17 (WebMCP).*

**output injection.** Prompt injection that rides out of your tool in its result, for example in user-generated content the tool returns. Mark such tools with `untrustedContentHint`. *Chapter 12.*

**over-parameterisation.** Chapter 12’s third threat: a tool that asks for more input than its task needs, turning a personalisation feature into a way to collect data from the agent’s context. *Chapter 12; first mentioned in Chapter 5.*

### P

**page-embedded agent.** Chapter 1’s name for an agent that ships inside a website; Chapter 7 calls it an *in-page agent*. *Chapter 1.*

**Permissions Policy.** The web platform mechanism, set by the `Permissions-Policy` header or an iframe’s `allow` attribute, “to allow and deny the use of browser features in a document or within any `<iframe>` elements”.[^19] WebMCP defines a policy-controlled feature named `tools` whose default allowlist is `'self'`, so cross-origin frames can’t use the API unless the embedder delegates it with `allow="tools"`. *Chapter 7; Chapter 12.*

**polyfill.** A script that implements a missing web API in JavaScript. For WebMCP the book uses MCP-B’s `@mcp-b/global` and `@mcp-b/webmcp-polyfill` (both 6.0.3 on 15 October 2026), which are second implementations with their own schedules.[^20] *Chapter 9; cautions in Chapter 15.*

**potentially trustworthy origin.** An origin the web platform treats as secure, such as `https:` or `http://localhost`. `exposedTo` and `fromOrigins` accept only these and throw `SecurityError` for anything else. *Chapter 5; Chapter 7.*

**progressive enhancement.** Building the page so it works without WebMCP and adds tools only where the API exists. Every project in the book follows it. *Chapter 9.*

**prompt injection.** Text that an agent reads as instructions although it came from content, such as a product review, a web page or a tool result. *Chapter 12; first mentioned in Chapter 1.*

**Prompt API.** Chrome’s built-in API for sending natural-language requests to an on-device model.[^21] The Test Agent can use it as its planner. *Chapter 1; Chapter 9.*

**prompts (MCP).** Templated messages a server offers, controlled by the user, such as Trailhead’s `packing_list`. *Chapter 3.*

**`provideContext()`.** *Removed 5 March 2026.* An early method that replaced a page’s whole tool set in one call. *Chapter 4; Appendix D.*

### R

**`readOnlyHint`.** An annotation that says the tool “does not modify any state and only reads data.”[^6] Trailhead’s `search_products`, `compare_products` and `get_cart` set it. *Chapter 6.*

**refusal.** A tool outcome where the arguments were fine but a rule says no: a purchase limit, a sold-out item, a rate limit. It is returned as `{ status: 'refused', code, message }`, for example `code: 'OUT_OF_STOCK'` for a sold-out item or the Helpdesk Widget’s `TICKET_LIMIT` (see *result status*). Unlike an error, it isn’t the agent’s to fix by retrying, and Chapter 11 words it so the agent takes the decision back to the person. *Chapter 11; applied in Chapter 6.*

**`registerTool()`.** The method that adds a tool to a document: `document.modelContext.registerTool(tool, { signal, exposedTo })`. There is no `unregisterTool()`; aborting the signal unregisters. *Chapter 4; in detail in Chapter 5.*

**RegisteredTool.** The dictionary `getTools()` returns for each visible tool: its name, title, description, input schema, annotations, and the window and origin it came from. You pass it back to `executeTool()`. *Chapter 7; Appendix A.*

**`requestUserInteraction()`.** *Not in the draft.* An early method for asking the user something during a tool call. It still appears on Chrome’s security page, and issues #165 and #204 discuss replacing it, for example with a `requestUserInput()` modelled on MCP elicitation. Until then, confirmation belongs in your page. *Chapter 4; Chapter 13; Appendix D.*

**resources (MCP).** Context and data a server offers for the application or model to use, addressed by URI, such as Trailhead’s `trailhead://policies/returns`. *Chapter 3.*

**`respondWith()`.** *Declarative API, removed from the spec.* A `SubmitEvent` method that lets a page answer an agent’s form submission with a result, instead of navigating. *Chapter 8.*

**result status.** The book’s convention for what a tool returns, set in Chapter 11 and followed by every chapter: the agent reads `status` first. Success uses a domain word (`added`, `created`, `booked`) or no status at all; the four non-success statuses are `error` (the agent can fix the call), `needs_input` (ask the user), `refused` (a rule says no) and `cancelled_by_user` (stop). Each non-success result carries a stable `code` for programs and a `message` for the model, except `cancelled_by_user`, which carries only a `message`. Because `status` is reserved for the outcome, domain data uses other names, such as `ticketState` and `orderState`. *Chapter 6 (`error`); Chapter 11 (the full set).*

### S

**schema synthesis.** *Declarative API.* The browser writing a JSON Schema from a form’s controls, their types, constraints and labels. The book documents Chromium’s current behaviour in Table 8.1. *Chapter 8.*

**secure context.** An environment, such as a window or worker, that “meets a defined standard of authentication and confidentiality,” in practice HTTPS or localhost.[^22] `document.modelContext` exists only in secure contexts. *Chapter 5; Chapter 9.*

**SecurityError.** The `DOMException` you get when `exposedTo` or `fromOrigins` contains an origin that doesn’t parse or isn’t potentially trustworthy. *Chapter 5; Chapter 7.*

**server (MCP).** A program that offers MCP features (tools, resources, prompts) to a client. It runs locally over stdio or remotely over Streamable HTTP. *Chapter 3.*

**`server/discover`.** The MCP 2026-07-28 method a client can call to learn what a server supports. Servers must implement it, but clients aren’t required to call it. *Chapter 3.*

**service-worker tools.** *Proposed.* A supplementary explainer’s idea for letting a site’s service worker offer tools when none of its pages is open. *Chapter 17.*

**standards position.** A browser engine’s public statement about a proposed web feature. On 15 October 2026 Mozilla’s position on WebMCP was labelled *neutral* and WebKit’s *oppose*.[^23][^24] *Chapter 4; Chapter 15.*

**stateless (MCP).** The defining property of MCP 2026-07-28. There is no session and no handshake: each request carries its own version, client identity and capabilities in `_meta`, so any server instance can answer any request. The specification lists “Stateless, self-contained requests” among the protocol’s key details.[^25] *Chapter 3.*

**stdio.** MCP’s local transport: “newline-delimited messages over the standard streams of a client-launched subprocess.”[^26] *Chapter 3.*

**Streamable HTTP.** MCP’s remote transport: each message is an HTTP POST to one endpoint, and replies come back as JSON or a request-scoped server-sent events stream.[^26] *Chapter 3.*

**structured interaction.** The alternative to actuation: the page offers named, described, schema-typed tools and the agent calls them. *Chapter 1.*

**`structuredContent`.** An MCP tool result’s machine-readable payload, which an `outputSchema` describes. *Chapter 3.*

**Structured Outputs.** OpenAI’s August 2024 feature that turned a function’s JSON Schema from guidance into a hard constraint on the model’s output. *Chapter 2.*

### T

**TAG (Technical Architecture Group).** An elected W3C group that “helps resolve Consortium-wide technical issues”[^12] and reviews new designs. WebMCP’s early design review, opened in June 2026, was still open on 15 October 2026 and labelled “Missing: Multi-stakeholder support”.[^27] *Chapter 4; Chapter 15.*

**target.** In Chapter 12, the role of a page whose tools are called with unexpected arguments by a hijacked agent. *Chapter 12.*

**Test Agent.** The book’s optional minimal agent harness, either an extension or an in-page agent using the Prompt API, for calling tools and running evals without depending on a commercial assistant. Its API is `createTestAgent()` with a `scripted()` planner or a `createPromptPlanner()` that uses the Prompt API. *Chapter 1; built in Chapter 9; reused in Chapter 14’s tests.*

**thin wrapper.** The book’s rule for tool code: a tool should call the same functions the interface already uses, not re-implement them. *Chapter 4; Chapter 9; Chapter 10.*

**`ticketState`.** The field that carries a Helpdesk Widget ticket’s own state (for example `'open'`) in `get_ticket_status` results, named so that `status` stays reserved for the call’s outcome (see *result status*). *Chapter 7; Chapter 11.*

**title.** An optional, human-readable label in a tool definition, for display in browser UI. `getTools()` returns an empty string when it’s missing (issue #224). *Chapter 5; Chapter 11.*

**tool.** A capability offered to a model as a name, a description written for the model and a schema for its input, plus code that runs when called. In WebMCP a tool is registered by a page and runs in the user’s tab. *Chapter 1; history in Chapter 2.*

**tool poisoning.** Prompt injection planted in your own tool descriptions, for example by a compromised dependency that registers or rewrites tools. *Chapter 12.*

**`:tool-form-active`, `:tool-submit-active`.** *Declarative API, still in Chrome’s trial.* CSS pseudo-classes that match a form, and its submit button, while an agent is filling or submitting it. *Chapter 8.*

**`toolactivated`.** The event fired at `document.modelContext` when a tool call begins, with the tool’s name. *Chapter 5; Chapter 6; Chapter 8.*

**`toolautosubmit`.** *Declarative API.* A boolean form attribute that lets the agent submit the form after filling it. Without it, the browser focuses the submit button and the person submits. *Chapter 8.*

**`toolcancel`.** The event fired when a running tool call is cancelled, with the tool’s name. It arrives alongside the abort of the call’s execution signal. *Chapter 6; Chapter 8.*

**`toolchange`.** The event fired at `document.modelContext` when the set of tools changes. Agents use it to know when to re-read the tool list. *Chapter 5; Chapter 6; Chapter 10.*

**`tooldescription`, `toolname`, `toolparamdescription`.** *Declarative API.* Form attributes that give a declarative tool its description and name, and give a form control its parameter description. *Chapter 8.*

**tool-level error.** A failure the tool reports as a value rather than an exception: `{ status: 'error', code, message }`, with a stable code and a sentence that tells the model how to fix the call. The draft allows this explicitly; the browser passes the result through as JSON. It is distinct from a platform error, a `DOMException` such as `NotFoundError` that the browser raises and the caller sees only by name. *Chapter 6; wording in Chapter 11.*

**tools (Permissions Policy feature).** See *Permissions Policy*. *Chapter 7.*

**TPAC.** The W3C’s annual meeting week, where groups meet in person. TPAC 2026 runs from 26 to 30 October in Dublin, and WebKit’s proposed path for agent work includes a workshop around it. *Chapter 13; Chapter 15.*

**trusted click.** A click that came from the person, shown by `event.isTrusted`. It proves that someone clicked, not that they read or understood what they agreed to. *Chapter 13.*

### U

**UnknownError.** The `DOMException` Chromium 156 returns for most tool-execution failures: a thrown error, a missing tool, a page that went away mid-call. The draft used it too until 8 October 2026, when it was replaced with specific error names (commit b206dae, pull request #339), so Chromium’s `UnknownError` is spec lag, not a bug. *Chapter 5; Chapter 6; Chapter 7; Appendix A.*

**`untrustedContentHint`.** An annotation that says the tool’s output “contains data that is untrusted, from the perspective of the author registering the tool”,[^6] such as reviews or community answers. *Chapter 6; Chapter 12.*

**`usewebmcp`.** A React hook package from MCP-B (6.0.3 on 15 October 2026) that registers tools with `document.modelContext` inside components.[^20] Trailhead’s React app uses it. *Chapter 10.*

**user activation.** The browser’s record that a person recently interacted with the page, which gates APIs such as pop-ups and full-screen. A tool call is not a user gesture and doesn’t grant it. *Chapter 13.*

### W

**W3C (World Wide Web Consortium).** The standards body that hosts the Web Machine Learning Community Group and its WebMCP draft, and that would charter any Working Group to standardise it. *Chapter 4; Chapter 15.*

**W3C Council.** The body that decides a formal objection the W3C Team can’t resolve. *Chapter 15.*

**web-platform-tests (WPT).** The shared, cross-browser test suite for web standards. The draft links to its WebMCP tests, which in places follow Chromium where the draft says something else (issue #332). *Chapter 6; Chapter 14.*

**Web Machine Learning Community Group (WebML CG).** The W3C Community Group that publishes the WebMCP draft. Its stated mission is about machine-learning inference in the browser, which is one reason WebKit called it the wrong venue.[^28] *Chapter 4; Chapter 15.*

**Web Machine Learning Working Group (WebML WG).** The W3C Working Group, chartered until 30 April 2027, that a June 2026 pull request proposed should take on WebMCP. That proposal was closed unmerged on 13 October 2026. *Chapter 15.*

**WebMCP.** A proposed web API that lets a page register JavaScript tools with `document.modelContext.registerTool()`, so agents can call them instead of operating the interface. It is a Draft Community Group Report (15 October 2026), not a W3C Standard.[^1] *Chapter 4.*

**WebMCP domain (CDP).** The part of the Chrome DevTools Protocol that lets automation see and call a page’s tools. It has commands such as `WebMCP.enable` and `WebMCP.invokeTool`, and events such as `WebMCP.toolsAdded`.[^29] *Chapter 14.*

**`WebMCPTesting`.** The Chromium feature that turns on WebMCP locally, as `--enable-features=WebMCPTesting` on the command line or `chrome://flags/#enable-webmcp-testing` in Chrome.[^30] Every “observed” behaviour in this book was measured with it in Chromium 156. *Chapter 6; setup in Chapter 9.*

**`webmcp-types`.** A community package of TypeScript type definitions for WebMCP (0.1.10 on 15 October 2026).[^20] *Chapter 5; Chapter 10.*

**Working Group (WG).** A chartered W3C group. Working Groups “typically produce deliverables (e.g., Recommendation Track technical reports, software, test suites, and reviews of the deliverables of other groups)”.[^12] Moving WebMCP from a Community Group into a Working Group would put it on the standards track. *Chapter 4; Chapter 15.*

## B.2 The running examples

**Fjord Table.** A small restaurant on the Oslo waterfront and its booking site, built in plain HTML, CSS and JavaScript modules. Its tools are `search_availability` (date, party size 1 to 12, optional time and seating) and the consequential `book_table`. *Introduced in Chapter 1; built in Chapters 4 and 5; declarative version in Chapter 8; end to end in Chapter 9; under test in Chapter 14.*

**Helpdesk Widget.** A support widget made by the vendor Supportly and embedded in the Ledgerly dashboard. Its tools are `search_articles` (read-only), `create_ticket` (consequential) and `get_ticket_status`, with ticket IDs shaped like `SUP-1042`. It is the book’s case study for Permissions Policy, `exposedTo` and `fromOrigins`, in-page agents and cross-origin threats. *Introduced in Chapter 1; Chapter 7; redesigned in Chapter 11; threat model in Chapter 12.*

**Kari.** Trailhead’s head of product, whose whiteboard questions frame the business chapter and the closing chapter. *Chapter 16; Chapter 17.*

**Lars.** The Trailhead customer in Chapter 1 who asks his browser’s assistant to find him a tent for a trip to Jotunheimen. *Chapter 1.*

**Ledgerly.** The fictional SaaS dashboard (`https://app.ledgerly.example`) that embeds the Helpdesk Widget: the host page, the embedder that sets the Permissions Policy. *Chapter 7.*

**Supportly.** The fictional third-party vendor (`https://widget.supportly.example`) whose iframe provides the Helpdesk Widget’s tools. *Chapter 7.*

**Test Agent.** See the entry in B.1. *Chapter 1; Chapter 9; Chapter 14.*

**Trailhead.** A fictional Norwegian outdoor-gear store built with React 19, Vite and TypeScript, with prices in NOK. Its WebMCP tools are `search_products`, `compare_products`, `add_to_cart`, `get_cart` and a consequential `checkout` that never completes without the person’s click. A companion backend MCP server offers `search_products` and `get_order_status`. *Introduced in Chapter 1; backend server in Chapter 3; annotations and errors in Chapter 6; React and Angular in Chapter 10; tool design in Chapter 11; threat model and consent in Chapters 12 and 13; evals in Chapter 14; business plan in Chapter 16; Chapter 17.*

## Notes

[^1]: WebMCP specification, Draft Community Group Report, 15 October 2026, §2 Terminology (definitions of *agent* and *browser agent*) and the document’s status section. Read 15 October 2026. <https://webmachinelearning.github.io/webmcp/>
[^2]: MDN Web Docs, “AbortSignal”: “The AbortSignal interface represents a signal object that allows you to communicate with an asynchronous operation (such as a fetch request) and abort it if required via an AbortController object.” Read 15 October 2026. <https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal>
[^3]: Chrome for Developers, “WebMCP” (published 18 May 2026, last updated 7 October 2026), Key Term: Actuation. Read 15 October 2026. <https://developer.chrome.com/docs/ai/webmcp>
[^4]: W3C, “DRAFT Agentic Web Working Group Charter”, mission statement and deliverables. Read 15 October 2026. <https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html>
[^5]: W3C, announcement of charter refinement for the proposed Agentic Web Working Group, public-new-work mailing list, October 2026. Read 15 October 2026. <https://lists.w3.org/Archives/Public/public-new-work/2026Oct/0002.html>
[^6]: WebMCP specification, §4.2.1 ToolAnnotations Dictionary. Read 15 October 2026. <https://webmachinelearning.github.io/webmcp/#dictdef-toolannotations>
[^7]: Chrome for Developers, “WebMCP tool security” (published 9 June 2026, last updated 1 September 2026): recommended limits of 500 characters per tool description and 150 characters per parameter description. Read 15 October 2026. <https://developer.chrome.com/docs/ai/webmcp/secure-tools>
[^8]: Chrome Platform Status, “WebMCP” (feature 5117755740913664), last updated 28 September 2026: status “Proposed”, developer trial from Chrome 146, origin trial stage from Chrome 149 to 156 with an extension through 162. Read 15 October 2026 through the page and its JSON API. <https://chromestatus.com/feature/5117755740913664>
[^9]: Model Context Protocol specification, version 2026-07-28, “Architecture”: hosts, clients (“Each client is created by the host and communicates with exactly one server”) and servers. Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28/architecture>
[^10]: W3C, “Community and Business Groups: Frequently Asked Questions”: “A W3C Community Group is an open forum, without fees… Community Groups do not create W3C standards.” Read 15 October 2026. <https://www.w3.org/community/about/faq/>
[^11]: Model Context Protocol specification, version 2026-07-28, “Elicitation”: “a standardized way for servers to request additional information from users through the client during interactions.” Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation>
[^12]: W3C Process Document, 18 August 2025: the Technical Architecture Group, Working Groups and Interest Groups, and Formal Objections and the W3C Council. Read 15 October 2026. <https://www.w3.org/policies/process/>
[^13]: JSON-RPC 2.0 Specification. Read 15 October 2026. <https://www.jsonrpc.org/specification>
[^14]: JSON Schema, “Specification”: “The current version is 2020-12!” Read 15 October 2026. <https://json-schema.org/specification>
[^15]: Model Context Protocol specification, version 2026-07-28, “Key Changes” (changelog): “Make MCP stateless: remove the initialize / notifications/initialized handshake. Every request now carries its protocol version and client c[apabilities]…”. Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
[^16]: Model Context Protocol specification, version 2026-07-28, “Tools”: “clients MUST consider tool annotations to be untrusted unless they come from trusted servers.” Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>
[^17]: Chrome for Developers, “Get started with origin trials”. Read 15 October 2026. <https://developer.chrome.com/docs/web-platform/origin-trials>
[^18]: Microsoft Edge Origin Trials, “WebMCP”: Trial Expiration Date March 30, 2027. Read 15 October 2026. <https://developer.microsoft.com/en-us/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a>
[^19]: MDN Web Docs, “Permissions-Policy header”. Read 15 October 2026. <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy>
[^20]: npm registry metadata for `@mcp-b/global` (6.0.3), `@mcp-b/webmcp-polyfill` (6.0.3), `usewebmcp` (6.0.3) and `webmcp-types` (0.1.10), read 15 October 2026. <https://registry.npmjs.org/usewebmcp/latest>
[^21]: Chrome for Developers, “The Prompt API” (published 20 May 2025): “With the Prompt API, you can send natural language requests to the foundation model in Chrome.” Read 15 October 2026. <https://developer.chrome.com/docs/ai/prompt-api>
[^22]: MDN Web Docs, “Secure contexts”: “A secure context is an environment such as a Window or Worker which meets a defined standard of authentication and confidentiality.” Read 15 October 2026. <https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts>
[^23]: mozilla/standards-positions issue #1412, “WebMCP”, labelled “position: neutral”. Read 15 October 2026. <https://github.com/mozilla/standards-positions/issues/1412>
[^24]: WebKit/standards-positions issue #670, “WebMCP”, labelled “position: oppose”. Read 15 October 2026. <https://github.com/WebKit/standards-positions/issues/670>
[^25]: Model Context Protocol specification, version 2026-07-28, overview, “Key Details”. Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28>
[^26]: Model Context Protocol specification, version 2026-07-28, “Transports”. Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports>
[^27]: w3ctag/design-reviews issue #1238, “Incubation: WebMCP”, open, labelled “Missing: Multi-stakeholder support”. Read 15 October 2026. <https://github.com/w3ctag/design-reviews/issues/1238>
[^28]: W3C, “Web Machine Learning Community Group” home page: its mission statement. Read 15 October 2026. <https://www.w3.org/community/webmachinelearning/>
[^29]: Chrome DevTools Protocol, tip-of-tree, “WebMCP” domain: `WebMCP.enable`, `WebMCP.invokeTool`, `WebMCP.cancelInvocation`, `WebMCP.toolsAdded` and related types. Read 15 October 2026. <https://chromedevtools.github.io/devtools-protocol/tot/WebMCP/>
[^30]: Chrome for Developers, “WebMCP”, section on local testing with `chrome://flags/#enable-webmcp-testing`. Read 15 October 2026. <https://developer.chrome.com/docs/ai/webmcp>
[^31]: Model Context Protocol specification, version 2026-07-28, Schema Reference, `ToolAnnotations`: `title`, `readOnlyHint` (default false), `destructiveHint` (default true), `idempotentHint` (default false) and `openWorldHint` (default true), the second and third “meaningful only when `readOnlyHint == false`”. Read 15 October 2026. <https://modelcontextprotocol.io/specification/2026-07-28/schema#toolannotations>
