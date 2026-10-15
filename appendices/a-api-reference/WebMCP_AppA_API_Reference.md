*Appendices*

# Appendix A: API Quick Reference (IDL, Attributes, Events, Errors)

> *“Tool execution errors are not exposed to the web.”*
>
> — WebMCP specification, §3 Supporting concepts[^1]

This appendix is the page to keep open while you write tool code. It collects the whole WebMCP surface in one place: the WebIDL, every dictionary member, the three events, the Permissions Policy feature, and the exceptions each method can reject with. It doesn’t teach; the chapters do that, and each section points back to the chapter that explains the idea.

Everything here was checked against the WebMCP Draft Community Group Report dated 15 October 2026, read on 15 October 2026; its IDL is unchanged from the 14 October draft.[^2] Every behaviour marked “tested” was observed in Chromium 156.0.8078.4 with the `WebMCPTesting` feature switched on, which is what `chrome://flags/#enable-webmcp-testing` turns on in Chrome.[^3] The probes behind the tables are in the book’s demos repository, in `appendices/a-api-reference/`, and all 25 checks pass. Where Chromium and the draft disagree, the tables show both.

## A.1 The interface at a glance

Listing A.1 is the specification’s IDL index, unabridged. It’s short, which tells you something: the whole imperative API is three methods, three events and seven dictionaries.

**Listing A.1 — The WebMCP IDL, from the specification’s IDL index (15 October 2026) (webmcp.idl)**

