# Chapter 14: Testing, Debugging and Evals

> *“When testing systems that use generative AI, you must account for probabilistic outcomes that don't match your expectations.”*
>
> — Chrome for Developers, “Build your user’s agentic workflows with WebMCP tools”[^ch14-1]

## Two kinds of “it works”

By now Fjord Table has two tools and Trailhead has five. Each of them is a small piece of JavaScript: a name, a description, a schema and an `execute` callback. So why not test them like any other function? Call it with some input, check what comes back, done. We will do exactly that, and this chapter starts there. But it’s not enough, because a WebMCP tool has a second kind of correctness that ordinary functions simply don’t have.

The first kind is the one you already know. Given valid input, does `book_table` open the confirmation dialog and return a reference? Given a date in the wrong format, does it say so in a way an agent can act on? When the agent gives up halfway, does the dialog close with nothing booked? These questions have yes-or-no answers, and you can check them on every commit.

The second kind is about the caller. A person who wants a table for two adults and three children on Saturday says it in words. Somewhere between those words and your `execute` callback, a language model has to pick the right tool, turn “three kids” into part of `partySize` and turn “Saturday 28 November” into `2026-11-28`. You don’t control that model. It may behave differently tomorrow, and it may be a different model on a different user’s machine. Your descriptions and schemas are the only part of that step you own, so they are what you test — by running real models against them many times and counting how often they get it right. That kind of test is called an *eval*.

Let’s build both, in five layers (Figure 14.1). The lower layers are fast, cheap and certain. The upper ones are slower and noisier, and much closer to what your users actually experience. A good suite uses all five and runs the lower ones far more often than the upper ones.

![Figure 14.1 — Five layers of evidence that a tool works, from unit tests of execute callbacks up to real-user measurement.](images/figure-14-1.png)

A few words on how this chapter was checked. Every API detail below was validated against the WebMCP Draft Community Group Report dated 27 October 2026,[^ch14-2] against Chrome’s WebMCP and DevTools documentation and against the tip-of-tree Chrome DevTools Protocol, all re-read on 2 November 2026. Everything described as *observed* was observed in Chrome for Testing 156.0.8078.4 (an early build of the version that reached Chrome’s Stable channel on 20 October), launched by Playwright with the `WebMCPTesting` feature switched on, which is the switch behind `chrome://flags/#enable-webmcp-testing`.[^ch14-3] Every listing lives in the book’s companion repository, `webmaxru/webmcp-book-demos`, under `chapters/14-testing-debugging-evals/`, and its test script runs all of them. On 2 November 2026 all 21 checks passed again on that build.

## Seeing your tools

Before you write a single test, look at what the browser actually received. Most first bugs with WebMCP are not logic bugs at all. The tool never registered because the code ran before the feature check. Or it registered twice and the second call was rejected. Or it registered in the wrong view, or its schema isn’t quite what you meant. All of this is visible in a few seconds — with the right tool.

### The WebMCP pane in Chrome DevTools

Chrome DevTools has a **WebMCP** pane in the **Application** panel.[^ch14-4] It has two halves. **Available Tools** is a live list of the tools on the current tab, with each tool’s name and description exactly as the agent sees them, plus an invocation counter. **Invoked Tools** is a log of every call. Select an entry and you see its status (Completed, Canceled, In Progress or Error), the exact input the agent sent and the output or error your tool returned. You can filter the log by name or description, by status and by tool type, declarative or imperative. The status icons in the invocation counter are clickable too, and filter the log to calls with that status.[^ch14-4]

Two features make the pane much more than a viewer. The first is manual testing. Click a tool in **Available Tools**, or the play icon next to a logged call, and DevTools opens a form where you edit the input and press **Run tool**. When you start from a logged call, the form is pre-filled with the agent’s input. In simple words, this is the fastest way to reproduce “the agent called it with *this*, and it went wrong”. The second feature is troubleshooting. The documentation says the output pane can show parameter or return-value schema mismatches. Treat that as a DevTools debugging aid, not proof that native `executeTool()` rejects a bad result: output validation remains unresolved in issue #92. A harness should validate before the result reaches its model and should send an error instead of the malformed value.[^ch14-4]

Microsoft Edge lists “WebMCP debugging” among the updates Edge 149 took from the Chromium project, so the same pane is there in Edge.[^ch14-5]

> **Still in flux:** *What the pane checks.* Chrome’s page says the output pane reports schema violations. The specification, however, gives the browser no role in validating input against `inputSchema`. Issue #92, which asks who should own validation, is still open on 2 November 2026, although its October comments lean towards making schemas required and validating them in the browser (more on that below).[^ch14-6] Treat anything the pane flags as a debugging aid. It is no promise that the browser will reject bad calls in production. Your `execute` callback still has to validate.

### An agent of your own: two extensions and DevTools for agents

The pane lets *you* call tools. To see what a *model* does with them, you need an agent. Chrome’s documentation offers two Chrome extensions for that.[^ch14-3] The Model Context Tool Inspector lists a page’s tools, shows their input schemas and lets you try natural-language prompts against them, with Gemini through an API key or, if you enable `chrome://flags/#prompt-api-tool-use`, with an on-device model through the Prompt API (no key, and the data stays on your machine). The Example Agentic Chrome Extension does a similar job with a different emphasis: it “always trusts WebMCP annotations”, so it shows how an agent can use hints such as `consequentialHint` to warn the user before a sensitive action. The same page carries a caution worth repeating here: Chrome extensions can query and execute WebMCP tools from their content scripts. The Chrome team publishes the Inspector together with demos, a polyfill and the eval tool we use later in this chapter in the `GoogleChromeLabs/webmcp-tools` repository.[^ch14-7]

The second kind of agent is aimed at coding assistants. Chrome DevTools for agents, published on npm as `chrome-devtools-mcp` (version 1.12.0 as of 2 November 2026), is an MCP server that lets an AI coding assistant drive a Chrome instance. It has two WebMCP tools, `list_webmcp_tools` and `execute_webmcp_tool`. They are off by default and turned on with the `--categoryExperimentalWebmcp` server argument.[^ch14-4][^ch14-8] Version 1.11.0, released on 15 October, made them more useful for testing: `execute_webmcp_tool` now surfaces the exception when a tool throws, and both tools reject JSON arrays as tool parameters.[^ch14-9] With that flag on, the assistant you write code with can call the tools you have just written and read the results — a very handy loop while you are still designing a tool. It also tells you what both of these tools are built on: the DevTools Protocol, which we use directly later in this chapter.

### Tools that exist only for tooling: the `debugging` annotation

Chrome 156 added a fourth annotation next to `readOnlyHint`, `untrustedContentHint` and `consequentialHint`. When `debugging` is `true`, the tool is meant for inspection and developer tooling, such as testing frameworks or DevTools’ own AI assistance, and general-purpose agents can filter it out.[^ch14-10] That makes it the proper home for helpers you want during development but don’t want a shopper’s assistant to call, for example a tool that seeds Trailhead’s cart with test data or dumps the state of the current view.

In Chromium 156 the annotation comes back from `getTools()` together with the other three, filled in with defaults. A tool registered with `annotations: { readOnlyHint: true, debugging: true }` was returned with `{ consequentialHint: false, debugging: true, readOnlyHint: true, untrustedContentHint: false }`, and the DevTools Protocol reported it as `{ readOnly: true, untrustedContent: false, consequential: false, debugging: true }`. A tool registered with no annotations had no `annotations` member at all, in either place.

The 27 October 2026 draft defines `debugging` in its `ToolAnnotations` dictionary next to the other three hints, with a default of `false`.[^ch14-11]

> **Still in flux:** *A hint, not a lock.* Like every annotation, `debugging` is a hint. The draft stores it and hands it to agents, and what an agent does with it is up to the agent. Chrome’s documentation only says that agents *can* filter such tools out.[^ch14-10][^ch14-11] Since 20 October the specification’s security section also says it plainly: a malicious site can omit or misrepresent its hints.[^ch14-2] So never rely on `debugging` to hide anything sensitive. A debugging tool should not ship to production at all, or should be registered only behind a development-only check.

## Layer 1: unit tests for `execute` callbacks

### Write tools as data

The easiest WebMCP code to test is code that doesn’t touch `document.modelContext` at all. A tool is a plain object: a name, a description, a schema, annotations and a function. If you build that object in a factory that takes its dependencies as arguments, a test can build the very same object with fakes and call `execute()` directly in Node. No browser involved.

Listing 14.1 does this for two of Trailhead’s tools. Everything the tools need from the rest of the store (the catalogue, the cart and the part of the UI that shows results) arrives as an argument. The schema follows the canonical Trailhead definitions we have used throughout the book, and the validation in `checkSearchInput()` repeats every rule the schema states, because nothing else will enforce them. Failures come back in Chapter 11’s shape, `{ status, code, message }`, with the same codes as Chapter 10’s Trailhead.

**Listing 14.1** `chapters/14-testing-debugging-evals/trailhead-tools.js` — Trailhead’s tools built by a factory, so tests can inject fakes

