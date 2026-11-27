# Chapter 17: The Road Ahead

> *“As the WebMCP proposal continues to evolve with community and stakeholder feedback, we are tracking several active design discussions and technical challenges.”*
>
> — WebMCP explainer, “Open Questions”[^ch17-1]


## The question after the first release

Three weeks after the Monday meeting in Chapter 16, Trailhead’s first release is live behind the origin trial. Agents can search and compare tents, the measurement wrapper is counting outcomes, and the front-end lead has stopped getting paged about the adapter. The product lead’s new question is: *What are we betting on, and what happens if we lose the bet?*

Everything in the previous sixteen chapters was checked against the specification on a particular day and against what one browser actually did. Both will move. The Community Group draft I read for most of this chapter is dated 27 October 2026.[^ch17-2] I checked the paragraphs on the `Tool` interface against the draft dated 23 November 2026. Chrome’s origin trial runs to Chrome 162, and Chrome Platform Status still lists the feature as “Proposed”, with no shipping milestone.[^ch17-3] Edge’s trial expires on 30 March 2027.[^ch17-4] Several of the questions that will decide what WebMCP becomes are being argued in threads that got new comments in the last week of October, during and right after TPAC, the W3C’s annual meeting week (26 to 30 October).

So this chapter is a map of those questions, plus a way to build so that your work survives the answers. It groups the questions into five (Figure 17.1): what a tool can declare, what happens during a single call, what happens when the work outlives the document, who gets to see a tool, and what the platform as a whole becomes. For each one, this chapter gives the state of play as of 2 November 2026 and a practical response now. Then come three competing futures, a checklist, and three short listings that Trailhead uses to keep its bets small.

![Figure 17.1 — The open questions, by layer, with their status as of 2 November 2026](images/figure-17-1.png)

Figure 17.1 is that 2 November map. Table 17.1 adds one later row, for `waitForToolsUntil()`, from the 24 November draft. The figure was not redrawn.


## How to read an open question

First, a word on how to weigh these questions. The WebMCP repository contains many kinds of “open”, and they don’t carry the same weight.

An *explainer section* is the lightest. The main explainer’s “Open Questions” list is a statement of intent from its authors: things they believe the API needs and haven’t designed yet.[^ch17-1] A *supplementary explainer*, such as the one for service workers or the one for continuations, is a worked proposal with an API sketch but no spec text.[^ch17-5][^ch17-6] An *issue* can be anything from a drive-by idea to a design thread with a formal *resolution* recorded in the Community Group’s minutes. A *pull request* against the spec is the closest thing to a decision before it lands. And an *implementation experiment* in Chromium is a strong signal of which way the browser running the trial is leaning.

One event from October shows why the distinction matters. On 8 October 2026 the Community Group merged pull request #338. It removed the declarative API from the specification and left it to be “explored in the Declarative API Explainer”. Five days later, in the same thread, François Beaufort from the Chrome team wrote that “the Chrome team plans to ship the imperative API **first**, with the declarative API following shortly after.”[^ch17-7] So something that had been spec text for months became an explainer again, while the browser running the trial kept shipping it. Chapter 8 covers what that means for forms. Here it’s a reminder that the spec, the explainers and Chromium are three separate sources of truth. You have to track all three.

Table 17.1 summarises the questions this chapter covers.

**Table 17.1 — Open questions that could change your tools.** The rows below were read on 2 November 2026, except the readiness row, which follows the 24 November draft.

| Question | Where it lives | Status | What to do now |
|---|---|---|---|
| Output schemas | Issues #9 and #92; PR #254 | PR #254 merged 2 Nov; `outputSchema` is optional; native validation behavior remains unresolved | Declare a useful schema and validate results in the agent harness |
| Multimodal inputs and outputs | Issues #41, #81 | Open | Return references and compact JSON, not blobs |
| Streaming arguments and progress | Issue #82, explainer | Open | Keep calls short, show progress on the page |
| Cross-document responses | Issue #135, continuations explainer | Group exploring continuation tokens | Finish tool calls in one document, keep state server-side |
| Service-worker tools | Service-workers explainer | Explainer only | Keep tools as thin wrappers over domain code |
| Built-in agent exposure | Explainer (`native-agent`) | Under consideration | Set `exposedTo` deliberately |
| Host-controlled iframe topologies | Issue #317 | Open, two-sided opt-in now in the spec (PR #326) | Use Permissions Policy and explicit origins |
| Result after a caller aborts | Issue #299 | Closed: standard `AbortSignal` semantics | Report partial work through your own UI or state |
| Cancel racing with a start | Issue #344 | Closed: no stronger guarantee | Make consequential tools idempotent |
| Event ordering | Issue #332 | Open: spec and Chromium disagree | Don’t depend on `toolactivated` timing |
| Sensitive reads | Issue #331 | Open | Treat sensitive reads like consequential ones |
| Asking the user mid-call | Issue #165, PR #204 | Open, a new proposal on 26 Oct | Keep confirmation on your own page |
| A generic call API | Issue #236, PR #375 | Open explainer, not merged (Appendix F). Still open on 27 November 2026. PR #348, the `Tool` interface, merged 19 Nov and is a different change (Appendix E) | Keep calls on `document.modelContext` |
| When a document’s tools are ready | Issue #328, PR #373 | `waitForToolsUntil()` merged 24 Nov. `tools ready` still starts `true`. #328 was still open on 27 Nov. `getTools()` does not wait | Call it around async registration, with `?.`, and keep retries inside the promise (Chapter 5) |


## Output schemas

Every Trailhead tool already returns structured data. `search_products` answers with an object that has a `products` array, each item with a SKU, a name, a price in NOK, a rating and a stock flag. What the agent doesn’t get is a description of that shape. It has to work out what `inStock: false` means from the value itself, and it can’t tell in advance whether the tool returns prices at all.

The request for an output schema is one of the oldest in the repository. Issue #9 was opened in August 2025, right after MCP added `outputSchema` to its tool definition. On 5 February 2026 the Community Group resolved to “add outputSchema to the imperative API and investigate how to associate outputSchema with declarative WebMCP.”[^ch17-8] Pull request #254 added the optional `outputSchema` member to both `ModelContextTool` and `RegisteredTool` (now `Tool`) and merged on 2 November 2026. The page declares a JSON Schema for the result, and an in-page agent can read it back from `getTools()`. The name was chosen over `responseConstraint`, which is specific to the Prompt API, to align with MCP.[^ch17-9] The task-supplied Chrome build `159.0.8140.0` supports the member; the companion repo’s browser tests still use Chromium 156 and do not verify Chrome 159.

Issue #92 remains open on whether schemas should be required and who validates them. Its latest discussion still contains competing views: some participants favor optional schemas because tools may return plain text, while others want explicit contracts as a security signal. November comments distinguish invalid tool output from invalid model input and argue that an agent should not pass mismatched output to a model. Those comments are proposals, not normative spec text.[^ch17-12]

