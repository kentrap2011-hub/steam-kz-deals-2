# WORKER TASK — Taste Steps 1–3 Production Materialization Acceptance 01

## Task ID
`taste-steps-1-3-production-materialization-acceptance-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`

## User goal — authoritative
Do not move away from Taste until the accepted Steps 1–3 semantics are materialized through the canonical production path far enough that the user can perform a meaningful real-site/mobile verification.

The independent Taste Review accepted the semantic boundary but explicitly found that the current persisted ranking/output is stale pre-change data and current semantic materialization is degraded. The purpose of this task is to close that observability/materialization gap, not to start unrelated product work.

## Required sources
Read at minimum:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `USER_TASTE_PROFILE.md`
- `reviews/taste_reviews/taste-steps-1-3-current-review-01.md`
- `reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
- `reviews/worker_reports/play-role-and-start-priority-implement-01.md`
- `reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
- `reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
- current canonical Taste/semantic producer, queue, runtime, final payload and ranking routes/contracts on `main`.

## Part A — implement the two remaining reviewer maintenance recommendations

### A1. Positive-exception regression controls
Add bounded durable regression coverage for:
- `Batman: Arkham` as a replay-positive anchor;
- `Red Dead Redemption 2` as a strong open-world positive anchor.

The regression purpose is to prevent future negative-risk logic from converting generic labels such as open world, directionlessness, complexity or repetition into an automatic personal dislike without title-specific/user-specific evidence.

Do not hardcode broad genre positivity and do not create new ranking bonuses.

### A2. Role/start calibration revalidation provenance
Add the smallest durable maintenance guard so static title-specific role/start calibrations are explicitly tied to the current canonical taste-profile evidence and are flagged/revalidated when `USER_TASTE_PROFILE.md` materially changes.

Requirements:
- provenance/revalidation guard only;
- no new ranker;
- no price/discount/wishlist influence on role/start;
- do not turn reviewer calibrations into timeless genre rules;
- fail visibly in validation if a material profile change makes the calibration provenance stale, rather than silently continuing forever.

## Part B — close production materialization / acceptance dependency

### B1. Respect canonical semantic runtime ownership
The current semantic production state was previously degraded by unresolved evidence/semantic backfill.

You must determine the current canonical runtime/queue truth from current `main` and current authoritative execution evidence.

Hard rules:
- do NOT create a second semantic scheduler;
- do NOT create a chat-owned production queue;
- do NOT manually process hundreds of semantic items one-by-one;
- do NOT fabricate semantic completion;
- do NOT bypass completeness/fail-closed gates merely to get a visible result;
- preserve GitHub-owned production/runtime ownership.

If the canonical semantic runtime is already operating, use/observe the normal flow and its durable output.

If the canonical runtime identity/health is still genuinely blocked on missing user evidence or an unavailable external runtime, stop with the exact bounded gate and report `needs_user_evidence` or `blocked_semantic_runtime`. Do not invent a parallel replacement.

If a small in-scope defect prevents the existing canonical runtime from progressing, fix only that defect and revalidate. Do not redesign the semantic system broadly.

### B2. Regenerate only through the canonical production path
Once the semantic scope is legitimately complete enough for the normal final producer to proceed:
- regenerate current canonical pre-AI/final visual/ranking output through the normal production route;
- prove the resulting artifact is post-Steps-1–3, not the stale schema-3 / older persisted snapshot identified by the Taste Reviewer;
- publish/deploy only through the repository's existing canonical deployment path if publication is part of the normal accepted route.

Do not manually patch generated production rows to manufacture desired control results.

## Integrated control acceptance

Run one bounded integrated control snapshot against the genuinely regenerated current output for all ten controls:

1. `Sifu`
2. `High On Life`
3. `Amnesia: The Bunker`
4. `Terminator: Resistance`
5. `Tails of Iron 2`
6. `Trine 4`
7. `TMNT: Splintered Fate`
8. `HighFleet`
9. `Batman: Arkham`
10. `Red Dead Redemption 2`

Required checks include:
- `HighFleet` must no longer reproduce the stale pre-change `strong / no-risk / БРАТЬ СЕЙЧАС` treatment; its accepted confirmed-negative semantics must be materially visible/fail closed as appropriate;
- calibrated role/start fields for Sifu, High On Life, Amnesia, Terminator, Tails of Iron 2, Trine 4 and HighFleet must be present/consistent where current canonical identity resolves them;
- `TMNT: Splintered Fate` remains conservative/unresolved unless genuine current evidence supports more;
- Batman/RDR2 remain positive exceptions against coarse generic-risk inference;
- commercial bridge rows, if present, preserve real Taste state and do not fake moderate/strong fit;
- warnings/risks/provenance remain visible;
- no new ranking-weight changes beyond already accepted semantics.

If one of the ten controls is absent from current commercial/source scope, record that as `not_currently_materialized` with the exact reason; do not fabricate a row. Deterministic fixture/control coverage can supplement absence but cannot be represented as live production evidence.

## User verification gate

Only report `complete_ready_for_user_verification` if:
- reviewer recommendations A1/A2 are durably implemented and validated;
- current production output has been legitimately regenerated through the canonical route;
- integrated control acceptance is green or has only truthful current-scope absences;
- the published/current site artifact is demonstrably the regenerated post-Steps-1–3 output.

Even then, do not claim final user-visible closure. Director must ask the user for real-device/mobile verification.

## Allowed statuses
Exactly one:
- `complete_ready_for_user_verification`
- `blocked_semantic_runtime`
- `needs_user_evidence`
- `needs_followup_fix`

## Required report contents
1. Status.
2. Exact A1 regression implementation and results.
3. Exact A2 calibration-provenance/revalidation implementation and results.
4. Current canonical semantic runtime identity/health and evidence.
5. Proof no second scheduler/parallel queue/manual bulk semantic processing was introduced.
6. Exact current semantic completion/materialization state.
7. Exact regeneration/deploy runs/commits if reached.
8. Integrated ten-control table with current-output evidence vs deterministic-only evidence clearly separated.
9. Explicit HighFleet result.
10. Whether the current site is ready for user mobile verification.
11. Any remaining exact blocker/user action.

## Boundaries
- No ITAD/giveaway implementation.
- No unrelated backlog work.
- No new semantic scheduler.
- No manual bulk semantic processing.
- No fake completeness.
- No Taste policy redesign unless a genuine blocking regression from the already accepted Steps 1–3 is found; if so, stop as `needs_followup_fix` rather than silently inventing policy.

## Completion
Save exactly:
`reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`
