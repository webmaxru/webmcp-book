# Chapter 7: Frames, Origins and Page-Embedded Agents

> *“I wonder if it would be better to reposition this idea as a general way to call functions in other environments.”*
>
> — Jake Archibald, webmachinelearning/webmcp issue #236[^ch07-1]

## A page is more than one document

Chapters 4 to 6 treated a WebMCP site as one page: Fjord Table registers its tools on `document.modelContext`, and an agent in the browser finds and calls them. That is the common case, but how many real pages are really one document? A SaaS dashboard embeds a payment form from its processor, a chat bubble from a support vendor, a map, a video player and a couple of analytics frames. Every `<iframe>` holds a document of its own, often from a different origin, and every document has its own `ModelContext`.[^ch07-2]

This chapter is about what happens to tools in that tree of documents. It answers three questions:

- **Who may register tools?** The `tools` Permissions Policy decides which frames get to use the API at all.
- **Who may see and call them?** `exposedTo` on the provider’s side and `fromOrigins` on the consumer’s side decide whether tools cross an origin boundary.
- **Who is the agent?** Besides the browser’s own agent, the specification has room for agents written in JavaScript that live in the page (`getTools()` and `executeTool()`), and in practice there are also agents that live in browser extensions.

The running example is the book’s third project, the **Helpdesk Widget**. Supportly, a fictional support-software vendor, serves an embeddable help widget from `https://widget.supportly.example`. Ledgerly, a fictional invoicing dashboard at `https://app.ledgerly.example`, embeds it. The widget registers three tools: `search_articles` and `get_ticket_status`, which only read, and `create_ticket`, which opens a ticket with Supportly’s staff. Ledgerly has an assistant of its own, a small in-page agent that should be able to use Supportly’s tools as well as Ledgerly’s. Nobody else on the page should.

Everything below was checked against the WebMCP Draft Community Group Report dated 27 October 2026, Chrome’s developer documentation, and the open issues and pull requests in the `webmachinelearning/webmcp` repository, re-read on 2 November 2026.[^ch07-3] The cross-origin algorithms this chapter relies on are the same as in the 15 October draft that the first edition used. What is new is that the specification now *explains* them, in a security section that was still unwritten two weeks earlier.

Every behaviour marked “tested” was observed in Chromium 156.0.8078.4 with the `WebMCPTesting` feature switched on (the switch behind `chrome://flags/#enable-webmcp-testing`[^ch07-4]), with Ledgerly and Supportly served from two different local origins. The tests live in the book’s demos repository, in `chapters/07-frames-origins-agents/` (the listing labels below give paths inside that folder), and all 30 of them passed on 15 October 2026 and again on 2 November 2026. Chrome 156 is the stable channel now, but my build is an early one, and I haven’t tested 157 or later. Where Chromium and the draft disagree, I say so.

![Figure 7.1 — Ledgerly’s frame tree. The top-level document and Supportly’s widget frame each have their own ModelContext. Three independent opt-ins stand between the widget’s tools and Ledgerly’s agent.](images/figure-7-1.png)

Figure 7.1 shows the shape of the whole chapter. A cross-origin tool reaches an agent only if three different parties have each said yes: the embedder, the tool provider and the tool consumer. If any of them stays silent, the answer is no.

## Two kinds of agent, two ways to see tools

The gates depend on which kind of agent is looking.

The specification describes a **browser agent**: the assistant built into the browser, which “does not run JavaScript on the page.” It gets its view of the page by performing an *observation*, an implementation-defined snapshot that includes, at minimum, a tool map. The observation walks every document in the tab’s frame tree and records, for each document, an *observed tool collection* with that document’s origin and its tools. A note in the draft adds that user agents “are expected to include the origin field to avoid confusion that could be exploited by an attacker.”[^ch07-5] The browser agent sees the tools of every frame, labelled by origin. The `exposedTo` and `fromOrigins` options don’t apply to it, because it isn’t a document. Only the Permissions Policy decides which frames can register tools in the first place.

The second kind is an **in-page agent**: an agent written in JavaScript that runs inside a document, “and possibly living in iframes,” in the draft’s words.[^ch07-2] It uses the two methods Chapter 5 set aside, `getTools()` to discover tools and `executeTool()` to call one. An in-page agent is just script in some origin, so the same-origin policy applies to it like to any other script, and that is what the two-sided opt-in is for.

A third kind, the extension agent, sits between the two. It runs JavaScript, but with the privileges of a browser extension. It gets its own section later in this chapter.

## Gate 1: the `tools` Permissions Policy

### The default is `'self'`

Access to the whole API is gated behind a policy-controlled feature called `"tools"`, “which has a default allowlist of `'self'`.”[^ch07-6] Every method checks it first. `registerTool()`, `getTools()` and `executeTool()` each begin by asking whether the calling document is allowed to use the `tools` feature and, if not, return a promise rejected with a `NotAllowedError` `DOMException`.[^ch07-7] `getTools()` also skips any document in the tree that isn’t allowed to use the feature, and so does the tool-change notification.[^ch07-8]

With the default allowlist, that means:

- the top-level document can use WebMCP,
- same-origin iframes can use it, with no markup needed,
- cross-origin iframes can’t, unless the embedder delegates the feature to them.

Chrome’s Imperative API guide puts it the same way: “Tool registration is disabled by default in cross-origin iframes. A page must delegate access using the `tools` Permissions Policy.”[^ch07-9]

### Delegating to one frame with `allow="tools"`

Ledgerly delegates the feature to Supportly’s frame with the iframe’s `allow` attribute. Listing 7.1 is Ledgerly’s whole page.

**Listing 7.1** `ledgerly/index.html` — Ledgerly embeds Supportly’s widget and delegates `tools` to it

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ledgerly · Invoices</title>
  <link rel="stylesheet" href="ledgerly.css">
</head>
<body>
  <header><strong>Ledgerly</strong> · Invoices</header>
  <main id="dashboard">…</main>

  <aside id="assistant" aria-label="Ledgerly Assistant">
    <form id="ask"><input name="goal" placeholder="Ask the assistant"><button>Ask</button></form>
    <ol id="transcript"></ol>
  </aside>

  <!-- Supportly's help widget, from a third-party origin. -->
  <iframe id="supportly"
          title="Supportly help"
          src="https://widget.supportly.example/embed.html?customer=ledgerly"
          allow="tools"></iframe>

  <script type="module" src="agent/assistant.js"></script>
