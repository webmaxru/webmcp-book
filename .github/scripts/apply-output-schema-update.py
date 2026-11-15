from pathlib import Path
import re
import sys

ROOT = Path.cwd()
DEMO = Path(sys.argv[1]).resolve()
updates: dict[str, str] = {}

def read(path: str) -> str:
    return updates.get(path, (ROOT / path).read_text(encoding='utf-8'))

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f'{label}: expected text not found: {old[:140]!r}')

def edit(path: str, old: str, new: str, label: str) -> None:
    updates[path] = replace_once(read(path), old, new, label)

def sync_listing(path: str, number: str, source: str) -> None:
    text = read(path)
    caption = f'**Listing {number}**'
    at = text.find(caption)
    if at < 0:
        raise RuntimeError(f'{path}: listing {number} caption missing')
    opening = text.find('```js\n', at)
    if opening < 0:
        raise RuntimeError(f'{path}: listing {number} JavaScript fence missing')
    body_start = opening + len('```js\n')
    closing = text.find('\n```', body_start)
    if closing < 0:
        raise RuntimeError(f'{path}: listing {number} closing fence missing')
    source_text = (DEMO / source).read_text(encoding='utf-8').rstrip('\n')
    updates[path] = text[:body_start] + source_text + text[closing:]

# Chapter 5: add the new optional member and the harness-side validation boundary.
p = 'manuscript/05-registering-tools.md'
edit(p,
"""      required: ['date', 'partySize']
    },
    annotations: { readOnlyHint: true },                            // → Chapter 6""",
"""      required: ['date', 'partySize']
    },
    outputSchema: {
      type: 'object',
      properties: {
        date: { type: 'string' },
        partySize: { type: 'integer' },
        slots: { type: 'array', items: { type: 'string' } }
      },
      required: ['date', 'partySize', 'slots']
    },
    annotations: { readOnlyHint: true },                            // → Chapter 6""", 'Chapter 5 Listing 5.1')
edit(p,
"""  object inputSchema;
  required ToolExecuteCallback execute;""",
"""  object inputSchema;
  object outputSchema;
  required ToolExecuteCallback execute;""", 'Chapter 5 IDL')
edit(p,
"""| `inputSchema` | `object` | No | Serializes it to a JSON string at registration time |
| `execute` | `ToolExecuteCallback` | Yes | Calls it with a parsed input object and `{ signal }` |""",
"""| `inputSchema` | `object` | No | Serializes it to a JSON string at registration time |
| `outputSchema` | `object` | No | Serializes it to a JSON string at registration; describes the expected result |
| `execute` | `ToolExecuteCallback` | Yes | Calls it with a parsed input object and `{ signal }` |""", 'Chapter 5 Table 5.2')
edit(p,
"""If you write `inputschema` (lower-case “s”) or add an `outputSchema` because a blog post mentioned one, the browser drops it. Your tool registers without a schema, and nothing tells you.""",
"""If you write `inputschema` (lower-case “s”), the browser ignores that unknown member without complaint. `outputSchema` is now a defined, optional member alongside `inputSchema`; both schemas are serialized at registration and exposed to agents.""", 'Chapter 5 unknown dictionary member')
edit(p,
"""    required: ['date', 'time', 'partySize']
  },
  annotations: { consequentialHint: true },          // a real-world action: Chapter 6""",
"""    required: ['date', 'time', 'partySize']
  },
  outputSchema: {
    type: 'object',
    properties: {
      status: { type: 'string', enum: ['error', 'refused', 'booked', 'cancelled_by_user'] },
      code: { type: 'string' },
      message: { type: 'string' },
      reference: { type: 'string' },
      date: { type: 'string' },
      time: { type: 'string' },
      partySize: { type: 'integer' }
    },
    required: ['status'],
    oneOf: [
      { properties: { status: { const: 'error' } }, required: ['code', 'message'] },
      { properties: { status: { const: 'refused' } }, required: ['code', 'message'] },
      { properties: { status: { const: 'booked' } }, required: ['reference', 'date', 'time', 'partySize'] },
      { properties: { status: { const: 'cancelled_by_user' } }, required: ['message'] }
    ]
  },
  annotations: { consequentialHint: true },          // a real-world action: Chapter 6""", 'Chapter 5 Listing 5.4')
