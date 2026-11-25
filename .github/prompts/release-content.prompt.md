---
description: Review a WebMCP content candidate and explain its release status
---

Follow `RELEASING.md`. Read the PR's base, head SHA, authored-by, exact Book CI run and **Book release preflight** result. Inspect the previous stable tag, metadata-only `tools/book.json` delta, dated CHANGELOG and editorial/fidelity/validation evidence. Check that no tooling is mixed in, the head includes main, and the edition accounts for all unreleased material since the stable tag.

Report the exact candidate tag, evidence gaps and the next human action. For someone else's PR, the owner reviews the current head; for the owner's PR show the exact `/release-book <full head SHA>` comment for the owner to post. Do not post approval, merge, tag, dispatch, rebuild published assets or deploy. If recovery is needed, report the five recorded controller inputs or identify the missing provenance; never invent them. A successful approved path publishes three editions and checksums, then verifies the stable web deployment.
