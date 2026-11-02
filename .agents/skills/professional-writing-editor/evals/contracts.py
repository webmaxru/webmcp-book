"""Validated evaluation records and local grading rules; no network or file writes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Tuple

MODES = {"AUDIT", "LIGHT EDIT", "DE-SLOP", "PROFESSIONAL REWRITE"}
DIMENSIONS = (
    "fidelity", "substance_density", "structure",
    "voice_preservation", "reader_fit", "slop_reduction",
)
EXPECT_LISTS = {
    "literal_checks", "verbatim", "semantic_invariants", "should_do", "must_not_do",
}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def strict_json(text: str) -> Any:
    return json.loads(
        text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant,
    )


def require_text(value: Any, label: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{label} must be {'a string' if allow_empty else 'a nonempty string'}")
    return value


def text_list(value: Any, label: str) -> Tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array of strings")
    return tuple(require_text(item, label) for item in value)


@dataclass(frozen=True)
class Candidate:
    mode: str
    edited_text: str = ""
    audit: str = ""
    substance_flags: Tuple[str, ...] = ()
    material_changes: Tuple[str, ...] = ()

    @property
    def body(self) -> str:
        return self.audit if self.mode == "AUDIT" else self.edited_text

    def payload(self) -> Dict[str, Any]:
        return asdict(self)


def parse_outputs(raw: Any) -> Dict[str, Candidate]:
    if not isinstance(raw, dict):
        raise ValueError("Outputs must map sample IDs to mode-aware output objects")
    results = {}
    allowed = {"mode", "edited_text", "audit", "substance_flags", "material_changes"}
    for sid, value in raw.items():
        require_text(sid, "sample ID")
        if not isinstance(value, dict):
            raise ValueError(f"{sid}: use an output object, not legacy text or another value")
        if set(value) - allowed:
            raise ValueError(f"{sid}: unknown output fields: {sorted(set(value) - allowed)}")
        mode = value.get("mode")
        if not isinstance(mode, str) or mode not in MODES:
            raise ValueError(f"{sid}: invalid or missing mode")
        active = "audit" if mode == "AUDIT" else "edited_text"
        inactive = "edited_text" if mode == "AUDIT" else "audit"
        body = require_text(value.get(active), f"{sid}.{active}", allow_empty=True)
        if value.get(inactive) not in (None, ""):
            raise ValueError(f"{sid}: {inactive} must be empty for {mode}")
        results[sid] = Candidate(
            mode=mode,
            edited_text=body if active == "edited_text" else "",
            audit=body if active == "audit" else "",
            substance_flags=text_list(value.get("substance_flags", []), f"{sid}.substance_flags"),
            material_changes=text_list(value.get("material_changes", []), f"{sid}.material_changes"),
        )
    return results


def validate_samples(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("Samples must be a nonempty array")
    seen = set()
    for sample in raw:
        if not isinstance(sample, dict):
            raise ValueError("Each sample must be an object")
        for field in ("id", "mode", "register", "reader", "task", "input"):
            require_text(sample.get(field), f"sample.{field}")
        sid = sample["id"]
        if sid in seen:
            raise ValueError(f"Duplicate sample ID: {sid}")
        seen.add(sid)
        if sample["mode"] not in MODES:
            raise ValueError(f"{sid}: unknown mode")
        if "voice_sample" in sample:
            require_text(sample["voice_sample"], f"{sid}.voice_sample")
        expect = sample.get("expect")
        if not isinstance(expect, dict):
            raise ValueError(f"{sid}: expect must be an object")
        unknown = set(expect) - EXPECT_LISTS - {"fact_relations"}
        if unknown:
            raise ValueError(f"{sid}: unknown expectation fields: {sorted(unknown)}")
        for key in EXPECT_LISTS:
            text_list(expect.get(key, []), f"{sid}.{key}")
        relations = expect.get("fact_relations", [])
        if not isinstance(relations, list):
            raise ValueError(f"{sid}: fact_relations must be an array")
        for relation in relations:
            if not isinstance(relation, dict) or set(relation) != {"subject", "relation", "object", "scope"}:
                raise ValueError(f"{sid}: a fact relation needs subject, relation, object, and scope")
            for key, value in relation.items():
                require_text(value, f"{sid}.fact_relations.{key}")
        for literal in expect.get("verbatim", []):
            if literal not in sample["input"]:
                raise ValueError(f"{sid}: protected verbatim span is absent from the source")
        if sample["mode"] == "AUDIT" and (expect.get("literal_checks") or expect.get("verbatim")):
            raise ValueError(f"{sid}: AUDIT expectations must not require repeating source literals")
    return raw


def candidate_problem(sample: Dict[str, Any], candidate: Candidate) -> str:
    if candidate.mode != sample["mode"]:
        return f"Expected {sample['mode']}, received {candidate.mode}"
    if not candidate.body.strip():
        justified_empty_rewrite = (
            candidate.mode in {"DE-SLOP", "PROFESSIONAL REWRITE"}
            and bool(candidate.substance_flags)
        )
        if not justified_empty_rewrite:
            return "Empty output without a substantive deletion explanation"
    return ""


def judge_contracts(sample: Dict[str, Any], second_pass: bool = False) -> List[Dict[str, Any]]:
    contracts = [
        {"id": "fidelity", "requirement": "Preserve supported meaning, relationships, uncertainty, recommendations, attribution, and protected content. For AUDIT, judge its claims and representative edits; it need not repeat all source facts.", "fidelity": True},
        {"id": "mode", "requirement": f"Follow {sample['mode']} and the requested editing/output scope; substantive source facts cannot survive only in commentary when lost from the edited text.", "fidelity": False},
    ]
    for key in ("literal_checks", "verbatim", "semantic_invariants", "fact_relations", "should_do", "must_not_do"):
        for index, item in enumerate(sample["expect"].get(key, [])):
            if key == "fact_relations":
                requirement = "Preserve this relationship in context: " + json.dumps(item, ensure_ascii=False)
            else:
                requirement = f"{key}: {item}"
            contracts.append({
                "id": f"{key}:{index}",
                "requirement": requirement,
                "fidelity": key in {"literal_checks", "verbatim", "semantic_invariants", "fact_relations"},
            })
    if second_pass:
        contracts.append({
            "id": "second_pass_restraint",
            "requirement": "Compared with the supplied first pass, change only actual remaining reader-facing defects; do not create churn to demonstrate editing. Preserve the original contract.",
            "fidelity": False,
        })
    return contracts


def judge_schema() -> Dict[str, Any]:
    def obj(properties):
        return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}

    return obj({
        "scores": obj({name: {"type": "integer", "minimum": 0, "maximum": 5} for name in DIMENSIONS}),
        "fidelity_violations": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
        "contract_checks": {
            "type": "array",
            "items": obj({
                "id": {"type": "string"},
                "status": {"type": "string", "enum": ["pass", "fail", "unclear"]},
                "reason": {"type": "string"},
            }),
        },
    })


def validate_judgment(raw: Any, contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
    required = {"scores", "fidelity_violations", "summary", "contract_checks"}
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("Judge result has missing/unknown fields or is not an object")
    scores = raw["scores"]
    if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
        raise ValueError("Judge must score all six dimensions exactly once")
    if any(type(score) is not int or not 0 <= score <= 5 for score in scores.values()):
        raise ValueError("Judge scores must be integers from 0 through 5, not booleans")
    violations = text_list(raw["fidelity_violations"], "fidelity_violations")
    require_text(raw["summary"], "judge.summary")
    checks = raw["contract_checks"]
    if not isinstance(checks, list):
        raise ValueError("contract_checks must be an array")
    expected = {item["id"]: item for item in contracts}
    seen = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"id", "status", "reason"}:
            raise ValueError("Invalid judge contract check")
        cid = require_text(check["id"], "contract check ID")
        if cid not in expected or cid in seen:
            raise ValueError(f"Unknown or duplicate judge contract ID: {cid}")
        seen.add(cid)
        if check["status"] not in ("pass", "fail", "unclear"):
            raise ValueError("Invalid judge contract status")
        require_text(check["reason"], f"{cid}.reason")
    if seen != set(expected):
        raise ValueError(f"Judge omitted contracts: {sorted(set(expected) - seen)}")

    hard_fail = bool(violations) or scores["fidelity"] < 5 or any(
        check["status"] == "fail" and expected[check["id"]]["fidelity"] for check in checks
    )
    status = "fail" if hard_fail or any(c["status"] == "fail" for c in checks) else (
        "not_evaluated" if any(c["status"] == "unclear" for c in checks) else "pass"
    )
    total = sum(scores.values())
    band = next(label for floor, label in (
        (27, "Excellent"), (23, "Strong"), (18, "Mixed"), (12, "Weak"), (0, "Fail")
    ) if total >= floor)
    return {
        **raw, "status": status, "hard_fail": hard_fail, "total": total,
        "quality_band": "FAIL" if status == "fail" else (
            "Not evaluated" if status == "not_evaluated" else band
        ),
        "note": "Content judgment of supplied artifacts, not proof of editor tool behavior.",
    }