old_output = """> *Output schemas.* MCP tools can declare an `outputSchema` and return `structuredContent`.[^ch05-15] WebMCP has neither. Issue #9 has asked for one since August 2025, and pull request #254 (opened on 21 August 2026, still open on 2 November) would add `outputSchema` to both `ModelContextTool` and `RegisteredTool`.[^ch05-37] Until it lands, a dictionary member named `outputSchema` is silently ignored (see ②), and Chromium 156 behaves exactly that way: a tool registered with an `outputSchema` registers without complaint, and the `RegisteredTool` an in-page agent gets back has no trace of it.[^ch05-3] A developer’s September 2026 issue described having to invent a size budget and a `RESULT_TOO_LARGE` error for 18 tools, because results are untyped.[^ch05-38]"""
new_output = """> *Output schemas.* Pull request #254 merged on 2 November 2026. It adds the optional `outputSchema` member to `ModelContextTool` and `RegisteredTool`; `getTools()` exposes the declared JSON Schema to in-page agents.[^ch05-output-schema] The task’s supplied Chrome build, `159.0.8140.0`, supports the member. This book’s browser observations and demo tests use Chromium 156, where the probe still found that `getTools()` drops it.[^ch05-3]
>
> The spec says a result is expected to match its `outputSchema`, but it does not yet require native `executeTool()` to reject a mismatch. Issue #92 remains open. For now, an agent harness should validate each parsed result before returning it to a model, and pass a clear validation error instead of a malformed result. Keep raw invalid data out of the transcript and error text. A tool without an `outputSchema` remains valid; text-returning tools can leave it out.[^ch05-output-validation][^ch05-output-extension]"""
edit(p, old_output, new_output, 'Chapter 5 output schema callout')
edit(p,
"""### What happens to your return value

When your promise fulfils with a value `v`, the browser serializes `v` with the Infra standard’s *serialize a JavaScript value to a JSON string* operation, which is a call to `JSON.stringify()` that throws if the result is `undefined`.[^ch05-25][^ch05-24] That string is the result. An in-page agent receives it as the resolved value of `executeTool()`, which is why the IDL declares `Promise<DOMString>`.[^ch05-31] A browser agent receives it through whatever channel the browser uses. The spec deliberately doesn’t prescribe the format its model sees: browsers may expose tools “via Model Context Protocol, other proprietary ‘function calling’ methods, or any other way.”[^ch05-33]

Because the serializer is `JSON.stringify()`, its edge cases are WebMCP’s edge cases.""",
"""### What happens to your return value

When your promise fulfils with a value `v`, the browser serializes `v` with the Infra standard’s *serialize a JavaScript value to a JSON string* operation, which is a call to `JSON.stringify()` that throws if the result is `undefined`.[^ch05-25][^ch05-24] That string is the result. An in-page agent receives it as the resolved value of `executeTool()`, which is why the IDL declares `Promise<DOMString>`.[^ch05-31] A browser agent receives it through whatever channel the browser uses. The spec deliberately doesn’t prescribe the format its model sees: browsers may expose tools “via Model Context Protocol, other proprietary ‘function calling’ methods, or any other way.”[^ch05-33]

`outputSchema` describes the expected result; it does not by itself guarantee runtime validation. Until issue #92 settles who owns output validation and how a mismatch should be reported, the harness must do the check before the result reaches the model. If validation fails, give the model a useful error without echoing the untrusted payload. When there is no schema, preserve the tool’s ordinary result, including plain text.[^ch05-output-validation][^ch05-output-extension]

Because the serializer is `JSON.stringify()`, its edge cases are WebMCP’s edge cases.""", 'Chapter 5 return validation guidance')
edit(p,
"""*Output schemas.* MCP tools can declare an `outputSchema` and return `structuredContent`.[^ch05-15] WebMCP has neither.""",
"""*Output schemas.* MCP tools can declare an `outputSchema` and return `structuredContent`.[^ch05-15] WebMCP now has the optional `outputSchema` member added by PR #254.""", 'Chapter 5 output subsection old start')
edit(p,
"""- The schema is stringified at registration and isn’t validated, and neither are calls against it. Whether schemas should become required and browser-validated is an active debate. Validate strictly in code, keep schemas simple and descriptive, and ask only for what the tool needs.""",
"""- `inputSchema` and optional `outputSchema` are serialized at registration and exposed to agents. Native output-validation behavior remains unresolved in issue #92, so harnesses should validate results before sending them to a model and return a clear error instead of malformed data.""", 'Chapter 5 summary')
updates[p] = read(p).rstrip() + """

[^ch05-output-schema]: webmachinelearning/webmcp pull request #254, “Add `outputSchema` to `ModelContextTool` and `RegisteredTool”, merged 2 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch05-output-validation]: webmachinelearning/webmcp issue #92, “Who owns the validation layer?”, open on 15 November 2026; the November comments continue to discuss output mismatch handling and do not establish native `executeTool()` rejection behavior. <https://github.com/webmachinelearning/webmcp/issues/92>
[^ch05-output-extension]: GoogleChromeLabs/webmcp-extension pull request #98, “Add support for tool outputSchema”, open on 15 November 2026; the example validates results in the agent host before model delivery. <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
"""

