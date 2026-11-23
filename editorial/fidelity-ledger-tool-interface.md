# Fidelity ledger: Tool interface (Chrome 160)

Checked 23 November 2026. Branch `spec/tool-interface-chrome160`, stacked on `editorial/serious-tech-prose`.

## Sources actually read

- webmachinelearning/webmcp pull request #348, merged 19 November 2026. Diff of `index.bs` and `README.md`, and the pull request description (null instead of undefined, `JSON.stringify` returns `"{}"`, spread copies nothing, `structuredClone` throws).
- `index.bs` on `main` after that merge, and the published draft at https://webmachinelearning.github.io/webmcp/ dated 23 November 2026 (retrieved the same day). `Tool` IDL, `getTools()` / `executeTool()` signatures, `source` getter, `null` for a missing schema or annotations, lookup by internal id, `NotFoundError` after unregister-and-reregister, opaque origin still `NotSupportedError`, inline issue #224 still present.
- Pull request #375, open on 23 November 2026, not merged. Diff is a new explainer only (`generalized-tool-calling.md`). It does not edit `index.bs`.
- GoogleChromeLabs/webmcp-extension pull request #105 (François Beaufort, open on 23 November 2026): Chrome 160.0.8173.0, `source ?? window`, remove the fallback when Chrome 160 is stable.
- Chromium milestone schedule: Chrome 160 stable date 5 January 2027 (https://chromiumdash.appspot.com/schedule, retrieved 23 November 2026).
- Chrome for Developers, “WebMCP Imperative API”, last updated 20 November 2026: the logged tool shows `source`, `title: ""`, `outputSchema: null`.
- GitHub API on 23 November 2026: #204 open, #355 open, #375 open, issue #349 open.

## What was not re-tested

No Chromium 160 probe was run. Every “tested” or “observed” sentence that names Chromium 156 is still about Chromium 156. Listing 7.9’s new fallback was not part of the 2 November test run. The sentence in Chapter 7 says so.

The build number 160.0.8173.0 is from Beaufort’s extension pull request and from the author’s summary of this task. It was not confirmed from a Chromium release note or a `chrome/VERSION` file.

## Listing change ledger (for the demos sync)

### Listing 7.4 — not a demos file

Label: `ModelContext` — discovery and execution, from the specification’s IDL.

Before: abridged 27 October IDL. `getTools()` returned `sequence<RegisteredTool>`, `executeTool()` took `RegisteredTool`, and the dictionary had `window` and no `outputSchema`.

After: abridged 23 November IDL. `sequence<Tool>`, `executeTool(Tool, ...)`, and the `Tool` interface with `object?` schemas, `WindowProxy? source`, `USVString origin`, `object? annotations`.

### Listing 7.9 — `extension/content-script.js`

Before: `.filter((t) => t.window === window)` and a destructure of `name`, `description`, `inputSchema`, `annotations`. The execute path compared `t.window === window`.

After: `.filter((t) => (t.source ?? t.window) === window)`, an explicit field copy with `inputSchema` and `annotations` normalized by `?? null`, and the same `source ?? window` test when finding a tool to run. Comment names 5 January 2027 as the day to drop `window`.

### Listing A.1 — `appendices/a-api-reference/webmcp.idl`

Before: `getTools()` / `executeTool()` used `RegisteredTool`. The block was `dictionary RegisteredTool` with `required Window window` and `ToolAnnotations annotations`.

After: both methods use `Tool`. The block is `interface Tool` with readonly attributes, `object? inputSchema`, `object? outputSchema`, `WindowProxy? source`, `object? annotations`. The rest of the IDL index is unchanged.

### Listing E.1 — new, `appendices/e-tool-interface/read-tool.js`

New file for the demos repo. `readTools()` maps each tool to a plain object. `source` is `tool.source ?? tool.window`. Schemas and annotations use `?? null`. No `TODO` token.

### Listing F.1 — do not sync as runnable demo code

Excerpt of the unmerged `Tool` in pull request #375 (`name`, `source`, `origin`, `execute()`). It is not the specification and not a file in the demos repository.

### Figure 5.2

`figures/src/figure-5-2.svg`: the third column label `RegisteredTool` is `Tool`, and `window, origin` is `source, origin`. PNG re-rendered. Not a code listing.

## Per-file coverage

| File | What changed |
| --- | --- |
| Chapter 1 | The early-November flux note now points at Appendix E and Appendix F as well as Appendix D. |
| Chapter 4 | The #348 callout says merged, `Tool`, `source`, Chrome 160.0.8173.0. Footnote updated. |
| Chapter 5 | Registration checks stay on the 27 October draft and Chromium 156. A new sentence separates the later `Tool` change. `window` in the duplicate-name note is `source`. `outputSchema` is on `Tool` and `null` when absent. #348 no longer “would” change `registerTool()`’s return value. Figure 5.2 caption names `Tool`. |
| Chapter 7 | IDL listing, `getTools()` / `executeTool()` prose, content-script listing, summary, and the open-items list. #348 removed from the open list. #375 pointed at Appendix F. 2 November test claim qualified. |
| Chapter 8 | “Current draft” date is 23 November 2026. Methods unchanged. `getTools()` returns `Tool`. |
| Chapter 9 | The harness note says #348 has merged and a fresh `getTools()` object is required. |
| Chapter 11 | `outputSchema` sentence names `Tool` and `null`. |
| Chapter 14 | The Chrome 158 prediction for `Tool` is corrected to 160.0.8173.0. The 16 October DOMException change is left as an unobserved Chromium landing. |
| Chapter 15 | Table 15.1 gains the 19 November row. #348 leaves the open list. #375 is named as an explainer. The 15 October / Chrome 158 reading is corrected. |
| Chapter 17 | Table row splits #375 (open) from #348 (merged). The narrative does the same. The adapter sentence points at Appendix E. |
| Appendix A | IDL, Table A.4, `executeTool()` paragraph, Section A.9, summary, footnotes. |
| Appendix B | `Tool` entry added. `RegisteredTool` marked removed. `getTools()` and `outputSchema` updated. |
| Appendix C | Demo table rows for Appendix E and for Appendix F (no demo). |
| Appendix D | The “next migration” box points at Appendix E and leaves #375 out of it. |
| Appendix E | New. Compatibility table, Listing E.1, checklist. |
| Appendix F | New. #375 only, status open on 23 November 2026. |
| `Book.txt` | Appendices E and F before About the Author. |

## Flagged

- Chrome build 160.0.8173.0 is not in a Chromium release note that this pass found. Two statements of it were used: the author’s task summary, and François Beaufort’s pull request #105 on GoogleChromeLabs/webmcp-extension.
- `source === window` for a same-frame content script was not re-tested on Chrome 160. The 23 November getter returns that browsing context’s `WindowProxy`. The Chromium 156 equality result was for `window`, not for `source`.
- `webmcp-types` 0.2.0 is mentioned only inside Beaufort’s pull request. This pass did not read the npm registry, and the book’s earlier “0.1.10” sentences were left as statements about 2 November 2026.
- Pull requests #204 and #355 were confirmed open on 23 November 2026. Their descriptions in Appendix A are still the book’s 2 November summaries, not a re-read of every comment.
