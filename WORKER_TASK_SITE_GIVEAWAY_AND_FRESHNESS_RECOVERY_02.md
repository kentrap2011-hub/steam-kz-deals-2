# ЧАТ 1 — ДОБИВАЕМ БЕСПЛАТНЫЕ ИГРЫ И FRESHNESS САЙТА

Task ID: `site-giveaway-and-freshness-recovery-02`
Mode: `IMPLEMENT / DIRECT CONTINUATION`

## Background

Continue directly from:
`reviews/worker_reports/site-current-games-and-free-game-recovery-01.md`

Already completed and DO NOT repeat:
- original visual-build blocker diagnosed and repaired;
- `Build daily visual payload` now succeeds;
- `Deploy visual mailing` now succeeds;
- a real GitHub Pages artifact is deployed;
- 115 non-giveaway entries are present in the deployed payload.

Remaining proven production gaps:
1. canonical giveaway snapshot is stale across the 2026-09-10 Epic rotation;
2. current giveaways `Astral Ascent` and `Luftrausers` are absent from deployed giveaway block (`state=unavailable`, `games=[]`);
3. deployed publication freshness is `degraded/no_fresh_build` with reason `visual_source_history_mismatch`.

## Goal

Finish the SAME user goal end to end:
- restore canonical giveaway refresh so current active/eligible giveaways are represented;
- repair the exact `visual_source_history_mismatch` freshness binding if it is a real defect;
- rebuild and deploy;
- prove the final deployed Pages artifact contains the current eligible giveaway entries and is certified fresh by the project's own freshness contract.

Do not return to Taste queue work until this is resolved or a genuine external blocker is proven.

## First action — REPORT FIRST

Create/update:
`reviews/worker_reports/site-giveaway-and-freshness-recovery-02.md`

Record UTC, exact inherited known facts, current giveaway snapshot state, current freshness state, and first investigation action.

## Workstream A — giveaway source freshness

Find why `data/production/giveaways/v1/current.json` failed to refresh after the 2026-09-10 15:00Z Epic rotation.

Trace only the canonical giveaway producer/scheduler/source path needed to answer:
- what normally refreshes this file;
- whether that refresh ran;
- if it failed, first real error/root cause;
- if it did not run, why not;
- whether the producer currently sees `Astral Ascent` and `Luftrausers` as active/eligible for the configured KZ rules.

Repair the smallest directly involved cause.

Do NOT hardcode giveaway titles into site output.
Do NOT weaken giveaway eligibility/region validation.

## Workstream B — publication freshness binding

Diagnose `visual_source_history_mismatch` from deploy run `34498439445`.

Determine whether the mismatch is:
- stale/incorrect provenance history produced by the repaired build path;
- a deploy binding bug;
- a legitimately stale source condition caused by giveaway freshness;
- or another directly proven cause.

Repair only if the invariant is incorrectly failing for a truly current build. Do not bypass or weaken the freshness contract.

## End-to-end validation

Prove all of the following on current main/state:
1. canonical giveaway snapshot refreshes to the current active rotation;
2. current eligible giveaways are exact and source-backed;
3. visual payload build succeeds;
4. freshness receipt/binding is accepted as fresh, not `degraded/no_fresh_build`;
5. deploy succeeds;
6. exact deployed Pages artifact contains the current giveaway games;
7. the 115+ normal publishable entries remain intact according to current canonical rules;
8. no Taste semantics/queue/cache/Scheduled Task changes occur;
9. no new Taste semantic batch starts.

If the public site URL itself can be fetched, verify it too. If not, verify GitHub Pages deployment plus exact uploaded artifact and state this limitation precisely.

## Failure handling

If failure remains, self-diagnose the exact first real blocker in the same report. Do not blindly rerun production. Record what changed, what did not, whether the site is still stale/degraded, and the smallest next action.

## Final statuses

Use one of:
- `complete_site_fresh_and_current_giveaways_visible`
- `complete_site_fresh_current_giveaway_legitimately_none`
- `waiting_user_dispatch`
- `failed_closed_root_cause_proven`
- `failed_closed_root_cause_unknown`
- `blocked_external`

## Stop condition

Stop only after current giveaway state and publication freshness are both resolved/verified, or a genuine external blocker is recorded. Do not start Taste queue ordering or semantic backlog work afterward.
