# Fidelity ledger: `waitForToolsUntil` (pull request #373)

Checked 27 November 2026. Branch `spec/wait-for-tools-until`, from `main`.

## Sources actually read

- webmachinelearning/webmcp pull request #373, merged 24 November 2026 at 03:10 UTC (merge commit `47e2b993ea9fd0599ffca3f58588eb3fd5f474f2`). Title: “Signal tool stability with waitForToolsUntil() for user agent observations”. Diff of `index.bs` only. Description: implement the resolution from issue #328, add the IDL and `tools-ready` state, and record that state on an observation. Wiring the wait into `getTools()` and changing `toolchange` dispatch is deferred. The description’s earlier sentence about waiting inside `perform an observation` is not what merged. The merge commit message says “Move tools ready to observed tool collection and drop the wait algorithm”.
- `index.bs` on `main`. `list_commits` for that path since 24 November 2026 returns only `47e2b993`. The published draft at https://webmachinelearning.github.io/webmcp/ was retrieved 27 November 2026 and is dated 24 November 2026. Its `waitForToolsUntil` steps match `index.bs`.
- Issue #328, “Signaling tool stability to agents”, still open on 27 November 2026 (`updated_at` that day). The draft’s inline issue still says `tools ready` should start false, and that the lifecycle point is unresolved. The initial value in the merged text is `true`.
- Issue #374, “Batch toolChange notifications for tool registry changes”, opened 4 November 2026, still open on 27 November 2026. The pull request adds the same question as an inline issue. The notify-documents steps still fire one event per call.
- Pull request #375, still open on 27 November 2026 (updated 26 November, 21 commits, head `674ba1ae`). `generalized-tool-calling.md` on that head still declares `undefined waitForToolsUntil(Promise<any> promise)` on `ToolManager`. The first `Tool` block still matches Listing F.1. The rest of the explainer was not re-audited. #375 does not edit `index.bs`.
- Chromium commit `dc7d570dff77eca05dae42b1fa6e3b816205a94f`, Khushal Sagar, 25 November 2026, `refs/heads/main@{#1754836}`, review https://chromium-review.googlesource.com/c/chromium/src/+/8839808. Chromium Dash `fetch_commit` (retrieved 27 November 2026): canary `160.0.8185.0`, not beta, dev, or stable. The commit message ships the method by removing the `WebMCPWaitForToolsUntil` runtime feature so origin-trial pages can call it. `ModelContext` stays `RuntimeEnabled=WebMCP`.
- At that revision, read from source, not from a browser:
  - `third_party/blink/renderer/core/script_tools/model_context.idl`: `[CallWith=ScriptState, RaisesException] undefined waitForToolsUntil(Promise<any> promise);`
  - `model_context.cc` was **not** in the commit diff. At that tree, `waitForToolsUntil` ignores an already-settled promise. The first unsettled promise calls `SetScriptToolsReady(false)` and starts `kWaitForToolsWarningDelay` of 10 seconds. The timer logs a console warning. It does not set script tools ready. The comment says the delay matches the actor observation timeout.
  - `components/actor/core/actor_features.cc`: `kActorObservationDelayTimeout` defaults to `base::Seconds(10)`, described as the overall observation timeout. `observation_delay_metrics_browsertest.cc` at that revision has `ScriptToolsDelayTimesOut`, which overrides the timeout to 3 seconds and expects the controller to finish with `kOk` and a timeout metric while tools are still not ready.
  - `RenderFrameHostImpl::GetScriptToolsReadyState`: `kLoading` until `DOMContentLoaded`, then `kWaiting` if `script_tools_waiting()`, otherwise `kReady`. The commit message says an observation that waits on script tools waits at least until `DOMContentLoaded`.

## What was not re-tested