# Chapter 9: copy the executable listings exactly from the companion repository.
p = 'manuscript/09-first-webmcp-app.md'
sync_listing(p, '9.3', 'chapters/09-first-webmcp-app/webmcp/tools.js')
sync_listing(p, '9.5', 'chapters/09-first-webmcp-app/test-agent.js')
edit(p,
"""The raw result goes into a transcript next to the parsed one. Chromium returns plain strings as they are, rather than JSON-quoting them, so the harness falls back to the raw string when parsing fails.""",
"""The harness parses the result and, when the tool declares `outputSchema`, validates it before the result enters the transcript or the next planner prompt. On a mismatch it stores only a concise validation error, not the malformed payload, so the planner can recover without seeing unvalidated data. Tools with no output schema remain valid, including tools that return plain text. Chromium 156 still returns plain strings as-is; the demo records that observed behavior separately from the newer schema contract.[^ch09-output-schema]""", 'Chapter 9 Test Agent explanation')
updates[p] = read(p).rstrip() + """

[^ch09-output-schema]: WebMCP PR #254 added optional output schemas on 2 November 2026; issue #92 remains open on validation behavior. The companion Test Agent validates before planner input. See also GoogleChromeLabs/webmcp-extension PR #98 for a host-side implementation example. <https://github.com/webmachinelearning/webmcp/pull/254> <https://github.com/webmachinelearning/webmcp/issues/92> <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
"""

# Chapter 11: make the output contract and validation boundary explicit.
p = 'manuscript/11-designing-tools.md'
edit(p,
"""## Returning useful results and errors

### Results: high signal, the right identifiers, and an honest count""",
"""## Returning useful results and errors

### Declare the result shape, then validate it in the harness

`outputSchema` is an optional JSON Schema for a tool’s return value. PR #254 added it to `ModelContextTool` and `RegisteredTool`, so an in-page agent can read it through `getTools()`.[^ch11-output-schema] The schema describes the result the tool promises; the current spec does not require native `executeTool()` to reject a mismatch. Issue #92 remains open on validation ownership and error semantics.[^ch11-output-validation]

Validate every result against its declared schema before the result enters the model’s next prompt. If it fails, give the model a concise error with a schema path or safe reason, and omit the malformed result from both transcript and error text. A result can contain untrusted page content, so quoting the bad value inside the error would send it to the model by another route. If a tool has no `outputSchema`, preserve the optional case rather than inventing an object wrapper for plain text. The Test Agent in Chapter 9 demonstrates this boundary; WebMCP Extension PR #98 is another host-side example.[^ch11-output-extension]

### Results: high signal, the right identifiers, and an honest count""", 'Chapter 11 output schema section')
updates[p] = read(p).rstrip() + """

[^ch11-output-schema]: webmachinelearning/webmcp pull request #254, merged 2 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch11-output-validation]: webmachinelearning/webmcp issue #92, open on 15 November 2026; the November discussion has not changed the spec’s execution algorithm. <https://github.com/webmachinelearning/webmcp/issues/92>
[^ch11-output-extension]: GoogleChromeLabs/webmcp-extension pull request #98, host-side validation before model delivery, open on 15 November 2026. <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
"""

