# Appendix A: API Quick Reference (IDL, Attributes, Events, Errors)

> *“Tool execution errors are not exposed to the web.”*
>
> — WebMCP specification, §3 Supporting concepts[^appa-1]

This appendix collects the whole WebMCP surface in one spot: the WebIDL, every dictionary member, the three events, the Permissions Policy feature and the exceptions each method can reject with. It doesn’t teach (the chapters do that), so each section points back to the chapter that explains the idea.

The IDL in Listing A.1 was checked against the WebMCP Draft Community Group Report dated 24 November 2026.[^appa-2] The 27 October 2026 draft, which matched the 15 October draft line for line, is the draft the Chromium 156 probes were written against. Three IDL changes have landed since that draft. Pull request #254, merged 2 November 2026, added optional `outputSchema`. Pull request #348, merged 19 November 2026, replaced `RegisteredTool` with the `Tool` interface. Pull request #373, merged 24 November 2026, added `waitForToolsUntil()`. Appendix E is how to read both generations of `getTools()`. The exception names for the three promise-returning methods are otherwise the ones in the October draft. `waitForToolsUntil()` throws, and those throws were not in the Chromium 156 probes.

Every behaviour marked “tested” was observed in Chromium 156.0.8078.4 with the `WebMCPTesting` feature switched on, which is what `chrome://flags/#enable-webmcp-testing` turns on in Chrome.[^appa-3] Chrome 156 has been the stable channel since 20 October 2026, and Chrome 157 is due on 3 November 2026.[^appa-23] The probes behind the tables live in the book’s demos repository, in `appendices/a-api-reference/`, and I re-ran all 25 of them on 2 November 2026: they all pass. Where Chromium and the draft disagree, the tables show both columns.

## A.1 The interface at a glance

Listing A.1 is the specification’s IDL index, unabridged. It’s short, and that tells you something: the whole imperative API is four methods, three events and the `Tool` interface.

**Listing A.1** `appendices/a-api-reference/webmcp.idl` — the WebMCP IDL, from the specification’s IDL index (24 November 2026 draft)

```webidl
partial interface Document {
  [SecureContext, SameObject] readonly attribute ModelContext modelContext;
};

[Exposed=Window, SecureContext]
interface ModelContext : EventTarget {
  Promise<undefined> registerTool(ModelContextTool tool, optional ModelContextRegisterToolOptions options = {});
  undefined waitForToolsUntil(Promise<any> promise);
  Promise<sequence<Tool>> getTools(optional ModelContextGetToolOptions options = {});
  Promise<DOMString> executeTool(Tool tool, optional object inputObject, optional ModelContextExecuteToolOptions options = {});

  attribute EventHandler ontoolchange;
  attribute EventHandler ontoolactivated;
  attribute EventHandler ontoolcancel;
};

dictionary ModelContextTool {
  required DOMString name;
  // Because `title` is for display in possibly native UIs, this must be a `USVString`.
  // See https://w3ctag.github.io/design-principles/#idl-string-types.
  USVString title;
  required DOMString description;
  object inputSchema;
  object outputSchema;
  required ToolExecuteCallback execute;
  ToolAnnotations annotations;
};

dictionary ToolAnnotations {
  boolean readOnlyHint = false;
  boolean untrustedContentHint = false;
  boolean consequentialHint = false;
  boolean debugging = false;
};

dictionary ToolExecuteCallbackOptions {
  required AbortSignal signal;
};

callback ToolExecuteCallback = Promise<any> (object inputObject, ToolExecuteCallbackOptions options);

dictionary ModelContextRegisterToolOptions {
  sequence<USVString> exposedTo;
  AbortSignal signal;
};

dictionary ModelContextGetToolOptions {
  sequence<USVString> fromOrigins;
};

dictionary ModelContextExecuteToolOptions {
  AbortSignal signal;
};

[Exposed=Window, SecureContext]
interface Tool {
  readonly attribute DOMString name;
  // `title` can be exposed as a `DOMString` since it was taken in by a
  // `USVString`, meaning all unmatched surrogate processing has already been
  // done, and there's no need to do it again on tool exposure.
  readonly attribute DOMString title;
  readonly attribute DOMString description;
  readonly attribute object? inputSchema;
  readonly attribute object? outputSchema;
  readonly attribute WindowProxy? source;
  readonly attribute USVString origin;
  readonly attribute object? annotations;
};

[Exposed=Window, SecureContext]
interface ToolActivatedEvent : Event {
  constructor(DOMString type, optional ToolActivatedEventInit eventInitDict = {});
  readonly attribute DOMString toolName;
};

dictionary ToolActivatedEventInit : EventInit {
  DOMString toolName = "";
};

[Exposed=Window, SecureContext]
interface ToolCancelEvent : Event {
  constructor(DOMString type, optional ToolCancelEventInit eventInitDict = {});
  readonly attribute DOMString toolName;
};

dictionary ToolCancelEventInit : EventInit {
  DOMString toolName = "";
};
```

Four things in Listing A.1 matter more than the rest:

- **The entry point is `document.modelContext`.** It hangs off `Document`, not `Navigator`, and it only exists in secure contexts.[^appa-4] There is one `ModelContext` per document, so every iframe has its own. (Tested: `'modelContext' in document` is `true` and `'modelContext' in navigator` is `false` in Chromium 156.) Appendix D covers the move from `navigator`.
- **There is no `unregisterTool()`.** You unregister by aborting the `AbortSignal` you passed to `registerTool()`.[^appa-5]
- **`waitForToolsUntil()` returns `undefined`.** It records a promise. It does not wait, and `getTools()` does not wait for it either (Section A.3).
- **Results are strings.** `executeTool()` resolves with a `DOMString`, whatever the tool returned.[^appa-6] How that string is produced is the one place where Chrome and the draft still disagree (Section A.5).