```js
// Trailhead's tools, built by a factory. Every dependency arrives as an
// argument, so a unit test can pass fakes and call execute() directly.
export function createTrailheadTools({ catalog, cart, ui }) {
  const searchProducts = {
    name: 'search_products',
    title: 'Search products',
    description:
      'Search the Trailhead catalogue by keyword, with an optional category, ' +
      'maximum price in NOK and in-stock filter. Returns up to 10 products. ' +
      'Does not change the cart.',
    inputSchema: {
      type: 'object',
      properties: {
        query:       { type: 'string', description: 'Keywords, e.g. "2-person tent"' },
        category:    { type: 'string', enum: CATEGORIES },
        maxPrice:    { type: 'number', minimum: 0, description: 'Maximum price in NOK' },
        inStockOnly: { type: 'boolean', description: 'Only products that are in stock' }
      },
      required: ['query']
    },
    annotations: { readOnlyHint: true },
    async execute(input, { signal }) {
      const problem = checkSearchInput(input);              // the browser won't check
      if (problem) return { status: 'error', code: 'INVALID_ARGUMENT', message: problem };
      const hits = await catalog.search(input, { signal });
      ui.showResults(hits);                                 // the user sees it too
      return {
        products: hits.slice(0, 10).map((p) => ({
          sku: p.sku, name: p.name,
          price: { amount: p.price, currency: 'NOK' },
          rating: p.rating, inStock: p.stock > 0
        }))
      };
    }
  };

  const addToCart = {
    name: 'add_to_cart',
    title: 'Add to cart',
    description:
      'Add a product to the cart by its SKU from search_products. ' +
      'Returns the updated cart line, or a status and code saying why not.',
    inputSchema: {
      type: 'object',
      properties: {
        sku:      { type: 'string', description: 'SKU from search_products' },
        quantity: { type: 'integer', minimum: 1, maximum: 10 }
      },
      required: ['sku', 'quantity']
    },
    async execute({ sku, quantity }, { signal }) {
      if (typeof sku !== 'string' || sku === '')
        return { status: 'error', code: 'INVALID_ARGUMENT', message: 'sku must be a SKU from search_products.' };
      if (!Number.isInteger(quantity) || quantity < 1 || quantity > 10)
        return { status: 'error', code: 'INVALID_ARGUMENT', message: 'quantity must be a whole number from 1 to 10.' };
      const product = await catalog.get(sku, { signal });
      if (!product)
        return { status: 'error', code: 'UNKNOWN_SKU', message: `No product ${sku}. Call search_products first.` };
      if (product.stock < quantity)
        return { status: 'refused', code: 'OUT_OF_STOCK',
                 message: `Only ${product.stock} of ${product.name} in stock. Ask the user before adding fewer.`,
                 available: product.stock };
      const line = cart.add(product, quantity);
      ui.showCart(cart);
      return { sku, quantity: line.quantity,
               lineTotal: { amount: line.quantity * product.price, currency: 'NOK' } };
    }
  };

  return [searchProducts, addToCart];
}

export const CATEGORIES = ['tents', 'sleeping-bags', 'backpacks', 'footwear', 'clothing'];

function checkSearchInput({ query, category, maxPrice, inStockOnly }) {
  if (typeof query !== 'string' || query.trim() === '')
    return 'query must be a non-empty string, e.g. "tent".';
  if (category !== undefined && !CATEGORIES.includes(category))
    return `category must be one of: ${CATEGORIES.join(', ')}.`;
  if (maxPrice !== undefined && !(typeof maxPrice === 'number' && maxPrice >= 0))
    return 'maxPrice must be a number of NOK, 0 or more.';
  if (inStockOnly !== undefined && typeof inStockOnly !== 'boolean')
    return 'inStockOnly must be true or false.';
  return null;
}
```

Registering these tools in the real store is one line, the same pattern as in Chapter 5: `for (const tool of createTrailheadTools(deps)) await document.modelContext.registerTool(tool, { signal });`. What changes is the factory. In Chapter 10’s React version the dependencies come from the component tree, here they could come from anywhere. This is also the shape Chrome’s best-practices page now asks for under “Share the application service”: the UI, the WebMCP tools and the tests all go through one service for validation, permissions and side effects, so a tool never becomes a second, less careful entrance to your app.[^ch14-12]

### What to test

Listing 14.2 is the unit test file. It uses `node:test`, the test runner built into Node.js and stable since Node 20, so it needs no dependencies.[^ch14-13] The fakes in `tests/fixtures/fakes.js` are about sixty lines: an in-memory catalogue of six products, a cart and a UI object that records what it was asked to show.

**Listing 14.2** `chapters/14-testing-debugging-evals/tests/trailhead-tools.test.js` — unit tests for the execute callbacks

```js
// Unit tests for Trailhead's execute callbacks. No browser, no WebMCP:
// node --test tests/trailhead-tools.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createTrailheadTools } from '../trailhead-tools.js';
import { fakeCatalog, fakeCart, recordingUi } from './fixtures/fakes.js';

function setup() {
  const catalog = fakeCatalog();
  const ui = recordingUi();
  const [search, addToCart] = createTrailheadTools({ catalog, cart: fakeCart(), ui });
  return { catalog, ui, search, addToCart };
}
const run = (tool, input, signal = new AbortController().signal) =>
  tool.execute(input, { signal });

test('search_products returns NOK prices and shows the same results', async () => {
  const { search, ui } = setup();
  const { products } = await run(search, { query: 'tent', maxPrice: 3000 });
  assert.ok(products.length > 0);
  for (const p of products) {
    assert.equal(p.price.currency, 'NOK');
    assert.ok(p.price.amount <= 3000);
  }
  assert.equal(ui.calls.at(-1)[0], 'showResults');           // the user sees it too
});

test('input the schema forbids comes back as a value, not a throw', async () => {
  const { search, catalog } = setup();
  for (const input of [{}, { query: '' }, { query: 'tent', maxPrice: '3000' },
                       { query: 'tent', category: 'kayaks' }]) {
    const result = await run(search, input);
    assert.equal(result.status, 'error', JSON.stringify(input));
    assert.equal(result.code, 'INVALID_ARGUMENT');
    assert.match(result.message, /must/);                    // tells the agent how to fix it
  }
  assert.equal(catalog.searches, 0);                         // never reached the backend
});

test('add_to_cart explains a stock problem the agent can act on', async () => {
  const { addToCart } = setup();
  const result = await run(addToCart, { sku: 'TH-TENT-2P', quantity: 9 });
  assert.equal(result.status, 'refused');
  assert.equal(result.code, 'OUT_OF_STOCK');
  assert.equal(result.available, 3);
});

test('an aborted call stops before touching the backend', async () => {
  const { search, catalog } = setup();
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(run(search, { query: 'tent' }, controller.signal),
                       { name: 'AbortError' });
  assert.equal(catalog.searches, 0);
});
```

Each test targets one specific way a tool can let an agent down.

**The result is shaped the way the description promises.** Prices are in NOK, at most ten products come back, and the same results reach the page. That last check matters more than it looks. Chapter 4 argued that a tool should drive the same UI a person uses, so that the user sees what the agent sees. A unit test is the cheapest place to keep that promise from quietly breaking.

**Input the schema forbids is answered with a value.** For me, this is the most important test in the file. The browser passes your callback whatever object the agent sent, as long as it is an object. It does not check it against `inputSchema`: the draft’s tool execute steps only reject input that isn’t an object.[^ch14-14] Whether the browser *should* validate is the question of issue #92, open since February 2026. In October it got lively. Google’s Mark Foltz argued on 13 October that `inputSchema` and the proposed `outputSchema` should become required, so that validation can later be layered into the browser, François Beaufort answered that they should stay optional with defaults the spec defines, Microsoft’s Samuel Dallstream sided with Foltz, and on 30 October Johann Hofmann wrote “Full support from security for requiring and validating these schemas in the spec”.[^ch14-6] PR #254 has since added optional `outputSchema` to the tool dictionaries, but issue #92 remains open on who validates schemas and what errors native calls should expose. The current spec does not say that `executeTool()` must reject an output mismatch. A missing `query`, a price sent as the string `'3000'` or a category the store doesn’t have still reaches your code in the Chromium 156 build tested here. The test sends each of them and checks two things: the tool returns status `'error'` with code `INVALID_ARGUMENT` and a message that says how to fix the call, and the backend was never touched. (And if browsers do start validating one day, this test keeps passing. It just stops being your only line of defence.)

**Stock problems are explained, not thrown.** A `refused` result with code `OUT_OF_STOCK` that includes `available: 3` lets an agent offer the user three tents instead of failing. Chapter 6 covered why recoverable failures should be return values, and Chapter 11 why a business rule is a refusal and not an error. Here is where you make sure they stay that way.

**An aborted call stops early.** An agent that gives up aborts the signal it passed to your callback. The test hands the tool an already-aborted signal and checks that it rejects with `AbortError` before reaching the catalogue. In the real page, this is what keeps a cancelled search from overwriting the results of the user’s next one.

Run the file with `node --test tests/trailhead-tools.test.js`. On the machine used for this chapter the four tests took about 80 milliseconds in total. And that speed is the whole point of this layer: these tests can run on every save, and they cover most of the logic in your tools.

> **Tip:** *A schema contract test.* Validation code and schemas drift apart. Someone raises the maximum quantity to 20 in the schema and forgets the check, or the other way round. A cheap guard is a test that walks the schema and, for every constraint it declares (`required`, `enum`, `minimum`, `maximum`), sends one input that breaks it and expects status `'error'` with code `INVALID_ARGUMENT`. The second test in Listing 14.2 is a hand-written version of that idea for `search_products`.

Chrome’s guide on building tools, a page I co-authored, adds two more habits to this layer.[^ch14-1] The first is to *test “time travel” states*: run sequences deterministically where the application edits, undoes, times out or reuses an idempotency key, because “the underlying state may have changed even when the page looks the same”. With a factory and fakes, that’s a few more test cases: add to the cart, change the fake catalogue’s stock, call again, and check that the second answer reflects the new state. The second habit is to *pin versions*: “Record and isolate the specification revision, browser version, agent client, and model during testing to track compatibility drift.” The eval reports in this chapter’s repository record the agent, the model, the Chromium build and the date of every run, this chapter names the specification revision it was checked against, and Table 14.1 below shows why all four matter.

## Layer 2: the browser contract

