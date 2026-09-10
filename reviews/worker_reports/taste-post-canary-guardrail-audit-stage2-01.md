# Taste Post-Canary Guardrail Audit — Stage 2

- task_id: `taste-post-canary-guardrail-audit-stage2-01`
- lifecycle: `in_progress`
- started_utc: `2026-09-10T06:48:37Z`
- completed_checks: `2/7`
- next_action: `check 3`

## Checks

1. Current one-game preparation freezes the live profile from an immutable repository commit and verifies exact content: `PASS`
   - `scripts/build_taste_current_main_canary.py` treats `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json` as the canonical authority required by policy, not committed `taste_projection.json`.
   - `freeze_current_live_profile()` resolves canonical `main`, fetches `gaming_taste_live.json` with `?ref=<resolved commit>`, validates decoded bytes against the advertised Git blob SHA, records SHA256 and byte count, and writes an immutable commit-pinned binding/snapshot.
   - `validate_frozen_profile_binding()` rechecks byte count, Git blob SHA and SHA256 against the frozen snapshot.
   - Predecessor implementation report confirms the stale committed projection authority was deliberately removed from this preparation path and the focused current-main validation proved the exact frozen blob propagated through projection, payload and prepared tuple.

2. Parallel profile changes are handled safely with bounded fail-closed retries: `PASS`
   - The same `freeze_current_live_profile()` performs head-before / commit-pinned file fetch / head-after confirmation. If head changed before freeze completion, that candidate is discarded and the next attempt starts from the newer head.
   - Once a stable head is confirmed, all later preparation is bound to the immutable frozen snapshot; a later live-profile change cannot rewrite or mix the tuple.
   - `PROFILE_FREEZE_MAX_ATTEMPTS = 3`; churn across all attempts raises a retry-later `CanaryError` and stops rather than looping indefinitely.
   - Predecessor focused tests explicitly passed for update-before-freeze selecting the newer state, update-after-freeze preventing mixed versions, and continuous churn failing closed after the bounded attempts.
