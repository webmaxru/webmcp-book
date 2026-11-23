# Appendix F: Possible Upcoming Changes

> *“This proposal includes three concrete API changes to satisfy great feedback from Mozilla.”*
>
> — Dominic Farolino, pull request #375[^appf-1]

Pull request #375, “Introduce generic tool calling explainer”, was open on 23 November 2026. It had not been merged. It adds one new file, `generalized-tool-calling.md`, and it does not change the specification. The text below is the state of that pull request on that date. It can still change, and it can be rejected.

It is not pull request #348. #348 merged on 19 November 2026 and is the `Tool` interface Appendix E describes: `getTools()` and `executeTool()` stay on `document.modelContext`, and `window` becomes `source`. #375 starts from Mozilla’s issues #236 and #237 and proposes a different split of the API. Where the two overlap, they overlap only in the idea of a tool handle. They are not the same change, and nothing in this appendix is the API to write against today.

## F.1 What the explainer proposes

The explainer, by Dominic Farolino and Khushal Sagar, names two jobs. One is web-to-web function calls, the kind of call sites now build on `postMessage`. The other is web-to-model tools, which is the WebMCP this book is about. It then sketches three areas.[^appf-1]

**Registration moves off `document.modelContext`.** A document would register tools on `window.toolManager`, with `registerTool()` and `waitForToolsUntil()`. The permissions policy would not gate this half. The only constraint in the sketch is that the documents share a browsing context group and the caller holds a `Window` reference. `exposedTo` would stay. Other names the explainer lists, and does not choose among, are `toolHost`, `toolProvider` and `toolRegistrar`.

**Discovery moves onto `Window`.** `getTools()` would be a cross-origin method on the target window (`iframe.contentWindow`, `parent`, `opener`, or the window `open()` returned), not a walk of the frame tree from `document.modelContext`. A `ToolObserver`, built in the caller’s realm, would report the current list and later changes. The explainer rejects an `EventTarget` for this job because a `change` event would still need a second `getTools()` call, and it rejects hanging a `tools` object on `Window` because that object’s lifetime is hard to keep across navigations.

**Execution moves onto the tool.** A `Tool` would have `name`, `source`, `origin` and `execute()`. There is no `executeTool()` on `ModelContext` in this sketch. Calling `execute()` on a tool that has been unregistered would throw. The explainer leaves open whether a userland error is returned as itself or wrapped in a non-constructible `ToolError`. Listing F.1 is that proposed interface, and only that. It is not the `Tool` in the 23 November specification.

**Listing F.1** `generalized-tool-calling.md` (excerpt from pull request #375, not merged) — the `Tool` this explainer proposes

```webidl
[Exposed=Window, SecureContext]
interface Tool {
  readonly attribute DOMString name;
  readonly attribute WindowProxy? source;
  readonly attribute USVString origin;

  Promise<any> execute(optional object inputObject, optional ToolExecuteOptions options = {});
};
```

The merged `Tool` has `title`, `description`, `inputSchema`, `outputSchema` and `annotations` as well, and it has no `execute()` method. Do not combine the two listings.

## F.2 Inputs, outputs and who the tool is for

The explainer wants ordinary web-to-web calls to accept any structured-cloneable value, and model-facing tools to stay on JSON. The switch would be a `naturalLanguageProperties` dictionary on the tool: `title`, `description`, `inputSchema`, `outputSchema` and `annotations`. Supplying it would opt the tool into JSON inputs and outputs and into exposure to the user agent. The explainer suggests renaming the `tools` permissions policy to `user-agent-tools` for that exposure.

It also argues that model-facing tools should accept a JSON-compatible subset of platform objects (`ImageData` is the example) and that a thrown `DOMException` or `Error` could be the error result, so a page would not have to wrap every failure in a special JSON object. The exact schema keyword for those platform types is left open. A separate note points at a work-in-progress gist for the schema subset and says that gist would be moved into the explainer later. That gist is not part of the specification.

None of this is in the 23 November draft. Chapters 5, 6 and 11 still describe the current rules: JSON in, a JSON string out of `executeTool()`, and errors either as return values or as `DOMException` names.

## F.3 Later sections of the same explainer

The rest of the file is labelled future work, not a proposal with IDL in the specification.

- **Workers.** `ToolManager` on `WorkerGlobalScope`, `getTools()` on the worker’s owner, and a `ToolSource` that is either a `WindowProxy` or a `Worker`.
- **A composed tool set.** One query would collect tools from descendant frames. The explainer says the query root, not the caller, should decide which frames count, and that permission policy is the wrong tool for that decision because it walks every ancestor. Iframes inside a shadow tree would be excluded unless the shadow tree opted in, because a same-origin `source` would otherwise reveal the shadow tree.
- **Passing a `Tool` through `postMessage`.** A document could hand its handle to another document. The explainer lists three options for what `source` would be after that hand-off and does not pick one.

Issue #236 is the thread this explainer comes from. Chapter 17 records that thread. If #375 lands, the migration is larger than Appendix E: registration, discovery and execution all move. Until it lands, keep tools on `document.modelContext`.

## Notes

[^appf-1]: Dominic Farolino, “Introduce generic tool calling explainer”, webmachinelearning/webmcp pull request #375 (opened 6 November 2026, open on 23 November 2026, not merged). The pull request adds `generalized-tool-calling.md` only. Authors named in the file: Dominic Farolino and Khushal Sagar. It cites issues #236 and #237. <https://github.com/webmachinelearning/webmcp/pull/375>