# Chapter 14: distinguish the newly specified result shape from native enforcement.
p = 'manuscript/14-testing-debugging-evals.md'
edit(p,
"""Nothing is merged yet. Until something is, a missing `query`, a price sent as the string `'3000'` or a category the store doesn’t have will all reach your code.""",
"""PR #254 has since added optional `outputSchema` to the tool dictionaries, but issue #92 remains open on who validates schemas and what errors native calls should expose. The current spec does not say that `executeTool()` must reject an output mismatch. A missing `query`, a price sent as the string `'3000'` or a category the store doesn’t have still reaches your code in the Chromium 156 build tested here.""", 'Chapter 14 issue 92 status')
edit(p,
"""According to the documentation, the output pane shows error messages when parameters or return values don’t match the defined schema, and the invocation counter tells you whether an agent ever chose your tool for a given prompt.""",
"""The documentation says the output pane can show parameter or return-value schema mismatches. Treat that as a DevTools debugging aid, not proof that native `executeTool()` rejects a bad result: output validation remains unresolved in issue #92. A harness should validate before the result reaches its model and should send an error instead of the malformed value.""", 'Chapter 14 DevTools output note')
edit(p,
"""## Layer 4: evaluations against real models""",
"""### Output-schema contract tests

A schema contract test should exercise both sides of the model boundary. A matching result reaches the planner. A wrong type or missing required property becomes a clear validation error. A tool without `outputSchema` remains callable. Most importantly, the planner’s transcript contains no raw invalid result, including when validation fails. The Chapter 9 Test Agent uses `@cfworker/json-schema` for this check; WebMCP Extension PR #98 shows the same host-side placement. Chromium 156 tests only the API behavior available in that build; they do not verify Chrome 159.0.8140.0.[^ch14-output-schema]

## Layer 4: evaluations against real models""", 'Chapter 14 before layer 4')
updates[p] = read(p).rstrip() + """

[^ch14-output-schema]: WebMCP PR #254 merged 2 November 2026; issue #92 remains open on validation; GoogleChromeLabs/webmcp-extension PR #98 shows host-side result checks. The task-supplied Chrome build is 159.0.8140.0; the book’s Playwright suites use Chromium 156 and were not run on 159. <https://github.com/webmachinelearning/webmcp/pull/254> <https://github.com/webmachinelearning/webmcp/issues/92> <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
"""

# Chapter 15: update only the schema-related standard status; retain dated browser observations.
p = 'manuscript/15-browser-support-and-standards.md'
edit(p,
"""| 8 Oct 2026 | `UnknownError` replaced with specific `DOMException` types | #339 |""",
"""| 8 Oct 2026 | `UnknownError` replaced with specific `DOMException` types | #339 |
| 2 Nov 2026 | Optional `outputSchema` added to `ModelContextTool` and `RegisteredTool` | #254 |""", 'Chapter 15 change table')
edit(p,
"""It won’t stand still forever — four open pull requests would change it if they were merged: a `Tool` interface that replaces the `RegisteredTool` dictionary (#348), an `outputSchema` member for tools (#254), `requestUserInput()` with interactive, form and URL modes (#204), and an `openWorldHint` annotation (#355).[^ch15-17] None of them is merged as of 2 November 2026, so none of them is in this book’s code. Please note that implementation sometimes runs ahead of the text: Chromium’s main branch already replaced the `RegisteredTool` dictionary with a `Tool` interface object on 15 October, the change #348 asks the spec to make.[^ch15-35] Treat them as the weather forecast, not as the weather.""",
"""It won’t stand still forever. PR #254, which adds optional `outputSchema` to `ModelContextTool` and `RegisteredTool`, merged on 2 November 2026. Three other API proposals remain open: a `Tool` interface replacing the `RegisteredTool` dictionary (#348), `requestUserInput()` with interactive, form and URL modes (#204), and an `openWorldHint` annotation (#355).[^ch15-17][^ch15-output-schema] The task-supplied Chrome build `159.0.8140.0` supports `outputSchema`; this book’s Playwright tests still run Chromium 156 and do not verify that newer build. The current spec exposes the schema but leaves native mismatch rejection unresolved in issue #92. Harnesses should validate before passing results to a model.[^ch15-output-validation] Please note that implementation sometimes runs ahead of the text: Chromium’s main branch already replaced the `RegisteredTool` dictionary with a `Tool` interface object on 15 October, the change #348 asks the spec to make.[^ch15-35]""", 'Chapter 15 open PR list')
updates[p] = read(p).rstrip() + """

[^ch15-output-schema]: webmachinelearning/webmcp pull request #254, merged 2 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch15-output-validation]: webmachinelearning/webmcp issue #92, open on 15 November 2026. The current discussion includes proposals for host-side error behavior but no normative change requiring `executeTool()` to reject output mismatches. <https://github.com/webmachinelearning/webmcp/issues/92>
"""