## A.2 `registerTool(tool, options)`

```js
await document.modelContext.registerTool(tool, { signal, exposedTo });
```

Registers one tool on the current document and returns a `Promise<undefined>`. Tested, it resolves with `undefined` in Chromium 156 too.[^appa-5] Chapter 5 introduces it, and Chapter 6 covers annotations and the execute callback’s signal.

**Table A.1 — `ModelContextTool` members**

| Member | Type | Required | Rule in the draft |
|---|---|---|---|
| `name` | `DOMString` | yes | 1–128 characters, only ASCII letters and digits, `_`, `-` and `.`, and unique per document. Otherwise `InvalidStateError`. |
| `title` | `USVString` | no | A display name for the browser’s UI. |
| `description` | `DOMString` | yes | Must not be empty, or `InvalidStateError`. |
| `inputSchema` | `object` | no | Serialized with `JSON.stringify` at registration. A `toJSON()` that returns `undefined` rejects with a `TypeError`, and an error `JSON.stringify` throws (a circular object, for example) is rethrown. Serializing can run script, so the name and fully-active checks run again afterwards. (Tested: when `toJSON()` registers another tool with the same name, Chromium 156 kills the page’s renderer, see Table A.7.) |
| `outputSchema` | `object` | no | Optional JSON Schema describing expected tool output. Serialized at registration and exposed by `getTools()`; this does not settle whether native `executeTool()` rejects a mismatch. |
| `execute` | `ToolExecuteCallback` | yes | `(inputObject, { signal }) => any`, may return a promise. |
| `annotations` | `ToolAnnotations` | no | See Table A.2. |

The rules in Table A.1 are the draft’s registration steps.[^appa-5] I tested all of them in Chromium 156, and the browser agrees with the draft. A name with a space, a 129-character name, an empty description and a duplicate name each reject with `InvalidStateError`. A missing `execute`, a circular `inputSchema` and a `toJSON()` that returns `undefined` each reject with `TypeError`.

**Table A.2 — `ToolAnnotations` members (all `boolean`, default `false`)**

| Member | Meaning in the draft |
|---|---|
| `readOnlyHint` | The tool doesn’t modify any state and only reads data. |
| `untrustedContentHint` | The tool’s output contains data that is untrusted from the registering author’s point of view. |
| `consequentialHint` | Running the tool has significant, real-world or non-reversible consequences, such as booking a flight or transferring money. |
| `debugging` | The tool is meant for debugging and developer tooling rather than end-user interactions. Chrome’s documentation says it is available from Chrome 156.[^appa-24] |

The wording in Table A.2 paraphrases the draft’s dictionary descriptions.[^appa-7] The draft carries annotations through to `getTools()`, but it doesn’t say what an agent must do with them. That is the agent’s policy (Chapter 6). Since 20 October 2026 the security section also says it plainly: a malicious site can omit or misrepresent the hints, and keeping an agent safe from that is the agent’s job, not something the specification can enforce.[^appa-25] Two open pull requests would add to this table, see Section A.10.

**Table A.3 — `ModelContextRegisterToolOptions` members**

| Member | Type | Meaning |
|---|---|---|
| `signal` | `AbortSignal` | Aborting it unregisters the tool. If it’s already aborted, `registerTool()` rejects with the signal’s abort reason. |
| `exposedTo` | `sequence<USVString>` | Origins of other documents in the same tree that may see and call this tool. Each entry must parse as a URL with a potentially trustworthy origin, or the call rejects with `SecurityError`. |

Both members come from the draft’s registration steps.[^appa-5][^appa-8] Tested in Chromium 156: an already-aborted signal rejects with `AbortError` (the default abort reason), and `exposedTo: ['http://example.com']` rejects with `SecurityError: Only secure origins are allowed in the exposedTo list.` Unregistering a tool doesn’t cancel calls already in flight. Chrome’s documentation dates that behaviour to Chrome 153,[^appa-24] and Chapter 6 shows how to live with it.

## A.3 `waitForToolsUntil(promise)`

```js
document.modelContext.waitForToolsUntil?.(toolsUpdated);
```

The 24 November 2026 draft’s non-normative description is: the method “signals that the document is asynchronously registering or updating its tools, and that tool consumers should wait until `promise` settles (or a timeout elapses) before reading the document’s tools. Multiple promises can be registered; the document’s tools are considered ready once all registered promises have settled.”[^appa-30]

The normative steps, in order:[^appa-30]

1. If the document is not fully active, throw an `InvalidStateError` `DOMException`.
2. If the document is not allowed to use the `tools` feature, throw a `NotAllowedError` `DOMException`.
3. Append `promise` to the model context’s pending tool-readiness promises.
4. Set the document’s `tools ready` flag to true when that set is empty, and to false otherwise.
5. When the promise fulfills or rejects, remove it and update the flag.
6. In parallel, wait an implementation-defined time, then queue a task that removes the promise and updates the flag, even if the promise has not settled.

The return type is `undefined`. Awaiting the call returns immediately. The wait is for the user agent’s observation, not for the caller. `getTools()`’s steps do not read `tools ready`. Pull request #373 says wiring that wait into `getTools()`, and changing `toolchange` dispatch, is deferred.[^appa-30]

