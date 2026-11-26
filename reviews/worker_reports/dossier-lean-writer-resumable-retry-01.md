# Dossier Lean Writer — resumable technical retry 01

Task: `dossier-lean-writer-resumable-retry-01`  
Worker: **НОВЫЙ ЧАТ 1**  
Repository / base: `kentrap2011-hub/steam-kz-deals-2` / `main`  
Source PR: [#494](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/494), branch `fix/dossier-lean-writer-resumable-retry-20261125`  
**Source-only; no real writer dispatch/merge/semantic work or sandbox mutation. Independent security L3 required on exact final HEAD.**

## Verified incident and architecture preflight

- Real owner automatic run [#45628656098](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45628656098) irrevocably created historic one-use control ref `refs/heads/dossier-lean-auto-attempts/cdcdb4951e2fc98336729af75b954da4` at `6df354d024b0e3104ee408e815a1e5d141fb8e84`, then failed at the V2 destination-path layout. Original sandbox remains `d1b9a9e78dcde879a03370682ade4969763fd9d1`, 0/6 accepted. Path fix PR #490 is already on `main`; it is not additional authority. Earlier failed manual run `45540222575` also remains spent.
- Owner for trial selection, grants, trigger, retry, lease, completeness and persistence: **GitHub control plane** under `config/execution_ownership_contract.json` and the existing per-trial owner grant/Lean sandbox authorization. ChatGPT chat is developer/operator only. The existing `taste-steam-review-dossier-canonical-writer` Actions lock remains single-writer authority.
- This task does **not** create an independent scheduler, time-based polling, arbitrary backlog, new semantic work, daily quota or production owner. Reuse existing read-only receipt hint, owner source push and shared writer. Strict original V1/V2, historical source and Deep/production contracts remain unchanged.
- Original policy `automatic_retry_after_failure=false` and `per_trial_at_most_one_attempt=true` made a path/network failure permanently consume the trial's execution right; an owner-scoped immutable grant should instead remain the immutable *identity*, with separate technical execution attempts.

## Before/after transition table

| Concern | BEFORE (V1) | AFTER (versioned V2 source design) |
|---|---|---|
| Authorization | Owner-issued exact trial, AppID/edition/year/TTL, original Research/Assembly SHA; one-use attempt conflated | **Same immutable owner-issued exact trial**, SHA and sandbox; claim anchor never overwritten; separate append-only technical attempts |
| READY | Frozen six + terminal typed receipts + strict Lean validator | Same mandatory frozen readiness/receipt, unchanged, checked again before each attempt |
| Acquire | Create-only `dossier-lean-auto-attempts/<nonce>` ref, permanently spent | First anchor remains create-only; add `started` record to **same ref** using non-force Git fast-forward CAS plus readback; existing Actions shared writer concurrency lock |
| Running | One Actions ID, failure terminal | Exclusive active lease bound to actual trusted main source, Actions run ID, original claim, marker, sandbox, SHA digest and issuer |
| Prewrite failure | No retry even if zero bytes written | Append `retryable_failed` only after verifying frozen remote sandbox; later new reviewed code-fix/valid event may initiate a fresh attempt with unchanged grant |
| Uncertain postwrite | Prior implementation blocks with no recovery | Check current sandbox HEAD **first**; only exact single-parent N+N commit and strict independent readback can become `accepted`; conflicting partial/changed bytes => `blocked_invalid_input`, never an overwrite |
| Accepted | 6 docs + 6 isolated receipts, one-time | Same exact N+N acceptance then immutable `accepted` journal event; rerun verifies exact existing commit/readback and is **NOOP** |
| Paused/blocked | No distinguishable retry state | Owner policy pause list and terminal invalid/conflicting input or exhausted budget; neither secretly reauthorizes another trial |
| Historic six | Old claim spent, no retry | **Still OFF**. Owner must explicitly approve an exact old claim/run/frozen head/Research+Assembly hash-map migration after separate L3/source review |

V2 state: `READY → STARTED (exclusive lease) → RETRYABLE_FAILED → STARTED (new code/run) → ACCEPTED`, or `BLOCKED_INVALID_INPUT`; `ACCEPTED → verified NOOP`. An orphaned `STARTED` requires a 30-minute lease expiry **and** exact sandbox readback/reconcile; it is not a blind retry.

**Limits:** maximum 3 journal attempt indices per scoped grant; historic exhausted V1 claim is preserved and new migration starts at index 2 (its earlier manual/auto failures remain separately recorded). Minimum 2-minute backoff for ordinary receipt events; genuinely reviewed owner-main source change permits immediately attempting a different code SHA. A retry with the same reviewed source SHA is rejected, as are stale leases, spoofed GitHub actor/ref, wrong original grant/digest or branch, and mismatched accepted SHA. Source-triggered future recovery only selects an **unambiguous single** failed existing control-granted trial; multiple candidate retries fail closed pending an exact owner signal. No uncontrolled retry storm or hidden perpetual polling.

## Trigger, transport and safety

1. Trusted `.github/workflows/dossier-lean-writer-auto-ready.yml` uses reviewed `main`, read-only sandbox-ready `workflow_run` hint or real owner `main` push with **Git-object** proof of a changed *existing* writer/policy file. Workflow source/actor/repo/branch/run attempt verified.
2. `scripts/dossier_lean_writer_auto_ready.py` freezes source and verified owner-issued grant, exact AppID/title/edition/release year/Research+Assembly SHA/TTL/source, checks terminal typed receipts and old genuine owner failed-run proof as applicable. Real historic migration is disabled.
3. `scripts/dossier_lean_writer_retry_state.py` checks original one-add anchor, exact immutable source SHA hash, append-only single-parent `started`, `retryable_failed`, `blocked_invalid_input`, `accepted` events. Nonforce Git ref fast-forward + remote readback is the attempt CAS.
4. Unmodified `scripts/taste_steam_review_dossier_buffered.py::_drain_notes_v2_individual` rechecks the strict issuer/source/write authorization inside **the same** GitHub-owned shared writer, using exact absolute sandbox writer destinations; no custom validator bypass.
5. Stage exactly N dossier files and N bound accepted receipts; read back every byte, hash, Lean source/TTL/identity and original Assembly lineage; commit one sandbox transaction; one nonforce push; independent check from exact remote sandbox commit; then append terminal accepted journal. Any partial remote commit or competing file collision fails closed.
6. `config/dossier_lean_writer_auto_ready_v1.json#retry_lifecycle.paused_trial_ids` enables an owner-reviewed trial STOP. Strict/production Lean writer, normal reader and Deep flags stay OFF. No Scheduled Tasks or Research/Assembly execution.

**Historic grant migration (prepared only):** the immutable previous claim SHA `6df354...` and old Actions #45628656098 are *read-only evidence*. New source does not set `historical_live_retry_authorized` true; `historical_migration_grant` is `null`. A future owner-reviewed policy delta must bind trial ID, old claim SHA, failed run ID, frozen sandbox head, exact pair digest and explicit decision string. Neither PR merge nor CI turns this on automatically.

## Regression / CI evidence

Added `scripts/test_dossier_lean_writer_retry_state.py` (disposable real Git refs, append-only claim, separate failed/retry/accepted records, source-fix event discovery, stale lease, spoofed authority/digest, CAS race, terminal NOOP, attempt exhaustion); updated `scripts/test_dossier_lean_writer_auto_ready.py` for versioned policy and no historic silent migration. Existing `scripts/test_dossier_notes_v2_isolated_lean_acceptance.py` supplies the real disposable exact-six **6 dossiers + 6 receipts** writer/readback fixture, including path and collision negatives. The existing `.github/workflows/validate-dossier-research-notes-v2.yml` now runs the new fixture. Existing strict writer QA and other PR checks remain the canonical CI gates.

**At report creation:** GitHub Actions on source PR were running; do not infer a full pass from partially completed runs. Review the source PR's **exact final HEAD** required checks, verify every mandatory conclusion is success, and record exact run links during Director/L3. Offline synthetic tests authenticate neither the real GitHub owner identity nor a live 6+6 write. No live writer was dispatched in this task and **actual accepted remains 0/6**.

## Residual risks / review focus

- Material auth/retry ownership code warrants **independent L3 review on the final PR HEAD**; PR #490's earlier "без проверки" exception does not apply. Confirm actor/ref/Git history checks, owner-selector env safety, policy migrations, receipt provenance, CAS and reentrancy.
- Git ref history is append-only under this source implementation and fails closed on malformed events; actual GitHub permissions must prevent external writers from replacing/force-moving the control ref.
- A failed control-event network push with no readback may leave a `STARTED` lease; expiry plus sandbox reconciliation is required. No automatic time-based watchdog/poller is introduced.
- Multiple simultaneously eligible failed future grants on one owner code-fix event stop without choosing a new scope; a specific owner event must disambiguate. This preserves existing grant authority but does not claim unattended recovery of every possible simultaneous batch.
- Strict source proofs and sandbox N+N tests are necessary but not a live credential/security QA, semantic evidence-quality audit, canonical/Deep integration or production completion proof.
- Manual owner workflow_dispatch for original strict V1/V2 remains unchanged; never rerun old failed Action IDs.

## Short Director handoff

**Status at authoring: `BLOCKED_CI_PENDING_L3`**, source PR [#494](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/494). Confirm exact final HEAD CI; assign **new independent L3 auth/retry/lease security QA**. If L3 and all mandatory source checks pass, Director may accept source **without executing sandbox writer**; keep historical migration OFF. Only after source acceptance make a separate exact historic-six live recovery decision; NEVER restart old workflow run #45628656098 or reinterpret its spent claim.
