# Chapter 10: WebMCP in Frameworks

> *“Register tools when they’re useful in a certain page state, then unregister when the tool is no longer usable.”*
>
> — Chrome for Developers, “WebMCP best practices”[^ch10-1]

## From a page to an app

Fjord Table is a page. Its tools live in a few module scripts, its booking view opens and closes, and Listing 5.5 registered `book_table` only while that view was on screen. That’s about as much lifecycle as a small site has.

Most of the web you’ll make agent-ready doesn’t look like that. It looks like Trailhead: a single-page store written in React, where “the page” is a tree of components that mount and unmount while the person searches, compares and checks out. State lives in stores that several components share, and the URL changes without a document ever reloading. In that world `registerTool()` raises questions Fjord Table never had to answer. Which component owns a tool? What happens to the tool when that component unmounts? What does React’s development mode do to code that registers something in an effect? And when an agent is halfway through a checkout and the person presses Back, who is responsible for the dialog that is still waiting for an answer?

The API doesn’t change in a framework. `document.modelContext` is still one object per document, tools are still registered with a dictionary and removed by aborting a signal, and every call still arrives with its own cancellation signal.[^ch10-2] What changes is who calls those methods, and when. This chapter gets the “who” and the “when” right. It ties registration to component and dependency-injection lifecycles, keeps tools thin over existing application logic, lets the set of tools follow the route, unregisters without breaking calls that are already running, and keeps the agent and the person in step about what changed.

The main example is Trailhead, the outdoor-gear store that runs through Parts III to VI. Table 10.1 lists the tools it ends this chapter with, and where each one lives.

**Table 10.1 — Trailhead’s WebMCP tools at the end of Chapter 10**

| Tool | Registered by | Lifetime | Annotations |
|---|---|---|---|
| `search_products` | `<AgentTools>` in the layout | whole app | `readOnlyHint` |
| `compare_products` | `<AgentTools>` in the layout | whole app | `readOnlyHint` |
| `add_to_cart` | `<AgentTools>` in the layout | whole app | none |
| `get_cart` | `<AgentTools>` in the layout | whole app | `readOnlyHint` |
| `checkout` | `<CartPage>` | while `/cart` is open and the cart isn’t empty | `consequentialHint` |

The React code builds with Vite 8.3.4 and TypeScript 7.0.2 against React 19.3.1, React Router 8.4.0 and `usewebmcp` 6.0.3. Those were the current versions on npm on 14 October 2026, and on 2 November 2026 they still were.[^ch10-3] Every listing is in the book’s companion repository, together with Playwright tests that run the built app twice: once against a small mock of `document.modelContext`, and once against Chromium 156’s own implementation with the `WebMCPTesting` feature switched on.[^ch10-4] When this chapter says “in Chromium 156”, it means one of those tests. (Chrome 156 reached the Stable channel on 20 October 2026, so the version the tests use is no longer a preview.[^ch10-21])

Later, this chapter looks at Vue briefly, and then leaves React for Angular, which ships its own experimental WebMCP support built on dependency injection and Signal Forms.

## What a framework integration has to do

Before reaching for a library, it helps to see the whole job. A component that offers a tool has to do five things:

1. **Detect support.** Do nothing where `document.modelContext` doesn’t exist, so the component still works as an ordinary UI.
2. **Register on mount and unregister on unmount.** The tool should exist exactly as long as the component that can honour it.
3. **Re-register when what the agent reads changes.** A tool’s name, description and schema are loaded into the model’s context when the agent observes the page. The explainer says that to change them you unregister the tool and register it again, and each step fires a `toolchange` event.[^ch10-5]
4. **Don’t re-register when nothing the agent reads has changed.** Components re-render all the time. If every render produced a new registration, the agent would see a stream of `toolchange` events, and a call could land on a tool that was replaced a moment ago.
5. **Run calls against current state.** When the agent calls the tool, the handler should see the props and state of the latest render, not of the render in which the tool was first registered.

Points 4 and 5 pull against each other. The `execute` function a component defines is a new closure on every render, and it closes over that render’s state. Register that closure once, and calls see stale state. Register every new closure, and you churn. The explainer points at the way out: the browser holds on to whatever function you passed, and as long as the name, description and schema stay accurate, that function can delegate to another one that the application changes over time.[^ch10-5]

Listing 10.1 does all five in about thirty lines. You won’t ship it (the packages in the next section do the same job and more), but it shows exactly what they do for you.

**Listing 10.1** `trailhead-react/src/agent/use-agent-tool.ts` — a minimal hook that ties a tool to a component

```ts
import { useEffect, useLayoutEffect, useRef } from 'react';

export interface AgentTool {
  name: string;
  description: string;
  inputSchema?: object;
  annotations?: WebMCP.ToolAnnotations;
  execute: (input: Record<string, unknown>, options: { signal: AbortSignal }) => unknown;
}

// What a WebMCP hook has to do, in about thirty lines.
export function useAgentTool(tool: AgentTool, enabled = true): void {
  // ① Keep the latest render's tool, so calls see current props and state.
  const latest = useRef(tool);
  useLayoutEffect(() => { latest.current = tool; });

  // ② Re-register only when what the agent reads changes.
  const metadata = JSON.stringify([tool.name, tool.description, tool.inputSchema, tool.annotations]);

  useEffect(() => {
    const modelContext = document.modelContext;
    if (!enabled || !modelContext) return;          // ③ progressive enhancement
    const { name, description, inputSchema, annotations } = latest.current;
    const controller = new AbortController();
    modelContext
      .registerTool(
        { name, description, inputSchema, annotations,
          execute: (input, options) => latest.current.execute(input as Record<string, unknown>, options) },
        { signal: controller.signal },
      )
      .catch((error: unknown) => {
        if (!controller.signal.aborted) console.warn(`registerTool("${name}") failed`, error);
      });
    return () => controller.abort();                // ④ unmount or change: unregister
  }, [metadata, enabled]);
}
```

① A ref holds the tool from the latest render. It’s updated in a layout effect, so it’s current before any passive effect or agent call can read it. The function registered with the browser never changes: it looks up `latest.current.execute` at call time, so every call runs against current state.

② The effect’s dependency is a serialized copy of the agent-facing metadata. A re-render that changes only state leaves that string the same, and nothing is re-registered. A new description produces a new string, and React runs the cleanup (unregister) and then the effect again (register).

③ Without the API the hook does nothing, and the component renders as it always did.

④ The cleanup aborts the registration signal. This is the only way to unregister a tool. The specification has no `unregisterTool()`: aborting the signal passed in the options removes the tool and fires `toolchange`.[^ch10-2]

### What StrictMode does to registration

In development, React’s `<StrictMode>` runs “one extra setup+cleanup cycle in development for every Effect”.[^ch10-6] For Listing 10.1 that means register, abort, register, all in the same tick and with the same name. If unregistration were asynchronous, the second `registerTool()` would hit the first tool and be rejected, because the name is taken.

It isn’t. The specification runs the abort steps synchronously when the signal fires, so the tool leaves the document’s tool map before the next line runs.[^ch10-2] In Chromium 156 the first registration promise rejects with an `AbortError` (“signal is aborted without reason”), the second one resolves, and `getTools()` lists the tool once. That rejection is why the hook ignores errors from a registration whose own signal was aborted: it’s simply the expected result of cleaning up. Trailhead mounts inside `<StrictMode>`, and its tests check that no tool is ever registered twice and that nothing is logged.

### The bug only a real browser caught