On the MCP side, the 2026-07-28 tools specification already defines `outputSchema` as an optional JSON Schema for the result, and `structuredContent` as the field that carries the conforming value. For backwards compatibility, a tool that returns structured content “SHOULD also return the serialized JSON in a TextContent block.”[^ch17-10]

So what does Chromium 156 do today if you include `outputSchema`? I tried it. Registration succeeds, the member is silently dropped, and `getTools()` returns a tool without it.[^ch17-11] That’s ordinary Web IDL dictionary behaviour: members the browser doesn’t know are ignored. It also means writing the schema now costs you nothing. Listing 17.1 is Trailhead’s search tool as plain data, with an output schema next to the input schema.

**Listing 17.1** `chapters/17-the-road-ahead/src/catalog.js` — `search_products` as plain data with an optional output schema

```js
// catalog.js: Trailhead's search tool as plain data plus a plain function.
// Nothing here touches document.modelContext; adapter.js does (Listing 17.2).
import { searchProducts } from './products.js';

const price = {
  type: 'object',
  properties: {
    amount: { type: 'number', description: 'Price in Norwegian kroner' },
    currency: { type: 'string', enum: ['NOK'] },
  },
  required: ['amount', 'currency'],
};

export const catalog = [
  {
    name: 'search_products',
    title: 'Search products',
    description:
      'Search Trailhead outdoor gear by keyword, with optional category, ' +
      'maximum price in NOK and an in-stock filter. Shows the results on ' +
      'the page and returns up to 10 products with SKU, name, price and rating.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Keywords, e.g. "2 person tent"' },
        category: {
          type: 'string',
          enum: ['tents', 'sleeping-bags', 'backpacks', 'footwear', 'clothing'],
        },
        maxPrice: { type: 'number', minimum: 0, description: 'Maximum price in NOK' },
        inStockOnly: { type: 'boolean' },
      },
      required: ['query'],
    },
    // Optional JSON Schema return contract; agents should validate results before passing them to a model.
    outputSchema: {
      type: 'object',
      properties: {
        products: {
          type: 'array',
          maxItems: 10,
          items: {
            type: 'object',
            properties: {
              sku: { type: 'string' },
              name: { type: 'string' },
              price,
              rating: { type: 'number', minimum: 0, maximum: 5 },
              inStock: { type: 'boolean' },
            },
            required: ['sku', 'name', 'price', 'inStock'],
          },
        },
      },
      required: ['products'],
    },
    annotations: { readOnlyHint: true },
    run: (input) => ({ products: searchProducts(input) }),
  },
];
```

Three choices in Listing 17.1 are deliberate. First, the definition never touches `document.modelContext`. It’s data plus a `run()` function, and Listing 17.2 turns it into a WebMCP tool. Second, an output schema is worth testing, not only writing, so a result that gains a field does not silently leave the schema behind.[^ch17-11] The schema printed in this listing requires `products`. Listing 17.2 can also return `{ status: 'error', code: 'INVALID_ARGUMENT', message }` and passes that schema through, so the error would not validate against the listing as printed. Third, `currency` is an `enum` of one value. That looks pedantic. It is also exactly the kind of fact an agent comparing stores needs and won’t guess.

> **Still in flux:** output validation
>
> PR #254 merged on 2 November 2026 and `outputSchema` is now part of the spec. The member is optional. The spec says a result is expected to conform, but does not yet say that native `executeTool()` must reject an output mismatch. Issue #92 remains open. Until it is resolved, validate results in the agent harness before model delivery, and return a safe validation error instead of malformed data. Keep the invalid payload out of the error itself.[^ch17-12][^ch17-output-schema]


## Multimodal and streaming data

Trailhead’s tools return text and numbers. A store that lets customers upload a photo of a broken tent pole, or a design tool that returns an image, needs more. The explainer lists “multimodal input/output” as an open question and notes that agents “are increasingly multimodal”.[^ch17-1] Issue #41, opened in October 2025, asks for image inputs and outputs and suggests “something web specific, allowing devs to use image elements for this”.[^ch17-13] Issue #81 proposes file attachments for the imperative API.[^ch17-14]

The more telling decision is a closure. Issue #86 asked WebMCP to adopt MCP’s content types for results (text, image, resource). On 28 September 2026 Dominic Farolino, who has driven most of the specification’s recent evolution, closed it in favour of #41. He wrote that he was “less convinced we should adopt MCP’s content model directly, or standardize presentation-specific types like `html`, `table`, or `link` as part of WebMCP.”[^ch17-15] My expectation is a web-shaped answer, perhaps built on `Blob` or elements, rather than base64 strings copied from MCP. Size is the practical problem nobody has solved yet. In October an agent-host developer pointed out on #41 that a screenshot is “easily several megabytes once it’s base64 in a JSON string”, and asked the spec to let hosts cap results and to describe returning a reference instead.[^ch17-13]

Streaming has the same status. Issue #82, opened in February 2026, asks for tool arguments to stream into the page while the model is still generating them, so a long email body could appear as it’s written.[^ch17-14] The explainer adds streaming outputs and progress reporting for long-running tools to the list, and points at MCP’s own progress utility as prior art.[^ch17-1] None of this is in the draft.

What to do now is mostly restraint. Return compact JSON with identifiers and URLs the agent can pass back to another tool, not large payloads. Keep the page as the place where images, previews and progress bars are shown. That’s good practice anyway (Chapter 16 argued that showing results on the page keeps the agent a guest), and it means that when a multimodal result type arrives, it’ll be an addition to tools that already work.


## When the work outlives the document

WebMCP tools live in a document. When the document goes, the tool and any call in progress go with it. Two open questions are about relaxing that: responses that survive a navigation, and tools that don’t need a document at all.

### Cross-document responses and continuation tokens

Most stores spread checkout over several pages. Trailhead’s goes from cart to delivery to payment to confirmation, with a full navigation at each step. An agent that calls `checkout` on the cart page gets nothing back once the page navigates away. The promise belongs to a document that no longer exists.

Issue #135, opened in March 2026, asked how a tool should respond when it causes a navigation. It started with declarative forms and the idea of using the target page’s JSON-LD as the response. On 16 April 2026 the group resolved to “explore `<context>` element without committing to form submission response with it.”[^ch17-16] The design that has gained ground since is a different one. In late September Mark Foltz from the Chrome team published an explainer for *continuation tokens*, merged into the repository on 2 October as pull request #327.[^ch17-6] On 1 October the group resolved that it “explores the Continuation Tokens design outlined in the explainer and welcomes further feedback.”[^ch17-16]

The explainer names the limitation up front: “tool calls are restricted to execute in a single document, and a single Promise per tool call.” Its proposal has two halves. A tool’s `execute` callback receives an `invocation` object and can call `requestToken()` to get a string token for the current call. The site carries that token to the next page, in a URL parameter or in storage, and calls `document.modelContext.resumeTool(token, callback)` there. The browser invokes the callback with the original input and returns the final result to the agent only when the whole chain has finished.[^ch17-6] The conditions are strict. A token can be redeemed once, only by a same-origin document in the same browsing context, and it’s revoked if the caller cancels. The browser may also limit its lifetime, which the explainer expects to “probably fall around 60 seconds”.[^ch17-6]