No Chrome or Chromium 160 probe was run. No web-platform-tests recount. `usewebmcp` 6.0.3, VueUse, and Angular 22.2 were not re-read for a call to `waitForToolsUntil`. Whether Chromium 156.0.8078.4 exposed the method behind `WebMCPWaitForToolsUntil` was not checked. The 10-second warning and the actor timeout were read from the tree at `dc7d570`, not from a later Chromium commit.

The author’s summary for this task said tools are considered ready once every promise has settled or after a timeout, currently 10 seconds in Chrome. The specification says the timeout removes the promise, so the document becomes ready. Chrome at `dc7d570` does not do that. The 10 seconds are a warning plus the agent observation timeout. The book follows the specification and that Chromium tree, and says so.

## Listing change ledger (for the demos sync)

### Listing 5.2 — not a demos file

Label: registration IDL excerpt.

Before: caption dated the excerpt to the 27 October 2026 draft. No `waitForToolsUntil` line. The excerpt already contained `outputSchema`, which that date did not have.

After: caption names the 24 November 2026 draft for `waitForToolsUntil()`. The line `undefined waitForToolsUntil(Promise<any> promise);` is added after `registerTool`. The omitted `getTools` / `executeTool` comment is unchanged.

### Listing 5.7 — new, `chapters/05-registering-tools/wait-for-tools.js`

New file for the demos repo. `registerToolsWhenReady` uses `Promise.allSettled`, aborts a batch controller if any registration rejected, and calls `document.modelContext.waitForToolsUntil?.(toolsUpdated)` while that promise is still pending. Not run on Chromium 156 or Chrome 160. No `TODO` token.

### Listing 10.12 — new, `chapters/10-webmcp-in-frameworks/on-route-change.js`

New file. `onRouteChange` aborts the previous controller, registers `route.tools` with `Promise.allSettled`, and calls `waitForToolsUntil?.`. It does not roll back a partial success. The prose points at Listing 5.7 for that. Not part of the Chromium 156 route suite.

### Listing 15.2 — `chapters/15-browser-support-and-standards/webmcp-support.js`

Before: `methods` filtered `registerTool`, `getTools`, `executeTool`.

After: the filter also includes `waitForToolsUntil`. The 2 November Chromium 156 run was of the previous listing and reported the first three. This edition did not re-run it.

### Listing 17.2 — `chapters/17-the-road-ahead/src/adapter.js`

Before: `export async function registerCatalog` awaited each `registerTool` and aborted the batch in `catch`. No readiness call.

After: `registerCatalog` is a non-async function. It returns `registerBatch`’s promise (or `Promise.resolve([])` when WebMCP is absent) and passes that same promise to `waitForToolsUntil?.`. `registerBatch` is the old body. Callers that `await registerCatalog(...)` still receive the array of names, because they await the returned promise. The fourteen checks were not re-run. On a build without the method, `?.` is a no-op.

### Listing 17.3 — `chapters/17-the-road-ahead/src/probe.js`

Before: the report had no `waitForToolsUntil` field. The printed JSON is the 2 November Chromium 156 result.

After: `waitForToolsUntil: typeof mc?.waitForToolsUntil === 'function'` is in the report object, before `resumeTool`. The printed JSON is unchanged and does not include the field. The prose says the probe was not re-run.

### Listing A.1 — `appendices/a-api-reference/webmcp.idl`

Before: three methods. Caption: 23 November 2026 draft.

After: `undefined waitForToolsUntil(Promise<any> promise);` between `registerTool` and `getTools`. Caption: 24 November 2026 draft. The rest of the IDL index is unchanged.

### Listing F.1 — do not sync as runnable demo code

Unchanged. Still the unmerged `Tool` with `execute()` from pull request #375. Confirmed against the explainer’s first `Tool` block on 27 November 2026. Not the specification.

### Figures

Figure 17.1 was not redrawn. Its caption remains “as of 2 November 2026”. The prose says Table 17.1’s readiness row is later. Figure D.1 was not redrawn. Its caption still describes the 27 October draft as having no IDL change, which is true of that date.

## Per-file coverage