Each observation’s tool collection includes the boolean. The draft says a browser agent can use it, with its own heuristics and timeouts, to decide whether to act or to wait for a later observation. Toggling the flag does not by itself cause an observation. The flag’s initial value is `true`. An inline issue, #328, says it should start false unless the document is not allowed to use `tools`. That issue was still open on 27 November 2026. The lifecycle point is not chosen.[^appa-30]

Chrome at commit `dc7d570dff77eca05dae42b1fa6e3b816205a94f` (25 November 2026, canary 160.0.8185.0) does not implement step 6 as a return to ready. The renderer ignores a promise that has already settled. The first unsettled promise sets script tools not ready and starts a 10-second timer that logs a console warning. The warning says agents may stop waiting. The actor observation timeout `kActorObservationDelayTimeout` defaults to 10 seconds and ends the agent’s wait. It does not clear the document’s not-ready state. The commit ships the method by deleting the `WebMCPWaitForToolsUntil` runtime flag, so the method is exposed wherever `ModelContext` is. The same revision reports a frame as loading until `DOMContentLoaded`. That loading state is Chromium’s `GetScriptToolsReadyState`, not the specification’s initial `true`. None of this was run in a browser for this book.[^appa-31]

`Promise.all()` rejects, and therefore settles, at the first failed `registerTool()`. If that is the only promise you passed, step 5 marks the document ready while other registrations are still pending. `Promise.allSettled()` waits for all of them. A retry or a rollback `abort()` has to be inside the promise. Chapter 5’s Listing 5.7 and Chapter 10’s Listing 10.12 are the calls. Before 160.0.8185.0, optional chaining skips a missing method.

## A.4 `getTools(options)` and `Tool`

```js
const tools = await document.modelContext.getTools({ fromOrigins });
```

Returns the tools an in-page agent may see. To be precise: the tools of every document in the tab’s frame tree that is allowed the `tools` feature, is same-origin with the caller or listed in `fromOrigins`, and has exposed the tool to the caller’s origin. The list is sorted by `name`.[^appa-9] The browser’s own agent doesn’t use this method (it has an internal mechanism).[^appa-6] Chapter 7 builds an in-page agent on it.

**Table A.4 — `Tool` members, as `getTools()` returns them (23 November 2026)**

| Member | Type | Notes |
|---|---|---|
| `name` | `DOMString` | As registered. |
| `title` | `DOMString` | The empty string when no title was given (tested: `""` in Chromium 156). |
| `description` | `DOMString` | As registered. |
| `inputSchema` | `object` or `null` | Parsed back from the stored JSON string. `null` when none was given. Chromium 156 omitted the member instead. |
| `outputSchema` | `object` or `null` | Parsed back from the stored JSON string. `null` when none was given. Chromium 156 dropped it. |
| `source` | `WindowProxy` or `null` | The registering document’s window, or `null` if that document is no longer fully active. The member was `window` before Chrome 160.0.8173.0. |
| `origin` | `USVString` | That document’s serialized origin. |
| `annotations` | `object` or `null` | `null` when the tool was registered without annotations. |

`fromOrigins` follows the same rule as `exposedTo`: every entry must be a URL with a potentially trustworthy origin, or `getTools()` rejects with `SecurityError`.[^appa-10] Tested: an insecure origin and a string that isn’t a URL both reject that way in Chromium 156.

> **Still in flux: what an empty title looks like**
>
> The draft fills a missing `title` with the empty string, and an inline issue in the `getTools()` steps asks whether to leave the member out instead.[^appa-9] Issue #224, “Tool `title` and `inputSchema`: what to expose when not provided?”, opened on 21 July 2026, was still open on 2 November 2026.[^appa-11] Test for a falsy title rather than for `undefined` or `""` specifically.

### Output schemas and validation

`outputSchema` is an optional JSON Schema for the result. The specification expects a conforming value, but does not currently require native `executeTool()` to reject a mismatch. Issue #92 remains open. An agent harness should validate before passing results to a model; on mismatch, return a clear error and do not include the malformed payload. Tools without an output schema remain valid and may return unstructured text.[^appa-output-schema]

## A.5 `executeTool(tool, inputObject, options)`

```js
const text = await document.modelContext.executeTool(tool, { query: 'tent' }, { signal });
```

Runs a tool on the document that registered it and resolves with the result as a string. `tool` is a `Tool` from `getTools()`. The algorithm uses an internal id that script cannot read, and the tool’s internal window reference. If that document is no longer fully active, the call rejects with `InvalidStateError` before the id is consulted. The public `source` getter is `null` in that same case. If the id is gone, or the tool is not exposed to the caller, the call rejects with `NotFoundError`. A hand-made dictionary is not a `Tool` and cannot reach a tool. A `Tool` from a registration that has since been replaced rejects with `NotFoundError`. Before Chrome 160 the argument was a `RegisteredTool` dictionary and the lookup used `name` and `window` (Appendix E). A missing `inputObject` becomes `{}`. The options take one member, `signal`: aborting it rejects the promise with the signal’s reason and cancels the execution in the target document.[^appa-6] Chrome’s documentation adds one case the draft doesn’t spell out: when the tool triggers a navigation, the call returns `null` instead of a result.[^appa-24] Pass an object as `inputObject`, too. Chrome deprecated JSON-string input arguments in Chrome 155.[^appa-24]

**Table A.5 — What `executeTool()` resolves with (tested, Chromium 156)**

| The tool’s `execute` returns | Draft | Chromium 156 |
|---|---|---|
| An object, `{ got: { a: 1 } }` | Its JSON string | `'{"got":{"a":1}}'` |
| A string, `'plain'` | Its JSON string, `'"plain"'` | `'plain'` (not JSON-quoted) |
| `undefined` | Rejects: “unserializable result”, `OperationError` | Resolves with `'undefined'` |
| A `BigInt`, `10n` | Rejects: “unserializable result”, `OperationError` | Resolves with `'10'` |

