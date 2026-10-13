# Worker report — Deep versioned history first core 01

**Task:** `WORKER_TASK_DEEP_VERSIONED_HISTORY_FIRST_CORE_01.md`  
**Worker:** new physical CHAT 1  
**Repository / base:** `kentrap2011-hub/steam-kz-deals-2` / `main`  
**Implementation branch:** `implement/deep-versioned-history-first-core-01`  
**PR:** #222, open draft, **not merged**  
**Status:** `implementation_complete_ready_for_director_review_producer_only`  
**Checked:** 2026-10-13.

## Gate and architecture

Read latest `CHAT_PROTOCOL.md` (START), `CHAT_CONTEXT.md`, task file, relevant `PROJECT_ROUTES.md` and `CURRENT_TASK.md`; checked GitHub-owned Fast/Dossier/Deep responsibilities in `config/execution_ownership_contract.json`, `config/progressive_pass2_contract.json`, `config/progressive_personalization_contract.json` and frozen Deep two-stage contract names. GitHub still owns scope/order/current semantic compatibility/recovery/attempt counts/persistence/publication; interactive development does not perform production Deep work, and no new scheduler, retry allowance or queue owner was created.

## Delivered producer implementation

1. `scripts/progressive_deep_history.py`: additive completed-history V1 with stable completed-revision IDs, full copied accepted result including verdict, positive/negative evidence, score findings, original immutable work/authorization provenance, actual accepted analysis timestamp and content-addressed pinned profile version when attested. Existing V2 successful root and `revision_history[].state` remain readable without destructive rewriting; unattested legacy content is marked unknown.
2. `scripts/progressive_pass2.py`: canonical accepted-result, terminal failure and consumed-contract-failure transitions all preserve earlier successful revisions in `entries[family_id].completed_versions` even when a changed profile/semantic generation replaces the active root. A failure does not fabricate a new success or clear old completed history. Existing one-attempt and explicit recovery authorization remain in force; migration overlap is deduplicated by accepted revision identity.
3. `scripts/build_progressive_pass2_work.py`: current **eligible** Deep work prioritizes exact-game never-successful history first; among games with a prior success, oldest **last successful** accepted UTC first, stable AppID/subject/family tie breaker. Never-analyzed tie order retains existing semantic score; failures/retries are not treated as successes, stale history does not authorize any attempt and wrong-edition results are excluded. Adds bounded, unique-game version counts into the prepared manifest scope.
4. `scripts/progressive_personalization.py`: producer attaches historical latest-completed fallback (outcome, original evidence, accepted timestamp, exact identity, profile-version content ID, source commit when attested) alongside `current_compatible`, current/outdated/never state and reason. These **do not** enter the effective/current Deep taste verdict or ranking. Producer statistics expose per-profile unique-game counts plus current-compatible count, older-history-only count, never-completed count, current target and remaining target. The 30 legacy reanalysis and 43 score-explainability migration targets **cannot be added** to each other: groups may overlap; counts are deduplicated per exact game identity.
5. Canonical contract revisions: `config/progressive_pass2_contract.json` version **14→15**; `config/progressive_personalization_contract.json` version **10→11**; explicit nested history contract `PROGRESSIVE-DEEP-COMPLETED-HISTORY-V1`. Existing PASS2 state V2 and immutable work/result transport remain compatible. `PROJECT_ROUTES.md` now locates the history implementation and tests.

## Acceptance evidence

- `scripts/test_progressive_deep_versioned_history.py`: byte-level punctuation change; same content at newer Git commit; success across multiple generations; success followed by incomplete; exact profile pin; oldest-last-success ordering; never-first; out-of-scope game/edition; overlapping legacy/score migration revisions; stale success not a current score; bounded persisted-state inspection.
- `scripts/test_semantic_queue_priority.py`: exact AppID/subject, no dropped eligible items, stable identity ties, existing semantic-score factors (never cohort), no change to eligibility.
- Existing core/integration/negative-assessment/profile-equivalence/staging/site regressions run by the existing `Validate Progressive PASS 2 core` workflow.
- PASS2 `38416076808` — **passed** after isolated regression corrections, all steps including real current projection accounting.
- Site publication resilience `38416077090` — **passed** after correcting compatibility with isolated projection fixtures.
- Deep Stage1 migration preparation `38416077052` — **passed**.
- Validate backlog dispositions `38416077228` — **passed**.
- Final added bounded real-state test triggered a subsequent CI run; use latest workflow check on PR #222 for final status.

## Historical observations and bounded limitations

The task cites **47 completed Deep at 2026-09-30** and **8 current-compatible at 2026-10-13** from different snapshots. Those figures indicate that current-compatibility filtering can hide older completed work; **they do not alone prove deletion or establish that all 47 original rows remain in present canonical state**. The new selector considers V2 root, V2 revision-history and forward V1 completions. It does not invent successes from missing/unverified prior commits. An optional historical backfill of absent old snapshots must first prove exact accepted Git provenance and cannot run as a broad semantic retry.

The existing canonical `PROGRESSIVE-PROFILE-PIN-V1` supplies an immutable profile **commit SHA, blob SHA and content SHA** but **no verified Git source commit timestamp**. Therefore `current_profile_version_at_utc` and `last_completed_profile_version_at_utc` are **null** rather than incorrectly equated with Deep accepted time, site publication time or a fresh commit. This remaining dependency must be filled by an explicit GitHub-owned, Git-proven provenance path before the later site phase can display a truthful profile update **date**. Content version identity is already available and a byte-identical newer commit does not create a new content version. The original commit SHA remains preserved separately.

This phase deliberately does **not** modify `web/**`: current production site may still show only compatible results until a separately approved site-card/statistics implementation consumes the new producer fields. No bulk rerun, no direct production state overwrite, no new Scheduled Task, no Fast/Dossier changes, no two-stage activation/cutover and **no self-merge**.

## Director handoff

Review PR #222 and complete the next bounded site phase only after approving the producer contract. The next task should explicitly render stale historic Deep as **OUTDATED** alongside actual last successful Deep UTC and verified current profile version date (if available), and render versioned counts in Statistics without ranking stale evidence. If historic source-commit timestamps or absent legacy rows are required, implement/prove those as GitHub-controlled provenance migration rather than a fabricated date or reset of the Deep retry budget. Stop this worker after final report.