A Microsoft engineer described a different prototype in the same issue. There, a tool returns a sentinel value such as `continueAfterNavigation: true`, and the browser invokes the same tool again on the next page. The explainer’s author replied that his proposal differs in two ways: the site asks for a continuation through an explicit API, and the next page doesn’t have to register the tool again to handle it.[^ch17-16]

My probe (Listing 17.3) found neither `invocation` nor `resumeTool()` in Chromium 156. The only option `execute` receives is `signal`.[^ch17-11] So for now, design each tool call to finish in one document. Trailhead’s `checkout` stops at the order summary, as Chapter 16 planned, and returns the summary. Keep any state that has to survive a navigation on the server, keyed by an identifier you return to the agent. That design is ready for continuation tokens if they arrive, because the token simply becomes one more thing the next page reads.

MCP went the same way in its 2026-07-28 revision. It removed protocol-level sessions and the `Mcp-Session-Id` header, and said that servers needing state across calls should use “explicit, server-minted handles passed as ordinary tool arguments.”[^ch17-17] Both protocols are converging on one idea: state that crosses a boundary should be explicit.

### Tools for sites that aren’t open

The second question is bigger. Today an agent can only use Trailhead’s tools while a Trailhead tab is open. Chrome’s overview lists this under “Tool discoverability”: clients and browsers “must visit a site directly to know if it has callable tools.”[^ch17-18] The service-worker explainer, first published on 28 August 2025, proposes that a site’s service worker registers tools with a `modelContext` object in its global scope, “the service worker counterpart of the `document.modelContext` object”, so that an agent can call them with no window open.[^ch17-5]

The explainer goes further than registration. It proposes just-in-time installation of a site’s service worker when an agent recommends it, building on the `serviceworker` manifest field from the Payment Handler API. It proposes a session identifier on each call, so that a worker serving two conversations can keep two carts apart. And on security it suggests limiting an agent conversation to a single origin once it touches a worker’s tools, to blunt the combination of private data, untrusted content and external communication.[^ch17-5] Tools that need the user, for payment or confirmation, would open a window and talk to it with `postMessage`.[^ch17-5]

This is an explainer with no spec text, and the main explainer still lists it as an open question.[^ch17-1] But it’s a strong argument for keeping tools thin anyway. If `search_products` wraps a search function that doesn’t depend on the DOM, the same function can be registered from a worker later. If the tool reads its results from the rendered grid, it can’t.


## Who sees your tools by default

Chapter 7 covered `exposedTo`, `fromOrigins` and the `tools` Permissions Policy. Three open questions could still change the defaults.

The first is the browser’s own agent. The `exposedTo` array accepts only origins, so a page can’t say whether the browser’s built-in assistant should see a tool. The explainer says its authors are “considering introducing a new keyword like `native-agent`”. The idea on the table is that a missing `exposedTo` in the top-level document would expose tools to the built-in agent, while in iframes it would not.[^ch17-1] If that lands, the default for most pages stays the same, and embedded widgets such as Supportly’s Helpdesk Widget become invisible to the browser’s agent unless they opt in.

The second comes from composed applications. Issue #317, opened on 23 September 2026, describes a host page with an agent in one iframe and several cross-origin apps in others. The host wants the agent to use the apps’ tools without the apps seeing each other’s. Today every app must know the agent’s origin in advance through `exposedTo`, and the agent must name every app in `fromOrigins`. The issue proposes host-controlled roles. Farolino’s first reply named the crux: what the host really wants is for a tool provider “to not have to know which origins to expose tools to explicitly.” On 26 October Khushal Sagar from Chrome agreed, and added that the ban on `*` in `exposedTo` “seems against the spirit of open web”.[^ch17-19]

The third was documentation, and it’s now settled on paper. Until late October, the draft’s §6.3.4 was an empty placeholder. Pull request #326 merged on 27 October and filled it. The section is now called “Interaction with the Same-Origin Policy”, and it describes what it calls the two-sided opt-in: by default a tool is “only visible to and executable by” same-origin documents, and a cross-origin document gets access only when three gates are satisfied. Those gates are Permissions Policy delegation by the embedder, `exposedTo` by the provider and `fromOrigins` by the consumer.[^ch17-20] That’s the model Chapter 7 taught, now in the spec’s own words. It’s also the model that #317 and the discussion in issue #236 (more on that below) might still loosen.

What to do now: never rely on defaults for exposure. If a tool should be visible to a specific embedding origin, say so in `exposedTo`. If it shouldn’t leave the top-level document, don’t delegate the `tools` policy to frames. Listing 17.2 passes `exposedTo` through only when the caller asks for it, which keeps that decision in one visible place.


## Smaller questions that still bite

Not every open question is a new feature. Some are about the semantics of what already ships, and those are the ones most likely to change behaviour under your existing code.

*What a cancelled call returns.* Issue #299 asked whether a tool could still deliver a final result after the caller aborted, such as how many items of a batch it had applied. Farolino closed it on 25 September 2026. Once the caller aborts, he wrote, “its promise rejects and any eventual result from the tool is discarded.” That’s how `AbortSignal` already works elsewhere on the platform, for example with `fetch()`. If an application needs to expose the resulting state, that’s the application’s job.[^ch17-21] So a tool that applies changes step by step should record its progress somewhere the user and the agent can see it afterwards, on the page or on the server.

*A cancel that races with a start.* Issue #344 was opened and closed on 14 October 2026. It showed that a call cancelled almost immediately can still start, with a fresh signal that isn’t aborted. Farolino declined to give a stronger guarantee than `AbortSignal` gives elsewhere: “once execution has begun, aborting can race with work that the tool has already performed,” and there can’t be a guarantee “that no side effect occurred”. Anything stronger would need a separate commit or transaction mechanism. He did agree that the ordering of parallel steps in the spec had a real bug, and said he would file it separately. Beaufort came back the next day to say the behaviour was “_still_ confusing” for web developers.[^ch17-22] The practical lesson is the same either way: make consequential tools idempotent, and check the signal before each irreversible step, not only at the start.

*When `toolactivated` fires.* Issue #332, opened on 1 October 2026, notes that the draft fires `toolactivated` before invoking `execute`, while Chromium and the web-platform tests fire it after, so that listeners see the tool’s effects.[^ch17-23] Beaufort ran into the same mismatch in mid-October while adding the events to the WebMCP polyfill, and on 28 October asked Mark Foltz for his view. Either side may change. Don’t write code that depends on the order of the event and the callback.