# Chapter 17: update the feature status, while keeping the Chromium 156 observations intact.
p = 'manuscript/17-the-road-ahead.md'
edit(p,
"""| Output schemas | Issues #9, #92, PR #254 | Resolved in principle (Feb 2026), PR open, required-or-optional still argued | Write `outputSchema` in your catalog today |""",
"""| Output schemas | Issues #9 and #92; PR #254 | PR #254 merged 2 Nov; `outputSchema` is optional; native validation behavior remains unresolved | Declare a useful schema and validate results in the agent harness |""", 'Chapter 17 Table 17.1')
edit(p,
"""The request for an output schema is one of the oldest in the repository. Issue #9 was opened in August 2025, right after MCP added `outputSchema` to its tool definition. On 5 February 2026 the Community Group resolved to “add outputSchema to the imperative API and investigate how to associate outputSchema with declarative WebMCP.”[^ch17-8] Pull request #254, opened on 21 August 2026, adds an optional `outputSchema` member to both `ModelContextTool` and `RegisteredTool`. The page declares it, and an in-page agent can read it back from `getTools()`. The PR explains that the name was chosen over `responseConstraint`, which is specific to the Prompt API, to align with MCP. On 11 September its author wrote that he had “started experimenting with `outputSchema` in Chromium” in a code review. The PR was still open on 2 November.[^ch17-9]""",
"""The request for an output schema is one of the oldest in the repository. Issue #9 was opened in August 2025, right after MCP added `outputSchema` to its tool definition. On 5 February 2026 the Community Group resolved to “add outputSchema to the imperative API and investigate how to associate outputSchema with declarative WebMCP.”[^ch17-8] Pull request #254 added the optional `outputSchema` member to both `ModelContextTool` and `RegisteredTool` and merged on 2 November 2026. The page declares a JSON Schema for the result, and an in-page agent can read it back from `getTools()`. The name was chosen over `responseConstraint`, which is specific to the Prompt API, to align with MCP.[^ch17-9] The task-supplied Chrome build `159.0.8140.0` supports the member; the companion repo’s browser tests still use Chromium 156 and do not verify Chrome 159.""", 'Chapter 17 PR status')
edit(p,
"""The argument has since moved to a sharper question: should the schemas be required? In issue #92, François Beaufort argued in mid-October for keeping both `inputSchema` and `outputSchema` “optional, with defaults the spec would define”, because a developer forced to write a schema can always write `{}`. Samuel Dallstream from Microsoft argued the opposite, that the cost of required schemas “is relatively small”. On 30 October Johann Hofmann added “full support from security for requiring and validating these schemas in the spec”.[^ch17-12] On the PR itself, an agent-host developer asked that the spec say plainly that leaving out `outputSchema` is the normal case for tools that return text.[^ch17-9]""",
"""Issue #92 remains open on whether schemas should be required and who validates them. Its latest discussion still contains competing views: some participants favor optional schemas because tools may return plain text, while others want explicit contracts as a security signal. November comments distinguish invalid tool output from invalid model input and argue that an agent should not pass mismatched output to a model. Those comments are proposals, not normative spec text.[^ch17-12]""", 'Chapter 17 issue 92 debate')
edit(p,
"""> **Still in flux:** output schemas
>
> PR #254 was still open on 2 November 2026, and the draft has no `outputSchema`. Whether schemas become required, and whether the browser validates inputs and results against them, is being argued in issue #92.[^ch17-12] If the PR lands as written, the schema you write today becomes visible to in-page agents through `getTools()`. If the name or shape changes, it’s one field in your catalog.""",
"""> **Still in flux:** output validation
>
> PR #254 merged on 2 November 2026 and `outputSchema` is now part of the spec. The member is optional. The spec says a result is expected to conform, but does not yet say that native `executeTool()` must reject an output mismatch. Issue #92 remains open. Until it is resolved, validate results in the agent harness before model delivery, and return a safe validation error instead of malformed data. Keep the invalid payload out of the error itself.[^ch17-12][^ch17-output-schema]""", 'Chapter 17 output schema callout')
edit(p,
"""  - Output schemas are resolved in principle and in an open PR (#254), and whether schemas should be required is argued in #92. Chromium 156 accepts and ignores `outputSchema`, so write it now and test results against it.""",
"""  - PR #254 added optional `outputSchema` to the spec on 2 November. Issue #92 remains open on validation behavior. Chromium 156 still drops the member from `getTools()`; agent harnesses should validate declared results before returning them to a model.""", 'Chapter 17 summary output schema')
edit(p,
"""**Listing 17.1** `chapters/17-the-road-ahead/src/catalog.js` — `search_products` as plain data, with an output schema the draft doesn’t have yet""",
"""**Listing 17.1** `chapters/17-the-road-ahead/src/catalog.js` — `search_products` as plain data with an optional output schema""", 'Chapter 17 Listing 17.1 caption')
edit(p,
"""  2. **Put the API shape in one file.** Only the adapter calls `document.modelContext` (Listing 17.2). When `outputSchema`, continuations or a new exposure keyword arrive, or the API moves again (Appendix D covers the last move), one file changes.""",
"""  2. **Put the API shape in one file.** Only the adapter calls `document.modelContext` (Listing 17.2). When continuation support or a new exposure keyword arrives, or the API moves again (Appendix D covers the last move), one file changes. The adapter already passes `outputSchema` through.""", 'Chapter 17 checklist adapter')
# replace stale footnote dates/source summary for output schema, preserving existing note ids
edit(p,
"""[^ch17-9]: webmachinelearning/webmcp pull request #254, “Add `outputSchema` to `ModelContextTool` and `RegisteredTool`” (opened 21 August 2026, open on 2 November 2026), including the author’s comment of 11 September 2026 and comments of 20 and 26 October 2026. <https://github.com/webmachinelearning/webmcp/pull/254>""",
"""[^ch17-9]: webmachinelearning/webmcp pull request #254, “Add `outputSchema` to `ModelContextTool` and `RegisteredTool” (merged 2 November 2026). <https://github.com/webmachinelearning/webmcp/pull/254>""", 'Chapter 17 PR 254 citation')
edit(p,
"""[^ch17-12]: webmachinelearning/webmcp issue #92, “Who owns the validation layer?” (opened 17 February 2026, open on 2 November 2026), including comments by François Beaufort (14 October 2026), Samuel Dallstream (16 October 2026) and Johann Hofmann (30 October 2026). <https://github.com/webmachinelearning/webmcp/issues/92>""",
"""[^ch17-12]: webmachinelearning/webmcp issue #92, “Who owns the validation layer?” (open on 15 November 2026), including the March resolution and comments through 9 November 2026 on input/output validation, error provenance and not passing malformed results to a model. <https://github.com/webmachinelearning/webmcp/issues/92>""", 'Chapter 17 issue 92 citation')
updates[p] = read(p).rstrip() + """

[^ch17-output-schema]: GoogleChromeLabs/webmcp-extension pull request #98, “Add support for tool outputSchema” (open on 15 November 2026), describes validating results in the host before model delivery. <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
"""
sync_listing(p, '17.1', 'chapters/17-the-road-ahead/src/catalog.js')
sync_listing(p, '17.2', 'chapters/17-the-road-ahead/src/adapter.js')
sync_listing(p, '17.3', 'chapters/17-the-road-ahead/src/probe.js')

