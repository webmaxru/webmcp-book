"""Text-level readers for the workflow tests: stdlib only, no YAML parser, same approach as test_flow_contract."""
import re
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
MAIN = "github.ref == 'refs/heads/main'"


def read(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def top_level(text, key):
    """Raw text of a top-level `key:` block, up to the next top-level key."""
    match = re.search(rf"^{re.escape(key)}:(.*?)(?=^\S|\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def jobs(name):
    """{job id: raw text}. Job ids sit at two spaces of indentation under `jobs:`."""
    parts = re.split(r"(?m)^  ([\w-]+):[ \t]*$", top_level(read(name), "jobs"))
    return dict(zip(parts[1::2], parts[2::2]))


def needs(chunk):
    found = re.search(r"(?m)^    needs:\s*(.+?)\s*$", chunk)
    return re.findall(r"[\w-]+", found[1]) if found else []


def permissions(chunk):
    """The job-level `permissions:` block as {scope: level}."""
    block = re.search(r"(?m)^    permissions:[ \t]*\n((?:      \S.*\n?)*)", chunk)
    return dict(re.findall(r"(?m)^      ([\w-]+):\s*(\w+)\s*$", block[1])) if block else {}


def main_only(name, job):
    """True when the job can only run from main: its own `if:` says so, or a job it needs does."""
    all_jobs = jobs(name)
    condition = re.search(r"(?m)^    if:\s*(.+)$", all_jobs[job])
    return bool(condition and MAIN in condition[1]) or any(main_only(name, n) for n in needs(all_jobs[job]))


def checkout_refs(chunk):
    """The `ref:` of every actions/checkout step in a job (None when the step has no ref)."""
    steps = re.split(r"(?m)^      - ", chunk)[1:]
    return [(re.search(r"(?m)^          ref:\s*(.+)$", s) or [None, None])[1]
            for s in steps if "uses: actions/checkout@" in s]


def dispatch_inputs(name):
    """Input ids of the workflow_dispatch trigger, and which of them are required."""
    on = top_level(read(name), "on")
    block = on[on.index("workflow_dispatch:"):]
    inputs = re.search(r"(?m)^    inputs:\s*\n((?:      .*\n?)*)", block)
    chunks = re.split(r"(?m)^      ([\w-]+):\s*$", inputs[1]) if inputs else [""]
    return {k: bool(re.search(r"(?m)^        required:\s*true\s*$", v)) for k, v in zip(chunks[1::2], chunks[2::2])}


def step_outputs(name):
    """{(step id, output name)} read through `steps.<id>.outputs.<name>` anywhere in the workflow."""
    return set(re.findall(r"steps\.([\w-]+)\.outputs\.([\w-]+)", read(name)))


def commands(*names):
    """{controller action: {frozenset of its --options}} for every `python tools/book_release.py` call."""
    found = {}
    for name in names:
        for action, rest in re.findall(r"python tools/book_release\.py ([\w-]+)([^\n]*)", read(name)):
            found.setdefault(action, set()).add(frozenset(re.findall(r"--[\w-]+", rest)))
    return found