*Sensitive reads.* `consequentialHint` describes actions that are “significant, real-world, or non-reversible”. Issue #331 points out that this leaves high-risk *read* tools ambiguous, such as tools that return health or financial records. Participants have proposed a separate `sensitiveHint` that would let an agent say “will read private data” instead of “will do something consequential”, and keep such outputs out of logs and long-term memory.[^ch17-24] Until something is decided, treat a sensitive read like a consequential action and ask for confirmation on the page. Don’t invent your own annotation names either. Chromium 156 drops unknown annotations silently. My probe registered a tool with `sensitiveHint` and got back only the four annotations the browser knows (`consequentialHint`, `debugging`, `readOnlyHint` and `untrustedContentHint`).[^ch17-11]

*Asking the user mid-call.* Elicitation is still unresolved. In June 2026 the group agreed to specify an “interactive” mode first, in pull request #204, which proposes replacing `requestUserInteraction()` with `requestUserInput()`. That PR changed hands on 29 October, when Samuel Dallstream picked it up. Three days earlier, Ilya Grigorik had proposed on issue #165 to fold the modes into one call with an optional URL and to add an outcome for the case where no person can be reached at all.[^ch17-25] Meanwhile Chrome’s security guide still says that “the spec draft includes requestUserInteraction()”.[^ch17-26] The 27 October draft doesn’t contain that method.[^ch17-2] Chapter 13 shows how to confirm on your own page, which works whatever the API becomes.

