# TASK — architecture-recommendations-followup-01

Status: `queued_later_do_not_start_now`
Mode when authorized: `IMPLEMENT_IN_SMALL_STEPS`

## Source

Accepted architecture report:
`reviews/worker_reports/code-architect-system-review-01.md`

Final status:
`review_complete_recommendations_ready`

## Goal

Later work through the accepted architecture recommendations without disrupting current operational work.

## Recommended order

1. Document the canonical production entry points and clearly label legacy/secondary execution paths.
2. Replace the Steam source-text/`exec` loading boundary with a normal importable Steam core while keeping `steam_partial_publish.py` as the separate failure-isolation layer.
3. Add direct deterministic tests for the real Steam runner boundary when doing that refactor.
4. Audit old Steam/visual execution paths and retire or clearly label them after confirming consumers.
5. Add clear section anchors/headings to large cohesive coordinators where navigation is difficult; do not split files merely because they are large.
6. Later extract deterministic policy logic from oversized GitHub Actions heredocs where it improves testability; keep GitHub Actions as orchestration.

## Explicit non-goals

- Do not mass-reorganize the `scripts/` tree.
- Do not split `build_final_visual_payload.py` or `director_orchestration_controller.py` merely because of file size.
- Do not start any of this work now.
- Current priority is launching the normal ChatGPT/Taste game-evaluation mechanism.

## Execution rule later

Handle recommendations in small independently reviewable changes. Before each structural change, confirm it still provides a material benefit versus implementation cost and does not interfere with production behavior.

Expected follow-up report when eventually authorized:
`reviews/worker_reports/architecture-recommendations-followup-01.md`