The first version of Listing 10.1 copied the metadata out of the serialized string with `JSON.parse()`. It passed every test against the mock and failed against Chromium. The reason is a small one. `JSON.stringify()` turns a missing `inputSchema` into `null`, and Chromium 156 rejects `inputSchema: null` with a `TypeError`: “Failed to read the 'inputSchema' property from 'ModelContextTool': Failed to convert value to 'object'.” An `undefined` member, on the other hand, is simply treated as absent, which is what Web IDL dictionaries do.[^ch10-7] The mock had been more forgiving than the browser. The fix was to read the metadata from the ref instead, and the mock now rejects `null` the way Chromium does. Run your tests against a real implementation as well as a mock. Chapter 14 comes back to this.

### The whole set, or none of it

Since 30 October 2026 Chrome’s best-practices page (I’m one of its co-authors) has a short list of architectural constraints, and the first one is about registration: “The page must expose either the complete tool surface or none of it. Roll back the whole batch on failure instead of leaving half a workflow callable.”[^ch10-1]

A hook per tool doesn’t give you that for free. Each hook registers its own tool, so if one registration fails (a name that is already taken, for example), its siblings stay registered. The raw API makes the batch version easy, though, because one `AbortSignal` can be passed to several `registerTool()` calls. In a quick probe in Chromium 156, two tools registered with the same signal disappeared together when it was aborted. A batch of two in which the second name was already taken got one fulfilled promise and one rejected with an `InvalidStateError`, and aborting the shared signal removed the tool that had made it in. So an all-or-nothing hook is Listing 10.1 with an array: one controller, every registration on its signal, and `controller.abort()` as soon as any of the promises rejects.

Trailhead doesn’t need that. Its four app-wide tools don’t form a workflow that breaks when one of them is missing: search is useful without a cart, and the cart is useful without a comparison. The one step that does depend on the others, `checkout`, lives on its own page with its own lifetime, as the cart page shows later in this chapter. If your tools only make sense together (a wizard with a `start_return` and a `confirm_return`, say), register them as one batch.

## React: two hooks

At the time of the first edition, Chrome’s documentation for the imperative API had a “React support” section that pointed to the `usewebmcp` package, a community hook from the WebMCP-org `npm-packages` repository (the same project behind the MCP-B polyfill and bridges you met in Chapter 9). On 16 October 2026 the page changed. It now says that React “has experimental support for WebMCP using the use-webmcp-tool package”, with a `useWebMCP` hook “tied to your component’s mount and unmount lifecycle” that “also supports conditional tool registration, and automatically normalizes execution results”.[^ch10-8] `use-webmcp-tool` is Chrome’s own hook, published by GoogleChromeLabs, and its README says it is “maintained by Chrome, and will be updated with any spec changes”.[^ch10-11]

So there are two React hooks with the same name, `useWebMCP`, and almost the same configuration. Table 10.2 lists them together with the related packages you’re likely to meet.

**Table 10.2 — React packages for WebMCP on npm, checked on 2 November 2026**

| Package | Version | What it is |
|---|---|---|
| `use-webmcp-tool` | 0.3.0 | Chrome’s own hook (GoogleChromeLabs), the one Chrome’s documentation names since 16 October 2026. Normalizes results to MCP `content` blocks. No runtime dependencies |
| `usewebmcp` | 6.0.3 | Community hook for the core `document.modelContext` contract. JSON Schema input inference, `exposedTo`, no validation, results passed through. Depends on `webmcp-types` |
| `@mcp-b/react-webmcp` | 6.0.3 | Community hook with Standard Schema (for example Zod) validation, `outputSchema`, MCP result formatting, prompts, resources and client hooks |
| `@mcp-b/webmcp-polyfill` | 6.0.3 | A `document.modelContext` implementation for browsers without one, recommended for tests |
| `webmcp-types` | 0.1.10 | The Community Group’s TypeScript definitions (Chapter 5) |

Sources: the npm registry entries for each package, read on 14 October 2026 and again on 2 November 2026. No new versions were published in between.[^ch10-3] [^ch10-9] [^ch10-10] [^ch10-11]

Where do the two hooks really differ? In what happens to your return value. Chrome’s hook turns a returned string into an MCP `content` block, serializes an object or array into a text block, wraps a thrown error (or a returned `Error`) as an `isError` result, and turns `undefined` into an empty `content` list.[^ch10-11] `usewebmcp` hands your return value to the browser untouched, except that `undefined` becomes `null`, because the browser can’t serialize `undefined`.[^ch10-12] Both register on mount, unregister on unmount, support `enabled`, and read the latest `execute` at call time without re-registering.

Trailhead stays on `usewebmcp` in this edition, for three reasons. Its results are exactly the plain objects Chapter 5 described and Chapter 11 designs, with no envelope around them. It infers TypeScript types from the schema, which Listing 10.2 relies on. And it supports `exposedTo`, for the cross-origin case Chapter 7 covers, which Chrome’s hook doesn’t offer. None of these is a verdict on Chrome’s hook. If you prefer `use-webmcp-tool`, the thin-wrapper design in the next section means the switch touches the files that call the hook and nothing else, and the tests that parse results would need to unwrap one `content` block.

> **Still in flux:** All the React integrations are community or experimental code that follows a draft specification. The hook Chrome’s documentation points to changed once already, the day after the text of this book’s first edition was finished. `usewebmcp` moved a whole feature set to another package in its 6.0 release and shipped four releases in the week before 14 October 2026. Pin exact versions, read the changelog before upgrading, and keep your tool logic out of the hook call, so that swapping one hook for another touches a single file.[^ch10-3] [^ch10-8] [^ch10-11]

### Trailhead’s app-wide tools

Listing 10.2 is the component that gives Trailhead its four app-wide tools. It renders nothing. It’s mounted once, in the layout route, so the tools live as long as the app does.

**Listing 10.2** `trailhead-react/src/agent/AgentTools.tsx` — app-wide tools with `useWebMCP`

```tsx
import { useNavigate } from 'react-router';
import { useWebMCP } from 'usewebmcp';
import { addToCartSchema, addToCartTool, getCartTool } from './cart-tools';
import { compareProductsSchema, compareProductsTool } from './compare-products';
import { searchProductsSchema, searchProductsTool } from './search-products';

// App-wide tools. Mounted once in the layout, so they live as long as the app.
export function AgentTools() {
  const navigate = useNavigate();

  useWebMCP({
    name: 'search_products',
    description: 'Search the Trailhead catalog of outdoor gear. Returns matching products with SKU, name, price in NOK, rating and stock status.',
    inputSchema: searchProductsSchema,
    annotations: { readOnlyHint: true },
    execute: searchProductsTool,
  });

  useWebMCP({
    name: 'compare_products',
    description: 'Compare 2 to 4 products side by side by price, rating, weight and stock. Also shows the comparison to the user.',
    inputSchema: compareProductsSchema,
    annotations: { readOnlyHint: true },
    execute: (input) => {
      const result = compareProductsTool(input);
      if (!('error' in result)) navigate(`/compare?skus=${input.skus.join(',')}`);
      return result;
    },
  });

  useWebMCP({
    name: 'add_to_cart',
    description: 'Add a product to the shopping cart by SKU. Returns the updated item count and total.',
    inputSchema: addToCartSchema,
    execute: addToCartTool,
  });

  useWebMCP({
    name: 'get_cart',
    description: 'Read the current shopping cart: lines, item count and total in NOK.',
    annotations: { readOnlyHint: true },
    execute: getCartTool,
  });

  return null;
}
```

Compare it with Listing 10.1, and you’ll see the same contract. The hook registers after React commits the component and aborts the registration when the component unmounts, so you never manage an `AbortController` yourself.[^ch10-13] It re-registers when the serialized metadata (name, title, description, schema, annotations), `enabled` or `exposedTo` changes, and not otherwise. It publishes the latest committed callback with a layout effect, so `compare_products` always calls the current `navigate` function without a new registration.[^ch10-12] And when a registration is rejected, for example because another tool already has the name, it logs one `console.warn` naming the tool and exposes the error as `registrationError`.[^ch10-12]

