# Worker report — Dossier async bridge proof gate decouple 01

- **Physical worker:** НОВЫЙ ЧАТ — ЧАТ 1.
- **Task:** `WORKER_TASK_DOSSIER_ASYNC_BRIDGE_PROOF_GATE_DECOUPLE_01.md`, ID `dossier-async-bridge-proof-flag-fix-01`.
- **Repository/base:** `kentrap2011-hub/steam-kz-deals-2` / `main`; PR creation base SHA `6bdd2a26f408d52eb533e1ef2135347f11956f57`.
- **Branch:** `fix/dossier-async-bridge-proof-gate-decouple-01`.
- **PR:** [#193](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/193), **not merged by worker**.
- **Mode:** GitHub-owned inactive offline fixture only; no live semantic execution, production activation, scheduled task or actual canonical Dossier write.

## START and architecture authority

Read current `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, the exact assigned task, Dossier route in `PROJECT_ROUTES.md`, relevant reports for merged PR #187, #188 and #190, the four real two-stage interface/staging/async/final contracts, `config/execution_ownership_contract.json`, the existing bridge/gate, the actual PR #190 joint suite, existing bridge tests and PR-only CI. Read `CURRENT_TASK.md` to avoid overwriting independent current work.

Preflight: `config/execution_ownership_contract.json` keeps production validation, strict canonical acceptance, ordering, persistence and retry authority in GitHub. `config/dossier_two_stage_final_acceptance_bridge_contract.json` and `config/dossier_two_stage_interfaces_contract.json` authorize only inactive offline fixtures here, not production cutover. This patch adds no work/queue/checkpoint/receipt, GitHub production workflow consumer, scheduler, separate writer or control-plane role for ChatGPT.

## Root cause and minimal correction

Merged PR #188's `scripts/dossier_two_stage_final_acceptance.py::offline_gate` incorrectly tested `cross_pr_research_original_year_fix_verified is not False` alongside the actual authority gates. This made factual proof metadata `true` disable even a safe, explicitly marked disposable-Git fixture. PR #190's report isolated this coupling; it was **not** evidence of live activation.

The guard now requires `type(spec.get("cross_pr_research_original_year_fix_verified")) is bool` — exactly boolean `false` or `true`, no absent/null/zero/one/string/array/object values. The independent guard retains `active is False`, `authorized_for_canonical_ingest is False`, `executable_in_production is False`, the precise existing shared writer domain and an explicit `offline_fixture=True`. The latter still requires an isolated Git working repository under system temp with a `.dossier-final-offline-fixture` marker, not the current checkout. Default/live entry is refused before any writer action.

After the existing real cross-PR direct joint tests passed on the new guard while proof remained `false`, the contract proof was changed to **`true`**, strictly as evidence metadata. The live contract fields remain **all `false`**.

## Modified implementation / regression scope

1. `scripts/dossier_two_stage_final_acceptance.py`: one narrow type-check correction to `offline_gate`; no change to strict group validator, existing buffered drain, Git transaction, Research or Assembly semantics.
2. `scripts/test_dossier_two_stage_postmerge_joint.py`: two new isolated tests, covering exact boolean proof values, each three live-authority field's unsafe/malformed state, malformed proof metadata, wrong writer domain, default live calls, actual checkout denial, missing disposable marker; and both proof values through the actual Research→Assembly→P2 GitHub chain and strict existing three-game group writer.
3. `scripts/test_dossier_two_stage_final_acceptance.py`: previous assertion that the proof flag must permanently be false is replaced by assertion that it must be an exact boolean.
4. `config/dossier_two_stage_final_acceptance_bridge_contract.json`: proof metadata `false → true` **after direct joint positive regression**; no activation flag or writer setting changed.
5. This worker report.

## Verified test behavior

- Contradictory **original-work year 2021** asserted by `rsource-002` against Research identity/source original **2020** produces P1 strict rejection and P2 `rejected_invalid / invalid_binding`. Assembly may have submitted from exact original Research Git bytes without waiting for its Research receipt; an invalid A cannot become accepted/canonical/Deep-ready.
- Independently valid B/C remain inspectable despite A; the incomplete original first group stays pending, and only the separate exact ready original **3/3** second group enters the pre-existing strict V2 writer.
- A later Steam/port source `publication_date=2024-08-09` with original-work year 2020 and valid platform/version corroborators is accepted by P1/P2; it is **not** treated as a 2024 original-work date.
- Under **both** proof values, default/live calls are rejected; any of `active=true`, `authorized_for_canonical_ingest=true`, `executable_in_production=true` (or null / stringified false) fails closed. Missing/malformed proof, non-fixture real checkout, absent marker and wrong writer domain fail closed. Disposable-Git inspections still never issue accepted/Deep-ready receipts.
- No fixture writes touch actual `data/`, the real Dossier cache or actual canonical manifests. The existing test-proven single-writer GitHub contract is unchanged.

## CI record

**Phase 1 (guard decoupled, proof still false):** code head `d03039abbe3e750721610da7c53832a1c5ed450f`.
- PR-only joint workflow run **38129805302: SUCCESS**; added two real joint tests and existing PR #190 suite, ordinary former-XFAIL negative, P1, P2, original bridge, async, strict one-stage and execution ownership checks.
- PR-only final bridge workflow run **38129805305: SUCCESS**.
- Both the new direct joint step and the old ordinary negative Research-year regression completed successfully **before** changing the proof bit to true.

**Phase 2 (proof=true):** implementation head `6c0c3df1851c1d3ef5af9c7d86a70fce0d191dc3`.
- PR-only joint workflow **38130006101: SUCCESS**. The new two-boolean Research→Assembly→GitHub tests and all merged PR #190, P1/P2, final bridge, async, one-stage and execution ownership regressions passed.
- PR-only final bridge workflow **38130006057: SUCCESS**.
- PR-only eventual chain workflow **38130006093: SUCCESS**.

## Explicit gate states and limits

- Final bridge: `active=false`, `authorized_for_canonical_ingest=false`, `executable_in_production=false`, `cross_pr_research_original_year_fix_verified=true`.
- Interfaces: `active=false`, `authoritative=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`.
- P2 staging: `active=false`, `authoritative=false`, `executable_in_production=false`.
- Async buffer: `active=false`, `authoritative=false`, `executable_in_production=false`.
- Shared writer remains `taste-steam-review-dossier-canonical-writer`, `cancel_in_progress=false`, `new_live_workflow=false`; one-stage Dossier remains the sole production authority.
- No real-evidence semantic parity/shadow acceptance or end-to-end production cutover is proven or authorized by this metadata. Future separate user/Director approval and writer integration under existing shared lock remain mandatory.
- `CURRENT_TASK.md` and Chat 2's independent planning, report, quality harness, site UI/metrics and Director plan remain unchanged to avoid cross-chat concurrent writes.

**Status:** offline correction and proof=true code CI complete and green; independent final review/merge remains with Director, and production/shadow/cutover remain blocked. The worker does not merge the PR.