</body>
</html>
```

In an `allow` attribute, a feature name with no allowlist uses the default value `src`: the feature is allowed in this iframe “as long as the document loaded into it comes from the same origin as the URL in its `src` attribute.”[^ch07-10] So `allow="tools"` here means “Supportly’s documents in this frame may use WebMCP.” If the widget navigates somewhere else, the delegation doesn’t follow it.

### Setting the policy for the whole page

The `allow` attribute delegates, but it doesn’t restrict. Any other iframe on the page with `allow="tools"` would get the same power, and a marketing team’s tag manager can add iframes. The `Permissions-Policy` response header sets the ceiling for the document and everything inside it. Listing 7.2 is the header Ledgerly sends with its HTML.

**Listing 7.2** `ledgerly/permissions-policy.txt` — Ledgerly’s response header

```http
Permissions-Policy: tools=(self "https://widget.supportly.example")
```

The header’s allowlist takes quoted origins, `self` and `*`. An empty list, `()`, disables the feature in the top-level document and in every nested frame.[^ch07-10] With Listing 7.2 in place, only Ledgerly itself and Supportly’s origin can ever be granted `tools`, whatever iframes appear later. The iframe still needs its own `allow="tools"`: the header says who *may* be granted the feature, and the attribute grants it to a particular frame.

For pages that shouldn’t expose tools at all, the specification lists the empty allowlist as a mitigation of its own. A `Permissions-Policy: tools=()` header makes the feature “unavailable to the document and its descendants,” it applies “to every descendant frame, including both same-origin and cross-origin ones,” and the user agent “enforces this before script runs on the page, protecting against malicious scripts or dependencies from using WebMCP APIs.”[^ch07-11] Ledgerly’s settings pages, where nobody needs an agent, are good candidates.

Table 7.1 shows what Supportly’s widget experienced under each configuration in the tests.

**Table 7.1 — Can Supportly’s cross-origin iframe register tools? (tested, Chromium 156)**

| Ledgerly’s header | `allow` on the iframe | Result inside the widget |
|---|---|---|
| none | none | `registerTool()` rejects with `NotAllowedError` |
| none | `allow="tools"` | Registers |
| `tools=(self "https://widget.supportly.example")` (Listing 7.2) | `allow="tools"` | Registers |
| `tools=(self)` | `allow="tools"` | `NotAllowedError`: the header wins over the attribute |
| `tools=()` | `allow="tools"` | `NotAllowedError` in the widget, and Ledgerly’s own `getTools()` rejects with `NotAllowedError` too |

The error message Chromium gives is `Access to the feature "tools" is disallowed by permissions policy.` A same-origin iframe with no `allow` attribute registered its tools without complaint, as the `'self'` default predicts.

### Feature detection doesn’t see the policy

One result in those tests deserves its own paragraph. In every blocked case, `'modelContext' in document` was still `true` inside the widget. The `modelContext` attribute exists on every `Document` in a secure context where the browser supports WebMCP.[^ch07-2] The policy is checked when you call a method, not when you look for the attribute. Chapter 5 recommended detecting the API, then awaiting registration and catching errors. In an embeddable widget that advice stops being optional. A widget is embedded by customers you don’t control, and some of them will forget `allow="tools"`. Listing 7.3 returns `'blocked'` in that case instead of throwing, so the widget still works as an ordinary help widget for humans.

> **Still in flux:** Today one feature, `tools`, covers both providing tools and consuming them. On 23 September 2026 issue #317 described a host that composes several cross-origin apps and one agent in iframes, and wants the apps to provide tools without using each other’s. It asked whether the policy should be split into two independently delegatable features, “conceptually” `allow="tools-provide"` and `allow="tools-consume"`.[^ch07-12] The same question came back after the Community Group’s face-to-face meeting at TPAC in late October: in issue #236, Mozilla’s Benjamin VanderSloot suggested that the policy should decide whether a frame’s tools may be rolled up into the embedder’s tool list, not whether the frame may register a tool at all, and Google’s Johann Hofmann concluded “I think we need to add a second permissions policy.”[^ch07-1] Both issues were still open on 2 November 2026. If a split lands, Listing 7.1’s single `allow="tools"` may need to become something more specific.

## Gates 2 and 3: `exposedTo` and `fromOrigins`

Getting past the Permissions Policy only means the widget can register tools. By default nobody outside Supportly’s origin can see them. Chrome’s security guide says it directly: “By default, other websites or cross-origin iframes can’t observe or interact with your tools.”[^ch07-13] Crossing that line takes one opt-in from each side.

### The provider’s side: `exposedTo`

`registerTool()` takes a second argument, the `ModelContextRegisterToolOptions` dictionary. Chapter 5 used its `signal` member. The other member is `exposedTo`, “an array of origins that control which documents this tool is exposed to, in the current document’s tree.”[^ch07-14] Listing 7.3 is the widget’s registration code.

**Listing 7.3** `supportly/widget-tools.js` — Supportly registers three tools for the embedding page’s agent

```js
// Supportly help widget: tools for the embedding page's agent.
// Runs inside https://widget.supportly.example/embed.html.
import { helpdesk } from './helpdesk-api.js';
import { confirmTicket } from './widget-ui.js';

// Which origins each customer has registered with Supportly.
const CUSTOMER_ORIGINS = {
  ledgerly: ['https://app.ledgerly.example'],
};

export async function registerWidgetTools(signal) {
  if (!('modelContext' in document)) return 'unsupported';

  const customer = new URLSearchParams(location.search).get('customer');
  const exposedTo = CUSTOMER_ORIGINS[customer] ?? [];   // ①
  const mc = document.modelContext;

  try {
    await mc.registerTool({
      name: 'search_articles',
      title: 'Search help articles',
      description:
        'Search the Supportly help centre for articles that answer a ' +
        'question about the product. Returns titles, links and a short excerpt.',
      inputSchema: {
        type: 'object',
        properties: { query: { type: 'string', maxLength: 200 } },
        required: ['query'],
      },
      annotations: { readOnlyHint: true },
      async execute({ query }) {
        if (typeof query !== 'string' || !query.trim()) {
          return { status: 'error', code: 'INVALID_INPUT',
                   message: 'Provide "query" as a non-empty string.' };
        }
        return { articles: await helpdesk.search(query.slice(0, 200)) };
      },
    }, { signal, exposedTo });                                   // ②

    await mc.registerTool({
      name: 'create_ticket',
      title: 'Open a support ticket',
      description:
        'Open a support ticket with the Supportly team on the user\'s behalf. ' +
        'The user reviews and sends it in the help widget. Returns the ticket ID.',
      inputSchema: {
        type: 'object',
        properties: {
          subject: { type: 'string', maxLength: 120 },
          body: { type: 'string', maxLength: 4000 },
          priority: { type: 'string', enum: ['low', 'normal', 'high'] },
        },
        required: ['subject', 'body', 'priority'],
      },
      annotations: { consequentialHint: true },
      async execute({ subject, body, priority }, { signal }) {
        if (!subject?.trim() || !body?.trim()) {
          return { status: 'error', code: 'INVALID_INPUT',
                   message: 'Provide a non-empty "subject" and "body".' };
        }
        if (!['low', 'normal', 'high'].includes(priority)) {
          return { status: 'error', code: 'INVALID_INPUT',
                   message: '"priority" must be low, normal or high.' };
        }
        const draft = { subject: subject.slice(0, 120), body: body.slice(0, 4000), priority };
        const sent = await confirmTicket(draft, signal);          // ③
        if (!sent) {
          return { status: 'cancelled_by_user',
                   message: 'The user closed the ticket form without sending it.' };
        }
        const ticket = await helpdesk.createTicket(draft);
        return { status: 'created', ticketId: ticket.id };
      },
    }, { signal, exposedTo });

    await mc.registerTool({
      name: 'get_ticket_status',
      title: 'Check a support ticket',
      description:
        'Get the status and latest reply of a Supportly ticket by its ID ' +
        '(for example SUP-1042).',
      inputSchema: {
        type: 'object',
        properties: { ticketId: { type: 'string', pattern: '^SUP-[0-9]+$' } },
        required: ['ticketId'],
      },
      annotations: { readOnlyHint: true, untrustedContentHint: true },  // ④
      async execute({ ticketId }) {
        if (!/^SUP-[0-9]+$/.test(ticketId ?? '')) {
          return { status: 'error', code: 'INVALID_INPUT',
                   message: '"ticketId" looks like SUP-1042.' };
        }
        const ticket = await helpdesk.getTicket(ticketId);
        if (!ticket) {
          return { status: 'error', code: 'TICKET_NOT_FOUND',
                   message: `No ticket ${ticketId} on this account.` };
        }
        // The ticket's own state is ticketState, so status stays free for outcomes.
        return { ticketId, ticketState: ticket.status, latestReply: ticket.latestReply };
      },
    }, { signal, exposedTo });

    return 'registered';
  } catch (err) {
    if (err.name === 'NotAllowedError') return 'blocked';         // ⑤
    throw err;
  }
}
```

The markers point at the parts that matter for this chapter.

① **Who gets the tools.** The widget doesn’t trust the page that embeds it to say who it is. It reads a customer ID from its own URL and looks up the origins that customer registered with Supportly. In a real product the table would come from Supportly’s server, keyed by the customer’s account. If someone embeds the widget with `?customer=ledgerly` on a site that isn’t Ledgerly, nothing leaks: `exposedTo` names the origin that may *consume* the tools, and the browser checks it against the caller’s actual origin. An unknown customer gets an empty list, which exposes the tools to nobody outside Supportly. The tests cover that case: the widget still registers its tools, and Ledgerly’s agent sees none of them.

② **One option per registration.** Each `registerTool()` call gets the same `signal` and the same `exposedTo`. Exposure is per tool, so a vendor could expose `search_articles` widely and keep `create_ticket` for a shorter list.

③ **The provider confirms.** `create_ticket` has consequences, so it carries `consequentialHint` (Chapter 6) and asks the user in the widget’s own UI before anything is sent. Who should ask is a real design question once two companies are involved. My answer here is the tool’s owner: Supportly can’t know whether Ledgerly’s agent asked the user, but it can always ask in its own frame. The confirmation card is wired to the call’s `signal`, so if the agent cancels, the card disappears.

④ **Content Supportly doesn’t vouch for.** Ticket replies are typed by people, and a customer can type anything, including text written to steer an agent. `untrustedContentHint` tells the consumer that this output shouldn’t be read as instructions (Chapters 6 and 12).

⑤ **The policy failure is a value.** As shown above, a missing `allow="tools"` surfaces as `NotAllowedError` from the first `registerTool()` call. The widget reports `'blocked'` and carries on as a widget for humans.

The draft is strict about the origins themselves. Each entry goes through the URL parser, and if parsing fails “or its origin is not potentially trustworthy,” registration rejects with a `SecurityError`.[^ch07-7] *Potentially trustworthy* means, roughly, HTTPS or a local origin such as `http://localhost`, which is why the tests can run on two local ports. In Chromium 156 both a plain-HTTP origin and a string that isn’t a URL at all were refused with `SecurityError: Only secure origins are allowed in the exposedTo list.` (tested). There is no wildcard either. In issue #317, one of the editors, Khushal Sagar, wrote on 26 October that he forgot why `*` was disallowed in `exposedTo` and that “the absence of it seems against the spirit of open web”, so this may yet change.[^ch07-12]