The draft’s column follows its execution steps. They serialize whatever the tool’s promise fulfils with to a JSON string and treat a failure to do so (`JSON.stringify` throws or yields `undefined`) as the “unserializable result” error.[^appa-6][^appa-1] Chapter 5 recommends returning a small, flat object, which behaves the same everywhere.

> **Still in flux: which column is right**
>
> Issue #361, opened on 23 October 2026, reports the same mismatch in stable Chrome 156.0.8078.48 and in Chrome 158.0.8119.0, and notes that the web-platform-tests follow Chrome. On 26 October François Beaufort, one of the people who wrote these steps, answered: “The WPT assertions are wrong, and so is Chrome. A tool that returns "hi" should resolve to '"hi"'.” In the same thread he suggests that `undefined` should map to `null`, so the result becomes the string `"null"`, instead of rejecting. Nothing was merged as of 2 November 2026.[^appa-26] So the plain-string row will most likely move to the draft’s column, and the `undefined` row may change in both. Return objects and you won’t notice either change.

## A.6 Events

`ModelContext` is an `EventTarget` with three events. Each has an `on…` handler attribute as well.[^appa-12]

**Table A.6 — `ModelContext` events**

| Event | Interface | Fired at | When (draft) | Tested, Chromium 156 |
|---|---|---|---|---|
| `toolchange` | `Event` | Each document in the tree that can see the changed tool | A tool is registered or unregistered | Fires once per registration and once per unregistration |
| `toolactivated` | `ToolActivatedEvent` (`toolName`) | The `ModelContext` of the tool’s document | Execution of a tool begins, after the input is parsed | Fires once per `executeTool()` call |
| `toolcancel` | `ToolCancelEvent` (`toolName`) | The `ModelContext` of the tool’s document | A pending execution is cancelled (the tool’s `signal` is aborted first) | Fires when the caller aborts, and the tool’s `signal` aborts too |

The firing rules in Table A.6 are from the draft’s `toolchange` notification steps, its execution steps and its cancellation steps.[^appa-12][^appa-13] The draft warns that `toolchange` is queued from parallel steps, so you can’t rely on its timing relative to other tasks.[^appa-13] It still fires once per registration and once per unregistration. Issue #374, open on 27 November 2026, asks whether a batch should fire once. Pull request #373 records that question and does not change the firing.[^appa-32] `ToolActivatedEvent` and `ToolCancelEvent` were added to the draft on 17 September 2026.[^appa-14] Listen for them on `document.modelContext`: Chrome’s documentation says that `window.ontoolactivated` and `window.ontoolcancel` are not supported from Chrome 156, and that both events are non-cancelable.[^appa-21]

## A.7 Permissions Policy

`registerTool()`, `getTools()`, `executeTool()` and `waitForToolsUntil()` are gated on the policy-controlled feature `tools`, whose default allowlist is `'self'`.[^appa-15] The first three reject a promise. `waitForToolsUntil()` throws (Section A.3). In practice:

- A same-origin iframe can use the API. A cross-origin iframe can’t, unless the embedder delegates the feature with `<iframe allow="tools">`.
- `Permissions-Policy: tools=()` on a response turns the API off for that document and every frame inside it. The draft lists this header as a mitigation for pages where WebMCP isn’t an intended capability.[^appa-16]
- A document without the feature gets `NotAllowedError` from `registerTool()`, `getTools()` and `executeTool()`, and from `waitForToolsUntil()` as a throw. `getTools()` in other documents skips it.[^appa-9][^appa-10][^appa-30]

Tested in Chromium 156: with `Permissions-Policy: tools=()`, `document.featurePolicy.allowsFeature('tools')` is `false` and `registerTool()`, `getTools()` and `executeTool()` reject with `NotAllowedError`. `waitForToolsUntil()` was not in those probes. A cross-origin iframe without `allow="tools"` gets `NotAllowedError` from `registerTool()`. With `allow="tools"` and `exposedTo` naming the parent, the parent sees the frame’s tool through `getTools({ fromOrigins })`, and without `fromOrigins` it doesn’t.

Those three switches (the embedder’s `allow="tools"`, the provider’s `exposedTo` and the consumer’s `fromOrigins`) now have a name in the specification. Since 27 October 2026 §6.3.4, “Interaction with the Same-Origin Policy”, describes them as “Enforcing Same-Origin Isolation via Two-Sided Opt-In”, three independent gates that all have to say yes. That section replaced the to-do note the first edition pointed at.[^appa-27] Chapter 7 covers the three opt-ins in detail.

## A.8 Errors

The draft names five platform failures for a tool execution and maps each one to an exception name. Callers only ever see the exception name.[^appa-1] Other exceptions come from the method steps themselves.[^appa-5][^appa-6][^appa-9] Table A.7 puts all of them next to what Chromium 156 actually does. If you read only one table in this appendix, make it this one.

**Table A.7 — Exception names: the 27 October 2026 draft vs Chromium 156 with WebMCPTesting (tested)**