Unit tests stop at the edge of your code. The next layer checks the part between your code and the agent: that the tool really registers, that `getTools()` lists it with the schema and annotations you meant, and that a call made through the browser comes back the way you expect.

There are two ways to get a `document.modelContext` into a test browser, and the companion repository uses both. The first is a mock: a small script injected before the page loads that implements `registerTool()`, `getTools()` and `executeTool()` in plain JavaScript. It works in any browser and on any CI machine, and it lets you test pages long before the browsers you care about ship the API. The second is the real thing: Chromium launched with `--enable-features=WebMCPTesting`. Playwright’s bundled Chromium 156 accepts the switch, so the same test file can run against either, chosen by an environment variable.

The test for Listing 14.8, later in this chapter, is written exactly that way. `tests/rum.test.js` loads a page that registers Trailhead’s tools, calls them with `getTools()` and `executeTool()` from inside the page, and runs once with the mock and once with Chromium’s own implementation. Is running both redundant? Not at all. The mock tells you that your page uses the API as specified. Chromium tells you what will actually happen today. And the two disagree in more places than you might expect (Table 14.1).

**Table 14.1 — Things a browser contract test should pin down: the 27 October 2026 draft against Chromium 156 (observed on 2 November 2026)**

| Behaviour | Draft (27 October 2026) | Chromium 156 (observed) |
|---|---|---|
| A tool returns a plain string | JSON-serialized, so it arrives quoted (confirmed by an editor on 26 October, issue #361) | Arrives as the bare string |
| A tool returns `undefined` | `OperationError` (issue #361 proposes the string `"null"` instead) | The string `"undefined"` |
| A tool throws | `OperationError` | `UnknownError` |
| Calling a tool that was unregistered | `NotFoundError` | `UnknownError` |
| What `executeTool()` resolves to | A string (`Promise<DOMString>`) | A string, so parse it with `JSON.parse()` |
| Invalid name, empty description, duplicate name | `InvalidStateError` | `InvalidStateError` |

Sources: the specification’s IDL, execute steps and table of tool execution errors,[^ch14-14] and issue #361 for the serialization ruling.[^ch14-15] The Chromium column comes from the Fjord Table test suite in the companion repository, run against Chromium 156.0.8078.4 with WebMCPTesting on 14 and 15 October 2026 and again on 2 November 2026.[^ch14-16]

Some of these differences are history catching up, and the top two rows got a ruling just after the first edition went out. On 23 October, issue #361 reported that the specification JSON-encodes a returned string and rejects `undefined`, while Chrome and the web-platform-tests do neither. François Beaufort, the author of the original serialization change, answered on 26 October: “The WPT assertions are wrong, and so is Chrome. A tool that returns "hi" should resolve to '"hi"'.” In the same reply he suggested that `undefined` should not reject at all and should map to `null`, so the result would be the string `"null"`. That second part is a proposal and nothing is merged yet.[^ch14-15] Please note: the issue reports the same behaviour in Chrome 158.0.8119.0 as in 156, so as of that report Chrome had not changed how it serializes results.

The error rows are moving too. The draft replaced its generic `UnknownError` rejections with specific `DOMException` types on 8 October 2026, in pull request #339, and our Chromium 156 build still reports `UnknownError`.[^ch14-17] Chromium itself has already followed the specification: a change titled “Reject executeTool() with granular DOMExceptions” landed on Chromium’s main branch on 16 October, with updated web-platform-tests, and a day earlier another change replaced the `RegisteredTool` dictionary that `getTools()` returns with a `Tool` interface object, so that executing a stale tool after a same-named re-registration rejects instead of running the new tool.[^ch14-18] Both landed after the Chrome 157 branch point, so the first version that should carry them is Chrome 158, in the Beta channel as of 2 November 2026. I have not observed either in a browser, because only Chromium 156 builds were available for this chapter’s tests. The `Tool` interface is still an open pull request on the specification side (#348).

Bottomline: assert on the shape your *page* controls, a JSON object with a `status` field (Chapter 11’s convention), and avoid tests that depend on how the browser wraps strings, `undefined` or exceptions. Those are exactly the details that are changing right now. If you must pin one of them, put the browser version in the test name, as Chrome’s “pin versions” advice suggests, so that the failure tells you what moved.

### What the web-platform-tests already cover

The browsers have their own contract tests, and they are very much worth reading. The specification names its test suite in its header: the `webmcp/` directory of web-platform-tests (WPT), with results on wpt.fyi.[^ch14-2] On 2 November 2026 that directory held an IDL test, tests for the `toolactivated` and `toolcancel` events, a `declarative/` folder with 25 HTML test files and an `imperative/` folder with 51 (49 when I first counted, on 15 October).[^ch14-19] Their names read like a list of edge cases you would otherwise discover in production: `executeTool-abort`, `unregister-during-executeTool`, `executeTool-target-navigation`, `exposedTo-cross-origin-child`, `register_tool_name_validation`, `non-secure`, and the new `tool-re-registration-race`.

The tests use `testharness.js`, so each one is a short page you can open and read, and they are often the most precise description of a behaviour you will find anywhere. The `toolcancel` event test, for example, carries a comment explaining the order of things: aborting the caller’s signal rejects the `executeTool()` promise first, and only then cancels the tool’s own execution, which queues the task that fires `toolcancel`. So awaiting the rejection alone isn’t enough to observe the event.[^ch14-20] If your page listens for `toolcancel` to clean up, that ordering is exactly what your own tests need to wait for.

One more thing to keep in mind after #361: on this point WPT follows the browser and disagrees with the specification. A suite can be wrong, and a test page is a statement of what someone believed on the day it was written. When you find a behaviour the WPT suite doesn’t cover (the observations in this chapter include a few), a WPT-style test page is also the most useful bug report you can write. We come back to that at the end of the chapter.

## Layer 3: calling tools the way a browser agent does

A test that calls `executeTool()` from inside the page calls your tool the way an *in-page* agent would (Chapter 7). Chrome’s built-in agent and agent extensions don’t live in your page. They reach your tools through the browser. If you want a test that exercises that path, including the moment where a person clicks a button in your UI halfway through a call, you need to stand where the browser agent stands. The Chrome DevTools Protocol lets you do exactly that.

### The WebMCP domain

The DevTools Protocol (CDP) is the interface Chrome DevTools uses to inspect and control the browser, and the one that automation libraries such as Playwright and Puppeteer let you talk to directly. Its tip-of-tree version has an experimental `WebMCP` domain with four commands and four events (Table 14.2).[^ch14-21] DevTools’ WebMCP pane is, in effect, a user interface for this domain.

**Table 14.2 — The WebMCP domain of the Chrome DevTools Protocol (experimental, tip-of-tree, unchanged from 15 October to 2 November 2026)**

| Name | Kind | What it does |
|---|---|---|
| `WebMCP.enable` | command | Starts sending events, and fires `toolsAdded` for every tool already registered |
| `WebMCP.disable` | command | Stops sending events |
| `WebMCP.invokeTool` | command | Calls a tool by `frameId` and `toolName` with an `input` object; returns an `invocationId` |
| `WebMCP.cancelInvocation` | command | Cancels a pending invocation by `invocationId` |
| `WebMCP.toolsAdded` | event | Tools were registered: name, description, `inputSchema`, annotations, `frameId`, and the registration’s stack trace |
| `WebMCP.toolsRemoved` | event | Tools were unregistered: name and `frameId` |
| `WebMCP.toolInvoked` | event | A call started: tool name, frame, `invocationId` and the input as a JSON string |
| `WebMCP.toolResponded` | event | A call ended with status `Completed`, `Canceled` or `Error`, plus `output`, `errorText` or the thrown exception |

Source: the protocol definition.[^ch14-21]

Two details in the definition are worth noticing. The `invokeTool` response, which carries the `invocationId`, “is sent before tool events”, so a client always learns the ID before the result arrives. And the description of `output` warns that it is untrusted and “poses a prompt injection risk”, so clients should treat it as potentially malicious input.[^ch14-21] Your test harness is a client too. If you ever feed tool output back into a model, as the eval runner later in this chapter does, that warning applies to you.

### A small driver

Listing 14.3 wraps the domain in about fifty lines. It keeps a live map of tools from `toolsAdded` and `toolsRemoved`, records every call, and turns the asynchronous `invokeTool` + `toolResponded` pair into something a test can simply `await`. It works with any CDP session that has `send()` and `on()`, which includes Playwright’s `CDPSession` (created with `page.context().newCDPSession(page)`)[^ch14-22] and Puppeteer’s.

**Listing 14.3** `chapters/14-testing-debugging-evals/webmcp-cdp.js` — a driver for the WebMCP DevTools Protocol domain

```js
// A small driver for the WebMCP domain of the Chrome DevTools Protocol
// (experimental). Takes any CDP session with send() and on(), such as
// Playwright's CDPSession or Puppeteer's CDPSession.
export async function attachWebMCP(cdp) {
  const tools = new Map();        // name -> Tool, as DevTools reports it
  const calls = [];               // one record per invocation, for reports
  const waiting = new Map();      // invocationId -> resolve()
  const early = new Map();        // responses that beat the waiter

  cdp.on('WebMCP.toolsAdded', (e) => { for (const t of e.tools) tools.set(t.name, t); });
  cdp.on('WebMCP.toolsRemoved', (e) => { for (const t of e.tools) tools.delete(t.name); });
  cdp.on('WebMCP.toolInvoked', (e) => calls.push({ ...e, input: JSON.parse(e.input) }));
  cdp.on('WebMCP.toolResponded', (e) => {
    Object.assign(calls.find((c) => c.invocationId === e.invocationId) ?? {}, e);
    const resolve = waiting.get(e.invocationId);
    if (resolve) resolve(e); else early.set(e.invocationId, e);
  });
  await cdp.send('WebMCP.enable');  // replays toolsAdded for tools already registered

  async function start(name, input = {}, { timeout = 15_000 } = {}) {
    const tool = tools.get(name);
    if (!tool) throw new Error(`No WebMCP tool named "${name}"`);
    const { invocationId } = await cdp.send('WebMCP.invokeTool',
      { frameId: tool.frameId, toolName: name, input });
    const response = early.has(invocationId)
      ? Promise.resolve(early.get(invocationId))
      : new Promise((resolve, reject) => {
          const timer = setTimeout(() => reject(new Error(`${name}: no response`)), timeout);
          waiting.set(invocationId, (e) => { clearTimeout(timer); resolve(e); });
        });
    return { invocationId, response };   // response: { status, output?, errorText?, exception? }
  }

  return {
    tools,
    calls,
    start,
    async invoke(name, input, options) {
      return (await start(name, input, options)).response;
    },
    cancel: (invocationId) => cdp.send('WebMCP.cancelInvocation', { invocationId }),
    async waitForTool(name, { timeout = 5_000 } = {}) {
      for (const end = Date.now() + timeout; !tools.has(name); ) {
        if (Date.now() > end) throw new Error(`Tool "${name}" never appeared`);
        await new Promise((r) => setTimeout(r, 50));
      }
      return tools.get(name);
    }
  };
}
```

There are two ways to call a tool. `invoke()` waits for the result, which suits most tests. `start()` returns as soon as the browser has accepted the call, with the `invocationId` and a promise for the response, so a test can do something in the middle: click a button, check the screen or cancel the call.

The `early` map is defensive. The protocol promises that the `invokeTool` response comes before the tool’s events, but a fast tool can finish before the test’s own code has registered its waiter, and the map makes sure that response isn’t lost.

### Fjord Table under test

Listing 14.4 uses the driver to test Fjord Table’s booking flow end to end. It serves the Fjord Table demo from the companion repository, launches Chromium with WebMCP on and attaches the driver to each new page *before* navigating, so that `toolsAdded` reports both tools as the page registers them.

**Listing 14.4** `chapters/14-testing-debugging-evals/tests/fjord-table.cdp.test.js` — Fjord Table driven over the DevTools Protocol, with a human click in the middle

```js
// Fjord Table, driven the way a browser agent drives it: over the WebMCP
// DevTools Protocol domain, with a human click in the site's own dialog.
// Needs Chromium with WebMCP on:  node --test tests/fjord-table.cdp.test.js
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { attachWebMCP } from '../webmcp-cdp.js';
import { serve, nextOpenDate } from './fixtures/serve.js';

let browser, site;
before(async () => {
  site = await serve(new URL('../../../fjord-table/', import.meta.url));
  browser = await chromium.launch({ args: ['--enable-features=WebMCPTesting'] });
});
after(async () => { await browser?.close(); await site?.close(); });

async function openBookingView() {
  const page = await browser.newPage();
  const webmcp = await attachWebMCP(await page.context().newCDPSession(page));
  await page.goto(`${site.url}#/book`);
  await webmcp.waitForTool('search_availability');
  await webmcp.waitForTool('book_table');      // registered only on this view
  return { page, webmcp };
}
const DATE = nextOpenDate();

test('agent books, person confirms in the site dialog', async () => {
  const { page, webmcp } = await openBookingView();
  const found = await webmcp.invoke('search_availability', { date: DATE, partySize: 2 });
  assert.equal(found.status, 'Completed');
  const time = found.output.slots[0];

  const call = await webmcp.start('book_table', { date: DATE, time, partySize: 2 });
  await page.waitForSelector('#confirm-dialog[open]');    // Fjord Table's own UI
  await page.click('#confirm-submit');                     // the human's decision
  const { status, output } = await call.response;

  assert.equal(status, 'Completed');
  assert.equal(output.status, 'booked');
  assert.match(output.reference, /^FT-\d+$/);
  assert.equal(webmcp.calls.at(-1).input.partySize, 2);    // what the agent sent
});

test('bad input is answered with a value the agent can fix', async () => {
  const { webmcp } = await openBookingView();
  const { status, output } =
    await webmcp.invoke('book_table', { date: '20/11/2026', time: '19:00', partySize: 2 });
  assert.equal(status, 'Completed');                       // not an Error
  assert.equal(output.status, 'error');
  assert.equal(output.code, 'INVALID_INPUT');
  assert.match(output.message, /YYYY-MM-DD/);
});

test('cancelling a call aborts the tool and closes the dialog', async () => {
  const { page, webmcp } = await openBookingView();
  const { output } = await webmcp.invoke('search_availability', { date: DATE, partySize: 4 });
  const call = await webmcp.start('book_table',
    { date: DATE, time: output.slots[0], partySize: 4 });
  await page.waitForSelector('#confirm-dialog[open]');
  await webmcp.cancel(call.invocationId);                  // the agent gives up

  assert.equal((await call.response).status, 'Canceled');
  await page.waitForFunction(() => !document.querySelector('#confirm-dialog').open);
  assert.equal(await page.isHidden('#confirmation'), true); // nothing was booked
});
```

The first test is the whole of Figure 14.2 in a dozen lines. The agent searches and starts a booking, and the test waits for Fjord Table’s own confirmation dialog to open before playing the person who presses **Confirm booking**. Only then does `toolResponded` arrive, with status `Completed` and Fjord Table’s result as the output. The second test checks that a malformed date comes back as a *successful* call whose output has status `'error'` and code `INVALID_INPUT`, which is what Chapter 6 asked for: from the protocol’s point of view, a recoverable failure is not an error. The third starts a booking, cancels it from the agent’s side while the dialog is open, and checks three things: the protocol reports `Canceled`, the dialog closes because the tool’s own `signal` was aborted, and nothing was booked.

![Figure 14.2 — Testing a tool the way a browser agent calls it: the test attaches to the WebMCP domain, invokes a tool, plays the person who confirms, and reads the result.](images/figure-14-2.png)

All three tests passed against Chromium 156, in October and again on 2 November 2026. Writing them also turned up a few behaviours that the protocol definition doesn’t spell out. They are worth knowing before you rely on them.

**`toolsAdded` arrives once per registration.** Fjord Table registers its two tools from two modules, and the driver saw two separate `toolsAdded` events, each with one tool. Because `book_table` is registered as soon as the booking view opens, while `search_availability` waits for its module’s top-level `await`, `book_table` was reported first. A first version of the test waited only for `book_table` and then failed to find `search_availability`. So wait for each tool you are about to call by name, as `openBookingView()` does, and not for “some tools”. Chrome’s best practices now recommend registering a workflow’s tools all at once and rolling back the whole batch on failure,[^ch14-12] but even a page that does that still makes one `registerTool()` call per tool, and a test should not assume more than the protocol promises.

**Calling a tool that doesn’t exist fails the command itself.** `invokeTool` with an unknown name was rejected with the protocol error `Tool not found`, instead of returning an `invocationId` and reporting an error later.

**A throw arrives with the exception.** A tool that threw `new Error('kaput')` produced a `toolResponded` with status `Error`, an empty `errorText` and an `exception` object whose description was the error’s message and stack trace, pointing at the line in the page that threw. That is far more useful in a test log than the `UnknownError` an in-page caller gets in Chromium 156 (Table 14.1).

**Cancelling aborts the tool’s signal and fires `toolcancel`.** After `cancelInvocation`, the tool’s `signal` fired `abort`, `toolcancel` was dispatched on the page’s `document.modelContext`, and the protocol reported `Canceled`.

**Object results arrive as objects.** For a tool that returned `{ got: { x: 3 } }`, the `output` field of `toolResponded` was that object, not a JSON string. The protocol declares `output` as type `any`, so a different build could send a string. The driver passes it through unchanged.

**`toolactivated` fired after `execute` had started.** The draft’s tool execute steps fire `toolactivated` at the page before the execute callback is invoked.[^ch14-14] In Chromium 156, the synchronous start of an `async execute` function ran *before* the page’s `toolactivated` listener. If you use the event to set up state that `execute` relies on, you will hit that difference. Use it for logging and UI hints, and not for setup.

> **Still in flux:** *The protocol domain.* The `WebMCP` domain is marked experimental and lives only in the tip-of-tree version of the protocol, which changes with Chrome. As of the protocol roll of 31 October 2026 it was unchanged since the first edition.[^ch14-21] Its annotation names (`readOnly`, `consequential`) already differ from the page API’s (`readOnlyHint`, `consequentialHint`), and its `Annotation` type still has an `autosubmit` field for declarative tools, although the declarative API left the specification on 8 October 2026 with pull request #338 and now lives in its own explainer.[^ch14-23] The Chromium change that introduced the `Tool` interface also says that DevTools still identifies tools by name, and that moving it to IDs is follow-up work.[^ch14-18] Keep protocol access in one module, as Listing 14.3 does, so that a rename costs you one file. And keep a small set of in-page tests next to the protocol tests, because only those use a surface the specification defines.

The same driver should work for tools registered inside frames: every `Tool` in `toolsAdded` carries the `frameId` of the frame that registered it, and `invokeTool` takes that ID.[^ch14-21] The Helpdesk Widget of Chapter 7 registers its tools inside a cross-origin iframe. I haven’t tested that combination through the protocol yet, so please treat it as the next experiment to run.

### Output-schema contract tests

A schema contract test should exercise both sides of the model boundary. A matching result reaches the planner. A wrong type or missing required property becomes a clear validation error. A tool without `outputSchema` remains callable. Most importantly, the planner’s transcript contains no raw invalid result, including when validation fails. The Chapter 9 Test Agent uses `@cfworker/json-schema` for this check; WebMCP Extension PR #98 shows the same host-side placement. Chromium 156 tests only the API behavior available in that build; they do not verify Chrome 159.0.8140.0.[^ch14-output-schema]

## Layer 4: evaluations against real models

Everything so far has been deterministic. Each test calls a tool with input *you* chose. An eval hands that choice to a model. You give the model a user’s request and your page’s tools, let it decide what to call, run those calls against the real page and score what happened. Chrome’s guide on building tools puts it in one sentence: evals can help you verify consistent tool selection, parameter extraction, and state management.[^ch14-1] Those three phrases make a good checklist for what a suite should cover.

- **Tool selection.** Given “is there a table for two on Friday?”, does the model call `search_availability`, and not `book_table`?
- **Parameter extraction.** Does “two adults and three kids” become `partySize: 5`? Does “21 November” become `2026-11-21` and not `21/11/2026`?
- **State management.** After a search, does the model book the slot the user asked for, and does the page end up showing a booking?

Chrome has a whole page on the topic, “Test WebMCP with Evals”, and it is a good companion to this section.[^ch14-24] It walks through the failure modes from both sides (the agent picks the wrong tool, calls tools in the wrong order or with wrong arguments, and the tool itself returns something wrong or too verbose), it recommends testing each tool in isolation before any browser simulation (“If an agent can't figure out which tool to call for a request like, "I'd like a small pizza," it won't stand a chance in a complex user journey”), and it reminds you to keep writing classic deterministic tests for everything that doesn’t talk to a model. Two of its ideas we will reuse below: an eval case should include the *full* list of tools the page exposes in that state, including the ones you are not testing, and a dataset should mix direct requests with ambiguous ones (“Add pepperoni to my pizza” versus “I want all of the meat on my pizza”).

### A task suite

You don’t have to invent a format. The Chrome team’s `webmcp-evals` tool, published in `GoogleChromeLabs/webmcp-tools` and on npm (version 0.0.4, marked experimental, still the latest on 2 November 2026), reads test cases from an `evals.json` file.[^ch14-25] Each case has a name, the conversation so far and the tool calls you expect, with argument values that can be exact or constraints such as `$pattern`, `$contains`, `$gte` or `$type`. Expected calls can be marked `optional`, and Chrome’s evals page also shows `ordered` and `unordered` groups for journeys where some steps may come in any order.[^ch14-25][^ch14-24] Listing 14.5 is Fjord Table’s first suite in that format.

**Listing 14.5** `chapters/14-testing-debugging-evals/evals/fjord-table.evals.json` — a task suite for Fjord Table

```json
[
  {
    "name": "Find a table for two on a named date",
    "messages": [
      { "role": "user", "type": "message",
        "content": "Is there a table for two at Fjord Table on Friday 20 November 2026, around 7 in the evening?" }
    ],
    "expectedCall": [
      { "functionName": "search_availability",
        "arguments": { "date": "2026-11-20", "partySize": 2,
                       "time": { "$pattern": "^(18|19|20):\\d{2}$" } } }
    ]
  },
  {
    "name": "Search, then book the slot the user asked for",
    "messages": [
      { "role": "user", "type": "message",
        "content": "Book us a window table for four at 19:30 on 21 November 2026. It's my mum's birthday." }
    ],
    "expectedCall": [
      { "functionName": "search_availability",
        "arguments": { "date": "2026-11-21", "partySize": 4 }, "optional": true },
      { "functionName": "book_table",
        "arguments": { "date": "2026-11-21", "time": "19:30", "partySize": 4,
                       "seating": "window", "notes": { "$contains": "birthday" } } }
    ],
    "assertions": [
      { "type": "dom", "selector": "#confirmation",
        "expect": { "text": { "$contains": "Booked: FT-" } } }
    ]
  },
  {
    "name": "Children count as guests",
    "messages": [
      { "role": "user", "type": "message",
        "content": "Two adults and three kids, Saturday 28 November 2026 at 17:30 please. Any table is fine." }
    ],
    "expectedCall": [
      { "functionName": "search_availability",
        "arguments": { "date": "2026-11-28", "partySize": 5 }, "optional": true },
      { "functionName": "book_table",
        "arguments": { "date": "2026-11-28", "time": "17:30", "partySize": 5 } }
    ],
    "assertions": [
      { "type": "dom", "selector": "#my-bookings li", "expect": { "count": 1 } }
    ]
  }
]
```

The three cases follow the three phrases above. The first is pure tool selection and extraction, with a regular expression that accepts any time from 18:00 to 20:59 for “around 7 in the evening”. The second and third test the full search-then-book flow, with the search marked `optional`, because a model that books directly from an unambiguous request isn’t wrong. The `assertions` arrays come in a moment. They are the lesson of the first run.

`webmcp-evals` can run a suite like this in several ways. Its `local` mode sends static tool schemas to a model, without a browser. Its `browser` mode runs the model against tools on a live page through Puppeteer. Its `smoke` mode needs no model at all: it executes the expected calls directly against the page, which makes it a deterministic check that the suite and the page still agree. And its `simulate` mode lets a second model play the user over several turns, then checks the final page with DOM assertions, a judge model or both.[^ch14-25] The README is very clear about what to rely on: conversations driven by a simulated user “remain non-deterministic, so keep `smoke` as the fully deterministic, API-key-free CI signal”.[^ch14-25]

### A minimal runner

To show what happens inside such a tool, and to have something you can run against any model with an OpenAI-compatible endpoint, the companion repository has a small runner of its own. It reads the same `evals.json` format, executes calls over the driver from Listing 14.3 and scores the results. Listing 14.6 is the argument matcher. It deliberately follows the semantics of `webmcp-evals`’ own matcher: objects match as subsets, so a model that adds an extra field isn’t penalized, arrays match strictly by position, and an object whose keys all start with `$` is a constraint.[^ch14-26]

**Listing 14.6** `chapters/14-testing-debugging-evals/evals/matcher.js` — matching expected arguments

```js
// Argument matching for evals.json suites, with the semantics of
// webmcp-evals' matcher: objects match as subsets, arrays match strictly,
// and an object whose keys all start with "$" is a constraint.
export function matchesArgument(expected, actual) {
  if (isConstraint(expected)) return matchesConstraint(expected, actual);
  if (expected === actual) return true;
  if (typeof expected !== 'object' || expected === null ||
      typeof actual !== 'object' || actual === null) return false;
  if (Array.isArray(expected) !== Array.isArray(actual)) return false;
  if (Array.isArray(expected)) {
    return expected.length === actual.length &&
           expected.every((e, i) => matchesArgument(e, actual[i]));
  }
  return Object.keys(expected).every((key) =>
    Object.hasOwn(actual, key) && matchesArgument(expected[key], actual[key]));
}

const isConstraint = (v) => typeof v === 'object' && v !== null && !Array.isArray(v) &&
  Object.keys(v).length > 0 && Object.keys(v).every((k) => k.startsWith('$'));

function matchesConstraint(c, actual) {
  const num = typeof actual === 'number';
  const str = typeof actual === 'string';
  return Object.entries(c).every(([op, value]) => {
    switch (op) {
      case '$pattern':  return str && new RegExp(value).test(actual);
      case '$contains': return str && actual.includes(value);
      case '$gt':  return num && actual > value;
      case '$gte': return num && actual >= value;
      case '$lt':  return num && actual < value;
      case '$lte': return num && actual <= value;
      case '$type':
        if (value === 'array') return Array.isArray(actual);
        if (value === 'null') return actual === null;
        if (value === 'object') return typeof actual === 'object' && actual !== null && !Array.isArray(actual);
        return typeof actual === value;
      case '$any':  return true;          // presence was checked by the caller
      default: throw new Error(`Unknown constraint ${op}`);
    }
  });
}
```

Listing 14.7 is the runner. For each case and each run it opens a fresh page, asks the agent for its next call, executes it, feeds the result back and repeats until the agent stops calling tools or runs out of steps. Then it scores the *trajectory* (the ordered list of calls) against `expectedCall` and finally checks the page.

**Listing 14.7** `chapters/14-testing-debugging-evals/evals/run-evals.js` — running a suite against a live page

```js
// Run an evals.json suite against a live page: an agent proposes tool calls,
// the page executes them over CDP, and the trajectory is scored.
import { matchesArgument } from './matcher.js';

export async function runSuite({ suite, openPage, agent, runs = 5, maxSteps = 6 }) {
  const report = [];
  for (const testCase of suite) {
    const result = { name: testCase.name, runs, passed: 0, failures: [] };
    for (let run = 0; run < runs; run++) {
      const { page, webmcp, close } = await openPage();    // a fresh page every run
      const trajectory = [];
      let verdict;
      try {
        const messages = [...testCase.messages];
        for (let step = 0; step < maxSteps; step++) {
          const tools = [...webmcp.tools.values()];
          const { call } = await agent.next({ messages, tools });
          if (!call) break;                                 // the agent has answered
          const reply = await webmcp.invoke(call.functionName, call.arguments);
          trajectory.push({ ...call, status: reply.status, output: reply.output });
          messages.push({ role: 'tool', name: call.functionName, call,
                          content: JSON.stringify(reply.output ?? reply.errorText ?? null) });
        }
        verdict = scoreTrajectory(testCase.expectedCall, trajectory);
        if (verdict.ok) verdict = await checkPage(page, testCase.assertions ?? []);
      } finally {
        await close();
      }
      if (verdict.ok) result.passed++; else result.failures.push(verdict.reason);
    }
    report.push({ ...result, passRate: result.passed / runs });
  }
  return report;
}

// Expected calls must appear in order. Optional ones may be missing.
// Extra calls in between are allowed: agents often look before they leap.
export function scoreTrajectory(expected, actual) {
  let from = 0;
  for (const exp of expected) {
    const at = actual.findIndex((a, i) => i >= from &&
      a.functionName === exp.functionName && matchesArgument(exp.arguments, a.arguments));
    if (at === -1) {
      if (exp.optional) continue;
      const got = actual.map((a) => `${a.functionName}(${JSON.stringify(a.arguments)})`);
      return { ok: false,
               reason: `expected ${exp.functionName}; got ${got.join(' → ') || 'no calls'}` };
    }
    from = at + 1;
  }
  return { ok: true };
}

// The right calls are not enough: did the page end up where the user wanted?
// Same shape as webmcp-evals' DOM assertions: one expectation per assertion.
async function checkPage(page, assertions) {
  for (const { selector, expect } of assertions) {
    const [key, want] = Object.entries(expect)[0];
    const seen = await page.$$eval(selector, (els) => ({
      exists: els.length > 0, count: els.length, text: els[0]?.textContent.trim() ?? null }));
    if (!matchesArgument(want, seen[key]))
      return { ok: false, reason: `${selector}: expected ${key} ${JSON.stringify(want)}, saw ${JSON.stringify(seen[key])}` };
  }
  return { ok: true };
}
```

The agent is anything with a `next({ messages, tools })` method that returns `{ call }` or `{ call: null }`. The repository has three of them. Two are scripted stand-ins with no model behind them: a “careful” agent that does what a good agent should, and a “sloppy” one that makes two classic mistakes, a European date format and forgetting the children. They exist to test the runner itself, and `tests/evals.test.js` checks that the careful one passes, the sloppy one fails with a readable reason, and the matcher and scorer behave as described. The third, `evals/chat-agent.js`, turns the page’s tools into function definitions for any OpenAI-compatible Chat Completions endpoint, configured through environment variables, so you can run `node evals/run.js --agent=chat --runs=5` against whichever model you want to measure.

If you built Chapter 9’s Test Agent, you already have an agent of the same kind that lives *inside* the page: `createTestAgent()` with a `scripted()` planner lists the tools with `getTools()`, runs each step with `executeTool()` and keeps a transcript. The companion repository runs it, unchanged, against the same Fjord Table booking view in `tests/test-agent.test.js`. A two-step script searches and then books the first slot, and the test plays the guest who confirms (the result is `booked`) or cancels (the result is `cancelled_by_user` and nothing is booked). The runner in this chapter stands outside the page, over the protocol, because that is where browser agents stand and because it scores every case the same way. The Test Agent stays the quickest way to script a flow during development, and a second check that your tools behave the same for an in-page caller (Chapter 7).

### What the first run taught us

The first version of Listing 14.5 had no `assertions`, and its third case asked for 17:00, not 17:30. We ran it five times against one hosted model (OpenAI’s `gpt-6-sol`, through its Chat Completions API, with reasoning turned off because that endpoint doesn’t accept function tools with reasoning enabled for this model) on 14 October 2026. The first two cases passed five times out of five. The third failed all five times, and always the same way: the model searched for a table for five at 17:00 and then stopped without booking.

The model’s final message explained why: “There’s no 17:00 table for five on Saturday 28 November. The earliest available is **17:30**. Would you like me to open the booking form for that time?” Fjord Table’s demo backend opens at 17:00, but for that date and party size it had nothing before 17:30. The model was right. The eval was wrong.

Then we noticed something worse. The scripted “careful” agent had passed that same case! It had called `book_table` with exactly the expected arguments, Fjord Table had refused with `SLOT_UNAVAILABLE`, and the scorer, which only compared calls, counted it as a success. A trajectory can be perfect, and the user can still end up with nothing.

Both problems have the same fix: check the outcome as well as the calls. `webmcp-evals` does this in its `simulate` mode with DOM assertions, deterministic checks against the final page, evaluated once after the conversation ends.[^ch14-25] Listing 14.7’s `checkPage()` borrows that shape: a CSS selector and one expectation (`exists`, `count` or `text`), with the same constraint operators as the arguments. The second case now requires the confirmation banner to read “Booked: FT-…”, and the third requires exactly one entry in the user’s list of bookings. A new test in `tests/evals.test.js` runs the careful agent against a page where the simulated person cancels every confirmation, and checks that both booking cases now fail with a message that names the selector.

With the third case corrected to 17:30 and the assertions in place, the same model passed all three cases five times out of five, 15 runs in total. The raw reports of both runs are in the repository under `evals/results/`, each one stamped with the model, the Chromium build and the date.

Read those numbers for what they are. Five runs of three cases against one model on one day is a smoke test. Call it a measurement and you fool yourself. It tells you that the suite works and the descriptions aren’t obviously broken. It does not tell you that 100 percent of real conversations will succeed.

### Designing suites that keep telling you something

A few habits make the difference between an eval suite that guides your work and one that only produces green ticks.

**Write cases from user language, not from your schema.** Real requests contain “tomorrow”, “around seven”, “me and my partner plus the twins”. If every case already says `2026-11-20` and `partySize 2`, you are testing the model’s ability to copy. Mix direct requests with ambiguous ones, as Chrome’s evals page suggests.[^ch14-24]

**Check outcomes, not only calls.** The 17:00 case is the reason. Where the page shows the result of an action, assert on the page. Where it doesn’t, assert on the tool’s returned `status`.

**Include cases where the right answer is not to act.** A request for fifteen people is outside `book_table`’s range of 1 to 12, and the tool’s own error message tells the agent to suggest calling the restaurant. A good suite checks that the agent relays that instead of booking two tables. Neither the `evals.json` format nor the runner here has a first-class way to say “expect no call”, so a `simulate` case with a judge model and prose success criteria is the closer fit.[^ch14-25]

**Test the failure in the middle of a chain.** Chrome’s evals page has a nice example: a coupon tool fails halfway through a pizza order, and the agent happily completes checkout at full price. You don’t need a model to set that up. Bring the page to the state just before the failing step with direct calls, then evaluate only the next decision.[^ch14-24]

**Run each case many times and report a rate.** One pass proves little, and one failure proves little more. Pick a run count you can afford, keep it fixed and track the pass rate per case over time.

**Run the same suite across models.** Your tools will be called by whatever model sits behind the user’s browser agent, and you won’t get to choose it. Running the suite against two or three models of different sizes, including a small on-device model if you can, tells you how much your descriptions depend on a clever caller. Chapter 5’s advice about descriptions and schemas becomes measurable here.

**Treat failing cases as bugs in either place.** Sometimes the model is wrong and your description needs to be clearer. Sometimes, as with 17:00, the eval is wrong. Read the transcript before changing anything.

**Table 14.3 — Where each layer runs**

| When | What to run | Cost |
|---|---|---|
| Every save or commit | Unit tests (Listing 14.2); browser tests with the mock | Seconds, free |
| Every pull request | Browser and protocol tests in Chromium with WebMCPTesting (Listing 14.4); the eval harness with scripted agents, Chapter 9’s Test Agent with a scripted planner, or `webmcp-evals smoke` | A minute or two, free |
| Nightly, or when descriptions change | The eval suite against two or three real models, several runs each | Minutes, costs tokens |
| Before a release | Multi-turn simulations with DOM assertions and a judge model; a manual session with one of Chrome’s two agent extensions | Longer, costs tokens and attention |
| Continuously, in production | Real-user measurement (Listing 14.8) | Small, ongoing |

## Layer 5: real-user measurement

Evals tell you whether models *can* use your tools. Only production tells you whether they *do*: which tools they reach for, how often a call comes back with an error the agent has to recover from, and how long users wait. Chrome’s guide makes the same point. Role-playing is great for a first prototype, but in production you should add real-world telemetry, analyze the interaction logs to find where agents struggle or deviate from the expected paths, and use what you learn to keep updating your evals and tool definitions.[^ch14-1]

And here WebMCP makes life easier than measuring agents usually is. An agent that drives your page by clicking looks almost exactly like a person, so analytics can only guess at it. An agent that uses your tools calls your code, so you know exactly when that happens and what came of it.

### Wrapping `execute`

Listing 14.8 wraps a tool so that every call reports one small event: which tool, how it ended, the result’s code when it fell short, and how many milliseconds it took. A call that returned is recorded as `ok`, or under its Chapter 11 status when it returned `error`, `refused`, `needs_input` or `cancelled_by_user` (a failure returned as a value, such as `refused` with `OUT_OF_STOCK`). A call that never returned is `aborted` (the caller gave up) or `threw` (a bug). Chapter 16’s `measure.ts` uses the same seven words.

**Listing 14.8** `chapters/14-testing-debugging-evals/instrument-tool.js` — measuring real tool calls without recording their contents

```js
// Real-user measurement for WebMCP tools: wrap execute() to record how each
// call ended and how long it took. No inputs or outputs leave the page.

// Chapter 11's statuses for a call that returned without doing what was asked.
const FELL_SHORT = ['error', 'refused', 'needs_input', 'cancelled_by_user'];

export function instrumentTool(tool, report) {
  const execute = tool.execute;
  return {
    ...tool,
    async execute(input, options) {
      const started = performance.now();
      const event = { tool: tool.name, outcome: 'ok', page: location.pathname };
      try {
        const result = await execute.call(tool, input, options);
        if (FELL_SHORT.includes(result?.status))           // a failure returned as a value
          Object.assign(event, { outcome: result.status, code: result.code ?? null });
        return result;
      } catch (err) {
        event.outcome = options.signal.aborted ? 'aborted' : 'threw';
        event.code = err?.name ?? 'Error';
        throw err;
      } finally {
        event.ms = Math.round(performance.now() - started);
        report(event);
      }
    }
  };
}

// One way to report: batch events and send them when the page is hidden.
export function beaconReporter(url) {
  const queue = [];
  addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && queue.length)
      navigator.sendBeacon(url, JSON.stringify(queue.splice(0)));
  });
  return (event) => queue.push({ ...event, at: Date.now() });
}
```

Registering an instrumented tool is a one-word change: `registerTool(instrumentTool(tool, report), { signal })`. The wrapper keeps the tool’s name, description, schema and annotations, so agents see exactly the same tool. Because every tool in this book follows Chapter 11’s result convention, one rule reads them all: a domain word such as Fjord Table’s `booked` counts as `ok`, and the four statuses for a call that fell short are recorded as they are, with their `code`. A site with its own result shape would change only the `FELL_SHORT` check.

`beaconReporter()` batches events and sends them with `navigator.sendBeacon()` when the page is hidden. The Beacon API exists for exactly this job: delivering analytics without blocking the page, including when the user is leaving.[^ch14-27]

The test for this listing, `tests/rum.test.js`, registers instrumented Trailhead tools on a test page and runs a successful search, an out-of-stock `add_to_cart`, an `add_to_cart` with a quantity of 0, and a slow search that the caller aborts after 100 milliseconds. It checks that the events read `ok`, `refused` with code `OUT_OF_STOCK`, `error` with code `INVALID_ARGUMENT` and `aborted`, and that the search term never appears in any event. It passes with the mock and with Chromium 156. Against Chromium it also checks that `toolactivated` fired once for each call, in order.

### What to record, and what not to

Notice what the wrapper leaves out: the input and the output. Tool inputs are whatever the user told their agent, often in their own words. Fjord Table’s `notes` field exists to carry allergies, and a booking carries names and dates. The specification’s privacy section warns about tools that ask for more than they need,[^ch14-28] and the same discipline applies to what you log about a call. The outcome, the error code and the duration are enough to answer the questions that matter.

- **Which tools are used, and how often?** A tool no agent calls is either badly described or not needed.
- **How often does each tool return a recoverable failure, and with which code?** A high rate of `error` with `INVALID_ARGUMENT` on one tool almost always means its schema or description misleads models. Turn the most common bad inputs into new eval cases.
- **How often are calls aborted?** Frequent aborts on a slow tool mean that agents, or users, give up waiting.
- **How long do calls take?** For a consequential tool, the duration includes the time the person spent looking at your confirmation dialog, which is worth tracking on its own.
- **What happens after an agent call?** Joining tool events with your existing funnel (did a search lead to a booking, a cart to a checkout?) is the start of measuring agent-driven conversion, which Chapter 16 picks up.

The page can also count activations without wrapping anything, by listening for `toolactivated` on `document.modelContext`.[^ch14-29] That is a reasonable way to count calls from code you don’t control, but it only tells you that a call started. The wrapper tells you how it ended.

> **Still in flux:** *Knowing who called.* Nothing in the 27 October 2026 draft tells your `execute` callback which agent is calling, or whether the caller is a browser agent, an extension or an in-page agent from another frame.[^ch14-2] Until that changes, your measurements count calls. Callers stay anonymous. Don’t try to infer the agent from the user agent string or from timing. You will be wrong often enough to mislead yourself.

## Sending what you learn back

WebMCP is in an origin trial so that its designers can learn from sites like yours. Almost everything in this chapter produces findings that are useful to them: a behaviour that differs from the specification, a DevTools gap, an eval that shows models misreading a pattern the specification encourages. The channels are specific, and using the right one makes it far more likely that your report leads to a change.

**Table 14.4 — Where to send what**

| What you found | Where it goes |
|---|---|
| The API shape itself: a missing feature, a confusing name, an unclear algorithm | An issue on the explainer and specification repository, `webmachinelearning/webmcp`[^ch14-30] |
| Chrome behaving differently from the specification, or a crash | A Chromium bug, component `Blink>Agentic Platform>WebMCP`[^ch14-30][^ch14-31] |
| Feedback on Chrome’s trial and early access to changes | Chrome’s early preview program and its mailing list[^ch14-30] |
| Feedback on Edge’s trial | Edge’s trial page and the surveys Microsoft sends to registered participants[^ch14-32] |
| A behaviour that should be tested in every browser | A test in the `webmcp/` directory of web-platform-tests[^ch14-19] |

Commenting on an issue is open to anyone. Making substantive contributions to the specification itself, such as pull requests with normative text, requires joining the W3C Web Machine Learning Community Group and agreeing to its contributor license agreement.[^ch14-33] (I’m a member of that group myself.)

A good report has the same parts wherever it goes: the browser and its version, the flag or trial token, a minimal page that shows the problem, what you expected with a link to the specification text that says so, and what you observed. For browser behaviour, the best minimal page is a WPT-style test. Issue #361 is a good model to copy: it names the spec text, the Chrome versions and the WPT assertions that disagree, and it got an editor’s answer within three days.[^ch14-15] Here is what a report of one of this chapter’s own observations could say:

```text
Chromium 156.0.8078.4, --enable-features=WebMCPTesting.
When a tool is invoked through WebMCP.invokeTool or executeTool(), the
synchronous part of an async execute callback runs before a toolactivated
listener on document.modelContext. The tool execute steps fire toolactivated
before invoking the callback (link to the spec). Test page attached: it logs
the order of the two.
```

Reports like this are short, can be checked in a minute and point at exactly one sentence of the specification. They are also what turns a team’s private test suite into something that improves the platform for everyone else.

## Chapter summary

- A WebMCP tool has two kinds of correctness: the code does what it promises, and models can work out how to use it. The first is tested with ordinary deterministic tests, the second with evals.
- Chrome DevTools has a WebMCP pane in the Application panel that lists available tools, logs every call with its input, output and status, and lets you run a tool by hand. Edge 149 includes the same Chromium feature. The Model Context Tool Inspector, the Example Agentic Chrome Extension and Chrome DevTools for agents (`chrome-devtools-mcp` 1.12.0, `--categoryExperimentalWebmcp`) put a model in front of your tools during development.
- The `debugging` annotation, available from Chrome 156 and defined in the 27 October 2026 draft, marks tools meant for developer tooling. It is a hint, not access control.
- Write tools as data, built by factories that take their dependencies as arguments (Chrome’s “share the application service”), and unit-test `execute` directly in Node. Test every input the schema forbids, because the browser doesn’t validate input against `inputSchema`. Issue #92 on that question is still open, with October comments in favour of required, browser-validated schemas. Add “time travel” sequences and pin the spec revision, browser, agent and model of every run.
- Browser contract tests should run against both a mock and Chromium with WebMCPTesting, and should assert on the result shapes your page controls, not on how the browser wraps strings, `undefined` and exceptions. That is where Chromium 156 and the draft differ, where an editor ruled for the specification on 26 October (issue #361), and where Chromium’s main branch already switched to specific `DOMException` types for Chrome 158.
- The web-platform-tests `webmcp/` directory (51 imperative and 25 declarative test files on 2 November 2026) is both the browsers’ contract and a precise reference, but it can be wrong too. A WPT-style test page is the best bug report.
- The experimental `WebMCP` domain of the DevTools Protocol, unchanged since October, lets a test call tools the way a browser agent does, cancel calls, and read results and exceptions. Combined with Playwright, it tests a consequential flow end to end, including the person’s click in your own dialog.
- Evals score a model’s tool calls, and should also score the outcome. The first run of Fjord Table’s suite found a broken case (the model was fine), and showed that a perfect-looking trajectory can still book nothing. Run cases many times, across several models, test mid-chain failures, and treat five runs as a smoke test.
- In production, wrap `execute` to record each call’s outcome and duration, never its content. The `code` of each `error` or `refused` result is the most useful signal you have for improving descriptions and schemas.
- Send API feedback to the `webmachinelearning/webmcp` issues, Chrome bugs to the `Blink>Agentic Platform>WebMCP` component, and tests to web-platform-tests.

Chapter 15 steps back from your own code to the platform it runs on: which browsers implement WebMCP, what the origin trials promise and what they don’t, and how a Community Group draft does or doesn’t become a standard.

## Notes

[^ch14-1]: Chrome for Developers, “Build your user’s agentic workflows with WebMCP tools” (André Cipriani Bandarra and Maxim Salnikov, published 26 August 2026, updated 30 October 2026, retrieved November 2026), sections “Evaluate your tools” (including “Test ‘time travel’ states” and “Pin versions”) and “Deploy to production”. <https://developer.chrome.com/docs/ai/webmcp/build-tools>
[^ch14-2]: WebMCP, Draft Community Group Report, 27 October 2026, header (four editors, test suite link), “Status of this document” (“not a W3C Standard nor … on the W3C Standards Track”) and §6, Security and Privacy Considerations (agent-ecosystem text added by pull request #334, merged 20 October 2026: “a malicious site can omit or misrepresent those hints”). <https://webmachinelearning.github.io/webmcp/>
[^ch14-3]: Chrome for Developers, “WebMCP” (published 18 May 2026, updated 7 October 2026, retrieved November 2026), sections on local testing (the `chrome://flags/#enable-webmcp-testing` flag), the Example Agentic Chrome Extension (“always trusts WebMCP annotations”), the Model Context Tool Inspector with Gemini or the Prompt API (`chrome://flags/#prompt-api-tool-use`), and the caution that Chrome extensions can query and execute WebMCP tools. <https://developer.chrome.com/docs/ai/webmcp>
[^ch14-4]: Chrome DevTools documentation, “Debug WebMCP tools” (no date shown on the page, retrieved November 2026), sections “Open the WebMCP pane”, “Interface overview”, “Test tools manually”, “Troubleshoot integration issues” and “Command-line flags”. <https://developer.chrome.com/docs/devtools/application/webmcp>
[^ch14-5]: Microsoft Edge documentation, “What’s new in DevTools (Microsoft Edge 149)” (dated 4 June 2026, last updated 2 September 2026), listing “WebMCP debugging” among the updates from the Chromium project. <https://learn.microsoft.com/en-us/microsoft-edge/devtools/whats-new/149>
[^ch14-6]: webmachinelearning/webmcp issue #92, “Who owns the validation layer?” (opened 17 February 2026, open on 2 November 2026), comments by Mark Foltz (13 October 2026), François Beaufort (14 October), Samuel Dallstream (16 October) and Johann Hofmann (30 October). <https://github.com/webmachinelearning/webmcp/issues/92>
[^ch14-7]: GoogleChromeLabs/webmcp-tools, README (re-read 2 November 2026, latest commit 29 October 2026): the Model Context Tool Inspector, WebMCP Evals, WebMCP Skills and the WebMCP polyfill. <https://github.com/GoogleChromeLabs/webmcp-tools>
[^ch14-8]: chrome-devtools-mcp on npm, version 1.12.0 (published 22 October 2026, the latest on 2 November 2026), and its GitHub releases. <https://github.com/ChromeDevTools/chrome-devtools-mcp>
[^ch14-9]: ChromeDevTools/chrome-devtools-mcp, release notes for v1.11.0 (15 October 2026): “surface WebMCP tool exceptions in execute_webmcp_tool”, “reject JSON arrays as 3p and WebMCP tool params”, “support debugging WebMCP tools in third-party developer tools”. <https://github.com/ChromeDevTools/chrome-devtools-mcp/releases>
[^ch14-10]: Chrome for Developers, “Imperative API” (published 18 May 2026, updated 16 October 2026, retrieved November 2026), section on annotations: `readOnlyHint`, `untrustedContentHint`, `consequentialHint` and `debugging` (“available from Chrome 156”). <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
[^ch14-11]: WebMCP specification (27 October 2026), §4.2.1, the `ToolAnnotations` dictionary (`readOnlyHint`, `untrustedContentHint`, `consequentialHint`, `debugging`, each defaulting to `false`), the `debugging` member was added by pull request #253, merged 17 September 2026. <https://webmachinelearning.github.io/webmcp/#dictdef-toolannotations>
[^ch14-12]: Chrome for Developers, “WebMCP best practices” (Alexandra Klepper, Maxim Salnikov and François Beaufort, published 18 May 2026, updated 30 October 2026, retrieved November 2026), section “Enforce architectural constraints”: “Register tools all at once”, “Share the application service”, “Wait for the UI”, “Establish explicit commit points”. <https://developer.chrome.com/docs/ai/webmcp/best-practices>
[^ch14-13]: Node.js documentation, “Test runner” (`node:test`, stable since Node.js 20.0.0). <https://nodejs.org/api/test.html>
[^ch14-14]: WebMCP specification (27 October 2026), §3.1, the “tool execute steps” (input that is not an object is rejected as invalid input, `toolactivated` is fired before the execute callback is invoked), §3, the table of tool execution errors, and the `executeTool()` IDL (`Promise<DOMString>`). <https://webmachinelearning.github.io/webmcp/#tool-execute-steps>
[^ch14-15]: webmachinelearning/webmcp issue #361, “executeTool(): spec JSON-encodes strings and rejects undefined, Chrome and WPT do neither” (opened 23 October 2026, tested in Chrome 156.0.8078.48 and 158.0.8119.0), with François Beaufort’s reply of 26 October 2026. Open on 2 November 2026. <https://github.com/webmachinelearning/webmcp/issues/361>
[^ch14-16]: webmaxru/webmcp-book-demos, `fjord-table/tests/run-tests.mjs` and `fjord-table/README.md` (“Chromium 156 vs the draft”), run with `npm run test:chrome` on 14 and 15 October 2026 and again on 2 November 2026. <https://github.com/webmaxru/webmcp-book-demos/tree/main/fjord-table>
[^ch14-17]: webmachinelearning/webmcp pull request #339, “Replace UnknownError with specific DOMException types.” (merged 8 October 2026). <https://github.com/webmachinelearning/webmcp/pull/339>
[^ch14-18]: Chromium changes 8546218, “[WebMCP] Reject executeTool() with granular DOMExceptions” (landed 16 October 2026, Cr-Commit-Position #1720407), and 8510757, “[3/N] WebMCP: Introduce the `Tool` interface object” (landed 15 October 2026, #1719188), both exported to web-platform-tests (wpt commits 22b4a4dd and 15e7837b). Chrome 157 branched at #1717349 and Chrome 158 at #1727472 (Chromium Dash milestones, read 2 November 2026). <https://chromium-review.googlesource.com/c/chromium/src/+/8546218>, <https://chromium-review.googlesource.com/c/chromium/src/+/8510757>, <https://chromiumdash.appspot.com/schedule>
[^ch14-19]: web-platform-tests, `webmcp/` directory (read 2 November 2026): `META.yml`, `idlharness.https.window.js`, `tool-activated-event.https.html`, `tool-cancel-event.https.html`, `declarative/` (25 HTML test files) and `imperative/` (51 HTML test files, 49 on 15 October 2026). <https://github.com/web-platform-tests/wpt/tree/master/webmcp>
[^ch14-20]: web-platform-tests, `webmcp/tool-cancel-event.https.html`, the comment inside the final `promise_test`, above `executeAndCancelTool`. <https://github.com/web-platform-tests/wpt/blob/master/webmcp/tool-cancel-event.https.html>
[^ch14-21]: Chrome DevTools Protocol, tip-of-tree, `WebMCP` domain (experimental): types `Annotation`, `InvocationStatus`, `Tool`, `RemovedTool`, commands `enable`, `disable`, `invokeTool`, `cancelInvocation`, events `toolsAdded`, `toolsRemoved`, `toolInvoked`, `toolResponded`. Definition read from `json/browser_protocol.json` in ChromeDevTools/devtools-protocol on 15 October 2026 and again on 2 November 2026 (protocol roll of 31 October 2026, no change to the domain). <https://chromedevtools.github.io/devtools-protocol/tot/WebMCP/>
[^ch14-22]: Playwright documentation, “CDPSession” (`page.context().newCDPSession(page)`, `send()`, `on()`). <https://playwright.dev/docs/api/class-cdpsession>
[^ch14-23]: webmachinelearning/webmcp pull request #338, “Remove declarative API from spec” (merged 8 October 2026), the declarative API now lives in `declarative-api-explainer.md`. <https://github.com/webmachinelearning/webmcp/pull/338>
[^ch14-24]: Chrome for Developers, “Test WebMCP with Evals” (Kasper Kulikowski, published 19 May 2026, updated 28 May 2026, retrieved November 2026): failure modes, testing tools in isolation, `expectedCall` with `ordered` and `unordered` groups, direct and ambiguous queries, mid-chain failures. <https://developer.chrome.com/docs/ai/webmcp/evals>
[^ch14-25]: GoogleChromeLabs/webmcp-tools, `webmcp-evals/README.md` (read 15 October 2026): commands `local`, `browser`, `smoke`, `simulate` and `analyze`, the `evals.json` and `simulations.json` schemas, argument matching operators, DOM assertions. Published on npm as `webmcp-evals` 0.0.4 (28 August 2026, still the latest version on 2 November 2026). <https://github.com/GoogleChromeLabs/webmcp-tools/tree/main/webmcp-evals>
[^ch14-26]: GoogleChromeLabs/webmcp-tools, `webmcp-evals/src/matcher.ts` (`matchesArgument`, subset matching for objects, strict matching for arrays, `$`-prefixed constraint objects). <https://github.com/GoogleChromeLabs/webmcp-tools/blob/main/webmcp-evals/src/matcher.ts>
[^ch14-27]: W3C, “Beacon” (Editor’s Draft, 11 March 2026), the `sendBeacon()` method and its use for analytics when the page’s visibility state becomes hidden. <https://w3c.github.io/beacon/>
[^ch14-28]: WebMCP specification (27 October 2026), §6, Security and Privacy Considerations, including §6.3.3, “Privacy Leakage Through Over-Parameterization”. <https://webmachinelearning.github.io/webmcp/#privacy-leakage-over-parameterization>
[^ch14-29]: WebMCP specification (27 October 2026), §4.3, event handlers on `ModelContext` and the `ToolActivatedEvent` interface. <https://webmachinelearning.github.io/webmcp/#tool-activated-event>
[^ch14-30]: Chrome for Developers blog, “Join the WebMCP origin trial” (Alexandra Klepper, 9 June 2026), section “Share your feedback”: issues on the WebMCP explainer repository for the API shape, Chromium bugs for Chrome’s implementation, and the early preview program. <https://developer.chrome.com/blog/ai-webmcp-origin-trial>
[^ch14-31]: Chrome Platform Status, “WebMCP” (feature 5117755740913664, updated 28 September 2026): Blink component `Blink>Agentic Platform>WebMCP`, tracking bug crbug.com/445637567. <https://chromestatus.com/feature/5117755740913664>
[^ch14-32]: Microsoft Edge Origin Trials, “WebMCP” (trial expiration 30 March 2027), terms of use on feedback surveys. <https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a>
[^ch14-33]: webmachinelearning/webmcp, `CONTRIBUTING.md` (substantive contributions require joining the W3C Web Machine Learning Community Group under the W3C Community Contributor License Agreement). <https://github.com/webmachinelearning/webmcp/blob/main/CONTRIBUTING.md>

[^ch14-output-schema]: WebMCP PR #254 merged 2 November 2026; issue #92 remains open on validation; GoogleChromeLabs/webmcp-extension PR #98 shows host-side result checks. The task-supplied Chrome build is 159.0.8140.0; the book’s Playwright suites use Chromium 156 and were not run on 159. <https://github.com/webmachinelearning/webmcp/pull/254> <https://github.com/webmachinelearning/webmcp/issues/92> <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