Two details in the listing deserve a closer look.

**Schema-driven types.** The schemas are imported from modules where they are declared `as const`. With a literal schema, `useWebMCP` infers the type of the handler’s `input` from it, using the `webmcp-types` definitions. That’s why `input.skus.join(',')` in `compare_products` type-checks: TypeScript knows that `skus` is an array of strings.[^ch10-12] The inference is only a type. The package says it plainly: the schema “is registered as metadata”, and “the hook passes runtime input to the handler without validation or transformation”.[^ch10-12] The browser doesn’t validate calls either (Chapter 5), so every handler in Trailhead still checks its input in code.

**No `inputSchema` on `get_cart`.** A tool that takes no input can leave the schema out. Chromium 156 accepts that, and the hook passes the member only when you set it.

## Tools as thin wrappers over one application service

The easiest way to add tools to an existing app is also the worst one: write each tool as a little program of its own. The handler fetches products its own way, keeps its own copy of the cart or (even worse) finds the “Add to cart” button and clicks it. You end up with two apps sharing a page. They disagree about rules, they drift apart with every release, and the agent sees a store that behaves differently from the one the person sees.

The alternative is a strict division of labour. Everything the store does lives in plain modules that know nothing about React or WebMCP. The UI calls them from event handlers, and the tools call the same functions from `execute`. Chrome’s best practices now name this constraint directly: “Share the application service”, keeping the visible UI, the WebMCP tools and the tests “in sync by sharing a single application service for validation, permissions, and side effects”.[^ch10-1] The tool layer is allowed to do only three things: describe the input (the schema), check it (validation), and translate (map the input to a call, and the result to something compact for the model). Figure 10.1 shows the shape.

![Figure 10.1 — One app, two callers. The UI and the agent reach the same functions and the same state. Tool files only describe, check and translate.](images/figure-10-1.png)

Listing 10.3 is `search_products` written that way. It is the whole file.

**Listing 10.3** `trailhead-react/src/agent/search-products.ts` — `search_products` as a thin wrapper over the catalog

```ts
// Agent-facing wrapper: a schema, validation in code, one call into the store's own search, a compact result.
import { CATEGORIES, searchProducts, type Category } from '../catalog';

export const searchProductsSchema = {
  type: 'object',
  properties: {
    query: { type: 'string', description: 'Keywords, for example "down sleeping bag".' },
    category: { type: 'string', enum: CATEGORIES, description: 'Optional product category.' },
    maxPrice: { type: 'number', minimum: 0, description: 'Optional maximum price in NOK.' },
    inStockOnly: { type: 'boolean', description: 'Only return products that are in stock.' },
  },
  required: ['query'],
  additionalProperties: false,
} as const;

export function searchProductsTool({ query, category, maxPrice, inStockOnly }: Record<string, unknown>) {
  if (typeof query !== 'string') return { status: 'error', code: 'INVALID_ARGUMENT', message: 'query must be a string.' };
  if (category !== undefined && !CATEGORIES.includes(category as Category)) {
    return { status: 'error', code: 'INVALID_ARGUMENT', message: `category must be one of: ${CATEGORIES.join(', ')}.` };
  }
  if (maxPrice !== undefined && (typeof maxPrice !== 'number' || maxPrice < 0)) {
    return { status: 'error', code: 'INVALID_ARGUMENT', message: 'maxPrice must be a non-negative number of NOK.' };
  }
  const products = searchProducts({
    query,
    category: category as Category | undefined,
    maxPrice: maxPrice as number | undefined,
    inStockOnly: inStockOnly === true,
  });
  return {
    products: products.map(({ sku, name, price, rating, inStock }) => ({ sku, name, price, rating, inStock })),
  };
}
```

The schema follows Chapter 5’s advice: plain types, an `enum` for the category, a description for every field, `additionalProperties: false`. The validation repeats the schema’s rules in code, because nothing else enforces them, and it returns failures as values the model can act on, in the `{ status: 'error', code, message }` shape Chapter 6 introduced (Chapter 11 completes the set). The real work is one call to `searchProducts()`, the very function the search box on the shop page calls on every keystroke. And the result is trimmed to what an agent needs to choose a product: no weights, no categories, no image URLs.

`compare_products` and `add_to_cart` follow the same pattern in their own files in the repository. `add_to_cart` rejects quantities outside 1–10 as an `error` and returns out-of-stock products as `refused` with the code `OUT_OF_STOCK` (Chapter 11 explains the difference), and then it calls `cartStore.add()`, the same method the “Add to cart” buttons call.

### Shared state with an external store

“The same method” helps only if there is one cart. In a component-based app, the place where the cart lives decides who can reach it. If it lived in `useState` inside `<CartPage>`, a tool registered in the layout couldn’t see it, and it would vanish as soon as the person left the cart page. Trailhead keeps it in a small external store that React subscribes to with `useSyncExternalStore`, the hook React provides “to subscribe to an external store”.[^ch10-14]

**Listing 10.4** `trailhead-react/src/cart-store.ts` — one cart for the buttons and the tools

```ts
import { useSyncExternalStore } from 'react';
import { getProduct, type Price } from './catalog';

export interface CartLine { sku: string; name: string; quantity: number; unitPrice: Price }
export interface Cart { lines: readonly CartLine[]; itemCount: number; total: Price }
export interface Order { orderId: string; total: Price; itemCount: number }

let cart: Cart = { lines: [], itemCount: 0, total: { amount: 0, currency: 'NOK' } };
let lastOrder: Order | null = null;
let nextOrderNumber = 10001;
const listeners = new Set<() => void>();

function commit(lines: CartLine[]): void {
  cart = {
    lines,
    itemCount: lines.reduce((n, l) => n + l.quantity, 0),
    total: { amount: lines.reduce((s, l) => s + l.quantity * l.unitPrice.amount, 0), currency: 'NOK' },
  };
  listeners.forEach((notify) => notify());
}

// One store, two callers: the page's buttons and the agent's tools.
export const cartStore = {
  subscribe(listener: () => void): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  getSnapshot: (): Cart => cart,
  getLastOrder: (): Order | null => lastOrder,

  add(sku: string, quantity: number): Cart {
    const product = getProduct(sku);
    if (!product) throw new Error(`Unknown SKU: ${sku}`);
    const existing = cart.lines.find((l) => l.sku === sku);
    commit(existing
      ? cart.lines.map((l) => (l.sku === sku ? { ...l, quantity: l.quantity + quantity } : l))
      : [...cart.lines, { sku, name: product.name, quantity, unitPrice: product.price }]);
    return cart;
  },

  placeOrder(): Order {
    if (cart.itemCount === 0) throw new Error('The cart is empty.');
    lastOrder = { orderId: `TH-${nextOrderNumber++}`, total: cart.total, itemCount: cart.itemCount };
    commit([]);
    return lastOrder;
  },
};

export function useCart(): Cart {
  return useSyncExternalStore(cartStore.subscribe, cartStore.getSnapshot);
}
```

The store is ordinary TypeScript. `add()` and `placeOrder()` update a snapshot and notify subscribers, and `useCart()` lets any component read the snapshot and re-render when it changes. Because the agent’s `add_to_cart` goes through `cartStore.add()`, the header’s “Cart (2)” updates the moment the tool runs, with no extra code. The tests check both directions: an agent’s `add_to_cart` updates the header, and an item the person adds with a click shows up in the agent’s next `get_cart`.

One more property of this store turns out to matter later. Every change creates a new snapshot object, so the identity of the snapshot is a version number for free. Keep that in mind until the checkout section.