### The consumer’s side: `fromOrigins`

The second opt-in belongs to the agent. `getTools()` takes a `ModelContextGetToolOptions` dictionary with one member, `fromOrigins`: “Documents whose origin appears in this list, or are same-origin with the caller, have their tools queried. An empty list only includes same-origin documents.”[^ch07-15] Its entries are validated like those of `exposedTo`, and an insecure origin rejects with `SecurityError`.

The rule fits in one sentence from the method steps. For each document in the tree, a tool is included only if the document is allowed to use `tools`, the document is same-origin with the caller *or* listed in `fromOrigins`, and the tool “is exposed to” the caller’s origin.[^ch07-8] That last check is a four-line algorithm: return true if the tool’s owner is same-origin with the caller, or if the caller’s origin is in the tool’s exposed origins, otherwise return false.[^ch07-16]

Chrome’s guide sums up the effect for developers: “Even if a tool is exposed to your origin, you must still explicitly request it from the hosting origin using the `fromOrigins` option in `getTools()`.”[^ch07-9] Table 7.2 puts the three opt-ins side by side.

**Table 7.2 — The three opt-ins for a cross-origin tool**

| Gate | Who decides | Mechanism | Default | Failure |
|---|---|---|---|---|
| 1. Delegation | The embedder (Ledgerly) | `Permissions-Policy` header and `allow="tools"` on the iframe | `'self'`: top-level and same-origin frames only | `NotAllowedError` from any method |
| 2. Exposure | The tool provider (Supportly) | `registerTool(tool, { exposedTo })` | Same-origin callers only | The tool is silently absent from the consumer’s list |
| 3. Request | The tool consumer (Ledgerly’s agent) | `getTools({ fromOrigins })` | Same-origin documents only | The document’s tools are silently absent |

Two things about the table are easy to miss. First, gates 2 and 3 fail silently. A tool you didn’t expose, or an origin you didn’t ask for, simply isn’t in the list, and no error tells you why. When a cross-origin tool is missing, check all three gates in order. Second, gate 3 exists so that a page isn’t flooded with tools it never asked for. The next section explains why, in the specification’s own words.

Both directions work, by the way. Exposure is about origins, not about who embeds whom. In the tests, Ledgerly registered a tool with `exposedTo: [Supportly’s origin]`, and the widget, asking with `fromOrigins: [Ledgerly’s origin]`, found and called it. A vendor widget could use that to ask the host for context (“which invoice is the user looking at?”) without a custom `postMessage` protocol. A tool Ledgerly registered without `exposedTo` stayed invisible to the widget.

`exposedTo` also drives events. When a tool is registered, the browser notifies every document in the tree that is allowed to use `tools` and to which the tool is exposed, by firing `toolchange` at its `ModelContext`.[^ch07-18] In the tests, Ledgerly’s `toolchange` listener fired when the widget registered its exposed tools. The event carries no details, so a listener has to call `getTools()` again to find out what changed. Listing 7.5 does exactly that.

### What the specification now says about it

In the first edition this was a “Still in flux” box: §6.3.4 of the 15 October draft, then titled “Violation of Same-Origin Boundaries”, had only a placeholder line where the text should be. On 27 October 2026 pull request #326 replaced it with a full section, “Interaction with the Same-Origin Policy”.[^ch07-17] It describes exactly the model of this chapter, and I recommend reading it in full. Three points from it are worth having in your head.

The reason for strictness. A registered tool’s `execute` callback “always runs within the registering Document’s execution context, with full access to that origin’s DOM, storage, and ambient credentials.” So letting a cross-origin document discover a tool, invoke it and receive its result “crosses a privilege boundary.” By default WebMCP enforces “strict same origin isolation”, and cross-origin documents can’t discover, observe `toolchange` events for, or execute a tool “unless three independent access-control gates are satisfied” — the embedder’s delegation, the provider’s `exposedTo` and the consumer’s `fromOrigins`.[^ch07-19]

Why both sides have to agree. The section calls this “Why Two-Sided Opt-In Matters”: mutual consent “prevents both unauthorized cross-origin actuation and unsolicited tool-list pollution.” Without the provider’s opt-in, a malicious parent page could invoke internal tools inside an embedded third-party widget. Without the consumer’s opt-in, a compromised iframe “could unilaterally expose tools with deceptive names or prompt-injected descriptions” into the parent’s `getTools()` results.[^ch07-19] The section’s own code example is a parent at `https://app.example.com` calling `getTools({ fromOrigins: [...] })` and a widget at `https://widget.example.org` registering with `exposedTo` — Ledgerly and Supportly under other names.

What stays risky. The section names two residual risks. Even after mutual opt-in, the two origins remain separate trust domains: providers must treat arguments as untrusted input, callers must treat cross-origin descriptions and results as untrusted data, and callers should inspect `origin` and `source` on each `Tool` to tell same-named tools apart (the 27 October draft said `window` on each `RegisteredTool`). Listing 7.5 keys tools by origin and name.[^ch07-19] And an agent working across several origins may carry state from one into tool calls on another. The spec calls this “a general risk of agentic browsing across the web rather than a WebMCP-specific threat.”[^ch07-19] Chapter 12 picks up both.

