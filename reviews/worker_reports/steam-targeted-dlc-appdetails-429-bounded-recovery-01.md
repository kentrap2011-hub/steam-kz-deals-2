# Worker report — Steam targeted DLC appdetails HTTP 429 bounded recovery

- Date: 2026-11-04
- Task: `steam-targeted-dlc-appdetails-429-bounded-recovery-01`
- Source: `main`, source fix branch `fix/steam-targeted-dlc-appdetails-429-bounded-recovery-01`
- Trigger: GitHub Actions [run 41844517992](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41844517992), job `126624434359`, HTTP 429 for `appids=750920&cc=kz&l=english` on post-PR #388 main.
- Scope: existing `scripts/steam_targeted_paid_lanes.py::get_appdetails` and existing test `scripts/test_steam_targeted_paid_lanes.py`; no change to source universe, parent filtering, verified DLC membership, KZT gate, identity, workers, scheduling, Dossier, Deep, frontend or production payloads.

## Architecture preflight

- `config/execution_ownership_contract.json`: GitHub retains collection, retry and completeness ownership; interactive chat is developer only.
- `config/daily_execution_contract.json`: unchanged one daily cycle; no new stage, scheduler or queue.
- `config/mailing_policy.json#paid_discovery`: exactly vetted parent AppIDs and verified KZ DLC, no global DLC search, no premature top-100.
- `PROJECT_ROUTES.md#Steam KZ discovery — bounded paid source scope`: existing `steam-test.yml` PR regression versus real main collection separation.

## Implementation

- Shared `_SharedAppdetailsPacer` gates all parent and DLC requests with the existing 0.9-second spacing plus a global cooldown. Waiting releases the lock, checks the shared window again on wake, and does not hold the whole pipeline mutex across a sleep.
- Only HTTP 429 receives retries: at most **4 HTTP attempts per AppID** (original plus 3), with a **120-second total per-lookup pacing/retry deadline** and `timeout=25` on each HTTP attempt.
- Valid integer or RFC-compatible HTTP-date `Retry-After` is respected, capped at **60 seconds per event**; absent/invalid headers use deterministic **5/15/30 seconds**. Concurrent threads share cooldown, preventing unpaced retry fanout.
- 5xx, transport errors, exhaustion, missing/contradictory Steam identity, malformed relations, non-KZT paid data fail closed. No partial paid source or Dossier publication; prior valid output retention is still enforced by the existing collector.

## Tests / execution evidence

- Deterministic tests added for 429-to-200 exact URL/params/identity, persistent 429, total attempt/window caps, numeric/date/invalid/oversized Retry-After, unrelated HTTP 503 and connection timeout, and two concurrent callers sharing cooldown/pacing.
- **Verified implementation-code HEAD:** `3900eab1496349285320b555f4388ee69b861973`; PR #392 `steam-test.yml` [run 41849535988](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41849535988), regression job `126641800306` SUCCESS; `scripts/test_steam_targeted_paid_lanes.py` **10/10 PASS** in logs. The `collect` job was correctly SKIPPED for the PR.\n- Also SUCCESS: site-task registry [41849535957](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41849535957), backlog dispositions [41849536054](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41849536054). The final documentation-only HEAD must be rechecked after this report update.
- Local checkout is unavailable in the current runtime: direct GitHub clone failed due to DNS resolution of `github.com`. No local full-suite execution is claimed.
- A PR green regression is not live Steam rate-limit evidence; only a post-merge full normal `steam-test.yml` run on current main can establish fresh paid-source and Dossier worker-index/binding acceptance.

## Remaining handoff

Director: inspect the single source PR at its exact final HEAD and actual CI; apply existing L3 merge safety protocol. No self-merge, no new QA worker task or recurring pipeline. After merge, initiate/verify **one actual existing main workflow run** using GitHub `Actions → Steam KZ production shortlist → Run workflow → main` when the workflow is dispatchable. Verify collector → mailing → pre-AI → new Dossier index and exact worker-prompt bindings. A failed live run remains fail-closed, not silently successful.
