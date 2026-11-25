# Releasing *Tools, Not Clicks*

## Prepare the edition

Run [`/update-book check`](.github/prompts/update-book.prompt.md) to compare the book with upstream sources without editing it. `prepare` updates the manuscript and its evidence, builds all editions and stops at a local commit. Review that commit and open a content PR against `main`.

Pick a version based on what **readers of the last stable tag** will see:

| Increment | When to use it |
| --- | --- |
| Major (`3.0.0`) | Whole-book revision, chapters added, removed or reordered, or an API change that breaks earlier listings. |
| Minor (`2.3.0`) | New material within the existing structure: section, appendix, figure, listing or implementation-status update. |
| Patch (`2.2.1`) | Corrections, broken links or errata. Put build/theme fixes in a separate tooling PR. |
| Prerelease (`2.3.0-rc.1`) | Review copy; neither Latest nor a production web deploy. |

The PR delta determines whether an update is tooling-only. The delta from the previous stable tag determines whether there is reader-facing material to publish. These are deliberately different: `main` already contains manuscript changes after `v2.2.0`, including two appendices. Do not reset the baseline to the workflow installation commit. A catch-up PR may consist entirely of the new metadata, CHANGELOG and evidence **if** the tagged edition differs from the manuscript on its head.

**Book release preflight** runs the tests, checks release policy, lints the manuscript, builds the PDF, EPUB and offline HTML, and runs EPUBCheck. For a content PR:

- Use only `manuscript/`, `outline/`, `editorial/`, `figures/`, `VALIDATION.md`, `CHANGELOG.md` and `tools/book.json`. In that JSON file only `version`, `edition`, `chrome_version`, `spec_date` and `year` are release metadata. Configuration and tooling belong in a separate PR with no version bump.
- Set a previously untagged version above the last stable tag and current base version. Add one nonempty `## [X.Y.Z] - YYYY-MM-DD` CHANGELOG section. Keep `[Unreleased]` for work not in that edition.
- For each chapter or appendix changed in the PR, update `editorial/<manuscript-stem>-editorial-log.md`, its `editorial/fidelity/<stem>.md` or a shared `editorial/fidelity-ledger*.md`, and `VALIDATION.md`. Add missing logs for new chapters. Record actual claim/source/retrieval dates, what changed, and what was not retested. CI checks changed paths; the owner checks whether the evidence supports the claims.

## Authorize and publish

For someone else's non-draft PR, **webmaxru** submits an **Approve** review on its current head. For an owner-authored PR, post exactly `/release-book <full lowercase 40-character head SHA>` in a new PR conversation comment. An older SHA, another user's comment, or approval superseded by requested changes or dismissal does not count. Reapprove after any such barrier. The head must include current `main`.

The controller inspects review and CI events; a scheduled scan of up to 30 open PRs and **Approved book → Run workflow → pr** can recover missed signals. None of those triggers grants approval. It repeats preflight with validators from the approved base, rechecks approval and the base, and requests a squash merge conditional on the approved SHA. Private free-plan repository settings do not enforce this gate: **manual merges bypass it**. The site's normal push deployment can then serve unreleased `main`.

The controller explicitly dispatches **Release** because a `GITHUB_TOKEN` merge, tag or publication does not trigger the usual downstream events. Release checks the merged PR, approval, exact tree, squash parent, main ancestry and version. It builds the merge commit *before* creating its annotated tag. A draft receives the PDF, EPUB, HTML zip and `SHA256SUMS.txt`; only then is it published, with notes from the same commit. Only the highest stable semver is marked Latest. For stable versions Release dispatches `deploy-swa` with `ref` set to the tag and waits for the deploy and smoke test. For store uploads see [Leanpub and KDP](README.md#leanpub).

## Recovery and corrections

Pushing a tag no longer publishes. If the squash succeeded but dispatch or build failed, run **Release → Run workflow** on `main` with the `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag` recorded in the merge job. Inputs are checked again; manually merged, forged or mismatched revisions are not recovery candidates. A matching published release with all four assets is a no-op. A lone tag, draft, incomplete asset set or wrong target stops recovery without writes. Inspect a partial publication before proceeding; never move a tag or overwrite published downloads.

A correction needs a **new patch version**, not a rebuild with `--clobber`. If only the deploy failed after publication, rerun **deploy-swa** with the published tag, not Release. Use the same deploy workflow with an older tag for a web-only rollback; downloads stay intact. See [DEPLOY.md](DEPLOY.md).