You can use whatever state library your app already has. What matters is that the state a tool needs doesn’t belong to a component that might unmount.

## Routing and per-view tool sets

In a single-page app, a route change replaces components without replacing the document. Tools registered by those components come and go with them, and the browser fires `toolchange` each time. That gives you a natural way to offer view-specific tools: put the hook in the route’s component. Figure 10.2 shows how Trailhead does it, and what the agent sees while the person moves around.

![Figure 10.2 — Tools follow the component tree. Mounting registers a tool, unmounting aborts its signal, and a call that is already running is not cancelled.](images/figure-10-2.png)

Should you, though? Chrome’s best-practices page answers both ways in a few lines. It tells you to “manage tool registration” and to register tools “when they’re useful in a certain page state”, and then it adds: “Reduce complexity: For most applications, static registration should be the default approach.” It also notes that there is no maximum number of tools, but “each tool takes up part of the context window”, and overlapping tools make it harder for the agent to choose.[^ch10-1]

Trailhead follows that advice. Search, compare, add to cart and read the cart make sense on every page, so they are registered once. Only `checkout` is tied to a view, and for a reason that has more to do with consent than with tool counts: an order should be placed from the page where the person can see what they are buying. Listing 10.5 shows the cart page.

**Listing 10.5** `trailhead-react/src/pages/CartPage.tsx` — a view-scoped, consequential tool

```tsx
import { useSyncExternalStore } from 'react';
import { useWebMCP } from 'usewebmcp';
import { cartStore, useCart } from '../cart-store';
import { checkout } from '../checkout';

export function CartPage() {
  const cart = useCart();
  const lastOrder = useSyncExternalStore(cartStore.subscribe, cartStore.getLastOrder);

  // A view-scoped, consequential tool: it exists only on this page, and only with items in the cart.
  useWebMCP({
    name: 'checkout',
    description: 'Place the order for everything in the cart. The user must confirm in the page\'s own dialog; nothing is ordered until they click "Place order". Returns the order ID, status "cancelled_by_user" if the user declines, or status "refused" if the cart changed before they confirmed.',
    annotations: { consequentialHint: true },
    enabled: cart.itemCount > 0,
    execute: (_input, { signal }) => checkout(signal),
  });

  return (
    <section>
      <h1>Your cart</h1>
      {lastOrder && cart.itemCount === 0 && (
        <p className="notice" data-testid="order-placed">Order {lastOrder.orderId} placed. Takk!</p>
      )}
      {cart.itemCount === 0 ? <p>Your cart is empty.</p> : (
        <>
          <ul className="lines">
            {cart.lines.map((l) => (
              <li key={l.sku}>{l.quantity} × {l.name} <span>{(l.quantity * l.unitPrice.amount).toLocaleString('nb-NO')} NOK</span></li>
            ))}
          </ul>
          <p className="total">Total: {cart.total.amount.toLocaleString('nb-NO')} NOK</p>
          <button type="button" onClick={() => void checkout(new AbortController().signal)}>Checkout</button>
        </>
      )}
    </section>
  );
}
```

The tool exists only while `<CartPage>` is mounted, and `enabled: cart.itemCount > 0` removes it whenever the cart is empty. That option unregisters the tool without unmounting anything, and registers it again when the condition becomes true.[^ch10-12] So an agent can’t try to check out an empty cart: the tool simply isn’t there. The `consequentialHint` annotation tells the agent and the browser that calling it has effects in the world (Chapter 6). And the description lists every outcome the agent can get back, including the `refused` case that the next section adds.

The tool and the “Checkout” button both call `checkout()`. The button passes a signal that never aborts, the tool passes the execution signal the browser gives every call. That one difference is the subject of the next section.

The tests walk through Figure 10.2 step by step in Chromium 156: four tools on `/`, still four on an empty `/cart`, five once `add_to_cart` has run, and four again after the person goes back to the shop.

## Unregistering without breaking in-flight calls

Here is the case that makes framework code different from page scripts. An agent calls `checkout`. Trailhead opens its confirmation dialog and waits for the person. While the dialog is open, the person presses Back. React Router renders the shop, `<CartPage>` unmounts, and the hook aborts the registration. What happens to the call?

The specification is explicit: “Unregistering a tool does not cancel an execution that has already invoked its ToolExecuteCallback, including when the callback itself performs the unregistration. The registration-time signal only controls tool availability, while the execution-time signal controls the lifetime of an specific invocation.”[^ch10-15] Chrome’s documentation says the same from the implementation side: “As of Chrome 153, you can unregister a tool without cancelling and breaking in-flight executions.”[^ch10-8] Chromium 156 behaves that way. In a probe, a tool unregistered 50 milliseconds into a 400-millisecond call disappeared from `getTools()` at once, and the call still resolved with its value. Its execution signal was never aborted.

So the browser won’t break the call. Your app can. If the pending confirmation lived in `<CartPage>`’s state, the dialog would unmount together with the page, nobody could answer it, and the agent’s call would hang forever (or until the agent gave up). Table 10.3 separates the two signals that are so easy to confuse.

**Table 10.3 — The two signals a tool deals with**

| | Registration signal | Execution signal |
|---|---|---|
| Who creates it | Your code (the hook does it for you) | The browser, one per call |
| Where you get it | `registerTool(tool, { signal })` | `execute(input, { signal })` |
| Aborting it means | The tool is no longer available | This call is cancelled |
| Typical cause | Component unmounts, route changes, `enabled` turns false | The agent or the person cancels, the agent times out, the caller passes its own signal to `executeTool()` |
| What happens to running calls | Nothing, they finish | This call should stop and clean up |

Sources: WebMCP specification, Draft Community Group Report, 27 October 2026.[^ch10-2] [^ch10-15]

The rule that follows is simple: **anything an in-flight call depends on must outlive the component that registered the tool.** Trailhead puts the checkout flow in a module, not a component (Listing 10.6), and the pending question in a store that the layout renders (Listing 10.7).

**Listing 10.6** `trailhead-react/src/checkout.ts` — one checkout path for the button and the tool, with a commit point

```ts
import { cartStore } from './cart-store';
import { requestConfirmation } from './confirm-store';

export type CheckoutResult =
  | { status: 'placed'; orderId: string; total: { amount: number; currency: 'NOK' } }
  | { status: 'cancelled_by_user'; message: string }
  | { status: 'refused'; code: 'CART_CHANGED'; message: string }
  | { status: 'error'; code: 'CART_EMPTY'; message: string };

// The one checkout path. The Checkout button and the checkout tool both call it.
export async function checkout(signal: AbortSignal): Promise<CheckoutResult> {
  const cart = cartStore.getSnapshot();
  if (cart.itemCount === 0) {
    return { status: 'error', code: 'CART_EMPTY', message: 'The cart is empty. Add products with add_to_cart first.' };
  }
  const confirmed = await requestConfirmation(
    'Place this order?',
    `${cart.itemCount} item(s), ${cart.total.amount.toLocaleString('nb-NO')} NOK in total.`,
    signal,
  );
  if (!confirmed) {
    return { status: 'cancelled_by_user', message: 'The user declined the order in the confirmation dialog.' };
  }
  // The commit point. The person confirmed the cart they saw, so order exactly that cart or nothing.
  if (cartStore.getSnapshot() !== cart) {
    return {
      status: 'refused',
      code: 'CART_CHANGED',
      message: 'The cart changed while the user was confirming, so nothing was ordered. Call get_cart, tell the user what changed, then call checkout again.',
    };
  }
  const order = cartStore.placeOrder();
  return { status: 'placed', orderId: order.orderId, total: order.total };
}
```

**Listing 10.7** `trailhead-react/src/confirm-store.ts` — a confirmation that survives navigation and honours cancellation