## `getTools()` and `executeTool()`: building an in-page agent

With the gates open, Ledgerly can build its assistant. The two methods are small. Listing 7.4 is their shape in the 23 November 2026 draft. The 27 October draft used a `RegisteredTool` dictionary here. Appendix E is the migration.

**Listing 7.4** `ModelContext` — discovery and execution, from the specification’s IDL (23 November 2026 draft, abridged)

```webidl
partial interface ModelContext {
  Promise<sequence<Tool>> getTools(optional ModelContextGetToolOptions options = {});
  Promise<DOMString> executeTool(Tool tool,
                                 optional object inputObject,
                                 optional ModelContextExecuteToolOptions options = {});
};

dictionary ModelContextGetToolOptions { sequence<USVString> fromOrigins; };
dictionary ModelContextExecuteToolOptions { AbortSignal signal; };

[Exposed=Window, SecureContext]
interface Tool {
  readonly attribute DOMString name;
  readonly attribute DOMString title;
  readonly attribute DOMString description;
  readonly attribute object? inputSchema;
  readonly attribute object? outputSchema;
  readonly attribute WindowProxy? source;
  readonly attribute USVString origin;
  readonly attribute object? annotations;
};
```

(The real IDL declares both methods on `ModelContext` itself. `partial` here just leaves out what Chapter 5 already covered.)[^ch07-20]

### What `getTools()` returns

`getTools()` resolves to a list of `Tool` objects.[^ch07-21] Most members repeat what the tool’s owner registered: `name`, `title`, `description`, a deep copy of `inputSchema` and of `outputSchema`, and the annotations. A schema or an annotations object that was not provided is `null`, not `undefined`. A missing `title` is still `""`. Two members locate the tool:

- `source` is the `WindowProxy` of the document that registered the tool, or `null` if that document is no longer fully active. In Chromium 156 the member was `window`, and in the tests it was strictly equal to the iframe’s `contentWindow`. This edition has not re-tested that equality for `source` on Chrome 160. The specification’s getter returns that browsing context’s `WindowProxy`.
- `origin` is the serialized origin of that document. The draft explains that it matters for cross-origin tools, because the consumer cannot otherwise get the tool’s origin from `source`.[^ch07-21]

Read `source` with the fallback in Appendix E (`tool.source ?? tool.window`) until Chrome 160 is stable on 5 January 2027. Do not `JSON.stringify` a `Tool` or spread it. Both produce an empty result, and `structuredClone` throws.[^ch07-32]

The list covers every document in the caller’s *top-level* frame tree: the method walks the inclusive descendants of the tab’s top-level document, not just the caller’s own descendants.[^ch07-8] That is why the widget, a child frame, could find Ledgerly’s tools above it. Documents in other tabs, popups and openers aren’t included. Issue #227, open since 21 July 2026, argues that discovery should cover the whole browsing context group, and it now has a concrete proposal attached (more on that at the end of the chapter).[^ch07-22] The list is sorted by tool name across all frames, which the tests confirmed: Ledgerly’s `find_invoice` came back between Supportly’s `create_ticket` and `get_ticket_status`. Don’t rely on list position to tell frames apart.

And that leads to a practical problem. Two frames can register tools with the same name. Supportly has `search_articles`, and a documentation widget from another vendor might have one too. Names are unique only within one document’s tool map. A consumer that hands tools to a language model needs names that are unique across the page, so Listing 7.5 keys each tool by vendor and name.

**Listing 7.5** `ledgerly/agent/discover.js` — Ledgerly’s agent discovers the tools it may use

```js
// Ledgerly's in-page agent: find the tools it is allowed to use.
const SUPPORTLY = 'https://widget.supportly.example';

export async function discoverTools() {
  // Same-origin tools come back by default; Supportly's only if we ask
  // for its origin AND Supportly exposed them to us.
  const tools = await document.modelContext.getTools({ fromOrigins: [SUPPORTLY] });

  // Key every tool by origin + name: two frames may both register "search".
  const catalog = new Map();
  for (const tool of tools) {
    const vendor = tool.origin === location.origin ? 'ledgerly' : 'supportly';
    catalog.set(`${vendor}__${tool.name}`, tool);
  }
  return catalog;
}

export function watchTools(onChange, signal) {
  let pending = null;
  document.modelContext.addEventListener('toolchange', () => {
    // toolchange carries no details, and frames register tools one by one,
    // so coalesce bursts and re-read the whole list.
    clearTimeout(pending);
    pending = setTimeout(async () => onChange(await discoverTools()), 50);
  }, { signal });
}
```

`watchTools()` debounces `toolchange`. In the tests the widget registered its three tools one after another, and Ledgerly received a separate event for each. Re-reading the list once after the burst is cheaper than three times, and the draft itself warns that the timing of `toolchange` relative to other tasks “cannot be relied upon.”[^ch07-18]

### What `executeTool()` does

`executeTool(tool, input, { signal })` runs a tool “on the document it was registered on” and resolves to “the stringified result of the tool’s execution.”[^ch07-20] Chapter 6 followed a call from the agent’s side, so here are only the cross-origin details.

**It takes the object `getTools()` returned, not a dictionary you built.** The argument is a `Tool`. Callers cannot fabricate one. `executeTool()` looks the tool up by the internal id stored on that object, not by name. If the tool has been unregistered, the call rejects with `NotFoundError` even when a new tool has since been registered under the same name.[^ch07-23] In Chromium 156, when the value was still a `RegisteredTool` dictionary, a shallow copy of a tool from `getTools()` executed normally (tested). That copy is not a `Tool`, and it will not keep working on Chrome 160.

**It doesn’t let you probe.** If the id is gone, or the tool is not exposed to the caller, the draft rejects with the same `NotFoundError`, so the caller cannot tell those two cases apart.[^ch07-23] The 27 October draft used that same error name to stop a caller from probing with a fabricated dictionary. Chromium 156 gave one answer for a made-up `name` and a forged `origin`, only under a different name: both rejected with `UnknownError` and the message “The operation failed for an unknown transient reason” (tested). The draft itself used `UnknownError` for these cases until 8 October 2026, when pull request #339 (commit b206dae) replaced it with `NotFoundError` and the other specific names, and Chromium 156 still implements the older text.[^ch07-30]

> **Note:** Pull request #348 merged on 19 November 2026. Chrome 160.0.8173.0 is where `Tool` replaces `RegisteredTool`. Appendix E has the fallback. Issue #349, executing a tool whose document has an opaque origin, is still unresolved: `executeTool()` rejects that case with `NotSupportedError`.[^ch07-31] Listings 7.5 to 7.7 already pass through the object `getTools()` returned, which is what the new interface requires.

**Only a name crosses back.** When a tool fails, the caller sees a `DOMException` whose name comes from a small table of platform failures. The draft says that passing only the error’s name, rather than “any internal JavaScript exception object or message thrown in targetDocument,” prevents “leaking provider implementation details or stack traces across origins.”[^ch07-23] The tests checked this from the attacker’s side: the widget registered a tool that threw `new Error('db password is hunter2')`, and Ledgerly’s agent got `UnknownError: Tool was executed but the invocation failed…` with no trace of the message. Recoverable failures still belong in the return value, as Listing 7.3 does with `{ status: 'error', code: 'INVALID_INPUT', message: '"priority" must be low, normal or high.' }`, using the result vocabulary Chapter 11 sets out.

