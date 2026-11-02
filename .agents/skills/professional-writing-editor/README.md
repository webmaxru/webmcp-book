# Professional Writing Editor

A personal skill for editing professional non-fiction and business writing
without flattening the author's voice. It bundles the user's voice profile
and loads it only when the task calls for that voice.

It is designed around five ideas:

1. Structural problems matter more than fashionable banned-word lists.
2. Fidelity is a hard constraint, not a score that style can compensate for.
3. Hollow prose should be flagged, not cosmetically rewritten.
4. Editing should proceed from argument to structure to paragraph to sentence.
5. Business writing needs reader, decision, evidence, and action discipline.

## Package

- `SKILL.md` — main workflow and behavioral contract
- `references/slop-patterns.md` — diagnostic catalog for AI-shaped prose
- `references/voice-calibration.md` — voice fingerprinting and drift protection
- `references\voice-profile.md` — the user's voice evidence, loaded on demand
- `references/business-writing.md` — business/exec/decision-writing module
- `evals/samples.json` — 23 adversarial content cases
- `evals/rubric.md` — scoring rubric with fidelity hard-fails
- `evals/run_evals.py` — standard-library lint/eval harness
- `evals/contracts.py` — strict records, explicit contracts, and local verdict gates
- `evals/test_run_evals.py` — offline regression tests with network access blocked
- `evals/test_voice_profile_contract.py` — structural profile-policy checks, not agent trials

Editing intensity follows the user's request, never suspected AI authorship.
The skill calibrates voice before removing passages, protects verbatim content
and factual relationships, and tracks coverage when editing documents in chunks.
Ordinary editing does not authorize file overwrites, publication, or external judging.

## Installation

For agents that support folder-based skills, copy this directory into the
appropriate skills directory and keep `SKILL.md` at the root of the skill.

For Claude Code, a typical location is:

`.claude/skills/professional-writing-editor/`

Other agents can load `SKILL.md` as the main instruction and resolve the
reference files relative to it. Copy the whole directory, including the
bundled profile; no project-level instruction file or external profile path
is needed.

## Bundled voice profile

`SKILL.md` requires `references\voice-profile.md` when editing or proposing
changes to the user's own writing, or when explicitly asked to adapt prose to
the user's voice. The path is relative to the skill directory, not the project
root, working directory, or document directory.

The profile stays in a separate reference file for on-demand loading. Do not
load it merely because the skill was activated, for neutral analysis, code or
instruction maintenance, or for work that must preserve another author's voice.
In mixed-author documents, apply it only to relevant user-authored passages
or explicitly authorized adaptations.

The editor must read the full current profile before proposing changes in any
mode, including AUDIT examples, select the closest supported register, and apply
its supported traits throughout editing. A missing or unreadable required
profile blocks editing unless the user explicitly waives or replaces the
requirement. Load an explicit replacement instead of the bundled profile, not
both. The final voice comparison runs after the register-specific pass, not
only before it.

The profile governs style, not facts, permissions, protected quotations, or
another author's voice. Explicit current-user instructions and newer matching
samples retain precedence. Outside the binding's scope, or after an explicit
waiver, keep source-based calibration and use a neutral fallback only when no
voice evidence exists.

## Evaluation

Run deterministic diagnostics from this skill's directory (PowerShell examples):

```powershell
python -B evals\run_evals.py --lint
python -B -m unittest discover -s evals -p "test_*.py" -v
```

Export a machine-readable report:

```powershell
python -B evals\run_evals.py --lint --json-out evals\lint-results.json
```

Check candidate rewrites for dropped source details:

```powershell
python -B evals\run_evals.py --check outputs.json --ids leadership_metric_drop
```

An external judge is optional and uploads selected source text, writing samples,
and candidate outputs. Use only synthetic or explicitly approved material:

```powershell
# Supply OPENAI_API_KEY through your approved environment/secret mechanism.
$env:OPENAI_MODEL = "<supported Responses API model>"
python -B evals\run_evals.py --judge outputs.json --ids leadership_metric_drop --allow-external-judge
```

`outputs.json` now maps IDs to mode-aware objects, separating edits from commentary:

```json
{
  "leadership_metric_drop": {
    "mode": "PROFESSIONAL REWRITE",
    "edited_text": "The actual candidate rewrite goes here.",
    "substance_flags": [],
    "material_changes": []
  }
}
```

AUDIT outputs use `audit` instead of `edited_text`. Legacy raw-string mappings
must be migrated; arbitrary values are no longer converted into prose.

The harness separates surface diagnostics from semantic judgment. No applicable
checks means Not evaluated, not Pass. Missing outputs, malformed judge responses,
and fidelity violations cannot produce a successful evaluation exit status.
The model does not control totals or hard-fail gates.

See `evals/README.md` for output schemas, exit codes, explicit case selection,
second-pass comparisons, endpoint requirements, and partial-result recovery.
The harness checks supplied artifacts; it does not generate edits or prove tool
safety. Source lint results are not evidence that behavioral cases passed.

## Design lineage

This package is a synthesis, not a copy, of ideas found in:

- AshwinSathian/humanize-writing-skill
- isatimur/de-slop
- soodoku/on-writing
- anildash/better-documents
- rohitjz/clear-writing-for-pms

The strongest ideas retained are structural diagnosis, fidelity, the removal
test, hollow-vs-rewordable triage, macro-to-micro editing, voice protection,
reader-first sequencing, and explicit evaluation.

House-style rules such as blanket punctuation bans were intentionally not
carried forward.