```ts
import { useSyncExternalStore } from 'react';

export interface PendingConfirmation {
  id: number;
  title: string;
  detail: string;
  answer: (confirmed: boolean) => void;
}

let pending: PendingConfirmation | null = null;
let nextId = 1;
const listeners = new Set<() => void>();
const emit = () => listeners.forEach((notify) => notify());

// Ask the person, in the page's own UI, and wait for their click.
// The question lives here, not in a route component, so it survives navigation.
export function requestConfirmation(title: string, detail: string, signal: AbortSignal): Promise<boolean> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(signal.reason);
    pending?.answer(false);                // only one question on screen at a time
    const id = nextId++;
    const close = () => {
      signal.removeEventListener('abort', onAbort);
      if (pending?.id === id) { pending = null; emit(); }
    };
    const onAbort = () => { close(); reject(signal.reason); };
    signal.addEventListener('abort', onAbort, { once: true });
    pending = { id, title, detail, answer: (confirmed) => { close(); resolve(confirmed); } };
    emit();
  });
}

export function usePendingConfirmation(): PendingConfirmation | null {
  return useSyncExternalStore(
    (listener) => { listeners.add(listener); return () => listeners.delete(listener); },
    () => pending,
  );
}
```

`requestConfirmation()` stores the question in module state, and `<ConfirmDialog>`, which the layout renders on every route, shows it. The question belongs to the call, and the page can change under it. If the person presses Back, the dialog stays on screen over the shop, and clicking “Place order” resolves the agent’s call with an order ID. The test for exactly that sequence passes in Chromium 156 and against the mock.

The execution signal is handled the other way round. If it aborts, the dialog closes and the promise rejects with the signal’s reason, so the agent can’t leave a stale question on the person’s screen. In Chromium 156, aborting the signal passed to `executeTool()` rejects the caller’s promise with an `AbortError`, aborts the signal the tool received, and fires a `toolcancel` event at `document.modelContext`.[^ch10-16] The dialog disappears, and nothing is ordered.

### A commit point, and a cart that must not move

Listing 10.6 has one check that the first edition didn’t: after the person clicks “Place order”, `checkout()` compares the cart snapshot with the one it showed in the dialog, and refuses to order if they differ. Why would they differ? Because the agent and the person share the page. While “Place this order?” sits on the screen with the item count and the total, the agent is free to call `add_to_cart` (it’s an app-wide tool), and the person can add something with a click. Without the check, “Place order” would order a cart nobody confirmed.

Chrome’s best practices describe this exact trap. Agents “might repeat a simulation, retry an earlier tool, or call a valid operation, after the human updated the page”, so you should “reject calls made against stale workflow state by binding consequential transitions to exact values, such as the resource identity, state version, plan ID, plan hash, and exact scope”, and confirmation “must recompute the current state and reject stale work”.[^ch10-1] In Trailhead the exact value is the snapshot object itself: the store never mutates it, so `cartStore.getSnapshot() !== cart` means that something changed. In a real store with a server, you would send a cart version or a hash of the confirmed lines and let the server refuse a mismatch.

The outcome is `refused` with the code `CART_CHANGED`, not an `error`, because the agent has nothing to fix in its arguments. The person has to look at the new cart and confirm again (Chapter 11 explains the vocabulary). In Chromium 156 the test opens the dialog, lets the agent add a sleeping bag behind it, clicks “Place order”, and gets `refused` back. The header still says “Cart (2)”, and no order exists.

The same check marks the commit point of the flow, which is the other constraint on Chrome’s list: “Define when cancellation can stop a change.” The page’s guidance continues: “If you receive a later abort signal, it’s possible the change was not cancelled and still completed.”[^ch10-1] In Listing 10.6 the line is easy to see. Before `placeOrder()`, an abort closes the dialog and nothing happens. After it, the order exists, and an abort that arrives later changes nothing. If your commit is a network request, decide which side of it a late abort falls on, and say so in the result.

Two smaller points complete the picture. First, the hook’s registration signal and the call’s execution signal are independent, so never use one in place of the other. A tool that aborted its work when its component unmounted would turn every navigation into a cancelled order. Second, don’t route a result through the state of the component that registered the tool. A handler that returns its result through the store or the promise, as Listing 10.6 does, works whether that component is still mounted or not.

## State sync: telling the agent what changed

An agent works from snapshots. The specification’s non-normative section on page observations describes the browser agent getting “an observation”, an implementation-defined structure that contains at least a tool map, and notes that it “often includes screenshots of the page, not just a DOM serialization”.[^ch10-17] Between observations, the agent knows only what it was told. In a component app the page changes all the time, so it’s worth being deliberate about how changes reach the agent. Trailhead uses four channels.

**Return values describe the new state.** `add_to_cart` doesn’t return `"OK"`. It returns what was added and the cart’s new item count and total, so the agent can plan its next step without another call. `checkout` returns a status the agent can act on: `placed` with an order ID, `cancelled_by_user` with an explanation, `refused` with `CART_CHANGED`, or `error` with the code `CART_EMPTY`. Failures use the `{ status, code, message }` shape that Chapter 11 sets out for the whole book.

**A read-only tool answers “what is the state now?”.** `get_cart` costs little, can be called at any time, and reflects changes the person made by hand. Chrome’s best practices add a related point: agents may rely on the interface to plan their next steps, so “update the interface state after functions are completed”. The newer list puts it even more strictly: “Only resolve a tool execution with success when the output matches the application state.”[^ch10-1] Trailhead’s tools change the same store the UI renders, so by the time a tool returns, the screen already matches.

**The tool set itself is information.** When `checkout` appears or disappears, the browser fires `toolchange`, and agents and in-page tool consumers that listen for it refresh their list.[^ch10-5] A tool’s availability tells the agent what is possible right now. `enabled: cart.itemCount > 0` says “there is something to check out” without a single word of description.

**Descriptions stay still.** Don’t put live state, such as a cart total or a count of results, into a description. Every change would mean unregistering and registering again, with a `toolchange` each time, and the model would read the new description only when it next observed the page anyway.[^ch10-5] Put state in results and read tools, and keep re-registration for real changes to what a tool is or does, such as a language switch. The test page for Listing 10.1 shows the difference: three clicks that change state produce zero `toolchange` events, while switching the description to Norwegian produces an unregistration and a registration.

### And telling the person what the agent did

State sync runs the other way too. When an agent adds a sleeping bag to the cart, the person should be able to see that it happened, and who did it. The specification defines two events for this, dispatched at `document.modelContext`: `toolactivated`, “when the execution of a tool begins”, and `toolcancel`, “when the execution of a tool is cancelled”. Each carries the tool’s name in `toolName`.[^ch10-16] Listing 10.8 turns them into a small status pill.

**Listing 10.8** `trailhead-react/src/agent/AgentActivity.tsx` — showing the person what the agent is doing

```tsx
import { useEffect, useState } from 'react';

// Shows the person what the agent just did, using the toolactivated and toolcancel events.
export function AgentActivity() {
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const modelContext = document.modelContext;
    if (!modelContext) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const show = (text: string) => {
      setMessage(text);
      clearTimeout(timer);
      timer = setTimeout(() => setMessage(null), 4000);
    };
    const onActivated = (e: WebMCP.ToolActivatedEvent) => show(`Agent is using ${e.toolName}`);
    const onCancel = (e: WebMCP.ToolCancelEvent) => show(`Agent cancelled ${e.toolName}`);
    modelContext.addEventListener('toolactivated', onActivated);
    modelContext.addEventListener('toolcancel', onCancel);
    return () => {
      clearTimeout(timer);
      modelContext.removeEventListener('toolactivated', onActivated);
      modelContext.removeEventListener('toolcancel', onCancel);
    };
  }, []);

  return message ? <p className="agent-activity" role="status">{message}</p> : null;
}
```