| Situation | Method | Draft | Chromium 156 |
|---|---|---|---|
| Document not fully active | `registerTool()`, `getTools()`, `executeTool()` | `InvalidStateError` (a rejected promise) | not tested |
| Document not fully active | `waitForToolsUntil()` | throws `InvalidStateError` | not in the Chromium 156 probes |
| `tools` feature not allowed (header or missing `allow`) | `registerTool()`, `getTools()`, `executeTool()` | `NotAllowedError` (a rejected promise) | `NotAllowedError` ✓ |
| `tools` feature not allowed | `waitForToolsUntil()` | throws `NotAllowedError` | not in the Chromium 156 probes |
| Bad name, empty description, duplicate name | `registerTool()` | `InvalidStateError` | `InvalidStateError` ✓ |
| `inputSchema` can’t be serialized, or `execute` is missing | `registerTool()` | `TypeError` (rethrown) | `TypeError` ✓ |
| Another tool with the same name registered while `inputSchema` is serialized | `registerTool()` | `InvalidStateError` (added 15 October 2026) | **The browser kills the page’s renderer** (a known bug)[^appa-22] |
| Already-aborted `signal` | `registerTool()`, `executeTool()` | The signal’s abort reason | The abort reason ✓ (`AbortError`, or your own reason) |
| Insecure or unparsable origin in `exposedTo` / `fromOrigins` | `registerTool()`, `getTools()` | `SecurityError` | `SecurityError` ✓ |
| `tool.origin` is opaque (`"null"`) or unparsable | `executeTool()` | `NotSupportedError` | `NotSupportedError` ✓ |
| `inputObject` can’t be serialized to JSON (a circular object) | `executeTool()` | The `JSON.stringify` error (rethrown) | `TypeError` ✓ |
| Target document has no navigable (detached), or is in another tab | `executeTool()` | `InvalidStateError` | not tested |
| Tool not registered (unregistered, or a forged `name`) | `executeTool()` | `NotFoundError` | **`UnknownError`** |
| `tool.origin` doesn’t match the target document | `executeTool()` | `NotFoundError` | **`UnknownError`** |
| Tool not exposed to the caller’s origin | `executeTool()` | `NotFoundError` | not tested directly (the tool isn’t in `getTools()`) |
| Input can’t be parsed into an object | `executeTool()` | `DataError` | not tested |
| The tool’s `execute` throws or rejects | `executeTool()` | `OperationError` | **`UnknownError`** |
| The result can’t be serialized | `executeTool()` | `OperationError` | **Resolves** (Table A.5) |
| Target document unloaded mid-call (iframe removed) | `executeTool()` | `AbortError` | **`UnknownError`** |
| Caller aborts the `signal` mid-call | `executeTool()` | The signal’s abort reason | `AbortError` ✓, and `toolcancel` fires |

A ✓ means Chromium agrees with the draft, and bold marks a difference. Chromium’s `UnknownError` comes with two different messages. For a tool that threw, it says “Tool was executed but the invocation failed. For example, the script function threw an error”. For a missing or forged tool and for a removed frame, it says “The operation failed for an unknown transient reason (e.g. out of memory).” The messages aren’t part of any contract, so don’t parse them.

Chapter 7 observed the same `UnknownError` for forged names and origins and for a frame that went away mid-call, and the same `NotAllowedError` under a blocking policy. Until Chromium and the draft line up, I treat the two names as one family, and Listing A.2 does exactly that.

**Listing A.2** `appendices/a-api-reference/classify-tool-error.js` — classifying an `executeTool()` rejection under both the draft and Chromium 156

```js
// Listing A.2: classify an executeTool() rejection in a way that works with both
// the draft's exception names (since 8 October 2026) and Chromium 156's.
export function classifyToolError(err) {
  const name = err && err.name;
  switch (name) {
    case 'AbortError':
      return { kind: 'cancelled', retry: false };   // caller's signal, or (draft) target unloaded
    case 'NotAllowedError':
      return { kind: 'blocked', retry: false };     // "tools" Permissions Policy says no
    case 'SecurityError':
      return { kind: 'bad-origin', retry: false };  // exposedTo / fromOrigins not secure
    case 'NotFoundError':                           // draft: tool gone or not exposed
    case 'InvalidStateError':                       // document inactive or other tab
      return { kind: 'gone', retry: true };         // re-read getTools(), then retry
    case 'OperationError':                          // draft: the tool threw or rejected
    case 'UnknownError':                            // Chromium 156: all of the above
      return { kind: 'failed', retry: true };
    default:
      return { kind: 'error', retry: false };
  }
}
```

> **Still in flux: exception names**
>
> Chromium’s `UnknownError` isn’t a bug against some old idea. It is what the draft itself said until recently. Until 8 October 2026 the `executeTool()` steps rejected with `UnknownError` in each of these cases, next to an inline issue asking for “more granular errors than UnknownError”. A pull request merged that day replaced it with the specific names in Table A.7 and added the tool execution error table.[^appa-17] Chromium 156 still behaves the way the draft read before that change. Expect the right-hand column of Table A.7 to move toward the draft, and key error handling on families (Listing A.2), not on single names.

> **Still in flux: what `registerTool()` resolves with**
>
> Issue #234, “registerTool should return registered tool instead of undefined”, opened on 29 July 2026, was still open on 2 November 2026.[^appa-18] Code that ignores the resolved value, as every listing in this book does, won’t break either way. The `Tool` interface is already in the draft (Appendix E). This appendix has not re-checked #234 since 2 November.

## A.9 The declarative attributes (removed from the specification)

Chapter 8 covers the declarative API: HTML attributes that turn a `<form>` into a tool. It was removed from the specification on 8 October 2026.[^appa-19] The project README calls it a “future exploration” that “is not part of the specification at this time”, and its explainer stays in the repository.[^appa-20] Chrome’s documentation still describes it, and Chromium 156 still ships it behind the same flag.[^appa-21] On 16 October 2026 the explainer was corrected to name the cancel event `toolcancel` (it had said `toolcanceled`), and its open question now asks whether the events should fire at `ModelContext` or at the `<form>`.[^appa-28]

