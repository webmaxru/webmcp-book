# Releasing *Tools, Not Clicks*

A release is a Git tag `vX.Y.Z` on the squash-merge of an **owner-approved, content-only pull request**. Nothing else publishes: not a push, a tag, a label or a manual merge.

```text
/update-book check ─► /update-book prepare ─► content PR ─► Book release preflight (green)
        ─► owner approval of the exact head ─► Approved book: squash-merge
        ─► Release: build, annotated tag, draft, upload, publish ─► deploy-swa: web edition
```

The sections below explain each step. [Scenarios](#scenarios-what-to-do-when) walks through the situations you will actually meet, with commands.

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

The controller inspects review and CI events; a scheduled scan of up to 30 open PRs and **Approved book → Run workflow → pr** can recover missed signals. None of those triggers grants approval. It repeats preflight with validators from the approved base, rechecks approval and the base, and requests a squash merge conditional on the approved SHA. The repository has no branch protection or ruleset, so nothing enforces this gate: **manual merges bypass it**. The site's normal push deployment can then serve unreleased `main`.

The controller explicitly dispatches **Release** because a `GITHUB_TOKEN` merge, tag or publication does not trigger the usual downstream events. Release checks the merged PR, approval, exact tree, squash parent, main ancestry and version. It builds the merge commit *before* creating its annotated tag. A draft receives the PDF, EPUB, HTML zip and `SHA256SUMS.txt`; only then is it published, with notes from the same commit. Only the highest stable semver is marked Latest. For stable versions Release dispatches `deploy-swa` with `ref` set to the tag and waits for the deploy and smoke test. For store uploads see [Leanpub and KDP](README.md#leanpub).

## Recovery and corrections

Pushing a tag no longer publishes. If the squash succeeded but dispatch or build failed, run **Release → Run workflow** on `main` with the `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag` recorded in the merge job. Inputs are checked again; manually merged, forged or mismatched revisions are not recovery candidates. A matching published release with all four assets is a no-op. A lone tag, draft, incomplete asset set or wrong target stops recovery without writes. Inspect a partial publication before proceeding; never move a tag or overwrite published downloads.

A correction needs a **new patch version**, not a rebuild with `--clobber`. If only the deploy failed after publication, rerun **deploy-swa** with the published tag, not Release. Use the same deploy workflow with an older tag for a web-only rollback; downloads stay intact. See [DEPLOY.md](DEPLOY.md).

## Scenarios: what to do when

Commands use the [GitHub CLI](https://cli.github.com/) (`gh`) from a clone of this repository and work in bash and PowerShell. `N` is the pull request number and `vX.Y.Z` a tag.

### What triggers what

| Event | What happens | Release? |
| --- | --- | --- |
| PR opened or pushed | **Book CI** runs tests, release policy, lint and a full build. Its **Book release preflight** job is the gate. | No |
| Owner **Approve** review, or an owner `/release-book <SHA>` comment | **Approved book** re-checks everything and squash-merges the approved head. | Yes, through **Release** |
| Book CI or approval-signal run finishes, or the half-hourly scan | The controller looks for an approved PR it missed. It never approves anything itself. | Only if a valid approval exists |
| **Approved book → Run workflow** with `pr` | Same re-check for one PR. | Only if a valid approval exists |
| Push a tag, add a label, press **Merge** | Nothing in the release flow. | **No** |
| Push to `main` touching the manuscript, theme or tools | **deploy-swa** deploys the web edition. | **No** |

The last two rows matter: the web edition and the downloads are separate. Only the controller's squash-merge produces a tag and downloads.

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
5. Authorize **the exact head**. You wrote the PR, so GitHub will not let you approve it. Comment instead:

   ```sh
   gh pr comment N --body "/release-book $(gh pr view N --json headRefOid --jq .headRefOid)"
   ```

6. Watch it go through, normally within a few minutes:

   ```sh
   gh run list --workflow approved-book.yml -L 3
   gh run list --workflow release.yml -L 3
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

**Do not press Merge.** A manual merge publishes nothing (scenario 10). The pushes in step 1 change the head, so approve after them, not before.

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

An approval counts only for the head it was given on. A push after approval, a **Request changes** review or a dismissed review voids it. Nothing merges until you approve again (a new **Approve** review, or a new `/release-book <SHA>` with the new head SHA). An old SHA in an old comment is ignored.

### 5. The branch is behind `main`

The head must include current `main`. Update it and approve again:

```sh
gh pr update-branch N
```

### 6. Approved, but the PR is still open

Look at the latest **Approved book** run for the cause: failing preflight, a head that moved, a branch behind `main`, or a run that never started. Fix that, or just run the controller for this PR:

```sh
gh workflow run approved-book.yml -f pr=N
```

If the run died within a second with no steps, see [Runs that fail without starting](#11-runs-that-fail-without-starting).

### 7. Tooling, docs and workflow changes

A PR that touches only files outside the content allowlist (`tools/` other than `book.json` release keys, `.github/`, `theme/`, `infra/`, `README.md`, `RELEASING.md`, tests) is **tooling-only**. It needs no version bump, never releases, and the controller never merges it (`release_policy.py` prints `Tooling only`). Merge it yourself when CI is green. It can still redeploy the web edition if it touches a deploy path.

### 8. Mixed content and tooling

A PR that changes both content and tooling fails preflight with `Separate content from tooling: [...]`. Split it into two PRs: tooling first (merged by you), then the content PR.

### 9. Review copy (prerelease)

Use a prerelease version such as `3.2.0-rc.1` for a copy to share before the real edition. The PR still goes through scenario 1 and still merges into `main`. The release is marked pre-release, is never Latest and does not dispatch a web deploy. Because the text is on `main`, the next push-triggered **deploy-swa** builds it, so a prerelease does not keep text off the web edition. To graduate it, open a new PR that sets `3.2.0`, adds that CHANGELOG section and carries the evidence.

### 10. A manual merge by mistake

Pressing **Merge** on a content PR, or merging from the command line, bypasses the controller. The repository has no branch protection or ruleset, so GitHub allows it. The effects:

- The web edition deploys the new content (**deploy-swa** runs on the push).
- **No tag, no release, no downloads.** The site is ahead of the PDF and EPUB.
- Recovery refuses it: **Release** only recovers a PR that the controller itself merged.
- The version the PR carried is now on `main` unreleased. The next PR must advance beyond it (`PR must advance the version on main`), so that version number is skipped, and the next release is `vX.Y.(Z+1)` or higher.

Fix it with a catch-up PR. For example, if `main` carries `3.1.0` but the latest tag is `v3.0.0`:

1. Branch from `main`, set `version` in `tools/book.json` to `3.1.1` and add a dated `## [3.1.1] - YYYY-MM-DD` section to `CHANGELOG.md`. Move the unreleased `3.1.0` entries under it so the release notes describe the whole edition.
2. Check it: `python tools/release_policy.py --base origin/main` prints `v3.1.1`. Metadata, CHANGELOG and evidence are enough, because the reader-facing changes since the last stable tag are already on `main`.
3. Open the PR and authorize it as in scenario 1.

Version `3.0.0` was released this way: PR #17 turned the manuscript changes that were already on `main` into the third edition.

### 11. Runs that fail without starting

If **Approved book** or **Book CI** runs end in about a second with no steps and the annotation *"The job was not started because recent account payments have failed or your spending limit needs to be increased"*, GitHub Actions is blocked by billing, not by this repository. Fix **Settings → Billing and plans**, then run `gh workflow run approved-book.yml -f pr=N` for each affected PR.

### 12. The release failed after the merge

The PR is merged but there is no (or an incomplete) release. Find the recorded inputs in the controller's `merge` job:

```sh
gh run list --workflow approved-book.yml -L 5
gh run view <run-id> --log | grep "Release recovery inputs"
```

In PowerShell, use `Select-String "Release recovery inputs"` instead of `grep`. The line looks like `Release recovery inputs: {"pr": 17, "head_sha": "…", "base_sha": "…", "tag": "v3.0.0", "merge_sha": "…"}`. Then run **Release** with them:

```sh
gh workflow run release.yml -f pr=17 -f head_sha=<head_sha> -f base_sha=<base_sha> -f merge_sha=<merge_sha> -f tag=v3.0.0
```

Release checks the merge again. If the release is already complete, it is a no-op. If there is a lone tag, a draft, an incomplete asset set or a mismatched target, it stops with `inspect manually; no writes`. Look at the tag and draft on GitHub, decide what is safe, and see [Recovery and corrections](#recovery-and-corrections). Never move a tag or overwrite published downloads; the answer to a bad published file is a new patch version.

### 13. Only the deploy failed

The release is published and complete but the web edition is not live (or **deploy-swa** failed, or the Azure token was missing at the time). Do not re-run **Release**. Deploy the tag:

```sh
gh workflow run deploy-swa.yml -f ref=vX.Y.Z
```

If the run summary says the web edition was not deployed because `AZURE_STATIC_WEB_APPS_API_TOKEN` is missing, see [DEPLOY.md](DEPLOY.md).

### 14. Roll back the web edition

Downloads stay as they are; only the site changes:

```sh
gh workflow run deploy-swa.yml -f ref=v2.2.0
```

Only tags that contain `tools/build.py` (`v2.0.0` and later) can be built. The next push to `main` that touches a deploy path will redeploy `main`, so fix `main` too if the rollback is meant to last.

### 15. A published release is wrong

Do not edit the release or move its tag. Fix `main`, add a patch version through scenario 1 and release it. To withdraw a release completely, delete the GitHub release, then delete the tag with `git push origin :refs/tags/vX.Y.Z`. The version number stays used on `main`, so the next release must still be higher.

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
| `N content file(s) changed since vX.Y.Z without a release` | Scenario 10: content reached `main` without the controller. |
| `Site is not responding` | Scenario 13, then [DEPLOY.md](DEPLOY.md). |

### Before you open any PR

```sh
python -m unittest discover -s tests
python tools/lint_manuscript.py
python tools/release_policy.py --base origin/main   # content PR: prints the tag; otherwise "Tooling only"
python tools/build.py all                           # all editions, as CI builds them
```