Chromium 156 dispatches both events. `toolactivated` arrives as a `ToolActivatedEvent` when a call starts, and `toolcancel` as a `ToolCancelEvent` when the caller aborts. Figure 10.3 is a screenshot from the test run: an agent has added two products, the person has opened the cart, and the agent has called `checkout`. The pill names the tool, and the order waits for the person’s click.

![Figure 10.3 — Trailhead in Chromium 156 with WebMCPTesting, after an agent called checkout. The page’s own dialog asks the person to confirm, and the status pill (bottom right) says which tool the agent is using.](images/figure-10-3.png)

> **Still in flux:** `toolactivated` and `toolcancel` are in the 27 October 2026 draft, and Chromium 156 fires both. Chrome’s documentation adds that both events are not cancelable, and that `window.ontoolactivated` and `window.ontoolcancel` are not supported from Chrome 156. There is no matching “completed” event, so a pill like Listing 10.8’s has to fade on a timer, or your own `execute` wrappers have to report completion. Treat the events as a convenience for the UI. The source of truth for what happened is still the tool’s result.[^ch10-16] [^ch10-22]

## Vue: a composable

Since 16 October 2026 Chrome’s imperative-API page has a Vue section too. It says Vue “has experimental support for WebMCP using the @vueuse/core package”, with a `useWebMCP` composable “tied to the current Vue scope lifecycle” that “also supports reactive and conditional tool registration, and automatically normalizes execution results”.[^ch10-8]

VueUse’s documentation describes the same contract as Listing 10.1, in Vue terms. The tool registers when the composable runs and unregisters when the scope is disposed. Name, description, schema, annotations and `enabled` accept refs or getters, and changing one of the agent-facing fields registers the tool again, while `execute` is read live at call time, “so a changing closure never churns the registration”. Results are normalized exactly as in Chrome’s React hook: a string becomes a `content` block, a thrown value becomes an `isError` result. The composable returns `isSupported`, `isRegistered` and `error`.[^ch10-23]

There is no Vue version of Trailhead in the demos folder, so this chapter doesn’t print untested code. If your app is written in Vue, the five jobs from the beginning of this chapter are your checklist, and VueUse’s composable ticks all of them.

## Angular: tools in the injector

Angular took a different route to the same place. Its WebMCP support is part of the framework itself, in `@angular/core` and `@angular/forms`, rather than a community package. Angular’s guide describes it as experimental support that lets you “easily register tools tied to your application’s dependency injection lifecycle and automatically turn your Signal Forms into AI-ready tools”, and it warns that the APIs “are subject to change even outside of major versions”.[^ch10-18] Chrome’s imperative-API page links to the same guide.[^ch10-8] The examples below were written and tested against Angular 22.2.2, the current release on 14 October 2026, in which every WebMCP function is marked `@experimental`.[^ch10-19] (On 2 November 2026 the latest release was 22.2.4.)

Where React ties a tool to a component, Angular ties it to an injector. Three APIs cover the cases:

- `provideExperimentalWebMcpTools([...])` in the application’s providers registers tools for the whole life of the app. Each tool’s `execute` runs in the injection context of the associated injector, so it can call `inject()` directly.[^ch10-18]
- The same function in a route’s `providers` registers tools for that route. Angular’s guide recommends `withAutoCleanupInjectors()` on the router, because without it route tools “will remain accessible to AI agents even after the user has navigated to a different route”.[^ch10-18]
- `declareExperimentalWebMcpTool()` registers a tool from inside any injection context, such as a service constructor, and unregisters it when that context is destroyed.[^ch10-18]

Listing 10.9 is Trailhead’s `search_products` as an Angular app-wide tool. The catalog module is the same file the React app uses. Only the wrapper changes.

**Listing 10.9** `angular/src/app.config.ts` — an app-wide tool in the application config

```ts
import { type ApplicationConfig, inject, provideExperimentalWebMcpTools } from '@angular/core';
import { provideExperimentalWebMcpForms } from '@angular/forms/signals';
import { provideRouter, withAutoCleanupInjectors } from '@angular/router';
import { CatalogService } from './catalog.service';
import { CATEGORIES } from './catalog';
import { routes } from './routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withAutoCleanupInjectors()),   // route tools go away with their route
    provideExperimentalWebMcpForms(),                     // lets Signal Forms opt in as tools
    provideExperimentalWebMcpTools([                      // app-wide: registered for the app's lifetime
      {
        name: 'search_products',
        description: 'Search the Trailhead catalog of outdoor gear. Returns matching products with SKU, name, price in NOK, rating and stock status.',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Keywords, for example "down sleeping bag".' },
            category: { type: 'string', enum: [...CATEGORIES] },
            maxPrice: { type: 'number', description: 'Optional maximum price in NOK.' },
          },
          required: ['query'],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true },
        execute: ({ query, category, maxPrice }) => {
          if (typeof query !== 'string') return { status: 'error', code: 'INVALID_ARGUMENT', message: 'query must be a string.' };
          if (category !== undefined && !CATEGORIES.includes(category)) {
            return { status: 'error', code: 'INVALID_ARGUMENT', message: `category must be one of: ${CATEGORIES.join(', ')}.` };
          }
          return { products: inject(CatalogService).search({ query, category, maxPrice }) };
        },
      },
    ]),
  ],
};
```

The `execute` function asks the injector for `CatalogService` at call time. Like `usewebmcp`, Angular infers the argument types from the schema, which is why `category` arrives typed as one of the enum’s strings. And like `usewebmcp`, it doesn’t check them. The guide is clear that inputs “may not be validated to match the schema”, and it recommends validating arguments explicitly.[^ch10-18] The handler also receives a second argument with the call’s `signal`, a change Angular made in August 2026 so that tools can handle cancellation.[^ch10-20]

Listing 10.10 adds a route-scoped tool.

**Listing 10.10** `angular/src/routes.ts` — a tool that lives with its route

```ts
import { inject, provideExperimentalWebMcpTools } from '@angular/core';
import type { Routes } from '@angular/router';
import { CartService } from './cart.service';
import { CartPage, ShopPage } from './pages';
import { StockAlertPage } from './stock-alert';

export const routes: Routes = [
  { path: '', component: ShopPage },
  {
    path: 'cart',
    component: CartPage,
    providers: [
      provideExperimentalWebMcpTools([   // registered while /cart is active
        {
          name: 'get_cart',
          description: 'Read the current shopping cart: lines and total in NOK.',
          inputSchema: { type: 'object', properties: {} },
          annotations: { readOnlyHint: true },
          execute: () => inject(CartService).snapshot(),
        },
      ]),
    ],
  },
  { path: 'stock-alert', component: StockAlertPage },
];
```

When the router activates `/cart`, it creates the route’s environment injector, and the tool registers. With `withAutoCleanupInjectors()` (Listing 10.9), leaving the route destroys that injector, and the tool unregisters. In Chromium 156 with WebMCPTesting, `get_cart` appears when the test clicks the Cart link and disappears again when it clicks Shop. Annotations such as `readOnlyHint` arrived in Angular’s API in September 2026, and `consequentialHint` a few days later.[^ch10-20] The spec’s fourth annotation, `debugging`, followed on Angular’s main branch on 20 October 2026, for `declareExperimentalWebMcpTool()` only (form tools always get `debugging: false`).[^ch10-24]

### Signal Forms as tools

