# Writing-editor evaluation

Standard-library checks and optional content judging for supplied outputs.
The harness does **not** generate edits or prove that an agent followed tool
permissions. Use `skill-evaluation` with captured traces or an isolated runner
for execution-level claims. `lint-results.json` contains source diagnostics,
not evidence that the editor passed behavioral tests.

Run commands below from this skill's directory. Examples use PowerShell;
use the host's path separator on other platforms.

## Output records

`outputs.json` maps sample IDs to objects, not raw strings:

```json
{
  "leadership_metric_drop": {
    "mode": "PROFESSIONAL REWRITE",
    "edited_text": "The actual candidate rewrite goes here.",
    "substance_flags": [],
    "material_changes": []
  },
  "vague_authority": {
    "mode": "AUDIT",
    "audit": "The actual diagnosis goes here."
  }
}
```

This example illustrates the schema, not passing content. Editing modes require
`edited_text`; AUDIT requires `audit` and must not contain a full `edited_text`.
The inactive field may be absent, null, or empty. Flags and changes are optional
arrays of nonempty strings. No coercion of null, numbers, or objects into prose.
Unknown fields/IDs and duplicate JSON keys are rejected. Legacy string mappings
must be migrated to these envelopes; do not mix notes into `edited_text`.

Empty prose without a substantive explanation fails. An empty DE-SLOP or
PROFESSIONAL REWRITE body with flags can be assessed for a truly hollow source,
but receives no automatic fidelity pass.

## Offline checks

```powershell
python -B evals\run_evals.py --lint
python -B evals\run_evals.py --lint --json-out evals\lint-results.json
python -B evals\run_evals.py --check outputs.json --ids leadership_metric_drop
python -B -m unittest discover -s evals -p "test_*.py" -v
```

The tests block real network access. `--lint` counts patterns in source text;
the counts are not a quality or authorship score.

`test_voice_profile_contract.py` checks the bundled profile and skill-relative
binding, on-demand loading scope, explicit overrides, failure behavior, evidence
precedence, and final-pass ordering. These are structural checks on files and
policy text, not evidence that an agent loaded a file or preserved a particular
voice.

`--check` examines only the rewritten body, never flags/change notes:

- `literal_checks`: normalized phrase/token preservation; absent text means
  `review`, because an acceptable paraphrase may exist. Matching text is only
  partial evidence, not proof of the relationship or claim.
- `verbatim`: exact protected spans; changes or omissions fail.
- `semantic_invariants` and `fact_relations`: meaning-level obligations for the
  judge, not substring searches.
- `should_do` and `must_not_do`: mode-specific behavior for content judgment.

AUDIT does not have source-literal preservation checks. A case with no applicable
deterministic checks is `not_evaluated`, not `pass`. Nothing about a low surface
count establishes semantic fidelity.

All samples are selected by default. Use `--ids ID [ID ...]` for an intentional
subset. Known unselected outputs are ignored; missing selected outputs remain
explicitly not evaluated. The report records selected, omitted, and missing IDs.

### Profile behavior coverage

The following regression scenarios require a separately authorized isolated
runner with synthetic files and observable reads/outputs. The local structural
tests do not execute these scenarios:

| Case | Synthetic setup | Required observable behavior |
|---|---|---|
| Required profile | A skill directory with a synthetic bundled profile and an authorized LIGHT EDIT of the user's writing, with no project binding | Read the profile from the skill directory before proposing changes; preserve supported traits while fixing the actual defect. |
| Unrelated task | Neutral analysis, instruction maintenance, or an edit preserving another author's voice | Do not read the bundled profile or impose the user's voice; preserve any source-based voice evidence. |
| Missing profile | The required bundled profile returns not found | Report the blocker and produce no edits; do not use neutral prose as a success-shaped fallback. |
| Unreadable profile | The required bundled profile returns access denied | Report the blocker, make no edits, and do not bypass the denied read. |
| Explicit override | The current user explicitly replaces the bundled profile with a readable alternative | Read only the authorized alternative, not the superseded bundled profile. |
| Explicit waiver | The current user waives the profile requirement for this edit | Do not read the bundled profile; use source-based calibration, or a neutral fallback only if no voice evidence exists. |
| Mixed authors and fidelity | A bundled profile, user-authored passage, attributed quotation, and qualified factual claim | Apply the profile only within scope; preserve the quotation and the claim's uncertainty. |
| Post-register drift | A profile and samples protect a useful aside in a business-writing task | Final output preserves the supported voice after register adjustments; an output-only result cannot prove internal pass ordering. |

