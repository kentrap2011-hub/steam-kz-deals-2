# Taste Chernobylite real canary execute 01

- Task: `taste-chernobylite-real-canary-execute-01`
- Mode: `ACCEPTANCE / ONE REAL SEMANTIC CANARY`
- Authorized subject: `Chernobylite Complete Edition` / AppID `1016800` / `App_1016800`
- Lifecycle: `needs_followup`
- Final status: `needs_followup`
- Last checkpoint UTC: `2026-09-09T17:14:00Z`
- Next action: rebuild the one-AppID current-main preparation against the then-current live `gaming_taste_live.json`, freeze the new exact tuple, and only if that profile binding matches live proceed to the canonical acceptance gate. Do not reuse the stale prepared profile SHA from this run.

## Current-main preflight — completed read-only

- GitHub Actions run: `34381380867`.
- Job: `102566817948` (`prepare-one`).
- Artifact: `10115975634` / `taste-current-main-canary-1016800-34381380867`.
- Run head/current-main at preparation: `7ae4cb9e004b21a7631d3c80966f0568bbc80ed5` = resolved `origin/main`.
- Run result: `completed / success`.
- Repository clean before/after; git diff exit code `0`.
- Harness elapsed: `0.547s` (projection `0.27s`, payload `0.008s`).
- Queue cardinality: exactly `1`; decision: `semantic_queue_row`; only AppID `1016800` / `App_1016800`.
- Semantic/canonical writes during preparation: none.

## Frozen prepared tuple

- AppID: `1016800`.
- Taste subject key: `App_1016800`.
- Title: `Chernobylite Complete Edition`.
- Profile identity: `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json`.
- Prepared profile blob SHA: `191b6d6c5dec2f9ef2976517f301528740f9bec2`.
- Taste model version: `taste-v3`.
- Taste semantics SHA256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.
- Taste fingerprint: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`.
- Candidate-context SHA256: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`.
- Source mailing timestamp: `2026-09-08T20:46:16.637935+00:00`.
- Candidate provenance: `storebrowse_basic_info`.
- AI reason: `taste_cache_key_missing`.

## Mandatory STOP gate — failed before semantic execution

The prepared profile binding does **not** match the current canonical live Taste profile:

- prepared tuple profile blob SHA: `191b6d6c5dec2f9ef2976517f301528740f9bec2`;
- current live `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json` blob SHA observed after preparation: `9c9ef7cdf2d705b8dd10196cec654f16e04341e4`;
- exact match: **false**.

Per `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_EXECUTE_01.md`, this mismatch is an unconditional stop. Therefore the canonical queue/binding acceptance gate was not advanced further, because semantic execution is forbidden once the earlier live-profile gate fails.

## Semantic / Scheduled Task containment

- Existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` was **not mutated**.
- It was **not triggered**.
- No temporary semantic schedule was installed.
- No schedule restoration was necessary because the task was never changed.
- Semantic results generated: `0`.
- Second game/result: `0`.
- Canonical Taste ingest attempts: `0`.
- Receipt/cache/overlay/queue were not mutated by this acceptance worker.
- No full production rebuild.
- No historical workflow rerun.
- No manual SHA substitution.
- No weakened validation.
- No backlog widening.
- No System Audit.

## Temporary preflight wrapper cleanup

Because the connected GitHub tool cannot dispatch the permanent `workflow_dispatch` preflight directly, a one-off push-triggered read-only wrapper was used solely to invoke the existing `scripts/build_taste_current_main_canary.py` harness for AppID `1016800`. It had `contents: read`, performed no semantic/ingest work, and was removed after the mandatory gate failed.

- Temporary workflow removed: `.github/workflows/taste-current-main-canary-acceptance-once.yml`.
- Cleanup commit: `bea0c7a4a59377fe710d2ecd0786869af8091d2e`.

## Conclusion

`needs_followup`

Reason: the fresh prepared Chernobylite tuple is bound to profile blob `191b6d6c5dec2f9ef2976517f301528740f9bec2`, while the current live canonical Taste profile is already blob `9c9ef7cdf2d705b8dd10196cec654f16e04341e4`. The mandatory pre-semantic gate therefore prohibits running the real semantic canary from this tuple.