The most distinctive part of Angular’s support turns an existing form into a tool. Add `provideExperimentalWebMcpForms()` to the providers (Listing 10.9 already does), then pass `experimentalWebMcpTool` with a name and a description when you create a Signal Form. Angular infers the JSON Schema from the form’s model, marks fields with a `required` validator as required, and connects the tool to the form’s validation and submission, so “the agent will observe any validation errors triggered by its inputs or any failures which happen during submission”.[^ch10-18] Listing 10.11 gives Trailhead a back-in-stock alert this way.

**Listing 10.11** `angular/src/stock-alert.ts` — a Signal Form that is also a tool

```ts
import { Component, inject, signal } from '@angular/core';
import { email, form, FormField, min, required } from '@angular/forms/signals';
import { StockAlertService } from './stock-alert.service';

@Component({
  selector: 'th-stock-alert',
  imports: [FormField],
  template: `
    <h1>Tell me when it's back</h1>
    <label>Email <input type="email" [formField]="alertForm.email" /></label>
    <label>SKU <input [formField]="alertForm.sku" /></label>
    <label>Quantity <input type="number" [formField]="alertForm.quantity" /></label>
  `,
})
export class StockAlertPage {
  private readonly alerts = inject(StockAlertService);
  private readonly model = signal({ email: '', sku: '', quantity: 1 });   // concrete initial values

  readonly alertForm = form(
    this.model,
    (f) => {
      required(f.email, { message: 'An email address is required.' });
      email(f.email, { message: 'Enter a valid email address.' });
      required(f.sku, { message: 'Give the product SKU from search_products.' });
      min(f.quantity, 1, { message: 'Quantity must be at least 1.' });
    },
    {
      experimentalWebMcpTool: {
        name: 'request_stock_alert',
        description: 'Ask Trailhead to email the user when an out-of-stock product is back in stock.',
      },
      submission: {
        action: async (field) => {
          await this.alerts.subscribe(field().value());
          return undefined;
        },
      },
    },
  );
}
```

This is what Chromium 156 reported for that form. `getTools()` listed `request_stock_alert` with this inferred schema:

```json
{"type":"object","properties":{"email":{"type":"string"},"sku":{"type":"string"},"quantity":{"type":"number"}},"required":["email","sku"],"additionalProperties":false}
```

A call with `email: "not-an-email"` came back as `{"content":[{"type":"text","text":"Form submission failed:\nemail: Enter a valid email address."}]}` and saved nothing. A valid call returned “Form submitted successfully.”, ran the submission action, and filled the visible form with the agent’s values, so the person could see what had been submitted on their behalf.

Three constraints come with the convenience, all from Angular’s guide. The schema is inferred from the model’s initial value, so every field needs a concrete starting value (`''`, `0`, `false`), and arrays need at least one element. Async validators don’t protect a tool call: in the guide’s corrected wording of 21 October 2026, “by default, async validators don’t block submission: the submission action runs before they finish, so their errors aren’t reported to the agent”, so do those checks in the submission action instead.[^ch10-18] And because WebMCP rejects duplicate names, a component that registers a tool, a form-backed one included, must never be on the page more than once at a time. Angular recommends putting tools in application providers, route providers or root services wherever possible.[^ch10-18]

Notice also what the inferred schema lacks: descriptions. The field names are all the model gets. For a form that agents will use often, a hand-written schema (Listing 10.9’s style) with a description for every field may be worth the duplication. Chapter 11 looks at why.

> **Still in flux:** Every Angular function used in this section carries “Experimental” in its name and an `@experimental` tag, and the guide warns they may change outside major versions. Their history shows how quickly they move: registration became asynchronous in July 2026, tools gained a cancellation signal in August, annotations arrived in September, and the `debugging` annotation and a switch to the official `webmcp-types` definitions landed on the main branch in late October.[^ch10-18] [^ch10-20] [^ch10-24]

## Server rendering and other frameworks

Two more situations deserve a paragraph each.

**Server rendering.** `document.modelContext` exists only in a browser, and only in a secure context. The MCP-B framework guide’s advice holds for any server-rendered app: mount tool hooks only in client-rendered components, and run anything that touches `document`, `window` or page state on the client. `usewebmcp` keeps its `'use client'` directive and doesn’t register tools during a server render.[^ch10-13]

**Other frameworks.** Chrome’s imperative-API page now names three frameworks: React, Vue and Angular.[^ch10-8] For everything else, the MCP-B guide suggests using the WebMCP API “with that framework’s native lifecycle guidance”.[^ch10-13] The five jobs at the start of this chapter are that guidance in framework-neutral form: detect, register on mount, abort on unmount, re-register only on metadata changes, and call through to current state. Any framework with a mount hook and a cleanup hook can do all five, and Listing 10.1 shows the shape to copy.

## Trailhead so far

Trailhead now has five tools, organised the way Table 10.1 shows: four registered once for the whole app, and one tied to the cart route and to the cart having items. Every tool is a thin wrapper over the same modules the UI uses. The cart lives in a store outside the component tree, and so does the checkout confirmation, so neither can be lost when a component unmounts. Checkout orders exactly the cart the person confirmed, or nothing. The layout shows the person which tool the agent is using. And the Angular listings show the same tools expressed through Angular’s injector and Signal Forms.

In the repository, 12 Playwright tests cover the React app and 5 cover the Angular listings. The React tests (including the new one for a cart that changes behind the dialog) passed against both the mock and Chromium 156 (156.0.8078.4) with WebMCPTesting on 2 November 2026. The Angular tests passed against both on 14 October 2026.[^ch10-4]

Chapter 11 steps back from mechanics to design. Trailhead’s tools work, but are they the right tools? How many should a store have, how coarse should they be, and what should they say and return so that a model picks the right one and uses it well?

## Chapter summary

- In a framework the WebMCP API is unchanged. What changes is who calls it and when. A component or injector that offers a tool must detect support, register on mount, unregister on unmount, re-register only when the agent-facing metadata changes, and run calls against current state.
- The trick behind every hook is a stable registered function that delegates to the latest render’s `execute`. Re-registering on every render churns `toolchange` events, and registering once without delegation gives calls stale state.
- React’s StrictMode registers, aborts and registers again in one tick. That works because abort steps run synchronously: in Chromium 156 the first promise rejects with `AbortError`, and the tool is listed once. Test against a real browser as well as a mock. Chromium rejects `inputSchema: null` with a `TypeError`, which a lenient mock missed.
- If your tools only make sense together, register them as one batch: one shared signal, aborted as soon as any registration fails. That is what Chrome’s “register tools all at once” asks for.
- Chrome’s documentation names `use-webmcp-tool` for React (since 16 October 2026) and `@vueuse/core` for Vue. Trailhead uses the community `usewebmcp` 6.0.3, which passes results through untouched, infers input types and supports `exposedTo`. Pin versions, and keep tool logic out of the hook call.
- Keep tools thin: schema, validation and translation over one application service that the UI and the tests use too. Keep shared state in stores outside the component tree, so tools registered anywhere see the same cart as the person.
- Let the route decide view-specific tools, but make static registration the default, as Chrome recommends. Trailhead ties only `checkout` to a view, and `enabled` hides it while the cart is empty.
- Unregistering never cancels a running call. Only the execution signal does. Anything an in-flight call depends on, such as a pending confirmation, must outlive the component that registered the tool. Honour the execution signal by closing dialogs and rejecting.
- Bind a consequential step to the exact state the person confirmed, and refuse it when that state changed. Know where your commit point is: an abort that arrives after it doesn’t undo anything.
- Tell the agent what changed through return values, read-only tools and the tool set itself, and keep descriptions free of live state. Tell the person what the agent did with `toolactivated` and `toolcancel`.
- Angular 22.2 ships experimental WebMCP support: `provideExperimentalWebMcpTools()` for app-wide and route-scoped tools (with `withAutoCleanupInjectors()`), `declareExperimentalWebMcpTool()` for services, and Signal Forms that become tools with an inferred schema and validation errors returned to the agent.