*Grouping tools.* Proposals for “skills” (#161) and tool collections with progressive disclosure (#255) would change how many tools a page can sensibly expose. On 3 September 2026 the group resolved to “seek explicit model harness creator feedback and defer the tool collections feature.” The first harness feedback arrived on #255 on 20 October.[^ch17-27] Keep your tool count small, as Chapter 16 recommended, and nothing here will catch you out.

> **Still in flux:** semantics under your feet
>
> The closures of #299 and #344 make WebMCP’s cancellation behave like the rest of the platform, which is good news for stability. The ordering bug Farolino said he would file, the `toolactivated` question in #332 and the hint proposals in #331 could still change observable behaviour. Pin these down in tests against each Chrome release (Chapter 14), and keep the expectations in one place, so that a change shows up as a failing test and not as a support ticket.


## Competing futures

Step back from individual issues and you can see three broad directions WebMCP could take. They aren’t mutually exclusive, but they lead to different APIs, and the people arguing for them aren’t the same people.

### WebMCP as drafted, Chromium first

The first is the path the specification is on: an imperative API on `document.modelContext`, extended with output schemas, continuations and exposure controls, shipped first in Chromium. Its supporters are the people writing the specification and the Chromium teams. Chrome Platform Status lists seven owners, an origin trial from M149 to M156 and an extension to M162 recorded on 28 September 2026.[^ch17-3] Chrome has said it plans to ship the imperative API first.[^ch17-7] Outside the browser teams, the strongest signal so far came on 26 October, when Ilya Grigorik wrote in the W3C charter discussion that “Shopify deploys WebMCP across millions of storefronts”.[^ch17-35] In this future the code in this book needs small updates, not a rewrite.

### Richer HTML and ARIA semantics

The second is the direction WebKit prefers. Its standards position is “oppose”. Its argument, covered in Chapter 4, is that “when a site’s actions are hard for an agent to use, that is a gap in the page’s own semantics,” and that the fix belongs in HTML and ARIA, “where the user, assistive technology, and agents all benefit.” WebKit also argues that a parallel tool layer moves the brittleness instead of removing it, “from the DOM into the tool descriptions”, and that an agent acting for a user “is, in effect, assistive technology.”[^ch17-28] In this future, the tool catalog turns into labels, form semantics and accessible names. The declarative API, now an explainer again, is the closest thing WebMCP has to a bridge.[^ch17-29]

This future gained a weighty voice in October. The TAG’s early comment on its review, posted on 26 October, worries about “an agent-only description of a page’s functionality that might be unreachable by human users or screen readers”, a “web for agents” that “removes the incentive for authors to provide a semantically rich, accessible website.” It asks the group to “fully work out the declarative version before shipping the imperative one”.[^ch17-32]

### A generic cross-environment call API

The third came from Jake Archibald in issue #236, opened on 3 August 2026: reposition WebMCP “as a general way to call functions in other environments.” Function calls between windows and workers are painful enough that libraries exist to make them easier. If registering a tool were simply a way for one environment to expose a function to another, with schemas and descriptions, then exposing functions to “the browser” would make them available to WebDriver and to agents, and “the LLM capability just falls out of the other capabilities provided.” A service worker could register functions at install time. A tool could ask not to return until the next page was ready, which would make multi-page automation possible.[^ch17-30]

The thread that followed is one of the most substantive in the repository. Farolino discussed tool objects that act as handles to a tool’s unique identifier, which could be passed across `postMessage()` to environments that have no direct access to each other. Archibald replied that this made `tool.call(…)` a more natural shape than a separate `callTool()`.[^ch17-30] Part of that idea is now two different artifacts. Pull request #348, which replaces the `RegisteredTool` dictionary with a `Tool` interface keyed by a unique identifier, merged on 19 November 2026. It fixes the unregister-and-reregister race. It does not move registration off `document.modelContext` (Appendix E).[^ch17-39] The generic-calling explainer is pull request #375, open on 23 November 2026, and it is not the API this chapter tells you to write (Appendix F). After the face-to-face meeting at TPAC, Benjamin VanderSloot from Mozilla noted that generic tools would need a different meaning for the permissions policy, and Johann Hofmann argued for a second policy, so that a site could use an embed’s tools without letting that embed expose tools to a browser’s agent. Archibald called the needed change “just a naming change”.[^ch17-36] Mozilla’s position thread, which settled on “neutral”, points to #236, and Archibald is one of the Mozillians it names as able to provide input.[^ch17-31] Several of the questions above, such as service-worker tools, continuations and the handle-based `executeTool()`, already move a little in this direction.

### Who decides

None of these futures has the support a web standard needs yet. The W3C TAG’s review of WebMCP is still open, with the label “Missing: Multi-stakeholder support”. Its 26 October comment opens with “This is not a resolution comment”, announces a TAG Finding “specifically related to Agentic Browsing”, notes that this would be the “first time that JSON Schema is used by a web platform API”, and even asks whether there is time “to rename the proposal to something like ‘Tools’”.[^ch17-32] Mozilla is neutral, WebKit is opposed, and the Chromium-based browsers are running trials. Chapter 15 covers the politics in detail. For your planning, the point is that each of the three futures keeps some of your work and changes some of it (Figure 17.2).

The venue is moving too. In June 2026 the W3C staff proposed adding WebMCP to the scope of the Web Machine Learning *Working Group* charter, the step that would move it from incubation onto the standards track. In August an Apple representative recorded that Apple was “opposed to this going working group” and that the W3C should “expect a formal objection if this is merged,” while saying Apple would be open to “a different venue at the W3C and doing this properly from first principles.” The pull request was closed without being merged on 13 October 2026.[^ch17-33] Its replacement is a draft charter for a new Agentic Web Working Group, which the spec itself now points to. Since 20 October its section on agent capabilities says that preventing an agent from being manipulated “is primarily the responsibility of the agent’s own security model rather than something this specification can normatively enforce”.[^ch17-40] The charter’s stated aim is “to develop specifications that facilitate web pages and applications to be leveraged by LLMs and AI agents.” The draft lists WebMCP as its one normative deliverable, adopted from the Community Group. Charter refinement began on 1 October, and the W3C team estimated it would last until approximately 10 November 2026.[^ch17-34] In late October the discussion widened. A proposed change to the draft adds Agent Identity and Agent Delegation as tentative deliverables, Grigorik called `SubmitEvent.agentInvoked` “unspecified and incomplete”, and another participant raised EU consumer law, noting that “whether an agent’s click satisfies that is an open question”.[^ch17-35] Whether that charter survives review, and on what terms, is the nearest decision point after this book goes to press.

![Figure 17.2 — Three futures, and which of Trailhead’s assets carry over to each](images/figure-17-2.png)

The pattern in Figure 17.2 is the basis of the checklist that follows. Domain code, accessible UI and the knowledge captured in your catalog and evals survive every future. The adapter is the part that changes. So the adapter should be small, and it should be the only thing that knows the API’s shape.


## A future-proofing checklist

Trailhead uses the following list as a release gate. None of it needs WebMCP to win.

1. **Keep tools as data plus functions.** Define each tool’s name, description, schemas and annotations as plain data, and its behaviour as a function over your domain code that doesn’t read the DOM (Listing 17.1). The same definitions can feed WebMCP, a backend MCP server (Chapter 3) or a service worker. Chrome’s best practices now say the same thing in their own words: share the application service between the UI and the tools.[^ch17-37]
  2. **Put the API shape in one file.** Only the adapter calls `document.modelContext` (Listing 17.2). When continuation support or a new exposure keyword arrives, or the API moves again (Appendix D covers the move onto `document`, Appendix E the move to `Tool`), one file changes. The adapter already passes `outputSchema` through.
3. **Register all or nothing, and say when the batch is finished.** If one registration fails, roll back the ones before it, so an agent never sees half a catalog. That’s Chrome’s guidance too: “Register tools all at once” and “Roll back the whole batch on failure”.[^ch17-37] Pass the promise that includes that rollback to `waitForToolsUntil()`, if the method exists. `Promise.all()` can reject, and therefore settle, before the other registrations finish (Chapter 5).
4. **Validate inputs yourself.** The browser doesn’t check calls against `inputSchema`, and native validation is still being argued (#92).[^ch17-12] Return an error result the agent can act on: `status: 'error'` with a code and a message, as in Chapter 11.
5. **Write `outputSchema` now, and test results against it.** Browsers that don’t know it ignore it.[^ch17-11]
6. **Finish each call in one document.** Keep cross-page state on the server, keyed by identifiers you return.
7. **Never rely on exposure defaults.** Set `exposedTo` and the `tools` policy explicitly.
8. **Make consequential tools idempotent, and confirm on your own page.** Don’t depend on cancellation stopping side effects (#299, #344), or on any particular elicitation API.
9. **Don’t depend on unspecified behaviour.** That includes `getTools()` order and `toolactivated` timing. It also includes the way Chromium 156 serialises a plain string result, which a spec author called the browser’s bug, not the spec’s, in late October (#361).[^ch17-41] Use only annotations the spec defines.
10. **Keep the page accessible and well labelled.** It’s what people use, it’s what WebKit’s future builds on, and it’s the fallback for every agent that doesn’t speak WebMCP.
11. **Probe every browser release, and record what you tested.** Run a capability probe (Listing 17.3) and your evals (Chapter 14) against each new Chrome and Edge milestone, and read the diff. Chrome’s guide on building tools asks you to “record and isolate the specification revision, browser version, agent client, and model” for every test run, which is the only way to tell a regression in your tools from a change in the platform.[^ch17-38]
12. **Give someone the job of tracking the spec.** Watch the issues in Table 17.1, and send your findings to the Community Group. The authors keep asking for implementation experience, and several threads in this chapter moved because someone reported what they saw.

Listing 17.2 is Trailhead’s adapter. It’s deliberately boring.

**Listing 17.2** `chapters/17-the-road-ahead/src/adapter.js` — The adapter, the only file that knows the WebMCP API shape

```js
// adapter.js: the only file that knows the shape of the WebMCP API.
import { checkInput } from './check-input.js';

export function webmcpAvailable() {
  return typeof document !== 'undefined'
    && typeof document.modelContext?.registerTool === 'function';
}

export function registerCatalog(catalog, { signal, exposedTo } = {}) {
  if (!webmcpAvailable()) return Promise.resolve([]);
  // The caller awaits this same promise. The catch below aborts before it rejects.
  const done = registerBatch(catalog, { signal, exposedTo });
  document.modelContext.waitForToolsUntil?.(done);
  return done;
}

async function registerBatch(catalog, { signal, exposedTo } = {}) {
  // All or nothing: if one registration fails, the ones before it are rolled back.
  const batch = new AbortController();
  const batchSignal = signal ? AbortSignal.any([signal, batch.signal]) : batch.signal;
  const registered = [];
  try {
    for (const def of catalog) {
      const tool = {
        name: def.name,
        title: def.title,
        description: def.description,
        inputSchema: def.inputSchema,
        outputSchema: def.outputSchema,
        annotations: def.annotations,
        async execute(input, { signal: callSignal } = {}) {
          // The browser does not check input against inputSchema. We do.
          const problems = checkInput(def.inputSchema, input);
          if (problems.length > 0) {
            return { status: 'error', code: 'INVALID_ARGUMENT', message: problems.join('; ') };
          }
          return def.run(input, { signal: callSignal });
        },
      };
      const options = { signal: batchSignal };
      if (exposedTo) options.exposedTo = exposedTo;
      await document.modelContext.registerTool(tool, options);
      registered.push(def.name);
    }
  } catch (err) {
    batch.abort();
    throw err;
  }
  return registered;
}
```

The adapter feature-detects the current entry point and registers nothing if it isn’t there, so the page works the same without WebMCP. `registerCatalog` returns the batch promise, and passes that same promise to `waitForToolsUntil()` when the method exists. The tools are registered one after another, so a rejection does not leave a later `registerTool()` still pending. The `abort()` in the `catch` runs before the rejection, so the wait covers the rollback. A parallel `Promise.all()` would settle on the first rejection while other registrations were still running (Chapter 5). On Chromium 156 the method is not part of the recorded tests. The optional call is a no-op there if the method is missing, which is the point of `?.`. This edition did not re-run the fourteen checks.[^ch17-42] It passes `outputSchema` through, even though Chromium 156 drops it today. It wraps each `run()` in input validation. A bad call gets Chapter 11’s error shape, `{ status: 'error', code: 'INVALID_ARGUMENT', message }`, with every problem listed in the message, so the agent can fix the call in one go. In my tests, a call with no `query` and a negative `maxPrice` reaches the page untouched in Chromium 156, and the adapter answers with both problems.[^ch17-11] One `AbortSignal` unregisters the whole catalog, as in Chapter 5. And registration is all or nothing (item 3). Every tool is registered with a signal that combines the caller’s signal with a batch controller of the adapter’s own, so if one `registerTool()` call rejects, aborting the batch removes the tools that already made it, and the error still reaches the caller. In Chromium 156 a second tool with the same name rejects, and the tests use exactly that to check the rollback. The input checker, `check-input.js`, is a small subset of JSON Schema written for these tests. In production, use a full validator.

Listing 17.3 is the probe from item 11. It asks the browser what it actually supports: whether the current and the legacy entry points exist, whether the methods from the continuations explainer are there, whether `outputSchema` survives a round trip through `getTools()`, which annotations are kept and which options `execute` receives. The schema check is `outputSchema != null`. On a `Tool` the attribute is always present, so `'outputSchema' in tool` stays true when the value is `null`. Chromium 156 omitted the member. Both an omitted member and a `null` schema fail that check, which is why the 2 November result below is false.

**Listing 17.3** `chapters/17-the-road-ahead/src/probe.js` — A capability probe to run against each browser release

```js
// probe.js: what does this browser's WebMCP actually support today?
// Run it on a test page in CI, once per browser release. Not for production pages.
export async function probeWebMCP() {
  const mc = globalThis.document?.modelContext;
  const report = {
    documentModelContext: Boolean(mc),
    legacyNavigatorModelContext: 'modelContext' in (globalThis.navigator ?? {}),
    getTools: typeof mc?.getTools === 'function',
    executeTool: typeof mc?.executeTool === 'function',
    waitForToolsUntil: typeof mc?.waitForToolsUntil === 'function',
    resumeTool: typeof mc?.resumeTool === 'function',   // continuations explainer
    outputSchemaReflected: null,
    annotationsKept: null,
    executeOptions: null,
  };
  if (!report.documentModelContext || !report.getTools || !report.executeTool) {
    return report;
  }
  const controller = new AbortController();
  const name = `probe_${Math.random().toString(36).slice(2, 10)}`;
  try {
    await mc.registerTool({
      name,
      description: 'Feature probe for tests. Returns the option names it receives.',
      inputSchema: { type: 'object', properties: {} },
      outputSchema: { type: 'object', properties: { options: { type: 'array' } } },
      annotations: { readOnlyHint: true, sensitiveHint: false },
      execute: async (_input, options = {}) => ({ options: Object.keys(options) }),
    }, { signal: controller.signal });
    const tool = (await mc.getTools()).find((t) => t.name === name);
    // A Tool always has the attribute. A missing schema is null.
    // Chromium 156 omitted the member, which is also not a schema.
    report.outputSchemaReflected = tool.outputSchema != null;
    report.annotationsKept = Object.keys(tool.annotations ?? {}).sort();
    const raw = await mc.executeTool(tool, {});
    report.executeOptions = (typeof raw === 'string' ? JSON.parse(raw) : raw).options;
  } finally {
    controller.abort();
  }
  return report;
}
```

The probe registers a tool, so run it on a test page in CI, not on production pages, where an agent could see the probe tool for the instant it exists. It cleans up with `abort()` in a `finally` block, and the tests check that nothing is left behind. Here is what it reported on 2 November 2026 in Chromium 156.0.8078.4 with `--enable-features=WebMCPTesting`.[^ch17-11] That run did not include `waitForToolsUntil`. The field in Listing 17.3 was added with this edition, and the probe was not re-run. Chrome exposes the method with `ModelContext` from 160.0.8185.0. Whether the 2 November Chromium 156 build had it behind the earlier `WebMCPWaitForToolsUntil` flag was not checked.[^ch17-42]

```json
{
  "documentModelContext": true,
  "legacyNavigatorModelContext": false,
  "getTools": true,
  "executeTool": true,
  "resumeTool": false,
  "outputSchemaReflected": false,
  "annotationsKept": ["consequentialHint", "debugging", "readOnlyHint", "untrustedContentHint"],
  "executeOptions": ["signal"]
}
```

Each `false` in that report is a question from this chapter that the browser hasn’t answered yet. When one of them flips in a future release, the test that asserts it fails, and you know it’s time to read the release notes and update the adapter. The demo runs all three listings against a `document.modelContext` mock and against Chromium 156’s own implementation, and all fourteen checks pass in both modes.[^ch17-11]

> **Still in flux:** this chapter
>
> This is the chapter most likely to date. Every status here was read, or read again, on 2 November 2026. In the four weeks before that, the declarative API left the spec, the Working Group plan was dropped, the cross-origin section of the spec was finally written, and the TAG posted its first comments. Before relying on any row of Table 17.1, open the issue. The book’s companion repository keeps the probe and its expected results up to date.


## Closing the book

Chapter 1 began with a customer, a tent and an agent dragging a price slider back and forth, taking a screenshot after every nudge. The rest of the book has been about replacing that with something better: a page that says what it can do, in the page’s own code, with the user watching and the site in control.

Will that something be called WebMCP in two years? Will it live on `document.modelContext`? Will Safari ever implement it? Those are open questions, and this chapter leaves them open. The work behind a good tool isn’t open to question, though. Deciding which journeys matter, describing them in words a model can act on, giving them clear inputs and honest results, confirming consequential steps with the person they affect, measuring what happens and keeping the page usable by everyone: that’s what makes a site agent-ready. It carries over to every future in Figure 17.2. The API is the adapter. The rest is the product.


## Chapter summary

- WebMCP is a Community Group draft (24 November 2026 for `waitForToolsUntil()`; the October reading of this chapter used the 27 October draft, and the `Tool` paragraphs used 23 November) in origin trials that run to Chrome 162 and, in Edge, to 30 March 2027. Chrome Platform Status lists it as “Proposed”. Chrome plans to ship the imperative API first. The declarative API left the spec on 8 October and is an explainer again.
- Weigh open questions by where they live: explainer, issue, resolution, pull request or Chromium experiment. Track the spec, the explainers and Chromium separately.
  - PR #254 added optional `outputSchema` to the spec on 2 November. Issue #92 remains open on validation behavior. Chromium 156 still drops the member from `getTools()`; agent harnesses should validate declared results before returning them to a model.
- Multimodal results, file inputs, streaming and progress are open (#41, #81, #82). The editor prefers a web-shaped design to MCP’s content model (#86). Return compact JSON and references, and show rich output on the page.
- Cross-document responses are being explored as continuation tokens (`requestToken()`, `resumeTool()`), single-use, same-origin and short-lived. Service-worker tools are an explainer. Chromium 156 has neither. Finish calls in one document and keep tools thin.
- The spec now documents the two-sided opt-in for cross-origin tools (§6.3.4, PR #326, merged 27 October). Exposure defaults may still change, through a `native-agent` keyword, host-controlled iframe topologies (#317) or a second permissions policy (#236). Set exposure explicitly.
- Cancellation follows standard `AbortSignal` semantics (#299 and #344 closed): an aborted call’s result is discarded, and side effects can still happen. Event ordering (#332), sensitive reads (#331), elicitation (#165, PR #204) and tool grouping (#161, #255) are open.
- Three futures are argued: WebMCP as drafted, richer HTML and ARIA (WebKit, and now the TAG’s concern about a “web for agents”), and a generic cross-environment call API (#236). The TAG review is open and notes missing multi-stakeholder support. The Web Machine Learning Working Group plan was dropped on 13 October 2026 after Apple warned of a formal objection. A draft Agentic Web Working Group charter that names WebMCP is in refinement, estimated to run until about 10 November 2026.
- Domain code, accessible UI, the tool catalog and evals carry over to every future. The adapter changes. So keep the API shape in one adapter that registers all or nothing (Listing 17.2), keep tools as data plus functions (Listing 17.1), and run a probe (Listing 17.3) against every browser release.

## Notes

[^ch17-1]: WebMCP explainer, “Open Questions” (multimodal input/output, cross-document tool response, built-in agent exposure by default, transferable/streamable inputs and outputs, schema validation, skills, output schema, user prompting and elicitation, tool progress reporting, service workers integration), webmachinelearning/webmcp, unchanged since 14 October 2026 and read again on 2 November 2026. <https://github.com/webmachinelearning/webmcp#open-questions>
[^ch17-2]: WebMCP specification, Draft Community Group Report, 27 October 2026: §4.2 ModelContext Interface and its dictionaries, §6.3.4 Interaction with the Same-Origin Policy, and the IDL index. <https://webmachinelearning.github.io/webmcp/>
[^ch17-3]: Chrome Platform Status, “WebMCP” (feature 5117755740913664): Chrome status “Proposed”, developer trial from M146, origin trial M149–M156, extension to M162, seven listed owners, last updated 28 September 2026, read on 2 November 2026. <https://chromestatus.com/feature/5117755740913664>
[^ch17-4]: Microsoft Edge Origin Trials, “WebMCP” (trial expiration date 30 March 2027), read on 2 November 2026. <https://developer.microsoft.com/en-us/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a>
[^ch17-5]: Brandon Walderman, “WebMCP for Service Workers” (supplementary explainer, first published 28 August 2025): “Discovery and Installation”, “Tool Registration and Use”, “Session Management” and “Security Considerations”. <https://github.com/webmachinelearning/webmcp/blob/main/docs/service-workers.md>
[^ch17-6]: Mark A. Foltz, “Continuation Tokens” (explainer, added by pull request #327, merged 2 October 2026): “Overview”, “Proposal” (token creation and redemption) and “Agent Behaviors”. <https://github.com/webmachinelearning/webmcp/blob/main/continuations-explainer.md>
[^ch17-7]: webmachinelearning/webmcp pull request #338, “Remove declarative API from spec” (opened 7 October 2026, merged 8 October 2026), including François Beaufort’s comment of 13 October 2026 on Chrome’s shipping plan. <https://github.com/webmachinelearning/webmcp/pull/338>
[^ch17-8]: webmachinelearning/webmcp issue #9, “Introduce `outputSchema` (was: Should output also have a schema?)” (opened 12 August 2025, open on 2 November 2026), including the Community Group resolution of 5 February 2026. <https://github.com/webmachinelearning/webmcp/issues/9>
[^ch17-9]: webmachinelearning/webmcp pull request #254, “Add `outputSchema` to `ModelContextTool` and `RegisteredTool`” (merged 2 November 2026). <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch17-10]: Model Context Protocol specification, version 2026-07-28, “Server Features › Tools”: tool definition (`outputSchema`), “Structured Content” and “Output Schema”. <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>
[^ch17-11]: Tested by the author on 2 November 2026 with Playwright 1.64 and Chromium 156.0.8078.4, both with a `document.modelContext` mock and with the browser’s own implementation (`--enable-features=WebMCPTesting`). Code and tests: webmaxru/webmcp-book-demos, chapters/17-the-road-ahead. Results describe this build only.
[^ch17-12]: webmachinelearning/webmcp issue #92, “Who owns the validation layer?” (open on 15 November 2026), including the March resolution and comments through 9 November 2026 on input/output validation, error provenance and not passing malformed results to a model. <https://github.com/webmachinelearning/webmcp/issues/92>
[^ch17-13]: webmachinelearning/webmcp issue #41, “Support multimodal tool input/output” (opened 17 October 2025, open on 2 November 2026), including the comment of 20 October 2026. <https://github.com/webmachinelearning/webmcp/issues/41>
[^ch17-14]: webmachinelearning/webmcp issue #81, “Proposal: Support file attachments via imperative WebMCP API” (opened 11 February 2026), and issue #82, “Proposal: Stream Tool Arguments” (opened 13 February 2026), both open on 2 November 2026. <https://github.com/webmachinelearning/webmcp/issues/82>
[^ch17-15]: webmachinelearning/webmcp issue #86, “Proposal: Tool result content types beyond text” (opened 14 February 2026, closed 28 September 2026 in favour of #41), closing comment by Dominic Farolino. <https://github.com/webmachinelearning/webmcp/issues/86>
[^ch17-16]: webmachinelearning/webmcp issue #135, “Cross-document tool response mechanism” (opened 9 March 2026, open on 2 November 2026), including the resolutions of 16 April and 1 October 2026 and the comments of 5 and 6 October 2026. <https://github.com/webmachinelearning/webmcp/issues/135>
[^ch17-17]: Model Context Protocol specification, version 2026-07-28, “Key Changes” (changelog): removal of protocol-level sessions (SEP-2567) and of the initialize handshake (SEP-2575). <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
[^ch17-18]: Chrome for Developers, “WebMCP” (published 18 May 2026, updated 7 October 2026), “Limitations” and “Permissions policy”. <https://developer.chrome.com/docs/ai/webmcp>
[^ch17-19]: webmachinelearning/webmcp issue #317, “Host-controlled WebMCP access between iframes” (opened 23 September 2026, open on 2 November 2026), including Dominic Farolino’s comment of 24 September 2026 and Khushal Sagar’s comment of 26 October 2026. <https://github.com/webmachinelearning/webmcp/issues/317>
[^ch17-20]: webmachinelearning/webmcp pull request #326, “Document cross-origin tool exposure and two-sided opt-in in Section 6.3.4” (opened 28 September 2026, merged 27 October 2026), and the resulting §6.3.4 “Interaction with the Same-Origin Policy” and §6.3.4.1 “Enforcing Same-Origin Isolation via Two-Sided Opt-In” in the 27 October 2026 draft. <https://github.com/webmachinelearning/webmcp/pull/326>
[^ch17-21]: webmachinelearning/webmcp issue #299, “Let a tool deliver a final result on caller abort” (opened 6 September 2026, closed 25 September 2026), closing comment by Dominic Farolino. <https://github.com/webmachinelearning/webmcp/issues/299>
[^ch17-22]: webmachinelearning/webmcp issue #344, “Don’t start a tool whose `executeTool()` call was already cancelled” (opened and closed 14 October 2026), including Dominic Farolino’s comments and François Beaufort’s comment of 15 October 2026. <https://github.com/webmachinelearning/webmcp/issues/344>
[^ch17-23]: webmachinelearning/webmcp issue #332, “Fire `toolactivated` after invoking `execute`” (opened 1 October 2026, open on 2 November 2026), including François Beaufort’s comments of 15 and 28 October 2026. <https://github.com/webmachinelearning/webmcp/issues/332>
[^ch17-24]: webmachinelearning/webmcp issue #331, “Scope of `consequentialHint` for high-risk read tools” (opened 30 September 2026, open on 2 November 2026), including the `sensitiveHint` proposals of 1 to 3 October 2026. <https://github.com/webmachinelearning/webmcp/issues/331>
[^ch17-25]: webmachinelearning/webmcp issue #165, “WebMCP elicitation via requestUserInteraction()” (opened 16 April 2026), including the resolution of 11 June 2026, and pull request #204, “Replace requestUserInteraction with requestUserInput” (opened 9 June 2026), both open on 2 November 2026, including Ilya Grigorik’s proposal of 26 October 2026 on #165 and the comments of 29 October 2026 on #204. <https://github.com/webmachinelearning/webmcp/issues/165>
[^ch17-26]: Chrome for Developers, “WebMCP tool security” (published 9 June 2026, updated 1 September 2026), “Next steps”. <https://developer.chrome.com/docs/ai/webmcp/secure-tools>
[^ch17-27]: webmachinelearning/webmcp issue #161, “Proposal: Skills — workflow-level context for tool composition” (opened 3 April 2026), and issue #255, “Tool collections: coarse-grained grouping with progressive disclosure” (opened 22 August 2026), including the resolution of 3 September 2026 and the harness feedback on #255 of 20 October 2026, both open on 2 November 2026. <https://github.com/webmachinelearning/webmcp/issues/255>
[^ch17-28]: WebKit standards-positions issue #670, “WebMCP” (position: oppose, topics include meaningful user consent and forms), read on 2 November 2026. <https://github.com/WebKit/standards-positions/issues/670>
[^ch17-29]: WebMCP, “Declarative API Explainer”, webmachinelearning/webmcp. <https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md>
[^ch17-30]: webmachinelearning/webmcp issue #236, “Reposition feature as a generic communication tool?” (opened by Jake Archibald, 3 August 2026, open on 2 November 2026), including comments of 27 August, 22 September and 24 September 2026. <https://github.com/webmachinelearning/webmcp/issues/236>
[^ch17-31]: Mozilla standards-positions issue #1412, “WebMCP” (position: neutral, closed), which names Jake Archibald among the Mozillians who can provide input and refers to webmcp issue #236. <https://github.com/mozilla/standards-positions/issues/1412>
[^ch17-32]: W3C TAG design review #1238, “Incubation: WebMCP” (open on 2 November 2026, labels include “Missing: Multi-stakeholder support”), including the TAG’s early comment of 26 October 2026. <https://github.com/w3ctag/design-reviews/issues/1238>
[^ch17-33]: w3c/charter-drafts pull request #829, “[wg/webmachinelearning] Adds WebMCP in scope” (opened 9 June 2026, closed without merging 13 October 2026), including Marcos Cáceres’s comment of 13 August 2026 and Philippe le Hégaret’s comment of 28 September 2026. <https://github.com/w3c/charter-drafts/pull/829>
[^ch17-34]: W3C, “Agentic Web Working Group Charter” (draft, read on 2 November 2026), “Scope” and “Deliverables”, w3c/strategy issue #576 (opened 28 September 2026), and Xueyuan Jia, “Start of refinement for a draft Agentic Web Working Group charter”, public-new-work@w3.org, 1 October 2026. <https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html>
[^ch17-35]: w3c/strategy issue #576, “Agentic Web Working Group” charter refinement, comments of 26 October 2026 by Ilya Grigorik (Shopify) and by Francesco Marinoni Moretto (GitHub: frmoretto), and of 29 October 2026 on w3c/charter-drafts pull request #901, which adds Agent Identity and Agent Delegation as tentative deliverables. <https://github.com/w3c/strategy/issues/576>
[^ch17-36]: webmachinelearning/webmcp issue #236, comments of 30 October 2026 by Benjamin VanderSloot, Johann Hofmann and Jake Archibald after the face-to-face meeting. <https://github.com/webmachinelearning/webmcp/issues/236>
[^ch17-37]: Chrome for Developers, “WebMCP best practices” by Alexandra Klepper, Maxim Salnikov and François Beaufort (published 18 May 2026, last updated 30 October 2026), “Enforce architectural constraints” (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp/best-practices>
[^ch17-38]: Chrome for Developers, “Build your user’s agentic workflows with WebMCP tools” by André Cipriani Bandarra and Maxim Salnikov (published 26 August 2026, last updated 30 October 2026), “Manage reliability during testing” (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp/build-tools>
[^ch17-39]: Dominic Farolino, “Introduce the `Tool` interface”, webmachinelearning/webmcp pull request #348 (opened 15 October 2026, merged 19 November 2026). The generic-calling explainer is pull request #375, open on 23 November 2026 (Appendix F). <https://github.com/webmachinelearning/webmcp/pull/348>
[^ch17-40]: WebMCP specification, Draft Community Group Report, 27 October 2026, §6.2 Agent Baseline Capabilities, text added by pull request #334 (merged 20 October 2026). <https://github.com/webmachinelearning/webmcp/pull/334>
[^ch17-41]: webmachinelearning/webmcp issue #361 (opened 23 October 2026), including François Beaufort’s comment of 26 October 2026: “The WPT assertions are wrong, and so is Chrome.” <https://github.com/webmachinelearning/webmcp/issues/361>

[^ch17-42]: webmachinelearning/webmcp pull request #373, merged 24 November 2026, and Chromium commit `dc7d570dff77eca05dae42b1fa6e3b816205a94f` (25 November 2026, canary 160.0.8185.0). The commit message says `waitForToolsUntil()` had been gated by `WebMCPWaitForToolsUntil`, so origin-trial pages could not call it. <https://github.com/webmachinelearning/webmcp/pull/373> <https://chromiumdash.appspot.com/commit/dc7d570dff77eca05dae42b1fa6e3b816205a94f>
[^ch17-output-schema]: GoogleChromeLabs/webmcp-extension pull request #98, “Add support for tool outputSchema” (open on 15 November 2026), describes validating results in the host before model delivery. <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