**Cancellation crosses origins.** The caller’s `signal` is wired to the target. In the tests, aborting Ledgerly’s controller rejected `executeTool()` with an `AbortError` in Ledgerly, aborted the `signal` that Supportly’s `execute` callback received, and fired `toolcancel` at the widget’s `ModelContext`. The widget’s confirmation card disappeared, as Listing 7.3 intended. This matches the draft’s cancellation steps exactly.[^ch07-24] Chapter 6 covers cancellation in full, including why a cancelled tool may still finish its work.

Listing 7.6 wraps all of that into one function the agent loop can call.

**Listing 7.6** `ledgerly/agent/run-tool.js` — running a tool with a deadline, a stop button and honest errors

```js
// Run one tool for the in-page agent, with a deadline and a stop button.
export async function runTool(tool, input, { stop, timeoutMs = 15000 } = {}) {
  const signal = AbortSignal.any([stop, AbortSignal.timeout(timeoutMs)]);
  const hints = tool.annotations ?? {};
  try {
    const text = await document.modelContext.executeTool(tool, input, { signal });
    let value = text;
    try { value = JSON.parse(text); } catch { /* plain string result */ }
    return {
      ok: true,
      origin: tool.origin,
      // Content the tool owner itself doesn't vouch for: label it, never obey it.
      untrusted: hints.untrustedContentHint === true,
      value,
    };
  } catch (err) {
    // Across origins you only ever get an exception name, never the message
    // or stack from the other document.
    const reason = signal.aborted
      ? (stop.aborted ? 'stopped by user' : 'timed out')
      : err.name;
    return {
      ok: false,
      origin: tool.origin,
      reason,
      // Never retry something with real-world effects on your own.
      retryable: !hints.consequentialHint && reason !== 'stopped by user',
    };
  }
}
```

`AbortSignal.any()` combines the user’s stop button with a timeout, so one signal covers both. When the call fails, the code checks the signal first: a timeout and a user’s stop both reject with an abort-type error, and the agent needs to know which one it was. Results flagged with `untrustedContentHint` are labelled, so the planner can treat them as data rather than instructions. Tools flagged as consequential are never retried automatically. Why? If `create_ticket` timed out, the user may have clicked Send a moment too late, and a retry could open a second ticket.

Table 7.3 collects what the tests observed when cross-origin calls went wrong, next to what the draft specifies.

**Table 7.3 — Cross-origin call failures: the 27 October 2026 draft and Chromium 156 (tested)**

| Situation | Draft | Chromium 156 |
|---|---|---|
| The tool’s `execute` throws | `OperationError` (“tool rejected”) | `UnknownError`, generic message |
| Forged `name` or forged `origin` | `NotFoundError` | `UnknownError` (same message for both) |
| Caller aborts its signal | Rejects with the signal’s reason, target gets `toolcancel` | `AbortError`, target’s signal aborted, `toolcancel` fired |
| Target iframe navigates away mid-call | `AbortError` (“target document unloaded”) | `UnknownError` |
| Target iframe removed mid-call | `AbortError` (“target document unloaded”) | `UnknownError` |
| Non-secure origin in `exposedTo` / `fromOrigins` | `SecurityError` | `SecurityError` |
| Calling document blocked by policy | `NotAllowedError` | `NotAllowedError` |

Sources: the draft’s tool execution error table and method steps,[^ch07-25] and the Chromium results from this chapter’s tests, re-run on 2 November 2026. Every `UnknownError` in the Chromium column is a case the draft named `UnknownError` until 8 October 2026.[^ch07-30]

Chrome’s guide adds one more case: `executeTool()` returns “null when a navigation is triggered.”[^ch07-9] In this chapter’s test, where the *widget’s* tool navigated the widget’s own frame, the caller got `UnknownError` and not `null`. Treat both as “the call didn’t complete, check the page”, and design consequential tools so that a lost answer can be checked afterwards: `create_ticket` returns a ticket ID, and `get_ticket_status` can confirm it.

### The loop

An in-page agent is a loop: show the model the tools, let it choose, run the choice, feed the result back, repeat. Listing 7.7 is Ledgerly’s. The planner is deliberately abstract. It could be a server-side model, Chrome’s built-in Prompt API (whose tool-use mode the Chrome team’s example extension can use behind a flag[^ch07-26]), or, as in the demos repository, a rule-based stand-in that keeps the tests deterministic. Chapter 14 builds a real test agent.

**Listing 7.7** `ledgerly/agent/agent-loop.js` — a minimal in-page agent loop

```js
// A minimal in-page agent loop. The planner (a model) chooses; this code acts.
import { discoverTools } from './discover.js';
import { runTool } from './run-tool.js';

export function toFunctionDeclarations(catalog) {
  return [...catalog].map(([alias, tool]) => ({
    name: alias,
    description: `${tool.description} (provided by ${tool.origin})`,
    parameters: tool.inputSchema ?? { type: 'object', properties: {} },
  }));
}

export async function runAgent(goal, planner, { stop, maxSteps = 6, onStep = () => {} }) {
  const history = [{ role: 'user', text: goal }];
  for (let step = 0; step < maxSteps && !stop.aborted; step++) {
    const catalog = await discoverTools();          // tools can change between steps
    const decision = await planner.next({ history, tools: toFunctionDeclarations(catalog) });

    if (decision.answer !== undefined) {
      history.push({ role: 'agent', text: decision.answer });
      onStep({ type: 'answer', text: decision.answer });
      return history;
    }

    const tool = catalog.get(decision.call);
    const result = tool
      ? await runTool(tool, decision.args ?? {}, { stop })
      : { ok: false, reason: `no tool called ${decision.call}`, retryable: false };
    history.push({ role: 'tool', name: decision.call, result });
    onStep({ type: 'tool', name: decision.call, result });
  }
  return history;
}
```

Three choices in Listing 7.7 are worth copying. The catalog is rebuilt on every step, because frames come and go and tools appear after navigations. The tool’s origin is appended to the description the model sees, so a tool called `delete_everything` from an unexpected origin at least *looks* unexpected. And the planner never touches `executeTool()` itself: it returns a decision, and code that knows the rules about consequential tools and timeouts carries it out.

![Figure 7.2 — The Helpdesk Widget at runtime: Ledgerly’s in-page agent discovers tools in two origins, runs create_ticket in Supportly’s frame, and the user confirms inside the widget.](images/figure-7-2.png)

The demos repository runs exactly this flow. A test asks Ledgerly’s agent to “open a ticket: CSV export is missing the VAT column,” waits for the confirmation card to appear inside Supportly’s frame, clicks Send there, and checks that the agent got back `{ status: 'created' }` with a ticket ID such as `SUP-1043`.

## Extensions as agents

The specification names two consumers, the browser agent and in-page agents. The explainer names a third. Its opening says that tools “can be invoked by AI agents, including those built into the browser, hosted in iframes, or running in extensions.”[^ch07-27] The extension is the shape many early WebMCP agents have taken, including the Chrome team’s own example: an agent in a side panel that “reads `document.modelContext.getTools()` and listens for `ontoolchange`, in the top page and in same-origin and cross-origin iframes.”[^ch07-26]

### Content scripts can already use the API

There is no extension-specific WebMCP API yet. An extension uses the page API through a content script, and Chrome’s security guide says so in a note: “Chrome Extensions can query and execute WebMCP tools using content scripts.”[^ch07-13] Content scripts “live in an isolated world,” a private JavaScript environment that shares the page’s DOM but not its globals, and a manifest can inject them into every frame with `"all_frames": true`.[^ch07-28] Whether `document.modelContext` works from an isolated world wasn’t stated in any source I could find, so I tested it. It does: in Chromium 156 with the testing flag, a content script of an unpacked Manifest V3 extension called `getTools()` and `executeTool()` successfully, from the top frame and from inside Supportly’s cross-origin frame (tested).