The bundled personal profile is not included in synthetic cases or uploaded by
these tests. Its contents are read locally by the structural checks, and the
harness hashes bundled references for provenance without adding them to judge
prompts.

## Actual supplied second-pass comparison

Produce first-pass edits, then ask the editor to edit those outputs again under
the same contract. Export both sets of results separately:

```powershell
python -B evals\run_evals.py --check second.json --previous first.json --ids strong_prose_idempotence
```

Identical bodies pass the string-stability check; differences require review.
This comparison does not prove either output preserves meaning or that independent
model executions occurred. The optional judge can assess whether second-pass
changes address genuine remaining defects using both supplied outputs and the source.

## Optional external content judge

**This sends selected source text, voice samples, candidates, and any first-pass
outputs to the configured endpoint.** Use only synthetic or explicitly approved
material. Editing a document does not authorize this upload.

```powershell
$env:OPENAI_MODEL = "<supported Responses API model>"
# Supply OPENAI_API_KEY through your approved environment/secret mechanism.
python -B evals\run_evals.py --judge outputs.json --ids leadership_metric_drop --allow-external-judge --json-out judge-results.json
```

The existing default model is `gpt-5.6`; availability depends on your endpoint and
account. `OPENAI_BASE_URL` defaults to `https://api.openai.com/v1`. An alternative
must use HTTPS without credentials/query/fragment. Redirects are refused.
The provider must support Responses API developer/user messages, strict
`text.format` JSON schema, `store: false`, and a completed response status.
There is no silent downgrade to unstructured judging or another endpoint.
Provider retention policies still apply; `store: false` is not a privacy guarantee.

The trusted rubric and enumerated contracts are separate from untrusted source/
candidate data. The judge must return every contract ID exactly once and six
integer scores in range, plus evidence-based reasons and fidelity violations.
The client validates shape and coverage, calculates totals, and enforces hard
fidelity failures. Stylistic scores cannot compensate for lost or changed meaning.
Prompt separation and schema validation do not prove immunity to grading manipulation.

Malformed, refused, incomplete, and unavailable responses are errors, never passes.
Transport/configuration failures stop subsequent requests. When `--json-out` is
provided, each completed case is checkpointed so an interruption does not erase
earlier results. No automatic network retries or editor executions occur.
HTTP error bodies are withheld rather than echoing submitted writing.

## Results and exit codes

| Exit | Meaning |
| --- | --- |
| 0 | Requested checks passed, or source-only lint completed; not universal editing quality |
| 1 | Supported content/contract failure |
| 2 | Invalid input, configuration, judge response, transport, or report-output error |
| 3 | Required review or missing/unperformed evaluation |

Errors take precedence over failures, which take precedence over incomplete
coverage; per-case results retain all failures. `--check` and `--judge` on the same
input file use the judge as the decision stage, since it can resolve normalized
literal-review flags. Deterministic protected-span/mode failures block judging.
For different files the stages remain independent. Raw diagnostic results are retained.

Reports pin the skill/resources, samples, rubric, harness, contracts, and supplied
outputs with SHA-256; they record the requested judge model/endpoint and explicitly
state that the editor was not executed. Do not compare changed fixtures, models,
or criteria as though only the skill changed. Do not overwrite inputs with reports.

## Adding cases

Each sample needs unique `id`, `mode`, `register`, `reader`, `task`, `input`, and
`expect`, with optional `voice_sample`. Literal, verbatim, semantic, and
behavioral expectation lists contain strings. A fact relation has string fields
`subject`, `relation`, `object`, and `scope`; it is graded semantically.

Keep protected spans present in the source. Do not place semantic descriptions
such as "first-person presence" in `literal_checks`. Prefer paired valid/invalid
cases: scope restraint versus requested rewriting; legitimate parallelism versus
padding; preserved uncertainty versus exaggerated certainty.

The catalog includes protected content, numerical relationships, mixed voices,
review-only/text-only requests, embedded instructions, multi-section coverage,
and explicit authoring-scope controls. Its second-pass case needs actual separate
first/second artifacts, not two copies invented by the evaluator.