**Table A.8 — Declarative API surface: removed from the spec on 8 October 2026, still in Chrome’s trial**

| Surface | Where | What it does (Chrome documentation) |
|---|---|---|
| `toolname` | `<form>` | Names the tool and registers the form as a tool. |
| `tooldescription` | `<form>` | Describes the tool. |
| `toolparamdescription` | form controls | Becomes the property’s `description` in the generated JSON Schema. |
| `toolautosubmit` | `<form>` | Submits the form when the agent calls the tool. Without it, the user clicks Submit. |
| `SubmitEvent.agentInvoked` | event | `true` when an agent triggered the submission. |
| `SubmitEvent.respondWith(promise)` | event | Hands the browser a promise for the form’s result. |
| `:tool-form-active`, `:tool-submit-active` | CSS | Match the form and its submit button while an agent is using them. |

The rows in Table A.8 are from Chrome’s declarative API page (published 18 May 2026, last updated 25 September 2026, unchanged on 2 November 2026).[^appa-21] Tested in Chromium 156: a `<form toolname="search_availability" tooldescription="Find free tables">` with a required `date` input and a required `number` input (`min="1" max="12"`) shows up in `getTools()` as a tool with a generated schema: `date` becomes `{ type: 'string', format: 'date' }`, `partySize` becomes `{ type: 'number', minimum: 1, maximum: 12, multipleOf: 1 }`, and both are listed in `required`.

> **Still in flux: the declarative API**
>
> Removed from the specification doesn’t mean removed from Chrome. Use the attributes only behind feature detection, keep an imperative tool for the same action, and check Chapter 8 and the Chrome page before you rely on them.

## A.10 Proposals that would change this page

Nothing below is in the specification. These are open pull requests that would still touch the IDL or the tables above. PR #254, which added `outputSchema`, merged on 2 November 2026 and is in Tables A.1 and A.4. PR #348, which replaced `RegisteredTool` with `Tool`, merged on 19 November 2026 and is in Listing A.1 and Table A.4 (Appendix E).[^appa-29] I list what is still open because the day one of them merges, a table in this appendix goes out of date.

**Table A.9 — Open pull requests against the API, as checked on 23 November 2026**

| Pull request | Opened by, last update | What it would change | What it means for your code |
|---|---|---|---|
| #375, “Introduce generic tool calling explainer” | Dominic Farolino, 6 November 2026, open on 23 November 2026 | A different API: `window.toolManager`, `getTools()` on `Window`, and `tool.execute()`. Not a change to the merged `Tool` interface. | Do not write to it. Appendix F. |
| #204, “Replace requestUserInteraction with requestUserInput” | Brandon Walderman, 29 October 2026 | A way for a tool to ask the user for input through the agent, with `interactive`, `form` and `url` modes, aligned with MCP elicitation. | Additive. Until it lands, confirmation stays in your own page (Chapter 13). |
| #355, “Clarify annotation defaults and add openWorldHint” (draft) and #358, “Say that a hint a tool leaves out is not an assurance” | Kenneth Christiansen, 20 October 2026 | A fifth annotation and clearer wording on what a missing hint means. | Additive. The second one is prose only. |

> **Tip:** Watching these is cheap. Subscribe to the open pull requests on GitHub, and re-run the probes in `appendices/a-api-reference/` whenever one of them merges or a new Chrome version reaches stable. The checks named “Chromium differs” are written to fail on purpose when Chromium catches up with the draft. Chrome 160 changes the shape of `getTools()` even though those probes were written for Chromium 156 (Appendix E).

## A.11 Summary