Please note one data point that doesn’t match. On 20 October 2026, Kenneth Christiansen, who works on an extension that consumes WebMCP tools, wrote in issue #74 that “today we have to inject a script into the page’s own world to reach `document.modelContext`, which any page script can see and interfere with.”[^ch07-29] I can’t tell from the comment which Chrome build or setup that refers to, and I tested only a page with the testing flag on, not one that enables WebMCP through an origin-trial token. If your extension targets origin-trial pages, test the isolated world there before you rely on it.

Listings 7.8 to 7.10 are a minimal tool inspector built that way.

**Listing 7.8** `extension/manifest.json` — the extension’s manifest

```json
{
  "manifest_version": 3,
  "name": "Tool Inspector",
  "version": "0.1.0",
  "description": "Lists and runs the WebMCP tools of every frame on a page.",
  "background": { "service_worker": "background.js" },
  "content_scripts": [{
    "matches": ["https://app.ledgerly.example/*", "https://widget.supportly.example/*"],
    "js": ["content-script.js"],
    "all_frames": true,
    "run_at": "document_idle"
  }]
}
```

**Listing 7.9** `extension/content-script.js` — the content script, one instance per frame

```js
// Runs in every matching frame, in the extension's isolated world.
// It shares the frame's DOM and origin, so it sees the frame's own tools.
async function report() {
  if (!('modelContext' in document)) return;
  try {
    const tools = await document.modelContext.getTools();
    chrome.runtime.sendMessage({
      type: 'tools',
      origin: location.origin,
      tools: tools
        // `source` on Chrome 160, `window` before it. Remove the
        // fallback when Chrome 160 reaches Stable (5 January 2027).
        .filter((t) => (t.source ?? t.window) === window)
        .map((t) => ({
          name: t.name,
          description: t.description,
          inputSchema: t.inputSchema ?? null,
          annotations: t.annotations ?? null,
        })),
    });
  } catch (err) {
    chrome.runtime.sendMessage({ type: 'tools', origin: location.origin, error: err.name });
  }
}

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (msg.type !== 'execute') return;
  (async () => {
    const tools = await document.modelContext.getTools();
    const tool = tools.find((t) => t.name === msg.name && (t.source ?? t.window) === window);
    if (!tool) return reply({ error: 'NotFound' });
    try {
      reply({ result: await document.modelContext.executeTool(tool, msg.args) });
    } catch (err) {
      reply({ error: err.name });
    }
  })();
  return true;   // we will reply asynchronously
});

document.modelContext?.addEventListener('toolchange', report);
report();
```

**Listing 7.10** `extension/background.js` — the service worker keeps the catalog and runs tools

```js
// Service worker: keeps the latest tool list per frame, runs tools on request.
const frames = new Map();   // "tabId:frameId" -> { origin, tools }

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.type !== 'tools') return;
  frames.set(`${sender.tab.id}:${sender.frameId}`, {
    origin: msg.origin, tools: msg.tools ?? [], error: msg.error,
  });
});

// Called by the extension's own UI (a side panel, say) with a user's request.
async function runTool(tabId, frameId, name, args) {
  return chrome.tabs.sendMessage(tabId, { type: 'execute', name, args }, { frameId });
}

self.toolInspector = { frames, runTool };
```

The design runs one content script in each frame and has each script report only its own frame’s tools, filtered with `(tool.source ?? tool.window) === window`. The fields are copied onto a plain object before `sendMessage`, because a `Tool` is not structured-cloneable. In Chromium 156 the `window` member of a tool from the content script’s own frame was strictly equal to the content script’s `window` (tested). The `source` comparison is what the 23 November specification specifies, and it was not re-tested on Chrome 160 for this edition. The service worker then knows every frame’s tools, keyed by tab and frame ID, and can run a tool in a specific frame with `chrome.tabs.sendMessage(…, { frameId })`. In the test, the worker’s catalog showed Ledgerly’s frame with `find_invoice` and Supportly’s frame with its three tools, and a `search_articles` call routed to Supportly’s frame came back with the article about bank feeds.

### Notice what that bypassed

Look again at what the content script in Supportly’s frame did. It called `getTools()` with no `fromOrigins`, and it saw Supportly’s tools anyway. A content script runs with the origin of the frame it’s injected into, so for the browser it is a same-origin caller, and same-origin callers see every tool in the document, exposed or not. Gates 2 and 3 are about origins on the page, and an extension with access to both origins simply stands on both sides. Gate 1 still applies, because a frame that isn’t allowed to use `tools` can’t register anything for the extension to find.

Is this a hole in WebMCP? Not really. Chrome’s security guide points out that extensions with host permissions “can manipulate the page by running custom JavaScript, even without WebMCP.”[^ch07-13] An extension that can inject scripts into Supportly’s frame could click Supportly’s buttons too. But it does change what `exposedTo` means: it limits which *web origins* can use your tools, not which *software on the user’s machine* can. Treat it as an access-control list for in-page agents, not as a secret. The consequential parts of your tools, such as Listing 7.3’s confirmation card, are what protect the user from any agent.

### A WebExtensions API, maybe

Issue #74, opened on 3 February 2026, suggests that the specification’s authors work with the WebExtensions Community Group on “an API exposed to browser extensions that allows them to enumerate and invoke tools defined with WebMCP.” An earlier comment asked whether such an API is still needed, given that an extension can already run script that calls `executeTool()` in the page. The October comment quoted above answers from practice: a dedicated API would let an extension “list, observe and call a tab’s tools” with tab, frame and document identity on every tool and call. The topic had a TPAC breakout session, and the issue was still open on 2 November 2026.[^ch07-29] Listing 7.9 is a practical response in code: it works, but every extension has to reinvent per-frame bookkeeping and cross-world messaging, and the browser can’t tell an extension’s calls apart from the page’s own.