# Appendix A: mirror the current IDL and remove PR #254 from the open-proposals list.
p = 'manuscript/appendix-a-api-reference.md'
idl = read(p)
idl = replace_once(idl, '    object inputSchema;\n    required ToolExecuteCallback execute;', '    object inputSchema;\n    object outputSchema;\n    required ToolExecuteCallback execute;', 'Appendix A ModelContextTool IDL')
idl = replace_once(idl, '    object inputSchema;\n    required Window window;', '    object inputSchema;\n    object outputSchema;\n    required Window window;', 'Appendix A RegisteredTool IDL')
updates[p] = idl
edit(p,
"""| `inputSchema` | `object` | no | Serialized with `JSON.stringify` at registration. A `toJSON()` that returns `undefined` rejects with a `TypeError`, and an error `JSON.stringify` throws (a circular object, for example) is rethrown. Serializing can run script, so the name and fully-active checks run again afterwards. (Tested: when `toJSON()` registers another tool with the same name, Chromium 156 kills the page’s renderer, see Table A.7.) |
| `execute` | `ToolExecuteCallback` | yes | `(inputObject, { signal }) => any`, may return a promise. |""",
"""| `inputSchema` | `object` | no | Serialized with `JSON.stringify` at registration. A `toJSON()` that returns `undefined` rejects with a `TypeError`, and an error `JSON.stringify` throws (a circular object, for example) is rethrown. Serializing can run script, so the name and fully-active checks run again afterwards. (Tested: when `toJSON()` registers another tool with the same name, Chromium 156 kills the page’s renderer, see Table A.7.) |
| `outputSchema` | `object` | no | Optional JSON Schema describing expected tool output. Serialized at registration and exposed by `getTools()`; this does not settle whether native `executeTool()` rejects a mismatch. |
| `execute` | `ToolExecuteCallback` | yes | `(inputObject, { signal }) => any`, may return a promise. |""", 'Appendix A Table A.1')
edit(p,
"""| `inputSchema` | `object` | Parsed back from the stored JSON string. Absent when none was given. |
| `window` | `Window` | The window of the document that registered the tool. |""",
"""| `inputSchema` | `object` | Parsed back from the stored JSON string. Absent when none was given. |
| `outputSchema` | `object` | Parsed back from the stored JSON string. Optional and absent when none was given. |
| `window` | `Window` | The window of the document that registered the tool. |""", 'Appendix A Table A.4')
edit(p,
"""Nothing below is in the specification. These are open pull requests that touch the IDL or the tables above, as of 2 November 2026.""",
"""Nothing below is in the specification. These are open pull requests that touch the IDL or the tables above, as of 15 November 2026. PR #254, which added `outputSchema`, merged on 2 November 2026 and is now reflected in Tables A.1 and A.4.""", 'Appendix A open proposals intro')
edit(p,
"""| #254, “Add `outputSchema` to `ModelContextTool` and `RegisteredTool`” | François Beaufort, 26 October 2026 | A JSON Schema for the tool’s result, next to `inputSchema`. | Additive. Nothing breaks, and you could describe results you already return. |
""", "", 'Appendix A remove merged PR row')
edit(p,
"""Four open pull requests (`Tool` interface, `outputSchema`, `requestUserInput`, `openWorldHint`) would change this page if they merge.""",
"""Three open pull requests (`Tool` interface, `requestUserInput` and `openWorldHint`) could change this page. `outputSchema` is in the current draft.""", 'Appendix A summary proposal count')
edit(p,
"""## A.4 `executeTool(tool, inputObject, options)`""",
"""### Output schemas and validation

`outputSchema` is an optional JSON Schema for the result. The specification expects a conforming value, but does not currently require native `executeTool()` to reject a mismatch. Issue #92 remains open. An agent harness should validate before passing results to a model; on mismatch, return a clear error and do not include the malformed payload. Tools without an output schema remain valid and may return unstructured text.[^appa-output-schema]

## A.4 `executeTool(tool, inputObject, options)`""", 'Appendix A output schema note')
updates[p] = read(p).rstrip() + """

[^appa-output-schema]: webmachinelearning/webmcp pull request #254, merged 2 November 2026, and issue #92, open on 15 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254> <https://github.com/webmachinelearning/webmcp/issues/92>
"""

