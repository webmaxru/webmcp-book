---
description: Check upstream changes or prepare a local WebMCP book update
---

Use `check` (default) or `prepare`. Work in one pass with targeted follow-up, not an agent fleet. Read `RELEASING.md`, `tools/book.json`, `manuscript/Book.txt` and the latest dated CHANGELOG section.

1. Run `python tools/check_upstream.py`. Use a checkout with tags and current main already available; in `check` mode do not fetch, edit, install, commit, or make remote writes. Record the exact revision, previous stable tag and tested Chrome/spec baselines. Read the actual `git diff <previous-stable>..<ref>`, including content already on main. Report missing refs or unavailable sources; do not interpret them as "no change."
2. Follow the primary sources. Compare the published WebMCP draft and changes to `index.bs` since `spec_date`; distinguish open explainers from merged normative changes. Compare ChromeStatus, Blink changes and channel milestones with `chrome_version`; distinguish shipped, trial, and documented-but-not-tested. Check `@w3c/webmcp-polyfill` release/API, the latest normative MCP revision, and `webmaxru/webmcp-book-demos` listings/tests. The helper's ten recent commits per feed are starting points; inspect older commits since baseline as needed.
3. Map each signal to an actual claim, example, figure or appendix. Output **upstream change + primary source | affected chapters | action | justification**. Include confirmed no-change and unresolved rows. Propose the version and draft CHANGELOG from the entire tagged-edition delta. **Stop here in check mode.**
4. In `prepare`, work on a content branch. Make targeted edits only. Use `.agents/skills/professional-writing-editor/SKILL.md` for the editorial pass and `.agents/skills/personal-author-voice/SKILL.md` for the author's voice. Reconcile listings and figure sources with the demos, update each changed chapter's editorial log and fidelity record, and add claim-specific retrieval dates and evidence to `VALIDATION.md`.
5. Update `version` and the applicable edition/date fields in `tools/book.json`; advance `chrome_version` only after an actual browser retest. Add a dated CHANGELOG section; leave build configuration untouched. Review the delta, run the manuscript lint, `python tools/build.py all`, and the stdlib tests. Make a local content commit, then run `python tools/release_policy.py --base <main-sha>` on it. Fix any failure locally. Report the SHA, tests, version rationale, and unresolved evidence.

Stop at the local commit. Never push, open a PR, approve, merge, tag, dispatch or publish as part of this prompt.