```webidl
partial interface Document {
  [SecureContext, SameObject] readonly attribute ModelContext modelContext;
};

[Exposed=Window, SecureContext]
interface ModelContext : EventTarget {
  Promise<undefined> registerTool(ModelContextTool tool, optional ModelContextRegisterToolOptions options = {});
  Promise<sequence<RegisteredTool>> getTools(optional ModelContextGetToolOptions options = {});
  Promise<DOMString> executeTool(RegisteredTool tool, optional object inputObject, optional ModelContextExecuteToolOptions options = {});

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

dictionary RegisteredTool {
  required DOMString name;
  // `title` can be exposed as a `DOMString` since it was taken in by a
  // `USVString`, meaning all unmatched surrogate processing has already been
  // done, and there's no need to do it again on tool exposure.
  DOMString title;
  required DOMString description;
  object inputSchema;
  required Window window;
  required USVString origin;
  ToolAnnotations annotations;
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

Three things about Listing A.1 matter more than the rest:

- **The entry point is `document.modelContext`.** It hangs off `Document`, not `Navigator`, and only exists in secure contexts.[^4] There is one `ModelContext` per document, so every iframe has its own. (Tested: `'modelContext' in document` is `true` and `'modelContext' in navigator` is `false` in Chromium 156.) Appendix D covers the move from `navigator`.
- **There is no `unregisterTool()`.** You unregister by aborting the `AbortSignal` you passed to `registerTool()`.[^5]
- **Results are strings.** `executeTool()` resolves with a `DOMString`, whatever the tool returned.[^6]

## A.2 `registerTool(tool, options)`

```js
await document.modelContext.registerTool(tool, { signal, exposedTo });
```

Registers one tool on the current document. It returns a `Promise<undefined>`; tested, it resolves with `undefined` in Chromium 156 as well.[^5] Chapter 5 introduces it, and chapter 6 covers annotations and the execute callback’s signal.

**Table A.1 — `ModelContextTool` members**

| Member | Type | Required | Rule in the draft |
|---|---|---|---|
| `name` | `DOMString` | yes | 1–128 characters, only ASCII letters and digits, `_`, `-` and `.`; unique per document. Otherwise `InvalidStateError`. |
| `title` | `USVString` | no | Display name for the browser’s UI. |
| `description` | `DOMString` | yes | Must not be empty, or `InvalidStateError`. |
| `inputSchema` | `object` | no | Serialized with `JSON.stringify` at registration. A `toJSON()` that returns `undefined` rejects with a `TypeError`; an error `JSON.stringify` throws (a circular object, for example) is rethrown. Because serializing can run script, the name and fully-active checks run again afterwards. (Tested: when `toJSON()` registers another tool with the same name, Chromium 156 kills the page’s renderer; see Table A.7.) |
| `execute` | `ToolExecuteCallback` | yes | `(inputObject, { signal }) => any`, may return a promise. |
| `annotations` | `ToolAnnotations` | no | See Table A.2. |

The rules in Table A.1 are the draft’s registration steps.[^5] All of them were tested in Chromium 156 and agree: a name with a space, a 129-character name, an empty description and a duplicate name each reject with `InvalidStateError`; a missing `execute`, a circular `inputSchema` and a `toJSON()` that returns `undefined` each reject with `TypeError`.

**Table A.2 — `ToolAnnotations` members (all `boolean`, default `false`)**

| Member | Meaning in the draft |
|---|---|
| `readOnlyHint` | The tool doesn’t modify any state and only reads data. |
| `untrustedContentHint` | The tool’s output contains data that is untrusted from the registering author’s point of view. |
| `consequentialHint` | Running the tool has significant, real-world or non-reversible consequences, such as booking a flight or transferring money. |
| `debugging` | The tool is meant for debugging and developer tooling rather than end-user interactions. |

The wording in Table A.2 paraphrases the draft’s dictionary descriptions.[^7] The draft carries annotations through to `getTools()` but doesn’t say what an agent must do with them; that is the agent’s policy (chapter 6).

**Table A.3 — `ModelContextRegisterToolOptions` members**

| Member | Type | Meaning |
|---|---|---|
| `signal` | `AbortSignal` | Aborting it unregisters the tool. If it’s already aborted, `registerTool()` rejects with the signal’s abort reason. |
| `exposedTo` | `sequence<USVString>` | Origins of other documents in the same tree that may see and call this tool. Each entry must parse as a URL with a potentially trustworthy origin, or the call rejects with `SecurityError`. |

Both members come from the draft’s registration steps.[^5][^8] Tested in Chromium 156: an already-aborted signal rejects with `AbortError` (the default abort reason), and `exposedTo: ['http://example.com']` rejects with `SecurityError: Only secure origins are allowed in the exposedTo list.` Unregistering a tool doesn’t cancel calls already in flight; chapter 6 shows how to handle that.

## A.3 `getTools(options)` and `RegisteredTool`

```js
const tools = await document.modelContext.getTools({ fromOrigins });
```

Returns the tools an in-page agent may see: the tools of every document in the tab’s frame tree that uses the `tools` feature, is same-origin with the caller or listed in `fromOrigins`, and has exposed the tool to the caller’s origin. The list is sorted by `name`.[^9] The browser’s own agent doesn’t use this method; it has an internal mechanism.[^6] Chapter 7 builds an in-page agent on it.

**Table A.4 — `RegisteredTool` members, as `getTools()` returns them**

| Member | Type | Notes |
|---|---|---|
| `name` | `DOMString` | As registered. |
| `title` | `DOMString` | The empty string when no title was given (tested: `""` in Chromium 156). |
| `description` | `DOMString` | As registered. |
| `inputSchema` | `object` | Parsed back from the stored JSON string; absent when none was given. |
| `window` | `Window` | The window of the document that registered the tool. |
| `origin` | `USVString` | That document’s serialized origin. |
| `annotations` | `ToolAnnotations` | Present only when the tool was registered with annotations. |

`fromOrigins` follows the same rule as `exposedTo`: every entry must be a URL with a potentially trustworthy origin, or `getTools()` rejects with `SecurityError`.[^10] Tested, an insecure origin and a string that isn’t a URL both reject that way in Chromium 156.

> **Still in flux: what an empty title looks like**
>
> The draft fills a missing `title` with the empty string, and an inline issue in the `getTools()` steps asks whether to leave the member out instead.[^9] Issue #224, “Tool `title` and `inputSchema`: what to expose when not provided?”, opened on 21 July 2026, was still open on 15 October 2026.[^11] Test for a falsy title, not for `undefined` or `""` specifically.

## A.4 `executeTool(tool, inputObject, options)`

```js
const text = await document.modelContext.executeTool(tool, { query: 'tent' }, { signal });
```

Runs a tool on the document that registered it and resolves with the result as a string. `tool` is a `RegisteredTool`, usually one that `getTools()` returned; the browser looks the tool up again by `name` in the document behind `tool.window` and checks that document’s origin against `tool.origin`, so a hand-made dictionary can’t reach a tool it couldn’t see. A missing `inputObject` becomes `{}`. The options take one member, `signal`: aborting it rejects the promise with the signal’s reason and cancels the execution in the target document.[^6]

**Table A.5 — What `executeTool()` resolves with (tested, Chromium 156)**

| The tool’s `execute` returns | Draft | Chromium 156 |
|---|---|---|
| An object, `{ got: { a: 1 } }` | Its JSON string | `'{"got":{"a":1}}'` |
| A string, `'plain'` | Its JSON string, `'"plain"'` | `'plain'` (not JSON-quoted) |
| `undefined` | Rejects: “unserializable result”, `OperationError` | Resolves with `'undefined'` |
| A `BigInt`, `10n` | Rejects: “unserializable result”, `OperationError` | Resolves with `'10'` |

The draft’s column follows its execution steps, which serialize whatever the tool’s promise fulfils with to a JSON string and treat a failure to do so (`JSON.stringify` throws or yields `undefined`) as the “unserializable result” error.[^6][^1] Chapter 5 recommends returning a small, flat object, which behaves the same everywhere.

## A.5 Events

`ModelContext` is an `EventTarget` with three events. Each has an `on…` handler attribute as well.[^12]

**Table A.6 — `ModelContext` events**

| Event | Interface | Fired at | When (draft) | Tested, Chromium 156 |
|---|---|---|---|---|
| `toolchange` | `Event` | Each document in the tree that can see the changed tool | A tool is registered or unregistered | Fires once per registration and once per unregistration |
| `toolactivated` | `ToolActivatedEvent` (`toolName`) | The `ModelContext` of the tool’s document | Execution of a tool begins, after the input is parsed | Fires once per `executeTool()` call |
| `toolcancel` | `ToolCancelEvent` (`toolName`) | The `ModelContext` of the tool’s document | A pending execution is cancelled; the tool’s `signal` is aborted first | Fires when the caller aborts; the tool’s `signal` aborts too |

The firing rules in Table A.6 are from the draft’s `toolchange` notification steps, its execution steps and its cancellation steps.[^12][^13] The draft warns that `toolchange` is queued from parallel steps, so its timing relative to other tasks can’t be relied on.[^13] `ToolActivatedEvent` and `ToolCancelEvent` were added to the draft on 17 September 2026.[^14]

## A.6 Permissions Policy

All three methods are gated on the policy-controlled feature `tools`, whose default allowlist is `'self'`.[^15] In practice:

- A same-origin iframe can use the API; a cross-origin iframe can’t unless the embedder delegates the feature with `<iframe allow="tools">`.
- `Permissions-Policy: tools=()` on a response turns the API off for that document and every frame inside it. The draft lists this header as a mitigation for pages where WebMCP isn’t an intended capability.[^16]
- A document without the feature gets `NotAllowedError` from `registerTool()`, `getTools()` and `executeTool()`, and `getTools()` in other documents skips it.[^9][^10]

Tested in Chromium 156: with `Permissions-Policy: tools=()`, `document.featurePolicy.allowsFeature('tools')` is `false` and all three methods reject with `NotAllowedError`. A cross-origin iframe without `allow="tools"` gets `NotAllowedError` from `registerTool()`; with `allow="tools"` and `exposedTo` naming the parent, the parent sees the frame’s tool through `getTools({ fromOrigins })` and not without it. Chapter 7 covers the three opt-ins in detail.

## A.7 Errors

The draft names five platform failures for a tool execution and maps each to an exception name. Callers only ever see the exception name.[^1] Other exceptions come from the method steps themselves.[^5][^6][^9] Table A.7 puts all of them next to what Chromium 156 actually does.

**Table A.7 — Exception names: the 15 October 2026 draft vs Chromium 156 with WebMCPTesting (tested)**

| Situation | Method | Draft | Chromium 156 |
|---|---|---|---|
| Document not fully active | all three | `InvalidStateError` | not tested |
| `tools` feature not allowed (header or missing `allow`) | all three | `NotAllowedError` | `NotAllowedError` ✓ |
| Bad name, empty description, duplicate name | `registerTool()` | `InvalidStateError` | `InvalidStateError` ✓ |
| `inputSchema` can’t be serialized; `execute` missing | `registerTool()` | `TypeError` (rethrown) | `TypeError` ✓ |
| Another tool with the same name registered while `inputSchema` is serialized | `registerTool()` | `InvalidStateError` (added 15 October 2026) | **The browser kills the page’s renderer** (a known bug)[^22] |
| Already-aborted `signal` | `registerTool()`, `executeTool()` | The signal’s abort reason | The abort reason ✓ (`AbortError`, or your own reason) |
| Insecure or unparsable origin in `exposedTo` / `fromOrigins` | `registerTool()`, `getTools()` | `SecurityError` | `SecurityError` ✓ |
| `tool.origin` is opaque (`"null"`) or unparsable | `executeTool()` | `NotSupportedError` | `NotSupportedError` ✓ |
| `inputObject` can’t be serialized to JSON (a circular object) | `executeTool()` | The `JSON.stringify` error (rethrown) | `TypeError` ✓ |
| Target document has no navigable (detached), or is in another tab | `executeTool()` | `InvalidStateError` | not tested |
| Tool not registered (unregistered, or a forged `name`) | `executeTool()` | `NotFoundError` | **`UnknownError`** |
| `tool.origin` doesn’t match the target document | `executeTool()` | `NotFoundError` | **`UnknownError`** |
| Tool not exposed to the caller’s origin | `executeTool()` | `NotFoundError` | not tested directly; the tool isn’t in `getTools()` |
| Input can’t be parsed into an object | `executeTool()` | `DataError` | not tested |
| The tool’s `execute` throws or rejects | `executeTool()` | `OperationError` | **`UnknownError`** |
| The result can’t be serialized | `executeTool()` | `OperationError` | **Resolves** (Table A.5) |
| Target document unloaded mid-call (iframe removed) | `executeTool()` | `AbortError` | **`UnknownError`** |
| Caller aborts the `signal` mid-call | `executeTool()` | The signal’s abort reason | `AbortError` ✓, and `toolcancel` fires |

A ✓ means Chromium agrees with the draft; bold marks a difference. Chromium’s `UnknownError` comes in two messages. For a tool that threw it says “Tool was executed but the invocation failed. For example, the script function threw an error”; for a missing or forged tool and a removed frame it says “The operation failed for an unknown transient reason (e.g. out of memory).” The messages aren’t part of any contract, so don’t parse them.

Chapter 7 observed the same `UnknownError` for forged names and origins and for a frame that went away mid-call, and the same `NotAllowedError` under a blocking policy. Until Chromium and the draft line up, treat the two names as one family. Listing A.2 does that.

**Listing A.2 — Classifying an `executeTool()` rejection under both the draft and Chromium 156 (classify-tool-error.js)**

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
> Chromium’s `UnknownError` isn’t a bug against an old idea; it is what the draft itself said until recently. Until 8 October 2026 the `executeTool()` steps rejected with `UnknownError` in each of these cases, next to an inline issue asking for “more granular errors than UnknownError”. A pull request merged that day replaced it with the specific names in Table A.7 and added the tool execution error table.[^17] Chromium 156 still behaves the way the draft read before that change. Expect the right-hand column of Table A.7 to move toward the draft, and key error handling on families (Listing A.2), not on single names.

> **Still in flux: what `registerTool()` resolves with**
>
> Issue #234, “registerTool should return registered tool instead of undefined”, opened on 29 July 2026, was open on 15 October 2026.[^18] Code that ignores the resolved value, as every listing in this book does, won’t break either way.

## A.8 The declarative attributes (removed from the specification)

Chapter 8 covers the declarative API: HTML attributes that turn a `<form>` into a tool. It was removed from the specification on 8 October 2026.[^19] The project README now calls it a “future exploration” that “is not part of the specification at this time”, and its explainer stays in the repository.[^20] Chrome’s documentation still describes it, and Chromium 156’s trial still ships it.[^21]

**Table A.8 — Declarative API surface: removed from the spec on 8 October 2026, still in Chrome’s trial**

| Surface | Where | What it does (Chrome documentation) |
|---|---|---|
| `toolname` | `<form>` | Names the tool; registers the form as a tool. |
| `tooldescription` | `<form>` | Describes the tool. |
| `toolparamdescription` | form controls | Becomes the property’s `description` in the generated JSON Schema. |
| `toolautosubmit` | `<form>` | Submits the form when the agent calls the tool; without it the user clicks Submit. |
| `SubmitEvent.agentInvoked` | event | `true` when an agent triggered the submission. |
| `SubmitEvent.respondWith(promise)` | event | Hands the browser a promise for the form’s result. |
| `:tool-form-active`, `:tool-submit-active` | CSS | Match the form and its submit button while an agent is using them. |

The rows in Table A.8 are from Chrome’s declarative API page (published 18 May 2026, last updated 25 September 2026).[^21] Tested in Chromium 156: a `<form toolname="search_availability" tooldescription="Find free tables">` with a required `date` input and a required `number` input (`min="1" max="12"`) shows up in `getTools()` as a tool with a generated schema: `date` becomes `{ type: 'string', format: 'date' }`, `partySize` becomes `{ type: 'number', minimum: 1, maximum: 12, multipleOf: 1 }`, and both are listed in `required`.

> **Still in flux: the declarative API**
>
> Removed from the specification is not the same as removed from Chrome. Use the attributes only behind feature detection, keep an imperative tool for the same action, and check chapter 8 and the Chrome page before relying on them.

## A.9 Summary

- The API is `document.modelContext` with three methods: `registerTool(tool, { signal, exposedTo })`, `getTools({ fromOrigins })` and `executeTool(tool, input, { signal })`, plus three events: `toolchange`, `toolactivated` and `toolcancel`.
- Unregister by aborting the signal. There’s no `unregisterTool()`, `provideContext()` or `clearContext()` any more (Appendix D).
- The `tools` Permissions Policy feature, default `'self'`, gates all three methods; without it you get `NotAllowedError`.
- `exposedTo` and `fromOrigins` accept only potentially trustworthy origins; anything else is a `SecurityError`.
- Chromium 156 reports most execution failures as `UnknownError` where the draft says `NotFoundError`, `OperationError` or `AbortError`, and it resolves results the draft would reject. Handle errors by family.
- The declarative form attributes left the specification on 8 October 2026 but still work in Chrome’s trial.

[^1]: WebMCP specification, Draft Community Group Report, 15 October 2026, §3 Supporting concepts: the tool execution error table (“tool not found” → `NotFoundError`, “invalid input” → `DataError`, “tool rejected” and “unserializable result” → `OperationError`, “target document unloaded” → `AbortError`) and the note that tool execution errors are not exposed to the web. Read 15 October 2026. <https://webmachinelearning.github.io/webmcp/#tool-execution-error>
[^2]: WebMCP specification, Draft Community Group Report dated 15 October 2026, editors Brandon Walderman (Microsoft), Khushal Sagar and Dominic Farolino (Google), published by the W3C Web Machine Learning Community Group. Read 15 October 2026. The changes since the 14 October draft are commits 1636b33 (#345) and 3279798 (#347); neither touches the IDL or the exception names. <https://webmachinelearning.github.io/webmcp/>
[^3]: Chrome for Developers, “WebMCP” overview (published 18 May 2026, last updated 7 October 2026), section “Local WebMCP”: the `chrome://flags/#enable-webmcp-testing` flag. Read 15 October 2026. <https://developer.chrome.com/docs/ai/webmcp>
[^4]: WebMCP specification, §4.1 Extensions to Document and the IDL index: `partial interface Document { [SecureContext, SameObject] readonly attribute ModelContext modelContext; }`. <https://webmachinelearning.github.io/webmcp/#idl-index>
[^5]: WebMCP specification, §4.2, the `registerTool(tool, options)` method steps: the “tools” check, the name, description and duplicate checks, `inputSchema` serialization and the checks repeated after it, the already-aborted signal, `exposedTo` parsing, and the abort steps that unregister the tool. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool>
[^6]: WebMCP specification, §4.2, the non-normative description of `executeTool()` (resolves to the stringified result; an omitted argument becomes an empty object) and the `executeTool(tool, inputObject, options)` method steps (including the rethrown error when `inputObject` can’t be serialized, and `InvalidStateError` when the target document has no navigable). <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-executetool>
[^7]: WebMCP specification, §4.2.1, the `ToolAnnotations` dictionary descriptions. <https://webmachinelearning.github.io/webmcp/#dictdef-toolannotations>
[^8]: WebMCP specification, §4.2.3 ModelContextRegisterToolOptions Dictionary: `exposedTo` is “an array of origins that control which documents this tool is exposed to, in the current document’s tree”; `signal` “unregisters the tool when aborted”. <https://webmachinelearning.github.io/webmcp/#dictdef-modelcontextregistertooloptions>
[^9]: WebMCP specification, §4.2, the `getTools(options)` method steps: traversal of the inclusive descendant navigables, the “tools” check per document, the same-origin-or-`fromOrigins` check, the exposure check, the empty-string `title` with its inline reference to issue #224, and sorting by name. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-gettools>
[^10]: WebMCP specification, §4.2.4 ModelContextGetToolOptions Dictionary and the `getTools()` steps (`SecurityError` for an origin that fails to parse or is not potentially trustworthy). <https://webmachinelearning.github.io/webmcp/#dom-modelcontextgettooloptions-fromorigins>
[^11]: “Tool `title` and `inputSchema`: what to expose when not provided?”, webmachinelearning/webmcp issue #224, opened 21 July 2026, open on 15 October 2026. <https://github.com/webmachinelearning/webmcp/issues/224>
[^12]: WebMCP specification, §4.3 Events, §4.3.1 ToolActivatedEvent Interface and §4.3.2 ToolCancelEvent Interface. <https://webmachinelearning.github.io/webmcp/#events>
[^13]: WebMCP specification: the steps that notify documents of a tool change (including the note on `toolchange` timing), the execute-callback steps that fire `toolactivated`, and the steps that cancel a pending tool execution and fire `toolcancel`. <https://webmachinelearning.github.io/webmcp/#eventdef-modelcontext-toolcancel>
[^14]: webmachinelearning/webmcp commit f5645e9, “Add `ToolActivatedEvent` and `ToolCancelEvent` event interfaces (#245)”, committed 17 September 2026; repository history read 15 October 2026. <https://github.com/webmachinelearning/webmcp/commit/f5645e9aea51eb589599f181d104a2f49430608e>
[^15]: WebMCP specification, §4.4 Permissions policy integration: the policy-controlled feature “tools” with a default allowlist of `'self'`. <https://webmachinelearning.github.io/webmcp/#permissions-policy>
[^16]: WebMCP specification, §6.4.1 Disabling WebMCP with Permissions Policy. <https://webmachinelearning.github.io/webmcp/#mitigation-disable-permissions-policy>
[^17]: webmachinelearning/webmcp commit b206dae, “Replace UnknownError with specific DOMException types. (#339)”, by Mark Foltz, committed 8 October 2026: it removes the `UnknownError` rejections and their “Support more granular errors” issue notes from `index.bs` and adds the `NotFoundError` / `DataError` / `OperationError` / `AbortError` table. Repository history and diff read 14 October 2026. <https://github.com/webmachinelearning/webmcp/commit/b206dae8bad34ea8e6ff7213b417b50b14a37e9a>
[^18]: “registerTool should return registered tool instead of undefined”, webmachinelearning/webmcp issue #234, opened 29 July 2026, last updated 3 October 2026, open on 15 October 2026. <https://github.com/webmachinelearning/webmcp/issues/234>
[^19]: webmachinelearning/webmcp commit 14ae813, “Remove declarative API from the spec for now (#338)”, by François Beaufort, committed 8 October 2026; it changed `index.bs` and `README.md`. Repository history read 14 October 2026. <https://github.com/webmachinelearning/webmcp/commit/14ae813cc4e9fe0d39313f4b1ee5b231746731ad>
[^20]: webmachinelearning/webmcp README, section “Future Exploration: Declarative API”, and the Declarative API Explainer, both read 15 October 2026. <https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md>
[^21]: Chrome for Developers, “Declarative API” (published 18 May 2026, last updated 25 September 2026): `toolname`, `tooldescription`, `toolparamdescription`, `toolautosubmit`, `SubmitEvent.agentInvoked`, `SubmitEvent.respondWith()`, `:tool-form-active` and `:tool-submit-active`. Read 15 October 2026. <https://developer.chrome.com/docs/ai/webmcp/declarative-api>
[^22]: Chromium issue 573722078, “WebMCP: Renderer killed when `registerTool()`’s `inputSchema` serialization registers a tool with the same name”, filed 14 October 2026 (Blink > Agentic Platform > WebMCP). The browser terminates the renderer for a bad IPC message, reason 345 (`RFHI_WEBMCP_REGISTER_DUPLICATE_TOOL_NAME`). The issue is marked Fixed, but the fix (crrev.com/c/8583183) was reverted on main (crrev.com/c/8575491) and had not relanded as of 15 October 2026, 09:26 UTC. <https://issues.chromium.org/issues/573722078>