- The API is `document.modelContext` with four methods, `registerTool(tool, { signal, exposedTo })`, `waitForToolsUntil(promise)`, `getTools({ fromOrigins })` and `executeTool(tool, input, { signal })`, plus three events: `toolchange`, `toolactivated` and `toolcancel`. `getTools()` returns `Tool` objects. The 27 October 2026 draft returned `RegisteredTool` dictionaries and had no `waitForToolsUntil()`. `getTools()` does not wait for that method.
- Unregister by aborting the signal. There’s no `unregisterTool()`, `provideContext()` or `clearContext()` any more (Appendix D).
- The `tools` Permissions Policy feature, default `'self'`, gates all four methods. The promise-returning methods reject with `NotAllowedError`. `waitForToolsUntil()` throws it. Cross-origin access needs all three opt-ins, which the draft now calls two-sided opt-in.
- `exposedTo` and `fromOrigins` accept only potentially trustworthy origins. Anything else is a `SecurityError`.
- Chromium 156 reports most execution failures as `UnknownError` where the draft says `NotFoundError`, `OperationError` or `AbortError`, and it resolves results the draft would reject or quote. The spec’s editors say the draft is right about strings. Handle errors by family and return objects.
- The declarative form attributes left the specification on 8 October 2026 but still work in Chrome.
- `outputSchema` is in the current draft, and it is `null` on a `Tool` when the tool was registered without one. Open proposals that could still change this page are `requestUserInput` (#204), `openWorldHint` (#355) and the generic-calling explainer (#375, Appendix F). The `Tool` interface is already in the draft.

[^appa-1]: WebMCP specification, Draft Community Group Report, 27 October 2026, §3 Supporting concepts: the tool execution error table (“tool not found” → `NotFoundError`, “invalid input” → `DataError`, “tool rejected” and “unserializable result” → `OperationError`, “target document unloaded” → `AbortError`) and the note that tool execution errors are not exposed to the web (retrieved November 2026). <https://webmachinelearning.github.io/webmcp/#tool-execution-error>
[^appa-2]: WebMCP specification, Draft Community Group Report dated 24 November 2026, editors Brandon Walderman (Microsoft), Khushal Sagar (Google), Dominic Farolino (Google) and Samuel Dallstream (Microsoft), published by the W3C Web Machine Learning Community Group (retrieved 27 November 2026). The 27 October 2026 IDL index matched the 15 October 2026 draft. Pull request #348 (merged 19 November 2026) replaced `RegisteredTool` with `Tool`. Pull request #373 (merged 24 November 2026) added `waitForToolsUntil()`. <https://webmachinelearning.github.io/webmcp/>
[^appa-3]: Chrome for Developers, “WebMCP” overview (published 18 May 2026, last updated 7 October 2026), section “Local WebMCP”: the `chrome://flags/#enable-webmcp-testing` flag (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp>
[^appa-4]: WebMCP specification, §4.1 Extensions to Document and the IDL index: `partial interface Document { [SecureContext, SameObject] readonly attribute ModelContext modelContext; }`. <https://webmachinelearning.github.io/webmcp/#idl-index>
[^appa-5]: WebMCP specification, §4.2, the `registerTool(tool, options)` method steps: the “tools” check, the name, description and duplicate checks, `inputSchema` serialization and the checks repeated after it, the already-aborted signal, `exposedTo` parsing, and the abort steps that unregister the tool. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool>
[^appa-6]: WebMCP specification, §4.2, the non-normative description of `executeTool()` (it resolves to the stringified result, and an omitted argument becomes an empty object) and the `executeTool(tool, inputObject, options)` method steps (including the rethrown error when `inputObject` can’t be serialized, and `InvalidStateError` when the target document has no navigable). <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-executetool>
[^appa-7]: WebMCP specification, §4.2.1, the `ToolAnnotations` dictionary descriptions. <https://webmachinelearning.github.io/webmcp/#dictdef-toolannotations>
[^appa-8]: WebMCP specification, §4.2.3 ModelContextRegisterToolOptions Dictionary: `exposedTo` is “an array of origins that control which documents this tool is exposed to, in the current document’s tree”, and `signal` “unregisters the tool when aborted”. <https://webmachinelearning.github.io/webmcp/#dictdef-modelcontextregistertooloptions>
[^appa-9]: WebMCP specification, §4.2, the `getTools(options)` method steps: traversal of the inclusive descendant navigables, the “tools” check per document, the same-origin-or-`fromOrigins` check, the exposure check, the empty-string `title` with its inline reference to issue #224, and sorting by name. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-gettools>
[^appa-10]: WebMCP specification, §4.2.4 ModelContextGetToolOptions Dictionary and the `getTools()` steps (`SecurityError` for an origin that fails to parse or is not potentially trustworthy). <https://webmachinelearning.github.io/webmcp/#dom-modelcontextgettooloptions-fromorigins>
[^appa-11]: “Tool `title` and `inputSchema`: what to expose when not provided?”, webmachinelearning/webmcp issue #224, opened 21 July 2026, still open on 2 November 2026. <https://github.com/webmachinelearning/webmcp/issues/224>
[^appa-12]: WebMCP specification, §4.3 Events, §4.3.1 ToolActivatedEvent Interface and §4.3.2 ToolCancelEvent Interface. <https://webmachinelearning.github.io/webmcp/#events>
[^appa-13]: WebMCP specification: the steps that notify documents of a tool change (including the note on `toolchange` timing), the execute-callback steps that fire `toolactivated`, and the steps that cancel a pending tool execution and fire `toolcancel`. <https://webmachinelearning.github.io/webmcp/#eventdef-modelcontext-toolcancel>
[^appa-14]: webmachinelearning/webmcp commit f5645e9, “Add `ToolActivatedEvent` and `ToolCancelEvent` event interfaces (#245)”, committed 17 September 2026 (repository history read 15 October 2026). <https://github.com/webmachinelearning/webmcp/commit/f5645e9aea51eb589599f181d104a2f49430608e>
[^appa-15]: WebMCP specification, §4.4 Permissions policy integration: the policy-controlled feature “tools” with a default allowlist of `'self'`. <https://webmachinelearning.github.io/webmcp/#permissions-policy>
[^appa-16]: WebMCP specification, §6.4.1 Disabling WebMCP with Permissions Policy. <https://webmachinelearning.github.io/webmcp/#mitigation-disable-permissions-policy>
[^appa-17]: webmachinelearning/webmcp commit b206dae, “Replace UnknownError with specific DOMException types. (#339)”, by Mark Foltz, committed 8 October 2026: it removes the `UnknownError` rejections and their “Support more granular errors” issue notes from `index.bs` and adds the `NotFoundError` / `DataError` / `OperationError` / `AbortError` table. Repository history and diff read 14 October 2026. <https://github.com/webmachinelearning/webmcp/commit/b206dae8bad34ea8e6ff7213b417b50b14a37e9a>
[^appa-18]: “registerTool should return registered tool instead of undefined”, webmachinelearning/webmcp issue #234, opened 29 July 2026, last updated 3 October 2026, still open on 2 November 2026. <https://github.com/webmachinelearning/webmcp/issues/234>
[^appa-19]: webmachinelearning/webmcp commit 14ae813, “Remove declarative API from the spec for now (#338)”, by François Beaufort, merged 8 October 2026 (pull request #338). It changed `index.bs` and `README.md`. Merge date re-checked against the GitHub API in November 2026. <https://github.com/webmachinelearning/webmcp/commit/14ae813cc4e9fe0d39313f4b1ee5b231746731ad>
[^appa-20]: webmachinelearning/webmcp README, section “Future Exploration: Declarative API”, and the Declarative API Explainer (retrieved November 2026). <https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md>
[^appa-21]: Chrome for Developers, “Declarative API” (published 18 May 2026, last updated 25 September 2026): `toolname`, `tooldescription`, `toolparamdescription`, `toolautosubmit`, `SubmitEvent.agentInvoked`, `SubmitEvent.respondWith()`, `:tool-form-active` and `:tool-submit-active`, plus the note that `window.ontoolactivated` and `window.ontoolcancel` are not supported from Chrome 156 (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp/declarative-api>
[^appa-22]: Chromium issue 573722078, “WebMCP: Renderer killed when `registerTool()`’s `inputSchema` serialization registers a tool with the same name”, filed 14 October 2026 (Blink > Agentic Platform > WebMCP). The browser terminates the renderer for a bad IPC message, reason 345 (`RFHI_WEBMCP_REGISTER_DUPLICATE_TOOL_NAME`). The issue is marked Fixed, but the fix (crrev.com/c/8583183) was reverted on main (crrev.com/c/8575491) and had not relanded as of 15 October 2026, 09:26 UTC. The crash still reproduces in Chromium 156.0.8078.4 on 2 November 2026. I couldn’t check whether a later Chrome build carries a fix. <https://issues.chromium.org/issues/573722078>
[^appa-23]: Chromium Dash, release schedule and current releases: Chrome 156 stable since 20 October 2026 (156.0.8078.80 on 2 November 2026), Chrome 157 stable date 3 November 2026 (retrieved November 2026). <https://chromiumdash.appspot.com/schedule>
[^appa-24]: Chrome for Developers, “Imperative API” (published 18 May 2026, last updated 16 October 2026): `executeTool()` “returns the result of the tool execution, or null when a navigation is triggered”, the `debugging` annotation is available from Chrome 156, a tool can be unregistered without cancelling in-flight executions as of Chrome 153, and JSON stringified input arguments are deprecated from Chrome 155 (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
[^appa-25]: WebMCP specification, §6 Security and privacy considerations, the agent-ecosystem text and §6.4.6 Agent-Level Guardrails and Best Practices, added by pull request #334 (merged 20 October 2026) (retrieved November 2026). <https://github.com/webmachinelearning/webmcp/pull/334>
[^appa-26]: webmachinelearning/webmcp issue #361, about how `executeTool()` serializes strings and `undefined` in the spec and in Chrome, opened 23 October 2026, with François Beaufort’s reply of 26 October 2026. Open on 2 November 2026. <https://github.com/webmachinelearning/webmcp/issues/361>
[^appa-27]: WebMCP specification, §6.3.4 Interaction with the Same-Origin Policy and §6.3.4.1 Enforcing Same-Origin Isolation via Two-Sided Opt-In, added by pull request #326, “Document cross-origin tool exposure and two-sided opt-in in Section 6.”, merged 27 October 2026 (retrieved November 2026). <https://github.com/webmachinelearning/webmcp/pull/326>
[^appa-28]: webmachinelearning/webmcp pull request #350, “Editorial: sync explainers with spec”, merged 16 October 2026. <https://github.com/webmachinelearning/webmcp/pull/350>
[^appa-29]: webmachinelearning/webmcp pull request #348, merged 19 November 2026, and pull request #254, merged 2 November 2026. Pull requests #204 and #355 were open on 2 November 2026. Pull request #375 was open on 23 November 2026 (Appendix F). <https://github.com/webmachinelearning/webmcp/pulls>

[^appa-32]: webmachinelearning/webmcp issue #374, “Batch toolChange notifications for tool registry changes”, opened 4 November 2026, still open on 27 November 2026. The 24 November draft has the same question as an inline issue on the notify-documents steps. <https://github.com/webmachinelearning/webmcp/issues/374>
[^appa-30]: WebMCP specification, Draft Community Group Report, 24 November 2026 (retrieved 27 November 2026): the `waitForToolsUntil(promise)` IDL line, the non-normative description quoted in Section A.3, the method steps, the initial value of `tools ready`, the inline issue #328, and the observation notes in §5.2. Pull request #373, merged 24 November 2026 at 03:10 UTC. Issue #328 was still open on 27 November 2026. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-waitfortoolsuntil> <https://github.com/webmachinelearning/webmcp/pull/373> <https://github.com/webmachinelearning/webmcp/issues/328>
[^appa-31]: Chromium commit `dc7d570dff77eca05dae42b1fa6e3b816205a94f`, “WebMCP: Ship waitForToolsUntil() with the WebMCP origin trial”, 25 November 2026, `refs/heads/main@{#1754836}`. Chromium Dash records canary 160.0.8185.0 (retrieved 27 November 2026). At that revision `model_context.cc` ignores an already-settled promise and warns after `kWaitForToolsWarningDelay` of 10 seconds without setting script tools ready. `kActorObservationDelayTimeout` defaults to `base::Seconds(10)`. `GetScriptToolsReadyState` returns loading until `DOMContentLoaded`. The commit diff does not edit `model_context.cc`. It removes the `WebMCPWaitForToolsUntil` runtime feature. No Chrome 160 probe was run. <https://chromiumdash.appspot.com/commit/dc7d570dff77eca05dae42b1fa6e3b816205a94f> <https://chromium-review.googlesource.com/c/chromium/src/+/8839808>
[^appa-output-schema]: webmachinelearning/webmcp pull request #254, merged 2 November 2026, and issue #92, open on 15 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254> <https://github.com/webmachinelearning/webmcp/issues/92>