> **Still in flux:** Nothing in the 27 October 2026 draft mentions extensions. Whether content scripts keep their access, whether extension calls will be labelled or permission-gated, and whether a dedicated `chrome.*` or `browser.*` API appears are all open (issue #74).[^ch07-29] The behaviour described above was observed in Chromium 156 with the testing flag only.

## Design note: is this really a general communication primitive?

Strip away the language-model vocabulary and look at what this chapter built. One document registers named functions with JSON-described inputs. Another document, in a different origin, lists them, calls one with a JSON object, can cancel the call, and gets a string back. Both sides opt in by origin, and the embedder holds a veto. That is a cross-origin remote procedure call mechanism, with better access control than most hand-written `postMessage` protocols.

Jake Archibald made that observation in issue #236 on 3 August 2026. Calling functions across windows and workers is “a pain,” he wrote, which is why libraries such as Comlink exist. WebMCP’s registration plus per-origin exposure is most of a built-in Comlink, and the language-model use could “just fall out of the other capabilities.” He went further: service workers could register tools without any window open, and tools could be exposed “to the browser,” and through it to WebDriver and other tooling.[^ch07-1] The issue got busy again after TPAC. On 30 October the discussion turned to what the permissions policy should mean if tools become generic communication (the second-policy idea from the box above), and it was still open on 2 November.[^ch07-1]

There are good arguments both ways. In favour: a general primitive would get more scrutiny and more users, the same cross-origin rules would serve the Helpdesk Widget whether or not a model is involved, and Ledgerly’s widget-to-host context tool from earlier in this chapter is already a non-agent use. Against: everything about WebMCP’s design is shaped by the fact that a probabilistic model chooses the calls. Natural-language descriptions, annotations such as `untrustedContentHint` and `consequentialHint`, and the security section’s long discussion of prompt injection make little sense for a plain RPC library, and a general primitive would invite developers to expose functions that were never written with an agent in mind.

My view, for what it’s worth: build your tools as if the general reading might win, because good practice is the same either way. Validate every input in code, make consequential actions confirm in your own UI, return errors as values, and expose tools to as few origins as you can. Those habits hold up whether the caller is Chrome’s assistant, Ledgerly’s agent, an extension or a test harness.

### Where the consumer API may be heading

Issue #227 deserves a closer look, because its proposal touches every listing in the second half of this chapter. On 26 October 2026, following a Community Group resolution, Khushal Sagar posted a concrete design.[^ch07-22] `document.modelContext` would keep only the provider side: `registerTool()` and the `toolactivated` and `toolcancel` events. The consumer side (`getTools()`, `executeTool()` and `toolchange`) would move to a new object, provisionally called `ModelContextClient`, available as `modelContextClient` on any window the caller holds a reference to, so `window.parent.modelContextClient` or `window.opener.modelContextClient`. `exposedTo` would still decide which tools a consumer sees. The same shape would extend to workers, which could register tools on their own global, with the page reaching them through `new Worker(…).modelContextClient` or the service worker controller. Mozilla’s Benjamin VanderSloot agreed with “the bulk of the proposal” while noting that openers increase the attack surface.

Nothing of this is in the draft. If it lands, Listing 7.5 would call `getTools()` on a client object instead of `document.modelContext`, and discovery would reach beyond one tab’s frame tree. The three gates, `origin` and `source`, the name-only errors and the advice in this chapter would all carry over. That worker idea is close to Jake Archibald’s “general way to call functions in other environments.” Pull request #375 is the explainer that writes this direction down. It was open on 23 November 2026 and is not the API in this chapter (Appendix F).

> **Still in flux:** Three open items could still change this chapter’s API surface: #236 (reposition WebMCP as a general cross-environment call mechanism, and possibly a second permissions policy),[^ch07-1] #227 (discovery across the browsing context group, with the `ModelContextClient` proposal),[^ch07-22] and #317 (let the host decide which frames may expose and use tools, and possibly allow `*` in `exposedTo`).[^ch07-12] Those three were still open on 2 November 2026, and #236’s explainer, pull request #375, was still open on 23 November 2026. The `Tool` interface is no longer in that list. Pull request #348 merged on 19 November 2026.[^ch07-31]

## The Helpdesk Widget so far

The demos repository folder `chapters/07-frames-origins-agents/` contains everything in this chapter as runnable code. `npm start` serves Ledgerly on `http://localhost:47101` and Supportly on `http://127.0.0.1:47102`, two different origins that are both potentially trustworthy, and rewrites the production origins in the listings to those local ones as it serves them. The files themselves matched the listings on that date. Listing 7.9 has since grown a `source ?? window` fallback for Chrome 160 (Appendix E). That fallback was not part of the 2 November run. On Chromium 156 it still selects the same tools, because `source` is absent and `window` is the member the tests compared. A few small files that the book doesn’t print fill the gaps: the widget’s page and its in-memory helpdesk backend, the confirmation card, Ledgerly’s assistant wiring and its rule-based planner, and a dev-only `document.modelContext` mock. The folder’s README maps every file to its listing.

`npm test` runs 30 checks: syntax checks for every script and the manifest, a unit test of the agent loop against the mock, 17 behavioural tests in Chromium 156 with WebMCP enabled across the two origins (Tables 7.1 and 7.3 come from them), and one test that loads Listings 7.8 to 7.10 as an unpacked extension in full Chromium. All 30 passed on 2 November 2026.

Chapter 11 returns to the widget to ask how its tools should be designed and described, Chapter 12 uses it to model cross-origin threats, and Chapter 14 tests it.

## Chapter summary

- A page is a tree of documents, each with its own `ModelContext`. The browser agent observes the tools of every frame, labelled by origin. In-page agents use `getTools()` and `executeTool()` and are bound by the same-origin rules below.
- **Gate 1, delegation.** The `tools` Permissions Policy defaults to `'self'`. Cross-origin iframes need `allow="tools"`, and the `Permissions-Policy` header sets the ceiling for the whole page: `tools=(self "https://widget.supportly.example")` limits delegation to one vendor, and `tools=()` turns WebMCP off for the page and every frame. A blocked call rejects with `NotAllowedError`, while `'modelContext' in document` stays `true`, so catch the error.
- **Gate 2, exposure.** `registerTool(tool, { exposedTo })` lists the origins that may see and call a tool. Same-origin callers always can. Non-secure origins reject with `SecurityError`, and there is no wildcard.
- **Gate 3, request.** `getTools({ fromOrigins })` lists the origins the caller wants tools from. Gates 2 and 3 fail silently: a missing tool just isn’t in the list.
- Since 27 October 2026 the specification explains the model in §6.3.4, “Interaction with the Same-Origin Policy”: three independent gates, two-sided opt-in against both unauthorized actuation and tool-list pollution, and residual risks that remain after both sides agree.
- `getTools()` covers the whole top-level frame tree, sorted by name, and each `Tool` carries `source` and `origin` (`window` before Chrome 160). Key tools by origin and name, because names are unique only per document. `toolchange` tells you to re-read the list, not what changed. Pass the object `getTools()` returned to `executeTool()`. Do not rebuild it.
- `executeTool()` returns a string, passes cancellation through to the target (`toolcancel`), and lets only an exception name cross origins. The draft uses one `NotFoundError` for forged names, forged origins and unexposed tools. Chromium 156 uses `UnknownError` for those and for thrown errors, navigations and removed frames, because it still follows the draft as it was before 8 October 2026.
- Extensions can use the page API from content scripts, in every frame (tested with the testing flag). A content script counts as same-origin with its frame, so it sees tools whatever their `exposedTo`. `exposedTo` limits web origins, not installed software.
- Still open: a dedicated WebExtensions API (#74), discovery beyond one tab and a separate consumer object (#227), host control and possibly a second policy (#317, #236), and whether WebMCP becomes a general cross-environment call mechanism (pull request #375, Appendix F). The `Tool` interface (#348) merged on 19 November 2026.

Chapter 8 turns from JavaScript to HTML: the declarative API, which lets a form become a tool.

## Notes

[^ch07-1]: Jake Archibald, “Reposition feature as a generic communication tool?”, webmachinelearning/webmcp issue #236, opened 3 August 2026, open as of 2 November 2026, with the post-TPAC comments of 25 and 30 October 2026 by Benjamin VanderSloot (Mozilla), Johann Hofmann (Google) and others. <https://github.com/webmachinelearning/webmcp/issues/236>
[^ch07-2]: WebMCP specification, Draft Community Group Report, 27 October 2026, §4.1 Extensions to Document and §4.2 ModelContext interface (including the non-normative descriptions of `getTools()` and `executeTool()`). Retrieved November 2026. <https://webmachinelearning.github.io/webmcp/#model-context-container>
[^ch07-3]: WebMCP specification, Draft Community Group Report dated 27 October 2026, editors Brandon Walderman (Microsoft), Khushal Sagar (Google), Dominic Farolino (Google) and Samuel Dallstream (Microsoft, added 20 October 2026), published by the W3C Web Machine Learning Community Group. Retrieved November 2026. <https://webmachinelearning.github.io/webmcp/>
[^ch07-4]: Chrome for Developers, “WebMCP” overview (published 18 May 2026, last updated 7 October 2026, retrieved November 2026), section “Local WebMCP”: the `chrome://flags/#enable-webmcp-testing` flag. <https://developer.chrome.com/docs/ai/webmcp>
[^ch07-5]: WebMCP specification, 27 October 2026, §5.2 Page observations (non-normative): the browser agent “does not run JavaScript on the page”, the observation walks the inclusive descendant navigables, and each observed tool collection carries an origin. <https://webmachinelearning.github.io/webmcp/#observations>
[^ch07-6]: WebMCP specification, 27 October 2026, §4.4 Permissions policy integration. <https://webmachinelearning.github.io/webmcp/#permissions-policy>
[^ch07-7]: WebMCP specification, 27 October 2026, §4.2, the `registerTool()`, `getTools()` and `executeTool()` method steps (`NotAllowedError` when the document is not allowed to use “tools”, `SecurityError` for origins that fail to parse or are not potentially trustworthy). <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool>
[^ch07-8]: WebMCP specification, 27 October 2026, §4.2, `getTools()` method steps: traversal of the top-level traversable’s inclusive descendant navigables, the “tools” check per document, the same-origin-or-`fromOrigins` check, the exposure check, and sorting by name. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-gettools>
[^ch07-9]: Chrome for Developers, “Imperative API”, WebMCP documentation (published 18 May 2026, last updated 16 October 2026, retrieved November 2026), sections on discovering tools, executing tools and cross-origin iframes. <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
[^ch07-10]: MDN Web Docs, “Permissions-Policy header”: syntax, allowlist values (`*`, `()`, `self`, `src`, quoted origins), and `src` as the default allowlist in an `<iframe>` `allow` attribute. Read 14 October 2026. <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy>
[^ch07-11]: WebMCP specification, 27 October 2026, §6.4.1 Disabling WebMCP with Permissions Policy. <https://webmachinelearning.github.io/webmcp/#mitigation-disable-permissions-policy>
[^ch07-12]: “Host-controlled WebMCP access between iframes”, webmachinelearning/webmcp issue #317, opened 23 September 2026, open as of 2 November 2026, including Khushal Sagar’s comment of 26 October 2026 on `*` in `exposedTo`. <https://github.com/webmachinelearning/webmcp/issues/317>
[^ch07-13]: Chrome for Developers, “WebMCP tool security” (published 9 June 2026, last updated 1 September 2026, retrieved November 2026), the section on exposing tools carefully and its note on Chrome Extensions. <https://developer.chrome.com/docs/ai/webmcp/secure-tools>
[^ch07-14]: WebMCP specification, 27 October 2026, §4.2.3 ModelContextRegisterToolOptions Dictionary. <https://webmachinelearning.github.io/webmcp/#model-context-register-tool-options>
[^ch07-15]: WebMCP specification, 27 October 2026, §4.2.4 ModelContextGetToolOptions Dictionary. <https://webmachinelearning.github.io/webmcp/#model-context-get-tool-options>
[^ch07-16]: WebMCP specification, 27 October 2026, §4.2, “determine if a tool is exposed to an origin”. <https://webmachinelearning.github.io/webmcp/#tool-is-exposed-to-an-origin>
[^ch07-17]: Julia Pagnucco, “Document cross-origin tool exposure and two-sided opt-in in Section 6.3.4”, webmachinelearning/webmcp pull request #326, opened 28 September 2026, merged 27 October 2026. <https://github.com/webmachinelearning/webmcp/pull/326>
[^ch07-18]: WebMCP specification, 27 October 2026, §4.2, “notify documents of a tool change”, including the note on `toolchange` timing. <https://webmachinelearning.github.io/webmcp/#notify-documents-of-a-tool-change>
[^ch07-19]: WebMCP specification, 27 October 2026, §6.3.4 Interaction with the Same-Origin Policy, §6.3.4.1 Enforcing Same-Origin Isolation via Two-Sided Opt-In and §6.3.4.2 Residual Risks. Retrieved November 2026. <https://webmachinelearning.github.io/webmcp/#interaction-with-same-origin-policy>
[^ch07-20]: WebMCP specification, Draft Community Group Report, 23 November 2026, §4.2 ModelContext Interface (IDL) and §4.2.4–§4.2.6 (retrieved 23 November 2026). The 27 October 2026 draft had the same methods with `RegisteredTool` in place of `Tool`. <https://webmachinelearning.github.io/webmcp/#model-context-container>
[^ch07-21]: WebMCP specification, 23 November 2026, §4.2.6 Tool Interface, including `source`, `origin`, and `null` for a missing schema or annotations (retrieved 23 November 2026). The 27 October draft called this dictionary `RegisteredTool` and named the window member `window`. <https://webmachinelearning.github.io/webmcp/#tool-interface>
[^ch07-22]: “Tool discovery should not be limited to a single traversable navigable”, webmachinelearning/webmcp issue #227, opened 21 July 2026, open as of 2 November 2026, including Khushal Sagar’s proposal of 26 October 2026 (`ModelContextClient`) and the replies of 30 October 2026. <https://github.com/webmachinelearning/webmcp/issues/227>
[^ch07-23]: WebMCP specification, 23 November 2026, §4.2, `executeTool()` method steps: lookup by the `Tool`’s internal id, `NotFoundError` when that id is gone or the tool is not exposed, and the note that callers cannot fabricate a `Tool` (retrieved 23 November 2026). The 27 October draft described the same error as a defence against fabricated `RegisteredTool` dictionaries. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-executetool>
[^ch07-24]: WebMCP specification, 27 October 2026, §3.1 Pending tool executions (“cancel a pending tool execution”) and §4.3.2 ToolCancelEvent Interface. <https://webmachinelearning.github.io/webmcp/#pending-tool-executions>
[^ch07-25]: WebMCP specification, 27 October 2026, §3 Supporting concepts, the tool execution error table, and §3.1 unloading document cleanup steps. <https://webmachinelearning.github.io/webmcp/#supporting-concepts>
[^ch07-26]: GoogleChromeLabs, “Example Agentic Chrome Extension to test WebMCP”, README (retrieved November 2026), including the on-device backend’s `chrome://flags/#prompt-api-tool-use` requirement. <https://github.com/GoogleChromeLabs/webmcp-extension>
[^ch07-27]: WebMCP explainer, README of webmachinelearning/webmcp (retrieved November 2026). <https://github.com/webmachinelearning/webmcp>
[^ch07-28]: Chrome for Developers, “Content scripts” (Chrome Extensions documentation), sections “Work in isolated worlds” and “Specify frames” (`all_frames`). Read 14 October 2026. <https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts>
[^ch07-29]: “WebExtensions API to enumerate and invoke tools”, webmachinelearning/webmcp issue #74, opened 3 February 2026, open as of 2 November 2026, with comments, including Kenneth Christiansen’s comment of 20 October 2026 referring to the TPAC 2026 breakout session (w3c/tpac2026-breakouts issue #84). <https://github.com/webmachinelearning/webmcp/issues/74>
[^ch07-30]: webmachinelearning/webmcp pull request #339, “Replace UnknownError with specific DOMException types.” (merged 8 October 2026 as commit b206dae). <https://github.com/webmachinelearning/webmcp/pull/339>
[^ch07-31]: Dominic Farolino, “Introduce the `Tool` interface”, webmachinelearning/webmcp pull request #348 (opened 15 October 2026, merged 19 November 2026). Issue #349, “Allow `executeTool()` to execute tools registered by opaque-origin documents”, is still marked unresolved in the 23 November 2026 `executeTool()` steps. <https://github.com/webmachinelearning/webmcp/pull/348>
[^ch07-32]: Compatibility of `Tool` with `JSON.stringify`, object spread and `structuredClone`, and the Chrome 160.0.8173.0 rollout: see Appendix E and its notes.