## Notes

[^ch10-1]: Chrome for Developers, “WebMCP best practices” by Alexandra Klepper, Maxim Salnikov and François Beaufort (published 18 May 2026, last updated 30 October 2026), sections “Enforce architectural constraints” (“Register tools all at once”, “Share the application service”, “Wait for the UI”, “Establish explicit commit points”), “Create a tool strategy” (“Manage tool registration”, “Reduce complexity”) and “Prioritize reliability” (“Update the interface state after functions are completed”, “Stale workflow state”, “Recompute on confirmation”), retrieved November 2026. <https://developer.chrome.com/docs/ai/webmcp/best-practices>
[^ch10-2]: WebMCP specification, Draft Community Group Report, 27 October 2026: §4.2 the `ModelContext` interface (`registerTool()`, `getTools()`, `executeTool()`, `ontoolchange`, `ontoolactivated`, `ontoolcancel`), §4.2.3 `ModelContextRegisterToolOptions` (“An AbortSignal that unregisters the tool when aborted”) and the abort steps in `registerTool()`. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool>
[^ch10-3]: npm registry entries read on 14 October 2026 and again on 2 November 2026 (no newer versions in between): `usewebmcp` 6.0.3 (published 14 October 2026, after 6.0.0 on 8 October, 6.0.1 on 12 October and 6.0.2 on 13 October, repository WebMCP-org/npm-packages, MIT licence, peer dependency React ^18 || ^19), `@mcp-b/react-webmcp` 6.0.3, `@mcp-b/webmcp-polyfill` 6.0.3, `react` 19.3.1, `react-router` 8.4.0, `vite` 8.3.4, `@vitejs/plugin-react` 6.1.2, `typescript` 7.0.2. <https://www.npmjs.com/package/usewebmcp>
[^ch10-4]: The book’s companion repository, folder `chapters/10-webmcp-in-frameworks/` (`trailhead-react/tests/run-tests.mjs` and `angular/tests/run-tests.mjs`, Playwright 1.64.1 with Chromium 156.0.8078.4). <https://github.com/webmaxru/webmcp-book-demos/tree/main/chapters/10-webmcp-in-frameworks>
[^ch10-5]: WebMCP explainer (README), “Best Practices”, “Keeping agent-facing parts of a tool definition updated” (“A tool’s implementation can by dynamic”, “Re-register changed agent-facing metadata”, “Validation at execution time”), retrieved November 2026. <https://github.com/webmachinelearning/webmcp#best-practices>
[^ch10-6]: React documentation, “&lt;StrictMode&gt;”: “React will also run one extra setup+cleanup cycle in development for every Effect.” <https://react.dev/reference/react/StrictMode>
[^ch10-7]: WebMCP specification, §4.2.1 `ModelContextTool` dictionary (`object inputSchema`), read with Web IDL’s dictionary conversion rules. <https://webmachinelearning.github.io/webmcp/#dictdef-modelcontexttool>
[^ch10-8]: Chrome for Developers, “Imperative API” (published 18 May 2026, last updated 16 October 2026), sections “React support”, “Vue support” and “Angular support”, and the version notes on unregistering during an execution (Chrome 153), retrieved November 2026. The “React support” section named the `usewebmcp` package until the 16 October 2026 update. <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
[^ch10-9]: `usewebmcp` README, version 6.0.3 (sections “Input schemas”, “State and lifecycle”, “Upgrading from 5.x”), as published in the npm package. <https://www.npmjs.com/package/usewebmcp>
[^ch10-10]: `webmcp-types` on npm (version 0.1.10, published 28 September 2026). <https://www.npmjs.com/package/webmcp-types>
[^ch10-11]: GoogleChromeLabs, `use-webmcp-tool` README (“This is maintained by Chrome, and will be updated with any spec changes”, sections “API” and “execute parameters & return values”), in the npm package for version 0.3.0 (published 11 September 2026). <https://github.com/GoogleChromeLabs/use-webmcp-tool>
[^ch10-12]: MCP-B documentation, “usewebmcp reference” (sections “Hook”, “Config fields”, “JSON Schema and inference”, “Re-registration triggers”, “Results”). <https://docs.mcp-b.ai/packages/usewebmcp/reference>
[^ch10-13]: MCP-B documentation, “Integrate with your framework” (sections “Choose a React hook”, “Handle server rendering”, “Use framework-owned guidance elsewhere”). <https://docs.mcp-b.ai/how-to/frameworks>
[^ch10-14]: React documentation, “useSyncExternalStore”. <https://react.dev/reference/react/useSyncExternalStore>
[^ch10-15]: WebMCP specification, Draft Community Group Report, 27 October 2026, §3, “unregister a tool”, including the note on executions already in progress. <https://webmachinelearning.github.io/webmcp/#model-context-unregister-a-tool>
[^ch10-16]: WebMCP specification, Draft Community Group Report, 27 October 2026, §4.3 Events: §4.3.1 `ToolActivatedEvent` and §4.3.2 `ToolCancelEvent`, and §4.2.5 `ModelContextExecuteToolOptions` (“An AbortSignal that can be used to cancel the execution of the tool”). <https://webmachinelearning.github.io/webmcp/#events>
[^ch10-17]: WebMCP specification, Draft Community Group Report, 27 October 2026, §5.2 Page observations (non-normative). <https://webmachinelearning.github.io/webmcp/#interaction-with-agents>
[^ch10-18]: Angular documentation, “WebMCP” (source `adev/src/content/ai/webmcp.md`, added 20 May 2026, last changed 21 October 2026 by “docs: correct the async validator note in the WebMCP guide”), sections “Provide tools for the application”, “Provide tools for a route”, “Provide tools within services”, “Implicit tools in Signal Forms” and “Best practices”, retrieved November 2026. <https://angular.dev/ai/webmcp>
[^ch10-19]: `@angular/core` and `@angular/forms` 22.2.2 on npm (published 8 October 2026), type definitions for `provideExperimentalWebMcpTools`, `declareExperimentalWebMcpTool` (`@experimental`), the tool `Annotations` interface (`@experimental 22.2`) and the `experimentalWebMcpTool` form option. Version 22.2.4 was published on 29 October 2026. <https://www.npmjs.com/package/@angular/core>
[^ch10-20]: angular/angular pull requests #69720 “Update WebMCP tool registration to be asynchronous” (merged 10 July 2026), #70258 “refactor(core): pass AbortSignal to WebMCP tools to handle cancellation” (merged 19 August 2026), #70496 “WebMCP annotations” (merged 1 September 2026) and #70654 “Add WebMCP `consequentialHint` annotation” (merged 10 September 2026). <https://github.com/angular/angular/pull/70258>
[^ch10-21]: Chromium Dash, Stable releases for Windows: Chrome 156 Stable (156.0.8078.80) since 20 October 2026, read 2 November 2026. <https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Windows>
[^ch10-22]: Chrome for Developers, “Declarative API” (last updated 25 September 2026), section on the `toolactivated` and `toolcancel` events, retrieved November 2026. <https://developer.chrome.com/docs/ai/webmcp/declarative-api>
[^ch10-23]: VueUse documentation, “useWebMCP” (sections “Usage”, “Result normalization” and “Reactive & conditional registration”), VueUse 15.0.0, retrieved November 2026. <https://vueuse.org/core/usewebmcp/>
[^ch10-24]: angular/angular pull requests #71123 “WebMCP `debugging` annotation” (merged 20 October 2026) and #71354 “refactor(core): use official webmcp-types” (merged 28 October 2026), both into the main branch. <https://github.com/angular/angular/pull/71123>
