# Appendix E: From RegisteredTool to Tool

> *“`Tool` objects can only be obtained from `getTools()`, and each one refers to the specific tool registration it was returned for.”*
>
> — WebMCP explainer, after pull request #348[^appe-1]

Pull request #348 merged on 19 November 2026. It replaced the `RegisteredTool` dictionary with a `Tool` interface. The published specification that includes it is the Draft Community Group Report dated 23 November 2026.[^appe-2] Chrome exposes the new object starting in version 160.0.8173.0.[^appe-3] Chrome 160 reaches the stable channel on 5 January 2027.[^appe-4] Until that date, code that also has to run on earlier Chrome needs the fallback in Listing E.1.

This book’s own browser tests were run on Chromium 156. They were not re-run on Chrome 160. Where this appendix describes what Chrome 160 returns, the source is the specification, Chrome’s Imperative API page (updated 20 November 2026) and the pull request, not a new probe.[^appe-2][^appe-3][^appe-5]

## E.1 What changed

`getTools()` still returns a promise for a list sorted by name. Each entry is now a `Tool` interface object, not a dictionary. `executeTool()` takes that object. The internal identifier that ties the object to one registration is not a property you can read. `executeTool()` uses it so that the call runs the tool `getTools()` actually returned.

**Table E.1 — `RegisteredTool` and `Tool`**

| | `RegisteredTool` (before Chrome 160.0.8173.0) | `Tool` (specification of 23 November 2026, Chrome 160.0.8173.0 and later) |
|---|---|---|
| Kind | Dictionary | Interface |
| Who creates it | Any script can build one | Only `getTools()` |
| Identity | `name` plus `window` | An internal id. A later tool with the same name is a different object |
| Window member | `window`, a `Window` | `source`, a `WindowProxy`, or `null` if the registering document is no longer fully active |
| Missing `inputSchema`, `outputSchema` or `annotations` | `undefined` (Chromium 156 omitted the member) | `null` |
| Missing `title` | `""` | `""`. The 23 November specification still has inline issue #224 on whether to drop that default |
| `JSON.stringify(tool)` | The dictionary’s own fields | `"{}"` |
| `{...tool}` | A copy of the fields | An empty object |
| `structuredClone(tool)` | Clones the dictionary | Throws a `DataCloneError`. `Tool` is not serializable |
| Stale tool after unregister and re-register under the same name | Could run the new tool | `executeTool(oldTool)` rejects with `NotFoundError` |
| Two calls to `getTools()` | Distinct dictionaries | Distinct objects, never `===`, even while the tool stays registered |

The `null` defaults are in the `getTools()` steps: a missing schema or a missing annotations dictionary is stored as `null`, not left absent.[^appe-2] `JSON.stringify`, object spread and `structuredClone` are recorded as compatibility notes in the pull request, not as separate algorithms in the specification.[^appe-1] `JSON.stringify` and object spread copy enumerable own properties. The attributes live on the prototype, so stringify returns the string `"{}"` and a spread copies nothing. `structuredClone` throws a `DataCloneError` because the interface is not declared serializable.

Chrome’s documentation logs a tool and shows `source`, `title: ""` and `outputSchema: null`.[^appe-5] That is the inspector walking the getters. It is not the string `JSON.stringify` would produce.

Opaque-origin documents are not executable yet. If `tool.origin` is an opaque origin, `executeTool()` still rejects with `NotSupportedError`. Issue #349, which asks to allow that case, was still open on 23 November 2026. Pull request #348 makes the lookup by id, which is what a later change would need. It does not itself allow the call.[^appe-6]

## E.2 Reading a tool without breaking older Chrome

Read the attributes you need. Do not stringify the tool, do not spread it, and do not pass it to `postMessage` or `chrome.runtime.sendMessage`. Copy the fields into a plain object first. For the window, use `source` and fall back to `window` until Chrome 160 is stable.

**Listing E.1** `appendices/e-tool-interface/read-tool.js` — read a `Tool` on Chrome 160 and on earlier Chrome

```js
export async function readTools() {
  const tools = await document.modelContext.getTools();
  const readable = [];
  for (const tool of tools) {
    // `null` means the registering document is gone. `??` would replace
    // that null with `window`. Remove the `window` fallback when Chrome
    // 160 reaches Stable (5 January 2027).
    const source = tool.source !== undefined ? tool.source : tool.window;
    if (source == null) continue;
    readable.push({
      name: tool.name,
      title: tool.title,
      description: tool.description,
      origin: tool.origin,
      inputSchema: tool.inputSchema ?? null,
      outputSchema: tool.outputSchema ?? null,
      annotations: tool.annotations ?? null,
      source,
    });
  }
  return readable;
}
```

