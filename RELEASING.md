# Releasing *Tools, Not Clicks*

A release is a Git tag `vX.Y.Z` on the squash-merge of an **owner-approved, content-only pull request**. Nothing else publishes: not a push, a tag, a label or a manual merge. Production serves released editions only.

```text
/update-book check ─► /update-book prepare ─► content PR ─► Book release preflight (green)
        ─► owner approval of the exact head ─► Release approved book: squash-merge
        ─► Release book: build, annotated tag, draft, upload, publish ─► deploy-swa: web edition
```

This repository follows the shared [Book release flow contract v1](#book-release-flow-contract-v1): every book repository runs the same release system, and only the [per-book settings](#per-book-settings) differ. The sections after them explain each step. [Scenarios](#scenarios-what-to-do-when) walks through the situations you will actually meet, with commands.

## Book release flow contract v1

Every book repository follows the same release flow. A repository conforms when `tests/test_flow_contract.py` passes and each rule below is covered by a test in that repository's own suite.

1. **Workflow surface (same names everywhere).**
   `ci.yml` named "Book CI" with the aggregate job "Book release preflight"; `book-approval-signal.yml` named "Book approval signal"; `approved-book.yml` named "Release approved book"; `release.yml` named "Release book"; one deploy workflow, `deploy-swa.yml` or `deploy-pages.yml`.
2. **Controller.**
   Triggers: `workflow_run` of "Book approval signal" and "Book CI", `issue_comment`, schedule `17,47 * * * *`, and `workflow_dispatch` with the input `pr`. Jobs run only from `main`. Workflow `permissions: {}` with least privilege per job. Concurrency group `approved-book`, no cancel. Validators always run from `main`, never from the pull request.
3. **Eligibility.**
   The pull request is open, not a draft, from the same repository, targets `main`, is mergeable, and its head contains the current `main`. Its files are content-only under the book's allowlist. "Book release preflight" is green on the exact head, and the version, CHANGELOG and evidence checks pass.
4. **Authorization.**
   Someone else's pull request: an owner Approve review on the current head. The owner's own pull request: an owner comment `/release-book <40-character head SHA>`. A later push, a CHANGES_REQUESTED review, a dismissed review or an edited or deleted comment revokes it. A non-owner never authorizes.
5. **Merge.**
   A squash merge conditioned on the approved head SHA. The controller then dispatches `release.yml`, because merges made with `GITHUB_TOKEN` trigger no workflows.
6. **Release.**
   `release.yml` is dispatch-only, with the inputs `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag`, and the concurrency group `book-publish`. Steps: plan, build from the merge commit, annotated tag, draft release, upload assets, publish, deploy the released tag, smoke test. Never clobber assets and never move a tag. A complete release is a no-op. A partial release or a provenance mismatch fails with no writes. Latest goes only to the highest stable version, and prereleases are never Latest. A fix is a new version.
7. **Deploy.**
   Production serves only released editions. A push to `main` deploys only when the content equals the latest published release (the `published-source` job). The release deploys its own tag. A manual dispatch takes a released ref or sha, which is the rollback path.
8. **No other publisher.**
   A tag push, a label or a branch name never publishes. A manual merge to `main` bypasses the controller; the fix is a catch-up pull request with a higher version.
9. **Pins.**
   Runner `ubuntu-24.04`. `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8` (a full commit SHA with a trailing `# v7.x.y` version comment is acceptable).

### Per-book settings

What differs in this book, behind the identical workflow surface:

| Setting | This book |
| --- | --- |
| Format and build | Markdown manuscript in `manuscript/` (order in `Book.txt`). `python tools/build.py all` builds the PDF (7 × 9.25 in), the EPUB 3 and the offline HTML zip; `python tools/build.py site` builds the web edition. CI and the release use the same composite action, [`build-editions`](.github/actions/build-editions/action.yml), which also runs EPUBCheck. |
| Version file, scheme and tag | `version` in `tools/book.json`. Semantic version `X.Y.Z`, annotated tag `vX.Y.Z`. A prerelease is `X.Y.Z-rc.N`: it is marked pre-release, is never Latest and never deploys. |
| Content allowlist | `manuscript/`, `outline/`, `editorial/`, `figures/`, `VALIDATION.md`, `CHANGELOG.md`, and in `tools/book.json` only the release keys `version`, `edition`, `chrome_version`, `spec_date` and `year`. Everything else is tooling and goes in a separate PR with no version bump. The definition lives once, in `tools/release_policy.py`, and the controller, preflight and the deploy gate all use it. |
| Evidence rules | For every chapter or appendix a PR changes: its `editorial/<stem>-editorial-log.md`, its `editorial/fidelity/<stem>.md` (or a shared `editorial/fidelity-ledger*.md`) and `VALIDATION.md`, plus one non-empty, dated `## [X.Y.Z] - YYYY-MM-DD` CHANGELOG section. CI checks the changed paths; the owner judges what they claim. |
| Release assets | `Tools-Not-Clicks-Maxim-Salnikov-vX.Y.Z.pdf`, `.epub`, `Tools-Not-Clicks-HTML-vX.Y.Z.zip` and `SHA256SUMS.txt` (stems from `file_stem` and `html_zip_stem` in `tools/book.json`). |
| Deploy target and domain | Azure Static Web Apps (Free plan) through `deploy-swa.yml`, serving https://webmcp.salnikov.no. Secret `AZURE_STATIC_WEB_APPS_API_TOKEN`, concurrency group `swa-production`, smoke test of `/`. Setup: [DEPLOY.md](DEPLOY.md). |
| Catch-up PR rules | A hand-merged content PR burns its version. The catch-up PR carries a version above the burned one and above the latest stable tag (`3.1.1` after a hand-merged `3.1.0`). It may consist of metadata, CHANGELOG and evidence only, because the content is already on `main`. See scenario 10. |
| Upstream-update scouting | `/update-book check` (read-only impact report) and `/update-book prepare` (a tested local content commit), from [`update-book.prompt.md`](.github/prompts/update-book.prompt.md) and `tools/check_upstream.py`. It surveys the WebMCP draft, the Blink implementation, Chrome status and the stable Chrome version, the W3C polyfill, the MCP specification and the companion demos. Scouting only reads; it has no part in the release flow. |
| Intentional refinement | After publishing, **Release book** deploys its own tag only if that tag is the highest stable version. Otherwise it prints a notice and the live site keeps the newer edition, so a stale recovery run cannot roll production back. A controller release is always the highest version, so normally this is the same as the contract's rule 7. |

## Prepare the edition

Run [`/update-book check`](.github/prompts/update-book.prompt.md) to compare the book with upstream sources without editing it. `prepare` updates the manuscript and its evidence, builds all editions and stops at a local commit. Review that commit and open a content PR against `main`.

Pick a version based on what **readers of the last stable tag** will see:

| Increment | When to use it |
| --- | --- |
| Major (`3.0.0`) | Whole-book revision, chapters added, removed or reordered, or an API change that breaks earlier listings. |
| Minor (`2.3.0`) | New material within the existing structure: section, appendix, figure, listing or implementation-status update. |
| Patch (`2.2.1`) | Corrections, broken links or errata. Put build/theme fixes in a separate tooling PR. |
| Prerelease (`2.3.0-rc.1`) | Review copy; neither Latest nor a production web deploy. |

The PR delta determines whether an update is tooling-only. The delta from the previous stable tag determines whether there is reader-facing material to publish. These are deliberately different: `main` can contain manuscript changes after the last stable tag, for example after a manual merge (scenario 10). Do not reset the baseline to the workflow installation commit. A catch-up PR may consist entirely of the new metadata, CHANGELOG and evidence **if** the tagged edition differs from the manuscript on its head.

**Book release preflight** runs the tests, checks release policy, lints the manuscript, builds the PDF, EPUB and offline HTML, and runs EPUBCheck. For a content PR:

- Use only `manuscript/`, `outline/`, `editorial/`, `figures/`, `VALIDATION.md`, `CHANGELOG.md` and `tools/book.json`. In that JSON file only `version`, `edition`, `chrome_version`, `spec_date` and `year` are release metadata. Configuration and tooling belong in a separate PR with no version bump.
- Set a previously untagged version above the last stable tag and current base version. Add one nonempty `## [X.Y.Z] - YYYY-MM-DD` CHANGELOG section. Keep `[Unreleased]` for work not in that edition.
- For each chapter or appendix changed in the PR, update `editorial/<manuscript-stem>-editorial-log.md`, its `editorial/fidelity/<stem>.md` or a shared `editorial/fidelity-ledger*.md`, and `VALIDATION.md`. Add missing logs for new chapters. Record actual claim/source/retrieval dates, what changed, and what was not retested. CI checks changed paths; the owner checks whether the evidence supports the claims.

## Authorize and publish

For someone else's non-draft PR, **webmaxru** submits an **Approve** review on its current head. GitHub does not let you approve your own PR, so for an owner-authored PR post a new PR conversation comment whose **entire body** is `/release-book <full lowercase 40-character head SHA>`. What counts:

- **Only the owner authorizes.** An approval or a command from anyone else never counts.
- **The latest formal owner review decides.** Plain `Comment` reviews are ignored. The latest of **Approve**, **Request changes** and dismissals by the owner must be an approval of the current head. A push that moves the head revokes it, and an approval of an older head never counts.
- **Anyone's veto is a barrier.** A **Request changes** review or a dismissed review by **any** reviewer, or any review dismissal, revokes every earlier authorization, an Approve review and a command comment alike. Only a fresh owner authorization strictly after the barrier counts, so approve again (or comment again) once the matter is settled. A plain `Comment` review by anyone changes nothing.
- **The command is exact and fresh.** It names the full SHA of the current head, was posted after the latest barrier, and was **never edited** (GitHub's `updated_at` equals `created_at`). Fixing a typo in a posted command revokes it, so post a new comment instead. A deleted comment authorizes nothing.
- **The head includes current `main`.**

The controller, **Release approved book**, inspects review and CI events; a scheduled scan of up to 30 open PRs (at :17 and :47 past each hour) and **Release approved book → Run workflow → pr** can recover missed signals. None of those triggers grants approval. It runs from `main` only, repeats preflight with the validators from `main` (never the PR's own code), rechecks approval and the base, and requests a squash merge conditional on the approved SHA. The repository has no branch protection or ruleset, so nothing enforces this gate: **a manual merge bypasses it** (scenario 10). Because the web deploy is gated too (see [Deploy](#deploy)), a manual merge cannot put unreleased content on the site, but it publishes nothing either.

The controller explicitly dispatches **Release book** because a `GITHUB_TOKEN` merge, tag or publication does not trigger the usual downstream events. Release book checks the merged PR, the approval as it stood at the merge, the exact tree, the squash parent, main ancestry and the version. It builds the merge commit *before* creating its annotated tag. A draft receives the PDF, EPUB, HTML zip and `SHA256SUMS.txt`; only then is it published, with notes from the same commit. Only the highest stable semver is marked Latest. For a stable version that is the highest, Release book then dispatches `deploy-swa` for that tag and waits for the deploy and smoke test. For store uploads see [Leanpub and KDP](README.md#leanpub).

## Deploy

Production serves **released editions only**. [`deploy-swa`](.github/workflows/deploy-swa.yml) can start three ways, and its first job, `published-source`, decides what it may build before anything is built or uploaded:

| Start | What it deploys |
| --- | --- |
| **Release book**, right after it publishes a stable version | That release's own tag, if it is the highest stable version. Release book waits for the run and requires the smoke test to have passed. A prerelease never deploys. |
| A push to `main` | `main` itself, but only while its book content equals the latest published stable release. Otherwise the run is skipped with a notice and stays green. |
| **deploy-swa → Run workflow** with `ref` | A published release tag (`vX.Y.Z`) or the full SHA of its commit: the rollback and retry path. Branches, drafts, prereleases, bare tags and unreleased commits are refused. |

What counts as book content is defined once, in `tools/release_policy.py` (the allowlist that also limits a content PR), not repeated as path patterns in the workflow. Tooling, theme and workflow changes are not book content, so they deploy on push whenever `main` equals the latest release. While `main` carries unreleased content, a push deploys nothing: see scenarios 10 and 19. Secrets, setup and rollback details are in [DEPLOY.md](DEPLOY.md).

## Recovery and corrections

Pushing a tag does not publish. If the squash succeeded but dispatch or build failed, run **Release book → Run workflow** on `main` with the `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag` recorded in the merge job. Inputs are checked again, and the approval is judged as it stood at the merge: later events are ignored, but a change request or dismissal by anyone before the merge needs a fresh owner authorization after it. Manually merged, forged or mismatched revisions are not recovery candidates, and neither is a merge whose approving review or command comment was edited, deleted or dismissed afterwards. A matching published release with all four assets is a no-op. A lone tag, draft, incomplete asset set or wrong target stops recovery without writes. Inspect a partial publication before proceeding; never move a tag or overwrite published downloads.

A correction needs a **new patch version**, not a rebuild with `--clobber`. If only the deploy failed after publication, rerun **deploy-swa** with the published tag, not Release book: a complete release is a no-op and does not redeploy. Use the same deploy workflow with an older published tag for a web-only rollback; downloads stay intact. See [DEPLOY.md](DEPLOY.md).

## Scenarios: what to do when

Commands use the [GitHub CLI](https://cli.github.com/) (`gh`) from a clone of this repository and work in bash and PowerShell. `N` is the pull request number and `vX.Y.Z` a tag.

### What triggers what

| Event | What happens | Release? |
| --- | --- | --- |
| PR opened or pushed | **Book CI** runs tests, release policy, lint and a full build. Its **Book release preflight** job is the gate. | No |
| Owner **Approve** review, or an owner `/release-book <SHA>` comment | **Book approval signal** relays a review; **Release approved book** re-checks everything and squash-merges the approved head. | Yes, through **Release book** |
| Book CI or approval-signal run finishes, or the half-hourly scan | The controller looks for an approved PR it missed. It never approves anything itself. | Only if a valid approval exists |
| **Release approved book → Run workflow** with `pr` | Same re-check for one PR. | Only if a valid approval exists |
| **Release book → Run workflow** with the recorded inputs | Recovery of a PR the controller merged (scenario 12). A complete release is a no-op; anything partial stops without writes. | Only for a PR the controller merged |
| Push a tag, add a label, press **Merge** | Nothing in the release flow. | **No** |
| Push to `main` | **deploy-swa** deploys `main` only if its book content equals the latest published release; otherwise it skips (scenarios 10 and 19). | **No** |
| **deploy-swa → Run workflow** with `ref` | Deploys a published release tag or its commit SHA: the rollback and retry path. Anything unreleased is refused. | **No** |

The last rows matter: the web edition and the downloads are separate. Only the controller's squash-merge produces a tag and downloads, and only a released edition reaches production.

### 1. Routine update (your own PR)

1. `/update-book check` for the impact report, then `/update-book prepare` for a tested commit on a branch.
2. Check locally what CI will check:

   ```sh
   python tools/release_policy.py --base origin/main   # prints the tag, e.g. v3.2.0
   python tools/lint_manuscript.py
   python -m unittest discover -s tests
   ```

3. Push and open the PR against `main`:

   ```sh
   git push -u origin content/my-update
   gh pr create --base main --title "Update for WebMCP draft of <date>" --body "See CHANGELOG."
   ```

4. Wait for **Book release preflight** to pass (`gh pr checks N --watch`). Check the CHANGELOG section and the editorial and validation evidence yourself.
5. Authorize **the exact head**. You wrote the PR, so GitHub will not let you approve it. Comment instead, and do not edit the comment afterwards (an edit revokes it; post a new one):

   ```sh
   gh pr comment N --body "/release-book $(gh pr view N --json headRefOid --jq .headRefOid)"
   ```

6. Watch it go through, normally within a few minutes:

   ```sh
   gh run list --workflow approved-book.yml -L 3
   gh run list --workflow release.yml -L 3
   gh run list --workflow deploy-swa.yml -L 3
   gh release view vX.Y.Z
   ```

**Result:** the PR is squash-merged, `vX.Y.Z` is an annotated tag on the merge commit, the release has the PDF, EPUB, HTML zip and `SHA256SUMS.txt`, it is Latest if it is the highest stable version, and the web edition is deployed from that tag and smoke-tested.

### 2. Someone else's PR on a branch in this repository

A collaborator with write access opens a content PR. This is the normal case for contributions.

1. Read the diff. The PR must be non-draft, target `main`, change only content files (see [Prepare the edition](#prepare-the-edition)) and pass **Book release preflight**. A contributor usually does not know about the version bump, the CHANGELOG section and the evidence files, so preflight fails until they exist. Add them to the contributor's branch yourself:

   ```sh
   gh pr checkout N
   # edit tools/book.json version, CHANGELOG.md, editorial/ and VALIDATION.md
   git add -A && git commit -m "Prepare vX.Y.Z" && git push
   ```

2. When preflight is green, submit an **Approve** review on the current head and stop there:

   ```sh
   gh pr review N --approve
   ```

**Do not press Merge.** A manual merge publishes nothing and leaves the web edition unchanged (scenario 10). The pushes in step 1 change the head, so approve after them, not before.

### 3. A pull request from a fork

The controller only merges PRs whose head branch is in this repository, so a fork PR is refused. Re-create it on a branch here and keep the contributor's commits:

```sh
gh pr checkout N
git switch -c content/from-pr-N
git push -u origin content/from-pr-N
gh pr create --base main --head content/from-pr-N --title "<title>" --body "Supersedes #N"
```

You now own the new PR, so continue with scenario 1: add the bump, CHANGELOG and evidence, then comment `/release-book <SHA>`. Close the original PR with a thank-you.

### 4. A new push after approval, requested changes or a dismissed review

An approval counts only for the head it was given on. A push after approval voids it, and so does a **Request changes** review or a dismissed review by **anyone**, not only by you: each is a barrier, and only a fresh owner authorization after it counts. A plain **Comment** review changes nothing. Nothing merges until you approve again (a new **Approve** review, or a new `/release-book <SHA>` comment with the new head SHA, posted after the barrier). An old SHA in an old comment is ignored, and so is a command comment that was edited after it was posted: post a new one.

### 5. The branch is behind `main`

The head must include current `main`. Update it and approve again:

```sh
gh pr update-branch N
```

### 6. Approved, but the PR is still open

Look at the latest **Release approved book** run for the cause: failing preflight, a head that moved, a branch behind `main`, a change request or dismissal by anyone after your approval, an edited command comment, or a run that never started. Fix that, or just run the controller for this PR:

```sh
gh workflow run approved-book.yml -f pr=N
```

If the run died within a second with no steps, see [Runs that fail without starting](#11-runs-that-fail-without-starting).

### 7. Tooling, docs and workflow changes

A PR that touches only files outside the content allowlist (`tools/` other than `book.json` release keys, `.github/`, `theme/`, `infra/`, `README.md`, `RELEASING.md`, tests) is **tooling-only**. It needs no version bump, never releases, and the controller never merges it (`release_policy.py` prints `Tooling only`). Merge it yourself when CI is green. The merge triggers **deploy-swa**, whose gate deploys `main` only if its book content equals the latest release, so a tooling merge never puts unreleased content on the site. If `main` does carry unreleased content, the run is skipped (scenario 19).

### 8. Mixed content and tooling

A PR that changes both content and tooling fails preflight with `Separate content from tooling: [...]`. Split it into two PRs: tooling first (merged by you), then the content PR.

### 9. Review copy (prerelease)

Use a prerelease version such as `3.2.0-rc.1` for a copy to share before the real edition. The PR still goes through scenario 1 and still merges into `main`. The release is marked pre-release, is never Latest and never deploys the web edition. Its text is on `main`, but the deploy gate compares `main` with the latest **stable** release, so later pushes to `main` skip the deploy until the stable edition is released (scenario 19). A prerelease therefore cannot put review text on the site. To graduate it, open a new PR that sets `3.2.0`, adds that CHANGELOG section and carries the evidence. Its release deploys the stable edition.

### 10. A manual merge by mistake

Pressing **Merge** on a content PR, or merging from the command line, bypasses the controller. The repository has no branch protection or ruleset, so GitHub allows it. The effects:

- **No tag, no release, no downloads.** Recovery refuses it too: **Release book** only recovers a PR that the controller itself merged.
- **The web edition does not change.** The push starts **deploy-swa**, but its `published-source` gate sees book content on `main` that the latest release does not contain, so it skips the deploy (the run is green, with a notice). Production keeps serving the last released edition. Tooling merged afterwards does not deploy either, until the next release (scenario 19).
- The version the PR carried is now on `main` unreleased, so it is **burned**. The next PR must advance beyond it (`PR must advance the version on main`), so that version number is skipped, and the next release is `vX.Y.(Z+1)` or higher.

Fix it with a catch-up PR. For example, PR #18 was merged by hand, so `main` carries `3.1.0` while the latest tag is `v3.0.0`. (That merge predates the deploy gate, so the site served the content at once; with the gate in place a hand merge no longer does.) The catch-up:

1. Branch from `main`, set `version` in `tools/book.json` to `3.1.1` and add a dated `## [3.1.1] - YYYY-MM-DD` section to `CHANGELOG.md`. Move the unreleased `3.1.0` entries under it so the release notes describe the whole edition.
2. Check it: `python tools/release_policy.py --base origin/main` prints `v3.1.1`. Metadata, CHANGELOG and evidence are enough, because the reader-facing changes since the last stable tag are already on `main`.
3. Open the PR and authorize it as in scenario 1. Its release deploys `v3.1.1`, and the gate then lets pushes to `main` deploy again.

Version `3.0.0` was released this way: PR #17 turned the manuscript changes that were already on `main` into the third edition.

### 11. Runs that fail without starting

If **Release approved book** or **Book CI** runs end in about a second with no steps and the annotation *"The job was not started because recent account payments have failed or your spending limit needs to be increased"*, GitHub Actions is blocked by billing, not by this repository. Fix **Settings → Billing and plans**, then run `gh workflow run approved-book.yml -f pr=N` for each affected PR.

### 12. The release failed after the merge

The PR is merged but there is no (or an incomplete) release. Find the recorded inputs in the controller's `merge` job:

```sh
gh run list --workflow approved-book.yml -L 5
gh run view <run-id> --log | grep "Release recovery inputs"
```

In PowerShell, use `Select-String "Release recovery inputs"` instead of `grep`. The line looks like `Release recovery inputs: {"pr": 17, "head_sha": "…", "base_sha": "…", "tag": "v3.0.0", "merge_sha": "…"}`. Then run **Release book** with them:

```sh
gh workflow run release.yml -f pr=17 -f head_sha=<head_sha> -f base_sha=<base_sha> -f merge_sha=<merge_sha> -f tag=v3.0.0
```

Release book checks the merge again, and judges the approval as it stood at the merge. If the release is already complete, it is a no-op. If there is a lone tag, a draft, an incomplete asset set or a mismatched target, it stops with `inspect manually; no writes`. Look at the tag and draft on GitHub, decide what is safe, and see [Recovery and corrections](#recovery-and-corrections). Never move a tag or overwrite published downloads; the answer to a bad published file is a new patch version.

If it stops with `Missing approved-head provenance`, the approval is gone: the approving review or the `/release-book` comment was edited, deleted or dismissed after the merge, or someone requested changes or dismissed a review between your authorization and the merge. Recovery stays refused on purpose. Do not recreate the comment. Release the merged content with a catch-up PR and a higher version (scenario 10). Until the release is published, leave the approving review and the command comment untouched.

### 13. Only the deploy failed

The release is published and complete but the web edition is not live (or **deploy-swa** failed, or the Azure token was missing at the time). Do not re-run **Release book**: a complete release is a no-op and does not redeploy. Deploy the tag:

```sh
gh workflow run deploy-swa.yml -f ref=vX.Y.Z
```

If the run summary says the web edition was not deployed because `AZURE_STATIC_WEB_APPS_API_TOKEN` is missing, see [DEPLOY.md](DEPLOY.md).

### 14. Roll back the web edition

Downloads stay as they are; only the site changes. Deploy an older **published** release by its tag or by the full SHA of its commit:

```sh
gh workflow run deploy-swa.yml -f ref=v2.2.0
```

The run refuses anything that is not a published stable release: a branch, a draft, a prerelease, a bare tag or an unreleased commit. That includes `v1.0.0`, which has a tag but no release. Only releases from `v2.0.0` on contain `tools/build.py`, so only they can be built.

A rollback is temporary. The next release, and any push to `main` that the gate allows (`main`'s content equals the latest release, as after a tooling merge), deploys the latest edition again. The lasting fix is a new version (scenario 15).

### 15. A published release is wrong

Do not edit the release or move its tag. Fix `main`, add a patch version through scenario 1 and release it. To withdraw a release completely, delete the GitHub release, then delete the tag with `git push origin :refs/tags/vX.Y.Z`. The version number stays used on `main`, so the next release must still be higher. Withdrawing a release does not change the live site; if it serves the bad edition, roll back with scenario 14.

### 16. Choosing the version

Follow the table in [Prepare the edition](#prepare-the-edition). When unsure, ask what a reader of the last stable tag would notice: broken earlier listings or a restructured book is major, new material is minor, corrections are patch. The version must exceed both the highest stable tag and the version already on `main`. Preflight tells you if it does not.

### 17. Leanpub and Kindle Direct Publishing

The workflow publishes GitHub downloads and the web edition only. Upload the EPUB or PDF to Leanpub and KDP by hand from the release page; see [Leanpub](README.md#leanpub) and [Kindle Direct Publishing](README.md#kindle-direct-publishing-kdp).

### 18. Control center alerts

If you use the book control center, each alert has a fix on this page:

| Alert | Cause and fix |
| --- | --- |
| `PR #N is ready for your approval` | Preflight is green. Approve the head (scenario 2) or comment `/release-book <SHA>` (scenario 1). |
| `PR #N release preflight is failing` | Open the failed **Book CI** run. Fix the PR, or re-run failed jobs if the failure was transient. |
| `PR #N was approved but is still open` | Scenario 6. |
| `PR #N changed after your approval` | Scenario 4. Approve the new head. |
| `<workflow> failed` | Open the run. Re-run failed jobs, or use scenario 11 (billing), 12 (release) or 13 (deploy). |
| `<run> has been queued for N days` | An orphaned run. `gh run cancel <run-id>`. |
| `N content file(s) changed since vX.Y.Z without a release` | Scenario 10: content reached `main` without the controller. The deploy gate keeps it off the site (scenario 19). |
| `Site is not responding` | Scenario 13, then [DEPLOY.md](DEPLOY.md). |

### 19. The web edition did not change after a merge to `main`

Open the latest **deploy-swa** run and read its summary:

```sh
gh run list --workflow deploy-swa.yml -L 3
gh run view <run-id> --web   # the notice and the run summary say why
```

`Deploy skipped.` with *main carries book content that is not in the latest release vX.Y.Z* is the gate working as intended: the run is green on purpose, and production keeps serving the last released edition. It means `main` holds book content that no release contains. The usual causes:

- a content PR merged by hand (scenario 10),
- a prerelease merged to `main` (scenario 9),
- a controller merge whose release never completed (scenario 12).

The fix is to release that content: complete the recovery (12) or open a catch-up PR with a higher version (10). Once the release is published, **Release book** deploys it, and later pushes to `main` deploy again.

To serve an edition that is already released, or to retry a failed deploy, name its tag:

```sh
gh workflow run deploy-swa.yml -f ref=vX.Y.Z
```

### Before you open any PR

```sh
python -m unittest discover -s tests
python tools/lint_manuscript.py
python tools/release_policy.py --base origin/main   # content PR: prints the tag; otherwise "Tooling only"
python tools/build.py all                           # all editions, as CI builds them
```