| File | What changed |
| --- | --- |
| Chapter 4 | One sentence: `waitForToolsUntil()` exists from the 24 November draft, with a pointer to Chapter 5. |
| Chapter 5 | Opening names #373. Listing 5.2 gains the method. Page-state section points at the new section. New section and Listing 5.7: multiple calls, settlement including rejection, implementation-defined timeout, Chrome 10-second warning versus the actor timeout, `DOMContentLoaded` loading state, optional chaining, `Promise.all` versus `Promise.allSettled`, rollback inside the promise, throws versus rejected promises, #328 still open, #374 still one event per change. Summary bullets. |
| Chapter 6 | The #328 sentence no longer says there is no decision. `toolchange` is still one event per change. #374 named. Summary bullet. |
| Chapter 7 | `waitForToolsUntil()` throws `NotAllowedError` instead of rejecting. Listing 7.4 unchanged. Prose says `getTools()` does not wait. |
| Chapter 9 | One sentence after the all-or-nothing rollback. Listing 9.4 was not edited. |
| Chapter 10 | Route-test paragraph names the gap. New section and Listing 10.12. Summary bullet. Hooks were not re-read. |
| Chapter 14 | Paragraph after the `Tool` version note. Tests not re-run. WPT directory not re-counted. |
| Chapter 15 | Status line is 24 November 2026, retrieved 27 November. Table 15.1 gains the 24 November row. Listing 15.2 lists the method when present. “Eleven” spec changes. Summary dates. |
| Chapter 17 | Table 17.1 gains a readiness row. Figure 17.1 not redrawn. Checklist item 3. Listing 17.2 and 17.3 as above. Summary date. |
| Appendix A | IDL, four methods, new Section A.3, later sections renumbered (old A.3–A.10 are A.4–A.11). Permissions policy, Table A.7 rows for the throws, `toolchange` / #374, summary. |
| Appendix B | ModelContext, NotAllowedError, observation, tools ready, `waitForToolsUntil`. Flux note names 24 November and says #375 was still open on 27 November. |
| Appendix C | Rows for chapters 5, 10 and 17 name the new or changed listings. Section A.10 cross-reference (was A.9). |
| Appendix D | The “nothing after 8 October changes the API shape” sentence now names the three later IDL changes. The flux box says #373 is additive. |
| Appendix E | New E.4. The `Tool` build 160.0.8173.0 and the method’s build 160.0.8185.0 are different canaries. |
| Appendix F | Not superseded. #373 added the method on `document.modelContext`. #375 would move a method of the same signature to `window.toolManager` and was still open on 27 November. |
| `Book.txt` | Unchanged. No new chapter file. |
| `CHANGELOG.md` | Unreleased note. Version in `tools/book.json` was not bumped. No browser retest. |
| `VALIDATION.md` | Short 27 November evidence block pointing at this ledger. |

## Flagged

- Chrome build 160.0.8185.0 is the canary deployment Chromium Dash records for `dc7d570`. It was not found in a separate Chrome release note. Stable for milestone 160 is still the date already in the book, 5 January 2027, from the earlier Appendix E check. That stable date was not re-fetched on 27 November.
- The 10-second actor timeout is the default of a feature param (`actor-observation-delay-timeout`). A field trial or a flag can change it. The book calls it the default at that revision.
- `model_context.cc`’s already-settled early return is Chrome, not the specification. The specification appends the promise and then reacts.
- Chrome reports loading until `DOMContentLoaded` even when the page never calls `waitForToolsUntil()`. The specification’s flag starts `true`. Both are stated. They were not observed in a browser.
- Issue #234 was not re-checked after 2 November 2026. The Appendix A callout says so.
- Pull request #375’s explainer has moved since 23 November. Only the `ToolManager` method and the first `Tool` block were compared on 27 November.
- Listing 5.7, Listing 10.12, the Listing 15.2 method name, Listing 17.2 and the new Listing 17.3 field were not executed.
