# Worker report — inactive Dossier GitHub final acceptance integration 01

- Physical worker: **НОВЫЙ ЧАТ — ЧАТ 2**.
- Task: `WORKER_TASK_DOSSIER_ASYNC_GITHUB_FINAL_ACCEPTANCE_INTEGRATION_01.md`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`, base `main`.
- Branch: `implement/dossier-async-final-acceptance-integration-01`.
- PR: **#188** — https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/188 (OPEN; worker must not merge).
- Mode: **INACTIVE / synthetic disposable Git only / PR-only**.
- Status: **inactive integration implemented; CI recheck pending; NOT authorized for production or canonical live acceptance**.

## START and architecture preflight

Read `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`, the assigned task, the complete preceding chain QA worker-report and the relevant Dossier route/contracts before writes. Scope is the new bridge, independent tests, dedicated PR-only workflow and this report. No P1 Research validator, Research tests, stage semantic prompts, existing strict final validator, live ingestion workflow or current canonical writer was changed.

Canonical owner: GitHub Actions control plane by `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json`. This is not a new ChatGPT execution responsibility, daily quota, queue, lease, retry, semantic stage or scheduler. The two-stage interface/staging/async contracts remain inactive. The actual shared writer domain is exactly **`taste-steam-review-dossier-canonical-writer`**, `cancel-in-progress: false`; the existing live owner is `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`, with the companion shared-writer workflows indexed in `PROJECT_ROUTES.md`.

The canonical final writer APIs were established before implementation:
- `scripts/dossier_two_stage_async_buffer.py::inspect_buffered_assembly_candidate` replays immutable Git Research/Assembly proof for **one item**; it does not accept a dossier.
- `scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact` is the existing authoritative *strict complete ordered original group* validator, including V2 strict item validation.
- `scripts/taste_steam_review_dossier_buffered.py::drain_buffered_groups` owns current strict final group classification, canonical Dossier cache writes and group-progress, via `plan_buffered_drain` and `apply_buffered_drain`.
- `scripts/stage_taste_dossier_canonical_writer.sh` and the above existing Actions shared concurrency domain own staging, one canonical Git commit, rebase/push and subsequent Deep eligibility recomputation. Python local filesystem writes alone are **not** an atomic public GitHub publication.

## New files and exact inactive handoff

1. `config/dossier_two_stage_final_acceptance_bridge_contract.json`: independent gate `active=false`, `authorized_for_canonical_ingest=false`, `executable_in_production=false`, cross-PR Research year confirmation `false`. Records existing writer domain, strict APIs and activation blockers.
2. `scripts/dossier_two_stage_final_acceptance.py`: refuses all live/default invocations. Allows explicit offline fixture execution only in a separately marked temporary disposable Git repository. No production CLI. It consumes only exact GitHub-supplied immutable per-item commit/buffer/marker/plan locators.
3. `scripts/test_dossier_two_stage_final_acceptance.py`: synthetic three- and six-game disposable Git cases, real Research and Assembly fixture commits, strict V2 ready dossiers and the existing unmodified buffered drain on isolated manifest/cache/inbox paths.
4. `.github/workflows/validate-dossier-async-final-acceptance-integration.yml`: `pull_request` path-filtered read-only checks; no push, workflow dispatch, workflow_run, schedule, production data or credentials.

**Transition / trust boundary**:

```text
GitHub-owned immutable original worker group descriptor + pending group plan
              |
finite Research/Assembly frozen Git authorizations (exact marker parents)
              |
independent create-only Research and Assembly Git submissions (no Research
accepted-receipt liveness gate for semantic Assembly)
              |
GitHub eventual inspect_buffered_assembly_candidate (per submitted item)
  |-- missing => missing_not_yet_submitted (no attempt)
  |-- invalid/forged/stale => invalid_item_quarantined_locally (no attempt)
  |-- valid nonready => non_ready_semantic_gap (no guessed retry)
  '-- strict ready => valid_pending_original_group (not accepted; no Deep)
              |
ONLY IF original ordered 3/3 strict V2 ready, descriptor/index/manifest match:
existing validate_buffer_artifact on complete original immutable descriptor
              |
offline-only ready handoff; canonical acceptance is STILL false
              |
second immutable Git + source HEAD + strict V2 check at writer boundary
              |
existing deterministic buffered inbox + existing drain_buffered_groups
              |
FUTURE activation only: existing Actions shared lock, atomic Git publication,
canonical progress/cache and existing Deep eligibility recomputation.
```

The test-only bridge does not publish GitHub accepted receipts and never derives authority from a worker readiness flag or forged receipt. A missing, rejected or gap item keeps only its original group pending; any independent original complete next group can proceed. Duplicate item locators, wrong original order/group, stale snapshot, wrong marker/commit/path/blob/hash/plan/prompt and submitted file rewrite fail closed. Pre-existing deterministic group-path collision is never overwritten/renamed; the existing strict writer handles/quarantines that transport, while independently valid other original groups remain ingestible. Already accepted groups are not replayed.

**Atomicity claim boundary:** Only the *existing serialized GitHub Actions writer's single canonical commit* can make final manifest/cache/progress/Deep publication atomic. This PR does **not** add a new production Actions consumer and does not execute canonical writes in the actual repository; it proves routing against the existing writer in disposable Git. Separate authorized cutover must put a real, revalidated consumer into that same shared writer transaction. Replaying an item-local QA verdict or the offline handoff as a production receipt would be unsafe.

## CI evidence and remaining gates

PR-only tests cover nonready Research A and subsequent Assembly A, exact three-chain ready group, strict real group writer accept, bad Research A with independently accepted next three-game group, group collision without overwrite, duplicate/foreign item, tampered Research and Assembly commit bindings, altered original order, fake GitHub receipt, stale manifest and replay.

Initial run `38114383516` **failed** due to a *test-fixture-only* mistake: fixture canonical work file was added in the same Git commit as a create-only Research transport. It was corrected by committing the synthetic fixture manifest separately. Further hardening revalidates original submitted Git bytes and current HEAD at final writer handoff instead of trusting an earlier local inspection object. No live data were touched. Latest run confirmation and exact status must be recorded only from subsequent GitHub CI evidence.

**Research original release year blocker (ЧАТ 1):** preceding PR #185 documented `test_known_gap_conflicting_source_original_year_must_be_rejected` as XFAIL. This adapter does not edit `validate_research`, cross-kind original-work vs Steam-storefront year compatibility or Research tests. `cross_pr_research_original_year_fix_verified=false` and the live gate remains false. Before any activation: merge/test the independent ЧАТ 1 correction; require the XFAIL to become genuine green; jointly rerun entire P1/P2/async/final writer fixture matrix without regression. Synthetic acceptance tests are **not** production semantic/evidence quality proof.

Further blockers: future real-evidence offline parity; shadow quality acceptance; separate Director/user-approved activation/cutover; correct integration inside the existing `taste-steam-review-dossier-canonical-writer` lock and canonical commit; real GitHub receipt/idempotent recovery review without a second retry manager; preserved one-stage Dossier and Deep readiness until cutover. No Scheduled Task, production, migration or manual-shell-write workflow change is authorized by this PR.

## Scope of side effects

No production Dossier/Deep/Fast/ranking/visual state touched, no semantic API or source retrieval, no actual canonical cache write and no Scheduled Task changed. No PR merge performed.
