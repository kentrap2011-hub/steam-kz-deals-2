# Worker report — first real 18-game Research shadow sandbox authority (ЧАТ 1)

Task ID: \`dossier-shadow-first-real-18-research-sandbox-authority-01\`
Source: \`kentrap2011-hub/steam-kz-deals-2\`, \`main\` (initial observed head \`8e857c4519970c8d2164249483c7b686fd4a0a81\`)
Branch: \`implement/dossier-shadow-first-real-18-research-sandbox-authority-01\`
Status: **implementation PR review; \`sandbox_research_invocation_ready=blocked\`**.

## Exact scope and provenance

- Accepted Director selection from \`reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json\`: original **six indivisible three-game groups 3, 8, 13, 15, 18, 20**, exactly **18** fixed AppIDs in their original item order. No substitute games, cohort resampling or separate normal backlog scan.
- Historical accepted baseline HEAD: \`95a4bf4990a60082ecb3302da5bc7f23b618d93e\`; manifest Git blob \`ef40fc186aabc79dfd24c72864dbe43817a56039\`, audit Git blob \`8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b\`.
- New \`scripts/dossier_shadow_research_trial_prepare.py --propose-buffer\` creates a **proposal only** from these immutable inputs and invokes the already accepted PR #201 strict baseline preflight on **only six** original writer groups in a marked OS-temporary detached Git replica. It emits metadata/hashes only; does not publish or grant authority.
- Proposed immutable buffer contains original descriptor Git SHA, original cache path, original strict writer Git commit, raw Git blob and canonical cache SHA-256, original recorded year, exact historical audit line SHA-256, and an exact full Research assignment, plus pinned trial contract/Research schema/new sandbox prompt Git blobs.
- Real evidence and user feedback are **not** included in these public proposal/authority metadata; never publish raw reviews, author identities, user IDs or profile URLs.

## Implementation / security boundaries

- \`config/dossier_shadow_research_trial_contract_v1.json\` is **separate, explicit, sandbox-only** and remains **inactive**. Existing production two-stage gates are untouched and remain \`active=false\` and \`authorized_for_semantic_execution=false\`; active one-stage Dossier stays sole canonical authority.
- \`scripts/dossier_shadow_research_trial.py\` reads only an **already published** exact immutable GitHub-prepared \`reviews/dossier_shadow_offline/trials/<trial_id>/research_buffer.json\` from the **actual parent** of a **single-parent, marker-only create-only** sandbox Git commit. A Director decision or stdout proposal never counts as a frozen marker.
- Exact original 6×3 membership/group SHA, historic accepted state and writer audit line, cache Git blob and SHA, Research schema, original immutable research assignment, trial prompt and contract Git blobs are checked at the frozen parent. No caller-supplied alternate group, recovery or second queue is accepted.
- \`validate_candidate\` reuses canonical \`validate_research\` and \`validate_physical_sources\`, including all twelve dimensions, source privacy and exact identity. A **new factually grounded original-work year different from the OLD cache claim** produces \`legacy_original_year_conflict_needs_comparison_adjudication\`; it is **not rewritten to match** old cache. This conflict must block strict comparison for that item/group until resolved by quality reviewer, but not other independent groups.
- Research transport may only be an isolated \`reviews/dossier_shadow_offline/trials/<trial_id>/research/...\` **single-create-only-file original Git commit**, on the marker first-parent chain. Replays/overwrites/collisions, unapproved paths, altered original bytes or additional \`data/production\` writes fail closed. Provenance contains actual raw SHA-256, Git blob, Git commit and canonical JSON SHA; merely submitted \`not accepted\`.
- No calls of real semantic research were made, no results were published in Git, no production/cache/live inbox/one-stage/Deep/Fast/ranking/website/scheduler or \`manual-shell-write.yml\` changed.

## Gate and launch blockers — not papered over

\`sandbox_research_invocation_ready=blocked\`; **actual immutable sandbox Git marker commit: ABSENT**, **published Git-authorized freeze/buffer: ABSENT**, **independent A/B vs C reviewer roles: NOT FINALIZED**, **separate Director acceptance: NOT YET CONFIRMED**, **sandbox semantic execution gate: false**.

The user approved attempting the experiment, but the existing Director decision expressly records that trial authority and independent review were not finalized. This implementation PR cannot mint a self-authorizing marker, declare quality acceptance, or turn on an inactive production prompt. Even valid local/proposal JSON or green synthetic tests **must** leave launch blocked.

## Bounded acceptance and independent tests

- PR-only \`.github/workflows/validate-dossier-shadow-research-trial.yml\` uses \`permissions: contents: read\`, full history, no push, schedule or workflow dispatch, no production writes. It verifies original strict writer receipts for **the exact six approved groups**, validates the proposed 18-item structure, compiles and runs disposable Git tests, and asserts that missing authority remains blocked.
- \`scripts/test_dossier_shadow_research_trial.py\`: actual Git single-parent marker, unexpected marker files/content/path, missing/unapproved buffer, exact group/member order and drift, Research strict all-12-dimensions/privacy/binding, original-year mismatch typed diagnostic, original create-only Git candidate with canonical/raw/blob hashes, collision, postsubmission overwrite and unauthorised production extra file.
- No invented speed data. Actual per-item/stage elapsed times can only be measured during separately authorized future real Research/Assembly execution.
- **CI result:** see PR checks; a successful proposal or negative synthetic test does not count as a real pilot launch.

## Minimal next authorized route

1. Director reviews and accepts implementation PR (without promoting trial to production), ensures the independent reviewer A/B and separate C roles and explicit failure/quality handling are approved.
2. GitHub-owned control plane, **not** ChatGPT's semantic worker, commits exactly the prepared six-group Research buffer and its immutable parent-bound original receipts/schema/prompt, then creates a **separate single-parent marker-only Git commit** on an isolated nonproduction branch. Revalidate exact marker-parent bindings and check paths cannot enter live inbox. Do **not** treat this report/decision or an uncommitted proposal as a marker.
3. Only after explicit standalone trial-gate approval and required reviewer appointments, user manually initiates **a new single-use semantic worker chat** with the exact GitHub-issued \`shadow_marker_commit\` and \`research_buffer_path\`, using the frozen \`config/dossier_shadow_research_trial_semantic_prompt.md\`. Worker traverses 18 items in original order, publishes create-only isolated package evidence only, no sibling acknowledgement wait or auto retry. Send exact Research commits to independently authorized Chat 2 Assembly sandbox and then human-blind quality comparison. **No Scheduled Tasks**.

**Result count as of report authoring:** 0 real Research calls, 0 Research packages, 0 Assembly packages, 0 canonical acceptances. No PR self-merge. \`CURRENT_TASK.md\` intentionally not rewritten: it is a large concurrent multi-worker handoff and changing it here risks erasing other active work.
