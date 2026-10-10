# Worker report — inactive Dossier asynchronous GitHub chain acceptance QA 01

- Physical worker: **НОВЫЙ ЧАТ — ЧАТ 2**
- Task: `WORKER_TASK_DOSSIER_ASYNC_GITHUB_CHAIN_ACCEPTANCE_QA_01.md`
- Base: `main`; branch: `qa/dossier-async-github-chain-acceptance-01`.
- Mode: **offline validation only; inactive; PR-only; never a semantic or production run**.
- PR: to be recorded after creation. No merge performed.

## Scope and independent ownership

Read current `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task, bounded route and relevant canonical ownership, interface, staging and async-buffer contracts. No file owned by ЧАТ 1 was changed. Source files, schema, live one-stage validator, production, Deep/Fast, scheduling and retry/claim authority remain untouched.

Added only:
1. `scripts/test_dossier_two_stage_eventual_chain_qa.py` — independent disposable Git-history adversarial cases against **existing** `inspect_buffered_assembly_candidate`, `receive_research`, frozen buffers and strict current group-transport validator.
2. `.github/workflows/validate-dossier-async-chain-acceptance-qa.yml` — PR-only isolated QA and existing P1/P2/async, one-stage factual-date and Deep-release-year regressions.
3. This report.

## What the checker actually does

- Research and Assembly work are preauthorized in exact GitHub-prepared frozen buffers and nonce-marker single-parent Git history. Assembly can inspect immutable **submitted** Research without waiting for a GitHub Research receipt. No semantic execution is part of these tests.
- The eventual inspector rechecks Research candidate's original introducing commit, exact path, Git blob hash, raw SHA-256 and canonical JSON SHA-256, original marker/assignment/first-parent ancestry, original prepared-work Git blob, Assembly plan Git blob, prompt/contract/target and immutable Assembly result. It then invokes GitHub Research structural/privacy checks, P1 Assembly provenance/gap rules, and for ready candidates the current strict V2 *item* validator.
- Its only positive result is `strict_item_valid_pending_existing_atomic_group_ingest` (or typed non-ready classification). All branches return `canonical_dossier_accepted=false` and `deep_ready=false`; rejected Research remains local to one item. No final acceptance is inferred from an item-local status.

## Independent QA matrix

| Case | Expected safe behavior |
| --- | --- |
| A subsequently rejected; B and C submitted while GitHub lags | A local quarantine, B/C remain independently inspectable; nobody gets canonical/Deep readiness |
| Wrong Research original commit/path/blob/raw SHA/canonical SHA | fail closed, never rebind to a newly submitted file |
| Wrong Research prepared blob/Assembly plan blob/Research marker | fail closed against frozen Git object identities |
| Wrong Assembly work ID/contract digest/prompt digest/marker/nonce/output | fail closed |
| Wrong original assignment or foreign game | fail closed; cannot shift original group |
| Duplicate, stale or overwritten Assembly submission | reject create-only reintroduction; no accepted replays |
| Unprepared B/foreign plan/unauthorized retry | cannot expand frozen authorization |
| Forged GitHub accepted Research receipt | cannot substitute for genuine structural validation; fake existing receipt collides fail-closed |
| Privacy-unsafe Research, broken feedback/parent refs | reject item without invalidating B/C |
| Forged Deep flag or canonical acceptance; invalid Assembly schema/outcome | reject; no semantic status grants Deep |
| Swapped Research vs Assembly marker | refuse marker-kind/ancestry mismatch |
| Strict original three-game group partial/reordered/duplicated/replaced | `validate_buffer_artifact` rejects independently of item-local chain verdicts |

**Limitation:** synthetic tests prove rejection and group-transport guards; no artificial successful three-game V2 factual dossier is persisted or treated as canonical.

## Blocking gap found: inconsistent Research original release year

The existing P1 `validate_research` verifies that the research identity's original-work year exists and binds source AppID/title, but does **not** require the original-work year in a source's `exact_product_binding.original_work_release_year` to match `identity.original_work_release_year`. The GitHub P2 `receive_research` currently calls that validator and can classify an internally contradictory fixture as `accepted_structural_evidence`.

An explicitly **expected-failure** regression (`test_known_gap_conflicting_source_original_year_must_be_rejected`) records the defect in green CI without changing the helper implementation shared with ЧАТ 1 or silently granting authority. Expected failure is **not** evidence of safety. Separate bounded authorization should require a fail-closed source/identity-year invariant and revalidate both the strict item candidate and group edge; do not implement it by weakening cross-kind Steam-storefront vs original-work-year compatibility.

## Strict group and GitHub final writer integration

**Current observed implementation: OFFLINE CHAIN VALIDATION ONLY.** `scripts/dossier_two_stage_async_buffer.py::inspect_buffered_assembly_candidate` explicitly says it never accepts canonical data; it returns an item-local verdict. The existing one-stage `scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact` requires the complete exact descriptor's ordered games and runs strict V2 validation on all dossiers. The async contract remains `active=false` and says no canonical writes. A real async item-to-three-game assembler/final-ingest/writer call path is **not implemented or proven by this task**.

A **separate Director-authorized integration** would need: a GitHub-owned shared-writer-lock consumer of each submitted Research/Assembly Git transport; exact immutable provenance revalidation at that write boundary; item-local classified accept/reject/quarantine; immutable assembly of the *original complete ordered group* only when all eligible items meet strict V2; existing strict buffered three-game `validate_buffer_artifact`/final ingest without weakening it; atomic canonical/cache/group-progress publication and separately derived Deep eligibility; idempotent collision/retry handling and no sibling head-of-line blocking. Do not activate or invent this pipeline as part of QA.

## Verification and nonactivation

- Isolated disposable Git fixtures only; no external Research, semantic worker, current production inputs, real user game evidence or synthetic production data.
- No cache/Deep/Fast/queue/retry/workflow production writes, no scheduled task/automation changes, no `manual-shell-write.yml`.
- Existing one-stage Dossier strict validator left unchanged.
- CI status: **pending PR-run confirmation**.
- Merge: **not performed**.