`tool.source !== undefined ? tool.source : tool.window` is the compatible read. On Chrome 160, `source` is a `WindowProxy` or `null`, and it is never `undefined`, so the expression does not read `window`. On earlier Chrome, `source` is `undefined`, so the expression is the old `window` member. `??` is the wrong operator here: it replaces `null` as well as `undefined`, and a `null` `source` means the registering document is no longer fully active. Listing E.1 drops that tool. Calling `executeTool()` on it rejects with `InvalidStateError`, which is the specification’s check for a document that is not fully active, before the internal id is consulted.[^appe-2]

Destructuring (`const { name } = tool`) does call the getters, so it still works. Spreading does not. The same split is why Listing 7.9 copies fields by name before it sends them to the extension’s service worker.

Pass the object from `getTools()` through to `executeTool()` unchanged. A hand-built dictionary, and a shallow copy, worked in Chromium 156 because `RegisteredTool` was a dictionary and the browser looked the tool up by name. They are not `Tool` objects, and `executeTool()` will not accept them once Chrome is on the new interface. Holding an old `Tool` across an unregister-and-reregister is also wrong: the id refers to the registration that has gone, and the call rejects with `NotFoundError` instead of running the new tool.[^appe-2]

## E.3 What to change in existing code

1. Replace every read of `tool.window` with `tool.source !== undefined ? tool.source : tool.window`. Delete the fallback after 5 January 2027. Skip a `null` result.
2. Treat a missing schema or missing annotations as `null`, not as a missing property. `value ?? null` covers both Chrome generations.
3. Copy fields into a plain object before `JSON.stringify`, object spread, `postMessage` or `structuredClone`.
4. Keep passing the object `getTools()` returned into `executeTool()`. Do not rebuild it.
5. After a `toolchange`, call `getTools()` again. Do not reuse a `Tool` from before the change if the tool may have been replaced.
6. Keep testing the way Chapter 14 describes, and record the browser version. Chromium 156 and Chrome 160 do not return the same shape.

Chapter 7 is the chapter that uses `getTools()` and `executeTool()`. Appendix A is the IDL. The generic-calling proposal in pull request #375 is a different design and is not part of this migration (Appendix F).

## Notes

[^appe-1]: Dominic Farolino, “Introduce the `Tool` interface”, webmachinelearning/webmcp pull request #348 (opened 15 October 2026, merged 19 November 2026). The pull request description records the compatibility changes: missing `inputSchema` and `annotations` are `null` rather than `undefined`, `JSON.stringify(tool)` returns `"{}"`, object spread copies nothing, and `structuredClone(tool)` throws because `Tool` is not serializable. <https://github.com/webmachinelearning/webmcp/pull/348>
[^appe-2]: WebMCP specification, Draft Community Group Report, 23 November 2026, §4.2 ModelContext (`getTools()` returns `sequence<Tool>`, `executeTool()` takes a `Tool`) and §4.2.6 Tool Interface, including the `getTools()` steps that set a missing schema or annotations to `null`, the `source` getter, the `executeTool()` step that rejects with `InvalidStateError` when the registering document is not fully active, and the note that a stale `Tool` rejects with `NotFoundError` after an unregister-and-reregister (retrieved 23 November 2026). <https://webmachinelearning.github.io/webmcp/#tool-interface>
[^appe-3]: François Beaufort, “Support the WebMCP Tool interface”, GoogleChromeLabs/webmcp-extension pull request #105 (opened 18 November 2026, merged 23 November 2026). It states that `getTools()` returns `Tool` objects starting in Chrome 160.0.8173.0, and that a `tool.window` fallback can be removed when Chrome 160 reaches Stable. Chromium Dash records the linked commit in canary 160.0.8173.0 (retrieved 23 November 2026). The pull request’s helper is `tool.source ?? tool.window ?? null`; this appendix tests `!== undefined` so that a `null` `source` stays `null`. <https://github.com/GoogleChromeLabs/webmcp-extension/pull/105> <https://chromiumdash.appspot.com/commit/8d7371ff0e6e38bea93b9ff2bb594fb2b788fdbe>
[^appe-4]: Chromium release schedule, milestone 160: stable date 5 January 2027 (retrieved 23 November 2026). <https://chromiumdash.appspot.com/schedule>
[^appe-5]: Chrome for Developers, “WebMCP Imperative API”, “Discover tools” (page last updated 20 November 2026, retrieved 23 November 2026). The logged tool shows `source`, `title: ""` and `outputSchema: null`. <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
[^appe-6]: webmachinelearning/webmcp issue #349, “Allow `executeTool()` to execute tools registered by opaque-origin documents”. The 23 November 2026 specification still rejects an opaque `Tool` origin with `NotSupportedError`, and its `executeTool()` steps still point at #349 as unresolved (retrieved 23 November 2026). <https://github.com/webmachinelearning/webmcp/issues/349>