# Validation log and changelog: preserve the 2 Nov browser evidence and document this follow-up.
p = 'VALIDATION.md'
edit(p,
"""The API the book teaches has not changed. The IDL in the 27 October draft has the same shape as the 15 October draft the first edition was written against: `document.modelContext` with `registerTool()`, `getTools()` and `executeTool()`, the three events, and `ToolAnnotations` with `readOnlyHint`, `untrustedContentHint`, `consequentialHint` and `debugging`. No listing needed an API change.""",
"""The API surface changed after the 2 November edition check: PR #254 merged that day and added optional `outputSchema` to `ModelContextTool` and `RegisteredTool`. This follow-up updates the IDL, chapter explanations and paired listings. The original Chromium 156 observations remain dated to their actual test runs; no test in this repository was run on Chrome 159.0.8140.0. Issue #92 remains open on output-validation ownership and native mismatch behavior.""", 'Validation summary')
edit(p,
"""| 28 | outputSchema: issue #9, PR #254 open | OK | PR #254 still open (updated 26 Oct); silently ignored in Chromium (probe) | https://github.com/webmachinelearning/webmcp/pull/254 |""",
"""| 28 | outputSchema: issue #9, PR #254 | CHANGED | PR #254 merged 2 Nov, adding the optional member; Chromium 156 probe still observes it dropped by `getTools()`; issue #92 remains open on validation | https://github.com/webmachinelearning/webmcp/pull/254 |""", 'Validation Chapter 5 row 28')
updates[p] = read(p).rstrip() + """

## OutputSchema follow-up (15 November 2026)

- Sources re-read this pass: WebMCP PR #254 (merged 2 November 2026), issue #92 (still open, with comments through 9 November), the current spec IDL, and GoogleChromeLabs/webmcp-extension PR #98 (still open).
- PR #254 adds optional `outputSchema` to `ModelContextTool` and `RegisteredTool`. The current spec expects outputs to conform, but does not require native `executeTool()` to reject mismatches. Issue #92 has not settled that behavior.
- The user supplied Chrome build `159.0.8140.0` as supporting the member. This task did not run that build. Existing observations and Playwright runs use Chromium 156.0.8078.4 and remain labelled as such.
- The companion changes validate parsed tool results in the Test Agent before transcript/model use; mismatches become safe validation errors without raw payloads. Tests cover valid and invalid results, absent schemas, and planner visibility. Exact commands and Actions results are recorded in the demo PR after the workflow finishes.
- Companion repository: <https://github.com/webmaxru/webmcp-book-demos>. Reference implementation: <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>.
"""

p = 'CHANGELOG.md'
text = read(p)
text = replace_once(text,
"""## [2.1.0] - 2026-11-04""",
"""## [Unreleased]

### Changed

- Update Chapters 5, 9, 11, 14, 15 and 17 and Appendix A for WebMCP `outputSchema` (PR #254, merged 2 November 2026). Clarify that the member is optional, the native mismatch behavior remains unresolved in issue #92, and agent harnesses should validate before model delivery. Synchronize Chapter 9 and Chapter 17 listings with the companion demo repository.
- Preserve Chromium 156 test observations and state that the supplied Chrome build 159.0.8140.0 was not tested by this repository.

## [2.1.0] - 2026-11-04""", 'Changelog follow-up')
updates[p] = text

# Apply only after every expected anchor has been checked successfully.
for path, content in updates.items():
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8', newline='\n')
print('Updated manuscript files:', ', '.join(sorted(updates)))
